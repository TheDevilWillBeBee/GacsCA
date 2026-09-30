"""The bit-level fixed rule M'0 of the "front" candidate family.

One physical cell has the fields listed in `schema(params)`. Hierarchy depth
is not a field and not a parameter. A candidate is fixed by `Params`; a
different Params value is a different fixed candidate, never a level kernel.

Per tick every cell:
  * applies Gray section 5.2 local structure (candidate-B maintenance,
    radius five) to obtain computed Address/Age and new Flag1/Flag2;
  * gathers: at computed Age 0 both mail tracks load Info; afterwards mail
    shifts one cell per tick and lane[-d]/lane[+d] capture the passing bit
    at Age d*Q+1, so lane n holds the Info bit of the same address in the
    colony n steps away;
  * runs a register-file *front* during the evaluation window: the front
    sweeps the colony boustrophedon, one cell per tick, and at every arrival
    executes the cell's own instruction I, a 20-bit word looked up as
    Pi[stored Address][psel];
  * during the match pass the front executes no instruction: the cell whose
    stored Address equals R[0:k] loads its instruction, looked up with the
    page carried in R[k:k+log NP], into R[k:k+IW]. This is Gray's
    hard-wiring step: the colony obtains the upper cell's ProgramBit from
    the physical cell with the matching Address;
  * commits Hold into Info at computed Age U-1.

The instruction lookup is the only use of the ROM. `psel` is an output of
the netlist computed without I, so the physical simulator can evaluate the
netlist, look up I = Pi[addr][psel] per cell, then finish the netlist.
"""
from dataclasses import dataclass, asdict
from functools import lru_cache
from .netlist import (Net, w_eq, w_eq_const, w_mux, w_add_const, w_ult_const,
                      w_in_range, w_sub_from_const)
from . import maintenance

OFFSETS = tuple(range(-5, 6))
LANE_OFFSETS = (-5, -4, -3, -2, -1, 1, 2, 3, 4, 5)

# instruction fields: op[2] kind[2] a[SB] b[SB] d[DB]; SB, DB depend on L, S
AND, OR, XOR, ANDN = range(4)          # ALU operation on sources A, B
K_REG, K_HOLD, K_SCR, K_NONE = range(4)  # destination kind
OPNAMES = ('AND', 'OR', 'XOR', 'ANDN')


@dataclass(frozen=True)
class Params:
    k: int = 7            # Q = 2^k
    m: int = 14           # U = 2^m
    L: int = 32           # front registers
    S: int = 2            # scratch bits per cell
    NP: int = 64          # passes in the evaluation window
    E0q: int = 6          # evaluation window starts at Age E0q*Q
    MP: int = 3           # match pass index (odd: leftward)
    skew: tuple = (0,) * 10  # per-lane capture skew delta_j, LANE_OFFSETS order
    dlog: int = 0         # the front dwells D = 2^dlog ticks at each cell
    win: int = 0          # instructions may read local lanes of cells x-win..x+win

    @property
    def D(self): return 1 << self.dlog
    @property
    def PW(self):
        """Width of psel: dwell index (low bits) then pass index."""
        return self.logNP + self.dlog
    @property
    def Q(self): return 1 << self.k
    @property
    def U(self): return 1 << self.m
    @property
    def E0(self): return self.E0q * self.Q
    @property
    def logNP(self): return max(1, (self.NP - 1).bit_length())
    @property
    def NPT(self):
        """ROM row width: every value of the psel field has an entry."""
        return 1 << self.PW
    @property
    def SB(self): return max(1, (self.n_sources - 1).bit_length())
    @property
    def DB(self): return max(1, (max(self.L, self.S) - 1).bit_length())
    @property
    def IW(self): return 2 + 2 + 2 * self.SB + self.DB
    @property
    def n_sources(self): return self.L + (2 * self.win + 1) * (12 + self.S) + 2

    def check(self):
        assert self.IW <= 32
        assert self.k + self.IW <= self.L, 'match load must preserve R[0:k]'
        assert self.k + self.PW <= self.L
        assert self.MP % 2 == 1 and 0 < self.MP < self.NP
        assert self.E0 >= 5 * self.Q + 2
        assert self.E0q % self.D == 0
        assert self.E0 + self.NP * self.D * self.Q <= self.U - 1
        assert self.S >= 1 and 0 <= self.win <= 3
        assert len(self.skew) == len(LANE_OFFSETS)
        for off, d in zip(LANE_OFFSETS, self.skew):
            assert 0 <= d < self.Q - 1
            assert self.capture_age(off) < self.E0
        return self

    def fam(self):
        """The module that defines this candidate family's rule."""
        import sys
        return sys.modules[__name__]

    def capture_age(self, off):
        """Computed Age at which lane `off` captures the passing mail bit.

        Lane off at cell x then holds the upper neighbour's Info bit at
        address x - skew (valid for x >= skew)."""
        d = self.skew[LANE_OFFSETS.index(off)]
        return abs(off) * self.Q + 1 + (d if off < 0 else -d)


def schema(p):
    """Ordered (field, width) list of the physical/upper cell alphabet."""
    return [('addr', p.k), ('age', p.m), ('f1', 1), ('f2', 1), ('wf1', 1),
            ('wf2', 1), ('info', 1), ('hold', 1), ('mr', 1), ('ml', 1),
            ('ln', len(LANE_OFFSETS)), ('scr', p.S), ('reg', p.L)]


def width(p):
    return sum(w for _, w in schema(p))


def info_copies(p):
    """(bit of field 'info', holder offset) for each stored copy of a logical
    cell's Info: the copy of logical cell x sits at physical cell x+offset."""
    return [(0, 0)]


def window_offsets(p):
    """Cell offsets whose lanes an instruction may read: 0 first, then +-1.."""
    return [0] + [o for d in range(1, getattr(p, 'win', 0) + 1) for o in (-d, d)]


def source_names(p):
    """Operand source codes: registers, then lanes of each window cell, then
    constants. Offset-0 names are ('info', 0), ('hold', 0), ('ln', i),
    ('scr', i); other offsets o use ('info@', o), ('hold@', o), ('ln@', i, o),
    ('scr@', i, o)."""
    names = [('reg', i) for i in range(p.L)]
    for o in window_offsets(p):
        if o == 0:
            names += [('info', 0), ('hold', 0)] + [('ln', i) for i in range(len(LANE_OFFSETS))]
            names += [('scr', i) for i in range(p.S)]
        else:
            names += [('info@', o), ('hold@', o)] + [('ln@', i, o) for i in range(len(LANE_OFFSETS))]
            names += [('scr@', i, o) for i in range(p.S)]
    names += [('const', 0), ('const', 1)]
    return names


def encode_instruction(p, op, kind, a, b, d):
    """Word 0 is AND into R[0] of R[0], R[0]: a no-op."""
    SB, DB = p.SB, p.DB
    assert 0 <= op < 4 and 0 <= kind < 4 and 0 <= a < (1 << SB) and 0 <= b < (1 << SB)
    assert 0 <= d < (1 << DB)
    return op | (kind << 2) | (a << 4) | (b << (4 + SB)) | (d << (4 + 2 * SB))


def decode_instruction(p, word):
    SB, DB = p.SB, p.DB
    return (word & 3, (word >> 2) & 3, (word >> 4) & ((1 << SB) - 1),
            (word >> (4 + SB)) & ((1 << SB) - 1), (word >> (4 + 2 * SB)) & ((1 << DB) - 1))


def _decoder(n, bits, count):
    """One-hot decode of an unsigned word into `count` lines (shared predecode)."""
    lines = [1]
    for i, x in enumerate(bits):
        nx = n.NOT(x)
        lines = [n.AND(l, nx) for l in lines] + [n.AND(l, x) for l in lines]
    return lines[:count]


def front_timing_dwell(n, p, c, cell, return_page=False):
    """Front clock with dwell: pass = D*Q ticks, D consecutive slots per cell.

    Stored Age bits: [dwell index t | cell position | pass block]. The front
    moves on the first slot of a visit and stays for the other D-1 slots.
    psel = t + D * pass outside the match pass."""
    k, m, L, Q, dl = p.k, p.m, p.L, p.Q, p.dlog
    confined = getattr(p, 'confined', False)
    pb = getattr(p, 'PB', k)                 # Age position bits (k unless confined)
    s = c['age'][:pb + dl]
    t, cellpos = s[:dl], s[dl:]
    block = c['age'][pb + dl:]
    base = getattr(p, 'E0b', p.E0q) >> dl
    in_window = w_in_range(n, block, base, base + p.NP)
    page = w_add_const(n, block, (-base) % (1 << (m - pb - dl)))[:p.logNP]
    direction = page[0]
    match_list = getattr(p, 'match_list', (p.MP,))
    match_pass = n.AND(in_window, n.any(w_eq_const(n, page, mp) for mp in match_list))
    first_pass = n.AND(in_window, w_eq_const(n, page, 0))
    if confined:
        # the front sweeps [lo, hi): forward at lo+pos, backward at hi-1-pos
        pos_k = list(cellpos) + [0] * (k - len(cellpos))
        fwd = w_add_const(n, pos_k, p.lo)
        back = w_sub_from_const(n, p.hi - 1, pos_k)
        arrive = n.AND(in_window, w_eq(n, c['addr'], w_mux(n, direction, back, fwd)))
    elif getattr(p, 'exact', False):
        # Q is not a power of two: a backward pass is at cell Q-1-pos
        back = w_sub_from_const(n, Q - 1, c['addr'])
        target = w_mux(n, direction, back, c['addr'])
        arrive = n.AND(in_window, w_eq(n, cellpos, target))
    else:
        arrive = n.AND(in_window, n.NOT(n.any(n.XOR(n.XOR(ci, xi), direction)
                                                  for ci, xi in zip(cellpos, c['addr']))))
    first_slot = w_eq_const(n, t, 0)
    at_left_end = w_eq_const(n, c['addr'], p.lo if confined else 0)
    at_right_end = w_eq_const(n, c['addr'], (p.hi if confined else Q) - 1)
    start = n.all([first_pass, at_left_end, first_slot])
    turn = n.AND(first_slot, n.AND(n.NOT(first_pass), n.MUX(direction, at_right_end, at_left_end)))
    stay = n.OR(turn, n.NOT(first_slot))
    move = n.AND(first_slot, n.NOT(turn))
    from_right = n.AND(move, direction)
    from_left = n.AND(move, n.NOT(direction))
    rsrc = []
    for i in range(L):
        v = n.OR(n.OR(n.AND(from_left, cell[-1]['reg'][i]),
                      n.AND(from_right, cell[1]['reg'][i])),
                 n.AND(stay, c['reg'][i]))
        rsrc.append(n.AND(n.NOT(start), v))
    psel = w_mux(n, match_pass, rsrc[k:k + p.PW], list(t) + list(page))
    if return_page:
        return rsrc, psel, arrive, match_pass, page, in_window
    return rsrc, psel, arrive, match_pass


def build(p):
    p.check()
    n = Net()
    k, m, L, S, Q, U = p.k, p.m, p.L, p.S, p.Q, p.U
    sch = schema(p)
    cell = {}
    for j in OFFSETS:
        cell[j] = {f: [n.input(('x', j, f, i)) for i in range(w)] for f, w in sch}
    I = [n.input(('I', i)) for i in range(p.IW)]
    c = cell[0]

    # ---------------------------------------------------------- local structure
    mt = maintenance.build(
        n, {j: dict(addr=cell[j]['addr'], age=cell[j]['age'], f1=cell[j]['f1'][0],
                    f2=cell[j]['f2'][0], wf1=cell[j]['wf1'][0], wf2=cell[j]['wf2'][0])
            for j in OFFSETS}, k, m)
    x_addr, age_now = mt['addr'], mt['age_now']
    f1_new = mt['f1']

    if p.dlog == 0:
        # ---------------------------------------------------------- front timing
        # The transient evaluator front is clocked by the cell's *stored* Age and
        # Address (as the current candidate's holder clock is), so its lookup key
        # depends only on the cell's own fields and the arriving register file.
        s = c['age'][:k]                     # position within a Q-tick block
        block = c['age'][k:]                 # Age >> k
        in_window = w_in_range(n, block, p.E0q, p.E0q + p.NP)
        page = w_add_const(n, block, (-p.E0q) % (1 << (m - k)))[:p.logNP]
        direction = page[0]
        match_pass = n.AND(in_window, w_eq_const(n, page, p.MP))
        first_pass = n.AND(in_window, w_eq_const(n, page, 0))

        # ---------------------------------------------------------- front arrival
        arrive = n.AND(in_window, n.NOT(n.any(n.XOR(n.XOR(si, xi), direction)
                                                  for si, xi in zip(s, c['addr']))))
        at_left_end = w_eq_const(n, c['addr'], 0)
        at_right_end = w_eq_const(n, c['addr'], Q - 1)
        start = n.AND(first_pass, at_left_end)
        turn = n.AND(n.NOT(first_pass), n.MUX(direction, at_right_end, at_left_end))
        from_right = n.AND(n.NOT(turn), direction)
        from_left = n.AND(n.NOT(turn), n.NOT(direction))
        rsrc = []
        for i in range(L):
            v = n.OR(n.OR(n.AND(from_left, cell[-1]['reg'][i]),
                          n.AND(from_right, cell[1]['reg'][i])),
                     n.AND(turn, c['reg'][i]))
            rsrc.append(n.AND(n.NOT(start), v))

        # psel: the page used by this cell's instruction lookup (independent of I)
        psel = w_mux(n, match_pass, rsrc[k:k + p.logNP], page)
        for i, b in enumerate(psel):
            n.set_output(('psel', i), b)
        n.set_output(('arrive', 0), arrive)
    else:
        rsrc, psel, arrive, match_pass = front_timing_dwell(n, p, c, cell)
        for i, b in enumerate(psel):
            n.set_output(('psel', i), b)
        n.set_output(('arrive', 0), arrive)

    # ---------------------------------------------------------- execute
    SB = p.SB
    op, kind = I[0:2], I[2:4]
    a_code, b_code, d_code = I[4:4 + SB], I[4 + SB:4 + 2 * SB], I[4 + 2 * SB:p.IW]
    lanes = []
    for o in window_offsets(p):
        co = cell[o]
        lanes += [co['info'][0], co['hold'][0]] + co['ln'] + co['scr']
    lanes += [0, 1]
    sources = rsrc + lanes
    assert len(sources) == p.n_sources
    dec_a = _decoder(n, a_code, len(sources))
    dec_b = _decoder(n, b_code, len(sources))
    A = n.any(n.AND(dl, v) for dl, v in zip(dec_a, sources))
    B = n.any(n.AND(dl, v) for dl, v in zip(dec_b, sources))
    op_lines = _decoder(n, op, 4)
    alu = n.any([n.AND(op_lines[AND], n.AND(A, B)),
                 n.AND(op_lines[OR], n.OR(A, B)),
                 n.AND(op_lines[XOR], n.XOR(A, B)),
                 n.AND(op_lines[ANDN], n.ANDN(A, B))])
    kind_lines = _decoder(n, kind, 4)
    dec_d = _decoder(n, d_code, L)
    executing = n.AND(arrive, n.NOT(match_pass))
    matched = n.AND(n.AND(arrive, match_pass), w_eq(n, c['addr'], rsrc[:k]))
    reg_new = []
    for i in range(L):
        v = n.MUX(n.AND(kind_lines[K_REG], dec_d[i]), alu, rsrc[i])
        if k <= i < k + p.IW:
            v_match = n.MUX(matched, I[i - k], rsrc[i])
        else:
            v_match = rsrc[i]
        v = n.MUX(match_pass, v_match, v)
        reg_new.append(n.AND(arrive, v))

    store_hold = n.AND(executing, kind_lines[K_HOLD])
    store_scr = n.AND(executing, kind_lines[K_SCR])
    scr_sel = _decoder(n, d_code[:max(1, (S - 1).bit_length())], S) if S > 1 else [1]

    # ---------------------------------------------------------- gather
    # Gather and commit use the computed (voted) Age, as in Gray.
    age_is = lambda value: w_eq_const(n, age_now, value)
    s_now, block_now = age_now[:k], age_now[k:]
    load_mail = age_is(0)
    mr = n.MUX(load_mail, c['info'][0], cell[-1]['mr'][0])
    ml = n.MUX(load_mail, c['info'][0], cell[1]['ml'][0])
    mr = n.AND(mr, n.NOT(f1_new))       # Gray: Mailbox cleared where Flag1
    ml = n.AND(ml, n.NOT(f1_new))
    ln_new = []
    for idx, off in enumerate(LANE_OFFSETS):
        t = p.capture_age(off)
        cap = n.AND(w_eq_const(n, s_now, t % Q), w_eq_const(n, block_now, t // Q))
        src = c['mr'][0] if off < 0 else c['ml'][0]
        ln_new.append(n.MUX(cap, src, c['ln'][idx]))

    # ---------------------------------------------------------- hold / info
    commit = age_is(U - 1)
    info = n.MUX(commit, c['hold'][0], c['info'][0])
    hold = n.MUX(store_hold, alu, c['hold'][0])
    hold = n.AND(hold, n.NOT(commit))
    scr_new = [n.MUX(n.AND(store_scr, scr_sel[i]), alu, c['scr'][i]) for i in range(S)]

    # Gray: simulation structure wiped where Flag1 and Address changes
    wipe = n.AND(f1_new, n.NOT(w_eq(n, x_addr, c['addr'])))
    keep = n.NOT(wipe)
    new = dict(addr=x_addr, age=mt['age'], f1=[f1_new], f2=[mt['f2']], wf1=[0], wf2=[0],
               info=[info], hold=[hold], mr=[mr], ml=[ml], ln=ln_new, scr=scr_new,
               reg=reg_new)
    for f in ('info', 'hold', 'mr', 'ml', 'ln', 'scr', 'reg'):
        new[f] = [n.AND(keep, b) for b in new[f]]
    for f, w in sch:
        assert len(new[f]) == w, f
        for i, b in enumerate(new[f]):
            n.set_output(('y', f, i), b)
    return n


@lru_cache(maxsize=8)
def cached(p):
    from .netlist import Compiled
    net = build(p)
    return net, Compiled(net)


def identity(p):
    net, comp = cached(p)
    return dict(params=asdict(p), Q=p.Q, U=p.U, width=width(p), schema=schema(p),
                radius=5, gates=len(comp.gates), netlist_sha256=comp.digest)
