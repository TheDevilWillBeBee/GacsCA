"""A ring of one level-2 cell on the level-1 automaton: where does damage persist?

`level1_campaign.py --continue-level2` follows a damaged level-2 colony that is
its own neighbour. There the level-2 state has no healthy copies elsewhere: the
five "copies" of a logical bit are five slots of the same cell, and for a random
level-2 cell they do not agree. A wrong slot can then tip a 3:2 majority, and
the difference stays for ever. This is a property of the one-cell ring, not of
the candidate; `three_level_g.py repair2` uses a ring of healthy level-2 cells.

This driver measures how often it happens, for stretches of damaged level-1
cells at random places: the stretch gets random states at a given level-1 Age,
and the ring is compared with the untouched one at the next two level-2
boundaries.

Usage: level2_single_ring.py --candidate G16 [--trials 100]
Receipt: figs/three_level/<candidate>_single_ring.json
"""
import argparse
import json
import os
import numpy as np
from gacsca import candidates, codec, gpu, machine

OUT = os.path.join(candidates.ROOT, 'figs', 'three_level')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--candidate', default=candidates.CURRENT)
    ap.add_argument('--trials', type=int, default=100)
    ap.add_argument('--seed', type=int, default=7)
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    c = candidates.load(args.candidate)
    p = c.p
    pack, unpack = machine.CKernel.pack, machine.CKernel.unpack
    rng = np.random.default_rng(args.seed)
    top = codec.random_upper(c, 1, rng)
    X0 = codec.encode(c, top)
    n = args.trials
    out = {}
    for name, age in (('gathers', 2), ('program', p.E0 + (p.MP + 3) * p.PL + 50)):
        for width in (9, 21):
            sim = gpu.GpuSim(c, 1, 1)
            sim.set_state(pack(X0))
            sim.run(age)
            base = unpack(sim.state()[0], p.Q)
            starts = rng.integers(p.lo, p.hi - width, size=n)
            states = [pack(base)]
            for x in starts:
                Y = base.copy()
                Y[:, x:x + width] = rng.random((c.W, width)) < 0.5
                states.append(pack(Y))
            sim = gpu.GpuSim(c, n + 1, 1)
            sim.set_state(np.stack(states), t=age)
            rows = []
            t = age
            for b in (1, 2):
                sim.run(b * p.U - t)
                t = b * p.U
                S = sim.state()
                ref = unpack(S[0], p.Q)
                d0 = codec.decode(c, ref)
                same = bits = 0
                for r in range(n):
                    Y = unpack(S[r + 1], p.Q)
                    if np.array_equal(Y, ref):
                        same += 1
                    elif (codec.decode(c, Y) != d0).any():
                        bits += 1
                rows.append(dict(boundary=b, identical=same, level2_state_wrong=bits))
            out[f'{name}_width{width}'] = dict(level1_age=int(age), trials=n, boundaries=rows)
            print(args.candidate, name, 'width', width, json.dumps(rows), flush=True)
    with open(os.path.join(OUT, f'{args.candidate}_single_ring.json'), 'w') as fh:
        json.dump(dict(candidate=args.candidate, seed=args.seed, results=out), fh, indent=1)


if __name__ == '__main__':
    main()
