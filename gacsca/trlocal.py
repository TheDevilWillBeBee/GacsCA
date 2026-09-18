"""Microprogram computing Gray's local-structure transition for a *simulated* cell whose
neighbourhood states are laid out bit-serially on the ARGA_j tracks (j = c-5..c+5).

Result: new ADDR/AGE/F1/F2 of the simulated cell at offset c, written to `out` (default HOLD)
at the corresponding addresses of the Info layout.  Uses temporaries T0..T5, BC, BF*.
"""
from .microcode import Compiler, Layout, Tracks
from .params import Variant


class Alloc:
    def __init__(self, names):
        self.free = list(names)
        self.peak = 0; self.n = 0

    def get(self):
        if not self.free:
            raise RuntimeError("out of temp tracks")
        self.n += 1; self.peak = max(self.peak, self.n)
        return self.free.pop()

    def put(self, *names):
        for n in names:
            self.free.append(n); self.n -= 1


def temps_of(T):
    return ["T0", "T1", "T2", "T3", "T4", "T5", "BC"] + [n for n in T.names if n.startswith("BF")]


class TrLocal:
    def __init__(self, C: Compiler, c: int = 0, variant: Variant = Variant(), out="HOLD", stage2=False):
        self.C, self.c, self.v, self.out = C, c, variant, out
        self.L, self.T = C.L, C.T
        self.Q, self.U = C.L.Qs, C.L.Us          # parameters of the simulated level
        self.FA = self.L.frange("ADDR"); self.FG = self.L.frange("AGE")
        self.aF1 = self.L.frange("F1")[0]; self.aF2 = self.L.frange("F2")[0]
        self.FR = (self.L.b0, self.L.b0 + self.L.track_base)     # local part of the layout
        self.al = Alloc(temps_of(self.T))
        self.stage2 = stage2

    # ---- helpers ----
    def A(self, i):
        return f"ARGA{self.c + i:+d}"

    def dec(self, dst, rng):
        """broadcast the ACC of the token at hi-1 over the whole local range FR"""
        lo, hi = rng
        self.C.bcast(dst, (self.FR[0], hi), right=(hi - 1, self.FR[1]))

    def eqf_dec(self, s1, s2, rng, dst):
        self.C.sweep("EQF", rng, src=s1, src2=s2, acc_init=1); self.dec(dst, rng)

    def eqc_dec(self, s, rng, c, dst):
        self.C.sweep("EQC", rng, src=s, const=c, acc_init=1); self.dec(dst, rng)

    def ltc_dec(self, s, rng, c, dst):
        self.C.sweep("LTC", rng, src=s, const=c, acc_init=0); self.dec(dst, rng)

    def count_init(self):
        c1, c0 = self.al.get(), self.al.get()
        self.C.const(c1, 0, rng=self.FR, advance=False); self.C.const(c0, 0, rng=self.FR)
        return c1, c0

    def count_add(self, cnt, b, rng=None):
        """saturating counter (>=3 detection): states 0,1,2,3+ ; b: track (bit to add)"""
        c1, c0 = cnt
        rng = rng or self.FR
        self.C.bitop(c1, lambda x1, x0, bb: x1 | (x0 & bb), c1, c0, b, rng=rng, advance=False)
        self.C.bitop(c0, lambda x0, x1, bb: ((x0 ^ 1) | x1) if bb else x0, c0, c1, b, rng=rng)

    def count_ge2(self, cnt):  return cnt[0]                       # track name whose bit = [count>=2]

    def count_ge3(self, cnt, dst, rng=None):
        self.C.bitop(dst, lambda a, b, _: a & b, cnt[0], cnt[1], rng=rng or self.FR)

    def maj5(self, vals, rng, cur, out, ex, masks=None):
        """majority (>=3 equal) of five bit-serial values on tracks `vals` over rng -> `out`
        (= cur if none); ex (over FR) <- exists.  masks: optional per-value validity tracks (over FR):
        a value only counts if its mask bit is 1 (pairwise equality is ANDed with both masks)."""
        C = self.C
        E = {}
        for a in range(5):
            for b in range(a + 1, 5):
                t = self.al.get(); E[(a, b)] = t
                self.eqf_dec(vals[a], vals[b], rng, t)
                if masks is not None:
                    C.bitop(t, lambda e, ma, mb: e & ma & mb, t, masks[a], masks[b], rng=self.FR)
        C.const(ex, 0, rng=self.FR, advance=False); C.const(out, 0, rng=rng)
        W = self.al.get()
        for a in range(5):
            cnt = self.count_init()
            for b in range(5):
                if b != a:
                    self.count_add(cnt, E[(min(a, b), max(a, b))])
            C.mov(W, self.count_ge2(cnt), rng=self.FR)
            self.al.put(*cnt)
            C.bitop(ex, lambda e, w, _: e | w, ex, W, rng=self.FR, advance=False)
            C.bitop(out, lambda o, w, v: o | (w & v), out, W, vals[a], rng=rng)
        C.bitop(out, lambda e, o, cu: o if e else cu, ex, out, cur, rng=rng)
        self.al.put(W, *E.values())

    # ---- the transition ----
    def build(self):
        C, al, Q, U = self.C, self.al, self.Q, self.U
        FA, FG, FR, aF1, aF2 = self.FA, self.FG, self.FR, self.aF1, self.aF2
        wq, wu = self.L.wq, self.L.wu
        A = self.A
        # --- apparent colony: v_i = ADDR_i - i ---
        va = [al.get() for _ in range(5)]
        for i in range(1, 6):
            C.add_const(va[i - 1], A(i), FA, (Q - i) % (1 << wq))
        VR, EX = al.get(), al.get()
        self.maj5(va, FA, A(0), VR, EX)
        al.put(*va)
        inR, inL = [None] * 6, [None] * 6
        for i in range(1, 6):
            t = al.get(); self.ltc_dec(VR, FA, Q - i, t)              # [v < Q-i]
            C.bitop(t, lambda e, l, _: e & l, EX, t, rng=FR); inR[i] = t
            t = al.get(); self.ltc_dec(VR, FA, i, t)                  # [v < i]
            C.bitop(t, lambda e, l, _: e & (1 - l), EX, t, rng=FR); inL[i] = t
        # --- (ii): >=3 sites in L&C with wrong address ---
        cnt = self.count_init()
        vm, eq = al.get(), al.get()
        for i in range(1, 6):
            C.add_const(vm, VR, FA, (Q - i) % (1 << wq))               # v - i
            self.eqf_dec(vm, A(-i), FA, eq)
            C.bitop(eq, lambda l, e, _: l & (1 - e), inL[i], eq, rng=FR)
            self.count_add(cnt, eq)
        BAD = al.get(); self.count_ge3(cnt, BAD); al.put(*cnt, vm, eq)
        # --- (iii)/(iv): ages in R ---
        AR, EXG = al.get(), al.get()
        self.maj5([A(i) for i in range(1, 6)], FG, A(0), AR, EXG)
        eq = al.get()
        cnt = self.count_init()
        for i in range(1, 6):
            self.eqf_dec(A(-i), AR, FG, eq)
            C.bitop(eq, lambda l, e, _: l & (1 - e), inL[i], eq, rng=FR)
            self.count_add(cnt, eq)
        DIFF = al.get(); self.count_ge3(cnt, DIFF); al.put(*cnt)
        INC = al.get()
        C.bitop(INC, lambda e, b, _: (1 - e) | b, EX, BAD, rng=FR)
        C.bitop(INC, lambda i, g, d: i | (1 - g) | (g & d), INC, EXG, DIFF, rng=FR)
        al.put(BAD, DIFF, eq)
        # --- Flag1 (at address aF1) ---
        one = (aF1, aF1 + 1)
        cnt = self.count_init(); t = al.get()
        for i in range(1, 6):
            if self.v.flag1_ii_in_colony:
                C.bitop(t, lambda r, f, _: r & f, inR[i], A(i), rng=one)
            else:
                C.mov(t, A(i), rng=one)
            self.count_add(cnt, t, rng=one)
        CII = al.get(); self.count_ge3(cnt, CII, rng=one)
        cnta = self.count_init()
        for i in range(1, 6):
            C.bitop(t, lambda r, f, _: r & f, inR[i], A(i), rng=one)
            self.count_add(cnta, t, rng=one)
        # (iii): >= 3 sites in N(x)&C(x) with Workspace.Flag1 = 1 ; (iv) same with Workspace.Flag2.
        # The WF bits of the neighbours sit at the WF1/WF2 addresses of the ARG tracks.
        CIII, DIV = al.get(), al.get()
        for fld, dst in (("WF1", CIII), ("WF2", DIV)):
            aw = self.L.frange(fld)[0]; wr_ = (aw, aw + 1)
            cw = self.count_init()
            for i in range(1, 6):
                C.bitop(t, lambda r, f, _: r & f, inR[i], A(i), rng=wr_); self.count_add(cw, t, rng=wr_)
                C.bitop(t, lambda l, f, _: l & f, inL[i], A(-i), rng=wr_); self.count_add(cw, t, rng=wr_)
            C.bitop(t, lambda e, f, _: e & f, EX, A(0), rng=wr_); self.count_add(cw, t, rng=wr_)
            self.count_ge3(cw, dst, rng=wr_); al.put(*cw)
            C.spread(aw, dst, FR, dst)
        F1N = al.get()
        # f1==0: INC | CII | CIII ; f1==1: !( !INC & !CIII & cnt<=1 )
        C.bitop(t, lambda i, c2, c3: i | c2 | c3, INC, CII, CIII, rng=one)          # on-value
        C.bitop(F1N, lambda i, c3, ge2: 1 - ((1 - i) & (1 - c3) & (1 - ge2)), INC, CIII, self.count_ge2(cnta), rng=one)
        C.bitop(F1N, lambda f, on, off: off if f else on, A(0), t, F1N, rng=one)
        al.put(*cnt, *cnta, CII, CIII, *inR[1:])
        C.spread(aF1, F1N, FR, F1N)
        # --- age from L, Flag2 cond (iii) ---
        AL = al.get()
        self.maj5([A(-i) for i in range(1, 6)], FG, A(0), AL, t)
        AL1 = al.get(); C.add_const(AL1, AL, FG, 1)
        DIII = al.get()
        self.eqc_dec(AL1, (FG[0], FG[0] + 4), 0, DIII)
        if self.v.flag2_iii_age == "current":
            self.eqc_dec(A(0), (FG[0], FG[0] + 4), 0, DIII)
        C.bitop(DIII, lambda e, z, _: (1 - e) & z, EX, DIII, rng=FR)
        # --- Flag2 (at aF2) ---
        two = (aF2, aF2 + 1)
        cz = self.count_init()       # zeros among (inL_i & F2_-i)  -> d_i = zeros<=1
        ca = self.count_init()       # zeros among F2_-i            -> d_ii needs zeros<=1
        anyL0 = al.get(); C.const(anyL0, 0, rng=two)   # OR_i (inL_i & !F2_-i)
        anyF2 = al.get(); C.const(anyF2, 0, rng=two)   # OR_i F2_-i
        for i in range(1, 6):
            C.bitop(t, lambda l, f, _: 1 - (l & f), inL[i], A(-i), rng=two); self.count_add(cz, t, rng=two)
            C.bitop(t, lambda f, _a, _b: 1 - f, A(-i), rng=two); self.count_add(ca, t, rng=two)
            C.bitop(anyL0, lambda o, l, f: o | (l & (1 - f)), anyL0, inL[i], A(-i), rng=two, advance=False)
            C.bitop(anyF2, lambda o, f, _: o | f, anyF2, A(-i), rng=two)
        DI, DII = al.get(), al.get()
        C.bitop(DI, lambda ge2, _a, _b: 1 - ge2, self.count_ge2(cz), rng=two, advance=False)
        C.bitop(DII, lambda f1, ge2, _: f1 & (1 - ge2), F1N, self.count_ge2(ca), rng=two)
        F2N = al.get()
        on = t
        C.bitop(on, lambda a, b, cc: a | b | cc, DI, DII, DIII, rng=two)
        C.bitop(on, lambda o, d4, _: o | d4, on, DIV, rng=two)
        a2 = al.get(); b2 = al.get()
        C.bitop(a2, lambda f1, l0, _: (1 - f1) & (1 - l0), F1N, anyL0, rng=two, advance=False)
        C.bitop(b2, lambda f1, af, _: f1 & (1 - af), F1N, anyF2, rng=two)
        # off: !DIII & !DIV & (a2|b2)  -> F2N = 0 ; else 1
        C.bitop(a2, lambda x, y, _: x | y, a2, b2, rng=two)
        C.bitop(F2N, lambda d3, d4, ab: 1 - ((1 - d3) & (1 - d4) & ab), DIII, DIV, a2, rng=two)
        C.bitop(F2N, lambda f, onv, off: off if f else onv, A(0), on, F2N, rng=two)
        al.put(*cz, *ca, anyL0, anyF2, DI, DII, DIV, a2, b2, DIII, AL1, *inL[1:], INC, EXG)
        C.spread(aF2, F2N, FR, F2N)
        # --- votes ---
        VRT = al.get()
        C.bitop(VRT, lambda e, f1, f2: e & ((1 - f1) | f2), EX, F1N, F2N, rng=FR)
        vl = [al.get() for _ in range(5)]
        for i in range(1, 6):
            C.add_const(vl[i - 1], A(-i), FA, i)
        ML, EXL = al.get(), al.get()
        self.maj5(vl, FA, A(0), ML, EXL)
        al.put(*vl, EXL)
        out = self.out
        C.bitop(out, lambda r, vr, ml: vr if r else ml, VRT, VR, ML, rng=FA)
        C.bitop(t, lambda r, ar, alv: ar if r else alv, VRT, AR, AL, rng=FG)
        C.add_const(out, t, FG, 1)
        C.mov(out, F1N, rng=one, advance=False)
        C.mov(out, F2N, rng=two)
        al.put(ML, AR, AL, t)                              # VR, EX still needed for the register masks
        # --- SIMAGE / SIMADDR registers of the simulated cell: majority repair (no increment) ---
        INW = al.get()
        C.emit("REGWIN", dst=self.T[INW], rng=(0, self.L.Q)); C.t += 1
        for fname in ("SIMAGE", "SIMADDR"):
            FS = self.L.frange(fname)
            # colony-local majority (voters restricted to R&C / L&C; needs >= 3), fallback, else keep
            masks = []
            for i in range(1, 6):
                m_ = al.get(); self.ltc_dec(VR, FA, Q - i, m_); C.bitop(m_, lambda e, l, _: e & l, EX, m_, rng=FR); masks.append(m_)
            MR, EXR = al.get(), al.get()
            self.maj5([A(i) for i in range(1, 6)], FS, A(0), MR, EXR, masks=masks)
            al.put(*masks)
            masks = []
            for i in range(1, 6):
                m_ = al.get(); self.ltc_dec(VR, FA, i, m_); C.bitop(m_, lambda e, l, _: e & (1 - l), EX, m_, rng=FR); masks.append(m_)
            ML2, EXL = al.get(), al.get()
            self.maj5([A(-i) for i in range(1, 6)], FS, A(0), ML2, EXL, masks=masks)
            al.put(*masks)
            tt = al.get()
            # first choice by direction, fallback to the other side, else own
            C.bitop(tt, lambda r, a, b: a if r else b, VRT, MR, ML2, rng=FS)          # first value
            fok = al.get(); sok = al.get()
            C.bitop(fok, lambda r, a, b: a if r else b, VRT, EXR, EXL, rng=FR, advance=False)
            C.bitop(sok, lambda r, a, b: b if r else a, VRT, EXR, EXL, rng=FR)
            sv = al.get(); C.bitop(sv, lambda r, a, b: b if r else a, VRT, MR, ML2, rng=FS)  # second value
            C.bitop(tt, lambda ok, first, second: first if ok else second, fok, tt, sv, rng=FS)
            C.bitop(tt, lambda ok1, ok2, v: v if (ok1 | ok2) else 0, fok, sok, tt, rng=FS, advance=False)
            C.bitop(sv, lambda ok1, ok2, own: 0 if (ok1 | ok2) else own, fok, sok, A(0), rng=FS)
            C.bitop(tt, lambda a, b, _: a | b, tt, sv, rng=FS)
            C.bitop(out, lambda w, own, mj: own if w else mj, INW, A(0), tt, rng=FS)
            al.put(MR, ML2, EXR, EXL, tt, fok, sok, sv)
        al.put(INW, VR, EX)
        self.F1N, self.F2N, self.VRT = F1N, F2N, VRT
        al.put(F2N, VRT)                                  # F1N is kept for the interpretation phase
        return C.t
