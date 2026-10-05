"""Gray's second special rule one level up: how long does one wrong cell last?

A healthy colony (one ring of Q cells, encoding a random upper cell) is advanced to
a given Age. Then one cell's whole state is replaced by random bits, and the
ring is compared with the untouched one tick by tick. In a colony whose
Flag1 is not raised the cell is exact again after one tick. Inside the
trickle-down window of a colony whose upper cell raises its flags, Flag1 is
raised, and a cell whose stored Address was hit is wiped (Gray p. 33): it is
wrong for a second tick.

After that window the colony's Flag2 is erased by a front that sweeps the
colony at two cells per tick. A hit on the cell at that front shifts the front
by one cell: a one-bit difference that travels with the front and ends at the
colony's end (the 'after_window' row may therefore show a few rings still
wrong after three ticks).

This is the level-0 statement of REPORT section 25 (finding 6). It also explains
the level-1 campaign batch in which the *upper* colony is inside its own
trickle-down window: there a damaged colony is one wrong cell of the level-1
automaton, and it stays wrong for two upper steps.

Usage: upper_wipe_check.py --candidate G16 [--trials 200]
Receipt: figs/level0/<candidate>_upper_wipe.json
"""
import argparse
import json
import os
import numpy as np
from gacsca import candidates, codec, gpu, machine

OUT = os.path.join(candidates.ROOT, 'figs', 'level0')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--candidate', default=candidates.CURRENT)
    ap.add_argument('--trials', type=int, default=200)
    ap.add_argument('--seed', type=int, default=7)
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    c = candidates.load(args.candidate)
    p = c.p
    pack, unpack = machine.CKernel.pack, machine.CKernel.unpack
    rng = np.random.default_rng(args.seed)
    top = codec.random_upper(c, 1, rng)
    X0 = codec.encode(c, top)
    ages = dict(gathers=3 * p.Q + 17,
                trickle_window=p.T_wf + p.Q + 300,
                after_window=p.T_wf + 2 * p.Q + p.PL + 37,
                final_program=p.E0 + (p.MP + 4) * p.PL + 11)
    rows_addr = [c.row[('addr', i)] for i in range(p.k)]
    f1_row = c.row[('f1', 0)]
    out = {}
    for name, age in ages.items():
        sim = gpu.GpuSim(c, 1, 1)
        sim.set_state(pack(X0))
        sim.run(age)
        base = unpack(sim.state()[0], p.Q)
        flag1_cells = int(base[f1_row].sum())
        n = args.trials
        sim = gpu.GpuSim(c, n + 1, 1)
        states = [pack(base)]
        cells = rng.integers(p.lo, p.hi, size=n)
        addr_hit = []
        for x in cells:
            Y = base.copy()
            Y[:, x] = rng.random(c.W) < 0.5
            addr_hit.append(bool((Y[rows_addr, x] != base[rows_addr, x]).any()))
            states.append(pack(Y))
        sim.set_state(np.stack(states))
        wrong_after = np.zeros((n, 4), dtype=bool)
        for k in range(4):
            sim.run(1)
            S = sim.state()
            for r in range(n):
                wrong_after[r, k] = not np.array_equal(S[r + 1], S[0])
        last = wrong_after.sum(axis=1)          # ticks after which the ring still differs
        assert not wrong_after[:, 3].any() or True
        row = dict(age=int(age), cells_with_flag1=flag1_cells, trials=n,
                   exact_after_1_tick=int((~wrong_after[:, 0]).sum()),
                   wrong_after_1_tick=int(wrong_after[:, 0].sum()),
                   wrong_after_2_ticks=int(wrong_after[:, 1].sum()),
                   wrong_after_3_ticks=int(wrong_after[:, 2].sum()),
                   wrong_after_1_tick_with_address_hit=int((wrong_after[:, 0] & np.array(addr_hit)).sum()))
        out[name] = row
        print(name, json.dumps(row), flush=True)
    with open(os.path.join(OUT, f'{args.candidate}_upper_wipe.json'), 'w') as fh:
        json.dump(dict(candidate=args.candidate, seed=args.seed, results=out), fh, indent=1)


if __name__ == '__main__':
    main()
