"""NumPy engine for the simulation structure: R-fold redundant tracks + Age-scheduled microprogram.

State S: 'addr','age','f1','f2' (B,L) int arrays (local structure, see level0_np) and
'trk' (B,L,NT,R) uint8: cell x holds copies of track bits of x+OFFS[r].
"""
import numpy as np
from .params import Params, Variant
from . import level0_np as l0
from .microcode import Tracks, Layout, Program, Op
from . import interp as _interp


def offs(R):
    h = (R - 1) // 2
    return list(range(-h, h + 1))


def roll(a, k, axis=1):
    """b[..., x] = a[..., x + k] along axis (periodic)."""
    return np.roll(a, -k, axis=axis)


def repair(trk):
    """Majority over the R holders of each track bit -> V (B,L,NT)."""
    B, L, NT, R = trk.shape
    votes = np.zeros((B, L, NT), np.int16)
    for r, o in enumerate(offs(R)):
        # holder x = y - o keeps copy r of bit y
        votes += roll(trk[:, :, :, r], -o)
    return (votes * 2 > R).astype(np.uint8)


def redistribute(P, R):
    """New primaries P (B,L,NT) -> copies trk' (B,L,NT,R): trk'[x, r] = P[x + off_r]."""
    return np.stack([roll(P, o) for o in offs(R)], axis=-1)


def _in_range(addr, lo, hi):
    return (addr >= lo) & (addr < hi)


def apply_ops(V, addr, age, prog: Program, T: Tracks, mask_age=None, S=None, ctx=None):
    """Apply the ops scheduled at each cell's age.  V: repaired (B,L,NT) uint8.  Returns P.
    S/ctx: full state and interpretation context (needed for the interpretation op kinds)."""
    P = V.copy()
    B, L, NT = V.shape
    ages = np.unique(age)
    D = prog.D
    for a in ages:
        ops = prog.ops_at(a)
        if not ops:
            continue
        am = (age == a)
        for op in ops:
            m = am & _in_range(addr, op.lo, op.hi)
            k = op.kind
            if k in _interp.IKINDS:
                _interp.apply_iop(P, V, S, m, am, op, int(a) - op.t0, ctx, T, D)
            elif k == "CONST":
                P[:, :, op.dst][m] = op.param
            elif k == "RESET":
                P[:, :, op.dst:op.param][m] = 0
                if op.param2 and S is not None:
                    for name in ("simage", "simaddr", "simage2", "simaddr2"):
                        if "_" + name in S:
                            S["_" + name][m] = 0
            elif k == "MOV":
                if op.param2:
                    m = am & _in_range(S["_computed_addr"], op.lo, op.hi)
                P[:, :, op.dst][m] = V[:, :, op.src][m]
            elif k == "BITOP":
                b1 = V[:, :, op.src].astype(np.int32)
                b2 = V[:, :, op.src2].astype(np.int32) if op.src2 is not None else 0
                b3 = V[:, :, op.src3].astype(np.int32) if op.src3 is not None else 0
                idx = (b1 << 2) | (b2 << 1) | b3
                val = ((op.param >> idx) & 1).astype(np.uint8)
                P[:, :, op.dst][m] = val[m]
            elif k == "SHIFT":
                d = op.param
                src_val = roll(V[:, :, op.src], -d)              # value at x-d
                inside = _in_range(addr - d, op.lo, op.hi)       # own-address based (robust to a corrupted neighbour)
                val = np.where(inside, src_val, op.param2).astype(np.uint8)
                P[:, :, op.dst][m] = val[m]
            elif k == "RSHIFT":
                P[:, :, op.dst][m] = roll(V[:, :, op.src], -op.param)[m]
            elif k == "SWEEP_INIT":
                P[:, :, T["SIG"]][m] = 1
                P[:, :, op.dst][m] = op.param
            elif k == "SWEEP":
                _sweep(P, V, addr, m, am, op, T, D)
            elif k == "BCAST_INIT":
                P[:, :, op.dst][m] = V[:, :, op.src][m]
            elif k == "BCAST":
                sig = V[:, :, T["SIG"]]
                val = V[:, :, op.dst]
                got = np.zeros_like(sig, dtype=bool); newv = val.copy()
                dirn = -1 if op.param == 0 else op.param   # -1: wave moves left (reads right)
                for kk in range(1, D + 1):
                    sh = kk if dirn < 0 else -kk
                    s_k = roll(sig, sh); v_k = roll(val, sh); a_k = addr + sh
                    cand = (s_k == 1) & (a_k < op.hi) & (a_k >= op.lo) & ~got
                    newv = np.where(cand, v_k, newv); got |= cand
                upd = m & (sig == 0) & got
                P[:, :, op.dst][upd] = newv[upd]
                P[:, :, T["SIG"]][upd] = 1
            else:
                raise ValueError(k)
    return P


def _sweep(P, V, addr, m, am, op, T, D):
    """Token sweep step (see microcode.py).  Ranges: data ops on [lo,hi); token on [lo-1,hi)."""
    lo, hi = op.lo, op.hi
    sig = V[:, :, T["SIG"]]; acc = V[:, :, T["ACC"]]
    s = V[:, :, op.src].astype(np.int32) if op.src is not None else np.zeros_like(sig, np.int32)
    s2 = V[:, :, op.src2].astype(np.int32) if op.src2 is not None else np.zeros_like(sig, np.int32)
    const = op.param
    kbit_at = lambda a: ((const >> np.clip(a - lo, 0, 62)) & 1).astype(np.int32)
    kind = op.skind

    def chain(cin, sv, s2v, kb):
        """one cell's contribution -> (out, cout)"""
        if kind == "EQC":  return None, cin & (sv == kb)
        if kind == "EQF":  return None, cin & (sv == s2v)
        if kind == "ORF":  return None, cin | sv
        if kind == "ANDF": return None, cin & sv
        if kind == "LTC":  return None, ((1 - sv) & kb) | ((sv == kb) & cin)
        if kind == "ADDC":
            out = sv ^ kb ^ cin
            cout = (sv & kb) | (sv & cin) | (kb & cin)
            return out, cout
        raise ValueError(kind)

    acted = np.zeros_like(sig, dtype=bool)
    new_out = np.zeros_like(sig, dtype=np.int32); new_acc = np.zeros_like(sig, dtype=np.int32)
    new_sig = np.zeros_like(sig, dtype=np.int32)
    for k in range(1, D + 1):
        hold = roll(sig, -k) == 1                       # token at y-k
        valid = hold & (addr - k >= lo - 1)
        cin = roll(acc, -k).astype(np.int32)
        for mm in range(1, k):                          # cells strictly between holder and y
            j = k - mm                                  # offset of that cell to the left of y
            sv = roll(s, -j); s2v = roll(s2, -j); kb = kbit_at(addr - j)
            _, cin = chain(cin, sv, s2v, kb)
        out, cout = chain(cin, s, s2, kbit_at(addr))
        sel = valid & ~acted & (addr >= lo) & (addr < hi)
        acted |= sel
        if out is not None:
            new_out = np.where(sel, out, new_out)
        new_acc = np.where(sel, cout, new_acc)
        last = (k == D) | (addr == hi - 1)
        new_sig = np.where(sel & last, 1, new_sig)
    # token bookkeeping on [lo-1, hi): finished token at hi-1 stays
    keep = (addr == hi - 1) & (sig == 1)
    tm = _in_range(addr, lo - 1, hi) & am
    P[:, :, T["SIG"]][tm] = np.where(keep | (new_sig == 1), 1, 0)[tm]
    upd = m & acted
    P[:, :, T["ACC"]][upd] = new_acc[upd].astype(np.uint8)
    if op.dst is not None:
        P[:, :, op.dst][upd] = new_out[upd].astype(np.uint8)


class Engine:
    """Full rule: local structure (Gray 5.2) + simulation structure (tracks + microprogram)."""

    def __init__(self, p: Params, tracks: Tracks, layout: Layout, prog: Program, variant=Variant(),
                 wipe_rules=True):
        self.p, self.T, self.L, self.prog, self.v = p, tracks, layout, prog, variant
        self.register_bits = max(16, (layout.Us - 1).bit_length(), (layout.Qs - 1).bit_length())
        self.nested_register_bits = getattr(prog, "nested_register_bits", 0)
        if not isinstance(self.nested_register_bits, int) or (self.nested_register_bits and not 16 <= self.nested_register_bits <= 31):
            raise ValueError("nested register width must be 0 or 16..31")
        self.register_names = ("simage", "simaddr") + (("simage2", "simaddr2") if self.nested_register_bits else ())
        for op in prog.ops:
            if op.kind == "BUSLATCH_INT" and (op.param not in (0, 1) or (op.param == 1 and
                    self.nested_register_bits < max(layout.fields["SIMAGE"][1], layout.fields["SIMADDR"][1]))):
                raise ValueError("register-load pair is absent or too narrow")
        self.wipe_rules = wipe_rules

    def initial(self, B, info_bits=None):
        p = self.p
        S = l0.initial(p, B)          # includes wf1, wf2 arrays
        if self.nested_register_bits:
            for name in ("simage2", "simaddr2"):
                S[name] = np.zeros((B, p.L), np.int32)
        trk = np.zeros((B, p.L, self.T.NT, self.T.R), np.uint8)
        if info_bits is not None:                        # (B, L) primary Info bits
            trk[:, :, self.T["INFO"], :] = redistribute(info_bits.astype(np.uint8), self.T.R)[..., :]
        S["trk"] = trk
        return S

    def step(self, S):
        if not self.nested_register_bits and ("simage2" in S or "simaddr2" in S):
            raise ValueError("extended controls cannot be dropped into a legacy schema")
        p, T = self.p, self.T
        V = repair(S["trk"])
        Sl = dict(addr=S["addr"], age=S["age"], f1=S["f1"], f2=S["f2"], wf1=S["wf1"], wf2=S["wf2"],
                  simage=S["simage"], simaddr=S["simaddr"])
        Sl.update({k:S[k] for k in self.register_names})
        N = l0.step(Sl, p, self.v, reg_window=getattr(self, "reg_window", (0, 0)))
        N.pop("_info")
        # Each holder executes its own redundant computation (Gray pp.33-34).
        # For target y=x+o, holder x supplies Age(x) and inferred address
        # (Address(x)+o) mod Q. Sharing the target's raw controls makes a
        # single clock/address fault corrupt all R replicas simultaneously.
        primary_state = dict(S)
        primary_state["_layout"] = self.L
        primary_state["_computed_addr"] = N["addr"]
        for k in self.register_names:
            primary_state["_" + k] = N[k].copy()
        primary = apply_ops(V, S["addr"], S["age"], self.prog, T,
                            S=primary_state, ctx=getattr(self, "ictx", None))
        copies = []
        for o in offs(T.R):
            if o == 0:
                copies.append(primary)
                continue
            Sx = dict(S)
            Sx["_layout"] = self.L
            Sx["addr"] = (roll(S["addr"], -o) + o) % p.Q
            Sx["age"] = roll(S["age"], -o)
            Sx["_computed_addr"] = (roll(N["addr"], -o) + o) % p.Q
            for k in self.register_names:
                Sx[k] = roll(S[k], -o)
                Sx["_" + k] = N[k].copy()
            # Reuse identical computations in a healthy configuration. This
            # is an exact shortcut, guarded by equality of every control.
            if (all(np.array_equal(Sx[k], S[k]) for k in ("addr", "age") + self.register_names)
                    and np.array_equal(Sx["_computed_addr"], N["addr"])):
                P = primary
            else:
                P = apply_ops(V, Sx["addr"], Sx["age"], self.prog, T,
                              S=Sx, ctx=getattr(self, "ictx", None))
            copies.append(roll(P, o))
        # Integer register loads belong to the holder itself.
        for k in self.register_names:
            N[k] = primary_state["_" + k]
        trk = np.stack(copies, axis=-1)
        F1 = N["f1"] == 1
        if self.wipe_rules:
            # Gray p.33 (holder form): a cell with computed Flag1 = 1 clears every Mailbox bit it
            # holds; if additionally its computed Address differs from its current Address it clears
            # every simulation-structure bit it holds.
            trk[:, :, T["MAILL"], :][F1] = 0; trk[:, :, T["MAILR"], :][F1] = 0
            wipe = F1 & (N["addr"] != S["addr"])
            trk[wipe] = 0
        # Workspace.Flag1/2 (Gray p.41-42) with computed Address/Age and the *current* (repaired)
        # SimBit at the site with address Q-3 (resp. 3) of x's colony.
        # The local rule also acts on arbitrary periodic configurations; the
        # initial-state factory's colony count is not the input ring length.
        A = N["addr"]; G = N["age"]; Q = p.Q; L = A.shape[1]
        x = np.arange(L)[None, :]
        site1 = (x - A + (Q - 3)) % L
        site2 = (x - A + 3) % L
        infoV = V[:, :, T["INFO"]]
        sb1 = np.take_along_axis(infoV, site1, axis=1)
        sb2 = np.take_along_axis(infoV, site2, axis=1)
        tlo, thi = self.trickle_window()
        in_win = (G >= tlo) & (G < thi)
        wf1 = (A >= Q - 5) & (A <= Q - 1) & in_win & (sb1 == 1)
        wf2 = (A >= 0) & (A <= 4) & in_win & (sb2 == 1) & (~F1)
        out = dict(addr=N["addr"], age=N["age"], f1=N["f1"], f2=N["f2"],
                   wf1=wf1.astype(np.int8), wf2=wf2.astype(np.int8), trk=trk,
                   simage=N["simage"], simaddr=N["simaddr"])
        out.update({k:N[k] for k in self.register_names})
        return out

    def trickle_window(self):
        return self.trickle if getattr(self, "trickle", None) else (3 * self.p.U // 4, 3 * self.p.U // 4 + 2 * self.p.Q)


def apply_noise(S, p, eps, rng, register_bits=16, nested_register_bits=0):
    """Whole-cell replacement noise including all track copies."""
    if not isinstance(register_bits, int) or not 16 <= register_bits <= 31:
        raise ValueError("register_bits must be an integer in [16,31]")
    if ("simage2" in S) != ("simaddr2" in S):
        raise ValueError("both nested control fields must be present")
    if "simage2" in S and (not isinstance(nested_register_bits, int) or not 16 <= nested_register_bits <= 31):
        raise ValueError("explicit nested register width required for extended state")
    if eps <= 0:
        return S
    B, L = S["addr"].shape
    hit = rng.random((B, L)) < eps
    n = int(hit.sum())
    out = dict(S)
    if n:
        for k, hi in (("addr", p.Q), ("age", p.U), ("simage", 1 << register_bits), ("simaddr", 1 << register_bits)):
            a = S[k].copy(); a[hit] = rng.integers(0, hi, n, dtype=a.dtype); out[k] = a
        for k in ("simage2", "simaddr2"):
            if k in S:
                a = S[k].copy(); a[hit] = rng.integers(0, 1 << nested_register_bits, n, dtype=a.dtype); out[k] = a
        for k in ("f1", "f2", "wf1", "wf2"):
            a = S[k].copy(); a[hit] = rng.integers(0, 2, n).astype(a.dtype); out[k] = a
        trk = S["trk"].copy()
        trk[hit] = rng.integers(0, 2, (n,) + trk.shape[2:], dtype=np.uint8); out["trk"] = trk
    out["_hit"] = hit
    return out
