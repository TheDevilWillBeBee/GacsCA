"""Bounded three-level vertical slice (not a level-3 macrostep).

top (n3 random cells) -> level 2 = encode(top) -> level 1 = encode(level 2)
-> level 0 = encode(level 1), all with the same encode function, width and
rule. The physical ring (n3 * Q^3 sites) is evolved by the C kernel only. After
every U physical ticks it is decoded and compared with the rule applied to
the previous level-1 ring (NumPy, full lookup). The level-1 ring is itself
checked to decode, at step 0, to the level-2 ring, and that to the top.

A level-2 macrostep needs U^2 and a level-3 macrostep U^3 physical ticks; this
slice checks only the first `--steps` level-1 steps of the three-level tower.
"""
import argparse
import hashlib
import json
import os
import time
import numpy as np
from gacsca.fixed_rule.design_optimization import candidates, codec

OUT = os.path.join(candidates.ROOT, 'figs', 'fixed_rule', 'design_optimization', 'three_level')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--candidate', default='R1')
    ap.add_argument('--n3', type=int, default=1)
    ap.add_argument('--steps', type=int, default=8)
    ap.add_argument('--threads', type=int, default=16)
    ap.add_argument('--seed', type=int, default=0)
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    cand = candidates.load(args.candidate)
    p, C = cand.p, cand.c_backend()
    rng = np.random.default_rng(args.seed)
    top = codec.random_upper(cand, args.n3, rng)
    l2 = codec.encode(cand, top)
    l1 = codec.encode(cand, l2)
    l0 = codec.encode(cand, l1)
    assert np.array_equal(codec.decode(cand, l0), l1)
    assert np.array_equal(codec.decode(cand, l1), l2)
    assert np.array_equal(codec.decode(cand, l2), top)
    widths = [x.shape[0] for x in (top, l2, l1, l0)]
    assert len(set(widths)) == 1
    rec = dict(candidate=args.candidate, identity={k: v for k, v in candidates.summary(cand).items()
                                                    if k != 'schema'},
               c_kernel_source_sha256=C.source_sha256, n3=args.n3, seed=args.seed,
               sites=dict(top=top.shape[1], level2=l2.shape[1], level1=l1.shape[1],
                          level0=l0.shape[1]),
               width_all_levels=widths[0], steps=[])
    P = C.pack(l0)
    t0 = time.time()
    for step in range(1, args.steps + 1):
        a = time.time()
        P = C.run_packed(P, p.U, threads=args.threads)
        dt = time.time() - a
        l1_next = cand.step_numpy(l1)
        X = C.unpack(P, l0.shape[1])
        dec = codec.decode(cand, X)
        health = codec.colony_health(cand, X)
        ok = bool(np.array_equal(dec, l1_next))
        rec['steps'].append(dict(level1_step=step, equal=ok, changed_bits=int((l1_next != l1).sum()),
                                 physical_seconds=round(dt, 1), health=health))
        print(json.dumps(rec['steps'][-1]), flush=True)
        if not ok:
            break
        l1 = l1_next
    rec.update(wall_seconds=round(time.time() - t0, 1),
               final_sha256=hashlib.sha256(P.tobytes()).hexdigest())
    with open(os.path.join(OUT, f'{args.candidate}_n3_{args.n3}_seed{args.seed}.json'), 'w') as fh:
        json.dump(rec, fh, indent=1)


if __name__ == '__main__':
    main()
