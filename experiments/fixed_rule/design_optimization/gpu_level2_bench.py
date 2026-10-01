"""CUDA throughput of a candidate at level-2 scale, and what a level-1 step
(U physical ticks) and a level-2 step (U^2 physical ticks) cost.

A level-2 cell is a colony of colonies: Q^2 physical sites. A physical ring
of n2 level-2 cells has n2 * Q^2 sites; a level-1 step takes U ticks of the
whole ring and a level-2 step U^2 ticks. Rings are filled with a coherent
three-level encoding (random level-2 cells) and timed with CUDA events
after a warm-up. --level1-configs times the level-1 automaton instead (the same
rule on a ring of n2 * Q level-1 cells, as the three-level experiments use it):
there a level-2 step is U ticks. Writes
figs/fixed_rule/design_optimization/gpu/<cand>_level2_bench.json.
Usage: gpu_level2_bench.py --candidate G15 [--ticks 2000]
"""
import argparse
import json
import os
import time
import numpy as np
from gacsca.fixed_rule.design_optimization import candidates, codec, gpu

OUT = os.path.join(candidates.ROOT, 'figs', 'fixed_rule', 'design_optimization', 'gpu')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--candidate', default='G15')
    ap.add_argument('--ticks', type=int, default=2000)
    ap.add_argument('--configs', default='1x1,1x2,1x4,1x8,4x1,16x1',
                    help='rings x level-2 cells per ring')
    ap.add_argument('--threads', default='128,256')
    ap.add_argument('--maxreg', default='0')
    ap.add_argument('--note', default='', help='recorded in the receipt (e.g. whether the GPU was idle)')
    ap.add_argument('--level1-configs', default='1x32,3x32',
                    help='rings x level-2 cells per ring, run as the level-1 automaton')
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    cand = candidates.load(args.candidate)
    p, C = cand.p, cand.c_backend()
    Q, U = p.Q, p.U
    rng = np.random.default_rng(5)
    rows = []
    cache = {}
    for cfg in args.configs.split(','):
        nr, n2 = map(int, cfg.split('x'))
        if n2 not in cache:
            top = codec.random_upper(cand, n2, rng)                 # level-2 cells
            lvl1 = codec.encode(cand, top)                          # Q * n2 level-1 cells
            cache[n2] = C.pack(codec.encode(cand, lvl1))            # Q^2 * n2 physical sites
        P = cache[n2]
        for threads in [int(x) for x in args.threads.split(',')]:
            for maxreg in [int(x) for x in args.maxreg.split(',')]:
                sim = gpu.GpuSim(cand, nr, n2 * Q, threads=threads, maxreg=maxreg or None, mode='grid')
                sim.set_state(P)
                sim.run(200)                                        # warm-up
                sim.run(args.ticks)
                us = sim.last_ms * 1000 / args.ticks
                sites = nr * n2 * Q * Q
                row = dict(rings=nr, level2_cells_per_ring=n2, sites_per_ring=n2 * Q * Q, threads=threads,
                           maxreg=maxreg, grid_blocks=sim.grid_blocks, us_per_tick=round(us, 2),
                           site_updates_per_s=round(sites / (us * 1e-6) / 1e9, 2),
                           level1_step_hours=round(U * us * 1e-6 / 3600, 3),
                           level2_step_days=round(U * U * us * 1e-6 / 86400, 1))
                rows.append(row)
                print(json.dumps(row), flush=True)
                del sim
    level1_rows = []
    for cfg in [c for c in args.level1_configs.split(',') if c]:
        nr, n2 = map(int, cfg.split('x'))
        P = C.pack(codec.encode(cand, codec.random_upper(cand, n2, rng)))   # n2 * Q level-1 cells
        sim = gpu.GpuSim(cand, nr, n2, mode='grid')
        sim.set_state(P)
        sim.run(200)
        sim.run(args.ticks)
        us = sim.last_ms * 1000 / args.ticks
        row = dict(rings=nr, level2_cells_per_ring=n2, level1_cells_per_ring=n2 * Q, us_per_tick=round(us, 2),
                   level2_step_seconds_on_level1_automaton=round(U * us * 1e-6, 1))
        level1_rows.append(row)
        print(json.dumps(row), flush=True)
        del sim
    with open(os.path.join(OUT, f'{args.candidate}_level2_bench.json'), 'w') as fh:
        json.dump(dict(candidate=args.candidate, Q=Q, U=U, W=cand.W, gates=len(cand.comp.gates),
                       gpu='A100-SXM4-80GB', date=time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime()),
                       gpu_shared_note=args.note, rows=rows, level1_automaton=level1_rows), fh, indent=1)


if __name__ == '__main__':
    main()
