"""Preliminary level-0 fault probe (not a noise-robustness claim).

During one continuous work period of a candidate, flip single physical bits
of one field class at sparse random (site, tick) points, far apart in space
and time. The physical ring is still evolved only by the C kernel; faults are
applied between kernel calls. At the boundary the decoded upper ring is
compared with the fault-free rule applied upstairs.

This measures which stored fields a candidate's redundancy absorbs on the
healthy path. It does not test bursts, damaged-colony repair, trickle-down
repair, or the hierarchy's noise threshold.
"""
import argparse
import json
import os
import time
import numpy as np
from gacsca.fixed_rule.design_optimization import candidates, codec

OUT = os.path.join(candidates.ROOT, 'figs', 'fixed_rule', 'design_optimization', 'noise_probe')

CLASSES = {
    'storage': ('info', 'hold', 'h1', 'h2', 'ln', 'scr', 'mr', 'ml'),
    'front': ('reg', 'pend', 'pkind', 'pval'),
    'geometry': ('addr', 'age'),
    'flags': ('f1', 'f2', 'wf1', 'wf2'),
    # register bit at the cell currently holding the front, in one colony
    'front-targeted': ('reg',),
    # stored Age / Address bit at the cell the front arrives at on the next tick
    'age-at-front': ('age',),
    'addr-at-front': ('addr',),
    # stored Age bit anywhere during the gather window (Age < 5Q + skew)
    'age-in-gather': ('age',),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--candidate', default='G1')
    ap.add_argument('--klass', choices=sorted(CLASSES), default='storage')
    ap.add_argument('--flips', type=int, default=50, help='faults per period')
    ap.add_argument('--trials', type=int, default=4)
    ap.add_argument('--colonies', type=int, default=12)
    ap.add_argument('--threads', type=int, default=8)
    ap.add_argument('--seed', type=int, default=0)
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    cand = candidates.load(args.candidate)
    p, C = cand.p, cand.c_backend()
    rows = [r for r, (f, _) in enumerate(cand.rows) if f in CLASSES[args.klass]]
    n1 = args.colonies
    N = n1 * p.Q
    rng = np.random.default_rng(args.seed)
    results = []
    for trial in range(args.trials):
        up = codec.random_upper(cand, n1, rng)
        ref = cand.step_numpy(up)
        P = C.pack(codec.encode(cand, up))
        lo, hi = (1, p.U - 1)
        if args.klass in ('front-targeted', 'age-at-front', 'addr-at-front'):
            D = getattr(p, 'D', 1)
            lo, hi = p.E0 + 1, p.E0 + p.NP * D * p.Q - 2
        elif args.klass == 'age-in-gather':
            lo, hi = 1, p.E0 - 1
        ticks = np.sort(rng.choice(np.arange(lo, hi), size=args.flips, replace=False))
        age = 0
        faults = []
        for t in ticks:
            P = C.run_packed(P, int(t) - age, threads=args.threads)
            age = int(t)
            r = int(rng.choice(rows))
            site = int(rng.integers(0, N))
            if args.klass in ('front-targeted', 'age-at-front', 'addr-at-front'):
                # front-targeted: the cell the front arrived at on the tick into
                # Age t; age/addr-at-front: the cell it arrives at on the next tick
                D = getattr(p, 'D', 1)
                k_ = int(t) - 1 - p.E0 + (0 if args.klass == 'front-targeted' else 1)
                page, pos = divmod(k_, D * p.Q)
                x = pos // D
                if page % 2:
                    x = p.Q - 1 - x
                site = int(rng.integers(0, n1)) * p.Q + x
            P[r, site // 64] ^= np.uint64(1) << np.uint64(site % 64)
            faults.append((int(t), cand.rows[r][0], site))
        P = C.run_packed(P, p.U - age, threads=args.threads)
        X = C.unpack(P, N)
        dec = codec.decode(cand, X)
        bad = np.argwhere(dec != ref)
        health = codec.colony_health(cand, X)
        results.append(dict(trial=trial, exact=bool(len(bad) == 0), wrong_bits=int(len(bad)),
                            wrong_colonies=int(len(set(int(c) for _, c in bad))),
                            health=health))
        print(json.dumps(results[-1]), flush=True)
    summary = dict(candidate=args.candidate, klass=args.klass, fields=CLASSES[args.klass],
                   flips_per_period=args.flips, trials=args.trials, colonies=n1,
                   exact_periods=sum(r['exact'] for r in results), results=results)
    path = os.path.join(OUT, f'{args.candidate}_{args.klass}_f{args.flips}_s{args.seed}.json')
    with open(path, 'w') as fh:
        json.dump(summary, fh, indent=1)
    print(json.dumps({k: summary[k] for k in ('candidate', 'klass', 'flips_per_period',
                                               'trials', 'exact_periods')}))


if __name__ == '__main__':
    main()
