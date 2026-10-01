"""How long does local structure take to recover from a burst?

Rings with one burst each (whole-state randomization in a box) are compared
tick by tick with a fault-free reference ring on the local-structure fields
(Address, Age, Flag1, Flag2) and, separately, on the Mailbox tracks. The
recovery time of a burst is the number of ticks from the end of the box until
the last tick at which any site's structure differs from the reference.

Gray (section 5.1) bounds level-1 recovery by about 200 + 500 + 2(Q + 200)
ticks. For the three-gather vote to see at most one disturbed gather, the rest
between consecutive gathers must exceed this time. Receipt:
figs/recovery/<cand>.json
"""
import argparse
import json
import os
import numpy as np
from gacsca import candidates, codec, gpu

OUT = os.path.join(candidates.ROOT, 'figs', 'recovery')


def rows_of(cand, fields):
    return [cand.row[(f, i)] for f, w in cand.schema if f in fields for i in range(w)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--candidate', default='G6')
    ap.add_argument('--colonies', type=int, default=8)
    ap.add_argument('--side', type=int, default=200)
    ap.add_argument('--window', type=int, default=0, help='ticks observed after each burst (default 6Q)')
    ap.add_argument('--seed', type=int, default=21)
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    cand = candidates.load(args.candidate)
    p, C = cand.p, cand.c_backend()
    Q = p.Q
    side = min(args.side, Q // 2)
    window = args.window or 6 * Q
    rng = np.random.default_rng(args.seed)
    up = codec.random_upper(cand, args.colonies, rng)
    X0 = C.pack(codec.encode(cand, up))
    srows = rows_of(cand, ('addr', 'age', 'f1', 'f2'))
    mrows = rows_of(cand, ('mr', 'ml'))
    rows = srows + mrows
    ns = len(srows)
    # burst start ticks: during the evaluation window (mid-period), so that
    # no gather or commit interferes with the measurement
    t_b = p.E0 + (p.NP // 3) * p.D * Q + 17
    places = {'mid-colony': 3 * Q + Q // 2 - side // 2, 'colony edge': 4 * Q - side // 2,
              'covers reserved cell Q-3': 4 * Q - 3 - side // 2}
    sizes = [(side, side), (side, 2 * side), (Q, 200), (2 * Q, 2 * Q)]
    sc = [(pl, x0 if w <= side else 3 * Q, w, h) for pl, x0 in places.items() for (w, h) in sizes[:1]]
    sc += [('mid-colony', 3 * Q + Q // 2 - side // 2, side, 2 * side),
           ('whole colony', 3 * Q, Q, 200), ('two colonies', 3 * Q, 2 * Q, 2 * Q)]
    R = 1 + len(sc)
    sim = gpu.GpuSim(cand, R, args.colonies)
    sim.set_state(X0)
    sim.set_noise([gpu.noise()] + [gpu.noise(args.seed + i, boxes=[(x0, w, t_b, h, 1.0)])
                                   for i, (_, x0, w, h) in enumerate(sc)])
    sim.run(t_b - 1)
    longest = max(h for *_, h in sc)
    span = longest + window
    snap = sim.run(span, rows=rows, stride=1)
    out = dict(candidate=args.candidate, Q=Q, U=p.U, burst_start=t_b, window=window,
               gray_level1_recovery_bound=200 + 500 + 2 * (Q + 200), results=[])
    if hasattr(p, 'gathers_q'):
        g = p.gathers_q
        last_capture = max(p.capture_age(o, 0) for o in (-5, 5))
        out['rest_between_gathers'] = (g[1] - g[0]) * Q - (last_capture - g[0] * Q)
    for r, (pl, x0, w, h) in enumerate(sc, start=1):
        d = snap[:, r] ^ snap[:, 0]                    # (span, rows, NW) packed differences
        ds = d[:, :ns].any(axis=(1, 2))
        dm = d[:, ns:].any(axis=(1, 2))
        orr = np.bitwise_or.reduce(d[:, :ns], axis=1)
        nsites = np.unpackbits(orr.view(np.uint8), axis=1).sum(axis=1)
        # snapshot s holds the state computed at tick t_b - 1 + s; the box
        # corrupts s = 1..h, so ticks after the box start at s = h + 1
        s_last = np.nonzero(ds)[0]
        m_last = np.nonzero(dm)[0]
        rec = dict(place=pl, x0=x0, width=w, height=h,
                   structure_recovery_ticks=max(0, int(s_last[-1] - h)) if len(s_last) else 0,
                   structure_still_differs_at_end=bool(ds[-1]),
                   mailbox_differs_ticks_after=max(0, int(m_last[-1] - h)) if len(m_last) else 0,
                   structure_sites_max=int(nsites.max()))
        out['results'].append(rec)
        print(json.dumps(rec), flush=True)
    with open(os.path.join(OUT, f'{args.candidate}.json'), 'w') as fh:
        json.dump(out, fh, indent=1)
    print(json.dumps({k: out[k] for k in ('gray_level1_recovery_bound',) + (('rest_between_gathers',) if 'rest_between_gathers' in out else ())}))


if __name__ == '__main__':
    main()
