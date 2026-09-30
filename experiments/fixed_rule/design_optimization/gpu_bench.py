"""Bounded CUDA check of a front candidate (run only in an acknowledged window).

1. Parity: CUDA and C (scalar) agree on every raw bit after a few ticks of
   arbitrary states with many front arrivals.
2. Closure: one full work period on the GPU decodes to the rule upstairs.
3. Throughput on a few ring sizes, measured with CUDA events.
"""
import argparse
import json
import os
import time
import numpy as np
from gacsca.fixed_rule.design_optimization import candidates, codec, cuda_backend

OUT = os.path.join(candidates.ROOT, 'figs', 'fixed_rule', 'design_optimization', 'gpu')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--candidate', default='R1')
    ap.add_argument('--sizes', default='128,384')
    ap.add_argument('--ticks', type=int, default=4096)
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    cand = candidates.load(args.candidate)
    p = cand.p
    C = cand.c_backend()
    G = cuda_backend.CudaKernel(cand)
    rec = dict(candidate=args.candidate, cuda_source_sha256=G.source_sha256)
    rng = np.random.default_rng(71)
    N = 8 * p.Q
    X = rng.random((cand.W, N)) < 0.5
    cand.set_field(X, 'age', rng.integers(p.E0, p.E0 + p.NP * p.Q, size=N))
    P = C.pack(X)
    for ticks in (1, 3, 17):
        a = C.run_packed_scalar(P.copy(), ticks)
        b = G.run_packed(P, ticks)
        assert np.array_equal(a, b), ('parity', ticks)
    rec['parity_arbitrary_ticks'] = [1, 3, 17]
    up = codec.random_upper(cand, 12, rng)
    P = C.pack(codec.encode(cand, up))
    t = time.time()
    Pg = G.run_packed(P, p.U)
    rec['closure_period_seconds'] = round(time.time() - t, 2)
    rec['closure_equal'] = bool(np.array_equal(codec.decode(cand, C.unpack(Pg, 12 * p.Q)),
                                               cand.step_numpy(up)))
    bench = []
    for n1 in [int(x) for x in args.sizes.split(',')]:
        up = codec.random_upper(cand, n1, rng)
        P = C.pack(codec.encode(cand, up))
        for threads in (128, 256, 512, 1024):
            if threads > P.shape[1] and threads > 128:
                continue
            G.run_packed(P, args.ticks, threads=threads)
            bench.append(dict(colonies=n1, sites=n1 * p.Q, threads=threads,
                              us_per_tick=round(G.last_ms * 1000 / args.ticks, 3)))
            print(json.dumps(bench[-1]), flush=True)
    rec['throughput'] = bench
    with open(os.path.join(OUT, f'{args.candidate}_gpu.json'), 'w') as fh:
        json.dump(rec, fh, indent=1)
    print(json.dumps({k: rec[k] for k in ('candidate', 'parity_arbitrary_ticks', 'closure_equal',
                                           'closure_period_seconds')}))


if __name__ == '__main__':
    main()
