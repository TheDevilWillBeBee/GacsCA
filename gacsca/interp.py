"""Interpretation phase (stage 2, finite tower): the level-0 colony computes the new
simulation-structure tracks of its simulated level-1 cell (offset c=0) and of its copies of the
neighbours' tracks (c=+-1) by interpreting the level-1 op table `prog_up` at the simulated age
(register simage) and address (register simaddr).  See Report/design_selfsim.md (stage 2).

Positions: the simulated state lives at addresses [b0, b0+K); track t copy r at
pos(t, r) = base + t*R + r.  The level-0 cell at pos(t, r) is the *writer* for track t of the
simulated cell c = r - h (h = (R-1)/2).  Latched data are held on temp tracks; the passes move a
bus track by D cells per step in both directions, and each cell latches the bits it needs from
offset o at the computed pass step.
"""
import numpy as np
from .microcode import Compiler, Layout, Tracks, Op, Program

NMAX = None       # no fixed dispatch cap; program/work-period and scratch limits still apply
NSLOT = 3         # latch slots per resource class (S-slots for value ops, SHSRC for shift ops)


def slot_of(ops1, i):
    """resource-class slot of op i among the ops active at one age: shift-kind ops use SHSRC
    slots, the others S-slots (sweeps/bcasts also use the shared SIGk/CARRYk tracks)."""
    k = ops1[i].kind
    cls = (lambda o: o.kind in ("SHIFT", "RSHIFT"))
    return sum(1 for j in range(i) if cls(ops1[j]) == cls(ops1[i]))


def validate_resource_slots(prog, label="upper"):
    """Large constant/reset batches use no operand slots; data operations do.

    Preserve the existing resource numbering (including preceding constants),
    rather than silently changing the represented interpreter's scratch state.
    Concurrency can increase only at an instruction's starting age.
    """
    for age in {op.t0 for op in prog.ops}:
        active = prog.ops_at(age)
        if any(op.kind not in ("CONST", "RESET", "BUSLATCH_INT") and slot_of(active, i) >= NSLOT
               for i, op in enumerate(active)):
            raise ValueError(f"too many concurrent {label} value instructions")


# level-0 op kinds of the interpretation phase
IKINDS = ("IINIT", "ILATCH", "ICHAIN", "IBC", "IEVAL", "IWF", "BUSLATCH_INT", "REGWIN")
INTERPRETABLE = ("CONST", "MOV", "BITOP", "SHIFT", "RSHIFT", "SWEEP_INIT", "SWEEP", "BCAST_INIT", "BCAST", "BUSLATCH_INT", "REGWIN", "RESET", "IINIT")


class InterpCtx:
    """Everything the engine needs to interpret level-1 ops."""

    def __init__(self, L: Layout, T: Tracks, prog_up: Program, L_up: Layout, trickle_up, names, regwin_up=(0, 0), inner=None):
        if getattr(prog_up, "nested_register_bits", 0):
            raise NotImplementedError("encoding an upper state with a second control pair is not yet supported")
        self.inner = inner
        if inner is not None and (inner.L is not L_up or inner.T.names != T.names or inner.inner is not None):
            raise ValueError("nested context must describe the exact middle layout and matching one-level track registry")
        supported = set(INTERPRETABLE) | ({"IBC", "ICHAIN", "ILATCH", "IEVAL"} if inner is not None else set())
        unsupported = {op.kind for op in prog_up.ops} - supported
        if unsupported:
            raise NotImplementedError(f"upper instruction kinds not interpretable: {sorted(unsupported)}")
        validate_resource_slots(prog_up)
        if inner is not None and any(op.kind in ("ICHAIN", "ILATCH", "IEVAL") for op in prog_up.ops):
            validate_resource_slots(inner.prog_up, "inner")
        if inner is not None and any(op.kind == "IEVAL" for op in prog_up.ops):
            if any(op.kind == "IEVAL" and op.param < 0 for op in prog_up.ops):
                raise ValueError("nested IEVAL instruction index must be nonnegative")
            if getattr(inner, "regwin_upup", (0, 0)) != (0, 0):
                raise NotImplementedError("nested IEVAL with nonempty deeper REGWIN is not implemented")
            for age in {o.t0 for o in prog_up.ops}:
                active = prog_up.ops_at(age)
                if any(o.kind == "IEVAL" for o in active) and len(active) != 1:
                    raise NotImplementedError("nested IEVAL requires a dedicated instruction age")
        computed_moves = [o for o in prog_up.ops if o.kind == "MOV" and o.param2]
        self.computed_move_addresses = sorted({o.lo for o in computed_moves})
        if (len(self.computed_move_addresses) > 2 or
                any(o.hi != o.lo + 1 or o.dst != T["INFO"] or o.param2 != 1
                    or not 0 <= o.lo < L.Qs for o in computed_moves)):
            raise NotImplementedError("interpreted computed-address MOV supports at most two singleton Info signals")
        self.L, self.T, self.prog_up, self.L_up, self.trickle_up = L, T, prog_up, L_up, trickle_up
        self.regwin_up = regwin_up
        self.R, self.h, self.NT = T.R, (T.R - 1) // 2, T.NT
        self.base = L.b0 + L.track_base
        self.trng = (self.base, self.base + T.NT * T.R)
        self.n = names          # dict of temp track names -> track index
        self.D_up = prog_up.D
        self.JI = self.h + self.D_up
        if self.R not in (3, 5) or not 1 <= self.D_up <= 5 - 2 * self.h:
            raise ValueError("redundancy and op reach must preserve interaction radius five")
        nested_init = [op for op in prog_up.ops if op.kind == "IINIT"]
        if nested_init and (L_up.tracks.R != self.R or L_up.tracks.NT != self.NT):
            raise ValueError("nested IINIT requires matching track registries and redundancy")
        for op in nested_init:
            if (op.src is None or not 0 <= op.src < self.NT or
                    op.dst is None or not 0 <= op.dst < self.NT or
                    abs(op.param) > self.h or op.param2 not in (0, 1) or
                    (not op.param2 and abs(op.param) > self.D_up)):
                raise ValueError("nested IINIT must use a valid slot and radius-safe routed source")
        for op in prog_up.ops:
            if op.kind == "BUSLATCH_INT" and (op.param != 0 or op.src is None or not 0 <= op.src < self.NT or op.param2 not in (-1, 1)):
                raise ValueError("nested BUSLATCH_INT requires a source track and direction +/-1")

    def pos(self, t, r):
        return self.base + t * self.R + r


def writes(op, T, ctx=None):
    k = op.kind
    if k == "RESET":
        return set(range(op.dst, op.param))
    if k in ("CONST", "MOV", "BITOP", "SHIFT", "RSHIFT", "BCAST_INIT", "REGWIN", "IINIT"):
        return {op.dst}
    if k == "SWEEP_INIT":
        return {T["SIG"], op.dst}
    if k == "SWEEP":
        s = {T["SIG"], T["ACC"]}
        if op.dst is not None: s.add(op.dst)
        return s
    if k == "BCAST":
        return {op.dst, T["SIG"]}
    if k == "IBC" and ctx is not None and ctx.inner is not None:
        return {ctx.inner.n["BFOUND"], ctx.inner.n["BVAL"]}
    if k == "ICHAIN" and ctx is not None and ctx.inner is not None:
        return {ctx.inner.n[f"CARRY{k}"] for k in range(2, ctx.inner.D_up + 1)}
    if k == "ILATCH" and ctx is not None and ctx.inner is not None:
        names = [f"S{i}{j}" for i in range(3) for j in range(3)]
        names += [f"SHSRC{i}" for i in range(3)]
        names += [f"{prefix}{k}" for prefix in ("SIG", "CARRY") for k in range(1, 4)]
        return {ctx.inner.n[n] for n in names + ["BLB", "WFB"]}
    if k == "IEVAL" and ctx is not None and ctx.inner is not None:
        return {T["HOLD"]}
    return set()


def _nested_bcast_cases(ctx, op1, a1, g2, sa2):
    """Guards of a middle IBC, using raw holder controls, not repaired output.

    Each yielded case reads SIGk/CARRYk/BFOUND at the represented target itself.
    The physical outer pass transports those bits; this helper only selects
    immutable table metadata and does not call a simulated transition.
    """
    inner = ctx.inner
    inrng, r2, t2, c2 = _cell_geometry(inner, a1)
    a2 = np.mod(sa2 + c2, inner.L.Qs)
    oo = op1.param - c2
    guarded = inrng & (a1 >= op1.lo) & (a1 < op1.hi)
    for age in np.unique(g2[guarded]):
        for op2 in inner.prog_up.ops_at(int(age)):
            if op2.kind != "BCAST":
                continue
            direction = op2.param or -1
            wr = (t2 == op2.dst) | (t2 == inner.T["SIG"])
            for kk in range(1, inner.D_up + 1):
                sh = kk if direction < 0 else -kk
                mask = guarded & (g2 == age) & wr & (oo == sh)
                mask &= (a2 + sh >= op2.lo) & (a2 + sh < op2.hi)
                if mask.any():
                    yield mask, kk, direction


def _nested_chain_cases(ctx, op1, a1, t, g2, sa2):
    """Last eligible inner SWEEP for each output carry, matching old-state reads.

    Distinct active SWEEPs can write the same carry hypothesis. Their writes
    use the same old repaired state, so the final eligible instruction wins;
    choose it before transporting its three operands, not by arrival time.
    """
    inner = ctx.inner
    if inner.D_up == 1:
        return
    inrng, _, t2, c2 = _cell_geometry(inner, a1)
    a2 = np.mod(sa2 + c2, inner.L.Qs)
    oo = op1.param - c2
    guarded = inrng & (a1 >= op1.lo) & (a1 < op1.hi)
    for age in np.unique(g2[guarded]):
        ops2 = inner.prog_up.ops_at(int(age))
        claimed = np.zeros_like(guarded)
        for i0 in reversed(range(len(ops2))):
            op2 = ops2[i0]
            if op2.kind != "SWEEP":
                continue
            i2 = slot_of(ops2, i0)
            if i2 >= NSLOT:
                raise ValueError("too many concurrent inner value instructions")
            wr = np.isin(t2, list(writes(op2, inner.T)))
            for kk in range(2, inner.D_up + 1):
                mask = guarded & (g2 == age) & wr & (oo < 0) & (oo > -kk)
                mask &= (t == inner.n[f"CARRY{kk}"]) & ~claimed
                if mask.any():
                    claimed |= mask
                    yield mask, kk, i2, op2, _kbit(op2.param, a2 + oo - op2.lo)


def _nested_latch_source(ctx, op1, a1, t, g1, g2, sa2):
    """Return (write mask, middle BUS source offset) for a nested ILATCH.

    All requests read the same repaired middle BUS, but possibly different
    nearby cells. Later requests overwrite earlier ones exactly as in the
    middle transition; operand arrival at the outer layer cannot reorder them.
    This is metadata/geometry selection only, not a simulated state oracle.
    """
    inner = ctx.inner
    inrng, r2, t2, c2 = _cell_geometry(inner, a1)
    a2 = np.mod(sa2 + c2, inner.L.Qs)
    guarded = (a1 >= op1.lo) & (a1 < op1.hi)
    hit = np.zeros_like(guarded)
    relative = np.zeros_like(a1)

    def consider(mask, X, target):
        tt, j, ok = _latch_time(a1, X, op1.param2, ctx.D_up)
        take = guarded & mask & (t == target) & ok & (tt == g1 - op1.t0)
        hit[take] = True
        relative[take] = (-op1.param2 * j)[take]

    for age in np.unique(g2[guarded]):
        ops2 = inner.prog_up.ops_at(int(age))
        gm = g2 == age
        for i0, op2 in enumerate(ops2):
            if op2.kind == "BUSLATCH_INT":
                for field, source_field in (("SIMAGE", "AGE"), ("SIMADDR", "ADDR")):
                    lo, hi = inner.L.frange(field)
                    slo, shi = inner.L_up.frange(source_field)
                    for bit in range(min(hi - lo, shi - slo)):
                        tt, j, ok = _latch_time(sa2, slo + bit, op2.param2, inner.D_up)
                        sel = gm & (a1 == lo + bit) & (sa2 >= op2.lo) & (sa2 < op2.hi)
                        sel &= ok & (tt == g2 - op2.t0) & (-op2.param2 * j == op1.param)
                        consider(sel, inner.pos(op2.src, inner.h), inner.n["BLB"])
                continue
            i2 = slot_of(ops2, i0)
            for mask, X, target in _needs(inner, op2, i2, inner.T, r2, t2, c2, a2, op1.param, inner.D_up):
                consider(gm & inrng & mask, X, target)
    # The direct middle latch performs workspace requests even at an inner
    # Age with no active table entry, and after all ordinary operand requests.
    for field, offset in (("WF1", inner.L.Qs - 3), ("WF2", 3)):
        sel = (a1 == inner.L.frange(field)[0]) & (offset - sa2 == op1.param)
        consider(sel, inner.pos(inner.T["INFO"], inner.h), inner.n["WFB"])
    return hit, relative


# ---------------------------------------------------------------- compile
def compile_iphase(C: Compiler, ctx: InterpCtx, al, F1N, load_output_registers=True):
    """Emit the interpretation phase.  al: temp allocator (Alloc).  Returns dict of temp names."""
    T, L, R, h = ctx.T, ctx.L, ctx.R, ctx.h
    trng = ctx.trng
    Q = L.Q
    names = {}
    for nm in ["VT", "BUS", "SA", "SB", "SIG1", "SIG2", "SIG3", "CARRY1", "CARRY2", "CARRY3", "BFOUND", "BVAL",
               "SHSRC0", "SHSRC1", "SHSRC2", "S00", "S01", "S02", "S10", "S11", "S12", "S20", "S21", "S22", "BLB", "WFB"]:
        names[nm] = al.get()
    ctx.n = {k: T[v] for k, v in names.items()}
    ctx.n["F1N"] = T[F1N]
    for i in range(len(ctx.computed_move_addresses)):
        names[f"CM{i}"] = al.get()
        ctx.n[f"CM{i}"] = T[names[f"CM{i}"]]
    n_pass = (T.NT * R - 1 + C.D - 1) // C.D + 1
    # clear latch state
    for nm in ["SIG1", "SIG2", "SIG3", "CARRY1", "CARRY2", "CARRY3", "BFOUND", "BVAL", "SHSRC0", "SHSRC1", "SHSRC2",
               "S00", "S01", "S02", "S10", "S11", "S12", "S20", "S21", "S22", "BLB", "WFB", "BUS"]:
        C.const(names[nm], 0, rng=(0, Q), advance=False)
    C.t += 1
    # Each simulated holder already has its computed Address in HOLD. Compute
    # guards for the Info copies it owns from that value plus the copy offset;
    # never inspect a neighbor's computed local rule (which could exceed r=5).
    for i, target in enumerate(ctx.computed_move_addresses):
        guard = names[f"CM{i}"]
        C.const(guard, 0)
        for r in range(R):
            c = r - h
            C.sweep("EQC", L.frange("ADDR"), src="HOLD", const=(target - c) % L.Qs, acc_init=1)
            _, hi = L.frange("ADDR")
            pos = ctx.pos(T["INFO"], r)
            C.bcast(names["SA"], (L.b0, hi), right=(hi - 1, pos + 1))
            C.mov(guard, names["SA"], rng=(pos, pos + 1))
    for o in range(-ctx.JI, ctx.JI + 1):
        compile_repaired_tracks(C, ctx, o, names)
        if -h <= o <= h:
            if abs(o) > C.D:
                # At R=5,D=1 a direct offset-two IINIT would exceed the
                # physical radius after repair/redistribution. Route it.
                C.shift(names["SA"], names["VT"], o, trng)
                C.emit("IINIT", dst=T["HOLD"], src=T[names["SA"]], param=o, param2=1, rng=trng)
            else:
                C.emit("IINIT", dst=T["HOLD"], src=T[names["VT"]], param=o, rng=trng)
            C.t += 1
        for dirn in (+1, -1):
            C.mov(names["BUS"], names["VT"], rng=(0, Q))
            C.emit("RSHIFT", dur=n_pass, dst=T[names["BUS"]], src=T[names["BUS"]], param=dirn * C.D, rng=(0, Q))
            C.emit("ILATCH", dur=n_pass, param=o, param2=dirn, rng=(0, Q))
            C.t += n_pass
        C.emit("ICHAIN", param=o, rng=trng); C.t += 1
        C.emit("IBC", param=o, rng=trng); C.t += 1
    C.const(names["BUS"], 0, rng=(0, Q))
    nmax = max(len(ctx.prog_up.ops_at(a)) for a in range(ctx.prog_up.U))
    for i in range(nmax):
        C.emit("IEVAL", param=i, rng=(0, Q)); C.t += 1
    # free the pass temporaries (BUS is kept for the register load, WFB for the IWF op)
    for nm in names:
        if nm not in ("BUS", "WFB"): al.put(names[nm])
    # level-1 wipes (holder form): mail bits if F1N; everything if F1N and the address changed
    ADDRCH = al.get()
    C.sweep("EQF", L.frange("ADDR"), src="HOLD", src2=T.names[T.arg(0)], acc_init=1)
    lo, hi = L.frange("ADDR")
    C.bcast(ADDRCH, (L.b0, hi), right=(hi - 1, trng[1]))
    F1T = al.get()
    C.spread(L.frange("F1")[0], F1T, (L.b0, trng[1]), F1N)
    for tname in ("MAILL", "MAILR"):
        p0 = ctx.pos(T[tname], 0)
        C.bitop("HOLD", lambda f, x, _: 0 if f else x, F1T, "HOLD", rng=(p0, p0 + R), advance=False)
    C.t += 1
    C.bitop("HOLD", lambda f, eq, x: 0 if (f & (1 - eq)) else x, F1T, ADDRCH, "HOLD", rng=trng)   # ADDRCH = [address unchanged]
    al.put(ADDRCH, F1T)
    # The repaired simulated Address/Age in HOLD may differ from the input
    # registers. Compute flags from those fields, rather than assuming a
    # healthy simulated cell (the old IWF shortcut did exactly that).
    compile_workspace_flags(C, ctx, al, F1N)
    al.put(names["WFB"])
    if load_output_registers:
        compile_register_load(C, "HOLD", names["BUS"])
    al.put(names["BUS"])
    return names


def compile_register_load(C, source, bus, nested=False):
    """Load encoded AGE/ADDR into each holder's integer controls using local mail.

    Compressed mode loads new HOLD at period end; Gray mode loads the voted
    input immediately before interpretation, after its stage-five reset.
    """
    if nested:
        # Load raw represented controls from the caller's input bank. Pair one
        # remains the represented AGE/ADDR; pair two is its own SIMAGE/SIMADDR.
        first = compile_register_load(C, source, bus)
        C.prog.nested_register_bits = max(16, C.L.fields["SIMAGE"][1], C.L.fields["SIMADDR"][1])
        second = _compile_register_pair(C, source, bus, ("SIMAGE", "SIMADDR"), 1)
        C.reg_window = (first[0], second[1])
        return C.reg_window
    return _compile_register_pair(C, source, bus, ("AGE", "ADDR"), 0)


def _compile_register_pair(C, source, bus, fields, pair):
    T, L, Q = C.T, C.L, C.L.Q
    C.const(bus, 0, rng=(0, Q))
    C.mov(bus, source, rng=L.frange(fields[0]), advance=False)
    C.mov(bus, source, rng=L.frange(fields[1]))
    np2 = (Q - 1 + C.D - 1) // C.D + 1
    C.reg_window = (C.t, C.t + 2 * np2 + 3)
    for dirn in (+1, -1):
        if dirn < 0:
            C.const(bus, 0, rng=(0, Q))
            C.mov(bus, source, rng=L.frange(fields[0]), advance=False)
            C.mov(bus, source, rng=L.frange(fields[1]))
        C.emit("RSHIFT", dur=np2, dst=T[bus], src=T[bus], param=dirn * C.D, rng=(0, Q))
        C.emit("BUSLATCH_INT", dur=np2, src=T[bus], param=pair, param2=dirn, rng=(0, Q))
        C.t += np2
    C.const(bus, 0, rng=(0, Q))
    return C.reg_window


def compile_repaired_tracks(C, ctx, o, names):
    """Align and majority-repair the simulated track copies at center slots.

    Fivefold repair uses two bitwise full adders. Only four existing scratch
    tracks are needed; BUS is free until the ensuing transport pass. Shifts
    of two bit positions are split into two physical steps when D=1.
    """
    T, trng = ctx.T, ctx.trng
    a, b, total, extra = (names[k] for k in ("SA", "SB", "VT", "BUS"))
    majority = lambda x, y, z: (x & y) | (x & z) | (y & z)
    if ctx.R == 3:
        C.emit("SHIFT", dst=T[a], src=T.arg(o + 1), param=1, param2=0, rng=trng)
        C.emit("SHIFT", dst=T[b], src=T.arg(o - 1), param=-1, param2=0, rng=trng)
        C.t += 1
        C.bitop(total, majority, a, T.names[T.arg(o)], b, rng=trng)
        return
    C.shift(a, T.names[T.arg(o + 2)], 2, trng)
    C.shift(b, T.names[T.arg(o + 1)], 1, trng)
    C.bitop(total, lambda x, y, z: x ^ y ^ z, a, b, T.names[T.arg(o)], rng=trng, advance=False)
    C.bitop(a, majority, a, b, T.names[T.arg(o)], rng=trng)
    C.shift(b, T.names[T.arg(o - 1)], -1, trng)
    C.shift(extra, T.names[T.arg(o - 2)], -2, trng)
    C.bitop(total, lambda x, y, z: x ^ y ^ z, b, extra, total, rng=trng, advance=False)
    C.bitop(b, majority, b, extra, total, rng=trng)
    C.bitop(total, lambda c1, c2, s: (c1 & c2) | ((c1 ^ c2) & s), a, b, total, rng=trng)


def compile_workspace_flags(C, ctx, al, F1N):
    """Match the engine's WF rule even when simulated local fields are damaged.

    Read current repaired INFO from the gathered neighbour states, and use
    computed Address/Age/Flag1 in HOLD. The separate question of Gray's
    'computed SimBit' timing is documented in the source audit.
    """
    from .trlocal import TrLocal
    T, L = ctx.T, ctx.L
    tl = TrLocal(C)
    tl.al = al
    in_window, below_end, equal, value = [al.get() for _ in range(4)]
    lo, hi = ctx.trickle_up
    tl.ltc_dec("HOLD", L.frange("AGE"), lo, in_window)
    tl.ltc_dec("HOLD", L.frange("AGE"), hi, below_end)
    C.bitop(in_window, lambda a, b, _: (1 - a) & b, in_window, below_end, rng=tl.FR)
    for field, target, offsets in (("WF1", L.Qs - 3, range(-2, 3)),
                                    ("WF2", 3, range(-1, 4))):
        aw = L.frange(field)[0]
        wr = (aw, aw + 1)
        C.const(value, 0, rng=wr)
        for o in offsets:
            # Source bit of target o is held at o+h-r in copy slot r.
            votes = [al.get() for _ in range(ctx.R)]
            for r, track in enumerate(votes):
                source = ctx.pos(T["INFO"], r)
                C.const(track, 0, rng=(0, L.Q))
                C.emit("MOV", dst=T[track], src=T.arg(o + ctx.h - r), rng=(source, source + 1))
                C.t += 1
                C.shift(track, track, aw - source, (min(aw, source), max(aw, source) + 1))
            if ctx.R == 3:
                C.bitop(votes[0], lambda a, b, c: (a & b) | (a & c) | (b & c), *votes, rng=wr)
            else:
                # Full-adder majority, keeping sums and carries in consumed inputs.
                C.bitop(votes[1], lambda a, b, c: a ^ b ^ c, *votes[:3], rng=wr, advance=False)
                C.bitop(votes[0], lambda a, b, c: (a & b) | (a & c) | (b & c), *votes[:3], rng=wr)
                C.bitop(votes[2], lambda a, b, c: a ^ b ^ c, votes[3], votes[4], votes[1], rng=wr, advance=False)
                C.bitop(votes[1], lambda a, b, c: (a & b) | (a & c) | (b & c), votes[3], votes[4], votes[1], rng=wr)
                C.bitop(votes[0], lambda a, b, c: (a & b) | ((a ^ b) & c), *votes[:3], rng=wr)
            tl.eqc_dec("HOLD", L.frange("ADDR"), target - o, equal)
            C.bitop(value, lambda old, eq, bit: old | (eq & bit), value, equal, votes[0], rng=wr)
            al.put(*votes)
        if field == "WF1":
            C.bitop("HOLD", lambda v, win, _: v & win, value, in_window, rng=wr)
        else:
            C.bitop("HOLD", lambda v, win, f: v & win & (1 - f), value, in_window, F1N, rng=wr)
    al.put(in_window, below_end, equal, value)


# ---------------------------------------------------------------- semantics (NumPy)
def _latch_time(p, X, dirn, D):
    """pass step tau and neighbour offset j (read BUS[p - dirn*j]) at which the bit at X passes p."""
    if dirn > 0:
        d = p - X
    else:
        d = X - p
    j = np.mod(d, D)
    tau = (d - j) // D
    ok = d >= 0
    return tau, j, ok


def _cell_geometry(ctx, addr):
    """slot r, track t, offset c for positions in the track range; masks."""
    q = addr - ctx.base
    inrng = (q >= 0) & (q < ctx.NT * ctx.R)
    qq = np.where(inrng, q, 0)
    r = qq % ctx.R; t = qq // ctx.R; c = r - ctx.h
    return inrng, r, t, c


def apply_iop(P, V, S, m, am, op, tau, ctx: InterpCtx, T, D):
    """Interpretation ops.  P: new primaries (B,L,NT) being built; V: repaired; S: state dict;
    m: mask (age & range); am: age mask; tau: age - op.t0."""
    k = op.kind
    addr, simage, simaddr = S["addr"], S["simage"], S["simaddr"]
    n = ctx.n if ctx is not None else None
    B, Lt, NT = V.shape
    if k == "REGWIN":
        lo1, hi1 = ctx.regwin_up if ctx is not None else (0, 0)
        val = ((simage >= lo1) & (simage < hi1)).astype(np.uint8)
        P[:, :, op.dst][m] = val[m]
        return
    if k == "BUSLATCH_INT":
        _buslatch_int(P, V, S, m, op, tau, ctx, D)
        return
    inrng, r, t, c = _cell_geometry(ctx, addr)
    a1 = np.mod(simaddr + c, ctx.L.Qs)              # simulated address of the cell at offset c
    if k == "IINIT":
        o = op.param
        sel = m & inrng & (c == o)
        val = V[:, :, op.src] if op.param2 else np.roll(V[:, :, op.src], o, axis=1)
        P[:, :, op.dst][sel] = val[sel]
        return
    # level-1 active ops per distinct simage value
    for g1 in np.unique(simage[m]) if m.any() else []:
        gm = m & (simage == g1)
        ops1 = ctx.prog_up.ops_at(int(g1))
        if k == "ILATCH":
            _ilatch(P, V, S, gm, op, tau, ctx, ops1, inrng, r, t, c, a1, D)
        elif k == "ICHAIN":
            _ichain(P, V, gm, op, ctx, ops1, inrng, r, t, c, a1)
        elif k == "IBC":
            _ibc(P, V, gm, op, ctx, ops1, inrng, r, t, c, a1)
        elif k == "IEVAL":
            _ieval(P, V, S, gm, op, ctx, ops1, inrng, r, t, c, a1)
        elif k == "IWF":
            _iwf(P, V, S, gm, ctx)


def _needs(ctx, op1, i, T, r, t, c, a1, o, D1):
    """list of (mask over cells, X position, target track) that cells need from absolute offset o
    for level-1 op op1 in slot i.  r,t,c,a1: per-cell arrays."""
    n = ctx.n; needs = []
    if op1.kind in ("CONST", "RESET"):
        return needs
    oo = o - c                                          # relative offset of o from the cell's simulated cell
    w = writes(op1, T, ctx)
    wr = np.isin(t, list(w)) if w else np.zeros_like(t, bool)
    assert i < NSLOT, "too many concurrent ops of one class"
    Si = [n[f"S{i}0"], n[f"S{i}1"], n[f"S{i}2"]]
    k = op1.kind
    ph = lambda tr: ctx.pos(tr, ctx.h)
    if k in ("CONST", "RESET"):
        return needs
    if k in ("MOV", "BITOP", "BCAST_INIT"):
        srcs = [op1.src, op1.src2, op1.src3]
        for jx, s in enumerate(srcs):
            if s is not None:
                needs.append((wr & (oo == 0), ph(s), Si[jx]))
        return needs
    if k == "IINIT":
        # Nested initialization reads one already-repaired middle-level bit.
        # Routed outer copies (param2) read locally; others read x-param.
        source_offset = 0 if op1.param2 else -op1.param
        needs.append((wr & (oo == source_offset), ph(op1.src), Si[0]))
        return needs
    if k in ("SHIFT", "RSHIFT"):
        d = op1.param
        needs.append((wr & (oo == -d), ph(op1.src), n[f"SHSRC{i}"]))
        return needs
    if k == "SWEEP_INIT":
        return needs
    if k == "SWEEP":
        # own: src, src2 -> S0,S1 ; own SIG -> S2 ; at oo=-kk: SIG->SIGk, ACC->CARRYk ; intermediates src,src2 -> S0,S1 (consumed by ICHAIN)
        if op1.src is not None: needs.append((wr & (oo == 0), ph(op1.src), Si[0]))
        if op1.src2 is not None: needs.append((wr & (oo == 0), ph(op1.src2), Si[1]))
        needs.append((wr & (oo == 0), ph(T["SIG"]), Si[2]))
        for kk in range(1, D1 + 1):
            needs.append((wr & (oo == -kk), ph(T["SIG"]), n[f"SIG{kk}"]))
            needs.append((wr & (oo == -kk), ph(T["ACC"]), n[f"CARRY{kk}"]))
        for kk in range(1, D1):    # intermediate cells at oo = -kk (kk < D1)
            if op1.src is not None: needs.append((wr & (oo == -kk), ph(op1.src), Si[0]))
            if op1.src2 is not None: needs.append((wr & (oo == -kk), ph(op1.src2), Si[1]))
        return needs
    if k == "BCAST":
        dirn = -1 if op1.param == 0 else op1.param
        needs.append((wr & (oo == 0), ph(T["SIG"]), Si[2]))
        for kk in range(1, D1 + 1):
            sh = kk if dirn < 0 else -kk
            needs.append((wr & (oo == sh), ph(T["SIG"]), n[f"SIG{kk}"]))
            needs.append((wr & (oo == sh), ph(op1.dst), n[f"CARRY{kk}"]))
        return needs
    if k == "BUSLATCH_INT":
        # writer cells: local-range positions of SIMAGE/SIMADDR fields (c=0 only); need BUS of level-1 cell a1 - j1
        return needs   # handled in _ilatch specially
    return needs


def _ilatch(P, V, S, gm, op, tau, ctx, ops1, inrng, r, t, c, a1, D):
    T = ctx.T; n = ctx.n
    o, dirn = op.param, op.param2
    addr = S["addr"]
    bus = V[:, :, n["BUS"]]
    D1 = ctx.D_up
    for i0, op1 in enumerate(ops1):
        i = slot_of(ops1, i0)
        if op1.kind == "BUSLATCH_INT":
            _ilatch_buslatch(P, V, S, gm, op, tau, ctx, op1, D)
            continue
        if op1.kind == "IBC":
            wr = np.isin(t, list(writes(op1, T, ctx)))
            for mask, kk, _ in _nested_bcast_cases(ctx, op1, a1, S["simage2"], S["simaddr2"]):
                sources = (ctx.inner.n[f"SIG{kk}"], ctx.inner.n[f"CARRY{kk}"], ctx.inner.n["BFOUND"])
                for jx, source in enumerate(sources):
                    tt, j, ok = _latch_time(addr, ctx.pos(source, ctx.h), dirn, D)
                    hit = gm & inrng & wr & mask & (o == c) & ok & (tt == tau)
                    for jj in range(D):
                        hj = hit & (j == jj)
                        P[:, :, n[f"S{i}{jx}"]][hj] = np.roll(bus, dirn * jj, axis=1)[hj]
            continue
        if op1.kind == "ICHAIN":
            for mask, kk, i2, _, _ in _nested_chain_cases(ctx, op1, a1, t, S["simage2"], S["simaddr2"]):
                sources = (ctx.inner.n[f"S{i2}0"], ctx.inner.n[f"S{i2}1"], ctx.inner.n[f"CARRY{kk}"])
                for jx, source in enumerate(sources):
                    tt, j, ok = _latch_time(addr, ctx.pos(source, ctx.h), dirn, D)
                    hit = gm & inrng & mask & (o == c) & ok & (tt == tau)
                    for jj in range(D):
                        hj = hit & (j == jj)
                        P[:, :, n[f"S{i}{jx}"]][hj] = np.roll(bus, dirn * jj, axis=1)[hj]
            continue
        if op1.kind == "ILATCH":
            select, relative = _nested_latch_source(ctx, op1, a1, t, S["simage"], S["simage2"], S["simaddr2"])
            X = ctx.pos(ctx.inner.n["BUS"], ctx.h)
            tt, j, ok = _latch_time(addr, X, dirn, D)
            hit = gm & inrng & select & (o == c + relative) & ok & (tt == tau)
            for jj in range(D):
                hj = hit & (j == jj)
                P[:, :, n[f"S{i}0"]][hj] = np.roll(bus, dirn * jj, axis=1)[hj]
            continue
        if op1.kind == "IEVAL":
            from .nested_eval import selected, operands
            for clock_guard, op2, slot2 in selected(ctx, op1, S["simage2"]):
                select = gm & inrng & (t == T["HOLD"]) & clock_guard & (o == c)
                select &= (a1 >= op1.lo) & (a1 < op1.hi)
                for source, target in operands(ctx, op2, slot2):
                    tt, j, ok = _latch_time(addr, ctx.pos(source, ctx.h), dirn, D)
                    hit = select & ok & (tt == tau)
                    for jj in range(D):
                        hj = hit & (j == jj)
                        P[:, :, target][hj] = np.roll(bus, dirn * jj, axis=1)[hj]
            continue
        for (mask, X, target) in _needs(ctx, op1, i, T, r, t, c, a1, o, D1):
            sel = gm & inrng & mask
            if not sel.any(): continue
            tt, j, ok = _latch_time(addr, X, dirn, D)
            hit = sel & ok & (tt == tau)
            if not hit.any(): continue
            for jj in range(D):
                hj = hit & (j == jj)
                if hj.any():
                    val = np.roll(bus, dirn * jj, axis=1)     # BUS[p - dirn*jj]
                    P[:, :, target][hj] = val[hj]
    # WF bits: the WF writer cells latch the INFO bit of the level-1 cell at offset (Qs-3)-simaddr / 3-simaddr
    Qs = ctx.L.Qs
    for fname, off in (("WF1", Qs - 3), ("WF2", 3)):
        pw = ctx.L.frange(fname)[0]
        need_o = off - S["simaddr"]
        sel = gm & (addr == pw) & (need_o == o)
        if sel.any():
            X = ctx.pos(T["INFO"], ctx.h)
            tt, j, ok = _latch_time(addr, X, dirn, D)
            hit = sel & ok & (tt == tau)
            for jj in range(D):
                hj = hit & (j == jj)
                if hj.any():
                    val = np.roll(bus, dirn * jj, axis=1)
                    P[:, :, n["WFB"]][hj] = val[hj]


def _ilatch_buslatch(P, V, S, gm, op, tau, ctx, op1, D):
    """The level-1 cell (address a1 = simaddr) executes BUSLATCH_INT at level-1 pass step
    tau1 = simage - op1.t0 with direction op1.param2: bit i of a level-1 field (positions in
    L_up) is read from the level-1 BUS of the cell at relative offset -dir1*j1.  Writer: level-0
    cells at the SIMAGE/SIMADDR field positions (c=0 only)."""
    T = ctx.T; n = ctx.n; L, Lup = ctx.L, ctx.L_up
    o, dirn = op.param, op.param2
    addr, simage, simaddr = S["addr"], S["simage"], S["simaddr"]
    D1 = ctx.D_up
    tau1 = simage - op1.t0
    dir1 = op1.param2
    bus = V[:, :, n["BUS"]]
    for fld, src_fld in (("SIMAGE", "AGE"), ("SIMADDR", "ADDR")):
        plo, phi = L.frange(fld)           # writer positions (level-0 layout)
        slo, shi = Lup.frange(src_fld)     # source field positions in the level-1 colony
        w = min(phi - plo, shi - slo)
        for i in range(w):
            pw = plo + i; X1 = slo + i
            sel = gm & (addr == pw) & (simaddr >= op1.lo) & (simaddr < op1.hi)
            if not sel.any(): continue
            # level-1 timing: cell a1 reads BUS_1[a1 - dir1*j1] at tau1 == (d - j1)/D1, d = dir1*(a1 - X1)
            d = dir1 * (simaddr - X1)
            j1 = np.mod(d, D1); tt1 = (d - j1) // D1
            okk = (d >= 0) & (tt1 == tau1)
            rel = -dir1 * j1                       # relative offset of the level-1 cell whose BUS is read
            sel2 = sel & okk & (rel == o)
            if not sel2.any(): continue
            X = ctx.pos(op1.src, ctx.h)
            tt, j, ok = _latch_time(addr, X, dirn, D)
            hit = sel2 & ok & (tt == tau)
            for jj in range(D):
                hj = hit & (j == jj)
                if hj.any():
                    val = np.roll(bus, dirn * jj, axis=1)
                    P[:, :, n["BLB"]][hj] = val[hj]


def _kbit(const, a):
    sh = np.clip(a, 0, 62)
    return np.where((a >= 0) & (a < 63), (const >> sh) & 1, 0)


def _chain(kind, cin, sv, s2v, kb):
    if kind == "EQC": return None, cin & (sv == kb)
    if kind == "EQF": return None, cin & (sv == s2v)
    if kind == "ORF": return None, cin | sv
    if kind == "ANDF": return None, cin & sv
    if kind == "LTC": return None, ((1 - sv) & kb) | ((sv == kb) & cin)
    if kind == "ADDC":
        return sv ^ kb ^ cin, (sv & kb) | (sv & cin) | (kb & cin)
    raise ValueError(kind)


def _ichain(P, V, gm, op, ctx, ops1, inrng, r, t, c, a1):
    """after the passes for absolute offset o: advance the sweep carry hypotheses through the
    intermediate cell at relative offset oo = o - c (for hypotheses k > -oo)."""
    T = ctx.T; n = ctx.n; o = op.param; D1 = ctx.D_up
    for i0, op1 in enumerate(ops1):
        if op1.kind != "SWEEP": continue
        i = slot_of(ops1, i0)
        oo = o - c
        wr = np.isin(t, list(writes(op1, T, ctx)))
        sv = V[:, :, n[f"S{i}0"]].astype(np.int32); s2v = V[:, :, n[f"S{i}1"]].astype(np.int32)
        for kk in range(2, D1 + 1):
            # hypothesis kk passes through intermediate cells at oo = -(kk-1) .. -1
            sel = gm & inrng & wr & (oo < 0) & (oo > -kk)
            if not sel.any(): continue
            kb = _kbit(op1.param, a1 + oo - op1.lo)
            cin = V[:, :, n[f"CARRY{kk}"]].astype(np.int32)
            _, cout = _chain(op1.skind, cin, sv, s2v, kb)
            P[:, :, n[f"CARRY{kk}"]][sel] = cout[sel].astype(np.uint8)


def _ibc(P, V, gm, op, ctx, ops1, inrng, r, t, c, a1):
    """after the passes for offset o: BCAST accumulation (first neighbour with SIG=1 wins)."""
    T = ctx.T; n = ctx.n; o = op.param; D1 = ctx.D_up
    for i0, op1 in enumerate(ops1):
        if op1.kind != "BCAST": continue
        dirn = -1 if op1.param == 0 else op1.param
        oo = o - c
        wr = np.isin(t, list(writes(op1, T, ctx)))
        for kk in range(1, D1 + 1):
            sh = kk if dirn < 0 else -kk
            sel = gm & inrng & wr & (oo == sh)
            if not sel.any(): continue
            sig = V[:, :, n[f"SIG{kk}"]]; val = V[:, :, n[f"CARRY{kk}"]]
            found = V[:, :, n["BFOUND"]]
            inr = (a1 + sh >= op1.lo) & (a1 + sh < op1.hi)
            # nearest neighbour wins (engine scans kk = 1..D): passes visit kk decreasing for dirn>0,
            # so a later (nearer) candidate overwrites; for dirn<0 the first found is the nearest.
            take = sel & ((found == 0) | (dirn > 0)) & (sig == 1) & inr
            P[:, :, n["BVAL"]][take] = val[take]
            P[:, :, n["BFOUND"]][take] = 1


def _ieval(P, V, S, gm, op, ctx, ops1, inrng, r, t, c, a1):
    T = ctx.T; n = ctx.n; i0 = op.param; D1 = ctx.D_up
    if i0 >= len(ops1): return
    op1 = ops1[i0]
    i = slot_of(ops1, i0)
    k = op1.kind
    hold = T["HOLD"]
    wr = np.isin(t, list(writes(op1, T, ctx)))
    inr = (a1 >= op1.lo) & (a1 < op1.hi)
    if k == "MOV" and op1.param2:
        ci = ctx.computed_move_addresses.index(op1.lo)
        inr = V[:, :, n[f"CM{ci}"]] == 1
    if k == "IINIT":
        # Slot geometry belongs to the represented middle cell's layout,
        # not the outer colony's encoded track layout.
        q = a1 - (ctx.L_up.b0 + ctx.L_up.track_base)
        inr = inr & (q >= 0) & (q < ctx.L_up.tracks.NT * ctx.R) & (q % ctx.R == op1.param + ctx.h)
    base_sel = gm & inrng & wr & inr
    if k == "BUSLATCH_INT":
        # writers: SIMAGE/SIMADDR field bits (c=0 only): value = BLB if it was latched at this level-1 step
        for fld in ("SIMAGE", "SIMADDR"):
            plo, phi = ctx.L.frange(fld)
            sel = gm & (S["addr"] >= plo) & (S["addr"] < phi) & (S["simaddr"] >= op1.lo) & (S["simaddr"] < op1.hi)
            # The same field-bit timing and address guard used by the latch
            # determine whether this represented register bit is overwritten.
            tau1 = S["simage"] - op1.t0
            dir1 = op1.param2
            Lup = ctx.L_up
            src_fld = "AGE" if fld == "SIMAGE" else "ADDR"
            slo, shi = Lup.frange(src_fld)
            for ii in range(min(phi - plo, shi - slo)):
                pw = plo + ii; X1 = slo + ii
                d = dir1 * (S["simaddr"] - X1)
                j1 = np.mod(d, D1); tt1 = (d - j1) // D1
                okk = (d >= 0) & (tt1 == tau1)
                s2 = sel & (S["addr"] == pw) & okk
                P[:, :, hold][s2] = V[:, :, n["BLB"]][s2]
        return
    if k == "RESET":
        P[:, :, hold][base_sel] = 0
        if op1.param2:
            own_in_range = (S["simaddr"] >= op1.lo) & (S["simaddr"] < op1.hi)
            for fld in ("SIMAGE", "SIMADDR"):
                plo, phi = ctx.L.frange(fld)
                sel = gm & own_in_range & (S["addr"] >= plo) & (S["addr"] < phi)
                P[:, :, hold][sel] = 0
        return
    if k == "CONST":
        P[:, :, hold][base_sel] = op1.param
        return
    if k == "IEVAL":
        from .nested_eval import evaluate
        select, value = evaluate(ctx, op1, a1, S["simage2"], S["simaddr2"], V)
        sel = base_sel & select
        P[:, :, hold][sel] = value[sel]
        return
    S0 = V[:, :, n[f"S{i}0"]].astype(np.int32); S1 = V[:, :, n[f"S{i}1"]].astype(np.int32); S2 = V[:, :, n[f"S{i}2"]].astype(np.int32)
    if k == "IBC":
        for mask, _, direction in _nested_bcast_cases(ctx, op1, a1, S["simage2"], S["simaddr2"]):
            take = base_sel & mask & (S0 == 1) & ((S2 == 0) | (direction > 0))
            value = np.where(t == ctx.inner.n["BFOUND"], 1, S1).astype(np.uint8)
            P[:, :, hold][take] = value[take]
    elif k == "ICHAIN":
        for mask, _, _, op2, kb in _nested_chain_cases(ctx, op1, a1, t, S["simage2"], S["simaddr2"]):
            _, carry = _chain(op2.skind, S2, S0, S1, kb)
            sel = base_sel & mask
            P[:, :, hold][sel] = carry[sel].astype(np.uint8)
    elif k == "ILATCH":
        select, _ = _nested_latch_source(ctx, op1, a1, t, S["simage"], S["simage2"], S["simaddr2"])
        sel = base_sel & select
        P[:, :, hold][sel] = S0[sel].astype(np.uint8)
    elif k == "REGWIN":
        # the simulated cell's [its own simulated age in the level-2 register window]: the level-2
        # program of a depth-2 tower has no register load -> window (0,0) -> 0 (ctx.regwin_upup)
        lo2, hi2 = getattr(ctx, "regwin_upup", (0, 0))
        val = ((S["simage"] * 0 + 0 >= lo2) & (0 < hi2)).astype(np.uint8) if hi2 > lo2 else np.zeros_like(a1, np.uint8)
        P[:, :, hold][base_sel] = val[base_sel]
    elif k in ("MOV", "IINIT"):
        P[:, :, hold][base_sel] = S0[base_sel].astype(np.uint8)
    elif k == "BITOP":
        idx = (S0 << 2) | (S1 << 1) | S2
        val = ((op1.param >> idx) & 1).astype(np.uint8)
        P[:, :, hold][base_sel] = val[base_sel]
    elif k == "SHIFT":
        d = op1.param
        inside = ((a1 - d) >= op1.lo) & ((a1 - d) < op1.hi)
        val = np.where(inside, V[:, :, n[f"SHSRC{i}"]], op1.param2).astype(np.uint8)
        P[:, :, hold][base_sel] = val[base_sel]
    elif k == "RSHIFT":
        P[:, :, hold][base_sel] = V[:, :, n[f"SHSRC{i}"]][base_sel]
    elif k == "SWEEP_INIT":
        sel_sig = base_sel & (t == T["SIG"]); sel_acc = base_sel & (t == op1.dst)
        P[:, :, hold][sel_sig] = 1
        P[:, :, hold][sel_acc] = op1.param
    elif k == "BCAST_INIT":
        P[:, :, hold][base_sel] = S0[base_sel].astype(np.uint8)
    elif k == "SWEEP":
        lo, hi = op1.lo, op1.hi
        tokrange = gm & inrng & wr & (a1 >= lo - 1) & (a1 < hi)
        keep = (a1 == hi - 1) & (S2 == 1)
        acted = np.zeros_like(a1, bool)
        out = np.zeros_like(a1); cout = np.zeros_like(a1); last = np.zeros_like(a1, bool)
        for kk in range(1, D1 + 1):
            sig = V[:, :, n[f"SIG{kk}"]]
            valid = (sig == 1) & (a1 - kk >= lo - 1) & inr & ~acted
            cin = V[:, :, n[f"CARRY{kk}"]].astype(np.int32)
            kb = _kbit(op1.param, a1 - lo)
            o_, co_ = _chain(op1.skind, cin, S0, S1, kb)
            if o_ is not None: out = np.where(valid, o_, out)
            cout = np.where(valid, co_, cout)
            last = np.where(valid, (kk == D1) | (a1 == hi - 1), last)
            acted |= valid
        sel = gm & inrng & wr
        sig_new = np.where(acted, last.astype(np.uint8), np.where(keep, 1, 0).astype(np.uint8))
        s_sig = tokrange & (t == T["SIG"])
        P[:, :, hold][s_sig] = sig_new[s_sig]
        s_acc = sel & acted & (t == T["ACC"])
        P[:, :, hold][s_acc] = cout[s_acc].astype(np.uint8)
        if op1.dst is not None:
            s_dst = sel & acted & (t == op1.dst)
            P[:, :, hold][s_dst] = out[s_dst].astype(np.uint8)
    elif k == "BCAST":
        found = V[:, :, n["BFOUND"]]; val = V[:, :, n["BVAL"]]
        act = base_sel & (S2 == 0) & (found == 1)
        s_dst = act & (t == op1.dst); s_sig = act & (t == T["SIG"])
        P[:, :, hold][s_dst] = val[s_dst]
        P[:, :, hold][s_sig] = 1


def _iwf(P, V, S, gm, ctx):
    """level-1 Workspace.Flag bits (Gray p.41-42) written into Hold at the WF1/WF2 positions."""
    T = ctx.T; n = ctx.n; L = ctx.L
    Qs = L.Qs
    hold = T["HOLD"]
    A = S["simaddr"]; G = np.mod(S["simage"] + 1, L.Us)
    tlo, thi = ctx.trickle_up
    in_win = (G >= tlo) & (G < thi)
    wfb = V[:, :, n["WFB"]]
    f1n = V[:, :, n["F1N"]]
    p1 = L.frange("WF1")[0]; p2 = L.frange("WF2")[0]
    wf1 = ((A >= Qs - 5) & (A <= Qs - 1) & in_win & (wfb == 1)).astype(np.uint8)
    wf2 = ((A >= 0) & (A <= 4) & in_win & (wfb == 1) & (f1n == 0)).astype(np.uint8)
    s1 = gm & (S["addr"] == p1); s2 = gm & (S["addr"] == p2)
    P[:, :, hold][s1] = wf1[s1]; P[:, :, hold][s2] = wf2[s2]


def _buslatch_int(P, V, S, m, op, tau, ctx, D):
    """level-0 register load: cell latches bit i of the Hold AGE/ADDR fields (riding on BUS) into
    simage/simaddr.  Registers are modified in S['_simage_new'] etc. (applied by the engine)."""
    L = ctx.L if ctx is not None else S["_layout"]
    addr = S["addr"]
    bus = V[:, :, op.src]
    dirn = op.param2
    fields = (("AGE", "simage"), ("ADDR", "simaddr")) if op.param == 0 else (("SIMAGE", "simage2"), ("SIMADDR", "simaddr2"))
    for fld, reg in fields:
        lo, hi = L.frange(fld)
        new = S["_" + reg]      # int array being assembled
        for i in range(hi - lo):
            X = lo + i
            tt, j, ok = _latch_time(addr, X, dirn, D)
            hit = m & ok & (tt == tau)
            for jj in range(D):
                hj = hit & (j == jj)
                if hj.any():
                    val = np.roll(bus, dirn * jj, axis=1).astype(np.int32)
                    new[hj] = (new[hj] & ~(1 << i)) | (val[hj] << i)
