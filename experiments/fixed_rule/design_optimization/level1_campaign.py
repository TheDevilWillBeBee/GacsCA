"""Error campaign on two-level rings: bursts at every stage of the work period.

Upper state: one healthy upper colony, upper = encode(top), optionally
advanced by `--upper-age` ticks with the rule (C kernel, bit-exact with
NumPy) so the upper colony can be in any stage of its own work period
(gathers, evaluation with its front, trickle-down, commit).

Physical ring: encode of either the whole upper colony (`--slice 0`, Q^2
sites) or a slice of `--slice` consecutive upper cells centred on the target
upper cell (the slice's ends meet at an Address jump; its effects travel at
most a few upper cells per upper step and the script checks that they never
reach the damaged region, see `slice_check`).

Rings: ring 0 is error-free. Every other ring gets one error set during
upper step 1, placed at each named phase of the physical work period and at
three places (middle of the target colony, its left boundary, its right
boundary), plus `--random` placements overlapping the target colony:
  --shape dense   a side x side box in which every site is an error at every
                  tick. Gray (section 5.1): a dense box of side <= 104 is one
                  level-1 error; a dense 200 x 200 box is a union of level-1
                  errors (it contains two (104,104)-separated linked pairs).
  --shape sparse  a sparse cluster of `--pairs-per-cluster` linked pairs of
                  candidate level-0 errors, kept only if gray_errors.classify
                  confirms it is one level-1 error.
Error sites take values by `--mode` (gpu.noise: random bits, stuck-at zero
or one, the correct new state inverted, the old state frozen, or the state of
the same Address one colony further: a plausible but wrong state).

The noise seed of a scenario depends only on its identity (phase and place,
or its index among the random scenarios), so filtering with --phases or
--places reproduces the faults of the unfiltered run exactly.

Measurements:
  per upper step k: each ring is decoded and compared with F^k(upper ring);
  every --sample ticks: the full physical state of each ring is compared
    with ring 0 (all fields, all sites).
Verdicts per error ring:
  decoded_contained  after the step containing the error, at most two
                     adjacent upper cells next to the target are wrong;
  decoded_repaired   no upper cell is wrong from the first boundary after
                     the error has ended;
  prop4              Gray's Proposition 4 at the sampled times, in two parts
                     that are both required: time (no difference in any
                     field of any colony after (k+2)U, for the box
                     [kU, (k+2)U) containing the error) and simbits (Info
                     differences only inside a box [jQ, (j+2)Q) x
                     [kU, (k+2)U) containing the error). Mail and histories
                     of neighbouring colonies legitimately carry the damaged
                     colony's state for a period (Gray counts only the
                     SimBits as lasting effects), so the all-field spatial
                     test is recorded separately as prop4_strict;
  identical          the physical state equals ring 0 at the last sample.
The dense level-0 ring (--e0) gets the one-tick check: at every sample time
t, the sites differing from ring 0 are among the sites corrupted at tick
t - 1 (every earlier level-0 error has been corrected).
Receipt: figs/fixed_rule/design_optimization/level1_campaign/<tag>.json
"""
import argparse
import hashlib
import json
import os
import time
import numpy as np
from gacsca.fixed_rule.design_optimization import candidates, codec, gpu, gray_errors

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
    ticks of the rule. Cached on disk."""
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


def diff_sites(S, r, rows=None):
    """Boolean per-site difference between ring r and ring 0 (all fields, or
    the given rows)."""
    a, b = (S[r], S[0]) if rows is None else (S[r][rows], S[0][rows])
    x = np.bitwise_or.reduce(a ^ b, axis=0)
    return np.unpackbits(x.view(np.uint8), bitorder='little').astype(bool)


def prop4_check(events, x_lo, x_hi, t_lo, t_hi, Q, U, n_col, time_only=False):
    """Gray Prop. 4 for one error at sites [x_lo, x_hi], ticks [t_lo, t_hi]:
    is there a box [jQ, (j+2)Q) x [kU, (k+2)U) containing the error and every
    sampled difference? events: (t, sorted differing colonies). With
    time_only, only the time extent is checked (any colonies)."""
    ks = [k for k in range(max(0, t_lo // U - 1), t_lo // U + 1) if k * U <= t_lo and t_hi < (k + 2) * U]
    js = [j for j in range(x_lo // Q - 1, x_lo // Q + 1) if j * Q <= x_lo and x_hi < (j + 2) * Q]
    for k in ks:
        for j in js:
            allowed = {j % n_col, (j + 1) % n_col}
            if all(t < (k + 2) * U and (time_only or set(cols) <= allowed) for t, cols in events):
                return dict(ok=True, j=j, k=k)
    return dict(ok=False, boxes_tried=[(j, k) for k in ks for j in js])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--candidate', default='G8')
    ap.add_argument('--upper-age', type=int, default=0)
    ap.add_argument('--target', default='mid', help="'mid', 'front', or an upper cell index")
    ap.add_argument('--slice', type=int, default=64, help='upper cells in the ring (0: whole colony)')
    ap.add_argument('--side', type=int, default=200)
    ap.add_argument('--shape', default='dense', choices=('dense', 'sparse'))
    ap.add_argument('--pairs-per-cluster', type=int, default=6)
    ap.add_argument('--mode', default='random', choices=gpu.VALUE_MODES)
    ap.add_argument('--random', type=int, default=16)
    ap.add_argument('--phases', default='all', help="comma list of phase names, or 'all'")
    ap.add_argument('--places', default='mid,left,right')
    ap.add_argument('--e0', action='store_true', help='add a dense level-0 (G=50) ring')
    ap.add_argument('--density', default='', help='comma list of p: side x side boxes, each site-tick an error with prob. p')
    ap.add_argument('--density-count', type=int, default=6, help='random boxes per density value')
    ap.add_argument('--pairs', type=int, default=0,
                    help='rings with two linked 2-site level-0 errors (within 24 sites and 24 ticks)')
    ap.add_argument('--upper-steps', type=int, default=3)
    ap.add_argument('--sample', type=int, default=0, help='ticks between full-state samples (0: Q)')
    ap.add_argument('--seed', type=int, default=7)
    ap.add_argument('--tag', default='')
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    cand = candidates.load(args.candidate)
    p, C = cand.p, cand.c_backend()
    Q, U, side = p.Q, p.U, args.side
    sample = args.sample or Q
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
    n_col = ring_up.shape[1]
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
    # scenarios; a scenario's noise seed depends only on its identity
    ph = phases(p)
    all_phases, all_places = list(ph), ['mid', 'left', 'right']
    names = all_phases if args.phases == 'all' else args.phases.split(',')
    places = dict(mid=c * Q + Q // 2 - side // 2, left=c * Q - side // 2, right=(c + 1) * Q - side // 2)
    crng = np.random.default_rng(args.seed + 2000)

    def shaped(s, ident):
        """Fill in the error set of scenario s at (x0, t0)."""
        if args.shape == 'dense' or 'boxes' in s:
            if 'boxes' not in s:
                s['boxes'] = [(s['x0'], side, s['t0'], side, s.get('p', 1.0))]
            return s
        r = np.random.default_rng([args.seed, 3000 + ident])
        for _ in range(100):
            pts, bx = gray_errors.random_level1_cluster(r, s['x0'], s['t0'], pairs=args.pairs_per_cluster)
            if gray_errors.classify(pts, Q=Q, U=U)['level1']:
                break
        s['boxes'] = [b + (1.0,) for b in bx]
        return s
    sc = []
    for nm in names:
        for pl in args.places.split(','):
            ident = all_phases.index(nm) * len(all_places) + all_places.index(pl)
            sc.append(shaped(dict(kind='E1', phase=nm, place=pl, x0=int(places[pl]), t0=int(ph[nm]),
                                  ident=ident), ident))
    base = len(all_phases) * len(all_places)
    rng = np.random.default_rng(args.seed + 1000)
    j = 0
    for i in range(args.random):
        sc.append(shaped(dict(kind='E1', phase='random', place='random', ident=base + j,
                              x0=int(rng.integers(c * Q - side + 1, (c + 1) * Q)),
                              t0=int(rng.integers(0, U - side))), base + j))
        j += 1
    for pr in [float(v) for v in args.density.split(',') if v]:
        for i in range(args.density_count):
            sc.append(dict(kind='E1', phase='random', place=f'density p={pr}', p=pr, ident=base + j,
                           x0=int(rng.integers(c * Q - side + 1, (c + 1) * Q)),
                           t0=int(rng.integers(0, U - side))))
            sc[-1]['boxes'] = [(sc[-1]['x0'], side, sc[-1]['t0'], side, pr)]
            j += 1
    for i in range(args.pairs):
        x = int(rng.integers(c * Q - 1, (c + 1) * Q))
        t = int(rng.integers(0, U - 30))
        dx, dt = int(rng.integers(-24, 25)), int(rng.integers(0, 25))
        sc.append(dict(kind='E1', phase='random', place='linked pair', x0=x, t0=t, ident=base + j,
                       boxes=[(x, 2, t, 1, 1.0), (x + dx, 2, t + dt, 1, 1.0)]))
        j += 1
    if args.e0:
        sc.append(dict(kind='E0', phase='all', place='everywhere', x0=0, t0=0, ident=base + j))
        j += 1
    cfgs = [gpu.noise()]
    for s in sc:
        s['noise_seed'] = args.seed + 50 + s['ident']
        if s['kind'] == 'E0':
            cfgs.append(gpu.noise(s['noise_seed'], e0_grid=50, mode=args.mode, shift_sites=Q))
        else:
            cfgs.append(gpu.noise(s['noise_seed'], boxes=s['boxes'], mode=args.mode, shift_sites=Q))
            pts = []
            dense = all(b[4] >= 1.0 for b in s['boxes'])
            if dense and len(s['boxes']) == 1 and s['boxes'][0][1] * s['boxes'][0][3] > 400:
                bx = s['boxes'][0]
                g = gray_errors.classify(gray_errors.dense_box(bx[0], bx[2], bx[1], bx[3]), Q=Q, U=U)
            elif dense:
                pts = [(x + dx, t + dt) for (x, w, t, h, _) in s['boxes'] for dx in range(w) for dt in range(h)]
                g = gray_errors.classify(pts, Q=Q, U=U)
            else:
                g = None                      # Bernoulli box: classified from the realized mask below
            if g is not None:
                s['gray'] = {k: (v if k != 'witness' else (v and [[list(map(int, q)) for q in M] for M in v]))
                             for k, v in g.items()}
            xs = [b[0] for b in s['boxes']] + [b[0] + b[1] - 1 for b in s['boxes']]
            ts = [b[2] for b in s['boxes']] + [b[2] + b[3] - 1 for b in s['boxes']]
            s['extent'] = dict(x_lo=min(xs), x_hi=max(xs), t_lo=min(ts), t_hi=max(ts))
    R = 1 + len(sc)
    sim = gpu.GpuSim(cand, R, ring_up.shape[1], mode='grid')
    sim.set_state(X0)
    sim.set_noise(cfgs)
    for i, s in enumerate(sc, 1):
        if s['kind'] == 'E1' and 'gray' not in s:
            # the realized error set of a Bernoulli box, from the kernel's own masks
            t_lo = min(b[2] for b in s['boxes'])
            t_hi = max(b[2] + b[3] for b in s['boxes'])
            m = sim.error_masks(cfgs[i], i, t_lo, t_hi - t_lo)
            ts, xs = np.nonzero(m)
            pts = list(zip(xs.tolist(), (ts + t_lo).tolist()))
            g = gray_errors.classify(pts, Q=Q, U=U)
            s['gray'] = {k: (v if k != 'witness' else (v and [[list(map(int, q)) for q in M] for M in v]))
                         for k, v in g.items()}
            s['gray']['realized_points'] = len(pts)
    tag = args.tag or f'{args.candidate}_age{args.upper_age}_{args.target}_slice{args.slice}_seed{args.seed}'
    rec = dict(candidate=args.candidate,
               identity={k: v for k, v in candidates.summary(cand).items() if k != 'schema'},
               gpu_source_sha256=sim.source_sha256, args=vars(args), target_upper_cell=d,
               target_colony_in_ring=c, upper_age=args.upper_age, sample_ticks=sample,
               upper_cells=n_col, physical_sites=sim.N, side=side, phases=ph,
               slice_check=slice_check, reference_exact=[],
               rings=[dict(**{k: v for k, v in s.items()}, steps=[], events=[]) for s in sc])
    e0_ring = [r for r, s in enumerate(sc, 1) if s['kind'] == 'E0']
    r0 = cand.row[('info', 0)]
    info_rows = np.arange(r0, r0 + dict(cand.schema)['info'])
    for ring in rec['rings']:
        ring['info_events'] = []
    one_tick = dict(samples=0, violations=0, by_colony={}, examples=[])
    prev = [ring_up] * R
    for k in range(1, args.upper_steps + 1):
        done = 0
        while done < U:
            chunk = min(sample, U - done)
            sim.run(chunk)
            done += chunk
            S = sim.state()
            tnow = sim.t
            for r in range(1, R):
                dif = diff_sites(S, r)
                if dif.any():
                    cols = sorted(set((np.nonzero(dif)[0] // Q).tolist()))
                    rec['rings'][r - 1]['events'].append((tnow, cols, int(dif.sum())))
                    di = diff_sites(S, r, info_rows)
                    if di.any():
                        icols = sorted(set((np.nonzero(di)[0] // Q).tolist()))
                        rec['rings'][r - 1]['info_events'].append((tnow, icols, int(di.sum())))
                if r in e0_ring:
                    one_tick['samples'] += 1
                    m = sim.error_masks(cfgs[r], r, tnow - 1, 1)[0]
                    extra = dif & ~m
                    if extra.any():
                        one_tick['violations'] += 1
                        sites = np.nonzero(extra)[0]
                        for col in set((sites // Q).tolist()):
                            one_tick['by_colony'][col] = one_tick['by_colony'].get(col, 0) + 1
                        if len(one_tick['examples']) < 10:
                            one_tick['examples'].append(dict(t=tnow, sites=sites[:10].tolist()))
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
        print(f'upper step {k} done ({time.time() - t0:.0f} s, {sim.last_ms * 1000 / sample:.0f} us/tick), '
              f'reference exact {ok_ref}', flush=True)
        with open(os.path.join(OUT, tag + '.json'), 'w') as fh:
            json.dump(rec, fh, indent=1)
    if e0_ring:
        # with a slice, the upper Address jump at the slice's ends is an
        # inconsistency upstairs (upper Flag1, then trickle-down); the middle
        # colonies, within 16 of the target, see a healthy upper colony
        mid = [col for col in one_tick['by_colony'] if not args.slice or abs(col - c) <= 16]
        one_tick['violations_in_middle_colonies'] = sum(one_tick['by_colony'][col] for col in mid)
        one_tick['by_colony'] = {str(k): v for k, v in sorted(one_tick['by_colony'].items())}
    rec['e0_one_tick'] = one_tick if e0_ring else None
    # verdicts
    summary = dict(total=0, decoded_contained=0, decoded_repaired=0, prop4=0, prop4_time=0,
                   prop4_simbits=0, prop4_strict=0, identical=0, gray_level1=0, failures=[])
    for ring in rec['rings']:
        if ring['kind'] != 'E1':
            continue
        st = ring['steps']
        ex = ring['extent']
        summary['total'] += 1
        summary['gray_level1'] += bool(ring['gray'].get('level1'))
        first = ex['t_hi'] // U                     # index of the step in which the error ends
        w_first = st[first]['wrong_upper_cells'] if first < len(st) else []
        w0 = st[0]['wrong_upper_cells']
        dmg = all(len(w) <= 2 and all(abs(x - c) <= 1 for x in w) and (len(w) < 2 or abs(w[0] - w[1]) == 1)
                  for w in (w0, w_first))
        repaired = all(not s['wrong_upper_cells'] for s in st[first + 1:]) and len(st) > first + 1
        args4 = (ex['x_lo'], ex['x_hi'], ex['t_lo'], ex['t_hi'], Q, U, n_col)
        ev = [(t, cols) for t, cols, _ in ring['events']]
        p4 = dict(time=prop4_check(ev, *args4, time_only=True)['ok'],
                  simbits=prop4_check([(t, cols) for t, cols, _ in ring['info_events']], *args4)['ok'],
                  strict=prop4_check(ev, *args4)['ok'])
        p4['ok'] = p4['time'] and p4['simbits']
        last_t = sim.t
        ident = not ring['events'] or ring['events'][-1][0] < last_t
        ring['last_difference_tick'] = ring['events'][-1][0] if ring['events'] else None
        ring['verdict'] = dict(decoded_contained=bool(dmg), decoded_repaired=bool(repaired),
                               prop4=p4, identical=bool(ident))
        summary['decoded_contained'] += dmg
        summary['decoded_repaired'] += repaired
        summary['prop4'] += p4['ok']
        summary['prop4_time'] += p4['time']
        summary['prop4_simbits'] += p4['simbits']
        summary['prop4_strict'] += p4['strict']
        summary['identical'] += ident
        if not (dmg and repaired and p4['ok'] and ident):
            summary['failures'].append(dict(phase=ring['phase'], place=ring['place'], x0=ring['x0'],
                                            t0=ring['t0'], prop4=p4,
                                            last_difference_tick=ring['last_difference_tick'],
                                            steps=[(s['wrong_upper_cells'][:8], s['physical_sites_differing'],
                                                    s['fields_differing']) for s in st]))
    rec['summary'] = summary
    rec['wall_seconds'] = round(time.time() - t0, 1)
    with open(os.path.join(OUT, tag + '.json'), 'w') as fh:
        json.dump(rec, fh, indent=1)
    print(json.dumps({k: v for k, v in summary.items() if k != 'failures'}), flush=True)
    for f in summary['failures']:
        print('FAIL', json.dumps(f)[:600], flush=True)
    print('slice check', slice_check, 'reference exact', rec['reference_exact'], 'e0 one tick', rec['e0_one_tick'])


if __name__ == '__main__':
    main()
