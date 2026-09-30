"""Position-driven scheduler ("flow") for the front machine.

Negative result (REPORT §24): best 583 passes on G12's final program
against 509 for the in-order scheduler, with deadlocks for wide admission
windows. Kept as the record of the attempt.

The in-order scheduler (compiler.run_inorder, multifront.run_multi) issues a
depth-first order and prefetches lanes for it: registers are spent on
values that wait for gates far behind in that order. This scheduler
instead lets the front's position choose the work:

  * at every visit it executes the most critical admissible gate whose
    operands are at hand here (registers, constants, lanes or scratch of
    this cell); gates that read a lane or a parked value here come first,
    since the front is back only a pass later;
  * a register value that must leave the register file is parked in
    scratch, preferably at a cell where a consumer reads it;
  * a local value (lane, parked value) is loaded when a gate that needs it
    elsewhere is ready;
  * the breadth of the computation is limited by an admission window on
    the depth-first order (gates beyond `window` of the first unfinished
    gate are not started), which bounds the live set.

Output: a multifront.MultiProgram listing (single front, F = 1), checked
by multifront.replay like the comb scheduler's.
"""
from collections import defaultdict
from . import rule
from .compiler import CompileError, M_OR


def run_flow(sched, comb, prog, pages, targets_hold, init_regs, window=600, reserve=6,
             park_same=True, stats_out=None):
    p, L = sched.p, sched.p.L
    assert comb.F == 1
    mops = sched.mops
    roots = [v for v, _ in targets_hold]
    gates = sched.cone(roots)
    order = sched.dfs_order(roots, gates)
    rank = {g: i for i, g in enumerate(order)}
    lane_loc = sched.lane_loc
    C0, C1 = sched.C0, sched.C1
    # consumers and remaining uses
    cons = defaultdict(list)
    uses = defaultdict(int)
    for g in order:
        _, a, b = mops[g]
        for z in {a, b}:
            cons[z].append(g)
        uses[a] += 1
        uses[b] += 1
    pend_cells = defaultdict(list)
    for v, cell in targets_hold:
        uses[v] += 1
        pend_cells[v].append(cell)
    pending_hold = defaultdict(list)
    for v, cell in targets_hold:
        pending_hold[cell].append(v)
    n_pending = len(targets_hold)
    # criticality: longest path (in gates) to an output
    height = {}
    for g in reversed(order):
        hs = [height[u] for u in cons.get(g, ()) if u in height]
        height[g] = 1 + (max(hs) if hs else 0)
    # lane consumers by cell
    lane_users = defaultdict(set)
    for v, (cell, _) in lane_loc.items():
        for g in cons.get(v, ()):
            lane_users[cell].add(g)
    reg = [None] * L
    regs_of = defaultdict(set)
    for r, v in init_regs.items():
        reg[r] = v
        regs_of[v].add(r)
    scr, scr_of = {}, defaultdict(set)
    done = set()
    ndep = {}
    for g in order:
        _, a, b = mops[g]
        ndep[g] = len({z for z in (a, b) if z in gates})
    ready = {g for g in order if ndep[g] == 0}
    frontier = 0

    def admissible(g):
        return rank[g] < frontier + window

    def code_at(v, c):
        if v == 0: return C0
        if v == 1: return C1
        rs = regs_of.get(v)
        if rs: return min(rs)
        if v in lane_loc:
            code = sched.lane_code(v, c)
            if code is not None: return code
        for (cc, s_) in scr_of.get(v, ()):
            if cc == c:
                return sched.src_code[('scr', s_)]
        return None

    def release(v):
        if uses[v] > 0: return
        for r in list(regs_of.get(v, ())):
            reg[r] = None
        regs_of.pop(v, None)
        for key in list(scr_of.get(v, ())):
            scr.pop(key, None)
        scr_of.pop(v, None)

    def consume(v):
        if v in (0, 1): return
        uses[v] -= 1
        release(v)

    def put_reg(v, r):
        old = reg[r]
        if old is not None:
            regs_of[old].discard(r)
        reg[r] = v
        regs_of[v].add(r)

    def n_free():
        return sum(1 for x in reg if x is None)

    def free_reg():
        for r in range(L):
            if reg[r] is None:
                return r
        return None

    def finish(g):
        nonlocal frontier
        done.add(g)
        ready.discard(g)
        for u in cons.get(g, ()):
            if u in gates:
                ndep[u] -= 1
                if ndep[u] == 0:
                    ready.add(u)
        while frontier < len(order) and order[frontier] in done:
            frontier += 1

    def local_value_cells(v):
        cells = [cc for cc, _ in scr_of.get(v, ())]
        if v in lane_loc:
            cells.append(lane_loc[v][0])
        return cells

    def needs_elsewhere(z, c):
        """Some admissible ready consumer of z cannot run at c."""
        for u in cons.get(z, ()):
            if u in ready and admissible(u):
                _, a, b = mops[u]
                other = b if a == z else a
                if other in (0, 1) or regs_of.get(other) or code_at(other, c) is not None:
                    continue       # it can run here (then it is a candidate itself)
                return u
        return None

    def park_score(v, c):
        """(heat, cost): lower = better candidate to leave the register file
        at cell c. heat 0: no admissible consumer; 1: admissible consumer
        not ready; 2: ready consumer; 3: ready consumer runnable now or at a
        cell ahead with everything else at hand. cost 0: another copy
        exists (lane, scratch, second register); 1: needs a scratch write."""
        heat = 0
        for u in cons.get(v, ()):
            if u in done or not admissible(u):
                continue
            if u not in ready:
                heat = max(heat, 1)
                continue
            _, a, b = mops[u]
            other = b if a == v else a
            if other in (0, 1) or regs_of.get(other) or other in lane_loc or scr_of.get(other):
                heat = 3
                break
            heat = max(heat, 2)
        if v in pend_cells and pend_cells[v]:
            heat = max(heat, 1)
        cost = 0 if (v in lane_loc or scr_of.get(v) or len(regs_of[v]) > 1) else 1
        nxt = min((rank[u] for u in cons.get(v, ()) if u not in done), default=10**9)
        return (heat, cost, -nxt)

    idle = defaultdict(int)
    last_page = None
    for pg, tk, vis in comb.ticks(pages):
        if n_pending == 0:
            break
        last_page = pg
        for j, c in vis:
            # 1. stores due here
            acted = False
            for v in list(pending_hold.get(c, ())):
                if v in gates and v not in done:
                    continue
                cv = code_at(v, c)
                if cv is not None:
                    prog.put(0, pg, tk, c, M_OR, rule.K_HOLD, cv, C0, 0, ('store', v))
                    pending_hold[c].remove(v)
                    pend_cells[v].remove(c)
                    n_pending -= 1
                    consume(v)
                    acted = True
                    break
            if acted:
                continue
            # 2. execute the best gate runnable here
            cands = set()
            for g in lane_users.get(c, ()):
                if g in ready:
                    cands.add(g)
            for s_ in range(p.S):
                v = scr.get((c, s_))
                if v is not None:
                    for g in cons.get(v, ()):
                        if g in ready:
                            cands.add(g)
            for v in list(regs_of):
                if regs_of[v]:
                    for g in cons.get(v, ()):
                        if g in ready:
                            cands.add(g)
            for g in list(ready):
                if len(cands) > 4000:
                    break
                _, a, b = mops[g]
                if a in (0, 1) and b in (0, 1):
                    cands.add(g)
            best = None
            nf = n_free()
            for g in cands:
                if not admissible(g):
                    continue
                op, a, b = mops[g]
                ca, cb = code_at(a, c), code_at(b, c)
                if ca is None or cb is None:
                    continue
                local = any(z not in (0, 1) and not regs_of.get(z) for z in (a, b))
                kills = sum(1 for z in {a, b} if z not in (0, 1) and uses[z] == (2 if a == b else 1)
                            and regs_of.get(z) and len(regs_of[z]) == 1)
                delta = 1 - kills
                if delta > 0 and nf == 0 and not any((c, x) not in scr for x in range(p.S)):
                    continue
                key = (local, -delta if nf <= reserve else 0, height[g], -rank[g])
                if best is None or key > best[0]:
                    best = (key, g, op, a, b, ca, cb)
            if best is not None:
                _, g, op, a, b, ca, cb = best
                dest = None
                for z in {a, b}:
                    if z not in (0, 1) and uses[z] == (2 if a == b else 1) and regs_of.get(z):
                        dest = min(regs_of[z])
                        break
                if dest is None:
                    dest = free_reg()
                if dest is None:
                    # park something here to make room
                    cand = [(park_score(reg[r], c), r) for r in range(L)
                            if reg[r] is not None and reg[r] not in (a, b)]
                    cand.sort()
                    if cand:
                        sc, r = cand[0]
                        v = reg[r]
                        if sc[1] == 0:
                            regs_of[v].discard(r)
                            reg[r] = None
                            dest = r
                        else:
                            s_ = next((x for x in range(p.S) if (c, x) not in scr), None)
                            if s_ is not None:
                                prog.put(0, pg, tk, c, M_OR, rule.K_SCR, r, C0, s_, ('park', v))
                                scr[(c, s_)] = v
                                scr_of[v].add((c, s_))
                                regs_of[v].discard(r)
                                reg[r] = None
                                continue
                    if dest is None:
                        idle['no-register'] += 1
                        continue
                prog.put(0, pg, tk, c, op, rule.K_REG, ca, cb, dest, ('gate', g))
                consume(a)
                consume(b)
                put_reg(g, dest)
                finish(g)
                continue
            # 3. park a register value whose consumer reads it here later
            if park_same and n_free() <= reserve:
                s_ = next((x for x in range(p.S) if (c, x) not in scr), None)
                if s_ is not None:
                    cand = [(park_score(reg[r], c), r) for r in range(L) if reg[r] is not None]
                    cand.sort()
                    if cand and cand[0][0][0] <= 1:
                        sc, r = cand[0]
                        v = reg[r]
                        if sc[1] == 0:
                            regs_of[v].discard(r)
                            reg[r] = None
                        else:
                            prog.put(0, pg, tk, c, M_OR, rule.K_SCR, r, C0, s_, ('park', v))
                            scr[(c, s_)] = v
                            scr_of[v].add((c, s_))
                            regs_of[v].discard(r)
                            reg[r] = None
                            continue
            # 4. load a local value a ready consumer needs elsewhere
            want = None
            locals_here = []
            for g in lane_users.get(c, ()):
                if g in ready and admissible(g):
                    _, a, b = mops[g]
                    for z in (a, b):
                        if z in lane_loc and lane_loc[z][0] == c and not regs_of.get(z):
                            locals_here.append((height[g], z))
            for s_ in range(p.S):
                v = scr.get((c, s_))
                if v is not None and not regs_of.get(v):
                    for g in cons.get(v, ()):
                        if g in ready and admissible(g):
                            locals_here.append((height[g], v))
                    if v in pend_cells and any(x != c for x in pend_cells[v]):
                        locals_here.append((0, v))
            locals_here.sort(reverse=True)
            for h, z in locals_here:
                if needs_elsewhere(z, c) is not None or (z in pend_cells and pend_cells[z]
                                                        and c not in pend_cells[z]):
                    want = z
                    break
            if want is not None:
                r = free_reg()
                if r is None:
                    cand = [(park_score(reg[x], c), x) for x in range(L) if reg[x] is not None]
                    cand.sort()
                    if cand and cand[0][0][1] == 0 and cand[0][0][0] <= 1:
                        r = cand[0][1]
                        regs_of[reg[r]].discard(r)
                        reg[r] = None
                if r is not None:
                    prog.put(0, pg, tk, c, M_OR, rule.K_REG, code_at(want, c), C0, r, ('load', want))
                    put_reg(want, r)
                    continue
            idle['idle'] += 1
    if stats_out is not None:
        stats_out.update(idle=dict(idle), last_page=last_page, left=len(gates) - len(done),
                         pending=n_pending)
        if frontier < len(order):
            g = order[frontier]
            _, a, b = mops[g]
            def where(z):
                return dict(done=z in done, gate=z in gates, lane=lane_loc.get(z, (None,))[0],
                            regs=sorted(regs_of.get(z, ())), scr=sorted(scr_of.get(z, ())))
            stats_out['frontier'] = dict(rank=frontier, ready=g in ready, a=where(a), b=where(b))
        stats_out['regs'] = [(r, v in done if v is not None else None, v in lane_loc if v is not None else None,
                              min((rank[u] for u in cons.get(v, ()) if u not in done), default=None) if v is not None else None)
                             for r, v in enumerate(reg)][:64]
        stats_out['scr_used'] = len(scr)
        # why is nothing runnable? for each register value: its admissible ready consumers and the other operand
        rows = []
        for r, v in enumerate(reg):
            if v is None:
                continue
            info = []
            for u in cons.get(v, ()):
                if u in done:
                    continue
                _, a, b = mops[u]
                other = b if a == v else a
                info.append(dict(adm=admissible(u), ready=u in ready,
                                 other=('const' if other in (0, 1) else 'reg' if regs_of.get(other) else
                                        f"lane@{lane_loc[other][0]}" if other in lane_loc else
                                        f"scr@{sorted(cc for cc, _ in scr_of.get(other, ()))}" if scr_of.get(other) else
                                        'notdone' if other in gates and other not in done else 'lost')))
            rows.append((r, park_score(v, -1), info[:3]))
        stats_out['reg_detail'] = rows
        occ = defaultdict(int)
        for (cc, s_) in scr:
            occ[cc] += 1
        stats_out['scr_full_cells'] = sum(1 for cc in occ if occ[cc] >= p.S)
    if n_pending:
        raise CompileError(f'flow unfinished: {n_pending} stores, {len(gates) - len(done)} gates left, '
                           f'idle {dict(idle)}')
    return last_page
