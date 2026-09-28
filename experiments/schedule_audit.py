"""Executable audit of the compressed schedule against Gray pp.34–35.

Does not implement or certify Gray's schedule. Counts explicit op-table writes
in Gray's prescribed rest intervals; a clean trajectory witnesses one such
write at the full Gray parameter values Q=8192,U=128Q,R=5.
"""
import argparse
from dataclasses import asdict
import json
from pathlib import Path

import numpy as np
import torch

from gacsca.build import make_system
from gacsca.gpu_engine import CleanGraphRunner
from gacsca.hierarchy import encode_info


def gray_stages(U):
    if U % 16:
        raise ValueError("Gray's equal half-stages require U divisible by 16")
    boundaries = (0, U // 4, U // 2, 3 * U // 4, 7 * U // 8, U)
    return [dict(stage=i + 1, active=[a, (a + b) // 2], rest=[(a + b) // 2, b])
            for i, (a, b) in enumerate(zip(boundaries, boundaries[1:]))]


def audit(system):
    stages = gray_stages(system.p.U)
    rests = []
    for stage in stages:
        lo, hi = stage["rest"]
        ops = [op for op in system.prog.ops if max(lo, op.t0) < min(hi, op.t1)]
        rests.append(dict(stage=stage["stage"], explicit_ops=len(ops),
                          op_time_sum=sum(min(hi, op.t1) - max(lo, op.t0) for op in ops)))
    return dict(parameters=asdict(system.p), R=system.T.R, K=system.L.K,
                prescribed_stages=stages, actual_gather_starts=system.sched.gather_starts,
                actual_compute=[system.sched.compute_start, system.sched.compute_end],
                actual_trickle=list(system.sched.trickle),
                prescribed_trickle=[3 * system.p.U // 4, 3 * system.p.U // 4 + 2 * system.p.Q],
                actual_commit_old_age=system.sched.update_age,
                rest_op_intersections=rests)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("refusing to overwrite existing evidence")
    system = make_system(Q=8192, U=128 * 8192, ncol=1, R=5, D=1, Qs=16, Us=2048)
    result = audit(system)
    result["scope"] = "compressed local-only upper rule; full physical Q,U,R; not uniform self-simulation"
    gpu = system.gpu_engine()
    bits = encode_info([dict(addr=5, age=777, f1=0, f2=1)], system.L, system.p.Q)
    initial = gpu.to_gpu(system.np_engine().initial(1, info_bits=bits[None]))
    runner = CleanGraphRunner(gpu, initial)
    age, stage = next((age, s) for age in system.sched.gather_starts
                      for s in result["prescribed_stages"] if s["rest"][0] <= age < s["rest"][1])
    runner.run(age)
    before = runner.state.cpu().numpy().copy()
    runner.run(1)
    after = runner.state.cpu().numpy()
    changed = np.any(before[..., 4:] != after[..., 4:], axis=-1)
    result["rest_witness"] = dict(old_age=age, prescribed_rest_stage=stage["stage"],
                                   changed_track_cells=int(changed.sum()),
                                   physical_address_unchanged=bool(np.array_equal(before[..., 0], after[..., 0])),
                                   address_ground=bool(np.array_equal(after[0, :, 0], np.arange(system.p.L) % system.p.Q)),
                                   clean_clock=bool(np.all(before[..., 1] == age) and np.all(after[..., 1] == age + 1)))
    assert changed.any() and result["rest_witness"]["address_ground"] and result["rest_witness"]["clean_clock"]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result["rest_witness"]), flush=True)


if __name__ == "__main__":
    main()
