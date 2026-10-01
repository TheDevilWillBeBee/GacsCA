"""Level-0 errors and Gray's one-tick property (Prop. 4, level 0).

Gray's Proposition 4 for a level-0 error at (x, t): outside the box
[x, x+1] x [t, t] the simulation-structure fields equal the error-free run,
i.e. one tick after the error the whole state is exact again. This driver
injects single level-0 errors (one site, or two adjacent sites, given an
arbitrary value) into a healthy two-colony ring at random times of the work
period, runs one tick and compares every field of every site with the
error-free run. Failures are listed with the differing (site, field).

Usage: level0_one_tick.py --candidate G14 --trials 2000 [--mode random] [--healthy]

--healthy uses a slice of a healthy upper colony and hits only its middle
colonies. Two random upper cells are not a healthy upper colony: their
upper rule raises Flag1, the trickle-down window then raises the computed
Flag1 of the physical cells, and Gray's second special rule (p. 33) zeroes
the simulation structure of a cell whose stored Address was hit; that cell
is restored one tick later (a two-tick footprint at the hit site only).
Receipt: figs/level0/<tag>.json
"""
import argparse
import json
import os
import time
from collections import Counter
import numpy as np
from gacsca import candidates, codec

OUT = os.path.join(candidates.ROOT, 'figs', 'level0')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--candidate', default='G14')
    ap.add_argument('--trials', type=int, default=2000)
    ap.add_argument('--times', type=int, default=40, help='distinct ticks of the work period sampled')
    ap.add_argument('--mode', default='random', choices=('random', 'invert', 'zero', 'one'))
    ap.add_argument('--pair', type=float, default=0.5, help='probability of a two-site error')
    ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--healthy', action='store_true',
                    help='a slice of a healthy upper colony instead of 2 random upper cells')
    ap.add_argument('--slice', type=int, default=16)
    ap.add_argument('--tag', default='')
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    c = candidates.load(args.candidate)
    p, C = c.p, c.c_backend()
    rng = np.random.default_rng(args.seed)
    if args.healthy:
        # a slice of a healthy upper colony (coherent Address/Age, flags 0);
        # errors go only into the middle colonies, far from the slice's ends
        top = codec.random_upper(c, 1, rng)
        full = codec.encode(c, top)
        n = args.slice
        up = full[:, (np.arange(n) + p.Q // 2 - n // 2) % p.Q]
        lo_site, hi_site = (n // 2 - 1) * p.Q, (n // 2 + 1) * p.Q - 1
    else:
        up = codec.random_upper(c, 2, rng)
        lo_site, hi_site = 0, 2 * p.Q - 1
    X0 = codec.encode(c, up)
    N = X0.shape[1]
    times = np.sort(rng.integers(0, p.U - 1, args.times))
    fields = [(f, cr) for f, w in c.schema for cr in [c.row[(f, 0)]]]
    row_field = np.empty(c.W, dtype=object)
    for f, w in c.schema:
        r0 = c.row[(f, 0)]
        row_field[r0:r0 + w] = f
    per = args.trials // len(times)
    fails, by_field, by_phase = [], Counter(), Counter()
    total = 0
    t_start = time.time()
    P = C.pack(X0)
    t_prev = 0
    for t in times:
        P = C.run_packed(P, int(t - t_prev), threads=4)
        t_prev = int(t)
        X = C.unpack(P, N)
        ref1 = C.unpack(C.run_packed_scalar(P.copy(), 1), N)
        for _ in range(per):
            x = int(rng.integers(lo_site, hi_site))
            sites = [x, x + 1] if rng.random() < args.pair else [x]
            Y = X.copy()
            for s in sites:
                if args.mode == 'random':
                    Y[:, s] = rng.random(c.W) < 0.5
                elif args.mode == 'invert':
                    Y[:, s] = ~Y[:, s]
                elif args.mode == 'zero':
                    Y[:, s] = False
                else:
                    Y[:, s] = True
            Y1 = C.unpack(C.run_packed_scalar(C.pack(Y), 1), N)
            d = Y1 != ref1
            total += 1
            if d.any():
                rows, cols = np.nonzero(d)
                fl = sorted(set(row_field[rows]))
                for f in fl:
                    by_field[f] += 1
                age = int(c.field(X[:, [x]], 'age')[0]) if 'age' in dict(c.schema) else None
                by_phase[int(t) * 8 // p.U] += 1
                if len(fails) < 40:
                    fails.append(dict(t=int(t), sites=sites, fields=fl, n_bits=int(d.sum()),
                                      differing_sites=sorted(set(cols.tolist()))[:12]))
    rec = dict(candidate=args.candidate, mode=args.mode, healthy=args.healthy, trials=total, failures=len(fails) and sum(by_phase.values()),
               failure_rate=sum(by_phase.values()) / max(1, total), by_field=dict(by_field),
               by_eighth_of_period=dict(by_phase), examples=fails, seconds=round(time.time() - t_start))
    tag = args.tag or f'{args.candidate}_{args.mode}_{"healthy" if args.healthy else "anyflags"}_seed{args.seed}'
    with open(os.path.join(OUT, tag + '.json'), 'w') as fh:
        json.dump(rec, fh, indent=1)
    print(json.dumps({k: v for k, v in rec.items() if k != 'examples'}))
    for e in fails[:8]:
        print(e)


if __name__ == '__main__':
    main()
