"""Resumable clean tower validation, checking EVERY simulated transition.

Run: python -m experiments.tower_checkpoint --output figs/tower_checked_R3
Resume: same command with --resume. For R=5 use --R 5.
Each NPZ contains physical state, upper reference, initial terminal state, all
period diagnostics, source/binary fingerprints, and exact logical progress.
This is reduced-parameter validation, NOT a claim of Gray's complete schedule.
"""
import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import time

import numpy as np
import torch

from gacsca import level0_np
from gacsca.build import make_tower
from gacsca.checkpoint import save_checkpoint, load_checkpoint
from gacsca.engine_np import repair
from gacsca.gpu import field, gacs_cuda
from gacsca.gpu_engine import CleanGraphRunner
from gacsca.hierarchy import encode_state_info, decode_state_info
from gacsca.params import Params


def fingerprint():
    root = Path(__file__).resolve().parents[1]
    paths = sorted((root / "gacsca").glob("*.py")) + sorted((root / "gacsca/cuda").glob("*.cu*"))
    paths += [Path(__file__).resolve(), Path(gacs_cuda.__file__)]
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def mismatch_counts(actual, expected):
    return {k: int(np.count_nonzero(actual[k] != v)) for k, v in expected.items() if k != "_info"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--R", type=int, choices=(3, 5), default=3)
    parser.add_argument("--ncol0", type=int, default=64)
    parser.add_argument("--periods", type=int, default=None)
    parser.add_argument("--stop-after", type=int, default=None, help="maximum periods this invocation (for resume tests)")
    parser.add_argument("--checkpoint-every", type=int, default=16)
    parser.add_argument("--graph-block", type=int, default=256)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--output", type=Path, required=True, help="checkpoint prefix; existing runs require --resume")
    args = parser.parse_args()
    if args.ncol0 < 64 or args.ncol0 % 64 or args.checkpoint_every < 1:
        parser.error("ncol0 must be a positive multiple of 64; checkpoint-every must be positive")
    if (args.periods is not None and args.periods <= 0) or (args.stop_after is not None and args.stop_after <= 0):
        parser.error("periods and stop-after must be positive")
    checkpoint = args.output.with_suffix(".npz")
    if checkpoint.exists() and not args.resume:
        parser.error(f"refusing to overwrite {checkpoint}; use --resume")
    kw = dict(R=5, D=1, Q0=512, U0=32768, U1=8192) if args.R == 5 else {}
    lower, upper = make_tower(ncol0=args.ncol0, **kw)
    gpu, direct = lower.gpu_engine(), upper.np_engine()
    target = args.periods or upper.p.U
    identity = dict(schema=1, R=args.R, lower=asdict(lower.p), upper=asdict(upper.p),
                    Q2=upper.L.Qs, U2=upper.L.Us, periods=target, noise_version=gpu.noise_version,
                    noise=0.0, fingerprints=fingerprint())
    if args.resume:
        meta, arrays = load_checkpoint(checkpoint, identity)
        if meta["status"] == "failed":
            raise ValueError("failed checkpoint retained for diagnosis; do not resume as a success")
        reference = {k[6:]: v for k, v in arrays.items() if k.startswith("upper_")}
        top_initial = {k[4:]: v for k, v in arrays.items() if k.startswith("top_")}
        state = torch.from_numpy(arrays["physical"]).cuda()
    else:
        top_p = Params(Q=upper.L.Qs, U=upper.L.Us, ncol=1)
        # A small terminal ring is permitted but explicitly labelled in results.
        ntop = args.ncol0 // upper.p.Q
        top_initial = {k: v[:, :ntop].copy() for k, v in level0_np.initial(
            Params(Q=top_p.Q, U=top_p.U, ncol=(ntop + top_p.Q - 1) // top_p.Q)).items()}
        i = np.arange(ntop)
        top_initial["addr"][:] = (i + 5) % top_p.Q
        top_initial["age"][:] = (777 + i) % top_p.U
        top_initial["f1"][:] = i % 2
        top_initial["f2"][:] = (i + 1) % 2
        reference = direct.initial(1, info_bits=encode_state_info(top_initial, upper.L, upper.p.Q))
        physical = lower.np_engine().initial(1, info_bits=encode_state_info(reference, lower.L, lower.p.Q))
        physical["simage"][:] = np.repeat(reference["age"], lower.p.Q, axis=1)
        physical["simaddr"][:] = np.repeat(reference["addr"], lower.p.Q, axis=1)
        state = gpu.to_gpu(physical)
        meta = dict(identity=identity, completed_periods=0, physical_steps=0, elapsed_seconds=0.0,
                    status="running", log=[], terminal_checks=[], terminal_cells=ntop,
                    terminal_neighborhood_aliasing=ntop < 11, torch=torch.__version__,
                    gpu=torch.cuda.get_device_name(), graph_block=args.graph_block)
    runner = CleanGraphRunner(gpu, state, args.graph_block)
    started = time.monotonic()
    elapsed_before = meta["elapsed_seconds"]
    initial_period = meta["completed_periods"]
    stop = min(target, initial_period + (args.stop_after or target))
    physical_addr = torch.arange(lower.p.L, device=state.device) % lower.p.Q

    def save():
        meta["elapsed_seconds"] = elapsed_before + time.monotonic() - started
        arrays = dict(physical=runner.state.cpu().numpy())
        arrays.update({"upper_" + k: v for k, v in reference.items()})
        arrays.update({"top_" + k: v for k, v in top_initial.items()})
        save_checkpoint(checkpoint, meta, arrays)

    if not args.resume:
        save()
    for period in range(initial_period + 1, stop + 1):
        runner.run(lower.p.U)
        reference = direct.step(reference)
        decoded = decode_state_info(gpu.info_bits(runner.state).cpu().numpy(), lower.L, lower.p.Q)
        counts = mismatch_counts(decoded, reference)
        bad_structure = int(((field(runner.state, "addr") != physical_addr) |
                             (field(runner.state, "age") != 0)).sum().item())
        record = dict(period=period, upper_mismatches=counts, physical_bad_structure=bad_structure)
        meta["log"].append(record)
        failed = bad_structure > 0 or any(counts.values())
        if period % upper.p.U == 0:
            # Compare the entire terminal state, not just Address/Age/Flags.
            top_p = Params(Q=upper.L.Qs, U=upper.L.Us, ncol=1)
            predicted = {k: v.copy() for k, v in top_initial.items()}
            for _ in range(period // upper.p.U):
                predicted = level0_np.step(predicted, top_p)
                predicted.pop("_info")
            def decode_top(S):
                return decode_state_info(repair(S["trk"])[..., upper.T["INFO"]], upper.L, upper.p.Q)
            top_from_physical, top_from_direct = decode_top(decoded), decode_top(reference)
            check = dict(period=period, physical=mismatch_counts(top_from_physical, predicted),
                         direct=mismatch_counts(top_from_direct, predicted),
                         decoded={k: v.tolist() for k, v in top_from_physical.items()},
                         expected={k: v.tolist() for k, v in predicted.items()})
            meta["terminal_checks"].append(check)
            failed |= any(check["physical"].values()) or any(check["direct"].values())
        meta["completed_periods"] = period
        meta["physical_steps"] = period * lower.p.U
        meta["status"] = "failed" if failed else "complete" if period == target else "running"
        if failed or period % args.checkpoint_every == 0 or period == stop:
            save()
            print(json.dumps(dict(period=period, target=target, status=meta["status"],
                                  upper_mismatches=sum(counts.values()), physical_bad_structure=bad_structure,
                                  elapsed_seconds=round(meta["elapsed_seconds"], 2))), flush=True)
        if failed:
            raise SystemExit(1)
    if meta["status"] == "complete":
        print("COMPLETE: every simulated transition checked; terminal checks:", len(meta["terminal_checks"]), flush=True)


if __name__ == "__main__":
    main()
