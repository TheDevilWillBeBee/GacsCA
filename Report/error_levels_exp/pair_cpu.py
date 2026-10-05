"""How far apart must two level-0 errors be for this rule to remove both? (CPU, C kernel)

Gray's level-0 class asks for (24, 24)-separation. Here two errors, each one site or two
adjacent sites with the whole state replaced by random bits, are injected into the middle
colonies of a healthy slice ring with a gap of g clean sites between them and dt ticks
apart. The state is compared with the error-free run k = 1..K ticks after the second error.

Reported per (g, dt): trials, and how many are bit-identical to the reference after
1, 2, 3 and K ticks.  g < 24 with dt < 24 is a pair Gray's definition does not call two
level-0 errors (it is a candidate level-1 error).

Run from errlevels/repo:  PYTHONPATH=. python3 ../pair_cpu.py --candidate G16
"""
import argparse
import json
import os
import time
from multiprocessing import Pool
import numpy as np
from gacsca import candidates, codec

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'results')
G = {}


def setup(name, n, seed):
    cand = candidates.load(name, check_manifest=False)
    p, C = cand.p, cand.c_backend()
    rng = np.random.default_rng(seed)
    top = codec.random_upper(cand, 1, rng)
    full = codec.encode(cand, top)
    up = full[:, (np.arange(n) + p.Q // 2 - n // 2) % p.Q]
    G.update(cand=cand, p=p, C=C, n=n, N=n * p.Q, X0=codec.encode(cand, up))


def work(args):
    times, gaps, dts, per, K, seed, width = args
    cand, p, C, n, N = G['cand'], G['p'], G['C'], G['n'], G['N']
    rng = np.random.default_rng(seed)
    lo_site, hi_site = (n // 2 - 1) * p.Q, (n // 2 + 1) * p.Q - 60
    res = {}
    P = C.pack(G['X0'])
    t_prev = 0
    maxdt = max(dts)
    for t in times:
        P = C.run_packed(P, int(t - t_prev), 1)
        t_prev = int(t)
        # reference trajectory for maxdt + K ticks
        refs = [P.copy()]
        R = P.copy()
        for _ in range(maxdt + K):
            R = C.run_packed(R, 1, 1)
            refs.append(R.copy())
        X = C.unpack(P, N)
        for g in gaps:
            for dt in dts:
                key = f'{g},{dt}'
                r = res.setdefault(key, dict(trials=0, clean=[0] * K, example=None))
                for _ in range(per):
                    x = int(rng.integers(lo_site, hi_site))
                    w1 = width or int(rng.integers(1, 3))
                    w2 = width or int(rng.integers(1, 3))
                    s1 = list(range(x, x + w1))
                    s2 = list(range(x + w1 + g, x + w1 + g + w2))
                    Y = X.copy()
                    for s in s1:
                        Y[:, s] = rng.random(cand.W) < 0.5
                    if dt == 0:
                        for s in s2:
                            Y[:, s] = rng.random(cand.W) < 0.5
                        Pf = C.pack(Y)
                    else:
                        Pf = C.run_packed(C.pack(Y), dt, 1)
                        Y = C.unpack(Pf, N)
                        for s in s2:
                            Y[:, s] = rng.random(cand.W) < 0.5
                        Pf = C.pack(Y)
                    r['trials'] += 1
                    for k in range(1, K + 1):
                        Pf = C.run_packed(Pf, 1, 1)
                        if np.array_equal(Pf, refs[dt + k]):
                            for kk in range(k, K + 1):
                                r['clean'][kk - 1] += 1
                            break
                    else:
                        if r['example'] is None:
                            d = Pf ^ refs[dt + K]
                            rows = np.nonzero(d.any(axis=1))[0]
                            r['example'] = dict(t=int(t), sites=[s1, s2],
                                                fields=sorted({cand.rows[i][0] for i in rows}))
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--candidate', default='G16')
    ap.add_argument('--colonies', type=int, default=16)
    ap.add_argument('--gaps', default='0,1,2,3,4,5,6,7,8,9,10,11,12,16,23')
    ap.add_argument('--dts', default='0,1,2,3')
    ap.add_argument('--times', type=int, default=48)
    ap.add_argument('--per', type=int, default=4)
    ap.add_argument('--K', type=int, default=6)
    ap.add_argument('--width', type=int, default=0, help='sites per error (0: one or two at random)')
    ap.add_argument('--seed', type=int, default=3)
    ap.add_argument('--workers', type=int, default=4)
    ap.add_argument('--tag', default='')
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    setup(args.candidate, args.colonies, args.seed)
    p = G['p']
    rng = np.random.default_rng(args.seed)
    times = np.sort(rng.integers(1, p.U - 20, args.times))
    gaps = [int(x) for x in args.gaps.split(',')]
    dts = [int(x) for x in args.dts.split(',')]
    chunks = [times[i::args.workers] for i in range(args.workers)]
    t0 = time.time()
    with Pool(args.workers, initializer=setup, initargs=(args.candidate, args.colonies, args.seed)) as pool:
        parts = pool.map(work, [(c, gaps, dts, args.per, args.K, args.seed * 100 + i, args.width)
                                for i, c in enumerate(chunks)])
    tot = {}
    for part in parts:
        for key, r in part.items():
            a = tot.setdefault(key, dict(trials=0, clean=[0] * args.K, example=None))
            a['trials'] += r['trials']
            a['clean'] = [u + v for u, v in zip(a['clean'], r['clean'])]
            a['example'] = a['example'] or r['example']
    out = dict(candidate=args.candidate, Q=p.Q, U=p.U, colonies=args.colonies, K=args.K, width=args.width,
               times=[int(t) for t in times], results=tot, seconds=round(time.time() - t0))
    tag = args.tag or args.candidate
    with open(os.path.join(OUT, f'pair_{tag}.json'), 'w') as fh:
        json.dump(out, fh, indent=1)
    print(f'{"gap":>4} {"dt":>3} {"trials":>6}  clean after 1..K ticks')
    for g in gaps:
        for dt in dts:
            r = tot[f'{g},{dt}']
            print(f'{g:>4} {dt:>3} {r["trials"]:>6}  {r["clean"]}  {r["example"] or ""}')


if __name__ == '__main__':
    main()
