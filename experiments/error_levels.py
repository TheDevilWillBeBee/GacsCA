"""Gray-style error levels on the GPU: do level-0 and level-1 errors vanish?

Many rings of the same candidate run side by side from the same encoded
initial state. Ring 0 has no errors (reference). Every other ring gets one
error pattern (gpu.noise; an error replaces a site's whole state by random
bits):

  E0 dense      errors on a G=50 space-time grid for every period: every error
                is a level-0 error (1-2 adjacent sites, one tick, at least 25
                away from any other error in space or time);
  E0 then off   the same for the first `--e0-periods` periods, then none;
  E1 bursts     one 200x200 box (Gray: every level-1 error fits in 200x200)
                where every site-tick is an error, at a chosen phase of the
                work period and place in the ring (mid colony or across a
                colony boundary);
  E2 wipes      colony-scale boxes (higher-level errors at the physical scale).

After every work period (U ticks) each ring is decoded and compared with
  * the reference upper trajectory F^k(upper0) (F = the rule, applied
    upstairs by the independent NumPy evaluator): wrong upper cells;
  * F applied to its own previous decoded state: whether the lower level
    simulated this step correctly ("closure"), per upper cell;
  * the reference ring, site by site: physical differences, by field.

Interpretation (Gray section 5.1): a level-0 error should not change the
decoded upper state at all and should disappear from the physical state. A
level-1 error may damage at most one or two adjacent upper cells for one
upper step (it is a level-0 error of the upper level, which the upper level
corrects); afterwards the colony structure must be healthy again and the
lower level must simulate F exactly. Receipts: JSON per run in
figs/error_levels/.
"""
import argparse
import json
import os
import time
import numpy as np
from gacsca import candidates, codec, gpu

OUT = os.path.join(candidates.ROOT, 'figs', 'error_levels')


def phases(p):
    """Named ticks inside a work period for burst placement."""
    Q = p.Q
    g = getattr(p, 'gathers_q', (0,))
    ph = {'gather1_mid': g[0] * Q + 3 * Q}
    if len(g) == 3:
        ph.update(gather2_mid=g[1] * Q + 3 * Q, gather3_mid=g[2] * Q + 3 * Q,
                  gather2_start=g[1] * Q - 100)
    PL = getattr(p, 'PL', Q)          # ticks per front pass (W for a confined front)
    ph['eval_early'] = p.E0 + 10 * PL
    if hasattr(p, 'T_sig'):
        ph['special_proc'] = p.T_sig - 100
    ph['match_pass'] = p.E0 + p.MP * PL * p.D + PL // 2
    ph['eval_late'] = p.E0 + (p.NP - 100) * PL * p.D
    ph['commit'] = p.U - 100
    return ph


def scenario_list(p, ncol, seed, side, e0_grid):
    Q = p.Q
    mid = 3 * Q + Q // 2 - side // 2
    edge = 4 * Q - side // 2
    out = [('E0 dense (all periods)', gpu.noise(seed, e0_grid=e0_grid), 'E0'),
           ('E0 dense, then off', gpu.noise(seed + 1, e0_grid=e0_grid), 'E0off')]
    for i, (name, t) in enumerate(phases(p).items()):
        out.append((f'E1 {side}x{side} mid-colony @ {name}',
                    gpu.noise(seed + 10 + i, boxes=[(mid, side, t, side, 1.0)]), 'E1'))
        out.append((f'E1 {side}x{side} colony edge @ {name}',
                    gpu.noise(seed + 30 + i, boxes=[(edge, side, t, side, 1.0)]), 'E1'))
    t_eval = p.E0 + 37 * Q + Q // 3
    out.append(('E2 colony 3 randomized for 200 ticks',
                gpu.noise(seed + 50, boxes=[(3 * Q, Q, t_eval, 200, 1.0)]), 'E2'))
    out.append(('E2 colonies 3-4 randomized for 2Q ticks',
                gpu.noise(seed + 51, boxes=[(3 * Q, 2 * Q, t_eval, 2 * Q, 1.0)]), 'E2'))
    return out


def field_diffs(cand, A, B):
    d = A != B
    out = {}
    for f, w in cand.schema:
        r0 = cand.row[(f, 0)]
        n = int(d[r0:r0 + w].any(axis=0).sum())
        if n:
            out[f] = n
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--candidate', default='G5')
    ap.add_argument('--colonies', type=int, default=8)
    ap.add_argument('--periods', type=int, default=4)
    ap.add_argument('--e0-periods', type=int, default=2)
    ap.add_argument('--e0-grid', type=int, default=50)
    ap.add_argument('--side', type=int, default=200)
    ap.add_argument('--seed', type=int, default=3)
    ap.add_argument('--only', default='', help='comma list of scenario kinds (E0,E0off,E1,E2)')
    ap.add_argument('--tag', default='')
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    cand = candidates.load(args.candidate)
    p, C = cand.p, cand.c_backend()
    side = min(args.side, p.Q // 2) if p.Q < 2 * args.side else args.side
    sc = scenario_list(p, args.colonies, args.seed, side, args.e0_grid)
    if args.only:
        kinds = set(args.only.split(','))
        sc = [s for s in sc if s[2] in kinds]
    R = 1 + len(sc)
    rng = np.random.default_rng(args.seed)
    up0 = codec.random_upper(cand, args.colonies, rng)
    X0 = C.pack(codec.encode(cand, up0))
    sim = gpu.GpuSim(cand, R, args.colonies)
    sim.set_state(X0)
    cfgs = [gpu.noise()] + [c for _, c, _ in sc]
    sim.set_noise(cfgs)
    rec = dict(candidate=args.candidate,
               identity={k: v for k, v in candidates.summary(cand).items() if k != 'schema'},
               gpu_source_sha256=sim.source_sha256, args=vars(args), side=side,
               phases=phases(p), rings=[dict(name='reference', kind='ref')] +
               [dict(name=n, kind=k, periods=[]) for n, _, k in sc])
    ref_up = up0
    prev_dec = [up0] * R
    t0 = time.time()
    for k in range(1, args.periods + 1):
        if k == args.e0_periods + 1:
            for i, (_, _, kind) in enumerate(sc):
                if kind == 'E0off':
                    cfgs[1 + i] = gpu.noise()
            sim.set_noise(cfgs)
        sim.run(p.U)
        S = sim.state()
        ref_up = cand.step_numpy(ref_up)
        Xref = C.unpack(S[0], sim.N)
        dec0 = codec.decode(cand, Xref)
        assert np.array_equal(dec0, ref_up), 'reference ring must close'
        for r in range(1, R):
            X = C.unpack(S[r], sim.N)
            dec = codec.decode(cand, X)
            want = cand.step_numpy(prev_dec[r])
            health = codec.colony_health(cand, X)
            row = dict(period=k,
                       wrong_upper_cells=np.nonzero((dec != ref_up).any(axis=0))[0].tolist(),
                       wrong_upper_bits=int((dec != ref_up).sum()),
                       closure_bad_cells=np.nonzero((dec != want).any(axis=0))[0].tolist(),
                       physical_sites_differing=int((X != Xref).any(axis=0).sum()),
                       fields_differing=field_diffs(cand, X, Xref),
                       health=health)
            rec['rings'][r]['periods'].append(row)
            prev_dec[r] = dec
        el = time.time() - t0
        print(f'period {k} done ({el:.0f} s, {sim.last_ms * 1000 / p.U:.1f} us/tick)', flush=True)
        for r in range(1, R):
            row = rec['rings'][r]['periods'][-1]
            print(f"  {rec['rings'][r]['name']:<48} wrong upper {row['wrong_upper_cells']} "
                  f"closure-bad {row['closure_bad_cells']} phys-diff {row['physical_sites_differing']} "
                  f"health {'ok' if row['health']['addr'] and row['health']['age'] else 'BAD'}", flush=True)
        name = f"{args.candidate}_{args.tag or 'run'}_seed{args.seed}.json"
        with open(os.path.join(OUT, name), 'w') as fh:
            json.dump(rec, fh, indent=1)
    rec['wall_seconds'] = round(time.time() - t0, 1)
    with open(os.path.join(OUT, name), 'w') as fh:
        json.dump(rec, fh, indent=1)


if __name__ == '__main__':
    main()
