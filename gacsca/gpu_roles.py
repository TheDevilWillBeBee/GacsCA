"""A faster CUDA kernel for one large ring of a comb candidate (G13 and later).

It runs the same netlist as `gpu.py` and is compared with it bit for bit in
the tests. It has no error injection and handles one ring; `gpu.GpuSim`
remains the reference backend.

Two things make it faster.

Skipping the comb's logic where no front arrives. The gates outside the cone
of the non-front outputs and of `arrive` (set Z: operand selection, the ALU,
the register update, the Pi lookup; 60% of G16's netlist) matter only at a
site a front arrives at. A block computes `arrive` for its 32 words; if it
is zero in all of them, the block does not evaluate Z and writes zeros to the
front fields (reg, pend, pkind, pval). That is the netlist with arrive = 0:
`check_guard` verifies when the kernel is built that those outputs are the
constant 0 there. Otherwise the block evaluates the whole netlist.

Several threads per word. A block is 32 lanes x P roles, one warp per role.
Lane i of every warp works on the same 32-site word, and role r evaluates
the gates homed at r. A value one role computes for another goes through a
shared-memory slot, written during a stage and read from the next stage on;
stages end with __syncthreads(). Every gate of the netlist is evaluated as it
stands: `Partition` only decides who evaluates it, and when.

Layout. The state is stored as [row][word position in the colony][colony],
so the 32 lanes of a block hold the same word position of 32 colonies. In a
healthy ring the comb is at the same place in every colony, so a block is
either all "no front" or all "front". The host permutes on upload and
download. The ring must have a multiple of 32 colonies.

What the GPU does with it (RTX 4090, G16, one level-2 cell = 8,192 words;
REPORT section 30):
  * `gpu.py`'s kernel, one thread per word: 37 us per tick during the
    gathers, 41 during the program. Three quarters of the GPU are idle: a
    warp executes its 18,000 instructions one after the other.
  * this kernel: 8.4 and 18.5 us.
  * Warps that run the same code run in parallel, up to four per
    multiprocessor at full speed. Warps that run different code get in each
    other's way: with five different streams a multiprocessor is barely
    faster than with one. So more roles do not help beyond about six.
  * Loads are compiled for one ring size (`NW` is a constant): otherwise
    address arithmetic is a third of the instructions.
"""
import collections
import ctypes
import hashlib
import heapq
import os
import subprocess
import numpy as np
from .machine import BUILD
from .netlist import Net, Compiled, OR
from .gpu import NVCC

FRONT_FIELDS = ('reg', 'pend', 'pkind', 'pval')


def check_guard(cand):
    """The claim the skip rests on: with every per-slot arrival forced to 0, the front outputs
    are the constant 0. Raises if not."""
    comp = cand.comp
    n_in = 2 + len(comp.inputs)
    G = comp.gates
    leaves, stack = set(), [comp.outputs[('arrive', 0)]]
    while stack:                                   # the OR tree under `arrive`
        x = stack.pop()
        g = G[x - n_in] if x >= n_in else None
        if g is not None and g[0] == OR:
            stack += [g[1], g[2]]
        else:
            leaves.add(x)
    net = Net()
    m = {0: 0, 1: 1}
    for i, name in enumerate(comp.inputs):
        m[2 + i] = net.input(name)
    for g, (op, a, b) in enumerate(G):
        x = n_in + g
        m[x] = 0 if x in leaves else net.op(op, m[a], m[b])
    assert m[comp.outputs[('arrive', 0)]] == 0
    for (f, i) in cand.rows:
        if f in FRONT_FIELDS and m[comp.outputs[('y', f, i)]] != 0:
            raise ValueError(f'output ({f}, {i}) is not 0 when no front arrives: the skip is not valid')


def default_territories(cand):
    """Six roles. 0: the core (Address, Age, flags and every control signal). 1: info, hold, mail,
    scratch, and the pending-write fields. 2, 3: the history lanes with negative / positive
    offset, and 3/16 of the registers each. 4, 5: 5/16 of the registers each. Every stored row is
    then read by one role."""
    from .rule import LANE_OFFSETS
    from .rule_g import logical_width
    p = cand.p
    cut = [3 * p.L // 16, 6 * p.L // 16, 11 * p.L // 16]
    terr = {}
    for r, (f, i) in enumerate(cand.rows):
        if f in ('addr', 'age', 'f1', 'f2', 'wf1', 'wf2'):
            terr[r] = 0
        elif f == 'reg':
            terr[r] = 2 + sum(i >= c for c in cut)
        elif f in ('pend', 'pkind', 'pval'):
            terr[r] = 1
        elif f in ('h1', 'h2'):
            terr[r] = 2 if LANE_OFFSETS[i % logical_width(f, p)] < 0 else 3
        else:
            terr[r] = 1
    return terr


class Partition:
    """Homes, stages and slots for the gates of a candidate's netlist.

    terr: output row -> role. Role `core` computes `arrive` and the Pi key."""

    def __init__(self, cand, terr=None, tdup=120, core=0):
        self.cand, self.comp, self.p = cand, cand.comp, cand.p
        comp, p = self.comp, self.p
        self.n_in = n_in = 2 + len(comp.inputs)
        self.G = G = comp.gates
        self.N = N = comp.n_nodes
        idx = comp.index
        self.name_of = name_of = {node: nm for nm, node in idx.items()}
        self.I_nodes = [idx.get(('I', i)) for i in range(p.IW)]
        self.I_set = {x for x in self.I_nodes if x is not None}
        self.arrive = comp.outputs[('arrive', 0)]
        self.key = ([comp.outputs[('psel', i)] for i in range(p.PW)]
                    + [comp.outputs[('laddr', i)] for i in range(p.k)])
        self.y = [comp.outputs[('y', f, i)] for (f, i) in cand.rows]
        self.terr = dict(terr if terr is not None else default_territories(cand))
        self.core, self.tdup = core, tdup
        self.P = max(self.terr.values()) + 1
        self.cons = [[] for _ in range(N)]
        cone = [0] * N                     # gates in the cone
        cone_in = [0] * N                  # inputs in the cone
        for i in range(n_in - 2):
            cone_in[2 + i] = 1 << i
        for g, (op, a, b) in enumerate(G):
            x = n_in + g
            self.cons[a].append(x)
            if b != a:
                self.cons[b].append(x)
            cone[x] = cone[a] | cone[b] | (1 << g)
            cone_in[x] = cone_in[a] | cone_in[b]
        self.cs = [bin(m).count('1') for m in cone]
        # Z: live gates outside the cone of (non-front outputs, arrive)
        live = 0
        for x in self.y + self.key + [self.arrive]:
            live |= cone[x]
        self.front_rows = {r for r, (f, i) in enumerate(cand.rows) if f in FRONT_FIELDS}
        keep = cone[self.arrive]
        for r, x in enumerate(self.y):
            if r not in self.front_rows:
                keep |= cone[x]
        self.Z = [False] * N
        for g in range(len(G)):
            if (live >> g) & 1 and not (keep >> g) & 1:
                self.Z[n_in + g] = True
        for r in self.front_rows:
            x = self.y[r]
            assert x == 0 or (x >= n_in and self.Z[x]), 'a front output outside Z'
        # The core's region. Unguarded: gates whose inputs all lie in the fields `arrive` depends
        # on (the computed Address and Age and every control signal derived from them alone).
        # Guarded: the cone of the Pi key.
        ctrl_fields = {name_of[2 + i][2] for i in range(n_in - 2) if (cone_in[self.arrive] >> i) & 1}
        cmask = 0
        for i in range(n_in - 2):
            nm = name_of[2 + i]
            if nm[0] == 'x' and nm[2] in ctrl_fields:
                cmask |= 1 << i
        key_cone = 0
        for x in self.key:
            key_cone |= cone[x]
        self.ctrl = [False] * N
        self.key_cone = [False] * N
        for g in range(len(G)):
            x = n_in + g
            if not (live >> g) & 1:
                continue
            if cone_in[x] & ~cmask == 0 and not self.Z[x]:
                self.ctrl[x] = True
            elif (key_cone >> g) & 1:
                self.key_cone[x] = True
        # Front work is homed by its inputs: a Z gate that depends on the stored bits of one role
        # only lives there (register i: the role of output reg[i]; the operand lanes and the
        # pending-write fields: the role of the pend output). Control fields and I do not count.
        lane_role = self.terr[cand.row[('pend', 0)]]
        masks = collections.defaultdict(int)
        for i in range(n_in - 2):
            nm = name_of[2 + i]
            if nm[0] != 'x' or nm[2] in ctrl_fields:
                continue
            role = self.terr[cand.row[('reg', nm[3])]] if nm[2] == 'reg' else lane_role
            masks[role] |= 1 << i
        self.zrole = [None] * N
        for g in range(len(G)):
            x = n_in + g
            if self.Z[x] and not self.key_cone[x]:
                touched = [r for r in sorted(masks) if cone_in[x] & masks[r]]
                if len(touched) == 1:
                    self.zrole[x] = touched[0]
        del cone, cone_in
        self._home()
        self._stages()

    def _home(self):
        """Consumers first. A role needs x *unguarded* if one of its unguarded gates, a non-front
        output or (core) `arrive` uses it, and *guarded* if only its Z work does.
          * Z gates: by their inputs (zrole), the core for the Pi key cone, else by consumers.
          * Other gates live only where they are needed unguarded; Z work elsewhere reads them
            from a slot. The core owns its region.
          * Needed by several roles: a small cone is duplicated, a large one gets one owner."""
        n_in, N, core, tdup = self.n_in, self.N, self.core, self.tdup
        home = [frozenset()] * N
        owner = [-1] * N
        guarded = [frozenset()] * N
        load = collections.Counter()
        need_u, need_g = collections.defaultdict(set), collections.defaultdict(set)
        for r, x in enumerate(self.y):
            (need_g if r in self.front_rows else need_u)[x].add(self.terr[r])
        need_u[self.arrive].add(core)
        for x in self.key:
            need_g[x].add(core)

        def place(x, H, forced):
            if forced is not None:
                if len(H - {forced}) == 0 or self.cs[x] <= tdup:
                    home[x] = frozenset(H | {forced})
                else:
                    home[x] = frozenset([forced])
                    owner[x] = forced
            elif len(H) == 1 or self.cs[x] <= tdup:
                home[x] = frozenset(H)
            else:
                best = max(votes[r] for r in H)
                o = min((r for r in H if votes[r] == best), key=lambda r: (load[r], r))
                home[x] = frozenset([o])
                owner[x] = o
                load[o] += self.cs[x]

        for x in range(N - 1, n_in - 1, -1):
            Hu, Hg = set(need_u.get(x, ())), set(need_g.get(x, ()))
            votes = collections.Counter(Hu | Hg)
            for c in self.cons[x]:
                for r in home[c]:
                    votes[r] += 1
                    (Hg if r in guarded[c] else Hu).add(r)
            if not Hu and not Hg:
                continue                                    # dead gate
            if self.Z[x]:
                if self.zrole[x] is not None:
                    home[x] = frozenset([self.zrole[x]])
                    owner[x] = self.zrole[x]
                else:
                    place(x, Hu | Hg, core if self.key_cone[x] else None)
                guarded[x] = home[x]
            else:
                assert Hu, 'a gate of the light cone that nobody needs unguarded'
                place(x, Hu, core if self.ctrl[x] else None)
        self.home, self.owner, self.guarded = home, owner, guarded

    def pub_owner(self, y):
        if y in self.I_set:
            return self.core
        return self.owner[y] if self.owner[y] >= 0 else min(self.home[y])

    def avail(self, y, r):
        """(how role r gets y, first stage in which it can use it)."""
        if y < 2:
            return 'const', 1
        if y < self.n_in:
            if y in self.I_set:              # looked up by the core at the end of rom_stage
                return ('own' if r == self.core else 'pub'), self.rom_stage + 1
            return 'in', 1
        if r in self.home[y]:
            return 'own', self.st[y][r]
        return 'pub', self.st[y][self.pub_owner(y)] + 1

    def _stages(self):
        n_in, G, N = self.n_in, self.G, self.N
        home, guarded = self.home, self.guarded
        self.st = st = [None] * N
        self.rom_stage, self.sG = 0, 0
        for _ in range(3):                   # sG and rom_stage settle in two rounds
            for g, (op, a, b) in enumerate(G):
                x = n_in + g
                if not home[x]:
                    continue
                d = {}
                for r in home[x]:
                    s = max(self.avail(a, r)[1], self.avail(b, r)[1])
                    if r in guarded[x]:
                        s = max(s, self.sG + 1)      # guarded work waits for the guard
                    d[r] = s
                st[x] = d
            self.sG = self.avail(self.arrive, self.core)[1]
            self.rom_stage = max([self.avail(x, self.core)[1] for x in self.key] + [self.sG + 1])
        steps = collections.defaultdict(list)        # (role, stage) -> gates
        readers = collections.defaultdict(set)       # published node -> stages in which it is read

        def use(y, r, s):
            if self.avail(y, r)[0] == 'pub':
                readers[y].add(s)
        for g, (op, a, b) in enumerate(G):
            x = n_in + g
            for r in home[x]:
                steps[(r, st[x][r])].append(x)
                use(a, r, st[x][r])
                use(b, r, st[x][r])
        for x in self.key + [self.arrive]:
            use(x, self.core, self.rom_stage)
        outs = collections.defaultdict(list)          # (role, stage) -> (row, node)
        for row, x in enumerate(self.y):
            r = self.terr[row]
            s = self.avail(x, r)[1]
            if row in self.front_rows:
                s = max(s, self.sG + 1)
            outs[(r, s)].append((row, x))
            use(x, r, s)
        self.S = max([s for (_, s) in steps] + [s for (_, s) in outs] + [self.rom_stage])
        # Slots. A value is written during stage w and read in stages w+1 .. l; a slot is free
        # again for a write in stage w' only if its last read was before w'.
        iv = []
        for y, rs in readers.items():
            w = self.rom_stage if y in self.I_set else st[y][self.pub_owner(y)]
            assert min(rs) > w, (y, w, rs)
            iv.append((w, max(rs), y))
        iv.sort()
        slot, free, busy, n = {}, [], [], 0
        for w, l, y in iv:
            while busy and busy[0][0] < w:
                heapq.heappush(free, heapq.heappop(busy)[1])
            if free:
                sl = heapq.heappop(free)
            else:
                sl, n = n, n + 1
            slot[y] = sl
            heapq.heappush(busy, (l, sl))
        self.steps, self.outs, self.slot, self.nslots = steps, outs, slot, n
        wl, wh = collections.Counter(), collections.Counter()
        for (r, s), xs in steps.items():
            wh[(r, s)] += len(xs)
            wl[(r, s)] += sum(r not in guarded[x] for x in xs)
        self.summary = dict(
            roles=self.P, stages=self.S, guard_stage=self.sG, rom_stage=self.rom_stage, slots=n,
            gates_no_front=sum(wl.values()), gates_front=sum(wh.values()),
            by_role_no_front=[sum(wl[(r, s)] for s in range(1, self.S + 1)) for r in range(self.P)],
            by_role_front=[sum(wh[(r, s)] for s in range(1, self.S + 1)) for r in range(self.P)])


def _stage_order(pt, xs):
    """Gates of one (role, stage) in DFS postorder from their local roots (short live ranges)."""
    n_in, G = pt.n_in, pt.G
    inset = set(xs)
    inner = set()
    for x in xs:
        for y in G[x - n_in][1:]:
            if y in inset:
                inner.add(y)
    done, out = set(), []
    for root in (x for x in xs if x not in inner):
        stack = [(root, False)]
        while stack:
            x, expanded = stack.pop()
            if x in done or x not in inset:
                continue
            if expanded:
                done.add(x)
                out.append(x)
                continue
            stack.append((x, True))
            _, a, b = G[x - n_in]
            stack.append((b, False))
            stack.append((a, False))
    assert len(out) == len(xs)
    return out


def _kernel(pt, NW, batch=96):
    """The kernel for a ring of NW 32-bit words (compiled in: loads then need no address
    arithmetic). batch: the state words that a stretch of this many gates reads are loaded
    together at its start, so that the loads overlap."""
    comp, p, cand = pt.comp, pt.p, pt.cand
    n_in, G, name_of = pt.n_in, pt.G, pt.name_of
    P, S, core, sG, rom_stage = pt.P, pt.S, pt.core, pt.sG, pt.rom_stage
    ops = {0: '&', 1: '|', 2: '^'}
    pub_w = collections.defaultdict(list)
    for y in pt.slot:
        o = pt.pub_owner(y)
        pub_w[(o, rom_stage if y in pt.I_set else pt.st[y][o])].append(y)
    I_core = [x for x in pt.I_nodes if x is not None]
    L = []
    emit = L.append

    def gen(r, stages, mode, words):
        """Lines of role r for `stages`. mode 'pre': before the guard is known (no guarded work
        exists there); 'light': no front in the block; 'heavy': everything."""
        lines = []
        words = dict(words)
        for s in stages:
            segs = [[[], []]]                      # [loads, code] per stretch of `batch` gates
            local = {}

            def word(row, which):
                if (row, which) not in words:
                    nm = f'L{row}{which}'
                    segs[-1][0].append(f'const wd {nm} = X{which}[{row * NW}];')
                    words[(row, which)] = nm
                return words[(row, which)]

            def ref(y):
                if y == 0:
                    return '0u'
                if y == 1:
                    return '0xFFFFFFFFu'
                kind, _ = pt.avail(y, r)
                if kind == 'own':
                    return f'v{y}'
                if y in local:
                    return local[y]
                nm = f'v{y}_{s}'
                if kind == 'pub':
                    e = f'pub[{pt.slot[y]}][lane]'
                else:
                    _, j, f, i = name_of[y]
                    row = cand.row[(f, i)]
                    if j == 0:
                        e = word(row, 'w')
                    elif j > 0:
                        e = f'(({word(row, "w")} >> {j}) | ({word(row, "wr")} << {32 - j}))'
                    else:
                        e = f'(({word(row, "w")} << {-j}) | ({word(row, "wl")} >> {32 + j}))'
                segs[-1][1].append(f'const wd {nm} = {e};')
                local[y] = nm
                return nm

            xs = [x for x in pt.steps.get((r, s), ()) if mode != 'light' or r not in pt.guarded[x]]
            assert mode != 'pre' or all(r not in pt.guarded[x] for x in xs)
            for k, x in enumerate(_stage_order(pt, xs)):
                if k and k % batch == 0:
                    segs.append([[], []])
                op, a, b = G[x - n_in]
                ea, eb = ref(a), ref(b)
                segs[-1][1].append(f'const wd v{x} = {ea} {ops[op]} {eb};')
            code = segs[-1][1]
            if r == core and s == sG:
                code.append(f'{{ const int any = __any_sync(0xffffffffu, {ref(pt.arrive)} != 0u); '
                            'if (lane == 0) front = (unsigned)any; }')
            if r == core and s == rom_stage and mode == 'heavy':
                arrive = ref(pt.arrive)
                la = [ref(comp.outputs[('laddr', i)]) for i in range(p.k)]
                ps = [ref(comp.outputs[('psel', i)]) for i in range(p.PW)]
                code.append(f'{{ wd arr = {arrive};')
                code.append('  while (arr) { const int t = __ffs(arr) - 1; arr &= arr - 1; unsigned a = 0, ps = 0;')
                for i, e in enumerate(la):
                    code.append(f'    a |= (({e} >> t) & 1u) << {i};')
                for i, e in enumerate(ps):
                    code.append(f'    ps |= (({e} >> t) & 1u) << {i};')
                code.append('    const uint32_t word = rom[a * NPT + ps];')
                for i, x in enumerate(pt.I_nodes):
                    if x is not None:
                        code.append(f'    v{x} |= ((word >> {i}) & 1u) << t;')
                code.append('  } }')
            for (row, x) in pt.outs.get((r, s), ()):
                if row in pt.front_rows and mode == 'light':
                    code.append(f'Yw[{row * NW}] = 0u;')
                else:
                    assert not (row in pt.front_rows and mode == 'pre')
                    code.append(f'Yw[{row * NW}] = {ref(x)};')
            for y in pub_w.get((r, s), ()):
                is_guarded = (y in pt.I_set) or (r in pt.guarded[y])
                if mode == 'light' and is_guarded:
                    continue
                assert not (mode == 'pre' and is_guarded)
                code.append(f'pub[{pt.slot[y]}][lane] = v{y};')
            lines.append(f'// stage {s} ({mode})')
            lines += [ln for loads, body in segs for ln in loads + body]
            lines.append('__syncthreads();')
        return lines, words

    emit(f'#define RL_P {P}')
    emit(f'#define RL_NPUB {max(1, pt.nslots)}')
    emit(f'#define RL_NW {NW}')
    emit(f'extern "C" __global__ void __launch_bounds__({32 * P}, 2) k_roles(wd* A, wd* B,')
    emit('                                 const uint32_t* __restrict__ rom, long ticks, int NC, int WPC) {')
    emit('  cg::grid_group grid = cg::this_grid();')
    emit('  __shared__ wd pub[RL_NPUB][32];')
    emit('  __shared__ unsigned front;')
    emit('  const int lane = threadIdx.x % 32, role = threadIdx.x / 32;')
    emit('  int flip = 0;')
    emit('  for (long tick = 0; tick < ticks; tick++) {')
    emit('    const wd* __restrict__ X = flip ? B : A;')
    emit('    wd* __restrict__ Y = flip ? A : B;')
    emit('    for (int chunk = blockIdx.x; chunk < RL_NW / 32; chunk += gridDim.x) {')
    emit('      const int w = chunk * 32 + lane, wpos = w / NC, col = w % NC;')
    emit('      const int wl = wpos > 0 ? w - NC : (WPC - 1) * NC + (col == 0 ? NC - 1 : col - 1);')
    emit('      const int wr = wpos < WPC - 1 ? w + NC : (col + 1 == NC ? 0 : col + 1);')
    emit('      const wd* __restrict__ Xw = X + w; const wd* __restrict__ Xwl = X + wl; const wd* __restrict__ Xwr = X + wr;')
    emit('      wd* __restrict__ Yw = Y + w;')
    emit('      switch (role) {')
    for r in range(P):
        emit(f'      case {r}: {{')
        pre, words = gen(r, range(1, sG + 1), 'pre', {})
        for ln in pre:
            emit('        ' + ln)
        # every thread of the block takes the same branch, so both sides may use the barrier
        emit('        if (front) {')
        if r == core and I_core:
            emit('          wd ' + ', '.join(f'v{x} = 0u' for x in I_core) + ';')
        for ln in gen(r, range(sG + 1, S + 1), 'heavy', words)[0]:
            emit('          ' + ln)
        emit('        } else {')
        for ln in gen(r, range(sG + 1, S + 1), 'light', words)[0]:
            emit('          ' + ln)
        emit('        }')
        emit('      } break;')
    emit('      }')
    emit('    }')
    emit('    grid.sync();')
    emit('    flip ^= 1;')
    emit('  }')
    emit('  if (flip) {')
    emit('    const long gid = (long)blockIdx.x * blockDim.x + threadIdx.x, gsz = (long)gridDim.x * blockDim.x;')
    emit('    for (long g = gid; g < (long)RL_NW * W; g += gsz) A[g] = B[g];')
    emit('  }')
    emit('}')
    return '\n'.join(L) + '\n'


_HOST = r'''
struct RSim { wd *A, *B; uint32_t* rom; };
extern "C" void* rs_create(const unsigned int* rom_host, int rom_words) {
  RSim* s = new RSim;
  size_t bytes = (size_t)W * RL_NW * sizeof(wd);
  if (cudaMalloc(&s->A, bytes) || cudaMalloc(&s->B, bytes) || cudaMalloc(&s->rom, rom_words * 4)) return 0;
  cudaMemcpy(s->rom, rom_host, rom_words * 4, cudaMemcpyHostToDevice);
  return s;
}
extern "C" void rs_upload(void* h, const wd* host) {
  cudaMemcpy(((RSim*)h)->A, host, (size_t)W * RL_NW * sizeof(wd), cudaMemcpyHostToDevice);
}
extern "C" void rs_download(void* h, wd* host) {
  cudaMemcpy(host, ((RSim*)h)->A, (size_t)W * RL_NW * sizeof(wd), cudaMemcpyDeviceToHost);
}
extern "C" int rs_max_blocks() {
  int per_sm = 0, dev = 0, sms = 0;
  cudaOccupancyMaxActiveBlocksPerMultiprocessor(&per_sm, k_roles, 32 * RL_P, 0);
  cudaGetDevice(&dev);
  cudaDeviceGetAttribute(&sms, cudaDevAttrMultiProcessorCount, dev);
  return per_sm * sms;
}
extern "C" int rs_run(void* h, long ticks, int blocks, int NC, int WPC, float* ms) {
  RSim* s = (RSim*)h;
  cudaEvent_t e0, e1; cudaEventCreate(&e0); cudaEventCreate(&e1);
  cudaEventRecord(e0);
  void* args[] = {&s->A, &s->B, &s->rom, &ticks, &NC, &WPC};
  cudaLaunchCooperativeKernel((void*)k_roles, blocks, 32 * RL_P, args, 0, 0);
  cudaEventRecord(e1); cudaEventSynchronize(e1);
  cudaEventElapsedTime(ms, e0, e1);
  int err = (int)cudaGetLastError();
  cudaEventDestroy(e0); cudaEventDestroy(e1);
  return err;
}
extern "C" void rs_destroy(void* h) {
  RSim* s = (RSim*)h; cudaFree(s->A); cudaFree(s->B); cudaFree(s->rom); delete s;
}
'''


def source(cand, NW, terr=None, tdup=120, batch=96):
    pt = Partition(cand, terr, tdup)
    head = ('#include <stdint.h>\n#include <cooperative_groups.h>\nnamespace cg = cooperative_groups;\n'
            f'typedef uint32_t wd;\n#define W {cand.W}\n#define NPT {cand.p.NPT}\n')
    return head + _kernel(pt, NW, batch) + _HOST, pt


def build(cand, NW, **kw):
    check_guard(cand)
    src, pt = source(cand, NW, **kw)
    flags = ['-O3', '-arch=sm_80', '-shared', '-Xcompiler', '-fPIC']
    tag = hashlib.sha256((src + ' '.join(flags)).encode()).hexdigest()[:16]
    os.makedirs(BUILD, exist_ok=True)
    cu = os.path.join(BUILD, f'gpuroles_{tag}.cu')
    so = os.path.join(BUILD, f'gpuroles_{tag}.so')
    if not os.path.exists(so):
        with open(cu, 'w') as fh:
            fh.write(src)
        tmp = so + f'.tmp{os.getpid()}'
        subprocess.run([NVCC] + flags + [cu, '-o', tmp], check=True)
        os.replace(tmp, so)
    lib = ctypes.CDLL(so)
    lib.rs_create.restype = ctypes.c_void_p
    lib.rs_create.argtypes = [ctypes.c_void_p, ctypes.c_int]
    lib.rs_upload.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    lib.rs_download.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    lib.rs_run.argtypes = [ctypes.c_void_p, ctypes.c_long, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                           ctypes.POINTER(ctypes.c_float)]
    lib.rs_destroy.argtypes = [ctypes.c_void_p]
    return lib, pt, hashlib.sha256(src.encode()).hexdigest()


class RoleSim:
    """One ring of `colonies` colonies on the GPU (a multiple of 32; Q a multiple of 32).

    set_state / state take and return the packed state of `machine.CKernel.pack`, shape
    (W, N / 64) uint64, in the natural site order."""

    def __init__(self, cand, colonies, **kw):
        p = cand.p
        if p.Q % 32 or colonies % 32:
            raise ValueError('RoleSim needs Q and the number of colonies to be multiples of 32')
        self.cand, self.p = cand, p
        self.N = colonies * p.Q
        self.NW = self.N // 32                       # 32-bit words
        self.NC, self.WPC = colonies, p.Q // 32
        self.lib, self.partition, self.source_sha256 = build(cand, self.NW, **kw)
        self.blocks = min(self.lib.rs_max_blocks(), self.NW // 32)
        rom = np.ascontiguousarray(cand.rom, dtype=np.uint32)
        self.h = self.lib.rs_create(rom.ctypes.data, rom.size)
        if not self.h:
            raise RuntimeError('CUDA allocation failed')
        i = np.arange(self.NW)
        self.perm = (i % self.NC) * self.WPC + (i // self.NC)    # natural index of permuted index i
        self.t = 0
        self.last_ms = 0.0

    def __del__(self):
        if getattr(self, 'h', None):
            self.lib.rs_destroy(self.h)
            self.h = None

    def set_state(self, packed, t=0):
        P = np.ascontiguousarray(packed, dtype=np.uint64)
        assert P.shape == (self.cand.W, self.NW // 2)
        A = np.ascontiguousarray(P.view(np.uint32)[:, self.perm])
        self.lib.rs_upload(self.h, A.ctypes.data)
        self.t = t

    def state(self):
        A = np.empty((self.cand.W, self.NW), dtype=np.uint32)
        self.lib.rs_download(self.h, A.ctypes.data)
        out = np.empty_like(A)
        out[:, self.perm] = A
        return out.view(np.uint64)

    def run(self, ticks):
        ms = ctypes.c_float()
        err = self.lib.rs_run(self.h, ticks, self.blocks, self.NC, self.WPC, ctypes.byref(ms))
        if err:
            raise RuntimeError(f'CUDA error {err}')
        self.t += ticks
        self.last_ms = ms.value
