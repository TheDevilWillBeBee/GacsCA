"""Front candidate family with Gray's simulation-structure redundancy ("G").

Same local structure (candidate-B maintenance, radius five), front, match
pass and ROM projection as `rule.py`, plus the correction structures that the
current Q8192 candidate also carries:

* Gray section 5.4 fivefold redundancy of every stored simulation-structure
  bit: Info, Hold, both Mailbox tracks, the gathered histories and the
  scratch memory. Field f of width w is stored as 5w bits; bit
  (slot*w + i) of cell y is the copy of bit i of the *logical* cell y+slot-2.
  Every tick every copy is recomputed from majority-corrected values; a
  logical cell's phase comes from the holder's own computed Address/Age
  (holder-local geometry, as in `stream28_holder_rule`).
* Three gathers at separated ages. History 1 and 2 are stored; the third
  arriving bit is voted with them (majority of three) into history 1, which
  is what the program reads.
* An early program computes the upper cell's new Flag1/Flag2 and stores
  them into Hold at Addresses Q-3 and 3; at Age T_sig the special procedure
  copies them into the SimBits (Info) there (Gray p. 35), and during the
  trickle-down window [T_sig+1, T_sig+1+2Q) Workspace.Flag1/Flag2 follow
  Gray p. 41 (single copy, recomputed each tick from corrected SimBits).
* The front is not replicated (like the evaluator of the current
  candidate). Its Hold/scratch writes go through a one-tick pending buffer
  (pend, pkind, pval) that every copy holder applies; reads forward it.

Parameters are a different fixed candidate from `rule.Params`; neither has a
depth parameter.
"""
from dataclasses import dataclass, asdict
from functools import lru_cache
import sys
from .netlist import (Net, w_eq, w_eq_const, w_mux, w_add_const, w_in_range, w_ult_const, at_least,
                      w_add_const_mod)
from . import maintenance
from .rule import (OFFSETS, LANE_OFFSETS, AND, OR, XOR, ANDN, K_REG, K_HOLD, K_SCR, K_NONE,
                   OPNAMES, encode_instruction, decode_instruction, _decoder, front_timing_dwell)

FIVE = ('info', 'hold', 'mr', 'ml', 'h1', 'h2', 'scr')
SLOTS = (-2, -1, 0, 1, 2)


@dataclass(frozen=True)
class ParamsG:
    k: int = 8
    m: int = 16
    L: int = 64
    S: int = 4
    NP: int = 160         # passes in the evaluation window (early + A + match + final)
    NPe: int = 30         # passes of the early Flag program
    MP: int = 37          # match pass (odd)
    E0q: int = 24         # evaluation window starts at Age E0q*Q
    gathers_q: tuple = (0, 8, 16)   # gather start Ages in units of Q
    skew: tuple = (0,) * 10
    dlog: int = 0         # front dwell D = 2^dlog slots per cell visit
    gate_pend: bool = False   # apply a pending write only where the front was last tick
    tmr: bool = False         # final program runs three times into Hold copies A/B/C
    computed_front: bool = False  # front clock, lookup key and match use computed Age/Address
    five_front: bool = False  # register file and pending buffer fivefold, one muxed lookup per cell
    run_len: int = 0          # passes per run (phase A + match + final), even
    margin: int = 0           # cells at each colony end holding no represented SimBit and no
                              # workspace (Gray p. 33): compiler layout and instruction slots only
    clear_ws: bool = False    # clear scratch at the period boundary (Gray p. 34: Workspace is
                              # set to 0 at the start of the work period); Hold is already
                              # cleared at the commit, histories and mail are reloaded
    q: int = 0                # exact colony size (0: Q = 2^k); a multiple of 64 with q <= 2^k
    nb: int = 0               # with q: blocks of Q ticks per work period, U = nb * Q; Age is stored
                              # packed as (tick mod Q in the low k bits, tick // Q above)
    mux_front: bool = False   # compact front evaluated once: the five candidate slots have distinct
                              # Addresses, so at most one 'arrive' holds and the inputs of the arriving
                              # slot can be selected before a single front step (same function)
    compact_front: bool = False  # the front's register file is one L-bit slot per cell: the copy of
                              # the (unique) front within two cells; its value is the majority
                              # of the five slots around the front (five_front stores 5L bits)
    fronts: int = 1           # a comb of `fronts` fronts `delta` cells apart moving in lockstep; each
    delta: int = 5            # executes its own program (Pi[Address][page, front]) with its own
                              # register file; the comb overhangs the working cells by
                              # H = (fronts-1)*delta at both ends, where it only carries (no-op)
    sel_front: int = 0        # 1: select, then vote: at most one front arrives at a cell, so the
                              # five register copies (and lane copies) of the arriving front's source
                              # are selected before a single five-way majority. 2: vote the seven
                              # register windows from lanes alone, then one 7-way select of the
                              # arriving front's source (lanes as mux_front). Both compute the same
                              # function as mux_front.
    confined: bool = False    # the front sweeps only the working cells [margin, Q - margin): a pass
                              # takes W = Q - 2*margin ticks and Age is packed with radix W; the new
                              # upper flags reach Gray's cells 3 and Q-3 by a courier on the mail

    @property
    def D(self): return 1 << self.dlog
    @property
    def PW(self): return self.logNP + self.dlog + self.FB
    @property
    def Q(self): return self.q if self.q else 1 << self.k
    @property
    def exact(self): return bool(self.q)
    @property
    def lo(self): return self.margin
    @property
    def hi(self): return self.Q - self.margin
    @property
    def H(self):
        """Overhang of the comb beyond the working cells."""
        return (self.fronts - 1) * self.delta
    @property
    def FB(self):
        """Bits of the front index in psel."""
        return (self.fronts - 1).bit_length()
    @property
    def PL(self):
        """Pass length in ticks (the front's sweep)."""
        return self.hi - self.lo + self.H if self.confined else self.Q
    @property
    def R(self):
        """Radix of the packed Age (position within a block)."""
        return self.PL if self.confined else self.Q
    @property
    def PB(self):
        """Bits of the Age position field."""
        return max(1, (self.R - 1).bit_length()) if self.confined else self.k
    @property
    def E0b(self):
        """First block of the evaluation window."""
        return -(-self.E0q * self.Q // self.PL) if self.confined else self.E0q
    @property
    def U(self): return self.nb * self.R if self.q else 1 << self.m

    def age_code(self, t):
        """Stored/computed Age value of tick t of the work period."""
        return ((t // self.R) << self.PB) | (t % self.R) if self.q else t
    @property
    def E0(self): return self.E0b * self.PL
    @property
    def logNP(self): return max(1, (self.NP - 1).bit_length())
    @property
    def NPT(self): return 1 << self.PW
    @property
    def n_sources(self): return self.L + 12 + self.S + 2
    @property
    def SB(self): return max(1, (self.n_sources - 1).bit_length())
    @property
    def DB(self): return max(1, (max(self.L, self.S) - 1).bit_length())
    @property
    def IW(self): return 2 + 2 + 2 * self.SB + self.DB
    @property
    def NH(self): return 3 if self.tmr else 1          # Hold copies (runs)
    @property
    def PK(self): return max(1, (self.NH + self.S).bit_length())  # pkind: hold r, then scr
    @property
    def match_list(self):
        return tuple(self.MP + r * self.run_len for r in range(self.NH)) if self.tmr else (self.MP,)
    @property
    def T_sig(self): return self.E0 + self.NPe * self.D * self.PL
    @property
    def T_wf(self): return self.T_sig + 1

    def fam(self):
        return sys.modules[__name__]

    def capture_age(self, off, g=0):
        d = self.skew[LANE_OFFSETS.index(off)]
        return self.gathers_q[g] * self.Q + abs(off) * self.Q + 1 + (d if off < 0 else -d)

    def check(self):
        assert self.IW <= 32 and self.k + self.IW <= self.L and self.k + self.PW <= self.L
        assert self.E0q % self.D == 0
        assert self.MP % 2 == 1 and self.NPe < self.MP < self.NP
        if self.five_front:
            assert self.computed_front and not self.gate_pend
        if self.compact_front:
            assert self.five_front
        if self.mux_front:
            assert self.compact_front
        if self.sel_front:
            assert self.mux_front and self.confined and self.dlog == 0
        if self.tmr:
            assert self.run_len % 2 == 0 and self.MP < self.NPe + self.run_len
            assert self.NPe + 3 * self.run_len <= self.NP
        assert len(self.skew) == len(LANE_OFFSETS) and len(self.gathers_q) == 3
        for g in range(3):
            for off, d in zip(LANE_OFFSETS, self.skew):
                assert 0 <= d < self.Q - 1
                t = self.capture_age(off, g)
                assert t > self.gathers_q[g] * self.Q
                if g < 2:
                    assert t < self.gathers_q[g + 1] * self.Q
                assert t < self.E0
        assert self.T_wf + 2 * self.Q < self.E0 + self.NP * self.D * self.PL
        assert self.E0 + self.NP * self.D * self.PL <= self.U - 1
        if self.q:
            assert self.q % 64 == 0 and self.q <= (1 << self.k) and self.dlog == 0
            assert self.m == self.PB + max(1, (self.nb - 1).bit_length())
        if self.fronts > 1:
            # compact slots and fivefold pending writes see at most one front
            # within two cells; the comb stays inside the colony, and a level-1
            # burst (200 cells wide) cannot reach front state or SimBits of two
            # colonies: the front state of the right-hand colony starts
            # 2*margin - 2*H - 3 cells after that of the left-hand one
            assert self.confined and self.mux_front and self.delta >= 5
            assert self.H <= self.lo - 2 and self.hi + 1 + self.H < self.Q
            assert 2 * self.margin - 2 * self.H - 3 >= 200
        if self.confined:
            # Gray's flag rule reads Age mod 16 from the low position bits; the
            # couriers need the flag sources inside the window and a free last
            # early pass (the early program ends one pass before T_sig)
            assert self.q and self.five_front and self.R % 16 == 0 and self.margin >= 8
            assert self.T_sig - self.PL < self.courier_ticks()[0] and self.NPe >= 2
        return self

    def courier_ticks(self):
        """Ages at which the flag couriers load: the left mail track at the left
        working-area end (new Flag2, towards cell 3) and the right mail track at
        the right end (new Flag1, towards cell Q-3); both arrive at T_sig."""
        a_l = self.T_sig - self.lo + 2
        a_r = self.T_sig - (self.Q - 2 - self.hi) - 1
        return min(a_l, a_r), a_l, a_r


FRONT = ('reg', 'pend', 'pkind', 'pval')


def fivefold_fields(p):
    if getattr(p, 'compact_front', False):
        return FIVE + ('pend', 'pkind', 'pval')
    return FIVE + (FRONT if getattr(p, 'five_front', False) else ())


def schema(p):
    sch = [('addr', p.k), ('age', p.m), ('f1', 1), ('f2', 1), ('wf1', 1), ('wf2', 1)]
    sch += [(f, 5 * logical_width(f, p)) for f in fivefold_fields(p)]
    if getattr(p, 'compact_front', False):
        sch += [('reg', p.L)]
    elif not getattr(p, 'five_front', False):
        sch += [('reg', p.L), ('pend', 1), ('pkind', p.PK), ('pval', 1)]
    return sch


def logical_width(f, p):
    return dict(info=1, hold=p.NH, mr=1, ml=1, h1=len(LANE_OFFSETS), h2=len(LANE_OFFSETS), scr=p.S,
                reg=p.L, pend=1, pkind=p.PK, pval=1)[f]


def width(p):
    return sum(w for _, w in schema(p))


def info_copies(p):
    """Copy slot s (bit s of 'info') at holder y belongs to logical cell
    y + s - 2, so logical cell x's copy s is at physical cell x - (s - 2)."""
    return [(s, -(s - 2)) for s in range(5)]


def source_names(p):
    """Operand sources: registers, corrected local lanes, constants.

    ('ln', i) reads the voted history (h1) lane i; ('info', 0), ('hold', 0)
    and ('scr', i) read majority-corrected values with pending-write forwarding."""
    names = [('reg', i) for i in range(p.L)]
    names += [('info', 0), ('hold', 0)] + [('ln', i) for i in range(len(LANE_OFFSETS))]
    names += [('scr', i) for i in range(p.S)] + [('const', 0), ('const', 1)]
    return names


def reserved_cells(p):
    """Cells whose Info is not part of the upper-state layout (Gray p. 35); a
    confined front also reserves the two flag-courier sources."""
    if getattr(p, 'confined', False):
        return (3, p.Q - 3, p.lo, p.hi - 1)
    return (3, p.Q - 3)


def flag_store_cells(p):
    """(cell for the new upper Flag1, cell for the new upper Flag2) written by
    the early program into Hold."""
    if getattr(p, 'confined', False):
        return p.hi - 1, p.lo
    return p.Q - 3, 3


def work_range(p):
    """Cells [lo, hi) that may hold represented SimBits and workspace; the
    rest of the colony is margin (Gray p. 33: the needed SimBits are placed
    away from the colony boundaries)."""
    m = getattr(p, 'margin', 0)
    return m, p.Q - m


def maj3(n, a, b, c):
    return n.OR(n.AND(a, b), n.AND(c, n.OR(a, b)))


def maj5(n, bits):
    return at_least(n, bits, 3)


def build(p):
    p.check()
    n = Net()
    k, m, L, S, Q, U = p.k, p.m, p.L, p.S, p.Q, p.U
    sch = schema(p)
    cell = {j: {f: [n.input(('x', j, f, i)) for i in range(w)] for f, w in sch} for j in OFFSETS}
    I = [n.input(('I', i)) for i in range(p.IW)]
    c = cell[0]

    # ------------------------------------------------------------ local structure
    mt = maintenance.build(
        n, {j: dict(addr=cell[j]['addr'], age=cell[j]['age'], f1=cell[j]['f1'][0],
                    f2=cell[j]['f2'][0], wf1=cell[j]['wf1'][0], wf2=cell[j]['wf2'][0])
            for j in OFFSETS}, k, m,
        **(dict(Q=Q, nb=p.nb, radix=p.R, pos_bits=p.PB) if p.exact else {}))
    addr_now, age_now, f1_new = mt['addr'], mt['age_now'], mt['f1']
    s_now, block_now = age_now[:p.PB], age_now[p.PB:]
    age_is = lambda value: w_eq_const(n, age_now, p.age_code(value))
    addq = (lambda a, v: w_add_const_mod(n, a, v, Q)) if p.exact else (lambda a, v: w_add_const(n, a, v))

    # ------------------------------------------------------------ corrected values
    def copy(z, f, slot, i):
        w = logical_width(f, p)
        return cell[z][f][(slot + 2) * w + i]

    prev_arrive = {}

    def was_front(z):
        """Stored Age/Address of logical cell z say the front executed there
        one tick ago (arrival condition evaluated at Age-1)."""
        if z not in prev_arrive:
            prev = dict(cell[z])
            prev['age'] = w_add_const(n, cell[z]['age'], (1 << m) - 1)
            _, _, arr, mpass = front_timing_dwell(n, p, prev, {-1: cell[z], 0: cell[z], 1: cell[z]})
            prev_arrive[z] = n.AND(arr, n.NOT(mpass))
        return prev_arrive[z]

    def pend_hits(z, f, i):
        """The pending front write at logical cell z targets (f, i)."""
        if f == 'hold':
            target = i
        elif f == 'scr':
            target = i + p.NH
        else:
            return 0
        if p.five_front:
            return n.AND(lv(z, 'pend'), w_eq_const(n, [lv(z, 'pkind', j) for j in range(p.PK)], target))
        hit = n.AND(cell[z]['pend'][0], w_eq_const(n, cell[z]['pkind'], target))
        return n.AND(hit, was_front(z)) if p.gate_pend else hit

    cache = {}

    def lv(z, f, i=0):
        """Logical current value of (f, i) at logical cell z (|z| <= 3)."""
        key = (z, f, i)
        if key not in cache:
            if f == 'reg' and p.compact_front:
                # one slot per cell: the five copies around logical cell z
                cache[key] = maj5(n, [cell[z + e]['reg'][i] for e in SLOTS])
                return cache[key]
            v = maj5(n, [copy(z - e, f, e, i) for e in SLOTS])
            hit = pend_hits(z, f, i)
            if hit != 0:
                pval = lv(z, 'pval') if p.five_front else cell[z]['pval'][0]
                v = n.MUX(hit, pval, v)
            cache[key] = v
        return cache[key]

    if p.five_front:
        front_new = _five_front(n, p, I, lv, age_now, addr_now,
                                raw=dict(cell=cell, copy=copy, pend_hits=pend_hits))
    # ------------------------------------------------------------ front timing (stored fields)
    if p.five_front:
        pass
    elif p.computed_front:
        timing_cell = dict(c, age=age_now, addr=addr_now)
        key_addr = addr_now
        for i, b in enumerate(addr_now):
            n.set_output(('laddr', i), b)
    else:
        timing_cell = c
        key_addr = c['addr']
    if not p.five_front:
        rsrc, psel, arrive, match_pass, page, _ = front_timing_dwell(n, p, timing_cell, cell,
                                                                     return_page=True)
        if p.tmr:
            run1 = n.NOT(w_ult_const(n, page, p.NPe + p.run_len))
            run2 = n.NOT(w_ult_const(n, page, p.NPe + 2 * p.run_len))
            run_idx = [n.AND(run1, n.NOT(run2)), run2]          # binary run index 0/1/2
        else:
            run_idx = [0]
        for i, b in enumerate(psel):
            n.set_output(('psel', i), b)
        n.set_output(('arrive', 0), arrive)

        # ------------------------------------------------------------ execute
        SB = p.SB
        op, kind = I[0:2], I[2:4]
        a_code, b_code, d_code = I[4:4 + SB], I[4 + SB:4 + 2 * SB], I[4 + 2 * SB:p.IW]
        lanes = ([lv(0, 'info'), lv(0, 'hold')] + [lv(0, 'h1', i) for i in range(len(LANE_OFFSETS))]
                 + [lv(0, 'scr', i) for i in range(S)] + [0, 1])
        sources = rsrc + lanes
        assert len(sources) == p.n_sources
        dec_a = _decoder(n, a_code, len(sources))
        dec_b = _decoder(n, b_code, len(sources))
        A = n.any(n.AND(dl, v) for dl, v in zip(dec_a, sources))
        B = n.any(n.AND(dl, v) for dl, v in zip(dec_b, sources))
        op_lines = _decoder(n, op, 4)
        alu = n.any([n.AND(op_lines[AND], n.AND(A, B)), n.AND(op_lines[OR], n.OR(A, B)),
                     n.AND(op_lines[XOR], n.XOR(A, B)), n.AND(op_lines[ANDN], n.ANDN(A, B))])
        kind_lines = _decoder(n, kind, 4)
        dec_d = _decoder(n, d_code, L)
        executing = n.AND(arrive, n.NOT(match_pass))
        matched = n.AND(n.AND(arrive, match_pass), w_eq(n, key_addr, rsrc[:k]))
        reg_new = []
        for i in range(L):
            v = n.MUX(n.AND(kind_lines[K_REG], dec_d[i]), alu, rsrc[i])
            v_match = n.MUX(matched, I[i - k], rsrc[i]) if k <= i < k + p.IW else rsrc[i]
            v = n.MUX(match_pass, v_match, v)
            reg_new.append(n.AND(arrive, v))
        store_hold = n.AND(executing, kind_lines[K_HOLD])
        store_scr = n.AND(executing, kind_lines[K_SCR])
        scr_index = d_code[:max(1, (S - 1).bit_length())]
        in_scr_range = n.AND(store_scr, w_in_range(n, d_code, 0, S)) if S < (1 << p.DB) else store_scr
        pend_new = n.OR(store_hold, in_scr_range)
        hold_target = (run_idx + [0] * p.PK)[:p.PK]
        pkind_new = w_mux(n, in_scr_range,
                          w_add_const(n, scr_index + [0] * (p.PK - len(scr_index)), p.NH)[:p.PK],
                          hold_target)
        pval_new = n.AND(pend_new, alu)

    # ------------------------------------------------------------ fivefold copy updates
    commit = age_is(U - 1)
    sig = age_is(p.T_sig)
    gather_start = [age_is(g * Q) for g in p.gathers_q]
    load_mail = n.any(gather_start)
    capture = []   # capture[g][lane idx]
    for g in range(3):
        row = []
        for idx, off in enumerate(LANE_OFFSETS):
            t = p.capture_age(off, g)
            row.append(n.AND(w_eq_const(n, s_now, t % p.R), w_eq_const(n, block_now, t // p.R)))
        capture.append(row)
    wipe = n.AND(f1_new, n.NOT(w_eq(n, addr_now, c['addr'])))
    keep = n.NOT(wipe)
    new = {f: [None] * (5 * logical_width(f, p)) for f in FIVE}
    for slot in SLOTS:
        x = slot                                # logical cell relative to holder
        xaddr = addq(addr_now, slot % Q)
        special = n.AND(sig, n.OR(w_eq_const(n, xaddr, 3), w_eq_const(n, xaddr, Q - 3)))
        if p.tmr:
            voted = maj3(n, lv(x, 'hold', 0), lv(x, 'hold', 1), lv(x, 'hold', 2))
            info = n.MUX(commit, voted, n.MUX(special, lv(x, 'hold', 0), lv(x, 'info')))
        elif p.confined:
            # special procedure: the flags arrive on the mail (couriers below)
            sp3 = n.AND(sig, w_eq_const(n, xaddr, 3))
            spq = n.AND(sig, w_eq_const(n, xaddr, Q - 3))
            info = n.MUX(commit, lv(x, 'hold'),
                         n.MUX(sp3, lv(x, 'ml'), n.MUX(spq, lv(x, 'mr'), lv(x, 'info'))))
        else:
            info = n.MUX(n.OR(commit, special), lv(x, 'hold'), lv(x, 'info'))
        holds = [n.AND(lv(x, 'hold', r), n.NOT(commit)) for r in range(p.NH)]
        if p.confined:
            # couriers: the working-area ends put their Hold (new upper Flag2 at
            # the left end, Flag1 at the right end) on the left/right mail track
            _, a_l, a_r = p.courier_ticks()
            cl = n.AND(age_is(a_l), w_eq_const(n, xaddr, p.lo))
            cr = n.AND(age_is(a_r), w_eq_const(n, xaddr, p.hi - 1))
            mr = n.MUX(load_mail, lv(x, 'info'), n.MUX(cr, lv(x, 'hold'), lv(x - 1, 'mr')))
            ml = n.MUX(load_mail, lv(x, 'info'), n.MUX(cl, lv(x, 'hold'), lv(x + 1, 'ml')))
        else:
            mr = n.MUX(load_mail, lv(x, 'info'), lv(x - 1, 'mr'))
            ml = n.MUX(load_mail, lv(x, 'info'), lv(x + 1, 'ml'))
        mr = n.AND(mr, n.NOT(f1_new))           # Gray: Mailbox cleared where Flag1
        ml = n.AND(ml, n.NOT(f1_new))
        vals = dict(info=[info], hold=holds, mr=[mr], ml=[ml], h1=[], h2=[], scr=[])
        for idx, off in enumerate(LANE_OFFSETS):
            passing = lv(x, 'mr') if off < 0 else lv(x, 'ml')
            h1, h2 = lv(x, 'h1', idx), lv(x, 'h2', idx)
            h1n = n.MUX(capture[0][idx], passing, h1)
            h1n = n.MUX(capture[2][idx], maj3(n, h1, h2, passing), h1n)
            h2n = n.MUX(capture[1][idx], passing, h2)
            vals['h1'].append(h1n)
            vals['h2'].append(h2n)
        vals['scr'] = [lv(x, 'scr', i) for i in range(S)]
        if getattr(p, 'clear_ws', False):
            vals['scr'] = [n.AND(v, n.NOT(commit)) for v in vals['scr']]
        for f in FIVE:
            w = logical_width(f, p)
            for i in range(w):
                new[f][(slot + 2) * w + i] = n.AND(keep, vals[f][i])

    # ------------------------------------------------------------ Workspace flags (Gray p. 41)
    in_wf = w_in_range(n, age_now, p.age_code(p.T_wf), p.age_code(p.T_wf + 2 * Q - 1) + 1)
    right_end = w_in_range(n, addr_now, Q - 5, Q)
    left_end = w_in_range(n, addr_now, 0, 5)
    sim_r = 0    # SimBit at logical offset (Q-3) - A, i.e. offset in [-2, 2]
    for a_off in range(5):
        A_val = Q - 5 + a_off
        sim_r = n.OR(sim_r, n.AND(w_eq_const(n, addr_now, A_val), lv((Q - 3) - A_val, 'info')))
    sim_l = 0    # SimBit at offset 3 - A, A in [0, 4]
    for A_val in range(5):
        sim_l = n.OR(sim_l, n.AND(w_eq_const(n, addr_now, A_val), lv(3 - A_val, 'info')))
    wf1 = n.all([right_end, in_wf, sim_r])
    wf2 = n.all([left_end, in_wf, sim_l, n.NOT(f1_new)])

    outs = dict(addr=addr_now, age=mt['age'], f1=[f1_new], f2=[mt['f2']], wf1=[wf1], wf2=[wf2])
    if p.five_front:
        for f in FRONT:
            outs[f] = [n.AND(keep, b) for b in front_new[f]]
    else:
        outs.update(reg=[n.AND(keep, b) for b in reg_new],
                    pend=[n.AND(keep, pend_new)], pkind=[n.AND(keep, b) for b in pkind_new],
                    pval=[n.AND(keep, pval_new)])
    outs.update(new)
    for f, w in sch:
        assert len(outs[f]) == w, (f, len(outs[f]), w)
        for i, b in enumerate(outs[f]):
            n.set_output(('y', f, i), b)
    return n


def _five_front(n, p, I, lv, age_now, addr_now, raw=None):
    """Fivefold front: copy slot d of reg/pend/pkind/pval at holder y belongs to
    logical cell y+d. Every holder executes the front step of each of its five
    logical cells from majority-corrected register files, with holder-local
    computed geometry. At most one logical cell holds the front, so each cell
    performs one Pi lookup, keyed by that logical cell's computed Address and
    psel. Returns the new copy-slot values of the front fields."""
    k, L, S, Q = p.k, p.L, p.S, p.Q
    lreg = None if p.sel_front else {z: [lv(z, 'reg', i) for i in range(L)] for z in range(-3, 4)}
    SB = p.SB
    op, kind = I[0:2], I[2:4]
    a_code, b_code, d_code = I[4:4 + SB], I[4 + SB:4 + 2 * SB], I[4 + 2 * SB:p.IW]
    op_lines = _decoder(n, op, 4)
    kind_lines = _decoder(n, kind, 4)
    dec_d = _decoder(n, d_code, L)
    scr_index = d_code[:max(1, (S - 1).bit_length())]
    new = {f: [None] * (5 * logical_width(f, p)) for f in FRONT}
    if p.compact_front:
        new['reg'] = [0] * L      # copy of the front's new registers if it is within two cells
    if p.sel_front:
        return _sel_front(n, p, I, lv, raw, age_now, addr_now, new, op_lines, kind_lines, dec_d,
                          scr_index, a_code, b_code, d_code)
    if p.mux_front:
        return _mux_front(n, p, I, lv, lreg, age_now, addr_now, new, op_lines, kind_lines, dec_d,
                          scr_index, a_code, b_code, d_code)
    key_psel, key_addr, any_arrive = None, None, 0
    for d in reversed(SLOTS):             # priority: slot -2 wins if several arrive
        xaddr = w_add_const_mod(n, addr_now, d % Q, Q)
        tcell = {'age': age_now, 'addr': xaddr, 'reg': lreg[d]}
        pseudo = {-1: {'reg': lreg[d - 1]}, 0: tcell, 1: {'reg': lreg[d + 1]}}
        rsrc, psel, arrive, match_pass, page, _ = front_timing_dwell(n, p, tcell, pseudo,
                                                                     return_page=True)
        key_psel = psel if key_psel is None else w_mux(n, arrive, psel, key_psel)
        key_addr = xaddr if key_addr is None else w_mux(n, arrive, xaddr, key_addr)
        any_arrive = n.OR(any_arrive, arrive)
        lanes = ([lv(d, 'info'), lv(d, 'hold')] + [lv(d, 'h1', i) for i in range(len(LANE_OFFSETS))]
                 + [lv(d, 'scr', i) for i in range(S)] + [0, 1])
        sources = rsrc + lanes
        assert len(sources) == p.n_sources
        dec_a = _decoder(n, a_code, len(sources))
        dec_b = _decoder(n, b_code, len(sources))
        A = n.any(n.AND(dl, v) for dl, v in zip(dec_a, sources))
        B = n.any(n.AND(dl, v) for dl, v in zip(dec_b, sources))
        alu = n.any([n.AND(op_lines[AND], n.AND(A, B)), n.AND(op_lines[OR], n.OR(A, B)),
                     n.AND(op_lines[XOR], n.XOR(A, B)), n.AND(op_lines[ANDN], n.ANDN(A, B))])
        executing = n.AND(arrive, n.NOT(match_pass))
        matched = n.AND(n.AND(arrive, match_pass), w_eq(n, xaddr, rsrc[:k]))
        for i in range(L):
            v = n.MUX(n.AND(kind_lines[K_REG], dec_d[i]), alu, rsrc[i])
            v_match = n.MUX(matched, I[i - k], rsrc[i]) if k <= i < k + p.IW else rsrc[i]
            v = n.MUX(match_pass, v_match, v)
            if p.compact_front:
                new['reg'][i] = n.OR(new['reg'][i], n.AND(arrive, v))
            else:
                new['reg'][(d + 2) * L + i] = n.AND(arrive, v)
        store_hold = n.AND(executing, kind_lines[K_HOLD])
        store_scr = n.AND(executing, kind_lines[K_SCR])
        in_scr = n.AND(store_scr, w_in_range(n, d_code, 0, S)) if S < (1 << p.DB) else store_scr
        pend = n.OR(store_hold, in_scr)
        pkind = w_mux(n, in_scr, w_add_const(n, scr_index + [0] * (p.PK - len(scr_index)), p.NH)[:p.PK],
                      [0] * p.PK)
        new['pend'][d + 2] = pend
        new['pval'][d + 2] = n.AND(pend, alu)
        for j in range(p.PK):
            new['pkind'][(d + 2) * p.PK + j] = pkind[j]
    for i, b in enumerate(key_psel):
        n.set_output(('psel', i), b)
    for i, b in enumerate(key_addr):
        n.set_output(('laddr', i), b)
    n.set_output(('arrive', 0), any_arrive)
    return new


def _mux_front(n, p, I, lv, lreg, age_now, addr_now, new, op_lines, kind_lines, dec_d, scr_index,
               a_code, b_code, d_code):
    """Compact front with one front step. The five candidate logical cells
    y-2..y+2 have pairwise distinct Addresses (Address + d mod Q), and a slot
    arrives only if its Address equals the front's target, so at most one
    'arrive' is true for every input. OR over d of (arrive_d AND step(inputs_d))
    therefore equals any_arrive AND step(inputs selected by arrive): the same
    function with one operand selection, ALU and register update instead of
    five."""
    k, L, S, Q = p.k, p.L, p.S, p.Q
    key_psel, key_addr, any_arrive = None, None, 0
    arr, rs, ln, xa = {}, {}, {}, {}
    match_pass = None
    for d in reversed(SLOTS):             # priority chain kept for psel / laddr outputs
        xaddr = w_add_const_mod(n, addr_now, d % Q, Q)
        tcell = {'age': age_now, 'addr': xaddr, 'reg': lreg[d]}
        pseudo = {-1: {'reg': lreg[d - 1]}, 0: tcell, 1: {'reg': lreg[d + 1]}}
        rsrc, psel, arrive, mpass, page, _ = front_timing_dwell(n, p, tcell, pseudo, return_page=True)
        match_pass = mpass                # independent of d (a function of Age only)
        key_psel = psel if key_psel is None else w_mux(n, arrive, psel, key_psel)
        key_addr = xaddr if key_addr is None else w_mux(n, arrive, xaddr, key_addr)
        any_arrive = n.OR(any_arrive, arrive)
        arr[d], rs[d], xa[d] = arrive, rsrc, xaddr
        ln[d] = ([lv(d, 'info'), lv(d, 'hold')] + [lv(d, 'h1', i) for i in range(len(LANE_OFFSETS))]
                 + [lv(d, 'scr', i) for i in range(S)])

    def pick(vals):
        return [n.any(n.AND(arr[d], vals[d][j]) for d in SLOTS) for j in range(len(vals[SLOTS[0]]))]
    rsrc, lanes, xaddr = pick(rs), pick(ln), pick(xa)
    if p.fronts > 1:
        # a front of the comb outside the working cells only carries its
        # registers: no register write, Hold or scratch store there
        inside = w_in_range(n, xaddr, p.lo, p.hi)
        kind_lines = [n.AND(inside, x) for x in kind_lines]
    sources = rsrc + lanes + [0, 1]
    assert len(sources) == p.n_sources
    dec_a = _decoder(n, a_code, len(sources))
    dec_b = _decoder(n, b_code, len(sources))
    A = n.any(n.AND(dl, v) for dl, v in zip(dec_a, sources))
    B = n.any(n.AND(dl, v) for dl, v in zip(dec_b, sources))
    alu = n.any([n.AND(op_lines[AND], n.AND(A, B)), n.AND(op_lines[OR], n.OR(A, B)),
                 n.AND(op_lines[XOR], n.XOR(A, B)), n.AND(op_lines[ANDN], n.ANDN(A, B))])
    matched = n.AND(n.AND(any_arrive, match_pass), w_eq(n, xaddr, rsrc[:k]))
    if p.fronts > 1:
        # only working cells answer the match pass: front 0, which holds the
        # lookup key one level down, never reaches the right overhang
        matched = n.AND(matched, inside)
    for i in range(L):
        v = n.MUX(n.AND(kind_lines[K_REG], dec_d[i]), alu, rsrc[i])
        v_match = n.MUX(matched, I[i - k], rsrc[i]) if k <= i < k + p.IW else rsrc[i]
        new['reg'][i] = n.AND(any_arrive, n.MUX(match_pass, v_match, v))
    not_match = n.NOT(match_pass)
    idx = w_add_const(n, scr_index + [0] * (p.PK - len(scr_index)), p.NH)[:p.PK]
    for d in SLOTS:
        executing = n.AND(arr[d], not_match)
        store_hold = n.AND(executing, kind_lines[K_HOLD])
        store_scr = n.AND(executing, kind_lines[K_SCR])
        in_scr = n.AND(store_scr, w_in_range(n, d_code, 0, S)) if S < (1 << p.DB) else store_scr
        pend = n.OR(store_hold, in_scr)
        new['pend'][d + 2] = pend
        new['pval'][d + 2] = n.AND(pend, alu)
        pkind = w_mux(n, in_scr, idx, [0] * p.PK)
        for j in range(p.PK):
            new['pkind'][(d + 2) * p.PK + j] = pkind[j]
    for i, b in enumerate(key_psel):
        n.set_output(('psel', i), b)
    for i, b in enumerate(key_addr):
        n.set_output(('laddr', i), b)
    n.set_output(('arrive', 0), any_arrive)
    return new


def _sel_front(n, p, I, lv, raw, age_now, addr_now, new, op_lines, kind_lines, dec_d, scr_index,
               a_code, b_code, d_code):
    """Select-then-vote front step (sel_front). As in _mux_front at most one
    slot d arrives. The register file it reads is the majority of the five
    copies around its source logical cell o = d-1, d+1 or d (moving from the
    left, from the right, or staying); a one-hot selector sel_o picks those
    five raw copies, and one five-way majority follows. Lane sources are
    likewise the majority of the arriving slot's five selected copies, with
    the pending-write forwarding of that slot. Same function as _mux_front,
    with one majority per register bit instead of seven."""
    from .rule import front_controls
    k, L, S, Q = p.k, p.L, p.S, p.Q
    cell, copy, pend_hits = raw['cell'], raw['copy'], raw['pend_hits']
    arr, xa, ctl = {}, {}, {}
    for d in reversed(SLOTS):
        xaddr = w_add_const_mod(n, addr_now, d % Q, Q)
        ctl[d] = front_controls(n, p, {'age': age_now, 'addr': xaddr})
        arr[d], xa[d] = ctl[d]['arrive'], xaddr
    match_pass = ctl[0]['match_pass']            # a function of Age only
    any_arrive = n.any(arr[d] for d in SLOTS)
    sel = {o: 0 for o in range(-3, 4)}
    for d in SLOTS:
        go = n.AND(arr[d], n.NOT(ctl[d]['start']))
        sel[d - 1] = n.OR(sel[d - 1], n.AND(go, ctl[d]['from_left']))
        sel[d + 1] = n.OR(sel[d + 1], n.AND(go, ctl[d]['from_right']))
        sel[d] = n.OR(sel[d], n.AND(go, ctl[d]['stay']))
    rsrc = []
    for i in range(L):
        if p.sel_front == 2:
            rsrc.append(n.any(n.AND(sel[o], lv(o, 'reg', i)) for o in range(-3, 4)))
        else:
            copies = [n.any(n.AND(sel[o], cell[o + e]['reg'][i]) for o in range(-3, 4)) for e in SLOTS]
            rsrc.append(maj5(n, copies))

    def pick(vals):
        return [n.any(n.AND(arr[d], vals[d][j]) for d in SLOTS) for j in range(len(vals[SLOTS[0]]))]
    xaddr = pick(xa)
    pval = n.any(n.AND(arr[d], lv(d, 'pval')) for d in SLOTS)

    def lane(f, i):
        """Value of fivefold (f, i) at the arriving logical cell."""
        if p.sel_front == 2:
            return n.any(n.AND(arr[d], lv(d, f, i)) for d in SLOTS)
        copies = [n.any(n.AND(arr[d], copy(d - e, f, e, i)) for d in SLOTS) for e in SLOTS]
        v = maj5(n, copies)
        hit = n.any(n.AND(arr[d], pend_hits(d, f, i)) for d in SLOTS)
        if hit != 0:
            v = n.MUX(hit, pval, v)
        return v
    lanes = ([lane('info', 0), lane('hold', 0)] + [lane('h1', i) for i in range(len(LANE_OFFSETS))]
             + [lane('scr', i) for i in range(S)])
    sources = rsrc + lanes + [0, 1]
    assert len(sources) == p.n_sources
    psel = w_mux(n, match_pass, rsrc[k:k + p.PW], pick({d: ctl[d]['psel_nm'] for d in SLOTS}))
    if p.fronts > 1:
        inside = w_in_range(n, xaddr, p.lo, p.hi)
        kind_lines = [n.AND(inside, x) for x in kind_lines]
    dec_a = _decoder(n, a_code, len(sources))
    dec_b = _decoder(n, b_code, len(sources))
    A = n.any(n.AND(dl, v) for dl, v in zip(dec_a, sources))
    B = n.any(n.AND(dl, v) for dl, v in zip(dec_b, sources))
    alu = n.any([n.AND(op_lines[AND], n.AND(A, B)), n.AND(op_lines[OR], n.OR(A, B)),
                 n.AND(op_lines[XOR], n.XOR(A, B)), n.AND(op_lines[ANDN], n.ANDN(A, B))])
    matched = n.AND(n.AND(any_arrive, match_pass), w_eq(n, xaddr, rsrc[:k]))
    if p.fronts > 1:
        matched = n.AND(matched, inside)
    for i in range(L):
        v = n.MUX(n.AND(kind_lines[K_REG], dec_d[i]), alu, rsrc[i])
        v_match = n.MUX(matched, I[i - k], rsrc[i]) if k <= i < k + p.IW else rsrc[i]
        new['reg'][i] = n.AND(any_arrive, n.MUX(match_pass, v_match, v))
    not_match = n.NOT(match_pass)
    idx = w_add_const(n, scr_index + [0] * (p.PK - len(scr_index)), p.NH)[:p.PK]
    for d in SLOTS:
        executing = n.AND(arr[d], not_match)
        store_hold = n.AND(executing, kind_lines[K_HOLD])
        store_scr = n.AND(executing, kind_lines[K_SCR])
        in_scr = n.AND(store_scr, w_in_range(n, d_code, 0, S)) if S < (1 << p.DB) else store_scr
        pend = n.OR(store_hold, in_scr)
        new['pend'][d + 2] = pend
        new['pval'][d + 2] = n.AND(pend, alu)
        pkind = w_mux(n, in_scr, idx, [0] * p.PK)
        for j in range(p.PK):
            new['pkind'][(d + 2) * p.PK + j] = pkind[j]
    for i, b in enumerate(psel):
        n.set_output(('psel', i), b)
    for i, b in enumerate(xaddr):
        n.set_output(('laddr', i), b)
    n.set_output(('arrive', 0), any_arrive)
    return new


@lru_cache(maxsize=8)
def cached(p):
    from .netlist import Compiled
    net = build(p)
    return net, Compiled(net)


def identity(p):
    net, comp = cached(p)
    return dict(family='G', params=asdict(p), Q=p.Q, U=p.U, width=width(p), schema=schema(p),
                radius=5, gates=len(comp.gates), netlist_sha256=comp.digest)
