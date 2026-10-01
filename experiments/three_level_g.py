"""Three-level experiments for a G candidate (physical -> level 1 -> level 2).

A level-2 cell is a colony of level-1 cells, each a colony of physical cells:
Q^2 physical sites. A level-2 step takes U level-1 steps = U^2 physical
ticks, far beyond a GPU run for G15 (weeks per level-2 step on an A100, see
gpu_level2_bench.py). The experiments therefore combine physical runs with
runs of the same rule one level up (the level-1 automaton), which is exact
wherever physical -> level-1 closure holds (it holds for arbitrary level-1
states in every closure test, and repair2 checks it at every physical step).

  phases    Level-2 cells -> level-1 ring -> level-1 automaton advanced to a
            chosen stage of the level-2 work period -> physical ring. The
            physical ring is run for --steps level-1 steps; after each one
            the decoded level-1 state must equal the level-1 automaton, and
            the twice-decoded level-2 state must equal the level-2 state the
            automaton represents (one run crosses a level-2 commit, where it
            must become F(level 2)).
  closure2  Level-2 macrosteps on the level-1 automaton: decode(level-1 ring
            after U ticks) must equal F(level-2 ring), for --steps successive
            level-2 steps.
  repair2   Errors that only level 2 can clear. A healthy level-2 colony
            slice (consecutive level-2 cells of an encoded level-3 cell) is
            encoded twice. A physical slice of the level-1 ring around the
            middle is run with and without a wipe of k adjacent physical
            colonies (k adjacent level-1 cells) for --phys-steps level-1
            steps, until the damaged colonies are healthy again and closure
            holds. The decoded difference (confined to the middle) is applied
            to the full level-1 ring, and both full rings continue on the
            level-1 automaton for --l2-steps level-2 steps; the level-2
            states and all level-1 fields are compared at every level-2
            boundary. Options: a data-rich level-2 colony (--level2-age),
            the wipe centred on a front of the level-2 comb (--target front)
            or on the bits of one level-2 field (--target field), dense
            level-0 noise in the physical rings (--e0) and level-1 errors at
            Gray's E0 density on the level-1 automaton (--level1-e0). The
            receipt lists the level-2 bits whose five copies the wipe
            destroys, and the physical residue at the hand-off.
  copy2     Level-2 errors with plausible wrong values, injected on the
            level-1 automaton: k level-1 cells replaced by the same cells of
            the next level-2 colony.
Receipts: figs/three_level/<tag>.json
"""
import argparse
import json
import os
import time
import numpy as np
from gacsca import candidates, codec, gpu

OUT = os.path.join(candidates.ROOT, 'figs', 'three_level')


def run_rings(cand, states, ticks, chunk=None, on_chunk=None):
    """Run unpacked (W, N) states (same N) on the GPU for `ticks`; returns the
    final unpacked states. on_chunk(k, states) is called every `chunk` ticks."""
    C = cand.c_backend()
    N = states[0].shape[1]
    if N % cand.p.Q or N < 4 * cand.p.Q:
        # a small ring (e.g. a decoded slice): the C kernel (its runs overwrite their input)
        assert on_chunk is None
        return [C.unpack(C.run_packed_scalar(C.pack(X).copy(), ticks), N) for X in states], 0.0
    sim = gpu.GpuSim(cand, len(states), N // cand.p.Q, mode='grid')
    sim.set_state(np.stack([C.pack(X) for X in states]))
    done, k = 0, 0
    chunk = chunk or ticks
    while done < ticks:
        n = min(chunk, ticks - done)
        sim.run(n)
        done += n
        k += 1
        if on_chunk is not None:
            S = sim.state()
            on_chunk(k, [C.unpack(S[r], N) for r in range(len(states))])
    S = sim.state()
    out = [C.unpack(S[r], N) for r in range(len(states))]
    return out, sim.last_ms


def level1_states(cand, L1, ages):
    """The level-1 automaton run from L1 to each of the given (sorted) ages."""
    out = {}
    X = L1
    t = 0
    for a in sorted(ages):
        if a > t:
            (X,), _ = run_rings(cand, [X], a - t)
            t = a
        out[a] = X
    return out


def health_except(cand, X, skip):
    """Physical Address and Age consistent with aligned healthy colonies, ignoring the sites
    in the boolean mask `skip` (sites hit by a level-0 error in the last ticks)."""
    keep = ~skip
    addr, age = cand.field(X, 'addr'), cand.field(X, 'age')
    want = np.tile(np.arange(cand.p.Q), X.shape[1] // cand.p.Q)
    return bool(np.array_equal(addr[keep], want[keep]) and np.all(age[keep] == age[keep][0]))


def wiped_level2_bits(cand, dec2, ring_cells):
    """Level-2 bits all five of whose level-1 copies lie in the level-1 ring cells `ring_cells`
    (so the level-1 rule cannot restore them): {level-2 cell: [(field, index, value)]}, with
    the values of the level-2 states dec2."""
    Q = cand.p.Q
    offs = [off for _, off in cand.p.fam().info_copies(cand.p)]
    names = {cand.row[(f, i)]: (f, i) for f, w in cand.schema for i in range(w)}
    N = dec2.shape[1] * Q
    wiped = set(int(x) for x in ring_cells)
    out = {}
    for j in sorted(set(x // Q for x in wiped)):
        for b in range(cand.W):
            if all((j * Q + cand.layout[b] + off) % N in wiped for off in offs):
                out.setdefault(j, []).append(names[b] + (int(dec2[b, j]),))
    return out


def field_cells(cand, A, B):
    """Number of cells in which each field of the unpacked states A and B differs."""
    out = {}
    for f, w in cand.schema:
        r0 = cand.row[(f, 0)]
        n = int((A[r0:r0 + w] != B[r0:r0 + w]).any(axis=0).sum())
        if n:
            out[f] = n
    return out


def phases_cmd(cand, args, rec):
    p = cand.p
    Q, U = p.Q, p.U
    rng = np.random.default_rng(args.seed)
    L2 = codec.random_upper(cand, args.n2, rng)
    L1 = codec.encode(cand, L2)
    F_L2 = cand.step_numpy(L2)
    PL = p.PL
    stages = dict(level2_gathers=2 * Q + 37, level2_early_program=p.E0 + 3 * PL + 11,
                  level2_match_pass=p.E0 + p.MP * PL + PL // 3,
                  level2_final_program=p.E0 + (p.MP + 40) * PL + 5,
                  level2_commit=U - 3)
    names = args.stages.split(',') if args.stages else list(stages)
    starts = level1_states(cand, L1, [stages[n] for n in names])
    # level-1 automaton reference for each start, one level-1 tick per physical level-1 step
    refs = {n: [starts[stages[n]]] for n in names}
    for n in names:
        X = refs[n][0]
        for k in range(args.steps):
            (X,), _ = run_rings(cand, [X], 1)
            refs[n].append(X)
    phys = [codec.encode(cand, starts[stages[n]]) for n in names]
    res = {n: [] for n in names}
    t0 = time.time()

    def check(k, states):
        for r, n in enumerate(names):
            dec1 = codec.decode(cand, states[r])
            ok1 = bool(np.array_equal(dec1, refs[n][k]))
            dec2 = codec.decode(cand, dec1)
            age1 = stages[n] + k
            want2 = F_L2 if age1 >= U else L2
            ok2 = bool(np.array_equal(dec2, want2))
            res[n].append(dict(level1_step=k, level1_age=age1, level1_exact=ok1,
                               level1_cells_wrong=int((dec1 != refs[n][k]).any(axis=0).sum()),
                               level2_equals=('F(level2)' if age1 >= U else 'level2'), level2_exact=ok2))
        print(f'level-1 step {k} ({time.time() - t0:.0f} s): ' +
              ', '.join(f'{n}: L1 {res[n][-1]["level1_exact"]}, L2 {res[n][-1]["level2_exact"]}'
                        for n in names), flush=True)
    _, ms = run_rings(cand, phys, args.steps * U, chunk=U, on_chunk=check)
    rec.update(n2=args.n2, physical_sites_per_ring=phys[0].shape[1], stages={n: stages[n] for n in names},
               results=res, us_per_tick_last_chunk=round(ms * 1000 / U, 1),
               all_level1_exact=all(x['level1_exact'] for n in names for x in res[n]),
               all_level2_exact=all(x['level2_exact'] for n in names for x in res[n]))


def closure2_cmd(cand, args, rec):
    p = cand.p
    rng = np.random.default_rng(args.seed)
    if args.healthy:
        # n2 consecutive level-2 cells of a healthy level-2 colony (an encoded random level-3 cell)
        colony2 = codec.encode(cand, codec.random_upper(cand, 1, rng))
        L2 = colony2[:, (np.arange(args.n2) + p.Q // 2 - args.n2 // 2) % p.Q]
    else:
        L2 = codec.random_upper(cand, args.n2, rng)
    X = codec.encode(cand, L2)
    rows = []
    for k in range(1, args.steps + 1):
        (X,), ms = run_rings(cand, [X], p.U)
        want = cand.step_numpy(L2)
        got = codec.decode(cand, X)
        rows.append(dict(level2_step=k, exact=bool(np.array_equal(got, want)),
                         changed_bits=int((want != L2).sum()), wrong_cells=int((got != want).any(axis=0).sum())))
        print(json.dumps(rows[-1]), flush=True)
        L2 = want
    rec.update(n2=args.n2, healthy=bool(args.healthy), level1_sites=X.shape[1], steps=rows,
               all_exact=all(r['exact'] for r in rows))


def repair2_cmd(cand, args, rec):
    p = cand.p
    Q, U = p.Q, p.U
    C = cand.c_backend()
    rng = np.random.default_rng(args.seed)
    top3 = codec.random_upper(cand, 1, rng)
    colony2 = codec.encode(cand, top3)                       # a healthy level-2 colony (Q level-2 cells)
    if args.level2_age:
        # run the level-2 colony (a ring of exactly one colony, its own neighbour) for
        # --level2-age ticks, so that its cells carry gathered histories, mail, scratch and
        # registers instead of the zeros of a fresh encoding
        (colony2,), _ = run_rings(cand, [colony2], args.level2_age)
    n2 = args.n2
    idx2 = (np.arange(n2) + Q // 2 - n2 // 2) % Q
    L2 = colony2[:, idx2]
    L1_full = codec.encode(cand, L2)                         # Q * n2 level-1 cells
    m2 = n2 // 2                                             # middle level-2 cell
    rec['level2_age'] = args.level2_age
    rec['level2_nonzero_bits_per_cell'] = round(float(L2.sum(axis=0).mean()), 1)
    a = args.level1_age                                      # level-1 age (stage of the level-2 period) at which the wipe happens
    start = level1_states(cand, L1_full, [a])[a]
    # physical slice of the level-1 ring around the middle level-1 cell of the middle level-2 cell,
    # or around the level-1 cells holding the middle level-2 cell's front (its register copies)
    n1 = args.slice
    assert n1 % 64 == 0, '--slice must be a multiple of 64 (the C kernel packs 64 cells per word)'
    mid = m2 * Q + Q // 2
    if args.target == 'front':
        rows = [cand.row[('reg', i)] for i in range(dict(cand.schema)['reg'])]
        cells = np.nonzero(start[rows, m2 * Q:(m2 + 1) * Q].any(axis=0))[0]
        assert len(cells), 'no level-2 front in the middle level-2 cell at this level-1 age'
        # the comb's fronts: a compact fivefold front is held by five consecutive cells (its
        # copies), and the comb's fronts are delta = 5 apart, so a run of register-holding
        # cells splits into fronts of five cells, left to right
        runs, cur = [], [int(cells[0])]
        for x in cells[1:]:
            if x - cur[-1] <= 1:
                cur.append(int(x))
            else:
                runs.append(cur)
                cur = [int(x)]
        runs.append(cur)
        span = int(cells[-1]) - int(cells[0]) + 1
        if span == 5 * cand.p.fronts:
            # the whole comb is visible (a front whose registers are all zero leaves a gap)
            groups = [list(range(int(cells[0]) + 5 * j, int(cells[0]) + 5 * j + 5)) for j in range(cand.p.fronts)]
        else:
            assert all(len(r) % 5 == 0 for r in runs), runs
            groups = [r[i:i + 5] for r in runs for i in range(0, len(r), 5)]
        if args.front_index >= len(groups):
            raise SystemExit(f'front index {args.front_index}: the comb has {len(groups)} fronts here')
        g = groups[args.front_index] if args.front_index >= 0 else list(range(int(cells[0]), int(cells[-1]) + 1))
        mid = m2 * Q + g[len(g) // 2]
        nz = int(start[rows][:, m2 * Q + np.array(g)].sum())
        rec['level2_front_groups'] = groups
        rec['level2_front_target'] = dict(cells=g, nonzero_register_bits=nz)
        print('register-holding groups', groups, 'target', g, 'nonzero register bits', nz, flush=True)
    if args.target == 'field':
        # centre the wipe where it covers all five copies of the most bits of one level-2 field
        offs = [off for _, off in p.fam().info_copies(p)]
        k = max(int(x) for x in args.wipe.split(','))
        pos = [cand.layout[cand.row[(args.field, i)]] for i in range(dict(cand.schema)[args.field])]
        best = None
        for x in range(p.lo, p.hi):
            w0 = x - (k - 1) // 2
            key = (sum(all(w0 <= y + off < w0 + k for off in offs) for y in pos), -abs(x - Q // 2))
            if best is None or key > best[0]:
                best = (key, x)
        mid = m2 * Q + best[1]
        rec['level2_field_target'] = dict(field=args.field, centre=best[1], bits_all_copies_covered=best[0][0])
        print('level-2 field target', rec['level2_field_target'], flush=True)
    sl = (np.arange(n1) + mid - n1 // 2) % L1_full.shape[1]
    phys0 = codec.encode(cand, start[:, sl])
    c = n1 // 2
    wipes = [int(k) for k in args.wipe.split(',')]
    # the level-2 bits whose five level-1 copies all lie in a wipe, and their values
    dec2_start = codec.decode(cand, start)
    rec['level2_bits_all_copies_wiped'] = []
    for k in wipes:
        wb = wiped_level2_bits(cand, dec2_start, sl[c - (k - 1) // 2: c - (k - 1) // 2 + k])
        flat = [(j - m2,) + t for j, lst in wb.items() for t in lst]
        rec['level2_bits_all_copies_wiped'].append(dict(wipe_colonies=k, bits=len(flat),
                                                        ones=sum(t[-1] for t in flat), bits_list=flat[:100]))
    print('level-2 bits with all copies wiped (bits, ones):',
          [(r['wipe_colonies'], r['bits'], r['ones']) for r in rec['level2_bits_all_copies_wiped']], flush=True)
    cfgs = [gpu.noise()]
    for i, k in enumerate(wipes):
        x0 = (c - (k - 1) // 2) * Q
        cfgs.append(gpu.noise(args.seed + 900 + i, e0_grid=args.e0,
                              boxes=[(x0, k * Q, args.wipe_tick, args.wipe_height, 1.0)]))
    if args.e0:
        # dense level-0 noise (Gray's E0 grid, G = --e0) in every wiped ring, plus one ring with
        # the noise alone
        wipes.append(0)
        cfgs.append(gpu.noise(args.seed + 899, e0_grid=args.e0))
    sim = gpu.GpuSim(cand, len(cfgs), n1, mode='grid')
    sim.set_state(C.pack(phys0))
    sim.set_noise(cfgs)
    N = phys0.shape[1]
    phys_rec = []
    prev = None
    t0 = time.time()
    for k in range(1, args.phys_steps + 1):
        sim.run(U)
        S = sim.state()
        X = [C.unpack(S[r], N) for r in range(len(cfgs))]
        dec = [codec.decode(cand, x) for x in X]
        row = dict(level1_step=k, rings=[])
        for r in range(1, len(cfgs)):
            if args.e0:
                h = health_except(cand, X[r], sim.error_masks(cfgs[r], r, sim.t - 2, 2).any(axis=0))
            else:
                h = codec.colony_health(cand, X[r])
                h = bool(h['addr'] and h['age'])
            diff_cells = np.nonzero((dec[r] != dec[0]).any(axis=0))[0]
            clos = None
            if prev is not None:
                (nxt,), _ = run_rings(cand, [prev[r]], 1)
                clos = np.nonzero((dec[r] != nxt).any(axis=0))[0]
                clos = [int(x) for x in clos if 6 <= x < n1 - 6]          # away from the slice ends
            row['rings'].append(dict(wipe_colonies=wipes[r - 1], physical_healthy=h,
                                     level1_cells_differing=[int(x) - c for x in diff_cells],
                                     level1_fields_differing=field_cells(cand, dec[r], dec[0]),
                                     level1_closure_bad_away_from_ends=clos))
        phys_rec.append(row)
        prev = dec
        print(f'physical level-1 step {k} ({time.time() - t0:.0f} s): ' + json.dumps(row['rings']), flush=True)
    # the physical state at the hand-off: which physical fields still differ from the reference,
    # and how many differing sites the encoding of the level-1 difference does not account for
    # (residue below level 1)
    enc0 = codec.encode(cand, dec[0])
    # Info copy slots that hold a represented SimBit (slot `bit` at cell layout[b] + off holds bit b)
    represented = np.zeros((5, N), dtype=bool)
    for bit, off in p.fam().info_copies(p):
        for y in set(int(v) for v in cand.layout):
            represented[bit, (np.arange(y, N, Q) + off) % N] = True
    info_rows = slice(cand.row[('info', 0)], cand.row[('info', 0)] + 5)
    rec['physical_at_handoff'] = []
    for r in range(1, len(cfgs)):
        R = X[r] ^ X[0] ^ codec.encode(cand, dec[r]) ^ enc0
        rec['physical_at_handoff'].append(dict(
            wipe_colonies=wipes[r - 1], fields_differing_from_reference=field_cells(cand, X[r], X[0]),
            sites_not_explained_by_level1_difference=int(R.any(axis=0).sum()),
            unexplained_bits_in_represented_info_slots=int((R[info_rows] & represented).sum()),
            unexplained_bits_elsewhere=int(R.sum() - (R[info_rows] & represented).sum())))
    print('physical at hand-off:', json.dumps(rec['physical_at_handoff']), flush=True)
    if args.verify_handoff:
        # each wiped ring and the plain encoding of its decoded state (a canonical twin) run
        # --verify-handoff more level-1 steps side by side; their decoded states must follow the
        # level-1 automaton, and once they are physically equal the continuation is the twin's
        twins = [C.pack(codec.encode(cand, dec[r])) for r in range(1, len(cfgs))]
        nr = len(cfgs)
        v = gpu.GpuSim(cand, 2 * nr - 1, n1, mode='grid')
        v.set_state(np.stack([S[r] for r in range(nr)] + twins), t=sim.t)
        v.set_noise([gpu.noise()] * (2 * nr - 1))
        cur = [dec[r] for r in range(nr)]
        rec['handoff_check'] = [dict(wipe_colonies=wipes[r - 1], steps=[]) for r in range(1, nr)]
        for k in range(1, args.verify_handoff + 1):
            v.run(U)
            V = v.state()
            for r in range(1, nr):
                xa, xt = C.unpack(V[r], N), C.unpack(V[nr - 1 + r], N)       # (a is the level-1 age)
                da, dt = codec.decode(cand, xa), codec.decode(cand, xt)
                (want,), _ = run_rings(cand, [cur[r]], 1)
                inner = [x for x in np.nonzero((da != want).any(axis=0))[0] if 6 <= x < n1 - 6]
                rec['handoff_check'][r - 1]['steps'].append(dict(
                    level1_step_after_handoff=k,
                    decoded_actual_vs_automaton_away_from_ends=[int(x) for x in inner],
                    decoded_actual_equals_twin=bool(np.array_equal(da, dt)),
                    physical_sites_actual_vs_twin=int((xa != xt).any(axis=0).sum())))
                cur[r] = da
        del v
        print('hand-off check:', json.dumps(rec['handoff_check']), flush=True)
    # apply the decoded damage to the full level-1 ring
    full_ref = level1_states(cand, L1_full, [a + args.phys_steps])[a + args.phys_steps]
    rings = [full_ref]
    for r in range(1, len(cfgs)):
        D = dec[r] ^ dec[0]
        assert not D[:, :8].any() and not D[:, -8:].any(), 'damage reached the slice ends'
        Xd = full_ref.copy()
        Xd[:, sl] ^= D
        rings.append(Xd)
    # continue on the level-1 automaton for --l2-steps level-2 steps
    t_now = a + args.phys_steps
    first_boundary = (t_now // U + 1) * U
    l2_rec = []

    def at_boundary(k, states, fresh=None):
        t = first_boundary + (k - 1) * U
        dec2 = [codec.decode(cand, x) for x in states]
        row = dict(level1_time=t, level2_step=t // U, rings=[])
        for r in range(1, len(states)):
            wrong2 = np.nonzero((dec2[r] != dec2[0]).any(axis=0))[0]
            dmask = (states[r] != states[0]).any(axis=0)
            diff1 = np.nonzero(dmask)[0]
            info1 = states[r][cand.row[('info', 0)]:cand.row[('info', 0)] + 5] != \
                states[0][cand.row[('info', 0)]:cand.row[('info', 0)] + 5]
            row['rings'].append(dict(wipe_colonies=wipes[r - 1],
                                     level2_cells_wrong=[int(x) - m2 for x in wrong2],
                                     level2_fields_wrong=field_cells(cand, dec2[r], dec2[0]),
                                     level1_cells_differing=int(len(diff1)),
                                     level1_cells_differing_span=([int(diff1.min()) // Q - m2, int(diff1.max()) // Q - m2]
                                                                  if len(diff1) else None),
                                     level1_info_cells_differing=int(info1.any(axis=0).sum()),
                                     level1_fields_differing=field_cells(cand, states[r], states[0])))
            if fresh is not None:
                # level-1 cells hit by the level-1 noise in the last two level-1 ticks are excluded
                row['rings'][-1].update(level1_cells_hit_last_two_ticks=int(fresh[r].sum()),
                                        level1_cells_differing_not_hit=int((dmask & ~fresh[r]).sum()))
        l2_rec.append(row)
        print(f'level-2 boundary {t // U} (level-1 time {t}): ' + json.dumps(row['rings']), flush=True)
    # the level-2 state at the hand-off (just after a level-2 commit when the wipe straddled one)
    dec2 = [codec.decode(cand, x) for x in rings]
    rec['level2_at_handoff'] = dict(level1_time=t_now, rings=[
        dict(wipe_colonies=wipes[r - 1],
             level2_cells_wrong=[int(x) - m2 for x in np.nonzero((dec2[r] != dec2[0]).any(axis=0))[0]],
             level2_fields_wrong=field_cells(cand, dec2[r], dec2[0]),
             level1_cells_differing=int((rings[r] != rings[0]).any(axis=0).sum()),
             level1_fields_differing=field_cells(cand, rings[r], rings[0]))
        for r in range(1, len(rings))])
    print('level-2 at hand-off (level-1 time %d): %s' % (t_now, json.dumps(rec['level2_at_handoff']['rings'])),
          flush=True)
    warm = first_boundary - t_now
    if not args.level1_e0:
        rings_w, _ = run_rings(cand, rings, warm)
        at_boundary(1, rings_w)
        run_rings(cand, rings_w, args.l2_steps * U, chunk=U, on_chunk=lambda k, st: at_boundary(k + 1, st))
    else:
        # level-1 errors at the level-0 density of the level-1 automaton (Gray's E0 grid one
        # level up, G = --level1-e0) in every ring but the reference
        N1 = L1_full.shape[1]
        lcfgs = [gpu.noise()] + [gpu.noise(args.seed + 950 + r, e0_grid=args.level1_e0) for r in range(1, len(rings))]
        sim1 = gpu.GpuSim(cand, len(rings), N1 // Q, mode='grid')
        sim1.set_state(np.stack([C.pack(x) for x in rings]), t=t_now)
        sim1.set_noise(lcfgs)
        for k in range(1, args.l2_steps + 2):
            sim1.run(warm if k == 1 else U)
            S1 = sim1.state()
            fresh = [None] + [sim1.error_masks(lcfgs[r], r, sim1.t - 2, 2).any(axis=0) for r in range(1, len(rings))]
            at_boundary(k, [C.unpack(S1[r], N1) for r in range(len(rings))], fresh)
    rec.update(n2=n2, level1_ring=L1_full.shape[1], slice_level1_cells=n1, level1_age_of_wipe=a,
               wipe_tick_in_step1=args.wipe_tick, wipe_height=args.wipe_height, wipes=wipes,
               level0_noise_grid=args.e0, level1_noise_grid=args.level1_e0,
               physical=phys_rec, level2=l2_rec)


def copy2_cmd(cand, args, rec):
    """Level-2 errors with plausible but wrong values, injected one level up: at level-1 age
    --level1-age, k adjacent level-1 cells of the middle level-2 colony are replaced by the
    level-1 cells at the same positions of the next level-2 colony (same level-1 Address and
    Age, the neighbour level-2 cell's SimBits, workspace and front registers). Physically this
    is an error that writes k colonies with copies of colonies one level-2 colony away. Both
    rings then run on the level-1 automaton across --l2-steps level-2 boundaries."""
    p = cand.p
    Q, U = p.Q, p.U
    rng = np.random.default_rng(args.seed)
    colony2 = codec.encode(cand, codec.random_upper(cand, 1, rng))
    if args.level2_age:
        (colony2,), _ = run_rings(cand, [colony2], args.level2_age)
    n2 = args.n2
    L2 = colony2[:, (np.arange(n2) + Q // 2 - n2 // 2) % Q]
    m2 = n2 // 2
    a = args.level1_age
    start = level1_states(cand, codec.encode(cand, L2), [a])[a]
    dec2_start = codec.decode(cand, start)
    if args.target == 'front':
        rows = [cand.row[('reg', i)] for i in range(dict(cand.schema)['reg'])]
        cells = np.nonzero(start[rows, m2 * Q:(m2 + 1) * Q].any(axis=0))[0]
        centre = (int(cells[0]) + int(cells[-1])) // 2
        rec['comb_cells'] = [int(cells[0]), int(cells[-1])]
    else:
        centre = Q // 2
    ks = [int(k) for k in args.wipe.split(',')]
    rings, rows_rec = [start], []
    for k in ks:
        x = np.arange(centre - (k - 1) // 2, centre - (k - 1) // 2 + k)
        X = start.copy()
        X[:, m2 * Q + x] = start[:, (m2 + 1) * Q + x]
        rings.append(X)
        wb = wiped_level2_bits(cand, dec2_start, m2 * Q + x)
        flat = [(j - m2,) + t for j, lst in wb.items() for t in lst]
        rows_rec.append(dict(cells_replaced=k, level1_fields_changed=field_cells(cand, X, start),
                             level2_bits_all_copies_replaced=len(flat),
                             of_which_changed=sum(int(dec2_start[cand.row[(f, i)], m2 + 1] != v) for _, f, i, v in flat)))
    print('injected:', json.dumps(rows_rec), flush=True)
    l2_rec = []
    t_now = a
    first_boundary = (t_now // U + 1) * U

    def at_boundary(kk, states):
        t = first_boundary + (kk - 1) * U
        dec2 = [codec.decode(cand, x) for x in states]
        row = dict(level1_time=t, rings=[])
        for r in range(1, len(states)):
            diff1 = (states[r] != states[0]).any(axis=0)
            row['rings'].append(dict(cells_replaced=ks[r - 1],
                                     level2_cells_wrong=[int(x) - m2 for x in np.nonzero((dec2[r] != dec2[0]).any(axis=0))[0]],
                                     level2_fields_wrong=field_cells(cand, dec2[r], dec2[0]),
                                     level1_cells_differing=int(diff1.sum()),
                                     level1_fields_differing=field_cells(cand, states[r], states[0])))
        l2_rec.append(row)
        print(f'level-2 boundary {t // U} (level-1 time {t}): ' + json.dumps(row['rings']), flush=True)
    rings_w, _ = run_rings(cand, rings, first_boundary - t_now)
    at_boundary(1, rings_w)
    run_rings(cand, rings_w, args.l2_steps * U, chunk=U, on_chunk=lambda kk, st: at_boundary(kk + 1, st))
    rec.update(n2=n2, level2_age=args.level2_age, level1_age=a, centre=centre, injected=rows_rec, level2=l2_rec)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=('phases', 'closure2', 'repair2', 'copy2'))
    ap.add_argument('--candidate', default='G15')
    ap.add_argument('--n2', type=int, default=2)
    ap.add_argument('--steps', type=int, default=6)
    ap.add_argument('--stages', default='')
    ap.add_argument('--healthy', action='store_true', help='closure2: level-2 cells from a healthy level-2 colony')
    ap.add_argument('--slice', type=int, default=64)
    ap.add_argument('--wipe', default='3,5')
    ap.add_argument('--wipe-tick', type=int, default=40000)
    ap.add_argument('--wipe-height', type=int, default=200)
    ap.add_argument('--level1-age', type=int, default=0)
    ap.add_argument('--level2-age', type=int, default=0,
                    help='repair2, copy2: run the level-2 colony this many ticks before slicing it')
    ap.add_argument('--target', default='mid', choices=('mid', 'front', 'field'))
    ap.add_argument('--field', default='age', help='with --target field: the level-2 field to destroy')
    ap.add_argument('--front-index', type=int, default=-1, help='with --target front: which front of the comb, left to right (-1: the whole comb)')
    ap.add_argument('--phys-steps', type=int, default=4)
    ap.add_argument('--verify-handoff', type=int, default=0,
                    help='repair2: run each wiped ring and a canonical twin this many more level-1 steps')
    ap.add_argument('--e0', type=int, default=0, help='repair2: E0 grid G (level-0 noise) in the wiped physical rings')
    ap.add_argument('--level1-e0', type=int, default=0,
                    help='repair2: E0 grid G applied to the level-1 automaton (level-1 errors everywhere)')
    ap.add_argument('--l2-steps', type=int, default=3)
    ap.add_argument('--seed', type=int, default=11)
    ap.add_argument('--tag', default='')
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    cand = candidates.load(args.candidate)
    rec = dict(candidate=args.candidate, cmd=args.cmd, args=vars(args))
    t0 = time.time()
    dict(phases=phases_cmd, closure2=closure2_cmd, repair2=repair2_cmd, copy2=copy2_cmd)[args.cmd](cand, args, rec)
    rec['wall_seconds'] = round(time.time() - t0)
    tag = args.tag or f'{args.candidate}_{args.cmd}'
    with open(os.path.join(OUT, tag + '.json'), 'w') as fh:
        json.dump(rec, fh, indent=1, default=lambda o: o.tolist() if hasattr(o, 'tolist') else str(o))
    print('wrote', tag, 'in', rec['wall_seconds'], 's')


if __name__ == '__main__':
    main()
