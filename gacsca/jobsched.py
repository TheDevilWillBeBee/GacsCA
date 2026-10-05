"""Job-pool scheduling for the comb of fronts.

The three programs of a G candidate (the early Flag program, the fetch key
and the final outputs) are compiled as one pool of gates, executed by the
fronts of the comb as interchangeable workers:

  * A front *claims* work: large unclaimed sub-cones of the first unfinished
    target (the flags, then the fetch key, then the Hold outputs). Its claimed
    nodes form a queue in depth-first order. The loadable inputs (lanes,
    parked values) of the first runnable nodes of the queue are *wished*:
    the front loads a wished value when it passes the value's cell, and
    executes a node as soon as its operands are in its registers, in any
    order. Nothing waits for the head of the queue.
  * A value with a consumer outside the claiming front is *parked* in a
    scratch bit of the cell the front is at; any front loads it from there.
    Scratch is the only channel between fronts and between claims. A node
    whose operand another front is still computing waits for that front to
    park it (a promise).
  * Registers are given to the earliest nodes of the queue: when they are
    full, the value whose next use lies farthest ahead is dropped (if it can
    be loaded again) or parked.
  * Maximal associative trees (AND, OR, XOR with single-use inner nodes) are
    n-ary nodes, folded in whatever order their leaves arrive. A partial
    result ("piece") that its front has no further leaf for is parked, and
    absorbed by whichever front holds another piece when it passes.
  * Deadlines. The flag stores come first (they define NPe). When the fetch
    key is complete, front 0 gives back its unfinished claims and collects
    the key from scratch into R[0 : k+PW]; the other fronts stop one page
    later, with everything they hold parked. Nobody executes in the match
    pass. After it, front 0 holds the fetched instruction I and first
    computes what depends on I alone.

The schedule is the same function as the netlist, gate for gate, except
that shared associative trees are folded in schedule order. `replay` runs a
compiled listing on random data and checks every value written, the key at
the match pass and every Hold target against the netlist; the physical
check is closure of the rule on encoded colonies.
"""
import heapq
from collections import defaultdict
import numpy as np
from . import rule, compiler
from .compiler import M_AND, M_OR, M_XOR, M_ANDN, CompileError, work_range
from .multifront import MultiProgram

BIG = 10**9


def bits_of(m):
    while m:
        low = m & -m
        yield low.bit_length() - 1
        m ^= low


class Dag:
    """Machine DAG of all targets of one work period, with n-ary associative nodes.

    nodes: gate ids in topological order; mops[g] = (op, a, b) for binary
    nodes, nary[x] = (op, leaves). cone[g] is the set of nodes g depends on
    (itself included) as a bit mask over `nodes`."""

    def __init__(self, p, comp, layout):
        self.p, self.comp = p, comp
        self.layout = np.asarray(layout)
        sched = compiler.Scheduler(p, comp, layout)
        fam = p.fam()
        k = p.k
        self.lane_loc = sched.lane_loc
        self.C0, self.C1 = sched.C0, sched.C1
        self.scr_code = [sched.src_code[('scr', s)] for s in range(p.S)]
        f1_cell, f2_cell = fam.flag_store_cells(p)
        # targets: flag stores, key registers of front 0, Hold stores
        self.flags = [(comp.outputs[('y', 'f1', 0)], f1_cell), (comp.outputs[('y', 'f2', 0)], f2_cell)]
        self.key = {i: comp.outputs[('laddr', i)] for i in range(k)}
        for i in range(p.PW):
            self.key[k + i] = comp.outputs[('psel', i)]
        self.holds = [(comp.outputs[('y', f, i)], int(layout[b])) for (f, i), b in sched.bit.items()]
        self.ibits = {}                      # node of fetched instruction bit i -> register of front 0
        for i in range(p.IW):
            node = comp.index.get(('I', i))
            if node is not None:
                self.ibits[node] = k + i
        mops = dict(sched.mops)
        roots = [v for v, _ in self.flags] + list(self.key.values()) + [v for v, _ in self.holds]
        gates = set()
        stack = list(roots)
        while stack:
            x = stack.pop()
            if x in gates or x not in mops:
                continue
            gates.add(x)
            stack.append(mops[x][1])
            stack.append(mops[x][2])
        # n-ary nodes: maximal associative trees whose inner nodes have one use
        fan = defaultdict(int)
        for g in gates:
            fan[mops[g][1]] += 1
            fan[mops[g][2]] += 1
        protect = set(roots)
        removed = set()
        self.nary = {}
        for x in sorted(gates, reverse=True):
            if x in removed:
                continue
            op, a, b = mops[x]
            if op not in (M_AND, M_OR, M_XOR) or a in (0, 1) or b in (0, 1):
                continue
            leaves, internal, st = [], [], [a, b]
            while st:
                z = st.pop()
                if (z in gates and z not in removed and z not in protect and fan[z] == 1
                        and mops[z][0] == op and mops[z][1] not in (0, 1) and mops[z][2] not in (0, 1)):
                    internal.append(z)
                    st += [mops[z][1], mops[z][2]]
                else:
                    leaves.append(z)
            if len(leaves) < 3:
                continue
            self.nary[x] = (op, sorted(leaves))
            removed |= set(internal)
        self.nodes = sorted(gates - removed)         # node ids are topological
        self.mops = {g: mops[g] for g in self.nodes if g not in self.nary}
        self.idx = {g: i for i, g in enumerate(self.nodes)}
        self.bit = {g: 1 << i for g, i in self.idx.items()}
        self.cons = defaultdict(list)
        for g in self.nodes:
            for z in self.operands(g):
                self.cons[z].append(g)
        self.cone = {}
        for g in self.nodes:
            m = self.bit[g]
            for z in self.operands(g):
                if z in self.cone:
                    m |= self.cone[z]
            self.cone[g] = m
        self.cons_mask = defaultdict(int)
        for v, lst in self.cons.items():
            for g in lst:
                self.cons_mask[v] |= self.bit[g]
        self.next_id = max(max(mops), comp.n_nodes) + 1
        # nodes that depend on the fetched instruction, and those computed from it alone
        dep = set(self.ibits)
        pure = set(self.ibits) | {0, 1}
        self.idep = self.pure_i = 0
        for g in self.nodes:
            ops = self.operands(g)
            if any(z in dep for z in ops):
                dep.add(g)
                self.idep |= self.bit[g]
            if all(z in pure for z in ops):
                pure.add(g)
                self.pure_i |= self.bit[g]

    def operands(self, g):
        if g in self.nary:
            return self.nary[g][1]
        return self.mops[g][1:]

    def fresh(self):
        self.next_id += 1
        return self.next_id

    def dfs_index(self, roots):
        """Depth-first post-order rank of every node, larger sub-cones first."""
        size = {g: self.cone[g].bit_count() for g in self.nodes}
        order, seen = {}, set()
        for r in roots:
            st = [(r, False)]
            while st:
                y, post = st.pop()
                if y not in self.idx or y in seen:
                    continue
                if post:
                    seen.add(y)
                    order[y] = len(order)
                    continue
                st.append((y, True))
                kids = sorted(set(self.operands(y)), key=lambda z: (-size.get(z, 0), z))
                for z in reversed(kids):
                    if z in self.idx and z not in seen:
                        st.append((z, False))
        return order


class Front:
    def __init__(self, j, L):
        self.j = j
        self.reg = [None] * L
        self.regs_of = defaultdict(set)
        self.nfree = L
        self.need = defaultdict(int)        # value -> pending uses on this front
        self.acons = defaultdict(list)      # value -> claimed binary nodes of this front using it
        self.active = set()                 # claimed, not yet computed
        self.mine = 0
        self.order = []                     # the queue: claimed nodes in priority order
        self.qpos = 0
        self.wish = {}                      # value -> cell where it will be loaded
        self.wishcell = defaultdict(set)
        self.ready = []                     # heap of nodes whose operands are in registers
        self.in_ready = set()
        self.topark = set()
        self.spill = set()                  # values to drop once parked (register pressure)
        self.pieces = defaultdict(list)     # n-ary x -> pieces held in registers
        self.piece_out = set()              # n-ary nodes whose held piece is to be parked (pressure)
        self.duty = defaultdict(list)       # leaf value -> n-ary nodes this front folds it into
        self.xpending = defaultdict(int)    # n-ary x -> claimed leaf folds not yet pieces
        self.xduty = set()                  # n-ary nodes claimed as a whole
        self.stores = defaultdict(list)     # cell -> values this front carries to Hold there
        self.nstores = 0
        self.version = self.scan_version = -1
        self.next_refill = 0
        self.last_act = 0
        self.runnable = 0                   # nodes in the queue window not waiting for another front
        self.frontier = BIG                 # priority of the front_k-th runnable node
        self.keyplace = None                # front 0: key register -> value still to collect
        self.draining = False


class Engine:
    """One compile: `run()` fills `prog` (a MultiProgram listing).

    MP=None probes: the match pass is placed as soon as the key is complete.
    With MP given, the key must be complete in time for it."""

    def __init__(self, p, comp, layout, MP=None, size_max=500, low=120, window=150, front_k=60,
                 reserve=10, load_reserve=3, headroom=8, wish_cap=200, store_cap=8,
                 pure_first=True, drain_ticks=120, root_order='size', share=True, try_wishes=1, key_fronts=0,
                 max_pages=1500):
        assert getattr(p, 'confined', False), 'the job scheduler drives a confined front or comb'
        self.p = p
        self.dag = d = Dag(p, comp, layout)
        self.L, self.S, self.F = p.L, p.S, p.fronts
        self.lo, self.hi = work_range(p)
        self.H = (p.fronts - 1) * p.delta
        self.PL = self.hi - self.lo + self.H
        self.size_max, self.low, self.window, self.front_k = size_max, low, window, front_k
        self.reserve, self.load_reserve, self.headroom = reserve, load_reserve, headroom
        self.wish_cap, self.store_cap, self.pure_first = wish_cap, store_cap, pure_first
        self.drain_ticks = drain_ticks
        self.share = share
        self.try_wishes = try_wishes
        self.key_fronts = key_fronts          # fronts that claim only flag and key work before the match pass
        self.fixed_MP = MP
        self.max_pages = max_pages
        self.prog = MultiProgram(p, self.F)
        self.fronts = [Front(j, self.L) for j in range(self.F)]
        self.done = set()
        self.done_mask = 0
        self.claimed = 0
        self.parked = {}                    # value -> (cell, scratch bit)
        self.scr = {}
        self.scr_used = defaultdict(int)
        self.unparked = set()               # computed values that exist only in registers
        self.version = 0
        self.T = 0
        self.uses = defaultdict(int)        # value -> pending uses anywhere
        for v, lst in d.cons.items():
            self.uses[v] = len(lst)
        self.store_cells = defaultdict(list)       # value -> pending Hold cells nobody carries
        self.flag_vals = [v for v, _ in d.flags]
        self.flag_cells = {cell for _, cell in d.flags}
        for v, cell in d.flags + d.holds:
            self.store_cells[v].append(cell)
            self.uses[v] += 1
        self.flag_left = len(d.flags)
        self.n_store_left = len(d.flags) + len(d.holds)
        self.key_vals = set(d.key.values())
        assert len(self.key_vals) == len(d.key), 'two key registers share a value'
        for v in self.key_vals:
            assert v in d.idx, 'key value must be a gate'
            self.uses[v] += 1
        self.keys_left = len(self.key_vals)
        self.key_cells = set()
        # n-ary state
        self.leaf_pending = {x: set(lv) for x, (op, lv) in d.nary.items()}   # leaves not yet pieces
        self.parked_pieces = defaultdict(set)      # x -> pieces lying at a cell (raw leaf or parked)
        self.loc_pieces = defaultdict(set)         # cell -> (x, piece)
        self.fold_claim = set()                    # (x, leaf): a front has claimed this fold
        self.piece_of = {}                         # piece id -> x
        self.leaf_count = {}
        for x, (op, lv) in d.nary.items():
            cnt = defaultdict(int)
            for v in lv:
                cnt[v] += 1
            self.leaf_count[x] = cnt
        # targets in deadline order: flags, key, then the Hold roots that do not depend on
        # the fetched instruction (they can be finished before the match pass), then the rest;
        # larger cones first within each group
        hold_roots = sorted({v for v, _ in d.holds if v in d.idx},
                            key=lambda v: (bool(d.bit[v] & d.idep) if root_order == 'free_first' else 0,
                                           -d.cone[v].bit_count(), v))
        self.targets = []
        seen = set()
        for v in self.flag_vals + [d.key[r] for r in sorted(d.key)] + hold_roots:
            if v in d.idx and v not in seen:
                seen.add(v)
                self.targets.append(v)
        self.dfsi = d.dfs_index(self.targets)
        self.key_cone = 0
        for v in self.flag_vals + sorted(self.key_vals):
            self.key_cone |= d.cone.get(v, 0)
        self.post_match = False
        self.MP = self.MP_min = None
        self.NPe_page = None
        self.stats = defaultdict(int)
        self.idle_why = defaultdict(int)
        self.page_instr = []
        for x, (op, lv) in d.nary.items():
            for v in sorted(set(lv)):
                if v in d.lane_loc:
                    self.make_raw_piece(x, v)

    # ------------------------------------------------------------------ values and registers
    def available(self, v):
        """v can be loaded by any front (a lane or a parked value)."""
        return v in self.dag.lane_loc or v in self.parked

    def loc_cell(self, v):
        ll = self.dag.lane_loc.get(v)
        if ll is not None:
            return ll[0]
        pk = self.parked.get(v)
        return pk[0] if pk else None

    def local_code(self, v, c):
        ll = self.dag.lane_loc.get(v)
        if ll is not None:
            return ll[1] if ll[0] == c else None
        pk = self.parked.get(v)
        if pk is not None and pk[0] == c:
            return self.dag.scr_code[pk[1]]
        return None

    def code(self, f, v, c):
        """Source code of v for front f at cell c, or None."""
        if v == 0:
            return self.dag.C0
        if v == 1:
            return self.dag.C1
        rs = f.regs_of.get(v)
        if rs:
            return min(rs)
        return self.local_code(v, c)

    def in_reg(self, f, v):
        return v in (0, 1) or bool(f.regs_of.get(v))

    def pri(self, g):
        return self.dfsi.get(g, BIG)

    def put_reg(self, f, v, r):
        old = f.reg[r]
        if old is not None:
            f.regs_of[old].discard(r)
            if not f.regs_of[old]:
                del f.regs_of[old]
        else:
            f.nfree -= 1
        f.reg[r] = v
        f.regs_of[v].add(r)
        if v in f.wish:
            self.drop_wish(f, v)
        for g in f.acons.get(v, ()):
            self.check_ready(f, g)

    def free_regs(self, f, v):
        rs = f.regs_of.pop(v, None)
        if rs:
            for r in rs:
                f.reg[r] = None
                f.nfree += 1

    def free_reg_index(self, f):
        return f.reg.index(None) if f.nfree > 0 else None

    def add_wish(self, f, v):
        if v in f.wish or self.in_reg(f, v):
            return
        c = self.loc_cell(v)
        assert c is not None, ('wish of an unavailable value', v)
        f.wish[v] = c
        f.wishcell[c].add(v)

    def drop_wish(self, f, v):
        c = f.wish.pop(v, None)
        if c is not None:
            f.wishcell[c].discard(v)

    def check_ready(self, f, g):
        if g in f.in_ready or g not in f.active or g in self.dag.nary:
            return
        _, a, b = self.dag.mops[g]
        if self.in_reg(f, a) and self.in_reg(f, b):
            f.in_ready.add(g)
            heapq.heappush(f.ready, (self.pri(g), g))

    def release(self, f, v):
        """Front f no longer needs v."""
        if v in (0, 1) or f.need.get(v, 0) > 0:
            return
        f.need.pop(v, None)
        if v in f.wish:
            self.drop_wish(f, v)
        if v in f.regs_of:
            if self.uses[v] > 0 and v in self.unparked:
                f.topark.add(v)             # the only copy: park it before dropping
            else:
                self.free_regs(f, v)
                f.topark.discard(v)

    def use_done(self, v):
        """One use of v was consumed; a value without uses frees its scratch bit and registers."""
        if v in (0, 1):
            return
        self.uses[v] -= 1
        if self.uses[v] <= 0:
            pk = self.parked.pop(v, None)
            if pk is not None:
                del self.scr[pk]
                self.scr_used[pk[0]] -= 1
            self.unparked.discard(v)
            for f in self.fronts:
                if v in f.regs_of and f.need.get(v, 0) <= 0:
                    self.free_regs(f, v)
                    f.topark.discard(v)

    def consume(self, f, z, g=None):
        if z in (0, 1):
            return
        f.need[z] -= 1
        if g is not None:
            lst = f.acons.get(z)
            if lst and g in lst:
                lst.remove(g)
        self.use_done(z)
        if f.need.get(z, 0) <= 0:
            self.release(f, z)

    def free_scr(self, c, v=None):
        """A free scratch bit of cell c for value v, or None."""
        if self.scr_used[c] >= self.S:
            return None
        if v in self.key_vals and c in self.key_cells:
            return None                     # front 0 collects one key value per visit
        for s in range(self.S):
            if (c, s) not in self.scr:
                return s
        return None

    def do_park(self, v, c, s):
        self.parked[v] = (c, s)
        if v in self.key_vals:
            self.key_cells.add(c)
        self.scr[(c, s)] = v
        self.scr_used[c] += 1
        self.unparked.discard(v)
        self.version += 1
        self.stats['max_parked'] = max(self.stats['max_parked'], len(self.parked))
        x = self.piece_of.get(v)
        if x is not None and x not in self.done:
            self.parked_pieces[x].add(v)
            self.loc_pieces[c].add((x, v))
        for x in self.dag.cons.get(v, ()):
            if x in self.dag.nary:
                self.make_raw_piece(x, v)

    def stored(self, v, c, pg):
        self.n_store_left -= 1
        if v in self.flag_vals and c in self.flag_cells:
            self.flag_left -= 1
            if self.flag_left == 0:
                self.NPe_page = pg

    # ------------------------------------------------------------------ n-ary nodes
    def make_raw_piece(self, x, v):
        """Pending leaf v of x lies at a cell and no front has claimed its fold: any front
        holding a piece of x may absorb it there."""
        if v not in self.leaf_pending[x] or (x, v) in self.fold_claim or x in self.done:
            return
        self.leaf_pending[x].discard(v)
        self.parked_pieces[x].add(v)
        self.loc_pieces[self.loc_cell(v)].add((x, v))

    def n_pieces(self, x):
        n = len(self.parked_pieces[x])
        for f in self.fronts:
            lst = f.pieces.get(x)
            if lst:
                n += len(lst)
        return n

    def claim_fold(self, f, x, z):
        """Front f will fold pending leaf z into x."""
        if z not in self.leaf_pending[x] or (x, z) in self.fold_claim:
            return
        self.fold_claim.add((x, z))
        n = self.leaf_count[x][z]
        f.need[z] += n
        f.xpending[x] += n
        if z in f.regs_of and (z in self.done or z in self.dag.lane_loc):
            self.become_piece(f, x, z)
        else:
            f.duty[z].append(x)

    def become_piece(self, f, x, v):
        """Leaf v, whose fold into x front f has claimed, is now in f's registers."""
        n = self.leaf_count[x][v]
        f.xpending[x] -= n
        self.leaf_pending[x].discard(v)
        for _ in range(n):
            f.pieces[x].append(v)
        self.queue_fold(f, x)

    def queue_fold(self, f, x):
        if len(f.pieces[x]) >= 2 and ('fold', x) not in f.in_ready:
            f.in_ready.add(('fold', x))
            heapq.heappush(f.ready, (self.pri(x), ('fold', x)))

    def piece_idle(self, f, x):
        """f holds a piece of x but has nothing more to fold into it."""
        return f.xpending.get(x, 0) <= 0 and x not in f.xduty

    # ------------------------------------------------------------------ claiming
    def refill(self, f):
        """Claim work for front f: large unclaimed sub-cones (size_max nodes in all) of the
        first unfinished targets. Sub-cones that depend on nothing another front has in
        progress are preferred."""
        d = self.dag
        starved = (not f.wish and not f.ready and self.T - f.last_act > 16)
        if (min(f.runnable, len(f.active)) > self.low and not starved) or self.T < f.next_refill \
                or len(f.active) > 4 * self.size_max or f.version == self.version:
            return
        f.version = self.version
        cone = d.cone
        notdone = ~self.done_mask
        todo = notdone & ~self.claimed
        if not self.post_match:
            todo &= ~d.idep
            if f.j < self.key_fronts:
                todo &= self.key_cone          # this front works on the flags and the key only
        foreign = self.claimed & ~f.mine & notdone
        job = 0
        budget = self.size_max
        if self.share:
            # near the end, leave the other fronts their share of what is left
            budget = min(budget, max(60, todo.bit_count() // self.F + 1))
        want = budget // 2

        def descend(X, indep, memo, count):
            if X not in d.idx or X in memo:
                return 0
            rem = cone[X] & todo & ~job
            if rem == 0:
                return 0
            count[0] += 1
            if count[0] > 2500:
                return 0
            if rem.bit_count() <= budget and not (indep and (cone[X] & foreign)):
                return rem
            kids = [z for z in set(d.operands(X)) if z in d.idx]
            kids.sort(key=lambda z: (-(cone[z] & todo & ~job).bit_count(), z))
            for Y in kids:
                r = descend(Y, indep, memo, count)
                if r:
                    return r
            memo.add(X)
            return 0

        for indep in (True, False):
            memo, count = set(), [0]
            for T in self.targets:
                if T in self.done:
                    continue
                while budget > 0 and job.bit_count() < want:
                    rem = descend(T, indep, memo, count)
                    if not rem:
                        break
                    job |= rem
                    budget -= rem.bit_count()
                if job.bit_count() >= want or budget <= 0 or count[0] > 2500:
                    break
            if job.bit_count() >= want // 4 or starved:
                break
        if job:
            self.claim(f, job)
        else:
            f.next_refill = self.T + 6

    def claim(self, f, job):
        d = self.dag
        self.claimed |= job
        f.mine |= job
        self.stats['claims'] += 1
        glist = [d.nodes[i] for i in bits_of(job)]
        f.active.update(glist)
        f.order = sorted([g for g in f.order[f.qpos:] if g in f.active] + glist, key=self.pri)
        f.qpos = 0
        for g in glist:
            if g in d.nary:
                f.xduty.add(g)
                for z in sorted(self.leaf_pending[g]):
                    if z in d.idx and ((d.bit[z] & job) or (d.bit[z] & f.mine)) or z in f.regs_of \
                            or self.available(z):
                        self.claim_fold(f, g, z)
            else:
                _, a, b = d.mops[g]
                for z in (a, b):
                    if z not in (0, 1):
                        f.need[z] += 1
                        f.acons[z].append(g)
            # this value is folded into its n-ary consumers by the front that computes it
            for x in d.cons.get(g, ()):
                if x in d.nary and not (d.bit[x] & job):
                    self.claim_fold(f, x, g)
        for g in glist:
            self.check_ready(f, g)

    def claim_store(self, f, v, cell):
        f.stores[cell].append(v)
        f.nstores += 1
        if v not in (0, 1):
            f.need[v] += 1

    def pickup_stores(self, f):
        """Front f takes over pending Hold stores of root values it can get."""
        cap = self.store_cap if f.active or not self.share else self.L - self.reserve
        if f.nstores >= cap:
            return
        for v, cells in self.store_cells.items():
            if not cells:
                continue
            if f.nstores >= cap or f.nfree <= self.reserve:
                break
            if v in (0, 1):
                while cells:
                    self.claim_store(f, v, cells.pop())
                continue
            if not (self.available(v) or (v in f.regs_of and v in self.done)):
                continue
            while cells and f.nstores < cap:
                self.claim_store(f, v, cells.pop())
            if not self.in_reg(f, v):
                self.add_wish(f, v)

    def unclaim_all(self, f):
        """Front f gives back everything it has claimed but not computed. Register values
        that other work still needs get parked; the rest is dropped."""
        d = self.dag
        for z in list(f.duty):
            for x in f.duty[z]:
                self.fold_claim.discard((x, z))
                f.need[z] -= self.leaf_count[x][z]
                if self.available(z):
                    self.make_raw_piece(x, z)
        f.duty.clear()
        f.xpending.clear()
        for g in f.active:
            if g not in d.nary:
                for z in d.mops[g][1:]:
                    if z not in (0, 1):
                        f.need[z] -= 1
            self.claimed &= ~d.bit[g]
            f.mine &= ~d.bit[g]
        f.xduty.clear()
        f.active.clear()
        f.acons.clear()
        f.order, f.qpos = [], 0
        f.ready, f.in_ready = [], set()
        f.spill.clear()
        f.piece_out.clear()
        for v in list(f.wish):
            self.drop_wish(f, v)
        for cell, lst in f.stores.items():
            for v in lst:
                self.store_cells[v].append(cell)
                if v not in (0, 1):
                    f.need[v] -= 1
        f.stores.clear()
        f.nstores = 0
        for v in [v for v, n in f.need.items() if n <= 0]:
            del f.need[v]
        for v in list(f.regs_of):
            if f.need.get(v, 0) <= 0:
                self.release(f, v)
        for x in list(f.pieces):
            self.queue_fold(f, x)
        self.version += 1

    # ------------------------------------------------------------------ register pressure
    def blocked(self, f, g):
        """Binary node g of f's queue waits for a result of another front."""
        d = self.dag
        for z in d.mops[g][1:]:
            if z in (0, 1) or z in f.regs_of or z in d.lane_loc or z in self.parked:
                continue
            if z in d.idx and (d.bit[z] & f.mine) and z not in self.done:
                continue
            return True
        return False

    def next_use(self, f, v):
        """Queue priority of the next node of f that uses v. Uses that wait for another
        front count as far away."""
        nu = BIG
        for g in f.acons.get(v, ()):
            pr = self.pri(g)
            if pr < nu and not self.blocked(f, g):
                nu = pr
        for x in f.duty.get(v, ()):
            nu = min(nu, self.pri(x))
        return nu

    def out_pending(self, f):
        """An eviction of f is still waiting for its park slot (stale marks are dropped)."""
        f.spill = {v for v in f.spill if v in f.topark and v in f.regs_of}
        f.piece_out = {x for x in f.piece_out if x not in self.done and len(f.pieces.get(x, ())) == 1}
        return bool(f.spill or f.piece_out)

    def evict(self, f, limit, protect=()):
        """Make room on f: give up the register value whose next use on f is farthest, if
        beyond priority `limit`. A value that can be loaded again is dropped at once (returns
        True); a piece or a value that exists only here is marked for parking (returns
        False)."""
        held = set()
        piece = {}
        for x, lst in f.pieces.items():
            if len(lst) == 1 and x not in f.piece_out:
                piece[lst[0]] = x
            else:
                held.update(lst)
        for lst in f.stores.values():
            held.update(lst)
        best = None
        for v in f.regs_of:
            if v in protect or v in f.topark or v in held:
                continue
            nu = self.next_use(f, v)
            if v in piece:
                x = piece[v]
                if not self.leaf_pending[x] or f.xpending.get(x, 0) > 0:
                    nu = min(nu, self.pri(x))       # folds of x are due on this front
            if nu <= limit:
                continue
            if best is None or (nu, v) > best:
                best = (nu, v)
        if best is None:
            return False
        v = best[1]
        self.stats['evictions'] += 1
        if v in piece:
            f.piece_out.add(piece[v])
            return False
        if self.available(v):
            self.free_regs(f, v)
            return True
        f.spill.add(v)
        f.topark.add(v)
        return False

    def scan(self, f):
        """Wish the loadable inputs of the first `window` runnable nodes of f's queue; the
        first `front_k` of them define the frontier of urgent work."""
        d = self.dag
        order = f.order
        while f.qpos < len(order) and order[f.qpos] not in f.active:
            f.qpos += 1
        budget = self.wish_cap - len(f.wish)
        n = 0
        q = f.qpos
        frontier = BIG
        while q < len(order) and n < self.window:
            g = order[q]
            q += 1
            if g not in f.active:
                continue
            if g in d.nary:
                ops = [z for z in sorted(self.leaf_pending[g]) if g in f.duty.get(z, ())]
            else:
                ops = d.mops[g][1:]
                # a node waiting for another front's result is not counted
                if any(z not in (0, 1) and z not in f.regs_of and not self.available(z)
                       and not (z in d.idx and (d.bit[z] & f.mine)) for z in ops):
                    continue
            n += 1
            if n == self.front_k:
                frontier = self.pri(g)
            for z in ops:
                if z in (0, 1) or z in f.regs_of or z in f.wish or not self.available(z):
                    continue
                if budget > 0:
                    self.add_wish(f, z)
                    budget -= 1
        f.runnable = n
        f.frontier = frontier
        if f.nfree <= self.load_reserve + 2 and f.wish and not self.out_pending(f):
            self.evict(f, frontier)         # keep a little room for the earliest runnable nodes

    # ------------------------------------------------------------------ execution
    def emit(self, f, pg, tk, c, op, kind, a, b, dd, note):
        self.prog.put(f.j, pg, tk, c, op, kind, a, b, dd, note)
        f.last_act = self.T
        self.stats['instr'] += 1

    def place_result(self, f, g, pg, tk, c, op, ca, cb, dying):
        """Emit the instruction computing value g on f at cell c and choose its destination:
        Hold (a root at its own cell, with no other use), scratch (no consumer on this front)
        or a register. Returns 'hold', 'park', ('reg', r, uses elsewhere) or None (no
        register free)."""
        need_here = f.need.get(g, 0)
        cells = self.store_cells.get(g)
        if cells and c in cells and need_here == 0 and self.uses[g] == 1:
            cells.remove(c)
            self.emit(f, pg, tk, c, op, rule.K_HOLD, ca, cb, 0, ('gate->hold', g))
            self.stored(g, c, pg)
            self.uses[g] -= 1
            return 'hold'
        if cells and not f.draining and g not in self.key_vals:
            while cells and f.nstores < self.store_cap:
                self.claim_store(f, g, cells.pop())
            need_here = f.need.get(g, 0)
        ext = self.uses[g] - need_here
        if need_here == 0:
            assert ext > 0, ('dead value', g)
            s = self.free_scr(c, g)
            if s is not None:
                self.emit(f, pg, tk, c, op, rule.K_SCR, ca, cb, s, ('gate->park', g))
                self.do_park(g, c, s)
                return 'park'
        r = dying[0] if dying else self.free_reg_index(f)
        if r is None:
            return None
        self.emit(f, pg, tk, c, op, rule.K_REG, ca, cb, r, ('gate', g))
        return ('reg', r, ext)

    def finish_value(self, f, g, how):
        d = self.dag
        self.done.add(g)
        if g in d.idx:
            self.done_mask |= d.bit[g]
        f.active.discard(g)
        self.version += 1
        if g in self.key_vals:
            self.keys_left -= 1
        if how in ('park', 'hold'):
            return
        _, r, ext = how
        self.unparked.add(g)
        self.put_reg(f, g, r)
        if ext > 0:
            f.topark.add(g)
        for x in f.duty.pop(g, ()):
            self.become_piece(f, x, g)

    def dying_regs(self, f, zs):
        """Registers of operands that die with the instruction being placed."""
        out = []
        for z in sorted(set(zs)):
            if z in (0, 1) or z not in f.regs_of:
                continue
            cnt = sum(1 for y in zs if y == z)
            if f.need.get(z, 0) == cnt and (self.uses[z] == cnt or z not in self.unparked):
                out.append(min(f.regs_of[z]))
        return out

    def exec_gate(self, f, g, pg, tk, c):
        """True: executed. False: no register for the result. None: an operand is not at hand."""
        op, a, b = self.dag.mops[g]
        ca, cb = self.code(f, a, c), self.code(f, b, c)
        if ca is None or cb is None:
            return None
        how = self.place_result(f, g, pg, tk, c, op, ca, cb, self.dying_regs(f, (a, b)))
        if how is None:
            return False
        self.consume(f, a, g)
        self.consume(f, b, g)
        self.finish_value(f, g, how)
        self.stats['gates'] += 1
        return True

    def exec_fold(self, f, x, local, pg, tk, c, duty=False):
        """Fold two pieces of x: two held in registers, or the first held piece with the
        piece `local` lying at this cell (duty: f had claimed that leaf's fold). The fold
        that leaves a single piece and no pending leaf produces x itself."""
        d = self.dag
        op = d.nary[x][0]
        lst = f.pieces[x]
        if local is None:
            if len(lst) < 2:
                return False
            p1, p2 = lst[0], lst[1]
            c2 = self.code(f, p2, c)
        else:
            if not lst:
                return False
            p1, p2 = lst[0], local
            c2 = self.local_code(p2, c)
        rs = f.regs_of.get(p1)
        if not rs or c2 is None:
            return False
        c1 = min(rs)
        last = (not self.leaf_pending[x] and self.n_pieces(x) == 2)
        dying = self.dying_regs(f, (p1, p2) if local is None else (p1,))
        if last:
            how = self.place_result(f, x, pg, tk, c, op, c1, c2, dying)
            if how is None:
                return False
        else:
            r = dying[0] if dying else self.free_reg_index(f)
            if r is None:
                return False
            q = d.fresh()
            self.piece_of[q] = x
            self.uses[q] = 1
            d.cons_mask[q] = d.bit[x]
            f.need[q] = 1
            self.emit(f, pg, tk, c, op, rule.K_REG, c1, c2, r, ('fold', x, q))
        self.stats['folds'] += 1
        lst.remove(p1)
        self.consume(f, p1)
        if local is None:
            lst.remove(p2)
            self.consume(f, p2)
        else:
            self.parked_pieces[x].discard(p2)
            self.loc_pieces[c].discard((x, p2))
            if duty:
                self.consume(f, p2)
            else:
                self.use_done(p2)
        if last:
            f.xduty.discard(x)
            for g in self.fronts:
                g.xpending.pop(x, None)
            self.finish_value(f, x, how)
        else:
            self.unparked.add(q)
            self.put_reg(f, q, r)
            lst.append(q)
            self.queue_fold(f, x)
        return True

    def load(self, f, v, pg, tk, c):
        r = self.free_reg_index(f)
        self.emit(f, pg, tk, c, M_OR, rule.K_REG, self.local_code(v, c), self.dag.C0, r, ('load', v))
        self.stats['loads'] += 1
        return r

    def act(self, f, pg, tk, c):
        """The one instruction of front f at cell c in page pg, or None."""
        d = self.dag
        # 1. a Hold store this front carries
        lst = f.stores.get(c)
        if lst:
            for v in lst:
                cv = self.code(f, v, c)
                if cv is not None:
                    self.emit(f, pg, tk, c, M_OR, rule.K_HOLD, cv, d.C0, 0, ('store', v))
                    lst.remove(v)
                    f.nstores -= 1
                    self.stored(v, c, pg)
                    self.consume(f, v)
                    return 'store'
        if f.keyplace is not None:
            return 'key' if self.place_key(f, pg, tk, c) else None
        # 2. wished values lying here, most urgent first: use one in place (its single use on
        #    this front) or load it
        wishes = f.wishcell.get(c)
        if wishes:
            ranked = []
            for v in wishes:
                pr = min((self.pri(g) for g in f.acons.get(v, ())), default=BIG)
                for x in f.duty.get(v, ()):
                    pr = min(pr, self.pri(x))
                ranked.append((pr, v))
            ranked.sort()
            for pr, v in ranked[:self.try_wishes]:
                if f.need.get(v, 0) <= 1:
                    for g in list(f.acons.get(v, ())):
                        _, a, b = d.mops[g]
                        if self.code(f, b if a == v else a, c) is not None and self.exec_gate(f, g, pg, tk, c):
                            return 'local'
                        break
                    for x in list(f.duty.get(v, ())):
                        if f.pieces.get(x) and self.leaf_count[x][v] == 1:
                            # fold the leaf straight into the held piece
                            f.duty[v].remove(x)
                            if not f.duty[v]:
                                del f.duty[v]
                            f.xpending[x] -= 1
                            self.leaf_pending[x].discard(v)
                            self.parked_pieces[x].add(v)
                            self.loc_pieces[c].add((x, v))
                            if self.exec_fold(f, x, v, pg, tk, c, duty=True):
                                return 'local'
                            self.parked_pieces[x].discard(v)
                            self.loc_pieces[c].discard((x, v))
                            self.leaf_pending[x].add(v)
                            f.xpending[x] += 1
                            f.duty[v].append(x)
                        break
                urgent = pr <= f.frontier
                if urgent and f.nfree <= self.load_reserve and not self.out_pending(f):
                    # registers full: an input of the earliest runnable nodes displaces the
                    # value used farthest ahead
                    self.evict(f, pr, (v,))
                if f.nfree > self.load_reserve + (0 if urgent else self.headroom):
                    r = self.load(f, v, pg, tk, c)
                    self.put_reg(f, v, r)
                    for x in f.duty.pop(v, ()):
                        self.become_piece(f, x, v)
                    return 'load'
        # 3. pieces lying here
        lp = self.loc_pieces.get(c)
        if lp:
            # a value that is a piece of several nodes this front is folding is loaded once
            byv = defaultdict(list)
            for (x, v) in sorted(lp):
                if x not in self.done and f.pieces.get(x):
                    byv[v].append(x)
            if byv:
                v, xs = max(byv.items(), key=lambda kv: (len(kv[1]), kv[0]))
                if len(xs) >= 2 and f.nfree > 1 and v not in f.regs_of:
                    r = self.load(f, v, pg, tk, c)
                    for x in xs:
                        self.parked_pieces[x].discard(v)
                        lp.discard((x, v))
                        f.need[v] += 1
                        f.pieces[x].append(v)
                    self.put_reg(f, v, r)
                    for x in xs:
                        self.queue_fold(f, x)
                    return 'load'
            for (x, v) in sorted(lp):
                if x in self.done:
                    lp.discard((x, v))
                    continue
                if f.pieces.get(x):
                    if self.exec_fold(f, x, v, pg, tk, c):
                        return 'absorb'
                elif x in f.xduty and f.nfree > 1 and not self.leaf_pending[x] and x not in f.piece_out:
                    # all leaves of x are pieces: pick one up and absorb the others in passing
                    r = self.load(f, v, pg, tk, c)
                    self.parked_pieces[x].discard(v)
                    lp.discard((x, v))
                    f.need[v] += 1
                    self.put_reg(f, v, r)
                    f.pieces[x].append(v)
                    self.queue_fold(f, x)
                    return 'load'
        # 4. park a value other work waits for
        if f.topark:
            v = min(f.topark, key=lambda z: (self.pri(z), z))
            s = self.free_scr(c, v)
            if s is not None:
                f.topark.discard(v)
                spilled = v in f.spill
                f.spill.discard(v)
                if v in f.regs_of and v not in self.parked and self.uses[v] > 0:
                    self.emit(f, pg, tk, c, M_OR, rule.K_SCR, min(f.regs_of[v]), d.C0, s, ('park', v))
                    self.stats['parks'] += 1
                    self.do_park(v, c, s)
                    if f.need.get(v, 0) <= 0:
                        self.free_regs(f, v)
                        f.need.pop(v, None)
                    elif spilled:
                        self.free_regs(f, v)
                    return 'park'
        # 5. a piece this front has nothing more to fold into: park it (or just let go of a
        #    leaf that lies at a cell anyway)
        for x in sorted(f.pieces):
            lst = f.pieces[x]
            if len(lst) == 1 and x not in self.done and (self.piece_idle(f, x) or x in f.piece_out):
                v = lst[0]
                f.piece_out.discard(x)
                if v in self.parked or v in d.lane_loc:
                    lst.remove(v)
                    self.parked_pieces[x].add(v)
                    self.loc_pieces[self.loc_cell(v)].add((x, v))
                    f.need[v] -= 1
                    if f.need[v] <= 0:
                        self.release(f, v)
                    self.version += 1
                    continue
                s = self.free_scr(c)
                if s is None or v not in f.regs_of:
                    break
                self.emit(f, pg, tk, c, M_OR, rule.K_SCR, min(f.regs_of[v]), d.C0, s, ('park-piece', x, v))
                self.stats['parks'] += 1
                lst.remove(v)
                self.piece_of.setdefault(v, x)
                self.do_park(v, c, s)
                self.parked_pieces[x].add(v)
                self.loc_pieces[c].add((x, v))
                f.topark.discard(v)
                f.need[v] -= 1
                if f.need[v] <= 0:
                    self.free_regs(f, v)
                    f.need.pop(v, None)
                return 'park'
        # 6. work on registers alone, in queue order
        tried = []
        res = None
        while f.ready and len(tried) < 6:
            item = heapq.heappop(f.ready)
            g = item[1]
            if isinstance(g, tuple):
                x = g[1]
                if x in self.done or len(f.pieces.get(x, ())) < 2:
                    f.in_ready.discard(g)
                    continue
                if self.exec_fold(f, x, None, pg, tk, c):
                    f.in_ready.discard(g)
                    self.queue_fold(f, x)
                    res = 'fold'
                    break
                tried.append(item)
                continue
            if g not in f.active:
                f.in_ready.discard(g)
                continue
            ok = self.exec_gate(f, g, pg, tk, c)
            if ok is False and self.evict(f, self.pri(g), d.mops[g][1:]):
                ok = self.exec_gate(f, g, pg, tk, c)
            if ok:
                f.in_ready.discard(g)
                res = 'gate'
                break
            if ok is None:
                f.in_ready.discard(g)       # an operand was given up: ready again when reloaded
                continue
            tried.append(item)
        for item in tried:
            heapq.heappush(f.ready, item)
        return res

    # ------------------------------------------------------------------ match pass
    def drained(self, f):
        return not (f.active or f.topark or f.nstores or f.wish or any(f.pieces.values()))

    def start_keyplace(self, f):
        for v in list(f.regs_of):
            assert f.need.get(v, 0) <= 0, ('live register at the match pass', v)
            self.free_regs(f, v)
        f.keyplace = dict(self.dag.key)

    def place_key(self, f, pg, tk, c):
        d = self.dag
        for r in sorted(f.keyplace):
            v = f.keyplace[r]
            pk = self.parked[v]
            if pk[0] == c:
                self.emit(f, pg, tk, c, M_OR, rule.K_REG, d.scr_code[pk[1]], d.C0, r, ('place', v))
                assert f.reg[r] is None
                f.reg[r] = v
                f.regs_of[v].add(r)
                f.nfree -= 1
                del f.keyplace[r]
                return True
        return False

    def after_match(self):
        """The match pass is over: registers are empty except front 0's fetched instruction."""
        d = self.dag
        f = self.fronts[0]
        for g in self.fronts:
            for v in list(g.regs_of):
                self.free_regs(g, v)
            g.draining = False
        f.keyplace = None
        for v in sorted(self.key_vals):
            self.use_done(v)
        for v, r in d.ibits.items():
            if self.uses[v] > 0:
                self.done.add(v)
                self.unparked.add(v)
                f.reg[r] = v
                f.regs_of[v].add(r)
                f.nfree -= 1
                f.topark.add(v)
        self.post_match = True
        # front 0 holds I: it computes what depends on I alone (the instruction decoders)
        job = d.pure_i & ~self.done_mask & ~self.claimed
        if job and self.pure_first:
            self.claim(f, job)
        self.version += 1

    # ------------------------------------------------------------------ main loop
    def run(self):
        p = self.p
        lo, hi, H, PL, F, dl = self.lo, self.hi, self.H, self.PL, self.F, p.delta
        f0 = self.fronts[0]
        self.MP = self.fixed_MP
        pg = 0
        while True:
            if pg > self.max_pages:
                raise CompileError(f'too many pages: {self.summary()}')
            if not self.post_match and self.MP is not None:
                if pg == self.MP - 1:
                    # last page before the match pass: front 0 collects the key
                    if f0.draining and self.drained(f0) and all(v in self.parked for v in self.key_vals):
                        self.start_keyplace(f0)
                    elif self.fixed_MP is not None:
                        raise CompileError(f'key not ready for match pass {self.MP}: {self.summary()}')
                    else:
                        self.MP += 2
                        self.MP_min = self.MP
                if pg == self.MP:
                    if not (all(f.draining and self.drained(f) for f in self.fronts)
                            and f0.keyplace is not None and not f0.keyplace):
                        if self.fixed_MP is not None:
                            raise CompileError(f'not drained at match pass {self.MP}: {self.summary()}')
                        # probe: try the next odd page; the fronts take up work again
                        self.MP += 2
                        self.MP_min = self.MP
                        for f in self.fronts[1:]:
                            f.draining = False
                    else:
                        self.T += PL
                        pg += 1
                        self.page_instr.append(0)
                        self.after_match()
                        continue
            n0 = self.stats['instr']
            for t in range(PL):
                if not self.post_match and self.keys_left == 0:
                    if self.MP_min is None:
                        # the key is complete: the match pass can be the next odd page that
                        # leaves front 0 time to drain and one page to collect the key
                        self.MP_min = pg + 2 if pg % 2 == 1 else pg + 3
                    if self.MP is None:
                        self.MP = self.MP_min
                    # front 0 gives its claims back in time to be drained before the last page;
                    # the other fronts work on and stop late in the last page, with everything
                    # they hold parked before the match pass
                    late = t >= PL - self.drain_ticks
                    if not f0.draining and (pg >= self.MP - 1 or (pg == self.MP - 2 and late)):
                        self.unclaim_all(f0)
                        f0.draining = True
                    if pg == self.MP - 1 and late and f0.keyplace is not None \
                            and not self.fronts[1].draining:
                        for f in self.fronts[1:]:
                            self.unclaim_all(f)
                            f.draining = True
                tt = t if pg % 2 == 0 else PL - 1 - t
                for j in (range(F - 1, -1, -1) if pg % 2 == 0 else range(F)):
                    c = lo - H + tt + j * dl
                    if not lo <= c < hi:
                        continue                    # in the overhang a front only carries its registers
                    f = self.fronts[j]
                    if not f.draining:
                        self.refill(f)
                        if f.scan_version != self.version or t % 8 == 0:
                            f.scan_version = self.version
                            self.scan(f)
                        if t % 16 == 0:
                            self.pickup_stores(f)
                    if self.act(f, pg, t, c) is None:
                        self.idle_why['drain' if f.draining else 'noreg' if f.ready else
                                      'gather' if f.wish else 'starved' if not f.active else 'wait'] += 1
                self.T += 1
            self.page_instr.append(self.stats['instr'] - n0)
            pg += 1
            if self.n_store_left == 0 and self.post_match:
                break
            if self.T - max(f.last_act for f in self.fronts) > 6 * PL:
                raise CompileError(f'stalled: {self.summary()}')
        self.NP = pg
        return self.prog

    def summary(self):
        return dict(post_match=self.post_match, MP=self.MP, stores_left=self.n_store_left,
                    keys_left=self.keys_left, done=len(self.done), nodes=len(self.dag.nodes),
                    active=[len(f.active) for f in self.fronts], wish=[len(f.wish) for f in self.fronts],
                    nfree=[f.nfree for f in self.fronts], topark=[len(f.topark) for f in self.fronts],
                    pieces=[sum(len(v) for v in f.pieces.values()) for f in self.fronts],
                    parked=len(self.parked), stats=dict(self.stats))

    def usage(self):
        """Pages the schedule needs: NPe (T_sig is one free page after the flag stores), the
        match pass and the number of passes."""
        return dict(NPe=self.NPe_page + 2, MP=self.MP, NP=self.NP, MP_min=self.MP_min)


def replay(p, eng, seed=0, inputs=None):
    """Execute the listing of a finished Engine on 64 input vectors at once: random ones, or
    `inputs` (netlist input name -> uint64, bit v = the input's value in vector v; see
    `neighbourhood_vectors`). Checks every register, scratch and Hold write of a netlist
    node against the netlist, the key in front 0's registers at the match pass, and every
    Hold target. Reads of an empty register or scratch bit raise. Returns the number of
    mismatches.

    Random inputs almost never raise the rare signals (a front arriving, the match pass);
    neighbourhoods taken from a running colony do."""
    from .netlist import AND as G_AND, OR as G_OR
    d = eng.dag
    comp = d.comp
    rng = np.random.default_rng(seed)
    node = [np.uint64(0), np.uint64(2**64 - 1)]
    for name in comp.inputs:
        node.append(rng.integers(0, 2**63, dtype=np.uint64) if inputs is None else np.uint64(inputs[name]))
    for op, a, b in comp.gates:
        x, y = node[a], node[b]
        node.append(x & y if op == G_AND else (x | y if op == G_OR else x ^ y))
    n_orig = len(node)
    names = p.fam().source_names(p)
    at = {(cell, code): v for v, (cell, code) in d.lane_loc.items()}
    F = eng.F
    regs = [[None] * p.L for _ in range(F)]
    scratch, hold = {}, {}
    ops = {M_AND: lambda x, y: x & y, M_OR: lambda x, y: x | y,
           M_XOR: lambda x, y: x ^ y, M_ANDN: lambda x, y: x & ~y}
    bad = 0
    matched = False
    used = set()
    for (seq, page, tick, j, cell, op, kind, a, b, dd, note) in eng.prog.listing:
        assert (j, page, cell) not in used and page != eng.MP
        used.add((j, page, cell))
        if not matched and page > eng.MP:
            matched = True
            for r, v in d.key.items():
                if regs[0][r] is None or regs[0][r] != node[v]:
                    bad += 1
            regs = [[None] * p.L for _ in range(F)]
            for v, r in d.ibits.items():
                regs[0][r] = node[v]

        def src(code):
            if code < p.L:
                x = regs[j][code]
                assert x is not None, ('empty register', seq, j, code, note)
                return x
            nm = names[code]
            if nm == ('const', 0):
                return np.uint64(0)
            if nm == ('const', 1):
                return np.uint64(2**64 - 1)
            if nm[0] == 'scr':
                return scratch[(cell, nm[1])]
            return node[at[(cell, code)]]
        x = ops[op](src(a), src(b))
        vid = note[-1]
        if vid < n_orig and x != node[vid]:
            bad += 1
        if kind == rule.K_REG:
            regs[j][dd] = x
        elif kind == rule.K_SCR:
            scratch[(cell, dd)] = x
        elif kind == rule.K_HOLD:
            hold[cell] = x
    for v, cell in d.flags + d.holds:
        if cell not in hold or hold[cell] != node[v]:
            bad += 1
    return bad


def neighbourhood_vectors(cand, X, cells):
    """Inputs for `replay` from a physical state: vector v is the radius-5 neighbourhood of
    cell cells[v] in state X (fields x rows, a ring), with the instruction word the rule
    looks up there. At most 64 cells."""
    comp, p = cand.comp, cand.p
    cells = np.asarray(cells)
    assert len(cells) <= 64
    N = X.shape[1]
    vals = {}
    for name in comp.inputs:
        if name[0] == 'x':
            _, j, f, i = name
            vals[name] = X[cand.row[(f, i)], (cells + j) % N]
        else:
            vals[name] = np.zeros(len(cells), dtype=bool)
    out = comp.evaluate(vals, bool)                 # psel and laddr do not depend on I
    psel = sum(out[('psel', i)].astype(np.int64) << i for i in range(p.PW))
    if ('laddr', 0) in out:
        addr = sum(out[('laddr', i)].astype(np.int64) << i for i in range(p.k))
    else:
        addr = sum(vals[('x', 0, 'addr', i)].astype(np.int64) << i for i in range(p.k))
    word = cand.rom[addr % p.Q, psel].astype(np.int64)
    for i in range(p.IW):
        vals[('I', i)] = ((word >> i) & 1).astype(bool)
    weights = np.uint64(1) << np.arange(len(cells), dtype=np.uint64)
    return {name: np.uint64((v.astype(np.uint64) * weights).sum()) for name, v in vals.items()}


def probe(p, layout, check=True, **opts):
    """Compile with a free match pass; returns (usage, engine). p should have generous
    NPe/MP/NP (they only enter the netlist as constants)."""
    comp = p.fam().cached(p)[1]
    eng = Engine(p, comp, layout, **opts)
    eng.run()
    if check and replay(p, eng):
        raise CompileError('replay mismatch')
    return eng.usage(), eng


def compile_program(p, layout, check=True, **opts):
    """The ROM of a candidate whose params fix NPe, MP and NP: the flag stores must be done
    one page before T_sig, the match pass is page MP, and everything ends within NP passes.
    Front j's instruction for page pg at a cell is Pi[cell][pg + (j << logNP)]."""
    comp = p.fam().cached(p)[1]
    eng = Engine(p, comp, layout, MP=p.MP, **opts)
    eng.run()
    use = eng.usage()
    if use['NPe'] > p.NPe or use['NP'] > p.NP:
        raise CompileError(f'schedule needs {use}, candidate has NPe={p.NPe} MP={p.MP} NP={p.NP}')
    if check:
        bad = replay(p, eng)
        if bad:
            raise CompileError(f'replay mismatch ({bad})')
    prog = compiler.Program(p, layout)
    for (seq, page, tick, j, cell, op, kind, a, b, dd, note) in eng.prog.listing:
        prog.put(page + (j << p.logNP), cell, op, kind, a, b, dd, note)
    prog.stats = dict(usage=use, instr=eng.stats['instr'], gates=eng.stats['gates'] + eng.stats['folds'],
                      loads=eng.stats['loads'], parks=eng.stats['parks'], evictions=eng.stats['evictions'],
                      max_parked=eng.stats['max_parked'], page_instr=eng.page_instr,
                      idle=dict(eng.idle_why))
    return prog
