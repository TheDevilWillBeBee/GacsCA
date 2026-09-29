"""Matched-parameter redundancy sweep with independent ring trial statistics.

Run: PYTHONPATH=. python experiments/redundancy_noise.py
Measures one-step simulated transition errors, not logical memory lifetime.
"""
import argparse
import hashlib
import json
from pathlib import Path
import time

import numpy as np
import torch

from gacsca.build import make_system
from gacsca.hierarchy import encode_info
from gacsca.params import Params
from gacsca import level0_np
from gacsca.gpu import field


def decode(gpu, state):
    layout, Q = gpu.L, gpu.p.Q
    info = gpu.info_bits(state).cpu().numpy().reshape(state.shape[0], gpu.p.ncol, Q)
    result = {}
    for name in ("ADDR", "AGE", "F1", "F2", "WF1", "WF2"):
        start, width = layout.fields[name]
        bits = info[:, :, layout.b0 + start:layout.b0 + start + width]
        result[name.lower()] = (bits * (1 << np.arange(width))).sum(-1).astype(np.int32)
    # The top automaton is local-only: Workspace flags are not persistent data.
    return result


def trial_interval(values, rng):
    """Bootstrap whole independent rings, preserving space/time correlations."""
    values = np.asarray(values)
    means = rng.choice(values, (4000, len(values)), replace=True).mean(1)
    return np.quantile(means, [0.025, 0.975]).tolist()


def run_point(args, redundancy, epsilon, seed):
    system = make_system(Q=args.Q, U=args.U, ncol=args.ncol, R=redundancy,
                         D=1, Qs=16, Us=2048)
    gpu = system.gpu_engine(seed=seed, noise_version=args.noise_version)
    cells = [dict(addr=i % 16, age=777, f1=0, f2=0) for i in range(args.ncol)]
    bits = np.tile(encode_info(cells, system.L, args.Q), (args.trials, 1))
    state = gpu.to_gpu(system.np_engine().initial(args.trials, info_bits=bits))
    previous = decode(gpu, state)
    upper = Params(Q=16, U=2048, ncol=args.ncol // 16)
    per_trial_errors = np.zeros((args.trials, args.periods), dtype=np.int64)
    physical_bad = np.zeros_like(per_trial_errors)
    local_bad = np.zeros_like(per_trial_errors)
    reference = torch.arange(gpu.p.L, device=state.device) % args.Q
    started = time.monotonic()
    for period in range(args.periods):
        state = gpu.run(state, args.U, epsilon, t0=period * args.U)
        current = decode(gpu, state)
        predicted = level0_np.step(previous, upper)
        bad = np.zeros((args.trials, args.ncol), dtype=bool)
        for k in ("addr", "age", "f1", "f2"):
            bad |= current[k] != predicted[k]
        per_trial_errors[:, period] = bad.sum(1)
        # Separate top-layer deviations from its intended ground trajectory.
        local_bad[:, period] = ((current["addr"] != np.arange(args.ncol) % 16) |
                               (current["age"] != (778 + period) % 2048)).sum(1)
        physical_bad[:, period] = ((field(state, "addr") != reference) |
                                  (field(state, "age") != 0)).sum(1).cpu().numpy()
        previous = current
    rates = per_trial_errors.sum(1) / (args.ncol * args.periods)
    any_failure = (per_trial_errors.sum(1) > 0)
    result = dict(R=redundancy, D=1, epsilon=epsilon, seed=seed,
                  errors_by_trial_period=per_trial_errors.tolist(),
                  physical_structure_bad_by_trial_period=physical_bad.tolist(),
                  simulated_structure_bad_by_trial_period=local_bad.tolist(),
                  transition_error_rate=float(rates.mean()),
                  trial_bootstrap_95=trial_interval(rates, np.random.default_rng(seed)),
                  trials_with_error=int(any_failure.sum()),
                  elapsed_seconds=time.monotonic() - started,
                  compute_window=[system.sched.compute_start, system.sched.compute_end],
                  layout_bits=system.L.K)
    if not any_failure.any():
        # Exact one-sided 95% limit for a ring experiencing any error during
        # this finite observation, NOT for independent cell-period errors.
        result["zero_event_ring_risk_upper95"] = 1 - 0.05 ** (1 / args.trials)
    if epsilon == 0:
        assert not per_trial_errors.any() and not physical_bad.any() and not local_bad.any()
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--Q", type=int, default=256)
    parser.add_argument("--U", type=int, default=32768)
    parser.add_argument("--ncol", type=int, default=32)
    parser.add_argument("--trials", type=int, default=16)
    parser.add_argument("--periods", type=int, default=4)
    parser.add_argument("--seed", type=int, default=920)
    parser.add_argument("--noise-version", type=int, choices=(1, 2), default=2)
    parser.add_argument("--eps", type=float, nargs="+", default=[0, 1e-5, 3e-5, 1e-4, 3e-4])
    parser.add_argument("--output", type=Path, default=Path("figs/redundancy_noise_20260920.json"))
    args = parser.parse_args()
    if args.ncol % 16 or min(args.trials, args.periods) < 1:
        parser.error("ncol must be divisible by 16; trials and periods must be positive")
    if args.output.exists():
        parser.error(f"refusing to overwrite {args.output}")
    sources = sorted(Path("gacsca").glob("*.py")) + sorted(Path("gacsca/cuda").glob("*.cu*"))
    digest = hashlib.sha256()
    for path in sources:
        digest.update(str(path).encode()); digest.update(path.read_bytes())
    result = dict(parameters={k: str(v) if isinstance(v, Path) else v for k, v in vars(args).items()},
                  source_sha256=digest.hexdigest(), torch=torch.__version__, numpy=np.__version__,
                  gpu=torch.cuda.get_device_name(), complete=False, points=[])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    for R in (3, 5):
        for i, eps in enumerate(args.eps):
            point = run_point(args, R, eps, args.seed + 100 * R + i)
            result["points"].append(point)
            args.output.write_text(json.dumps(result, indent=2) + "\n")
            print(f"R={R} eps={eps:g}: rate={point['transition_error_rate']:.6g}, "
                  f"CI={point['trial_bootstrap_95']}, rings={point['trials_with_error']}/{args.trials}, "
                  f"{point['elapsed_seconds']:.1f}s", flush=True)
    result["complete"] = True
    args.output.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
