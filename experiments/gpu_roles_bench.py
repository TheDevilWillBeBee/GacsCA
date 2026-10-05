"""gpu.py's kernel against gpu_roles.py's on rings of level-2 cells (REPORT section 30).

For each ring size the state (random level-2 cells, encoded twice) is advanced to an Age
inside the gathers and to one inside the program. From each, both kernels run the same
--ticks ticks; the two physical states must be equal, and the time per tick is recorded.
The whole-period figure weights the two by the share of the program in the work period.
Usage: gpu_roles_bench.py --candidate G16 [--cells 1,2] [--ticks 2000]
Receipt: figs/gpu/<candidate>_roles_bench.json
"""
import argparse
import json
import os
import subprocess
import time
import numpy as np
from gacsca import candidates, codec, gpu, gpu_roles

OUT = os.path.join(candidates.ROOT, 'figs', 'gpu')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--candidate', default=candidates.CURRENT)
    ap.add_argument('--cells', default='1,2', help='level-2 cells per ring')
    ap.add_argument('--ticks', type=int, default=2000)
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    cand = candidates.load(args.candidate)
    p, C = cand.p, cand.c_backend()
    Q, U = p.Q, p.U
    ages = dict(gathers=3000 % U, program=p.E0 + (p.NP // 2) * p.PL)
    program_share = p.NP * p.PL / U
    rng = np.random.default_rng(5)
    rows = []
    for n2 in [int(x) for x in args.cells.split(',')]:
        P = C.pack(codec.encode(cand, codec.encode(cand, codec.random_upper(cand, n2, rng))))
        fast = gpu_roles.RoleSim(cand, n2 * Q)
        ref = gpu.GpuSim(cand, 1, n2 * Q, mode='grid')
        row = dict(level2_cells=n2, sites=n2 * Q * Q, blocks=fast.blocks, **fast.partition.summary)
        cur, age = P, 0
        for name, target in sorted(ages.items(), key=lambda kv: kv[1]):
            ref.set_state(cur)
            ref.run(target - age)
            cur, age = ref.state()[0], target
            best = {}
            for _ in range(3):
                fast.set_state(cur)
                fast.run(args.ticks)
                ref.set_state(cur)
                ref.run(args.ticks)
                best['roles'] = min(best.get('roles', 1e9), fast.last_ms * 1000 / args.ticks)
                best['reference'] = min(best.get('reference', 1e9), ref.last_ms * 1000 / args.ticks)
            row[name] = dict(age=target, equal=bool(np.array_equal(fast.state(), ref.state()[0])),
                             us_per_tick_roles=round(best['roles'], 2),
                             us_per_tick_reference=round(best['reference'], 2))
        for k in ('roles', 'reference'):
            us = ((1 - program_share) * row['gathers'][f'us_per_tick_{k}']
                  + program_share * row['program'][f'us_per_tick_{k}'])
            row[f'whole_period_us_per_tick_{k}'] = round(us, 2)
            row[f'level2_step_hours_{k}'] = round(U * U * us * 1e-6 / 3600, 2)
        rows.append(row)
        print(json.dumps(row), flush=True)
        del fast, ref
    gpu_name = subprocess.run(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'],
                              capture_output=True, text=True).stdout.strip()
    with open(os.path.join(OUT, f'{args.candidate}_roles_bench.json'), 'w') as fh:
        json.dump(dict(candidate=args.candidate, Q=Q, U=U, gpu=gpu_name, program_share=round(program_share, 4),
                       date=time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime()), rows=rows), fh, indent=1)


if __name__ == '__main__':
    main()
