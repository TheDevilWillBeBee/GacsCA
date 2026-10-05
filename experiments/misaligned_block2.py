"""The misaligned-colony race one level up (REPORT section 33).

Section 32 measured, at level 0, how long a burst must hold a block of shifted Addresses across a
colony boundary before the block becomes a whole misaligned colony that level-0 rules cannot
erode: (5/6)(Q - w) ticks for a block with w cells inside the burst, from the damage front's
speed (3 cells per tick) and the fall-back of Flag1 (2 per tick). This driver repeats the
experiment on the level-1 automaton: the same rule on a ring of n2 * Q level-1 cells (n2
consecutive level-2 cells of a healthy level-3 colony). For `height` level-1 steps the burst
replaces the level-1 cells of a box across the boundary between the two middle level-2 cells by
the level-1 cells 2Q + `shift` positions to the right (plausible states, Addresses off by
`shift`), so that the block's apparent colony boundary lies `shift` cells left of the real one,
inside the box. Recorded: the level-1 cells whose Address differs from the error-free ring (count,
longest run, left and right end), every `--stride` level-1 steps from the first burst on, and the
level-2 state at the next level-2 boundaries.

Usage: misaligned_block2.py --candidate G17 [--shifts 32,96,160] [--heights 10,30,70,150,300]
Receipt: figs/three_level/<candidate>_misaligned_block2.json
"""
import argparse
import json
import os
import time
import numpy as np
from gacsca import candidates, codec, gpu

OUT = os.path.join(candidates.ROOT, 'figs', 'three_level')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--candidate', default=candidates.CURRENT)
    ap.add_argument('--n2', type=int, default=32)
    ap.add_argument('--shifts', default='32,96,160')
    ap.add_argument('--widths', default='72,200')
    ap.add_argument('--heights', default='10,30,70,150,300')
    ap.add_argument('--starts', default='', help='level-1 ages at which the bursts begin')
    ap.add_argument('--reach', type=int, default=10)
    ap.add_argument('--periods', type=int, default=4, help='level-2 steps to follow')
    ap.add_argument('--stride', type=int, default=8)
    ap.add_argument('--seed', type=int, default=11)
    ap.add_argument('--tag', default='')
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    cand = candidates.load(args.candidate)
    p, C = cand.p, cand.c_backend()
    Q, U = p.Q, p.U
    rng = np.random.default_rng(args.seed)
    n2 = args.n2
    n3 = max(1, -(-n2 // Q))                            # level-3 cells needed for n2 level-2 cells
    colony2 = codec.encode(cand, codec.random_upper(cand, n3, rng))
    # the middle of the ring is the middle (Address Q/2) of a level-2 colony
    L2 = colony2[:, (np.arange(n2) + Q // 2 - n2 // 2) % (n3 * Q)]
    L1 = codec.encode(cand, L2)
    N = n2 * Q
    b = (n2 // 2) * Q
    starts = [int(x) for x in args.starts.split(',')] if args.starts else [2000, p.T_wf + 2 * Q + 500]
    cases = []
    for t0 in starts:
        for shift in [int(x) for x in args.shifts.split(',')]:
            for w in [int(x) for x in args.widths.split(',')]:
                if w <= shift + args.reach:
                    continue
                for h in [int(x) for x in args.heights.split(',')]:
                    cases.append(dict(shift=shift, width=w, height=h, start=t0, x0=b + args.reach - w))
    print(len(cases), 'cases', flush=True)
    t_start = time.time()
    sim = gpu.GpuSim(cand, 1 + len(cases), n2, mode='grid')
    pack, unpack = C.pack, C.unpack
    # all rings start at the earliest burst; bursts begin later are advanced in lockstep
    t_min = min(cs['start'] for cs in cases)
    X = L1
    if t_min:
        sim.set_state(pack(X))
        sim.run(t_min)
        X = unpack(sim.state()[0], N)
    states = [X.copy() for _ in range(1 + len(cases))]
    addr_rows = [cand.row[('addr', i)] for i in range(p.k)]
    series = [[] for _ in cases]
    t = t_min
    t_end = max(cs['start'] + cs['height'] for cs in cases)
    sim.set_state(np.stack([pack(s) for s in states]))
    print('bursts from', t_min, 'to', t_end, flush=True)
    prev = {i: states[i + 1] for i in range(len(cases))}       # a burst ring's state before the step
    while t < t_end:
        sim.run(1)
        t += 1
        S = sim.state()
        active = [i for i, cs in enumerate(cases) if cs['start'] < t <= cs['start'] + cs['height']]
        for i in active:
            cs = cases[i]
            Xi = unpack(S[i + 1], N)
            src = (np.arange(cs['x0'], cs['x0'] + cs['width']) + 2 * Q + cs['shift']) % N
            Xi[:, cs['x0']:cs['x0'] + cs['width']] = prev[i][:, src]
            S[i + 1] = pack(Xi)
            prev[i] = Xi
        for i in range(len(cases)):
            if i not in active and cases[i]['start'] >= t:
                prev[i] = unpack(S[i + 1], N)
        if active:
            sim.set_state(S, t)
        if t % args.stride == 0:                             # the Addresses during and right after the bursts
            bits = np.unpackbits(S[:, addr_rows].view(np.uint8).reshape(S.shape[0], len(addr_rows), -1),
                                 axis=2, bitorder='little').astype(bool)[:, :, :N]
            for i in range(len(cases)):
                d = (bits[i + 1] != bits[0]).any(axis=0)
                if d.any() or (series[i] and series[i][-1][1]):
                    series[i].append((t, int(d.sum()), _longest(d)) + _span(d, b))
    bounds = [[] for _ in cases]
    t_stop = ((t_min // U) + args.periods + 1) * U
    assert U % args.stride == 0
    if t % args.stride:                                  # align the samples with the boundaries
        sim.run(args.stride - t % args.stride)
        t += args.stride - t % args.stride
    NW = sim.NW
    while t < t_stop:
        m = min(U - t % U, (U // 8 // args.stride) * args.stride)
        snap = sim.run(m, rows=addr_rows, stride=args.stride)      # (m // stride, rings, rows, NW)
        bits = np.unpackbits(snap.view(np.uint8).reshape(snap.shape[0], snap.shape[1], len(addr_rows), -1),
                             axis=3, bitorder='little').astype(bool)[:, :, :, :N]
        for k in range(bits.shape[0]):
            tt = t + (k + 1) * args.stride
            for i in range(len(cases)):
                d = (bits[k, i + 1] != bits[k, 0]).any(axis=0)
                if d.any() or (series[i] and series[i][-1][1]):
                    series[i].append((tt, int(d.sum()), _longest(d)) + _span(d, b))
        t += m
        if t % U == 0:
            S = sim.state()
            for r in range(1 + len(cases)):
                states[r] = unpack(S[r], N)
            dref = codec.decode(cand, states[0])
            for i in range(len(cases)):
                dec = codec.decode(cand, states[i + 1])
                wrong = (np.flatnonzero((dec != dref).any(axis=0)) - n2 // 2).tolist()
                bounds[i].append(dict(level2_boundary=t // U, level2_cells_wrong=wrong,
                                      level1_cells_differing=int((states[i + 1] != states[0]).any(axis=0).sum())))
            print(f'level-2 boundary {t // U} ({time.time() - t_start:.0f} s)', flush=True)
    rows = []
    for i, cs in enumerate(cases):
        end = cs['start'] + cs['height']
        after = [s for s in series[i] if s[0] > end]
        last = max([s[0] for s in after if s[1]], default=end)
        full = [s[0] for s in after if s[2] >= Q - 10]
        row = dict(cs, burst_end=end, addresses_wrong_until=last, steps_after_burst=last - end,
                   full_block_steps=(max(full) - end) if full else 0,
                   max_cells_wrong=max([s[1] for s in series[i]], default=0), boundaries=bounds[i],
                   series=[s for s in series[i] if s[0] <= end + 4 * Q])   # (step, wrong, longest run, left, right)
        rows.append(row)
        print(json.dumps({a: v for a, v in row.items() if a not in ('boundaries', 'series')}),
              [(x['level2_cells_wrong'], x['level1_cells_differing']) for x in bounds[i]], flush=True)
    path = os.path.join(OUT, f'{args.candidate}_misaligned_block2{args.tag}.json')
    with open(path, 'w') as fh:
        json.dump(dict(candidate=args.candidate, Q=Q, U=U, n2=n2, seed=args.seed, stride=args.stride,
                       reach=args.reach, cases=rows), fh, indent=1)
    print(path)


def _longest(mask):
    edges = np.flatnonzero(np.diff(np.concatenate(([0], mask.astype(np.int8), [0]))))
    return int((edges[1::2] - edges[::2]).max()) if len(edges) else 0


def _span(mask, b):
    """Left and right end of the wrong Addresses, relative to the colony boundary b."""
    idx = np.flatnonzero(mask)
    return (int(idx[0]) - b, int(idx[-1]) - b) if len(idx) else (None, None)


if __name__ == '__main__':
    main()
