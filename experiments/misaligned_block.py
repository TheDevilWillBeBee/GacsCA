"""Can a burst leave a misaligned colony behind? (REPORT section 32)

Gray's proof that level-0 rules repair a level-1 error (Proposition 2) needs the damage island to
stay smaller than a colony: a block of Q cells with consistent but shifted Addresses has no
inconsistency inside, its left end looks like a colony boundary, and nothing erodes it until the
level above notices (trickle-down of Flag1). With Q = 512 the island of a 200-cell burst can fill
a whole colony, so the question is a race: does the left end of the island reach the left end of
the shifted block while Flag1 is still raised there?

Ring: 32 colonies, consecutive cells of one healthy upper colony (upper Age 0). A burst replaces
every site of a w x h box by the state of the site 2Q + `shift` cells to its right (mode 'copy';
the source lies two colonies away, outside the damage), so the box holds a block of plausible
states whose Addresses agree with each other and are off by `shift`. The box ends
`reach` cells inside the right-hand colony R of the two middle colonies; the shifted block's
colony boundary (apparent Address 0) lies `shift` cells left of R's left end, inside the box.

Recorded per burst: the number of sites whose Address differs from the error-free ring, every
`--stride` ticks (how long the island lives, and how long it is at least Q - 10 wide), and at
each of the next four period boundaries the upper cells whose decoded state differs and whether
the physical states are equal.

Usage: misaligned_block.py --candidate G16 [--shifts 160,96] [--heights 200,300,450]
Receipt: figs/level0/<candidate>_misaligned_block.json
"""
import argparse
import json
import os
import time
import numpy as np
from gacsca import candidates, codec, gpu, machine

OUT = os.path.join(candidates.ROOT, 'figs', 'level0')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--candidate', default=candidates.CURRENT)
    ap.add_argument('--shifts', default='160,96')
    ap.add_argument('--heights', default='150,200,250,300,450')
    ap.add_argument('--widths', default='200,16')
    ap.add_argument('--starts', default='', help='Ages at which the bursts begin (default: one in the gathers, one after the trickle-down window)')
    ap.add_argument('--reach', type=int, default=10)
    ap.add_argument('--periods', type=int, default=4)
    ap.add_argument('--stride', type=int, default=32)
    ap.add_argument('--seed', type=int, default=3)
    ap.add_argument('--tag', default='')
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    c = candidates.load(args.candidate)
    p, C = c.p, c.c_backend()
    Q, U, n = p.Q, p.U, 32
    N = n * Q
    rng = np.random.default_rng(args.seed)
    top = codec.random_upper(c, 1, rng)
    up = codec.encode(c, top)[:, (np.arange(n) + Q // 2 - n // 2) % Q]
    P0 = C.pack(codec.encode(c, up))
    b = (n // 2) * Q                                   # left end of colony R
    starts = [int(x) for x in args.starts.split(',')] if args.starts else [2000, p.T_wf + 2 * Q + 500]
    cases = []
    for t0 in starts:
        for shift in [int(x) for x in args.shifts.split(',')]:
            for w in [int(x) for x in args.widths.split(',')]:
                for h in [int(x) for x in args.heights.split(',')]:
                    # the box holds the shifted block's left end, b - shift, and ends `reach` cells
                    # inside R (wide box) or covers w cells from that left end (narrow box)
                    x0 = b + args.reach - w if w > shift + args.reach else b - shift
                    cases.append(dict(mode='copy', shift=shift, width=w, height=h, start=t0, x0=x0))
        cases.append(dict(mode='random', shift=0, width=200, height=max(int(x) for x in args.heights.split(',')),
                          start=t0, x0=b + args.reach - 200))
    assert all(cs['shift'] % 32 == 0 for cs in cases)
    nr = len(cases) + 1
    sim = gpu.GpuSim(c, nr, n, mode='grid')
    sim.set_state(P0)
    cfgs = [gpu.noise()]
    for i, cs in enumerate(cases):
        cfgs.append(gpu.noise(seed=100 + i, boxes=[(cs['x0'], cs['width'], cs['start'], cs['height'], 1.0)],
                              mode=cs['mode'], shift_sites=(2 * Q + cs['shift']) if cs['mode'] == 'copy' else 0))
    sim.set_noise(cfgs)
    addr_rows = [c.row[('addr', i)] for i in range(p.k)]
    f1_row = c.row[('f1', 0)]
    series = [[] for _ in cases]                       # (tick, sites with a wrong Address, longest run)
    bounds = [[] for _ in cases]
    t_start = time.time()

    def longest_run(mask):
        best = cur = 0
        for v in mask:
            cur = cur + 1 if v else 0
            best = max(best, cur)
        return best

    for k in range(1, args.periods + 1):
        done = 0
        chunk = (U // 8 // args.stride) * args.stride or args.stride
        while done < U:
            m = min(chunk, U - done)
            snap = sim.run(m, rows=addr_rows, stride=args.stride) if m >= args.stride else (sim.run(m), None)[1]
            if snap is not None:
                bits = np.unpackbits(snap.view(np.uint8).reshape(snap.shape[0], nr, len(addr_rows), -1),
                                     axis=3, bitorder='little').astype(bool)
                for s in range(bits.shape[0]):
                    tick = (k - 1) * U + done + (s + 1) * args.stride
                    for i in range(len(cases)):
                        d = (bits[s, i + 1] != bits[s, 0]).any(axis=0)
                        cnt = int(d.sum())
                        if cnt or (series[i] and series[i][-1][1]):
                            series[i].append((tick, cnt, longest_run(d) if cnt else 0))
            done += m
        S = sim.state()
        ref = C.unpack(S[0], N)
        dref = codec.decode(c, ref)
        for i in range(len(cases)):
            X = C.unpack(S[i + 1], N)
            d = codec.decode(c, X)
            wrong = np.flatnonzero((d != dref).any(axis=0)) - n // 2
            bounds[i].append(dict(boundary=k, wrong_upper_cells=wrong.tolist(),
                                  physical_sites_differing=int((X != ref).any(axis=0).sum())))
        print(f'period {k} done ({time.time() - t_start:.0f} s)', flush=True)
    rows = []
    for i, cs in enumerate(cases):
        end = cs['start'] + cs['height']
        after = [(t, cnt, run) for t, cnt, run in series[i] if t > end]
        last = max([t for t, cnt, run in after if cnt], default=end)
        full = [t for t, cnt, run in after if run >= Q - 10]
        row = dict(cs, burst_end=end,
                   addresses_wrong_until=last, ticks_after_burst=last - end,
                   full_block_ticks=(max(full) - end) if full else 0,
                   max_sites_wrong=max([cnt for _, cnt, _ in series[i]], default=0),
                   boundaries=bounds[i])
        rows.append(row)
        print(json.dumps({a: v for a, v in row.items() if a != 'boundaries'}),
              [(x['wrong_upper_cells'], x['physical_sites_differing']) for x in bounds[i]], flush=True)
    path = os.path.join(OUT, f'{args.candidate}_misaligned_block{args.tag}.json')
    with open(path, 'w') as fh:
        json.dump(dict(candidate=args.candidate, Q=Q, U=U, colonies=n, seed=args.seed, stride=args.stride,
                       T_wf=p.T_wf, reach=args.reach, cases=rows), fh, indent=1)
    print(path)


if __name__ == '__main__':
    main()
