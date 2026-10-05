"""Replay a job-scheduled program on neighbourhoods of a running colony.

`jobsched.replay` with random inputs almost never raises the signals that
matter most: a front arriving, the match pass, a capture, the commit. Here
the inputs are radius-5 neighbourhoods of cells of a healthy colony (one ring
of Q cells encoding a random upper cell), taken at Ages spread over the whole
work period, with the instruction word the rule looks up at each cell. For
every such neighbourhood the compiled program must write exactly the netlist's
values and leave the rule's next state in Hold: this is what a colony one
level down computes when its upper cell is that cell.

Each sampled Age contributes 64 cells: the cells within two of every front of
the comb (if the Age is inside the evaluation window), the special cells and
the colony ends, and random cells.

Usage: replay_structured.py --candidate G16 [--samples 400]
Receipt: figs/replay/<candidate>_structured.json
"""
import argparse
import json
import os
import time
import numpy as np
from gacsca import candidates, codec, gpu, jobsched, machine

OUT = os.path.join(candidates.ROOT, 'figs', 'replay')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--candidate', default=candidates.CURRENT)
    ap.add_argument('--samples', type=int, default=400)
    ap.add_argument('--seed', type=int, default=5)
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    c = candidates.load(args.candidate)
    p = c.p
    eng = jobsched.Engine(p, c.comp, c.layout, MP=p.MP, **candidates.RECIPES[args.candidate]['compile']['jobs'])
    eng.run()
    rng = np.random.default_rng(args.seed)
    pack, unpack = machine.CKernel.pack, machine.CKernel.unpack
    top = codec.random_upper(c, 1, rng)
    sim = gpu.GpuSim(c, 1, 1)
    sim.set_state(pack(codec.encode(c, top)))
    # sample Ages: evenly spread, plus every page of the evaluation window in both halves
    ages = set(int(a) for a in np.linspace(1, p.U - 2, args.samples // 2))
    ages |= {p.U - 1, 0, p.T_sig, p.T_sig + 1, p.E0 - 1}
    for pg in range(p.NP):
        for off in rng.integers(0, p.PL, size=max(1, args.samples // (2 * p.NP))):
            ages.add(p.E0 + pg * p.PL + int(off))
    ages = sorted(ages)
    special = [3, p.Q - 3, p.lo, p.hi - 1, 0, p.Q - 1, p.lo - 1, p.hi]
    t0 = time.time()
    now = 0
    bad = arrivals = matched = vectors = 0
    pages = set()
    for a in ages:
        sim.run(a - now)
        now = a
        X = unpack(sim.state()[0], p.Q)
        cells = list(special)
        pg, tk = divmod(a - p.E0, p.PL)
        if 0 <= pg < p.NP:
            pages.add(int(pg))
            tt = tk if pg % 2 == 0 else p.PL - 1 - tk
            for j in range(p.fronts):
                x = p.lo - p.H + tt + j * p.delta
                cells += [x + e for e in range(-2, 3) if 0 <= x + e < p.Q]
        cells = list(dict.fromkeys(cells))
        extra = [int(x) for x in rng.permutation(p.Q) if x not in cells][:64 - len(cells)]
        cells = np.array(cells + extra)
        inputs = jobsched.neighbourhood_vectors(c, X, cells)
        arr = inputs_arrive(c, X, cells)
        arrivals += int(arr.sum())
        if pg == p.MP:
            matched += int(arr.sum())
        vectors += len(cells)
        bad += jobsched.replay(p, eng, inputs=inputs)
    rec = dict(candidate=args.candidate, candidate_sha256=c.digest(), ages=len(ages), neighbourhoods=vectors,
               with_an_arriving_front=arrivals, of_which_in_the_match_pass=matched,
               pages_of_the_window_sampled=len(pages), passes=p.NP, mismatches=bad,
               seconds=round(time.time() - t0))
    print(json.dumps(rec))
    with open(os.path.join(OUT, f'{args.candidate}_structured.json'), 'w') as fh:
        json.dump(rec, fh, indent=1)


def inputs_arrive(c, X, cells):
    """The rule's `arrive` output at the given cells of state X."""
    vals = {}
    N = X.shape[1]
    for name in c.comp.inputs:
        if name[0] == 'x':
            _, j, f, i = name
            vals[name] = X[c.row[(f, i)], (cells + j) % N]
        else:
            vals[name] = np.zeros(len(cells), dtype=bool)
    return c.comp.evaluate(vals, bool)[('arrive', 0)].astype(bool)


if __name__ == '__main__':
    main()
