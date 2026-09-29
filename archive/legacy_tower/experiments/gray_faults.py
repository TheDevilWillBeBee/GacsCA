"""Checkpointed full-Q Gray transient-fault diagnostics (not an iid sweep).

Four rings: clean, a one-cell one-step fault, a 200x200 early fault box,
and a 200x200 update-stage fault box. Inside a box, replacement probability
is one; outside all boxes it is zero. All fields use the engine's version-2
counter RNG. Box times refer to old physical time t, with replacement after
the transition t -> t+1. Two periods include a subsequent repair opportunity.
"""
import argparse
from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
import time

import numpy as np
import torch

from gacsca import level0_np
from gacsca.build import make_system
from gacsca.checkpoint import load_checkpoint, save_checkpoint
from gacsca.gpu import field
from gacsca.gpu_engine import CleanGraphRunner
from gacsca.hierarchy import encode_state_info, decode_state_info
from gacsca.params import Params, Variant
from experiments.tower_checkpoint import fingerprint


@dataclass(frozen=True)
class FaultBox:
    batch: int
    start: int
    stop: int
    left: int
    right: int

    def validate(self, batches, length):
        if not (0 <= self.batch < batches and 0 <= self.start < self.stop
                and 0 <= self.left < self.right <= length):
            raise ValueError("fault box must lie within one ring and a nonempty time interval")


def advance(runner, start, stop, boxes, noise_buffer):
    """Exact clean graph segments plus separately countered noisy microsteps.

No noise is captured in a graph. The two kernels at a faulty step share the
same input; only the selected sites take the whole-cell replacement output.
"""
    if not 0 <= start <= stop:
        raise ValueError("invalid time interval")
    if noise_buffer.shape != runner.state.shape or noise_buffer.data_ptr() in (
            runner.state.data_ptr(), runner.buffer.data_ptr()):
        raise ValueError("noise buffer must be distinct and match state shape")
    for box in boxes:
        box.validate(*runner.state.shape[:2])
    t = start
    while t < stop:
        active = [box for box in boxes if box.start <= t < box.stop]
        if active:
            runner.engine.step(runner.state, noise_buffer, t + 1, eps=1.0)
            runner.run(1)
            for box in active:
                runner.state[box.batch, box.left:box.right].copy_(
                    noise_buffer[box.batch, box.left:box.right])
            t += 1
        else:
            end = min([stop] + [box.start for box in boxes if box.start > t])
            runner.run(end - t)
            t = end


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--stop-after", type=int)
    parser.add_argument("--periods", type=int, default=2)
    parser.add_argument("--chunk", type=int, default=8192)
    parser.add_argument("--seed", type=int, default=20920)
    parser.add_argument("--flag2-erase", choices=("printed", "no_ones", "at_most_one"), default="printed",
                        help="explicit D8 research variant; printed remains the source baseline")
    args = parser.parse_args()
    if min(args.periods, args.chunk, args.stop_after or 1) < 1:
        parser.error("periods, chunk and stop-after must be positive")
    path = args.output.with_suffix(".npz")
    if path.exists() and not args.resume:
        parser.error("refusing to overwrite; use --resume")
    variant = Variant(flag2_healthy_erase=args.flag2_erase)
    system = make_system(Q=8192, U=1048576, ncol=16, R=5, D=1,
                         Qs=16, Us=2048, schedule="gray", variant=variant)
    Q, U = system.p.Q, system.p.U
    gpu = system.gpu_engine(seed=args.seed)
    upper_p = Params(Q=16, U=2048, ncol=1)
    reference = level0_np.initial(upper_p, 4)
    reference["age"][:] = 777
    left = 7 * Q
    boxes = [FaultBox(1, 64, 65, left + system.L.b0, left + system.L.b0 + 1),
             FaultBox(2, 64, 264, left, left + 200),
             FaultBox(3, system.sched.compute_start + 256,
                      system.sched.compute_start + 456, left, left + 200)]
    hashes = fingerprint()
    script = Path(__file__)
    hashes[str(script.relative_to(script.parents[1]))] = hashlib.sha256(script.read_bytes()).hexdigest()
    identity = dict(schema=2, protocol="gray-physical-transients", fingerprints=hashes,
                    Q=Q, U=U, ncol=16, encoded_bits=system.L.K, noise_version=2,
                    seed=args.seed, periods=args.periods, chunk=args.chunk, variant=asdict(variant),
                    boxes=[asdict(box) for box in boxes],
                    scenarios=["clean", "one-cell", "early-200x200", "update-200x200"])
    if args.resume:
        meta, arrays = load_checkpoint(path, identity)
        if meta["status"] == "failed":
            raise ValueError("failed checkpoint requires diagnosis")
        state = torch.from_numpy(arrays["physical"]).cuda()
        reference = {k[4:]: v for k, v in arrays.items() if k.startswith("ref_")}
        previous = {k[5:]: v for k, v in arrays.items() if k.startswith("prev_")}
        traces = list(arrays["structure_bins"])
    else:
        bits = encode_state_info(reference, system.L, Q)
        state = gpu.to_gpu(system.np_engine().initial(4, info_bits=bits))
        previous = {k: v.copy() for k, v in reference.items()}
        meta = dict(identity=identity, steps=0, status="running", samples=[], commits=[],
                    elapsed_seconds=0.0, gpu=torch.cuda.get_device_name(), torch=torch.__version__)
        traces = []
    runner = CleanGraphRunner(gpu, state)
    noise_buffer = torch.empty_like(state)
    target = args.periods * U
    stop = min(target, meta["steps"] + (args.stop_after or target))
    begin = time.monotonic()
    previous_elapsed = meta["elapsed_seconds"]
    ideal_addr = torch.arange(system.p.L, device=state.device) % Q
    events = {i * U for i in range(1, args.periods + 1)}
    for box in boxes:
        events.update((box.start, box.stop))
        events.update(box.stop + delta for delta in (1, 16, 64, 256, 1024, 4096, Q, 2 * Q))

    def save():
        meta["elapsed_seconds"] = previous_elapsed + time.monotonic() - begin
        arrays = dict(physical=runner.state.cpu().numpy(),
                      structure_bins=np.asarray(traces, dtype=np.uint8).reshape(-1, 4, system.p.L // 64))
        arrays.update({"ref_" + k: v for k, v in reference.items()})
        arrays.update({"prev_" + k: v for k, v in previous.items()})
        save_checkpoint(path, meta, arrays)

    if not args.resume:
        save()
    try:
        while meta["steps"] < stop:
            t = meta["steps"]
            end = min([stop, t + args.chunk] + [e for e in events if e > t])
            advance(runner, t, end, boxes, noise_buffer)
            meta["steps"] = end
            bad_addr = field(runner.state, "addr") != ideal_addr
            bad_age = field(runner.state, "age") != end % U
            bad = bad_addr | bad_age
            traces.append(bad.reshape(4, -1, 64).sum(-1).cpu().numpy().astype(np.uint8))
            sample = dict(step=end, bad_address=bad_addr.sum(1).cpu().tolist(),
                          bad_age=bad_age.sum(1).cpu().tolist(),
                          bad_structure=bad.sum(1).cpu().tolist(),
                          flag1=field(runner.state, "f1").sum(1).cpu().tolist(),
                          flag2=field(runner.state, "f2").sum(1).cpu().tolist())
            meta["samples"].append(sample)
            assert sample["bad_structure"][0] == 0, sample
            if end % U == 0:
                reference = level0_np.step(reference, upper_p, variant)
                reference.pop("_info")
                predicted = level0_np.step(previous, upper_p, variant)
                predicted.pop("_info")
                decoded = decode_state_info(gpu.info_bits(runner.state).cpu().numpy(), system.L, Q)
                record = dict(period=end // U)
                for label, expected in (("ground", reference), ("conditional_transition", predicted)):
                    record[label] = {k: (decoded[k] != v).sum(1).tolist() for k, v in expected.items()}
                record["decoded"] = {k: v.tolist() for k, v in decoded.items()}
                meta["commits"].append(record)
                assert not any(counts[0] for counts in record["ground"].values()), record
                previous = decoded
                print(json.dumps(record), flush=True)
            meta["status"] = "complete" if end == target else "running"
            save()
            print(json.dumps(dict(**sample, elapsed_seconds=round(meta["elapsed_seconds"], 2))), flush=True)
    except Exception as exc:
        meta["status"] = "failed"
        meta["error"] = repr(exc)
        save()
        raise


if __name__ == "__main__":
    main()
