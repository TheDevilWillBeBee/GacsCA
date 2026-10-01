"""Multi-front ("comb") scheduling for the G family.

F fronts move in lockstep, spaced `delta` cells apart. In a forward pass
front j is at lo - H + t + j*delta (H = (F-1)*delta, t = 0..W+H-1); a
backward pass is the same motion time-reversed. Every front therefore visits
every working cell once per pass, and a pass lasts W + H ticks; the comb
overhangs the working range by H cells at the ends, where it only carries its
registers. At a visit a front executes one instruction of its own program
(Pi[address][page, front]) with its own register file; the fronts share the
lanes and the scratch bits of the cells.

Communication between fronts goes through scratch: the producing front
writes a value into a scratch bit of the cell it is at, and a consuming front
reads it when it visits that cell. In a forward pass a lower-index front
visits a cell after a higher-index one (delta*(j'-j) ticks later); in a
backward pass the order is reversed.

The partition assigns every gate of the machine DAG to one front:
  * upper bits (field, i) are dealt to fronts by the rank of their layout
    cell (interleaved), and every lane of a bit belongs to the bit's owner;
  * a gate whose cone reads lanes of one owner only goes to that owner;
  * a gate that feeds a single Hold root goes to the root's owner;
  * a gate derived only from constants and the initial registers goes to
    front 0 (which holds the fetched instruction and key);
  * remaining (combining) gates go to front 0, or with `combine='spread'`
    to the owner holding most of its cone's leaves.
Associative trees can first be regrouped by owner (`reassociate_by_owner`),
so that each front folds its own leaves into a partial result.

`replay` executes a compiled multi-front listing on random data and checks
every Hold store against the netlist: it validates the scheduler, not the
physical rule.
"""
from collections import defaultdict
import heapq
import numpy as np
from . import rule
from .compiler import (CompileError, work_range, M_AND, M_OR, M_XOR, M_ANDN)


class Comb:
    def __init__(self, p, F, delta):
        self.p, self.F, self.delta = p, F, delta
        self.lo, self.hi = work_range(p)
        self.W = self.hi - self.lo
        self.H = (F - 1) * delta
        self.PL = self.W + self.H

    def ticks(self, pages):
        """(page, tick, [(front, cell)]) for every tick of the given pages;
        only visits inside the working range are listed."""
        lo, hi, H = self.lo, self.hi, self.H
        for pg in sorted(pages):
            for t in range(self.PL):
                tt = t if pg % 2 == 0 else self.PL - 1 - t
                vis = []
                for j in range(self.F):
                    c = lo - H + tt + j * self.delta
                    if lo <= c < hi:
                        vis.append((j, c))
                # the front that is first at a cell in this direction acts first
                if pg % 2 == 0:
                    vis.reverse()
                yield pg, t, vis


class MultiProgram:
    def __init__(self, p, F):
        self.p, self.F = p, F
        self.used = defaultdict(set)          # (front, page) -> cells used
        self.listing = []
        self.seq = 0

    def put(self, front, page, tick, cell, op, kind, a, b, d, note=None):
        key = (front, page)
        assert cell not in self.used[key]
        self.used[key].add(cell)
        self.listing.append((self.seq, page, tick, front, cell, op, kind, a, b, d, note))
        self.seq += 1

    def count(self):
        return len(self.listing)


def bit_owners(sched, F, mode='interleave', seed=None):
    """Owner front of every upper bit (field, i), by the rank of its cell
    (with a seed: the fronts are relabelled by a random permutation per
    block of F consecutive cells)."""
    cells = sorted(int(x) for x in sched.layout)
    rank = {c: r for r, c in enumerate(cells)}
    own = {}
    n = len(cells)
    perm = None
    if seed is not None:
        rng = np.random.default_rng(seed)
        perm = [rng.permutation(F) for _ in range(n // F + 1)]
    for (f, i), b in sched.bit.items():
        r = rank[int(sched.layout[b])]
        o = r % F if mode == 'interleave' else (r * F) // n
        if perm is not None:
            o = int(perm[r // F][o])
        own[(f, i)] = o
    return own


CTRL_FIELDS = ('addr', 'age', 'f1', 'f2', 'wf1', 'wf2')


def input_owner(sched, owners, ctrl_fields=CTRL_FIELDS):
    """Owner of every netlist input node that is a lane (by its upper bit).
    Lanes of control fields (Address, Age, flags) are not owned: values
    derived from them are broadcast to the fronts that need them."""
    out = {}
    for name, node in sched.comp.index.items():
        if name[0] == 'x':
            _, j, f, i = name
            if f not in ctrl_fields:
                out[node] = owners[(f, i)]
    return out


MULTI = -2


def owner_classes(mops, topo, leaf_owner, cut=True):
    """Owner class of every node: a front index, -1 when the node depends on
    no owned lane (constants, front 0's registers), MULTI when it combines
    data of several owners. With cut=True a MULTI operand counts as a
    broadcast (control) value and does not make its consumers MULTI."""
    cls = dict(leaf_owner)
    for x in topo:
        _, a, b = mops[x]
        fr = set()
        for z in (a, b):
            o = cls.get(z, -1)
            if o >= 0:
                fr.add(o)
            elif o == MULTI and not cut:
                fr.add(MULTI)
        if MULTI in fr or len(fr) > 1:
            cls[x] = MULTI
        elif fr:
            cls[x] = fr.pop()
        else:
            cls[x] = -1
    return cls


def reassociate_by_owner(sched, leaf_owner, protect, cut=True):
    """Regroup every maximal AND/OR/XOR tree with single-use inner nodes into
    per-owner partial chains, combined in owner order. Leaves whose own cone
    mixes owners are folded in last. Same function as before."""
    mops = dict(sched.mops)
    fan = defaultdict(int)
    for x, (op, a, b) in mops.items():
        fan[a] += 1
        fan[b] += 1
    rank = getattr(sched, 'rank', None)
    topo = sorted(mops, key=rank.get if rank else None)
    cls = owner_classes(mops, topo, leaf_owner, cut)

    def owner_key(z):
        o = cls.get(z, -1)
        return (0, o) if o >= 0 else (1, 0)
    protect = set(protect)
    next_id = max(mops) + 1
    n_trees = 0
    for x in list(reversed(topo)):
        if x not in mops:
            continue
        op, a, b = mops[x]
        if op not in (M_AND, M_OR, M_XOR):
            continue
        leaves, internal, stack = [], [], [a, b]
        while stack:
            z = stack.pop()
            if z in mops and z not in protect and fan[z] == 1 and mops[z][0] == op:
                internal.append(z)
                stack += [mops[z][1], mops[z][2]]
            else:
                leaves.append(z)
        if len(leaves) < 3:
            continue
        groups = defaultdict(list)
        for z in leaves:
            groups[owner_key(z)].append(z)
        if len(groups) < 2:
            continue
        partials = []
        for key in sorted(groups):
            zs = sorted(groups[key])
            prev = zs[0]
            for z in zs[1:]:
                mops[next_id] = (op, prev, z)
                prev = next_id
                next_id += 1
            partials.append(prev)
        prev = partials[0]
        for z in partials[1:-1]:
            mops[next_id] = (op, prev, z)
            prev = next_id
            next_id += 1
        mops[x] = (op, prev, partials[-1])
        for z in internal:
            del mops[z]
        n_trees += 1
    # topological rank of the rewritten DAG
    rank, indeg, succ = {}, defaultdict(int), defaultdict(list)
    for x, (_, a, b) in mops.items():
        for z in {a, b}:
            if z in mops:
                indeg[x] += 1
                succ[z].append(x)
    ready = [x for x in mops if indeg[x] == 0]
    heapq.heapify(ready)
    while ready:
        x = heapq.heappop(ready)
        rank[x] = len(rank)
        for w in succ[x]:
            indeg[w] -= 1
            if indeg[w] == 0:
                heapq.heappush(ready, w)
    assert len(rank) == len(mops)
    sched.mops, sched.rank = mops, rank
    return n_trees


def partition(sched, F, holds, root_owner, leaf_owner, combine='front0', cut=True):
    """Assign every gate in the cone of `holds` ((value, cell) pairs; the
    root's owner is root_owner[cell]) to a front."""
    roots = [v for v, _ in holds]
    gates = sched.cone(roots)
    topo = sched.topo_sorted(gates)
    cls = owner_classes(sched.mops, topo, leaf_owner, cut)
    # single-root membership (top-down): root id or -1 for several
    rootof = {}
    for v, cell in holds:
        if v in gates:
            o = root_owner[cell]
            rootof[v] = o if rootof.get(v, o) == o else -1
    for g in reversed(topo):
        r = rootof.get(g)
        if r is None:
            continue
        _, a, b = sched.mops[g]
        for z in (a, b):
            if z in gates:
                rootof[z] = r if rootof.get(z, r) == r else -1
    assign = {}
    for g in topo:
        o = cls[g]
        if o >= 0:
            assign[g] = o
        elif rootof.get(g, -1) >= 0:
            assign[g] = rootof[g]
        elif o == -1:
            continue
        elif combine == 'spread':
            _, a, b = sched.mops[g]
            assign[g] = assign.get(a, assign.get(b, 0)) if a in gates else assign.get(b, 0)
        elif combine == 'owned':
            # follow an operand owned by a single front (lane or gate), else
            # the front of a computed operand
            _, a, b = sched.mops[g]
            own = [cls.get(z, -1) for z in (a, b) if cls.get(z, -1) >= 0]
            if own:
                assign[g] = own[0]
            else:
                fr = [assign[z] for z in (a, b) if z in assign]
                assign[g] = fr[0] if fr else 0
        else:
            assign[g] = 0
    # gates derived only from constants and front 0's registers: computed on
    # the front of their consumers when that is a single front, else front 0
    users = defaultdict(set)
    for g in topo:
        _, a, b = sched.mops[g]
        users[a].add(g)
        users[b].add(g)
    for g in reversed(topo):
        if g in assign:
            continue
        fr = {assign[u] for u in users[g] if u in assign}
        assign[g] = fr.pop() if len(fr) == 1 else 0
    return assign


def _rank(sched):
    rank, indeg, succ = {}, defaultdict(int), defaultdict(list)
    for x, (_, a, b) in sched.mops.items():
        for z in {a, b}:
            if z in sched.mops:
                indeg[x] += 1
                succ[z].append(x)
    ready = [x for x in sched.mops if indeg[x] == 0]
    heapq.heapify(ready)
    while ready:
        x = heapq.heappop(ready)
        rank[x] = len(rank)
        for w in succ[x]:
            indeg[w] -= 1
            if indeg[w] == 0:
                heapq.heappush(ready, w)
    assert len(rank) == len(sched.mops)
    sched.rank = rank


def replicate_ctrl(sched, assign, holds, leaf_owner, cut=True):
    """Give every front its own copy of the control gates (class -1: derived
    only from unowned lanes, constants and front 0's registers) that its
    other gates need, so control values are recomputed from lanes instead of
    being sent between fronts. Rewrites sched.mops and extends `assign`."""
    roots = [v for v, _ in holds]
    gates = sched.cone(roots)
    topo = sched.topo_sorted(gates)
    cls = owner_classes(sched.mops, topo, leaf_owner, cut)
    ctrl = {g for g in gates if cls[g] == -1}
    held = {v for v, _ in holds}
    # fronts needing each control gate (through non-control consumers)
    need = defaultdict(set)
    for g in reversed(topo):
        if g in ctrl:
            continue
        _, a, b = sched.mops[g]
        for z in (a, b):
            if z in ctrl:
                need[z].add(assign[g])
    for g in reversed(topo):
        if g not in ctrl:
            continue
        if g in held:
            need[g].add(assign.get(g, 0) if g in assign else 0)
        _, a, b = sched.mops[g]
        for z in (a, b):
            if z in ctrl:
                need[z] |= need[g]
    next_id = max(sched.mops) + 1
    clone = {}
    n_clones = 0
    for g in topo:
        if g not in ctrl:
            continue
        fr = sorted(need[g]) or [0]
        assign[g] = fr[0]
        for j in fr[1:]:
            op, a, b = sched.mops[g]
            clone[(g, j)] = next_id
            sched.mops[next_id] = (op, clone.get((a, j), a), clone.get((b, j), b))
            assign[next_id] = j
            next_id += 1
            n_clones += 1
        # the original's operands stay the first front's
        op, a, b = sched.mops[g]
        j0 = fr[0]
        sched.mops[g] = (op, clone.get((a, j0), a), clone.get((b, j0), b))
    for g in topo:
        if g in ctrl:
            continue
        op, a, b = sched.mops[g]
        j = assign[g]
        sched.mops[g] = (op, clone.get((a, j), a), clone.get((b, j), b))
    _rank(sched)
    return n_clones


def asap_times(sched, comb, gates):
    """Earliest tick of every gate when slots and registers are unlimited:
    a gate reading a lane runs at the first visit (by any front) of the
    lane's cell after its operands are ready; other gates one tick after
    their operands."""
    lo, H, PL, F, dl = comb.lo, comb.H, comb.PL, comb.F, comb.delta

    def visit(c, t0):
        pg0 = t0 // PL
        for pg in range(pg0, pg0 + 3):
            best = None
            for j in range(F):
                tt = c - (lo - H) - j * dl
                t = tt if pg % 2 == 0 else PL - 1 - tt
                T = pg * PL + t
                if T >= t0 and (best is None or T < best):
                    best = T
            if best is not None:
                return best
        raise AssertionError
    T = {}
    for g in sched.topo_sorted(gates):
        _, a, b = sched.mops[g]
        rdy = max(T.get(a, 0), T.get(b, 0)) + 1
        cells = [sched.lane_loc[z][0] for z in (a, b) if z in sched.lane_loc]
        if not cells:
            T[g] = rdy
        elif len(cells) == 1 or cells[0] == cells[1]:
            T[g] = visit(cells[0], rdy)
        else:
            T[g] = min(visit(cells[0], visit(cells[1], rdy) + 1),
                       visit(cells[1], visit(cells[0], rdy) + 1))
    return T


def sweep_order(sched, comb, roots, gates, lam=50.0, window=300, dfs=None):
    """Issue order from a sequential model of the front: one instruction per
    tick, a gate reading a lane runs at the lane cell's next visit (two lanes
    on different cells: a load at one, then the gate at the other), other
    gates one tick later. Among the ready gates within `window` of the
    depth-first frontier, the next one minimizes (ticks until it can run)
    + lam * (change in the number of live computed values); ties by
    depth-first rank. Registers are not modelled (the in-order executor
    handles them)."""
    import bisect
    lo, H, PL, F, dl = comb.lo, comb.H, comb.PL, comb.F, comb.delta
    mops, lane_loc = sched.mops, sched.lane_loc

    def visit(c, t0):
        pg0 = t0 // PL
        for pg in range(pg0, pg0 + 3):
            best = None
            for j in range(F):
                tt = c - (lo - H) - j * dl
                t = tt if pg % 2 == 0 else PL - 1 - tt
                T = pg * PL + t
                if T >= t0 and (best is None or T < best):
                    best = T
            if best is not None:
                return best
        raise AssertionError
    if dfs is None:
        dfs = sched.dfs_order(roots, gates)
    rank = {g: i for i, g in enumerate(dfs)}
    cons = defaultdict(list)
    for g in dfs:
        _, a, b = mops[g]
        for z in {a, b}:
            if z in gates:
                cons[z].append(g)
    rem = {g: len(cons[g]) for g in dfs}
    held = set(roots)
    ndep = {g: len({z for z in mops[g][1:] if z in gates}) for g in dfs}
    ready = sorted(rank[g] for g in dfs if ndep[g] == 0)
    done = set()
    frontier = 0
    T = 0
    out = []
    while ready:
        best = None
        lim = frontier + window
        for r in ready:
            if r >= lim and best is not None:
                break
            g = dfs[r]
            _, a, b = mops[g]
            cells = sorted({lane_loc[z][0] for z in (a, b) if z in lane_loc})
            if not cells:
                t = T + 1
            elif len(cells) == 1:
                t = visit(cells[0], T + 1)
            else:
                x, y = cells
                t = min(visit(y, visit(x, T + 1) + 1), visit(x, visit(y, T + 1) + 1))
            kills = sum(1 for z in {a, b} if z in gates and rem[z] == 1 and z not in held)
            dlive = (1 if (cons[g] or g in held) else 0) - kills
            key = (t - T + lam * dlive, r)
            if best is None or key < best[0]:
                best = (key, r, g, t)
        _, r, g, t = best
        T = t
        out.append(g)
        done.add(g)
        ready.remove(r)
        for z in set(mops[g][1:]):
            if z in rem:
                rem[z] -= 1
        for u in cons[g]:
            ndep[u] -= 1
            if ndep[u] == 0:
                bisect.insort(ready, rank[u])
        while frontier < len(dfs) and dfs[frontier] in done:
            frontier += 1
    assert len(out) == len(dfs)
    sched.last_model_ticks = T
    return out


def run_multi(sched, comb, prog, pages, targets_hold, init_regs, assign, store_owner,
              lookahead=300, ooo=32, targets_reg=None, eager_export=True, free_floor=10**9,
              order_kind='dfs', profile=None, jit=0.0, rate_floor=0.01, trace=None, hop_order=0,
              boost_shared=False):
    """In-order issue per front (the global depth-first order restricted to
    the front's gates) with lane prefetch, Belady replacement and export of
    values other fronts need through scratch. init_regs are front 0's."""
    p, L, F = sched.p, sched.p.L, comb.F
    targets_reg = dict(targets_reg or {})
    roots = list(targets_reg) + [v for v, _ in targets_hold]
    gates = sched.cone(roots)
    order = sched.dfs_order(roots, gates)
    if isinstance(order_kind, (tuple, list)) and order_kind[0] == 'interleave':
        order = sched.interleaved_order(roots, gates, order_kind[1])
    elif isinstance(order_kind, tuple) and order_kind[0] == 'sweep':
        order = sweep_order(sched, comb, roots, gates, lam=order_kind[1], window=order_kind[2], dfs=order)
    elif isinstance(order_kind, dict):
        # explicit priority (e.g. execution ticks of an earlier schedule)
        rank = {g: q for q, g in enumerate(order)}
        order = sorted(order, key=lambda g: (order_kind.get(g, 10**12), rank[g]))
    elif order_kind == 'asap':
        T = asap_times(sched, comb, gates)
        rank = {g: q for q, g in enumerate(order)}
        order = sorted(order, key=lambda g: (T[g], rank[g]))
    elif order_kind == 'asap-pass':
        # ASAP pass, depth-first inside a pass
        T = asap_times(sched, comb, gates)
        rank = {g: q for q, g in enumerate(order)}
        order = sorted(order, key=lambda g: (T[g] // comb.PL, rank[g]))
    if boost_shared:
        # the cone of values consumed on several fronts is issued first, so
        # that it is exported before the other fronts need it
        fr_use = defaultdict(set)
        for g in gates:
            _, a, b = sched.mops[g]
            for z in (a, b):
                if z in gates:
                    fr_use[z].add(assign[g])
        shared = [g for g in gates if len(fr_use[g] | {assign[g]}) > 1]
        cone = sched.cone(shared) & gates
        pos0 = {g: q for q, g in enumerate(order)}
        order = sorted(order, key=lambda g: (g not in cone, pos0[g]))
    if hop_order:
        # per front: work with fewer cross-front hops on its longest input path first
        rd = {}
        for g in sched.topo_sorted(gates):
            _, a, b = sched.mops[g]
            rd[g] = max([rd[z] + (assign[z] != assign[g]) for z in (a, b) if z in rd] or [0])
        pos0 = {g: q for q, g in enumerate(order)}
        order = sorted(order, key=lambda g: (min(rd[g], hop_order), pos0[g]))
    forder = [[g for g in order if assign[g] == j] for j in range(F)]
    fpos = [{g: q for q, g in enumerate(o)} for o in forder]
    mops = sched.mops
    producer = {g: assign[g] for g in gates}
    for v in init_regs.values():
        producer.setdefault(v, 0)
    uses = defaultdict(int)
    cons = [defaultdict(list) for _ in range(F)]
    remote = defaultdict(int)
    for j in range(F):
        for q, g in enumerate(forder[j]):
            _, a, b = mops[g]
            for z in (a, b):
                uses[z] += 1
                cons[j][z].append(q)
                if z in producer and producer[z] != j:
                    remote[z] += 1
    for v, cell in targets_hold:
        uses[v] += 1
        if v in producer and producer[v] != store_owner(v, cell):
            remote[v] += 1
    for v in targets_reg:
        uses[v] += 1
        if v in producer and producer[v] != 0:
            remote[v] += 1
    reg = [[None] * L for _ in range(F)]
    regs_of = [defaultdict(set) for _ in range(F)]
    for r, v in init_regs.items():
        reg[0][r] = v
        regs_of[0][v].add(r)
    scr, scr_of = {}, defaultdict(set)
    done = set()
    pending_hold = defaultdict(list)          # cell -> values to store there
    cells_of = defaultdict(list)
    for v, cell in targets_hold:
        pending_hold[cell].append(v)
        cells_of[v].append(cell)
    n_pending = len(targets_hold)
    export = [[] for _ in range(F)]
    store_due = [dict() for _ in range(F)]
    for v, cell in targets_hold:
        jj = store_owner(v, cell)
        store_due[jj][v] = fpos[jj].get(v, 0) + lookahead
    for v in init_regs.values():
        if remote[v] > 0:
            export[0].append(v)
    C0, C1 = sched.C0, sched.C1
    lane_loc = sched.lane_loc
    head = [0] * F
    cons_ptr = [defaultdict(int) for _ in range(F)]
    reserved = set()

    def code_at(j, v, c):
        if v == 0: return C0
        if v == 1: return C1
        rs = regs_of[j].get(v)
        if rs: return min(rs)
        if v in lane_loc:
            code = sched.lane_code(v, c)
            if code is not None: return code
        for (cc, s_) in scr_of.get(v, ()):
            code = sched.scr_code(s_, cc, c)
            if code is not None: return code
        return None

    def next_use(j, v):
        lst = cons[j].get(v, ())
        i = cons_ptr[j][v]
        while i < len(lst) and forder[j][lst[i]] in done:
            i += 1
        cons_ptr[j][v] = i
        if i < len(lst):
            return lst[i]
        return store_due[j].get(v, 10**9)

    def release(v):
        if uses[v] > 0: return
        for j in range(F):
            for r in list(regs_of[j].get(v, ())):
                reg[j][r] = None
            regs_of[j].pop(v, None)
        for key in list(scr_of.get(v, ())):
            scr.pop(key, None)
        scr_of.pop(v, None)

    def consume(j, v):
        uses[v] -= 1
        if v in producer and producer[v] != j:
            remote[v] -= 1
        release(v)

    def put_reg(j, v, r):
        old = reg[j][r]
        if old is not None:
            regs_of[j][old].discard(r)
        reg[j][r] = v
        regs_of[j][v].add(r)

    def drop(j, r):
        v = reg[j][r]
        regs_of[j][v].discard(r)
        reg[j][r] = None

    def free_reg(j):
        for r in range(L):
            if reg[j][r] is None and not (j == 0 and r in reserved):
                return r
        return None

    def free_scr(c):
        for s_ in range(p.S):
            if (c, s_) not in scr:
                return s_
        return None

    def to_scratch(j, pg, tk, c, r, v, note):
        s_ = free_scr(c)
        if s_ is None:
            return False
        prog.put(j, pg, tk, c, M_OR, rule.K_SCR, r, C0, s_, (note, v))
        scr[(c, s_)] = v
        scr_of[v].add((c, s_))
        return True

    def must_keep(j, v):
        """v may not simply be dropped from front j's registers."""
        return uses[v] > 0 and v not in lane_loc and not scr_of.get(v)

    def evict(j, c, pg, tk, hot, limit):
        best = None
        for r in range(L):
            v = reg[j][r]
            if v is None or v in hot or v in (0, 1) or (j == 0 and r in reserved):
                continue
            nu = next_use(j, v)
            if nu <= limit:
                continue
            keep = must_keep(j, v)
            key = (not keep, nu)
            if best is None or key > best[0]:
                best = (key, r, v)
        if best is None:
            return None, None
        _, r, v = best
        if not must_keep(j, v):
            drop(j, r)
            return 'free', r
        if to_scratch(j, pg, tk, c, r, v, 'spill'):
            drop(j, r)
            return 'slot', None
        return None, None

    def operands_ready(j, g, c):
        _, a, b = mops[g]
        for z in (a, b):
            if z in gates and z not in done:
                return False, 'dep'
        ca, cb = code_at(j, a, c), code_at(j, b, c)
        if ca is None or cb is None:
            return False, 'loc'
        return True, (ca, cb)

    idle = defaultdict(int)
    fidle = [defaultdict(int) for _ in range(F)]
    last_act = [None] * F
    last_page = None
    init_vals = set(init_regs.values())
    rate_hist = [[] for _ in range(F)]
    for pg, tk, vis in comb.ticks(pages):
        if n_pending == 0 and all(reg[0][r] == v for v, r in targets_reg.items()):
            break
        last_page = pg
        if profile is not None and tk == 0:
            row = []
            for j in range(F):
                used = [v for v in reg[j] if v is not None]
                far = sum(1 for v in used if next_use(j, v) - head[j] > lookahead)
                row.append((len(used), sum(1 for v in used if v in init_vals), far))
            profile.append((pg, row))
        for j, c in vis:
            f_or = forder[j]
            while head[j] < len(f_or) and f_or[head[j]] in done:
                head[j] += 1
            # 0. front 0 places the register targets once every gate is done
            if j == 0 and targets_reg and len(done) == len(gates):
                placed = False
                for v, r in targets_reg.items():
                    if reg[0][r] == v:
                        continue
                    occ = reg[0][r]
                    if occ is not None and occ in targets_reg and reg[0][targets_reg[occ]] != occ \
                            and len(regs_of[0][occ]) == 1 and must_keep(0, occ):
                        tmp = next((q for q in range(L) if reg[0][q] is None
                                    and q not in targets_reg.values()), None)
                        if tmp is None:
                            continue
                        prog.put(0, pg, tk, c, M_OR, rule.K_REG, r, C0, tmp, ('place-tmp', occ))
                        put_reg(0, occ, tmp)
                        regs_of[0][occ].discard(r)
                        reg[0][r] = None
                        placed = True
                        break
                    cv = code_at(0, v, c)
                    if cv is None:
                        continue
                    prog.put(0, pg, tk, c, M_OR, rule.K_REG, cv, C0, r, ('place', v))
                    put_reg(0, v, r)
                    placed = True
                    break
                if placed:
                    continue
            # 1. stores owned by this front
            acted = False
            for v in list(pending_hold.get(c, ())):
                if store_owner(v, c) != j:
                    continue
                cv = code_at(j, v, c)
                if cv is not None and (v not in gates or v in done):
                    prog.put(j, pg, tk, c, M_OR, rule.K_HOLD, cv, C0, 0, ('store', v))
                    pending_hold[c].remove(v)
                    n_pending -= 1
                    consume(j, v)
                    if not any(v in pending_hold[x] for x in cells_of[v]):
                        store_due[j].pop(v, None)
                    acted = True
                    break
            if acted:
                continue
            # 2. exports of values other fronts wait for
            if eager_export and export[j]:
                sent = False
                for v in list(export[j]):
                    if uses[v] <= 0 or remote[v] <= 0 or scr_of.get(v):
                        export[j].remove(v)
                        continue
                    rs = regs_of[j].get(v)
                    if not rs:
                        continue
                    if to_scratch(j, pg, tk, c, min(rs), v, 'export'):
                        export[j].remove(v)
                        sent = True
                    break
                if sent:
                    continue
            # 3. issue: head, or another ready gate in the window
            issue = None
            head_dep = False
            n_free = sum(1 for r in range(L) if reg[j][r] is None)
            for q in range(head[j], min(len(f_or), head[j] + ooo)):
                g = f_or[q]
                if g in done:
                    continue
                ok, info = operands_ready(j, g, c)
                if q == head[j]:
                    if ok:
                        issue = (g, info, [])
                        break
                    head_dep = info == 'dep'
                    continue
                if not ok:
                    continue
                _, a, b = mops[g]
                kills = [z for z in {a, b} if z not in (0, 1) and uses[z] == 1 and regs_of[j].get(z)]
                if kills or head_dep or n_free > free_floor:
                    issue = (g, info, kills)
                    break
            if issue is not None:
                g, (ca, cb), kills = issue
                op, a, b = mops[g]
                if not kills:
                    kills = [z for z in {a, b} if z not in (0, 1) and uses[z] == 1 and regs_of[j].get(z)]
                dest = None
                if kills:
                    dest = next((r for r in (min(regs_of[j][z]) for z in kills)
                                 if not (j == 0 and r in reserved)), None)
                if dest is None:
                    dest = free_reg(j)
                if dest is None:
                    hot = set()
                    for q in range(head[j], min(len(f_or), head[j] + 16)):
                        _, x, y = mops[f_or[q]]
                        hot.add(x)
                        hot.add(y)
                    res, r = evict(j, c, pg, tk, hot | {a, b}, fpos[j][g])
                    if res == 'free':
                        dest = r
                    elif res == 'slot':
                        continue
                if dest is not None:
                    ca, cb = code_at(j, a, c), code_at(j, b, c)
                    prog.put(j, pg, tk, c, op, rule.K_REG, ca, cb, dest, ('gate', g))
                    done.add(g)
                    consume(j, a)
                    consume(j, b)
                    put_reg(j, g, dest)
                    if remote[g] > 0:
                        export[j].append(g)
                    continue
            # 4. prefetch a local or imported operand of an upcoming gate
            # (just in time: only if the head is expected to reach the gate
            # before this front's next visit of this cell)
            want = None
            if jit:
                T = pg * comb.PL + tk
                hist = rate_hist[j]
                if not hist or T - hist[-1][0] >= comb.PL // 8:
                    hist.append((T, head[j]))
                    if len(hist) > 9:
                        hist.pop(0)
                t0, h0 = hist[0]
                rate = max(rate_floor, (head[j] - h0) / max(1, T - t0)) if T > t0 else 0.1
                if pg % 2 == 0:
                    revisit = 2 * (comb.hi - 1 + j * comb.delta - c) + 1
                else:
                    revisit = 2 * (c - (comb.lo - comb.H + j * comb.delta)) + 1
                horizon = head[j] + int(jit * rate * revisit) + 1
            else:
                horizon = 10**12
            for q in range(head[j], min(len(f_or), head[j] + lookahead, horizon)):
                g = f_or[q]
                if g in done:
                    continue
                _, a, b = mops[g]
                for z in (a, b):
                    if z in (0, 1) or regs_of[j].get(z):
                        continue
                    if z in gates and z not in done:
                        continue
                    if code_at(j, z, c) is not None:
                        want = (q, z)
                        break
                if want:
                    break
            if want is None:
                # pick up a value this front must store elsewhere
                for s_ in range(p.S):
                    v = scr.get((c, s_))
                    if v is not None and v in store_due[j] and uses[v] > 0 and not regs_of[j].get(v):
                        want = (10**8, v)
                        break
            if want is not None:
                q, z = want
                r = free_reg(j)
                if r is None:
                    res, r = evict(j, c, pg, tk, {z}, q)
                    if res == 'slot':
                        continue
                    if res is None:
                        idle['full'] += 1
                        continue
                prog.put(j, pg, tk, c, M_OR, rule.K_REG, code_at(j, z, c), C0, r, ('load', z))
                put_reg(j, z, r)
                continue
            # classify idleness
            reason = 'drained'
            if head[j] < len(f_or):
                g = f_or[head[j]]
                _, a, b = mops[g]
                if any(z in gates and z not in done for z in (a, b)):
                    reason = 'waits-remote-gate'
                else:
                    for z in (a, b):
                        if code_at(j, z, c) is None:
                            reason = ('waits-lane' if z in lane_loc else
                                      'waits-scratch' if scr_of.get(z) else
                                      'waits-export' if producer.get(z, j) != j else 'lost')
                            break
                    else:
                        reason = 'no-register'
            idle[reason] += 1
            if trace is not None:
                where = None
                if head[j] < len(f_or):
                    _, a, b = mops[f_or[head[j]]]
                    for z in (a, b):
                        if code_at(j, z, c) is None:
                            where = (z, lane_loc[z][0] if z in lane_loc else
                                     sorted(cc for cc, _ in scr_of.get(z, ())) or None)
                            break
                trace.append((pg * comb.PL + tk, j, c, reason, head[j], where))
            fidle[j][reason] += 1
    miss = sum(1 for v, r in targets_reg.items() if reg[0][r] != v)
    for (seq, pg_, tk_, j_, *_rest) in prog.listing:
        last_act[j_] = pg_
    stats = dict(last_page=last_page, idle=dict(idle), instr=prog.count(),
                 front_last=last_act, front_idle=[dict(x) for x in fidle],
                 per_front=[len(o) for o in forder], left=len(gates) - len(done),
                 pending=n_pending, miss=miss)
    if n_pending or miss:
        raise CompileError(f'unfinished: {stats}')
    return stats



def compile_phases(p, layout, F, delta, lookahead=300, ooo=32, owner_mode='interleave',
                   combine='front0', reassoc=True, cut=True, ctrl_fields=CTRL_FIELDS,
                   replicate=False, order_kind='dfs', free_floor=10**9, phases=('early', 'a', 'final'),
                   budgets=(400, 800, 3000), sched=None, check=True, ranges=None, programs=None,
                   win_counterfactual=0, profile=None, order_seed=None, order_flip=0.2, owner_seed=None,
                   jit=0.0, trace=None, hop_order=0, boost_shared=False):
    """Multi-front compile of the three programs of a G candidate with
    generous page budgets: the early Flag program (Hold at the flag cells),
    phase A (upper fetch key into front 0's registers k.. at the match pass)
    and the final program (every Hold output, starting from front 0 holding
    the key and the fetched instruction). Returns per-phase statistics; with
    check=True every phase is replayed against the netlist."""
    from .compiler import Scheduler
    comp = p.fam().cached(p)[1]
    if sched is None:
        sched = Scheduler(p, comp, layout)
    if win_counterfactual:
        # scheduler-only estimate of window reads (the rule would need the
        # extra sources): lanes and scratch of cells c-w..c+w readable at c
        sched.win = win_counterfactual
        nxt = max(sched.src_code.values()) + 1
        for d in [x for x in range(-sched.win, sched.win + 1) if x]:
            for key in [('info@', d)] + [('ln@', i, d) for i in range(10)] + [('scr@', s_, d) for s_ in range(p.S)]:
                sched.src_code[key] = nxt
                nxt += 1
    if order_seed is not None:
        sched.order_rng = np.random.default_rng(order_seed)
        sched.order_flip = order_flip
    owners = bit_owners(sched, F, owner_mode, owner_seed)
    leaf = input_owner(sched, owners, tuple(ctrl_fields))
    k = p.k
    comb = Comb(p, F, delta)
    holds, root_owner = [], {}
    for (f, i), b in sched.bit.items():
        v = comp.outputs[('y', f, i)]
        cell = int(layout[b])
        holds.append((v, cell))
        root_owner[cell] = owners[(f, i)]
    addr_nodes = [comp.outputs[('laddr', i)] for i in range(k)]
    psel_nodes = [comp.outputs[('psel', i)] for i in range(p.PW)]
    key = {}
    for i, v in enumerate(addr_nodes):
        key[v] = i
    for i, v in enumerate(psel_nodes):
        assert v not in key
        key[v] = k + i
    init = {i: v for i, v in enumerate(addr_nodes)}
    for i in range(p.IW):
        node = comp.index.get(('I', i))
        if node is not None:
            init[k + i] = node
    if reassoc:
        reassociate_by_owner(sched, leaf, [v for v, _ in holds] + list(key) + list(init.values()), cut=cut)
    f1_cell, f2_cell = p.fam().flag_store_cells(p)
    early = [(comp.outputs[('y', 'f1', 0)], f1_cell), (comp.outputs[('y', 'f2', 0)], f2_cell)]
    out = {}
    start = 0
    for ph in phases:
        prog = MultiProgram(p, F)
        if ph == 'early':
            targets, treg, ini, pages = early, {}, {}, range(0, budgets[0])
        elif ph == 'a':
            targets, treg, ini = [], key, {}
            pages = range(start, start + budgets[1])
        else:
            targets, treg, ini = holds, {}, init
            pages = range(start, start + budgets[2])
        if ranges is not None:
            pages = ranges[ph]
        ro = dict(root_owner)
        for v, cell in targets:
            ro.setdefault(cell, 0)                # reserved flag cells
        roots = list(targets) + [(v, ('reg', r)) for v, r in treg.items()]
        for v, r in treg.items():
            ro[('reg', r)] = 0
        assign = partition(sched, F, roots, ro, leaf, combine=combine, cut=cut)
        n_clones = replicate_ctrl(sched, assign, roots, leaf, cut=cut) if replicate else 0

        def store_owner(v, cell, assign=assign, ro=ro):
            return assign[v] if v in assign else ro[cell]
        st = run_multi(sched, comb, prog, set(pages), targets, ini, assign, store_owner,
                       lookahead=lookahead, ooo=ooo, targets_reg=treg, order_kind=order_kind,
                       free_floor=free_floor, profile=None if profile is None else profile.setdefault(ph, []),
                       jit=jit, trace=trace, hop_order=hop_order, boost_shared=boost_shared)
        st['passes'] = st['last_page'] - min(pages) + 1
        st['clones'] = n_clones
        if check:
            st['replay_bad'] = replay(p, sched, prog, targets, ini, targets_reg=treg)
        out[ph] = st
        if programs is not None:
            programs[ph] = prog
        # next phase starts after this one; phase A ends one pass before the match pass
        nxt = st['last_page'] + 1
        if ph == 'early':
            nxt += 1                              # courier: flags leave one pass early
        if ph == 'a':
            nxt += 1                              # the match pass
        start = nxt
    out['PL'] = comb.PL
    return out, sched


def compile_program(p, layout, check=True, **kw):
    """The ROM of a comb candidate (p.fronts > 1): the early program in
    pages [0, NPe-1), phase A in [NPe, MP), the final program in (MP, NP).
    Front j's instruction for page pg at a cell is Pi[cell][pg + (j << logNP)]."""
    from .compiler import Program
    ranges = dict(early=range(0, p.NPe - 1), a=range(p.NPe, p.MP), final=range(p.MP + 1, p.NP))
    programs = {}
    out, sched = compile_phases(p, layout, p.fronts, p.delta, ranges=ranges, programs=programs,
                                check=check, **kw)
    for ph, st in out.items():
        if ph != 'PL' and st.get('replay_bad'):
            raise CompileError(f'{ph}: replay mismatch {st["replay_bad"]}')
    prog = Program(p, layout)
    for ph in ('early', 'a', 'final'):
        for (seq, page, tick, j, cell, op, kind, a, b, d, note) in programs[ph].listing:
            prog.put(page + (j << p.logNP), cell, op, kind, a, b, d, note)
    prog.stats = out
    return prog


def replay(p, sched, prog, holds, init, seed=0, targets_reg=None):
    """Execute the listing on random inputs; return the number of Hold
    targets whose final stored value differs from the netlist."""
    comp = sched.comp
    rng = np.random.default_rng(seed)
    vals = {name: rng.integers(0, 2**63, dtype=np.uint64) for name in comp.inputs}
    ref = comp.evaluate(vals)
    node = {0: np.uint64(0), 1: np.uint64(2**64 - 1)}
    for name, idx in comp.index.items():
        node[idx] = vals[name]
    # values of machine-DAG gates needed: evaluate mops on demand
    names = sched.p.fam().source_names(p)
    code_name = {code: nm for code, nm in enumerate(names)}
    at = {}                                          # (cell, source code) -> input node
    for v, (cell, code) in sched.lane_loc.items():
        at[(cell, code)] = v
    F = prog.F
    regs = [[None] * p.L for _ in range(F)]
    scratch, hold = {}, {}
    ops = {M_AND: lambda x, y: x & y, M_OR: lambda x, y: x | y,
           M_XOR: lambda x, y: x ^ y, M_ANDN: lambda x, y: x & ~y}
    init_vals = {r: _eval(sched, v, node) for r, v in init.items()}
    for r, x in init_vals.items():
        regs[0][r] = x
    for (seq, page, tick, j, cell, op, kind, a, b, d, note) in prog.listing:
        def src(code):
            if code < p.L:
                x = regs[j][code]
                assert x is not None, ('empty register', seq, j, code)
                return x
            nm = code_name[code]
            if nm == ('const', 0):
                return np.uint64(0)
            if nm == ('const', 1):
                return np.uint64(2**64 - 1)
            if nm[0] == 'scr':
                return scratch[(cell, nm[1])]
            if nm[0] == 'scr@':
                return scratch[(cell + nm[2], nm[1])]
            v = at.get((cell, code))
            if v is None:
                # window read of a neighbouring cell
                raise KeyError(('lane', cell, nm))
            return node[v]
        x = ops[op](src(a), src(b))
        if kind == rule.K_REG:
            regs[j][d] = x
        elif kind == rule.K_SCR:
            scratch[(cell, d)] = x
        elif kind == rule.K_HOLD:
            hold[cell] = x
    bad = 0
    for v, cell in holds:
        want = _eval(sched, v, node)
        if cell not in hold or hold[cell] != want:
            bad += 1
    for v, r in (targets_reg or {}).items():
        if regs[0][r] is None or regs[0][r] != _eval(sched, v, node):
            bad += 1
    return bad


def _eval(sched, v, node):
    if v in node:
        return node[v]
    stack = [v]
    while stack:
        x = stack[-1]
        if x in node:
            stack.pop()
            continue
        op, a, b = sched.mops[x]
        pend = [z for z in (a, b) if z not in node]
        if pend:
            stack.extend(pend)
            continue
        ya, yb = node[a], node[b]
        node[x] = (ya & yb if op == M_AND else ya | yb if op == M_OR else
                   ya ^ yb if op == M_XOR else ya & ~yb)
        stack.pop()
    return node[v]
