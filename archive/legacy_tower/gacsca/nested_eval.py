"""Local nested-IEVAL operand mapping and bit evaluation.

Only immutable program metadata and already transported holder-local bits are
read here. This never calls a simulated CA transition or accesses remote state.
The represented middle IEVAL occupies a dedicated instruction age, so the
outer interpreter's existing shared token/broadcast scratch can be reused.
"""
import numpy as np


def selected(ctx, op1, age):
    from .interp import slot_of
    for g in np.unique(age):
        active = ctx.inner.prog_up.ops_at(int(g))
        if 0 <= op1.param < len(active):
            yield age == g, active[op1.param], slot_of(active, op1.param)


def operands(ctx, op2, slot):
    """(middle scratch track, outer temporary) pairs; no additional tracks."""
    J, n = ctx.inner, ctx.n
    kind = op2.kind
    if kind in ("CONST", "RESET", "SWEEP_INIT", "REGWIN"):
        return []
    if kind == "BUSLATCH_INT":
        return [(J.n["BLB"], n["BLB"])]
    if kind in ("SHIFT", "RSHIFT"):
        return [(J.n[f"SHSRC{slot}"], n["SHSRC0"])]
    if kind == "BCAST":
        return [(J.n[f"S{slot}2"], n["S02"]), (J.n["BFOUND"], n["BFOUND"]), (J.n["BVAL"], n["BVAL"])]
    if kind in ("MOV", "IINIT", "BCAST_INIT"):
        result = [(J.n[f"S{slot}0"], n["S00"])]
        if kind == "MOV" and op2.param2:
            i = J.computed_move_addresses.index(op2.lo)
            result.append((J.n[f"CM{i}"], n["BLB"]))
        return result
    if kind in ("BITOP", "SWEEP"):
        result = [(J.n[f"S{slot}{j}"], n[f"S0{j}"]) for j in range(3)]
        if kind == "SWEEP":
            result += [(J.n[f"{prefix}{k}"], n[f"{prefix}{k}"])
                       for k in range(1, J.D_up + 1) for prefix in ("SIG", "CARRY")]
        return result
    raise NotImplementedError(f"nested IEVAL operand kind {kind}")


def evaluate(ctx, op1, address, age, simaddr, V):
    """Return per-writer (write mask, bit), preserving old-state token semantics."""
    from .interp import _cell_geometry, _chain, _kbit, writes
    J, T, n = ctx.inner, ctx.T, ctx.n
    geometry, _, track, copy = _cell_geometry(J, address)
    a2 = np.mod(simaddr + copy, J.L.Qs)
    own_guard = (address >= op1.lo) & (address < op1.hi)
    changed = np.zeros_like(own_guard)
    value = np.zeros_like(address, dtype=np.uint8)
    bit = lambda name: V[:, :, n[name]].astype(np.int32)
    S0, S1, S2 = bit("S00"), bit("S01"), bit("S02")

    def put(mask, val):
        changed[mask] = True
        value[mask] = val if np.isscalar(val) else val[mask]

    for clock_guard, op2, _ in selected(ctx, op1, age):
        gm = own_guard & clock_guard
        kind = op2.kind
        raw_range = (simaddr >= op2.lo) & (simaddr < op2.hi)
        if kind == "BUSLATCH_INT":
            for field, source in (("SIMAGE", "AGE"), ("SIMADDR", "ADDR")):
                lo, hi = J.L.frange(field)
                slo, shi = J.L_up.frange(source)
                for i in range(min(hi - lo, shi - slo)):
                    d = op2.param2 * (simaddr - slo - i)
                    sel = gm & raw_range & (address == lo + i) & (d >= 0)
                    sel &= d // J.D_up == age - op2.t0
                    put(sel, bit("BLB"))
            continue
        if kind == "RESET" and op2.param2:
            for field in ("SIMAGE", "SIMADDR"):
                lo, hi = J.L.frange(field)
                put(gm & raw_range & (address >= lo) & (address < hi), 0)
        wr = np.isin(track, list(writes(op2, T)))
        inr = (a2 >= op2.lo) & (a2 < op2.hi)
        if kind == "MOV" and op2.param2:
            inr = bit("BLB") == 1
        if kind == "IINIT":
            q = a2 - (J.L_up.b0 + J.L_up.track_base)
            inr &= (q >= 0) & (q < J.L_up.tracks.NT * J.R) & (q % J.R == op2.param + J.h)
        target = gm & geometry & wr
        base = target & inr
        if kind in ("RESET", "REGWIN"):
            put(base, 0)
        elif kind == "CONST":
            put(base, op2.param)
        elif kind in ("MOV", "IINIT", "BCAST_INIT"):
            put(base, S0)
        elif kind == "BITOP":
            put(base, (op2.param >> ((S0 << 2) | (S1 << 1) | S2)) & 1)
        elif kind == "SHIFT":
            inside = (a2 - op2.param >= op2.lo) & (a2 - op2.param < op2.hi)
            put(base, np.where(inside, bit("SHSRC0"), op2.param2))
        elif kind == "RSHIFT":
            put(base, bit("SHSRC0"))
        elif kind == "SWEEP_INIT":
            put(base & (track == T["SIG"]), 1)
            put(base & (track == op2.dst), op2.param)
        elif kind == "SWEEP":
            acted = np.zeros_like(base)
            out, carry, last = np.zeros_like(a2), np.zeros_like(a2), np.zeros_like(base)
            for k in range(1, J.D_up + 1):
                take = (bit(f"SIG{k}") == 1) & (a2 - k >= op2.lo - 1) & inr & ~acted
                new_out, new_carry = _chain(op2.skind, bit(f"CARRY{k}"), S0, S1, _kbit(op2.param, a2 - op2.lo))
                if new_out is not None: out = np.where(take, new_out, out)
                carry = np.where(take, new_carry, carry)
                last = np.where(take, (k == J.D_up) | (a2 == op2.hi - 1), last)
                acted |= take
            token = np.where(acted, last, (a2 == op2.hi - 1) & (S2 == 1))
            put(target & (track == T["SIG"]) & (a2 >= op2.lo - 1) & (a2 < op2.hi), token)
            put(target & acted & (track == T["ACC"]), carry)
            if op2.dst is not None: put(target & acted & (track == op2.dst), out)
        elif kind == "BCAST":
            take = base & (S2 == 0) & (bit("BFOUND") == 1)
            put(take & (track == op2.dst), bit("BVAL"))
            put(take & (track == T["SIG"]), 1)
        else:
            raise NotImplementedError(f"nested IEVAL bit kind {kind}")
    return changed, value
