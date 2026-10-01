"""Gray's Proposition 4 field by field.

Gray (reader's guide p. 15): the six fields are Address, Age, Flags, SimBit,
Workspace and Mailbox; "the first two fields form ... the local structure,
while the last three fields are the simulation structure". Proposition 4:
outside a box [jQ, (j+2)Q) x [kU, (k+2)U) per level-1 error, the simulation
structure fields equal the error-free run.

For one level-1 error per ring (a dense side x side box at every named phase
and place of level1_campaign.py), this samples the full state every
`--sample` ticks and records, per field, whether it ever differs (a) outside
the two-colony box during the box's time window, (b) after the window.

Our fields by Gray's names:
  SimBit     info (five copies, as Gray's five SimBit bits)
  Mailbox    mr, ml
  Workspace  hold, h1, h2, scr, reg, pend, pkind, pval, wf1, wf2
             (Gray's Workspace.Flag1/2 are wf1/wf2; the front's registers
             and pending write are evaluator workspace)
  Flags      f1, f2
  local      addr, age
Usage: prop4_fields.py --candidate G15 [--side 100] [--mode random]
Receipt: figs/level1_campaign/<tag>.json
"""
import argparse
import json
import os
import sys
import time
from collections import defaultdict
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from level1_campaign import upper_state, phases, OUT
from gacsca import candidates, codec, gpu

GROUP = dict(info='SimBit', mr='Mailbox', ml='Mailbox', hold='Workspace', h1='Workspace', h2='Workspace',
             scr='Workspace', reg='Workspace', pend='Workspace', pkind='Workspace', pval='Workspace',
             wf1='Workspace', wf2='Workspace', f1='Flags', f2='Flags', addr='local', age='local')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--candidate', default='G15')
    ap.add_argument('--side', type=int, default=100)
    ap.add_argument('--mode', default='random', choices=gpu.VALUE_MODES)
    ap.add_argument('--sample', type=int, default=0, help='ticks between samples (0: Q)')
    ap.add_argument('--seed', type=int, default=7)
    ap.add_argument('--tag', default='')
    args = ap.parse_args()
    cand = candidates.load(args.candidate)
    p, C = cand.p, cand.c_backend()
    Q, U, side = p.Q, p.U, args.side
    sample = args.sample or Q
    top, full = upper_state(cand, args.seed, 0)
    n = 64
    idx = (np.arange(n) + Q // 2 - n // 2) % Q
    ring_up = full[:, idx]
    c = n // 2
    ph = phases(p)
    places = dict(mid=c * Q + Q // 2 - side // 2, left=c * Q - side // 2, right=(c + 1) * Q - side // 2)
    sc = [dict(phase=nm, place=pl, x0=int(places[pl]), t0=int(ph[nm])) for nm in ph for pl in places]
    cfgs = [gpu.noise()] + [gpu.noise(args.seed + 500 + i, boxes=[(s['x0'], side, s['t0'], side, 1.0)],
                                      mode=args.mode, shift_sites=Q) for i, s in enumerate(sc)]
    sim = gpu.GpuSim(cand, len(cfgs), n, mode='grid')
    sim.set_state(C.pack(codec.encode(cand, ring_up)))
    sim.set_noise(cfgs)
    rows = {f: np.arange(cand.row[(f, 0)], cand.row[(f, 0)] + w) for f, w in cand.schema}
    t_end = 2 * U + 4 * Q + max(s['t0'] for s in sc) // U * U
    rec = defaultdict(lambda: defaultdict(lambda: dict(outside_window=0, after_window=0)))
    per_ring = [defaultdict(lambda: dict(outside=False, after=False, cols=set())) for _ in sc]
    t0 = time.time()
    while sim.t < t_end:
        sim.run(min(sample, t_end - sim.t))
        S = sim.state()
        t = sim.t
        for r, s in enumerate(sc, 1):
            k = s['t0'] // U
            xlo, xhi = s['x0'], s['x0'] + side - 1
            js = [j for j in (xlo // Q - 1, xlo // Q) if j * Q <= xlo and xhi < (j + 2) * Q]
            for f, rr in rows.items():
                x = np.bitwise_or.reduce(S[r][rr] ^ S[0][rr], axis=0)
                if not x.any():
                    continue
                d = np.unpackbits(x.view(np.uint8), bitorder='little').astype(bool)
                cols = set((np.nonzero(d)[0] // Q).tolist())
                pr = per_ring[r - 1][f]
                if t >= (k + 2) * U:
                    pr['after'] = True
                elif not any(cols <= {j % n, (j + 1) % n} for j in js):
                    pr['outside'] = True
                    pr['cols'] |= cols
    rows_out = []
    for f, w in cand.schema:
        out = sum(per_ring[i][f]['outside'] for i in range(len(sc)))
        aft = sum(per_ring[i][f]['after'] for i in range(len(sc)))
        far = max((max(abs(cc - c) for cc in per_ring[i][f]['cols']) for i in range(len(sc))
                   if per_ring[i][f]['cols']), default=0)
        rows_out.append(dict(field=f, gray=GROUP[f], rings=len(sc), outside_box_in_window=out,
                             after_window=aft, farthest_colony_from_target=far))
        print(f'{GROUP[f]:9s} {f:6s}  differs outside the 2-colony box during the window: {out:2d}/{len(sc)} '
              f'(farthest {far} colonies away)   after the window: {aft}/{len(sc)}', flush=True)
    tag = args.tag or f'{args.candidate}_prop4_fields_box{side}_{args.mode}'
    with open(os.path.join(OUT, tag + '.json'), 'w') as fh:
        json.dump(dict(candidate=args.candidate, side=side, mode=args.mode, sample_ticks=sample,
                       scenarios=sc, fields=rows_out, seconds=round(time.time() - t0)), fh, indent=1)


if __name__ == '__main__':
    main()
