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

NMAX = 4          # max concurrent level-1 ops per age handled by the interpreter
NSLOT = 3         # latch slots per resource class (S-slots for value ops, SHSRC for shift ops)


def slot_of(ops1, i):
    """resource-class slot of op i among the ops active at one age: shift-kind ops use SHSRC
    slots, the others S-slots (sweeps/bcasts also use the shared SIGk/CARRYk tracks)."""
    k = ops1[i].kind
    cls = (lambda o: o.kind in ("SHIFT", "RSHIFT"))
    return sum(1 for j in range(i) if cls(ops1[j]) == cls(ops1[i]))


# level-0 op kinds of the interpretation phase
IKINDS = ("IINIT", "ILATCH", "ICHAIN", "IBC", "IEVAL", "IWF", "BUSLATCH_INT", "REGWIN")
INTERPRETABLE = ("CONST", "MOV", "BITOP", "SHIFT", "RSHIFT", "SWEEP_INIT", "SWEEP", "BCAST_INIT", "BCAST", "BUSLATCH_INT", "REGWIN")


class InterpCtx:
    """Everything the engine needs to interpret level-1 ops."""

    def __init__(self, L: Layout, T: Tracks, prog_up: Program, L_up: Layout, trickle_up, names, regwin_up=(0, 0)):
        self.L, self.T, self.prog_up, self.L_up, self.trickle_up = L, T, prog_up, L_up, trickle_up
        self.regwin_up = regwin_up
        self.R, self.h, self.NT = T.R, (T.R - 1) // 2, T.NT
        self.base = L.b0 + L.track_base
        self.trng = (self.base, self.base + T.NT * T.R)
        self.n = names          # dict of temp track names -> track index
        self.D_up = prog_up.D
        self.JI = 4

    def pos(self, t, r):
        return self.base + t * self.R + r


def writes(op, T):
    k = op.kind
    if k in ("CONST", "MOV", "BITOP", "SHIFT", "RSHIFT", "BCAST_INIT", "REGWIN"):
        return {op.dst}
    if k == "SWEEP_INIT":
        return {T["SIG"], op.dst}
    if k == "SWEEP":
        s = {T["SIG"], T["ACC"]}
        if op.dst is not None: s.add(op.dst)
        return s
    if k == "BCAST":
        return {op.dst, T["SIG"]}
    return set()


# ---------------------------------------------------------------- compile
def compile_iphase(C: Compiler, ctx: InterpCtx, al, F1N):
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
    n_pass = (T.NT * R - 1 + C.D - 1) // C.D + 1
    # clear latch state
    for nm in ["SIG1", "SIG2", "SIG3", "CARRY1", "CARRY2", "CARRY3", "BFOUND", "BVAL", "SHSRC0", "SHSRC1", "SHSRC2",
               "S00", "S01", "S02", "S10", "S11", "S12", "S20", "S21", "S22", "BLB", "WFB", "BUS"]:
        C.const(names[nm], 0, rng=(0, Q), advance=False)
    C.t += 1
    for o in range(-ctx.JI, ctx.JI + 1):
        # repaired level-1 tracks of the cell at offset o (valid at slot-h positions)
        C.emit("SHIFT", dst=T[names["SA"]], src=T.arg(o + 1), param=+1, param2=0, rng=trng)
        C.emit("SHIFT", dst=T[names["SB"]], src=T.arg(o - 1), param=-1, param2=0, rng=trng)
        C.t += 1
        C.bitop(names["VT"], lambda a, b, c: (a & b) | (a & c) | (b & c), names["SA"], T.names[T.arg(o)], names["SB"], rng=trng)
        if -h <= o <= h:
            C.emit("IINIT", dst=T["HOLD"], src=T[names["VT"]], param=o, rng=trng); C.t += 1
        for dirn in (+1, -1):
            C.mov(names["BUS"], names["VT"], rng=(0, Q))
            C.emit("RSHIFT", dur=n_pass, dst=T[names["BUS"]], src=T[names["BUS"]], param=dirn * C.D, rng=(0, Q))
            C.emit("ILATCH", dur=n_pass, param=o, param2=dirn, rng=(0, Q))
            C.t += n_pass
        C.emit("ICHAIN", param=o, rng=trng); C.t += 1
        C.emit("IBC", param=o, rng=trng); C.t += 1
    C.const(names["BUS"], 0, rng=(0, Q))
    nmax = max(len(ctx.prog_up.ops_at(a)) for a in range(ctx.prog_up.U))
    assert nmax <= NMAX, f"level-1 program has {nmax} concurrent ops (max {NMAX})"
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
    C.bitop("HOLD", lambda f, a, x: 0 if (f & a) else x, F1T, ADDRCH, "HOLD", rng=trng)
    al.put(ADDRCH, F1T)
    # level-1 workspace flags (writer cells at the WF1/WF2 positions use WFB latched INFO bits)
    C.emit("IWF", rng=(L.frange("WF1")[0], L.frange("WF2")[0] + 1)); C.t += 1
    al.put(names["WFB"])
    # load the level-0 registers from the new simulated AGE / ADDR fields (Hold) via two bus passes
    C.const(names["BUS"], 0, rng=(0, Q))
    C.mov(names["BUS"], "HOLD", rng=L.frange("AGE"), advance=False)
    C.mov(names["BUS"], "HOLD", rng=L.frange("ADDR"))
    np2 = (Q - 1 + C.D - 1) // C.D + 1
    C.reg_window = (C.t, C.t + 2 * np2 + 3)
    for dirn in (+1, -1):
        if dirn < 0:
            C.const(names["BUS"], 0, rng=(0, Q))
            C.mov(names["BUS"], "HOLD", rng=L.frange("AGE"), advance=False)
            C.mov(names["BUS"], "HOLD", rng=L.frange("ADDR"))
        C.emit("RSHIFT", dur=np2, dst=T[names["BUS"]], src=T[names["BUS"]], param=dirn * C.D, rng=(0, Q))
        C.emit("BUSLATCH_INT", dur=np2, src=T[names["BUS"]], param2=dirn, rng=(0, Q))
        C.t += np2
    C.const(names["BUS"], 0, rng=(0, Q))
    al.put(names["BUS"])
    return names


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
    inrng, r, t, c = _cell_geometry(ctx, addr)
    a1 = np.mod(simaddr + c, ctx.L.Qs)              # simulated address of the cell at offset c
    if k == "IINIT":
        o = op.param
        sel = m & inrng & (c == o)
        val = np.roll(V[:, :, op.src], o, axis=1)      # VT[p - o]  (roll by +o gives V[x-o])
        P[:, :, op.dst][sel] = val[sel]
        return
    if k == "BUSLATCH_INT":
        _buslatch_int(P, V, S, m, op, tau, ctx, D)
        return
    # level-1 active ops per distinct simage value
    for g1 in np.unique(simage[m]) if m.any() else []:
        gm = m & (simage == g1)
        ops1 = ctx.prog_up.ops_at(int(g1))
        assert len(ops1) <= NMAX
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
    oo = o - c                                          # relative offset of o from the cell's simulated cell
    w = writes(op1, T)
    wr = np.isin(t, list(w)) if w else np.zeros_like(t, bool)
    assert i < NSLOT, "too many concurrent ops of one class"
    Si = [n[f"S{i}0"], n[f"S{i}1"], n[f"S{i}2"]]
    k = op1.kind
    ph = lambda tr: ctx.pos(tr, ctx.h)
    if k in ("CONST",):
        return needs
    if k in ("MOV", "BITOP", "BCAST_INIT"):
        srcs = [op1.src, op1.src2, op1.src3]
        for jx, s in enumerate(srcs):
            if s is not None:
                needs.append((wr & (oo == 0), ph(s), Si[jx]))
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
            sel = gm & (addr == pw)
            if not sel.any(): continue
            # level-1 timing: cell a1 reads BUS_1[a1 - dir1*j1] at tau1 == (d - j1)/D1, d = dir1*(a1 - X1)
            d = dir1 * (simaddr - X1)
            j1 = np.mod(d, D1); tt1 = (d - j1) // D1
            okk = (d >= 0) & (tt1 == tau1)
            rel = -dir1 * j1                       # relative offset of the level-1 cell whose BUS is read
            sel2 = sel & okk & (rel == o)
            if not sel2.any(): continue
            if getattr(ctx, "bus_up", None) is None:
                continue                      # the simulated level has no register load (depth-2 tower)
            X = ctx.pos(ctx.bus_up, ctx.h)
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
        wr = np.isin(t, list(writes(op1, T)))
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
        wr = np.isin(t, list(writes(op1, T)))
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
    wr = np.isin(t, list(writes(op1, T)))
    S0 = V[:, :, n[f"S{i}0"]].astype(np.int32); S1 = V[:, :, n[f"S{i}1"]].astype(np.int32); S2 = V[:, :, n[f"S{i}2"]].astype(np.int32)
    inr = (a1 >= op1.lo) & (a1 < op1.hi)
    base_sel = gm & inrng & wr & inr
    if k == "BUSLATCH_INT":
        # writers: SIMAGE/SIMADDR field bits (c=0 only): value = BLB if it was latched at this level-1 step
        for fld in ("SIMAGE", "SIMADDR"):
            plo, phi = ctx.L.frange(fld)
            sel = gm & (S["addr"] >= plo) & (S["addr"] < phi)
            # a bit is written only if the level-1 timing matched (BLB latched this period); we
            # detect that via WFB? -> keep simple: write BLB when the level-1 cell is in its pass
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
    if k == "CONST":
        P[:, :, hold][base_sel] = op1.param
    elif k == "REGWIN":
        # the simulated cell's [its own simulated age in the level-2 register window]: the level-2
        # program of a depth-2 tower has no register load -> window (0,0) -> 0 (ctx.regwin_upup)
        lo2, hi2 = getattr(ctx, "regwin_upup", (0, 0))
        val = ((S["simage"] * 0 + 0 >= lo2) & (0 < hi2)).astype(np.uint8) if hi2 > lo2 else np.zeros_like(a1, np.uint8)
        P[:, :, hold][base_sel] = val[base_sel]
    elif k == "MOV":
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
    L = ctx.L
    addr = S["addr"]
    bus = V[:, :, op.src]
    dirn = op.param2
    for fld, reg in (("AGE", "simage"), ("ADDR", "simaddr")):
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
