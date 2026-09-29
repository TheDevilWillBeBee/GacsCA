"""Full-Q Gray-stage validation with clean and single-gather-corruption controls.

Four deterministic trajectories: clean, or complement every gathered bit in
bank A/B/C after that gather completes. This is a protocol-level adversarial
test, NOT iid physical noise or a bounded physical space-time island.
"""
import argparse
import hashlib
import json
from pathlib import Path
import time

import numpy as np
import torch

from gacsca import level0_np
from gacsca.build import make_system
from gacsca.checkpoint import save_checkpoint, load_checkpoint
from gacsca.gpu import field
from gacsca.gpu_engine import CleanGraphRunner
from gacsca.hierarchy import encode_state_info, decode_state_info
from gacsca.params import Params
from experiments.tower_checkpoint import fingerprint


def track_bits(gpu, state, track):
    votes = torch.zeros(state.shape[:2], dtype=torch.int32, device=state.device)
    h = (gpu.R - 1) // 2
    for r in range(gpu.R):
        word = state[..., gpu.track_base + r * gpu.NW + track // 32].contiguous().view(torch.int32)
        votes += torch.roll((word >> (track % 32)) & 1, r - h, dims=1)
    return (votes * 2 > gpu.R).to(torch.uint8).cpu().numpy()


def flip_bank(gpu, state, batch, bank):
    mask = np.zeros(gpu.W, np.uint32)
    for j in range(-5, 6):
        track = gpu.T.arg(j, bank)
        for r in range(gpu.R):
            mask[gpu.track_base + r * gpu.NW + track // 32] |= np.uint32(1) << np.uint32(track % 32)
    state.view(torch.int32)[batch].bitwise_xor_(torch.from_numpy(mask.view(np.int32)).cuda())


def rest_digest(state):
    a = state.cpu().numpy()
    # Local Address/Age/Flag1/Flag2 can evolve; simulation registers, workspace
    # flags, and every raw track copy are the rest-period invariants.
    digest = hashlib.sha256(a[..., 3:].tobytes())
    digest.update((a[..., 2] & 12).tobytes())
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--stop-after", type=int, help="stop after this many additional physical steps")
    parser.add_argument("--chunk", type=int, default=32768)
    parser.add_argument("--certified-skip", action="store_true",
                        help="verify and skip only noiseless instruction-free fixed-point intervals")
    args = parser.parse_args()
    if args.chunk < 1 or (args.stop_after is not None and args.stop_after < 1):
        parser.error("chunk and stop-after must be positive")
    path = args.output.with_suffix(".npz")
    if path.exists() and not args.resume:
        parser.error("refusing to overwrite; use --resume")
    s = make_system(Q=8192, U=1048576, ncol=16, R=5, D=1, Qs=16, Us=2048, schedule="gray")
    gpu = s.gpu_engine()
    upper_p = Params(Q=16, U=2048, ncol=1)
    initial = level0_np.initial(upper_p, 4)
    initial["age"][:] = 777; initial["age"][:, 5] = 780
    rng = np.random.default_rng(20260920)
    initial["f1"][:] = rng.integers(0, 2, (1, 16))
    initial["f2"][:] = rng.integers(0, 2, (1, 16))
    # Exercise the actual upper fault alphabet, not just its healthy subset.
    # Share the same input across scenarios so only bank corruption differs.
    for name in ("simage", "simaddr"):
        initial[name][:] = rng.integers(0, 65536, (1, 16), dtype=np.int32)
        initial[name][:, 7] = 65535
    info = encode_state_info(initial, s.L, s.p.Q)
    predicted = level0_np.step(initial, upper_p); predicted.pop("_info")
    hashes = fingerprint()
    hashes[str(Path(__file__).relative_to(Path(__file__).parents[1]))] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    if args.certified_skip:
        from experiments.quiescent import advance_certified
        skip_source = Path(__file__).with_name("quiescent.py")
        hashes[str(skip_source.relative_to(Path(__file__).parents[1]))] = hashlib.sha256(skip_source.read_bytes()).hexdigest()
    identity = dict(schema=2, fingerprints=hashes, protocol="gray-five-stage", Q=s.p.Q, U=s.p.U,
                    ncol=16, tracks=s.T.NT, encoded_bits=s.L.K,
                    encoded_register_bits=s.L.fields["SIMAGE"][1],
                    physical_register_bits=gpu.register_bits,
                    scenarios=["clean", "flip-A", "flip-B", "flip-C"], certified_skip=args.certified_skip)
    if args.resume:
        meta, arrays = load_checkpoint(path, identity)
        if meta["status"] == "failed":
            raise ValueError("failed checkpoint requires diagnosis")
        state = torch.from_numpy(arrays["physical"]).cuda()
    else:
        state = gpu.to_gpu(s.np_engine().initial(4, info_bits=info))
        meta = dict(identity=identity, steps=0, status="running", events=[], rest_hashes={}, elapsed_seconds=0.0,
                    skip_certificates=[], skipped_steps=0)
    runner = CleanGraphRunner(gpu, state)
    start = time.monotonic(); previous_elapsed = meta["elapsed_seconds"]
    stop = min(s.p.U, meta["steps"] + (args.stop_after or s.p.U))
    events = {}
    for i, g in enumerate(s.sched.gather_starts):
        events[g + 5 * s.p.Q + 2] = ("gather", i)
    for i, (_, active_end, end) in enumerate(s.sched.stages):
        events[active_end] = ("rest-start", i)
        events[end - 1] = ("rest-end", i)
    events[s.sched.signal_write + 1] = ("signal", 0)
    events[s.sched.compute_end] = ("computed", 0)
    events[s.p.U] = ("commit", 0)
    def save():
        meta["elapsed_seconds"] = previous_elapsed + time.monotonic() - start
        save_checkpoint(path, meta, dict(physical=runner.state.cpu().numpy()))
    if not args.resume:
        save()
    try:
        while meta["steps"] < stop:
            t = meta["steps"]
            event_time = min(e for e in events if e > t)
            next_time = min(event_time, t + args.chunk, stop)
            if args.certified_skip:
                certificates = []
                advance_certified(runner, next_time - t, certificates)
                meta["skip_certificates"].extend(certificates)
                meta["skipped_steps"] += sum(c["steps"] for c in certificates)
            else:
                runner.run(next_time - t)
            meta["steps"] = next_time
            if next_time == event_time:
                kind, i = events[next_time]
                record = dict(step=next_time, kind=kind, index=i)
                if kind == "gather":
                    bank = "ABC"[i]
                    errors = 0
                    for j in range(-5, 6):
                        actual = track_bits(gpu, runner.state, s.T.arg(j, bank)).reshape(4, 16, s.p.Q)
                        expected = np.roll(info, -j * s.p.Q, axis=1).reshape(4, 16, s.p.Q)
                        sl = slice(s.L.b0, s.L.b0 + s.L.K)
                        errors += int(np.count_nonzero(actual[..., sl] != expected[..., sl]))
                    record["gather_bit_errors_before_fault"] = errors
                    assert errors == 0, record
                    flip_bank(gpu, runner.state, i + 1, bank)
                    record["flipped_bank_in_batch"] = i + 1
                elif kind == "rest-start":
                    meta["rest_hashes"][str(i)] = rest_digest(runner.state)
                elif kind == "rest-end":
                    record["simulation_fields_unchanged"] = rest_digest(runner.state) == meta["rest_hashes"][str(i)]
                    assert record["simulation_fields_unchanged"], record
                elif kind == "signal":
                    bits = gpu.info_bits(runner.state).cpu().numpy().reshape(4, 16, s.p.Q)
                    record["flag_signal_errors"] = int(np.count_nonzero(bits[..., s.p.Q - 3] != predicted["f1"]) +
                                                       np.count_nonzero(bits[..., 3] != predicted["f2"]))
                    assert record["flag_signal_errors"] == 0, record
                elif kind in ("computed", "commit"):
                    track = s.T["HOLD"] if kind == "computed" else s.T["INFO"]
                    decoded = decode_state_info(track_bits(gpu, runner.state, track), s.L, s.p.Q)
                    record["errors_by_field_scenario"] = {k: (decoded[k] != v).sum(1).tolist() for k, v in predicted.items()}
                    assert not any(any(v) for v in record["errors_by_field_scenario"].values()), record
                meta["events"].append(record)
                print(json.dumps(record), flush=True)
            physical_bad = ((field(runner.state, "addr") != torch.arange(s.p.L, device=state.device) % s.p.Q) |
                            (field(runner.state, "age") != next_time % s.p.U)).sum().item()
            assert physical_bad == 0, (next_time, physical_bad)
            meta["status"] = "complete" if next_time == s.p.U else "running"
            save()
            print(json.dumps(dict(step=next_time, total=s.p.U, status=meta["status"],
                                  elapsed_seconds=round(meta["elapsed_seconds"], 2))), flush=True)
    except Exception as exc:
        meta["status"] = "failed"; meta["error"] = repr(exc); save()
        raise


if __name__ == "__main__":
    main()
