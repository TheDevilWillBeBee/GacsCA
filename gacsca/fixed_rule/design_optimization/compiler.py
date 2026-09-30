"""Compile the rule's own netlist into the front program (the ROM table Pi).

The program computes, inside one colony, the rule's transition of the upper
cell encoded by that colony. It is a list of instructions indexed by
(physical Address, page). The front visits cell c during pass p at exactly
one slot; there it may read its registers and the lanes of cell c:

  * Info at cell layout[b] is the upper cell's own bit b (lane offset 0);
  * ln[idx] at cell layout[b] is bit b of the upper neighbour at offset
    LANE_OFFSETS[idx] (filled by the gather);
  * Hold at layout[b] receives new upper bit b; scratch bits are local spill
    memory.

Passes 0..MP-1 compute the upper fetch key: R[0:k] = upper stored Address and
R[k:k+logNP] = upper psel. Pass MP is the physical match pass, after which
R[k:k+IW] holds the upper instruction I. Passes MP+1..NP-1 compute every
upper output and store it into Hold.

`simulate_program` replays the machine abstractly and checks that the
compiled program computes the netlist; the physical proof is running the
actual rule on encoded colonies.
"""
from collections import defaultdict
import heapq
import numpy as np
from . import rule
from .netlist import AND as G_AND, OR as G_OR, XOR as G_XOR

M_AND, M_OR, M_XOR, M_ANDN = rule.AND, rule.OR, rule.XOR, rule.ANDN


class CompileError(RuntimeError):
    pass


def work_range(p):
    fn = getattr(p.fam(), 'work_range', None)
    return fn(p) if fn else (0, p.Q)


def slots(p):
    """Execution order of front slots as (ROM column, cell).

    Pass `pg` visits the cells boustrophedon; the front dwells D slots at
    each cell and the ROM column is t + D*pg for dwell index t. With a
    colony margin, no instruction is placed at margin cells (the front
    crosses them without executing or storing anything), except at the two
    reserved special-procedure cells during the early Flag program, which
    writes the new upper Flag1/Flag2 there (Gray p. 35: these SimBits sit
    near the colony ends and are not part of the represented state)."""
    D = getattr(p, 'D', 1)
    lo, hi = work_range(p)
    if getattr(p, 'confined', False):
        # the front itself sweeps only [lo, hi)
        for pg in range(p.NP):
            cells = range(lo, hi) if pg % 2 == 0 else range(hi - 1, lo - 1, -1)
            for c in cells:
                for t in range(D):
                    yield pg * D + t, c
        return
    special = set(getattr(p.fam(), 'reserved_cells', lambda p: ())(p)) if lo > 0 else set()
    NPe = getattr(p, 'NPe', 0)
    for pg in range(p.NP):
        cells = range(p.Q) if pg % 2 == 0 else range(p.Q - 1, -1, -1)
        for c in cells:
            if not lo <= c < hi and not (c in special and pg < NPe):
                continue
            for t in range(D):
                yield pg * D + t, c


def columns(p, passes):
    D = getattr(p, 'D', 1)
    return {pg * D + t for pg in passes for t in range(D)}


class Program:
    def __init__(self, p, layout):
        self.p = p
        self.layout = np.asarray(layout)
        self.rom = np.zeros((p.Q, p.NPT), dtype=np.uint32)
        self.used = np.zeros((p.Q, p.NPT), dtype=bool)
        self.listing = []

    def put(self, page, cell, op, kind, a, b, d, note=None):
        assert not self.used[cell, page]
        self.used[cell, page] = True
        self.rom[cell, page] = rule.encode_instruction(self.p, op, kind, a, b, d)
        self.listing.append((page, cell, op, kind, a, b, d, note))


def default_layout(p, spread=True, interleave=False):
    """Cells holding upper bits in schema order; reserved cells are skipped.

    With interleave=True the five stored copies of each logical bit of a
    fivefold field sit on adjacent cells (order: field, logical bit, slot)."""
    W = p.fam().width(p)
    reserved = set(getattr(p.fam(), 'reserved_cells', lambda p: ())(p))
    lo, hi = work_range(p)
    cells = [c for c in range(lo, hi) if c not in reserved]
    if W > len(cells):
        raise CompileError(f'upper state ({W} bits) does not fit in the colony')
    order = list(range(W))
    if interleave:
        five = set(getattr(p.fam(), 'fivefold_fields', lambda p: ())(p))
        keys = []
        b = 0
        for fi, (f, w) in enumerate(p.fam().schema(p)):
            lw = w // 5 if f in five else w
            for j in range(w):
                keys.append((fi, j % lw, j // lw) if f in five else (fi, j, 0))
        order = sorted(range(W), key=lambda b: keys[b])
    slot = [0] * W
    for rank, b in enumerate(order):
        slot[b] = rank
    if not spread:
        return np.array([cells[slot[b]] for b in range(W)])
    return np.array([cells[(slot[b] * len(cells)) // W] for b in range(W)])


def proportional_layout(p, layout):
    """Spread every field evenly over the cells of `layout`: upper bits are
    ordered by their relative position (i + 0.5) / width within their field
    (ties by schema order), so every stretch of the colony holds a sample of
    every field. Data a computation needs is then within reach throughout
    each pass instead of in one region."""
    sch = p.fam().schema(p)
    keys = []
    for fi, (f, w) in enumerate(sch):
        for i in range(w):
            keys.append(((i + 0.5) / w, fi, i))
    order = sorted(range(len(keys)), key=lambda x: keys[x])
    cells = sorted(int(x) for x in layout)
    out = [None] * len(keys)
    for rank, bit in enumerate(order):
        out[bit] = cells[rank]
    return np.array(out)


def lane_locations(p, comp, layout):
    """(cell, source code) of every upper input bit after the gather.

    Info at layout[b] is the upper cell's own bit b; lane j at cell x holds
    neighbour j's bit at address x - skew_j."""
    bit = {}
    b = 0
    for f, w in p.fam().schema(p):
        for i in range(w):
            bit[(f, i)] = b
            b += 1
    src = {name: code for code, name in enumerate(p.fam().source_names(p))}
    loc = {}
    for name, node in comp.index.items():
        if name[0] != 'x':
            continue
        _, j, f, i = name
        cell = int(layout[bit[(f, i)]])
        if j == 0:
            loc[node] = (cell, src[('info', 0)])
        else:
            idx = p.fam().LANE_OFFSETS.index(j)
            loc[node] = (cell + p.skew[idx], src[('ln', idx)])
    return loc


def read_load(p, comp, layout):
    """Number of used upper input bits located at each cell."""
    live = set()
    for op, a, b in comp.gates:
        live.add(a)
        live.add(b)
    live |= set(comp.outputs.values())
    loc = lane_locations(p, comp, layout)
    counts = np.zeros(p.Q + 128, dtype=int)
    bad = 0
    for node, (cell, _) in loc.items():
        if node in live:
            if cell >= p.Q:
                bad += 1
            else:
                counts[cell] += 1
    return counts[:p.Q], bad


def choose_skew(p, layout, seed=0, iters=4000):
    """Randomized search for per-lane skews that balance lane reads per cell."""
    from dataclasses import replace
    rng = np.random.default_rng(seed)
    net, comp = p.fam().cached(replace(p, skew=(0,) * 10))
    used = defaultdict(list)          # lane index -> used bit cells
    own = np.zeros(p.Q, dtype=int)
    live = set()
    for op, a, b in comp.gates:
        live.add(a)
        live.add(b)
    bit = {}
    b = 0
    for f, w in p.fam().schema(p):
        for i in range(w):
            bit[(f, i)] = b
            b += 1
    for name, node in comp.index.items():
        if name[0] != 'x' or node not in live:
            continue
        _, j, f, i = name
        cell = int(layout[bit[(f, i)]])
        if j == 0:
            own[cell] += 1
        else:
            used[p.fam().LANE_OFFSETS.index(j)].append(cell)
    maxd = {l: work_range(p)[1] - 1 - max(cells) for l, cells in used.items()}

    def cost(sk):
        load = own.copy()
        for l, cells in used.items():
            for c in cells:
                load[c + sk[l]] += 1
        return (int(load.max()), int((load ** 2).sum())), load

    best = [0] * 10
    best_cost, _ = cost(best)
    for it in range(iters):
        cand = list(best)
        l = int(rng.integers(0, 10))
        if l in maxd:
            cand[l] = int(rng.integers(0, maxd[l] + 1))
        c, _ = cost(cand)
        if c <= best_cost:
            best, best_cost = cand, c
    for l in range(10):
        if l not in maxd:
            best[l] = 0
    return tuple(best), best_cost


def machine_dag(p, comp):
    """Machine-level DAG: fuse AND(x, NOT y) into ANDN, keep NOT as XOR 1."""
    n_in = 2 + len(comp.inputs)
    gates = comp.gates
    op_of = {}
    for g, (op, a, b) in enumerate(gates):
        op_of[n_in + g] = (op, a, b)

    def is_not(x):
        g = op_of.get(x)
        if g and g[0] == G_XOR and g[1] == 1:
            return g[2]
        return None

    mops = {}
    for node, (op, a, b) in op_of.items():
        if op == G_AND:
            na, nb = is_not(a), is_not(b)
            if nb is not None and na is None:
                mops[node] = (M_ANDN, a, nb)
                continue
            if na is not None and nb is None:
                mops[node] = (M_ANDN, b, na)
                continue
            mops[node] = (M_AND, a, b)
        elif op == G_OR:
            mops[node] = (M_OR, a, b)
        else:
            mops[node] = (M_XOR, a, b)
    return mops


class Scheduler:
    """Slot-by-slot list scheduler for the front machine.

    Gates are taken in a depth-first post-order T of the target cones (short
    live ranges). Only the first `window` ready gates of T are active. At each
    visit the front executes one instruction, chosen in this order:
    a designated register load, a Hold store due at this cell, the earliest
    active gate whose operands are at hand (registers, constants, or a
    lane/scratch bit of this cell), or a just-in-time load of a local operand
    that an active gate needs. Computed values are spilled to local scratch
    (furthest next use first) when registers run out; input copies are simply
    dropped because they can be reloaded. The scheduler never changes the
    netlist function; `verify_program` replays the result.
    """

    def __init__(self, p, comp, layout, window=24, reserve=4, verbose=False):
        self.p, self.comp = p, comp
        self.layout = np.asarray(layout)
        self.sch = p.fam().schema(p)
        self.bit = {}
        b = 0
        for f, w in self.sch:
            for i in range(w):
                self.bit[(f, i)] = b
                b += 1
        self.src_code = {name: code for code, name in enumerate(p.fam().source_names(p))}
        self.C0 = self.src_code[('const', 0)]
        self.C1 = self.src_code[('const', 1)]
        self.mops = machine_dag(p, comp)
        self.window = window
        self.reserve = reserve
        self.verbose = verbose
        self.lane_loc = lane_locations(p, comp, self.layout)
        # window reads: the kind of each input and the codes per cell offset
        self.win = getattr(p, 'win', 0)
        names = self.src_code
        self.lane_kind = {}
        for node, (cell, code) in self.lane_loc.items():
            self.lane_kind[node] = ('info',) if code == names[('info', 0)] else (
                'ln', next(i for i in range(len(rule.LANE_OFFSETS)) if names[('ln', i)] == code))

    def lane_code(self, v, c):
        """Source code reading input v while the front is at cell c, or None."""
        cell, code = self.lane_loc[v]
        d = cell - c
        if d == 0:
            return code
        if self.win and abs(d) <= self.win:
            kind = self.lane_kind[v]
            key = ('info@', d) if kind[0] == 'info' else ('ln@', kind[1], d)
            return self.src_code[key]
        return None

    def scr_code(self, s, cell, c):
        d = cell - c
        if d == 0:
            return self.src_code[('scr', s)]
        if self.win and abs(d) <= self.win:
            return self.src_code[('scr@', s, d)]
        return None

    def topo_sorted(self, nodes, reverse=False):
        """Nodes in topological order. Node ids are topological unless the
        machine DAG was rewritten (reassociate), which sets self.rank."""
        rank = getattr(self, 'rank', None)
        return sorted(nodes, key=rank.get if rank else None, reverse=reverse)

    def reassociate(self, protect):
        """Rebuild every maximal AND/OR/XOR tree whose inner nodes have one
        use into a chain, operands ordered by where their data first becomes
        available in a forward sweep (lane cell of an input; for a computed
        value, the latest input cell in its cone). The function computed is
        unchanged; a front sweeping forward can then fold the operands in as
        it passes them instead of waiting for whole subtrees."""
        mops = dict(self.mops)
        fan = defaultdict(int)
        for x, (op, a, b) in mops.items():
            fan[a] += 1
            fan[b] += 1
        pos = {}
        for x in sorted(mops):                       # original ids are topological
            _, a, b = mops[x]
            pos[x] = max(pos.get(a, self.lane_loc[a][0] if a in self.lane_loc else -1),
                         pos.get(b, self.lane_loc[b][0] if b in self.lane_loc else -1))

        def key(v):
            if v in pos:
                return pos[v]
            return self.lane_loc[v][0] if v in self.lane_loc else -1
        protect = set(protect)
        assoc = (M_AND, M_OR, M_XOR)
        next_id = max(mops) + 1
        n_trees = n_nodes = 0
        for x in sorted(mops, reverse=True):
            if x not in mops:
                continue
            op, a, b = mops[x]
            if op not in assoc:
                continue
            leaves, internal, stack = [], [], [a, b]
            while stack:
                z = stack.pop()
                if (z in mops and z not in protect and fan[z] == 1 and mops[z][0] == op):
                    internal.append(z)
                    stack += [mops[z][1], mops[z][2]]
                else:
                    leaves.append(z)
            if len(leaves) < 3:
                continue
            leaves.sort(key=lambda z: (key(z), z))
            prev = leaves[0]
            for z in leaves[1:-1]:
                mops[next_id] = (op, prev, z)
                prev = next_id
                next_id += 1
            mops[x] = (op, prev, leaves[-1])
            for z in internal:
                del mops[z]
            n_trees += 1
            n_nodes += len(internal)
        # explicit topological rank for the rewritten DAG
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
        self.mops, self.rank = mops, rank
        self.reassoc_stats = dict(trees=n_trees, rewritten_nodes=n_nodes)
        return self.reassoc_stats

    def cone(self, roots):
        seen = set()
        stack = list(roots)
        while stack:
            x = stack.pop()
            if x in seen or x not in self.mops:
                continue
            seen.add(x)
            _, a, b = self.mops[x]
            stack.append(a)
            stack.append(b)
        return seen

    def dfs_order(self, roots, gates):
        rng = getattr(self, 'order_rng', None)
        if rng is not None:
            roots = list(roots)
            # shuffle roots in field blocks, keeping bits of a field together
            blocks, cur = [], []
            for r in roots:
                cur.append(r)
                if len(cur) >= int(rng.integers(1, 12)):
                    blocks.append(cur)
                    cur = []
            if cur:
                blocks.append(cur)
            order_idx = rng.permutation(len(blocks))
            roots = [r for i in order_idx for r in blocks[i]]
        size = {}
        for g in self.topo_sorted(gates):
            _, a, b = self.mops[g]
            size[g] = 1 + size.get(a, 0) + size.get(b, 0)
        order, seen = [], set()
        for r in roots:
            stack = [(r, False)]
            while stack:
                y, post = stack.pop()
                if y not in gates or y in seen:
                    continue
                if post:
                    seen.add(y)
                    order.append(y)
                    continue
                stack.append((y, True))
                _, a, b = self.mops[y]
                kids = sorted({a, b}, key=lambda z: -size.get(z, 0))
                if rng is not None and len(kids) == 2 and rng.random() < self.order_flip:
                    kids.reverse()
                for z in reversed(kids):
                    if z in gates and z not in seen:
                        stack.append((z, False))
        return order

    def run(self, program, pages, targets_reg, targets_hold, init_regs, root_order=None):
        p, L = self.p, self.p.L
        roots = list(targets_reg) + [v for v, _ in targets_hold]
        if root_order is not None:
            roots = root_order(roots)
        gates = self.cone(roots)
        order = self.dfs_order(roots, gates)
        pos = {g: i for i, g in enumerate(order)}
        consumers = defaultdict(list)
        uses = defaultdict(int)
        for g in gates:
            _, a, b = self.mops[g]
            consumers[a].append(g)
            consumers[b].append(g)
            uses[a] += 1
            uses[b] += 1
        for v in targets_reg:
            uses[v] += 1
        for v, _ in targets_hold:
            uses[v] += 1
        height = defaultdict(int)
        for g in self.topo_sorted(gates, reverse=True):
            height[g] = 1 + max((height[w] for w in consumers.get(g, ())), default=0)
        reg = [None] * L
        regs_of = defaultdict(set)
        for r, v in init_regs.items():
            reg[r] = v
            regs_of[v].add(r)
        scr, scr_of = {}, defaultdict(set)
        done = set()
        missing = {}
        for g in gates:
            _, a, b = self.mops[g]
            missing[g] = len({z for z in (a, b) if z in gates})
        ready = [pos[g] for g in gates if missing[g] == 0]
        heapq.heapify(ready)
        pending_hold = defaultdict(list)
        for v, cell in targets_hold:
            pending_hold[cell].append(v)
        n_pending = len(targets_hold)
        reserved = set(targets_reg.values())
        input_targets = defaultdict(list)
        for v, r in targets_reg.items():
            if v in self.lane_loc:
                input_targets[self.lane_loc[v][0]].append((v, r))
        C0, C1 = self.C0, self.C1
        src_scr = [self.src_code[('scr', s)] for s in range(p.S)]

        def code_at(v, c):
            if v == 0: return C0
            if v == 1: return C1
            rs = regs_of.get(v)
            if rs: return min(rs)
            loc = self.lane_loc.get(v)
            if loc is not None:
                code = self.lane_code(v, c)
                if code is not None: return code
            for (cc, s) in scr_of.get(v, ()):
                code = self.scr_code(s, cc, c)
                if code is not None: return code
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
            uses[v] -= 1
            release(v)

        def free_register():
            for r in range(L):
                if reg[r] is None and r not in reserved:
                    return r
            return None

        def put_reg(v, r):
            old = reg[r]
            if old is not None:
                regs_of[old].discard(r)
            reg[r] = v
            regs_of[v].add(r)

        def finish(g):
            done.add(g)
            for w in consumers.get(g, ()):
                missing[w] -= 1
                if missing[w] == 0:
                    heapq.heappush(ready, pos[w])

        def next_use(v):
            return min((pos[w] for w in consumers.get(v, ()) if w not in done), default=10**9)

        def make_room(c, hot=()):
            """Free a register without using the slot if possible.

            Returns 'free' if a register is now free, 'slot' if the slot was
            used to spill, or None. Values used by the active window (`hot`)
            are never evicted."""
            cands = []
            for r in range(L):
                v = reg[r]
                if v is None or r in reserved or v in (0, 1) or v in hot:
                    continue
                cands.append((next_use(v), r, v))
            cands.sort(reverse=True)
            for nu, r, v in cands:
                if v in self.lane_loc or len(regs_of[v]) > 1 or scr_of.get(v):
                    regs_of[v].discard(r)
                    reg[r] = None
                    return 'free'
            for nu, r, v in cands:
                free_s = [s for s in range(p.S) if (c, s) not in scr]
                if not free_s:
                    return None
                s = free_s[0]
                program.put(page, c, M_OR, rule.K_SCR, r, C0, s, ('spill', v))
                scr[(c, s)] = v
                scr_of[v].add((c, s))
                regs_of[v].discard(r)
                reg[r] = None
                return 'slot'
            return None

        def targets_met():
            return n_pending == 0 and all(reg[r] == v for v, r in targets_reg.items())

        idle = 0
        page = None
        head = 0
        for page, c in slots(p):
            if page not in pages:
                continue
            if targets_met():
                break
            acted = False
            for item in list(input_targets.get(c, ())):
                v, r = item
                if reg[r] == v:
                    input_targets[c].remove(item)
                elif reg[r] is None:
                    program.put(page, c, M_OR, rule.K_REG, self.lane_loc[v][1], C0, r, ('load-target', v))
                    put_reg(v, r)
                    input_targets[c].remove(item)
                    acted = True
                    break
            if acted:
                continue
            for v in list(pending_hold.get(c, ())):
                cv = code_at(v, c)
                if cv is not None:
                    program.put(page, c, M_OR, rule.K_HOLD, cv, C0, 0, ('store', v))
                    pending_hold[c].remove(v)
                    n_pending -= 1
                    consume(v)
                    acted = True
                    break
                if v in gates and v not in done and missing[v] == 0 and uses[v] == 1:
                    op, a, b = self.mops[v]
                    ca, cb = code_at(a, c), code_at(b, c)
                    if ca is not None and cb is not None:
                        program.put(page, c, op, rule.K_HOLD, ca, cb, 0, ('gate->hold', v))
                        pending_hold[c].remove(v)
                        n_pending -= 1
                        uses[v] -= 1
                        finish(v)
                        consume(a)
                        consume(b)
                        acted = True
                        break
            if acted:
                continue
            # active window: the next `window` unfinished gates of T
            while head < len(order) and order[head] in done:
                head += 1
            active = []
            q = head
            while q < len(order) and len(active) < self.window:
                if order[q] not in done:
                    active.append(order[q])
                q += 1
            action = None
            active_set = set(active)
            for attempt in range(3):
                n_free = sum(1 for r in range(L) if reg[r] is None and r not in reserved)
                # load-once: a local bit with several pending consumers
                bestm = None
                if n_free > 0:
                    counts = defaultdict(int)
                    hmax = defaultdict(int)
                    for g in active:
                        _, a, b = self.mops[g]
                        for z in {a, b}:
                            if z in (0, 1) or regs_of.get(z) or code_at(z, c) is None:
                                continue
                            counts[z] += 1
                            hmax[z] = max(hmax[z], height[g])
                    for z, cnt in counts.items():
                        total = sum(1 for w in consumers.get(z, ()) if w not in done)
                        if total >= 2:
                            key = (hmax[z], cnt)
                            if bestm is None or key > bestm[0]:
                                bestm = (key, z)
                if bestm is not None:
                    action = ('load', bestm[1])
                    break
                best = None
                for g in active:
                    if missing[g]:
                        continue
                    op, a, b = self.mops[g]
                    if code_at(a, c) is None or code_at(b, c) is None:
                        continue
                    kl = sum(1 for z in {a, b} if z not in (0, 1) and uses[z] == 1 and regs_of.get(z))
                    if n_free == 0 and kl == 0:
                        continue
                    local = any(not (z in (0, 1) or regs_of.get(z)) for z in (a, b))
                    key = (local, height[g], -pos[g])
                    if best is None or key > best[0]:
                        best = (key, g, op, a, b)
                if best is not None:
                    action = ('gate',) + best[1:]
                    break
                bestz = None
                if n_free > self.reserve:
                    for g in active:
                        _, a, b = self.mops[g]
                        ready_now = missing[g] == 0
                        for z, other in ((a, b), (b, a)):
                            if z in (0, 1) or regs_of.get(z) or code_at(z, c) is None:
                                continue
                            if (not ready_now) or code_at(other, c) is None:
                                key = (height[g], -pos[g])
                                if bestz is None or key > bestz[0]:
                                    bestz = (key, z)
                if bestz is not None:
                    action = ('load', bestz[1])
                    break
                if n_free > self.reserve:
                    break
                hot = set()
                for g in active[:max(4, self.window // 4)]:
                    _, a, b = self.mops[g]
                    hot.add(a)
                    hot.add(b)
                res = make_room(c, hot)
                if res == 'slot':
                    action = ('used',)
                    break
                if res is None:
                    break
            if action is None:
                idle += 1
                continue
            if action[0] == 'used':
                continue
            if action[0] == 'gate':
                _, g, op, a, b = action
                dest = None
                if g in targets_reg and reg[targets_reg[g]] is None:
                    dest = targets_reg[g]
                if dest is None:
                    for z in (a, b):
                        if z not in (0, 1) and uses[z] == 1 and regs_of.get(z):
                            r = min(regs_of[z])
                            if r not in reserved:
                                dest = r
                                break
                if dest is None:
                    dest = free_register()
                if dest is None:
                    res = make_room(c, {a, b})
                    if res == 'free':
                        dest = free_register()
                    else:
                        if res is None:
                            idle += 1
                        continue
                ca, cb = code_at(a, c), code_at(b, c)
                program.put(page, c, op, rule.K_REG, ca, cb, dest, ('gate', g))
                finish(g)
                consume(a)
                consume(b)
                put_reg(g, dest)
            else:
                z = action[1]
                r = free_register()
                if r is None:
                    res = make_room(c, {z})
                    if res == 'free':
                        r = free_register()
                    else:
                        if res is None:
                            idle += 1
                        continue
                program.put(page, c, M_OR, rule.K_REG, code_at(z, c), C0, r, ('load', z))
                put_reg(z, r)
        self.last_idle = idle
        self.last_page = page
        self._dbg = dict(ready=ready, done=done, reg=reg, uses=uses, gates=gates, order=order,
                         scr=scr, regs_of=regs_of, pending_hold=pending_hold)
        miss = [v for v, r in targets_reg.items() if reg[r] != v]
        if n_pending or miss:
            raise CompileError(f'unfinished: {n_pending} stores, {len(miss)} register targets, '
                               f'{len(gates) - len(done)} gates left')
        return reg


def stream_order(self, roots, gates):
    """Topological order sorted by the latest input cell in each gate's cone.

    Following a rightward sweep, a gate is placed as soon as every input it
    depends on has been passed; ties keep the depth-first order."""
    dfs = self.dfs_order(roots, gates)
    rank = {g: i for i, g in enumerate(dfs)}
    h = {}
    for g in self.topo_sorted(gates):
        _, a, b = self.mops[g]
        vals = []
        for z in (a, b):
            if z in gates:
                vals.append(h[z])
            elif z in self.lane_loc:
                vals.append(self.lane_loc[z][0])
            else:
                vals.append(-1)
        h[g] = max(vals)
    return sorted(gates, key=lambda g: (h[g], rank[g]))


Scheduler.stream_order = stream_order


def interleaved_order(self, roots, gates, K):
    """Round-robin merge of K depth-first streams over contiguous root groups.

    A gate shared by several streams belongs to the first stream whose DFS
    reaches it; later streams simply wait for it. Consecutive positions then
    mostly hold independent gates, which the in-order issue window can use
    while one stream waits for the front."""
    roots = list(roots)
    size = max(1, (len(roots) + K - 1) // K)
    groups = [roots[i:i + size] for i in range(0, len(roots), size)]
    seen = set()
    streams = []
    for grp in groups:
        cone = self.cone(grp) - seen
        order = [g for g in self.dfs_order(grp, self.cone(grp)) if g in cone]
        seen |= set(order)
        streams.append(order)
    merged = []
    idx = [0] * len(streams)
    while any(idx[i] < len(streams[i]) for i in range(len(streams))):
        for i, st in enumerate(streams):
            if idx[i] < len(st):
                merged.append(st[idx[i]])
                idx[i] += 1
    # the merge must remain topological: repair by a stable topological sort
    pos = {g: i for i, g in enumerate(merged)}
    indeg = {g: 0 for g in merged}
    succ = defaultdict(list)
    for g in merged:
        _, a, b = self.mops[g]
        for z in {a, b}:
            if z in pos:
                indeg[g] += 1
                succ[z].append(g)
    ready = [pos[g] for g in merged if indeg[g] == 0]
    heapq.heapify(ready)
    out = []
    while ready:
        g = merged[heapq.heappop(ready)]
        out.append(g)
        for w in succ[g]:
            indeg[w] -= 1
            if indeg[w] == 0:
                heapq.heappush(ready, pos[w])
    assert len(out) == len(merged)
    return out


Scheduler.interleaved_order = interleaved_order


def run_inorder(self, program, pages, targets_hold, init_regs, lookahead=160, ooo=8,
                order_kind='dfs', free_floor=10**9, targets_reg=None, late_targets=False):
    """In-order issue of the DFS order T with lane prefetch.

    Gates issue strictly in T order except that a gate among the next `ooo`
    that frees a register may issue early. Lane/scratch operands of the next
    `lookahead` gates are loaded when the front passes their cell. Registers
    are replaced by furthest next use (Belady); input copies are dropped,
    computed values spilled to a free scratch bit of the visited cell.
    """
    p, L = self.p, self.p.L
    targets_reg = dict(targets_reg or {})
    reserved = set() if late_targets else set(targets_reg.values())
    roots = list(targets_reg) + [v for v, _ in targets_hold]
    gates = self.cone(roots)
    if order_kind == 'stream':
        order = self.stream_order(roots, gates)
    elif isinstance(order_kind, tuple) and order_kind[0] == 'interleave':
        order = self.interleaved_order(roots, gates, order_kind[1])
    else:
        order = self.dfs_order(roots, gates)
    pos = {g: i for i, g in enumerate(order)}
    consumers = defaultdict(list)
    uses = defaultdict(int)
    for g in order:
        _, a, b = self.mops[g]
        consumers[a].append(pos[g])
        consumers[b].append(pos[g])
        uses[a] += 1
        uses[b] += 1
    for v, _ in targets_hold:
        uses[v] += 1
    for v in targets_reg:
        uses[v] += 1
    store_pos = defaultdict(lambda: 10**9)
    for v, _ in targets_hold:
        store_pos[v] = min(store_pos[v], pos.get(v, -1) + 1)
    reg = [None] * L
    regs_of = defaultdict(set)
    for r, v in init_regs.items():
        reg[r] = v
        regs_of[v].add(r)
    scr, scr_of = {}, defaultdict(set)
    done = set()
    pending_hold = defaultdict(list)
    for v, cell in targets_hold:
        pending_hold[cell].append(v)
    n_pending = len(targets_hold)
    C0, C1 = self.C0, self.C1
    src_scr = [self.src_code[('scr', s_)] for s_ in range(p.S)]
    lane_loc = self.lane_loc
    head = 0
    cons_ptr = defaultdict(int)

    def code_at(v, c):
        if v == 0: return C0
        if v == 1: return C1
        rs = regs_of.get(v)
        if rs: return min(rs)
        loc = lane_loc.get(v)
        if loc is not None:
            code = self.lane_code(v, c)
            if code is not None: return code
        for (cc, s_) in scr_of.get(v, ()):
            code = self.scr_code(s_, cc, c)
            if code is not None: return code
        return None

    def next_use(v):
        lst = consumers.get(v, ())
        i = cons_ptr[v]
        while i < len(lst) and order[lst[i]] in done:
            i += 1
        cons_ptr[v] = i
        nu = lst[i] if i < len(lst) else 10**9
        if v in store_pos and any(v in pending_hold[cc] for cc in ()):
            pass
        return nu

    def release(v):
        if uses[v] > 0: return
        for r in list(regs_of.get(v, ())):
            reg[r] = None
        regs_of.pop(v, None)
        for key in list(scr_of.get(v, ())):
            scr.pop(key, None)
        scr_of.pop(v, None)

    def consume(v):
        uses[v] -= 1
        release(v)

    def put_reg(v, r):
        old = reg[r]
        if old is not None:
            regs_of[old].discard(r)
        reg[r] = v
        regs_of[v].add(r)

    def free_reg():
        for r in range(L):
            if reg[r] is None and r not in reserved:
                return r
        return None

    def targets_met():
        return all(reg[r] == v for v, r in targets_reg.items())

    def evict(c, page, hot, limit):
        """Free a register holding a value whose next use is beyond `limit`.
        Returns ('free', r) without using the slot, ('slot', None) when the
        slot was used for a spill, or (None, None)."""
        best = None
        for r in range(L):
            v = reg[r]
            if v is None or v in hot or v in (0, 1) or r in reserved:
                continue
            nu = next_use(v)
            if v in stored_later:
                nu = min(nu, stored_later[v])
            if nu <= limit:
                continue
            key = (v in lane_loc or len(regs_of[v]) > 1 or bool(scr_of.get(v)), nu)
            if best is None or key > best[0]:
                best = (key, r, v)
        if best is None:
            return None, None
        _, r, v = best
        if v in lane_loc or len(regs_of[v]) > 1 or scr_of.get(v):
            regs_of[v].discard(r)
            reg[r] = None
            return 'free', r
        free_s = [s_ for s_ in range(p.S) if (c, s_) not in scr]
        if not free_s:
            return None, None
        s_ = free_s[0]
        program.put(page, c, M_OR, rule.K_SCR, r, C0, s_, ('spill', v))
        scr[(c, s_)] = v
        scr_of[v].add((c, s_))
        regs_of[v].discard(r)
        reg[r] = None
        return 'slot', None

    # outputs that are pending stores keep a (late) use
    stored_later = {}
    for v, _ in targets_hold:
        stored_later[v] = pos.get(v, 0) + lookahead
    idle = 0
    idle_reasons = {}
    page = None
    for page, c in slots(p):
        if page not in pages:
            continue
        if n_pending == 0 and targets_met():
            break
        # 0a. late placement of register targets once every gate is done
        if late_targets and targets_reg and all(g in done for g in gates):
            placed = False
            for v, r in targets_reg.items():
                if reg[r] == v:
                    continue
                occupant = reg[r]
                if occupant is not None and occupant in targets_reg and reg[targets_reg[occupant]] != occupant:
                    # move the occupant (another target) to a scratch register first
                    tmp = next((q for q in range(L) if reg[q] is None and q not in targets_reg.values()), None)
                    if tmp is None:
                        continue
                    program.put(page, c, M_OR, rule.K_REG, r, C0, tmp, ('place-tmp', occupant))
                    put_reg(occupant, tmp)
                    regs_of[occupant].discard(r)
                    reg[r] = None
                    placed = True
                    break
                if occupant is not None and occupant not in targets_reg:
                    regs_of[occupant].discard(r)
                    reg[r] = None
                cv = code_at(v, c)
                if cv is None:
                    continue
                program.put(page, c, M_OR, rule.K_REG, cv, C0, r, ('place', v))
                put_reg(v, r)
                placed = True
                break
            if placed:
                continue
        # 0. inputs that must sit in a designated register
        acted = False
        for v, r in targets_reg.items():
            if v in lane_loc and reg[r] != v and reg[r] is None:
                cv = code_at(v, c)
                if cv is not None and cv < L:
                    continue
                if cv is not None:
                    program.put(page, c, M_OR, rule.K_REG, cv, C0, r, ('load-target', v))
                    put_reg(v, r)
                    acted = True
                    break
        if acted:
            continue
        while head < len(order) and order[head] in done:
            head += 1
        acted = False
        # 1. stores
        for v in list(pending_hold.get(c, ())):
            cv = code_at(v, c)
            if cv is not None:
                program.put(page, c, M_OR, rule.K_HOLD, cv, C0, 0, ('store', v))
                pending_hold[c].remove(v)
                n_pending -= 1
                consume(v)
                stored_later.pop(v, None) if uses[v] == 0 else None
                acted = True
                break
            if v in gates and v not in done and uses[v] == 1:
                op, a, b = self.mops[v]
                if all(z in done or z not in gates for z in (a, b)):
                    ca, cb = code_at(a, c), code_at(b, c)
                    if ca is not None and cb is not None:
                        program.put(page, c, op, rule.K_HOLD, ca, cb, 0, ('gate->hold', v))
                        pending_hold[c].remove(v)
                        n_pending -= 1
                        uses[v] -= 1
                        done.add(v)
                        consume(a)
                        consume(b)
                        acted = True
                        break
        if acted:
            continue
        # 2. issue: head, or an early register-freeing gate
        issue = None
        for q in range(head, min(len(order), head + ooo)):
            g = order[q]
            if g in done:
                continue
            op, a, b = self.mops[g]
            if not all(z in done or z not in gates for z in (a, b)):
                if q == head:
                    break
                continue
            ca, cb = code_at(a, c), code_at(b, c)
            if ca is None or cb is None:
                continue
            kills = [z for z in {a, b} if z not in (0, 1) and uses[z] == 1 and regs_of.get(z)]
            n_free = sum(1 for r in range(L) if reg[r] is None)
            if q == head or kills or n_free > free_floor:
                issue = (g, op, a, b, kills)
                break
        if issue is not None:
            g, op, a, b, kills = issue
            if g in targets_reg and reg[targets_reg[g]] is None:
                dest = targets_reg[g]
            else:
                dest = next((r for r in (min(regs_of[z]) for z in kills) if r not in reserved), None) \
                    if kills else free_reg()
                if dest is None and not kills:
                    dest = free_reg()
            if dest is None:
                hot = set()
                for q in range(head, min(len(order), head + 16)):
                    _, x, y = self.mops[order[q]]
                    hot.add(x)
                    hot.add(y)
                res, r = evict(c, page, hot | {a, b}, pos[g])
                if res == 'free':
                    dest = r
                elif res == 'slot':
                    continue
            if dest is not None:
                ca, cb = code_at(a, c), code_at(b, c)
                program.put(page, c, op, rule.K_REG, ca, cb, dest, ('gate', g))
                done.add(g)
                consume(a)
                consume(b)
                put_reg(g, dest)
                continue
        # 3. prefetch a local operand of an upcoming gate
        want = None
        for q in range(head, min(len(order), head + lookahead)):
            g = order[q]
            if g in done:
                continue
            _, a, b = self.mops[g]
            for z in (a, b):
                if z in (0, 1) or regs_of.get(z):
                    continue
                if code_at(z, c) is not None:
                    want = (q, z)
                    break
            if want:
                break
        if want is None:
            # reload an output value that was spilled here but is stored elsewhere
            for (cc, s_), v in list(scr.items()):
                if abs(cc - c) <= self.win and uses[v] > 0 and not regs_of.get(v) and v in stored_later:
                    want = (pos.get(v, 0), v)
                    break
        if want is not None:
            q, z = want
            r = free_reg()
            if r is None:
                res, r = evict(c, page, {z}, q)
                if res == 'slot':
                    continue
                if res is None:
                    idle += 1
                    continue
            program.put(page, c, M_OR, rule.K_REG, code_at(z, c), C0, r, ('load', z))
            put_reg(z, r)
            continue
        idle += 1
        # classify: why can the head gate not issue here?
        reason = 'drained'
        if head < len(order):
            g = order[head]
            _, a, b = self.mops[g]
            if not all(z in done or z not in gates for z in (a, b)):
                reason = 'head-operand-pending'
            else:
                for z in (a, b):
                    if code_at(z, c) is None:
                        if z in lane_loc:
                            reason = 'head-waits-lane'
                        elif scr_of.get(z):
                            reason = 'head-waits-spill'
                        else:
                            reason = 'head-lost-value'
                        break
                else:
                    reason = 'head-no-register'
        idle_reasons[reason] = idle_reasons.get(reason, 0) + 1
    self.last_idle = idle
    self.idle_reasons = idle_reasons
    self.last_page = page
    self._dbg = dict(done=done, reg=reg, uses=uses, gates=gates, order=order, head=head,
                     scr=scr, regs_of=regs_of, pending_hold=pending_hold)
    if n_pending or not targets_met():
        miss = sum(1 for v, r in targets_reg.items() if reg[r] != v)
        raise CompileError(f'unfinished: {n_pending} stores, {miss} register targets, '
                           f'{len(gates) - len(done)} gates left')
    return reg


Scheduler.run_inorder = run_inorder


def run_sweep(self, program, pages, targets_hold, init_regs, reserve=2, priority='dfs', active=64,
              **_ignored):
    """Location-aware list scheduling over the sweep (no fixed global order).

    At every visited cell the front takes the single most useful action:
      1. store a finished output due at this cell (or compute it into Hold);
      2. compute a ready gate whose operands are all at hand (registers,
         constants, lane or scratch bits of this cell), preferring gates that
         free registers, then gates with the longest path to an output;
      3. load a value located here (lane input or spilled bit) that is an
         operand of a ready gate, preferring the most critical consumer;
      4. spill the least urgent computed register value to this cell's
         scratch when registers run short.
    Input copies are dropped (they can be reloaded); computed values are
    spilled before their register is reused.
    """
    p, L = self.p, self.p.L
    roots = [v for v, _ in targets_hold]
    gates = self.cone(roots)
    mops = self.mops
    consumers = defaultdict(list)
    uses = defaultdict(int)
    for g in gates:
        _, a, b = mops[g]
        for z in {a, b}:
            consumers[z].append(g)
        uses[a] += 1
        uses[b] += 1
    for v, _ in targets_hold:
        uses[v] += 1
    height = {}
    for g in self.topo_sorted(gates, reverse=True):
        hs = [height[q] for q in consumers.get(g, ()) if q in gates]
        height[g] = 1 + (max(hs) if hs else 0)
    if priority == 'dfs':
        # earlier in the depth-first order = more urgent; only the first
        # `active` ready gates (by that order) may pull operands in
        order = self.dfs_order(roots, gates)
        n_ord = len(order)
        for i, g in enumerate(order):
            height[g] = n_ord - i
    reg = [None] * L
    regs_of = defaultdict(set)
    for r, v in init_regs.items():
        reg[r] = v
        regs_of[v].add(r)
    scr, scr_of = {}, defaultdict(set)
    done = set()
    pending_hold = defaultdict(list)
    for v, cell in targets_hold:
        pending_hold[cell].append(v)
    n_pending = len(targets_hold)
    C0, C1 = self.C0, self.C1
    lane_loc = self.lane_loc
    at_cell = defaultdict(list)                    # cell -> input values used here
    for v, (cell, _) in lane_loc.items():
        if uses.get(v):
            at_cell[cell].append(v)

    def is_avail(z):
        return z in (0, 1) or z not in gates or z in done

    def ready(g):
        _, a, b = mops[g]
        return g not in done and is_avail(a) and is_avail(b)

    def code_at(v, c):
        if v == 0: return C0
        if v == 1: return C1
        rs = regs_of.get(v)
        if rs: return min(rs)
        if v in lane_loc:
            code = self.lane_code(v, c)
            if code is not None: return code
        for (cc, s_) in scr_of.get(v, ()):
            code = self.scr_code(s_, cc, c)
            if code is not None: return code
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

    store_left = defaultdict(int)                  # outputs still to be stored
    for v, _ in targets_hold:
        store_left[v] += 1

    def urgency(v):
        best = 500 if store_left.get(v) else 0
        for g in consumers.get(v, ()):
            if g in gates and g not in done:
                best = max(best, height[g] + (1000 if ready(g) else 0))
        return best

    def droppable(r):
        """Register whose value can be dropped without a slot (reloadable)."""
        v = reg[r]
        return v is not None and (v in lane_loc or len(regs_of[v]) > 1 or bool(scr_of.get(v)))

    def free_reg(protect=()):
        for r in range(L):
            if reg[r] is None:
                return r
        cand = [(urgency(reg[r]), r) for r in range(L) if droppable(r) and reg[r] not in protect]
        if cand:
            _, r = min(cand)
            v = reg[r]
            regs_of[v].discard(r)
            reg[r] = None
            return r
        return None

    readyset = set(g for g in gates if ready(g))
    page = None
    for page, c in slots(p):
        if page not in pages:
            continue
        if n_pending == 0:
            break
        acted = False
        # 1. stores due here
        for v in list(pending_hold.get(c, ())):
            cv = code_at(v, c)
            if cv is not None:
                program.put(page, c, M_OR, rule.K_HOLD, cv, C0, 0, ('store', v))
                pending_hold[c].remove(v)
                n_pending -= 1
                store_left[v] -= 1
                consume(v)
                acted = True
                break
            if v in gates and v not in done and uses[v] == 1 and ready(v):
                op, a, b = mops[v]
                ca, cb = code_at(a, c), code_at(b, c)
                if ca is not None and cb is not None:
                    program.put(page, c, op, rule.K_HOLD, ca, cb, 0, ('gate->hold', v))
                    pending_hold[c].remove(v)
                    n_pending -= 1
                    store_left[v] -= 1
                    uses[v] -= 1
                    done.add(v)
                    readyset.discard(v)
                    consume(a)
                    consume(b)
                    for q in consumers.get(v, ()):
                        if q in gates and ready(q):
                            readyset.add(q)
                    acted = True
                    break
        if acted:
            continue
        # 2. compute: candidates are gates with all operands at hand here
        cands = set()
        for v in regs_of:
            for g in consumers.get(v, ()):
                if g in readyset:
                    cands.add(g)
        for v in at_cell.get(c, ()):
            for g in consumers.get(v, ()):
                if g in readyset:
                    cands.add(g)
        for (cc, s_), v in list(scr.items()):
            if cc == c:
                for g in consumers.get(v, ()):
                    if g in readyset:
                        cands.add(g)
        best = None
        n_free = sum(1 for r in range(L) if reg[r] is None)
        for g in cands:
            op, a, b = mops[g]
            ca, cb = code_at(a, c), code_at(b, c)
            if ca is None or cb is None:
                continue
            kills = [z for z in {a, b} if z not in (0, 1) and uses[z] == (2 if a == b else 1) and regs_of.get(z)]
            key = (len(kills) if n_free <= reserve else 0, height[g])
            if best is None or key > best[0]:
                best = (key, g, op, a, b, kills, ca, cb)
        if best is not None:
            _, g, op, a, b, kills, ca, cb = best
            dest = min(regs_of[kills[0]]) if kills else free_reg(protect=(a, b))
            if dest is not None:
                program.put(page, c, op, rule.K_REG, ca, cb, dest, ('gate', g))
                done.add(g)
                readyset.discard(g)
                consume(a)
                consume(b)
                put_reg(g, dest)
                for q in consumers.get(g, ()):
                    if q in gates and ready(q):
                        readyset.add(q)
                continue
        # 3. load a value located here that a ready gate needs
        want = None
        local = [(v, None) for v in at_cell.get(c, ())] + \
                [(v, s_) for (cc, s_), v in scr.items() if cc == c]
        if priority == 'dfs' and readyset:
            cutoff = sorted((height[g] for g in readyset), reverse=True)[:active][-1]
        else:
            cutoff = 0
        for v, s_ in local:
            if regs_of.get(v) or uses.get(v, 0) <= 0:
                continue
            u = 300 if store_left.get(v) else 0
            for g in consumers.get(v, ()):
                if g in readyset and height[g] >= cutoff:
                    _, a, b = mops[g]
                    other = b if a == v else a
                    bonus = 1000 if code_at(other, c) is not None or regs_of.get(other) else 0
                    u = max(u, height[g] + bonus)
            if u and (want is None or u > want[0]):
                want = (u, v)
        if want is not None:
            u, v = want
            r = None
            for q in range(L):
                if reg[q] is None:
                    r = q
                    break
            if r is None:
                cand = [(urgency(reg[q]), q) for q in range(L) if droppable(q)]
                if cand:
                    ue, q = min(cand)
                    if ue < u:
                        vv = reg[q]
                        regs_of[vv].discard(q)
                        reg[q] = None
                        r = q
            if r is not None:
                program.put(page, c, M_OR, rule.K_REG, code_at(v, c), C0, r, ('load', v))
                put_reg(v, r)
                continue
        # 4. spill the least urgent computed value when registers are short
        n_free = sum(1 for r in range(L) if reg[r] is None)
        if n_free <= reserve:
            free_s = [s_ for s_ in range(p.S) if (c, s_) not in scr]
            if free_s:
                cand = [(urgency(reg[r]), r) for r in range(L)
                        if reg[r] is not None and reg[r] not in (0, 1) and not droppable(r)
                        and reg[r] in gates]
                if cand:
                    _, r = min(cand)
                    v = reg[r]
                    s_ = free_s[0]
                    program.put(page, c, M_OR, rule.K_SCR, r, C0, s_, ('spill', v))
                    scr[(c, s_)] = v
                    scr_of[v].add((c, s_))
                    regs_of[v].discard(r)
                    reg[r] = None
                    continue
    self.last_page = page
    self.last_idle = 0
    self.idle_reasons = {}
    if n_pending:
        raise CompileError(f'unfinished (sweep): {n_pending} stores, {len(gates) - len(done)} gates left')
    return reg


Scheduler.run_sweep = run_sweep


def compile_candidate(p, layout=None, window=64, reserve=2, verbose=False,
                      mode='inorder', lookahead=160, ooo=8, order_seed=None, order_flip=0.2,
                      free_floor=10**9, order_kind='dfs', reassoc=False):
    net, comp = p.fam().cached(p)
    if layout is None:
        layout = default_layout(p)
    sched = Scheduler(p, comp, layout, window=window, reserve=reserve, verbose=verbose)
    if reassoc:
        sched.reassociate(comp.outputs.values())
    if order_seed is not None:
        sched.order_rng = np.random.default_rng(order_seed)
        sched.order_flip = order_flip
    prog = Program(p, layout)
    k = p.k
    computed_front = getattr(p, 'computed_front', False)
    if computed_front:
        addr_nodes = [comp.outputs[('laddr', i)] for i in range(k)]
    else:
        addr_nodes = [comp.index[('x', 0, 'addr', i)] for i in range(k)]
    psel_nodes = [comp.outputs[('psel', i)] for i in range(p.PW)]
    # Phase A: fetch key.
    targets = {}
    for i, v in enumerate(addr_nodes):
        targets[v] = i
    for i, v in enumerate(psel_nodes):
        if v in targets and targets[v] != k + i:
            raise CompileError('psel equals an address bit; needs a copy')
        targets[v] = k + i
    # Constant psel bits need explicit materialization.
    for v in list(targets):
        if v in (0, 1):
            raise CompileError('constant psel bit not supported yet')
    phase_a_pages = set(range(p.MP))
    if hasattr(p, 'NPe'):
        # Early program (Gray p. 35): upper new Flag1 into Hold at Q-3, Flag2 at 3.
        f1_cell, f2_cell = getattr(p.fam(), 'flag_store_cells', lambda p: (p.Q - 3, 3))(p)
        early = [(comp.outputs[('y', 'f1', 0)], f1_cell), (comp.outputs[('y', 'f2', 0)], f2_cell)]
        # a confined front's flags leave by courier before T_sig: finish one pass early
        early_pages = range(p.NPe - 1) if getattr(p, 'confined', False) else range(p.NPe)
        sched.run_inorder(prog, columns(p, early_pages), early, {}, lookahead=lookahead, ooo=ooo,
                          free_floor=free_floor)
        phase_a_pages = set(range(p.NPe, p.MP))
    if computed_front:
        sched.run_inorder(prog, columns(p, phase_a_pages), [], {}, lookahead=lookahead, ooo=ooo,
                          free_floor=free_floor, targets_reg=targets,
                          late_targets=getattr(p, 'five_front', False))
    else:
        window_b = sched.window
        sched.window = max(64, window_b)
        sched.run(prog, columns(p, phase_a_pages), targets, [], {})
        sched.window = window_b
    # Phase B: all outputs.
    init = {i: v for i, v in enumerate(addr_nodes)}
    for i in range(p.IW):
        node = comp.index.get(('I', i))
        if node is not None:
            init[k + i] = node
    holds = []
    for f, w in p.fam().schema(p):
        for i in range(w):
            v = comp.outputs[('y', f, i)]
            holds.append((v, int(layout[sched.bit[(f, i)]])))
    final_end = p.NPe + p.run_len if getattr(p, 'tmr', False) else p.NP
    if mode == 'sweep':
        sched.run_sweep(prog, columns(p, range(p.MP + 1, final_end)), holds, init)
    elif mode == 'inorder':
        sched.run_inorder(prog, columns(p, range(p.MP + 1, final_end)), holds, init,
                          lookahead=lookahead, ooo=ooo, free_floor=free_floor,
                          order_kind=order_kind)
    else:
        sched.run(prog, columns(p, range(p.MP + 1, final_end)), {}, holds, init)
    if getattr(p, 'tmr', False):
        # Runs 1 and 2 execute the identical program (phase A, match, final),
        # shifted by run_len passes; the hardware routes their Hold stores to
        # Hold copies B and C. run_len is even, so sweep directions agree.
        D = getattr(p, 'D', 1)
        src = sorted(columns(p, range(p.NPe, p.NPe + p.run_len)))
        for r in (1, 2):
            shift = r * p.run_len * D
            for col in src:
                prog.rom[:, col + shift] = prog.rom[:, col]
                prog.used[:, col + shift] = prog.used[:, col]
        run0 = [x for x in prog.listing if p.NPe * D <= x[0] < (p.NPe + p.run_len) * D]
        for r in (1, 2):
            prog.listing += [(x[0] + r * p.run_len * D,) + tuple(x[1:]) for x in run0]
    return prog
