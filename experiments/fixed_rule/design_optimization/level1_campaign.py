"""Level-1 error campaign on two-level rings: is every level-1 error removed?

Upper state: one healthy upper colony, upper = encode(top), optionally
advanced by `--upper-age` upper steps with the rule (C kernel, bit-exact
with NumPy) so the upper colony can be in any stage of its own work period
(gathers, evaluation with its front, trickle-down, commit).

Physical ring: encode of either the whole upper colony (`--slice 0`, Q^2
sites) or a slice of `--slice` consecutive upper cells centred on the target
upper cell (the slice's ends meet at an Address jump; its effects travel at
most a few upper cells per upper step and the script checks that they never
reach the damaged region, see `slice_check`).

Rings: ring 0 is error-free. Every other ring gets one burst: a side x side
box (Gray: every level-1 error fits in 200 x 200) in which every site's whole
state is replaced by random bits at every tick. Bursts are placed at each
named phase of the physical work period (gathers, rest, early program,
special procedure, match pass, late evaluation, commit) and at three places
(middle of the target colony, its left boundary, its right boundary), plus
`--random` bursts at uniformly random (site, tick) overlapping the target
colony. All bursts happen during upper step 1.

Per upper step k, each ring is decoded and compared with F^k(upper ring)
(NumPy evaluator). The level-1 criteria (Gray section 5.1, Prop. 4):
  damage_ok    after the step containing the burst, at most two adjacent
               upper cells next to the target are wrong;
  repaired     from upper step 2 on (step 3 for bursts straddling the end of
               step 1), no upper cell is wrong;
  identical    after the last step the physical state equals the reference
               ring bit for bit.
Receipt: figs/fixed_rule/design_optimization/level1_campaign/<tag>.json
"""
import argparse
import hashlib
import json
import os
import time
import numpy as np
from gacsca.fixed_rule.design_optimization import candidates, codec, gpu

OUT = os.path.join(candidates.ROOT, 'figs', 'fixed_rule', 'design_optimization', 'level1_campaign')


def phases(p):
    Q = p.Q
    PL = getattr(p, 'PL', Q)          # ticks per front pass (W for a confined front)
    g = p.gathers_q
    last_cap = max(p.capture_age(o, 0) for o in (-5, 5)) - g[0] * Q
    return {
        'gather1_mid': g[0] * Q + 3 * Q,
        'gather1_end': g[0] * Q + last_cap - 100,
        'rest12': (g[0] * Q + last_cap + g[1] * Q) // 2,
        'gather2_start': g[1] * Q - 100,
        'gather2_mid': g[1] * Q + 3 * Q,
        'gather3_mid': g[2] * Q + 3 * Q,
        'gather3_end': g[2] * Q + last_cap - 100,
        'eval_start': p.E0 - 100,
        'early_program': p.E0 + (p.NPe // 2) * PL,
        'special_proc': p.T_sig - 100,
        'trickle_window': p.T_wf + Q,
        'phase_a': p.E0 + ((p.NPe + p.MP) // 2) * PL,
        'match_pass': p.E0 + p.MP * PL + PL // 2,
        'final_program': p.E0 + ((p.MP + p.NP) // 2) * PL,
        'program_end': p.E0 + (p.NP - 2) * PL,
        'commit': p.U - 100,
    }


def upper_state(cand, seed, age):
    """Healthy upper colony encoding a random top cell, advanced by `age`
    upper steps. Cached on disk."""
    p, C = cand.p, cand.c_backend()
    os.makedirs(OUT, exist_ok=True)
    key = hashlib.sha256(f'{cand.digest()}|{seed}|{age}'.encode()).hexdigest()[:16]
    path = os.path.join(OUT, f'upper_{key}.npz')
    rng = np.random.default_rng(seed)
    top = codec.random_upper(cand, 1, rng)
    if os.path.exists(path):
        z = np.load(path)
        return top, z['upper']
    up = codec.encode(cand, top)
    if age:
        P = C.run_packed(C.pack(up), age, threads=4)
        up = C.unpack(P, up.shape[1])
    np.savez_compressed(path, upper=up)
    return top, up


def front_cell(cand, up):
    """Upper cell holding the upper front (middle of the cells whose register
    copies are non-zero), or None."""
    rows = [cand.row[('reg', i)] for i in range(dict(cand.schema)['reg'])]
    cells = np.nonzero(up[rows].any(axis=0))[0]
    if len(cells) == 0:
        return None
    return int(cells[len(cells) // 2])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--candidate', default='G8')
    ap.add_argument('--upper-age', type=int, default=0)
    ap.add_argument('--target', default='mid', help="'mid', 'front', or an upper cell index")
    ap.add_argument('--slice', type=int, default=64, help='upper cells in the ring (0: whole colony)')
    ap.add_argument('--side', type=int, default=200)
    ap.add_argument('--random', type=int, default=16)
    ap.add_argument('--phases', default='all', help="comma list of phase names, or 'all'")
    ap.add_argument('--places', default='mid,left,right')
    ap.add_argument('--e0', action='store_true', help='add a dense level-0 (G=50) ring')
    ap.add_argument('--density', default='', help='comma list of p: side x side boxes, each site-tick an error with prob. p')
    ap.add_argument('--density-count', type=int, default=6, help='random boxes per density value')
    ap.add_argument('--pairs', type=int, default=0,
                    help='rings with two linked 2-site level-0 errors (within 24 sites and 24 ticks)')
    ap.add_argument('--upper-steps', type=int, default=3)
    ap.add_argument('--seed', type=int, default=7)
    ap.add_argument('--tag', default='')
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    cand = candidates.load(args.candidate)
    p, C = cand.p, cand.c_backend()
    Q, U, side = p.Q, p.U, args.side
    t0 = time.time()
    top, full = upper_state(cand, args.seed, args.upper_age)
    if args.target == 'front':
        d = front_cell(cand, full)
        assert d is not None, 'no upper front at this upper age'
    elif args.target == 'mid':
        d = Q // 2
    else:
        d = int(args.target)
    if args.slice:
        n = args.slice
        idx = (np.arange(n) + d - n // 2) % full.shape[1]
        ring_up = full[:, idx]
        c = n // 2
    else:
        ring_up = full
        c = d
    X0 = C.pack(codec.encode(cand, ring_up))
    # slice check: F^k(slice) must agree with F^k(full colony) near the target
    slice_check = None
    ref_traj = [ring_up]
    for k in range(args.upper_steps):
        ref_traj.append(cand.step_numpy(ref_traj[-1]))
    if args.slice:
        full_k = full
        dist = []
        for k in range(1, args.upper_steps + 1):
            full_k = cand.step_numpy(full_k)
            diff = np.nonzero((ref_traj[k] != full_k[:, idx]).any(axis=0))[0]
            dist.append(int(np.min(np.abs(diff - c))) if len(diff) else None)
        slice_check = dict(min_distance_of_wrap_effects_from_target=dist)
    # scenarios
    ph = phases(p)
    names = list(ph) if args.phases == 'all' else args.phases.split(',')
    places = dict(mid=c * Q + Q // 2 - side // 2, left=c * Q - side // 2, right=(c + 1) * Q - side // 2)
    sc = []
    for nm in names:
        for pl in args.places.split(','):
            sc.append(dict(kind='E1', phase=nm, place=pl, x0=int(places[pl]), t0=int(ph[nm])))
    rng = np.random.default_rng(args.seed + 1000)
    for i in range(args.random):
        sc.append(dict(kind='E1', phase='random', place='random',
                       x0=int(rng.integers(c * Q - side + 1, (c + 1) * Q)), t0=int(rng.integers(0, U - side))))
    for pr in [float(v) for v in args.density.split(',') if v]:
        for i in range(args.density_count):
            sc.append(dict(kind='E1', phase='random', place=f'density p={pr}', p=pr,
                           x0=int(rng.integers(c * Q - side + 1, (c + 1) * Q)),
                           t0=int(rng.integers(0, U - side))))
    for i in range(args.pairs):
        x = int(rng.integers(c * Q - 1, (c + 1) * Q))
        t = int(rng.integers(0, U - 30))
        dx, dt = int(rng.integers(-24, 25)), int(rng.integers(0, 25))
        sc.append(dict(kind='E1', phase='random', place='linked pair', x0=x, t0=t,
                       boxes=[(x, 2, t, 1), (x + dx, 2, t + dt, 1)]))
    if args.e0:
        sc.append(dict(kind='E0', phase='all', place='everywhere', x0=0, t0=0))
    cfgs = [gpu.noise()]
    for i, s in enumerate(sc):
        if s['kind'] == 'E0':
            cfgs.append(gpu.noise(args.seed + 50 + i, e0_grid=50))
        elif 'boxes' in s:
            cfgs.append(gpu.noise(args.seed + 50 + i, boxes=[b + (1.0,) for b in s['boxes']]))
        else:
            cfgs.append(gpu.noise(args.seed + 50 + i, boxes=[(s['x0'], side, s['t0'], side, s.get('p', 1.0))]))
    R = 1 + len(sc)
    sim = gpu.GpuSim(cand, R, ring_up.shape[1], mode='grid')
    sim.set_state(X0)
    sim.set_noise(cfgs)
    tag = args.tag or f'{args.candidate}_age{args.upper_age}_{args.target}_slice{args.slice}_seed{args.seed}'
    rec = dict(candidate=args.candidate,
               identity={k: v for k, v in candidates.summary(cand).items() if k != 'schema'},
               gpu_source_sha256=sim.source_sha256, args=vars(args), target_upper_cell=d,
               target_colony_in_ring=c, upper_age=args.upper_age,
               upper_cells=ring_up.shape[1], physical_sites=sim.N, side=side, phases=ph,
               slice_check=slice_check, reference_exact=[], rings=[dict(**s, steps=[]) for s in sc])
    prev = [ring_up] * R
    for k in range(1, args.upper_steps + 1):
        sim.run(U)
        S = sim.state()
        Xref = C.unpack(S[0], sim.N)
        ok_ref = bool(np.array_equal(codec.decode(cand, Xref), ref_traj[k]))
        rec['reference_exact'].append(ok_ref)
        decs = [None] * R
        for r in range(1, R):
            X = C.unpack(S[r], sim.N)
            dec = decs[r] = codec.decode(cand, X)
            wrong = np.nonzero((dec != ref_traj[k]).any(axis=0))[0].tolist()
            closure_bad = np.nonzero((dec != cand.step_numpy(prev[r])).any(axis=0))[0].tolist()
            h = codec.colony_health(cand, X)
            dfield = {}
            dd = X != Xref
            for f, w in cand.schema:
                r0 = cand.row[(f, 0)]
                nd = int(dd[r0:r0 + w].any(axis=0).sum())
                if nd:
                    dfield[f] = nd
            rec['rings'][r - 1]['steps'].append(dict(fields_differing=dfield,
                upper_step=k, wrong_upper_cells=wrong, wrong_upper_bits=int((dec != ref_traj[k]).sum()),
                closure_bad_cells=closure_bad, physical_sites_differing=int((X != Xref).any(axis=0).sum()),
                healthy=bool(h['addr'] and h['age'])))
        prev = decs
        prev[0] = ref_traj[k]
        print(f'upper step {k} done ({time.time() - t0:.0f} s, {sim.last_ms * 1000 / U:.0f} us/tick), '
              f'reference exact {ok_ref}', flush=True)
        with open(os.path.join(OUT, tag + '.json'), 'w') as fh:
            json.dump(rec, fh, indent=1)
    # verdicts
    summary = dict(total=0, damage_ok=0, repaired=0, identical=0, failures=[])
    for ring in rec['rings']:
        if ring['kind'] != 'E1':
            continue
        st = ring['steps']
        summary['total'] += 1
        w1 = st[0]['wrong_upper_cells']
        straddle = ring['t0'] + (30 if 'boxes' in ring else side) > U
        w_first = st[1]['wrong_upper_cells'] if straddle and len(st) > 1 else w1
        dmg = (len(w1) <= 2 and all(abs(x - c) <= 1 for x in w1)
               and (len(w1) < 2 or abs(w1[0] - w1[1]) == 1))
        if straddle:
            dmg = dmg and len(w_first) <= 2 and all(abs(x - c) <= 1 for x in w_first)
        rep_from = 2 if straddle else 1
        repaired = all(not s['wrong_upper_cells'] for s in st[rep_from:]) and len(st) > rep_from
        ident = st[-1]['physical_sites_differing'] == 0
        ring['verdict'] = dict(damage_ok=bool(dmg), repaired=bool(repaired), identical=bool(ident))
        summary['damage_ok'] += dmg
        summary['repaired'] += repaired
        summary['identical'] += ident
        if not (dmg and repaired and ident):
            summary['failures'].append(dict(phase=ring['phase'], place=ring['place'], x0=ring['x0'],
                                            t0=ring['t0'], steps=[(s['wrong_upper_cells'][:8],
                                                                   s['physical_sites_differing'])
                                                                  for s in st]))
    rec['summary'] = summary
    rec['wall_seconds'] = round(time.time() - t0, 1)
    with open(os.path.join(OUT, tag + '.json'), 'w') as fh:
        json.dump(rec, fh, indent=1)
    print(json.dumps({k: v for k, v in summary.items() if k != 'failures'}), flush=True)
    for f in summary['failures']:
        print('FAIL', json.dumps(f), flush=True)
    print('slice check', slice_check, 'reference exact', rec['reference_exact'])


if __name__ == '__main__':
    main()
