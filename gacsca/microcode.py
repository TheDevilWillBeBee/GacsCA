"""Microprogram DSL for the colony computer (see Report/design_selfsim.md, Sec 2-3).

A *track* is a one-bit field of every cell, held R-fold redundantly (cell x keeps copies of the
track bit of x+off for off in OFFS = [-(R-1)/2 .. (R-1)/2]).  Every step the value of a track bit
is restored by majority over its R holders. Each holder independently computes its output copies,
using its own Age and offset-adjusted Address; it never trusts the target cell's raw clock/address.
Ops read repaired tracks within reach D and are restricted to an address range [lo, hi).

Op kinds (all per cell x, a = Address(x), V = repaired track values, P = new primaries):
  CONST  dst <- c                                   (a in [lo,hi))
  MOV    dst <- V[src][x]
  BITOP  dst <- f(V[s1][x], V[s2][x], V[s3][x])     f = 8-entry truth table
  SHIFT  dst <- V[src][x-d]  (|d| <= D)             cells whose source lies outside [lo,hi) get `fill`
  SWEEP  token sweep from lo to hi-1, D cells per step, computing a carry chain:
           kinds: EQC (acc &= (src bit == const bit)), EQF (acc &= (src==src2)), ORF,
                  INC (dst = src ^ cin, cout = src & cin), ADDC (dst = src^k^cin, cout=maj)
  BCAST  wavefront from hi-1 leftwards copying the ACC of the token holder into dst (D/step)

The compiler assigns ages; `Program.ops_at(age)` gives the ops active at an age.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict
import numpy as np

# ---------------------------------------------------------------- tracks & layout
class Tracks:
    """Track name registry.  ARG tracks are indexed by neighbour offset j in [-JMAX, JMAX]."""

    def __init__(self, JMAX=6, wq=8, wu=14, R=3, ntemp=22, temporal_banks=False):
        """The registry is independent of Q/U (the tower needs identical registries at all levels):
        JMAX=6 arg tracks each side and ntemp=22 extra temporaries (BF0..)."""
        self.R, self.JMAX = R, JMAX
        JMAX = 6
        names = ["INFO"]
        names += [f"ARGA{j:+d}" for j in range(-JMAX, JMAX + 1)]
        names += [f"ARGB{j:+d}" for j in range(-JMAX, JMAX + 1)]
        names += ["HOLD", "T0", "T1", "T2", "T3", "T4", "T5", "SIG", "ACC", "BC"]
        names += [f"BF{i}" for i in range(ntemp)]
        names += ["MAILL", "MAILR"]
        if temporal_banks:
            # A/B/C retain the three independent gathers; D is disposable
            # input for the stage-three flag computation, never a history bank.
            names += [f"ARG{bank}{j:+d}" for bank in "CD" for j in range(-JMAX, JMAX + 1)]
        self.names = names
        self.idx = {n: i for i, n in enumerate(names)}
        self.NT = len(names)

    def __getitem__(self, n):
        return self.idx[n]

    def arg(self, j, which="A"):
        return self.idx[f"ARG{which}{j:+d}"]


@dataclass
class Layout:
    """Bit layout of the *simulated* cell state as a bit-serial string living in the Info track of
    a colony of the simulating level at addresses [b0, b0+K).  Little-endian fields.
    Q, U: colony size / work period of the simulating level (where the string lives).
    Qs, Us: parameters of the simulated level (address modulus, work period) - default = Q, U.
    with_tracks: whether the simulated cell has simulation-structure tracks (False: local-only cell).
    The local part is ADDR, AGE, F1, F2, WF1, WF2, SIMAGE, SIMADDR (the simulated cell's own
    registers for the level above it, widths from Qss/Uss)."""
    Q: int
    U: int
    tracks: Tracks
    b0: int = 8
    Qs: int = None
    Us: int = None
    with_tracks: bool = True
    Qss: int = None      # parameters of the level above the simulated one (for its SIMADDR/SIMAGE)
    Uss: int = None
    full_registers: bool = False  # legacy narrow fields retained only for replay

    def __post_init__(self):
        if self.Qs is None: self.Qs = self.Q
        if self.Us is None: self.Us = self.U
        if self.Qss is None: self.Qss = self.Qs
        if self.Uss is None: self.Uss = self.Us
        self.wq = (self.Qs - 1).bit_length()
        self.wu = (self.Us - 1).bit_length()
        self.wqs = (self.Qss - 1).bit_length()
        self.wus = (self.Uss - 1).bit_length()
        if self.full_registers:
            # Match the represented cell's actual GPU register alphabet, not
            # just its normal control-value range. Whole-cell faults can set
            # any of these bits, including out-of-range simulated controls.
            self.wqs = self.wus = max(16, self.wqs, self.wus)
        self.fields: Dict[str, Tuple[int, int]] = {}
        p = 0
        for name, w in [("ADDR", self.wq), ("AGE", self.wu), ("F1", 1), ("F2", 1), ("WF1", 1), ("WF2", 1),
                        ("SIMAGE", self.wus), ("SIMADDR", self.wqs)]:
            self.fields[name] = (p, w); p += w
        self.track_base = p
        self.K = p + (self.tracks.NT * self.tracks.R if self.with_tracks else 0)
        assert self.b0 + self.K <= self.Q - 4, f"K={self.K} does not fit in Q={self.Q}"

    def pos(self, t, r):
        """address of copy r of track t of the simulated cell"""
        return self.b0 + self.track_base + t * self.tracks.R + r

    def frange(self, name):
        p, w = self.fields[name]
        return self.b0 + p, self.b0 + p + w

    def encode(self, addr, age, f1, f2, trackbits, wf1=0, wf2=0, simage=0, simaddr=0):
        """-> K-bit array (index i = address b0+i).  trackbits: (NT, R) array or None."""
        bits = np.zeros(self.K, np.uint8)
        for name, val in [("ADDR", addr), ("AGE", age), ("F1", f1), ("F2", f2), ("WF1", wf1), ("WF2", wf2),
                          ("SIMAGE", simage), ("SIMADDR", simaddr)]:
            p, w = self.fields[name]
            for i in range(w):
                bits[p + i] = (int(val) >> i) & 1
        if trackbits is not None and self.with_tracks:
            bits[self.track_base:] = np.asarray(trackbits, np.uint8).reshape(-1)
        return bits

    def decode(self, bits):
        out = {}
        for name, (p, w) in self.fields.items():
            out[name] = int(sum(int(bits[p + i]) << i for i in range(w)))
        if self.with_tracks:
            out["tracks"] = np.asarray(bits[self.track_base:], np.uint8).reshape(self.tracks.NT, self.tracks.R)
        return out


# ---------------------------------------------------------------- ops
@dataclass
class Op:
    kind: str
    t0: int
    t1: int                     # active for ages in [t0, t1)
    lo: int = 0
    hi: int = 0
    dst: Optional[int] = None
    src: Optional[int] = None
    src2: Optional[int] = None
    src3: Optional[int] = None
    param: int = 0              # constant / truth table / shift amount / fill
    param2: int = 0
    skind: str = ""             # sweep kind
    tag: str = ""


class Program:
    def __init__(self, D=1, U=None):
        self.ops: List[Op] = []
        self.D = D
        self.U = U
        self.nested_register_bits = 0  # optional second raw-input control pair; 0 preserves legacy layout
        self._by_age = None

    def add(self, op: Op):
        self.ops.append(op); self._by_age = None
        return op

    def ops_at(self, age):
        if self._by_age is None:
            self._by_age = {}
            for op in self.ops:
                for a in range(op.t0, op.t1):
                    self._by_age.setdefault(a, []).append(op)
        return self._by_age.get(int(age), [])

    @property
    def length(self):
        return max((op.t1 for op in self.ops), default=0)


class Compiler:
    """Emits ops sequentially; `self.t` is the current age.  Parallel ops: use `par()`."""

    def __init__(self, tracks: Tracks, layout: Layout, D=1, t=0):
        self.T, self.L, self.D = tracks, layout, D
        self.prog = Program(D=D)
        self.t = t

    # -- helpers --
    def _range(self, rng):
        if isinstance(rng, str):
            return self.L.frange(rng)
        return rng

    def emit(self, kind, dur=1, **kw):
        rng = kw.pop("rng", (0, self.L.Q))
        lo, hi = self._range(rng)
        op = Op(kind=kind, t0=self.t, t1=self.t + dur, lo=lo, hi=hi, **kw)
        self.prog.add(op)
        return op

    # -- simple per-cell ops (1 step) --
    def const(self, dst, c, rng=None, advance=True):
        op = self.emit("CONST", dst=self.T[dst], param=c, rng=rng or (0, self.L.Q))
        if advance: self.t += 1
        return op

    def mov(self, dst, src, rng=None, advance=True, computed_address=False):
        # Gray p.35 signals select destinations using the holder's computed
        # Address. Other instructions retain their existing input controls.
        op = self.emit("MOV", dst=self.T[dst], src=self.T[src], rng=rng or (0, self.L.Q),
                       param2=int(computed_address))
        if advance: self.t += 1
        return op

    def bitop(self, dst, table, s1, s2=None, s3=None, rng=None, advance=True):
        """table: function (b1,b2,b3)->bit or an int truth table with bit index (b1<<2)|(b2<<1)|b3"""
        if callable(table):
            tb = 0
            for b1 in (0, 1):
                for b2 in (0, 1):
                    for b3 in (0, 1):
                        if table(b1, b2, b3): tb |= 1 << ((b1 << 2) | (b2 << 1) | b3)
            table = tb
        op = self.emit("BITOP", dst=self.T[dst], src=self.T[s1], src2=self.T[s2] if s2 else None,
                       src3=self.T[s3] if s3 else None, param=table, rng=rng or (0, self.L.Q))
        if advance: self.t += 1
        return op

    def shift(self, dst, src, d, rng, fill=0):
        """dst[x] <- src[x-d] within rng (|d| arbitrary; split into steps of <= D).  If dst != src the
        first step copies into dst and further steps shift dst in place."""
        lo, hi = self._range(rng)
        cur = self.T[src]
        remaining = d
        if d == 0:
            self.mov(dst, src, rng=(lo, hi)); return
        while remaining != 0:
            s = max(-self.D, min(self.D, remaining))
            self.emit("SHIFT", dst=self.T[dst], src=cur, param=s, param2=fill, rng=(lo, hi))
            self.t += 1
            cur = self.T[dst]
            remaining -= s

    # -- sweeps --
    def sweep(self, skind, rng, src=None, src2=None, dst=None, const=0, acc_init=0, tag=""):
        """Token sweep over [lo,hi): INIT at lo-1 then steps of D cells.  Returns nothing; the ACC of
        cell hi-1 holds the reduction result afterwards (token remains at hi-1 with SIG=1)."""
        lo, hi = self._range(rng)
        assert lo >= 1
        self.emit("SWEEP_INIT", dst=self.T["ACC"], param=acc_init, rng=(lo - 1, lo))
        self.t += 1
        w = hi - lo
        nsteps = (w + self.D - 1) // self.D
        self.emit("SWEEP", dur=nsteps, skind=skind, src=self.T[src] if src else None,
                  src2=self.T[src2] if src2 else None, dst=self.T[dst] if dst else None,
                  param=const, param2=lo, rng=(lo, hi), tag=tag)
        self.t += nsteps
        return nsteps

    def bcast(self, dst, rng, src="ACC", clear=True, right=None):
        """Broadcast the src bit of the token holder at hi-1 (SIG=1) leftwards over [lo,hi) into dst.
        If right=(hi-1, hi2) is given, also spread rightwards over that range (token at hi-1)."""
        lo, hi = self._range(rng)
        self.emit("BCAST_INIT", dst=self.T[dst], src=self.T[src], rng=(hi - 1, hi))
        self.t += 1
        w = hi - lo
        nsteps = (w - 1 + self.D - 1) // self.D
        if right is not None:
            rlo, rhi = right
            nsteps = max(nsteps, (rhi - rlo - 1 + self.D - 1) // self.D)
        if nsteps > 0:
            self.emit("BCAST", dur=nsteps, dst=self.T[dst], rng=(lo, hi), param=-1)
            if right is not None:
                self.emit("BCAST", dur=nsteps, dst=self.T[dst], rng=right, param=+1)
            self.t += nsteps
        if clear:
            top = hi if right is None else right[1]
            self.const("SIG", 0, rng=(max(lo - 1, 0), top))

    def spread(self, src_bit_addr, dst, rng, src):
        """Spread the bit of track src at a single address over rng (both directions) into dst."""
        lo, hi = self._range(rng)
        a = src_bit_addr
        self.emit("SWEEP_INIT", dst=self.T["ACC"], param=0, rng=(a, a + 1))   # plant token
        self.t += 1
        self.emit("BCAST_INIT", dst=self.T[dst], src=self.T[src], rng=(a, a + 1))
        self.t += 1
        nsteps = max(a - lo, hi - 1 - a)
        nsteps = (nsteps + self.D - 1) // self.D
        if nsteps > 0:
            if a > lo: self.emit("BCAST", dur=nsteps, dst=self.T[dst], rng=(lo, a + 1), param=-1)
            if a < hi - 1: self.emit("BCAST", dur=nsteps, dst=self.T[dst], rng=(a, hi), param=+1)
            self.t += nsteps
        self.const("SIG", 0, rng=(max(lo - 1, 0), hi))

    # -- macros on bit-serial fields --
    def eq_const(self, src, rng, c, dst, bc_rng=None):
        """dst (broadcast over bc_rng or rng) <- [field src over rng == c]"""
        self.sweep("EQC", rng, src=src, const=c, acc_init=1)
        self.bcast(dst, bc_rng or rng)

    def eq_field(self, s1, s2, rng, dst, bc_rng=None):
        self.sweep("EQF", rng, src=s1, src2=s2, acc_init=1)
        self.bcast(dst, bc_rng or rng)

    def add_const(self, dst, src, rng, c):
        """dst <- (src + c) mod 2^w over rng (little-endian)."""
        self.sweep("ADDC", rng, src=src, dst=dst, const=c, acc_init=0)
        lo, hi = self._range(rng)
        self.const("SIG", 0, rng=(lo - 1, hi))

    def lt_const(self, src, rng, c, dst, bc_rng=None):
        """dst <- [field src over rng < c] (unsigned)"""
        self.sweep("LTC", rng, src=src, const=c, acc_init=0)
        self.bcast(dst, bc_rng or rng)

    def or_reduce(self, src, rng, dst, bc_rng=None):
        self.sweep("ORF", rng, src=src, acc_init=0)
        self.bcast(dst, bc_rng or rng)

    def rest(self, n):
        self.t += n
