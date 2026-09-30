"""Gray section 5.2 local structure (candidate-B Flag2) as a netlist.

This is a transcription of `stream28_holder_core.maintenance`, parameterized
by Q=2^k and U=2^m. It is cross-checked against that independent scalar code
(at its own Q=2^13, U=2^28) and against `maintenance_scalar` below.
Radius five: the inputs are the Address/Age/Flag1/Flag2/Wf1/Wf2 fields of
cells -5..5.
"""
from .netlist import (w_eq, w_add_const, w_mux, w_ult_const, at_least,
                      majority_word, const_word, w_add_const_mod, mixed_age_increment)


def build(n, cells, k, m, Q=None, nb=None, radix=None, pos_bits=None):
    """cells: dict j -> dict(addr=[k], age=[m], f1, f2, wf1, wf2) for j=-5..5.

    Returns dict with computed `addr` (k bits, the new Address), computed
    current `age_now` (m bits, before the increment), new `age`, `f1`, `f2`.

    Default: Q = 2^k and U = 2^m. With `Q` (any Q <= 2^k, a multiple of 16)
    and `nb`, Addresses are taken mod Q and Age is stored packed as
    (position mod radix in the low pos_bits bits, block in [0, nb) above),
    U = nb * radix (radix defaults to Q, pos_bits to k).
    The default netlist is unchanged by these options.
    """
    exact = Q is not None
    if not exact:
        Q = 1 << k
    add = (lambda a, v: w_add_const_mod(n, a, v, Q)) if exact else (lambda a, v: w_add_const(n, a, v))
    c = cells[0]
    adjusted = {j: add(cells[j]['addr'], (-j) % Q)
                for j in (*range(-5, 0), *range(1, 6))}
    v, exists = majority_word(n, [adjusted[j] for j in range(1, 6)], c['addr'])
    inside = {}
    for j in range(-5, 6):
        # 0 <= v + j < Q
        if j >= 0:
            ok = w_ult_const(n, v, Q - j)
        else:
            ok = n.NOT(w_ult_const(n, v, -j))
        inside[j] = n.AND(exists, ok)
    age_r, age_exists = majority_word(n, [cells[j]['age'] for j in range(1, 6)], c['age'])
    age_l, _ = majority_word(n, [cells[j]['age'] for j in range(-1, -6, -1)], c['age'])
    addr_mismatch = [n.AND(inside[j], n.NOT(w_eq(n, cells[j]['addr'], add(v, j % Q))))
                     for j in range(-1, -6, -1)]
    age_mismatch = [n.AND(inside[j], n.NOT(w_eq(n, cells[j]['age'], age_r)))
                    for j in range(-1, -6, -1)]
    incons = n.any([n.NOT(exists), n.NOT(age_exists),
                    at_least(n, addr_mismatch, 3), at_least(n, age_mismatch, 3)])
    flag_bits = [n.AND(inside[j], cells[j]['f1']) for j in range(1, 6)]
    flags3 = at_least(n, flag_bits, 3)
    flags2 = at_least(n, flag_bits, 2)
    wf1 = at_least(n, [n.AND(inside[j], cells[j]['wf1']) for j in range(-5, 6)], 3)
    f1 = n.any([incons, wf1, flags3, n.AND(c['f1'], flags2)])
    d3 = n.AND(n.NOT(exists), n.all(age_l[:4]))           # (age_l + 1) % 16 == 0
    d4 = at_least(n, [n.AND(inside[j], cells[j]['wf2']) for j in range(-5, 6)], 3)
    left = [cells[j]['f2'] for j in range(-1, -6, -1)]
    left_inside = [n.AND(inside[j], cells[j]['f2']) for j in range(-1, -6, -1)]
    on = n.any([at_least(n, left_inside, 4), n.AND(f1, at_least(n, left, 4)), d3, d4])
    erase = n.OR(n.AND(n.NOT(f1), n.NOT(at_least(n, left_inside, 2))),
                 n.AND(f1, n.NOT(n.any(left))))
    keep = n.any([d3, d4, n.NOT(erase)])
    f2 = n.MUX(c['f2'], keep, on)
    addr_l, _ = majority_word(n, [adjusted[j] for j in range(-1, -6, -1)], c['addr'])
    vote_right = n.AND(exists, n.OR(n.NOT(f1), f2))
    addr = w_mux(n, vote_right, v, addr_l)
    age_now = w_mux(n, vote_right, age_r, age_l)
    if exact:
        age = mixed_age_increment(n, age_now, pos_bits or k, radix or Q, nb)
    else:
        age = w_add_const(n, age_now, 1)
    return dict(addr=addr, age_now=age_now, age=age, f1=f1, f2=f2)


def maintenance_scalar(cells, Q, U):
    """Independent integer transcription (same semantics as candidate B).

    cells: dict j -> dict(addr, age, f1, f2, wf1, wf2) for j=-5..5.
    """
    c = cells[0]
    r = cells

    def majority(values, default):
        for cand in values:
            if values.count(cand) >= 3:
                return cand, True
        return default, False

    adjusted = {j: (r[j]['addr'] - j) % Q for j in (*range(-5, 0), *range(1, 6))}
    v, exists = majority([adjusted[j] for j in range(1, 6)], c['addr'])
    inside = {j: exists and 0 <= v + j < Q for j in range(-5, 6)}
    age_r, age_exists = majority([r[j]['age'] for j in range(1, 6)], c['age'])
    age_l, _ = majority([r[j]['age'] for j in range(-1, -6, -1)], c['age'])
    incons = (not exists or not age_exists or
              sum(inside[j] and r[j]['addr'] != (v + j) % Q for j in range(-1, -6, -1)) >= 3 or
              sum(inside[j] and r[j]['age'] != age_r for j in range(-1, -6, -1)) >= 3)
    flags = sum(inside[j] and r[j]['f1'] for j in range(1, 6))
    f1 = int(incons or sum(inside[j] and r[j]['wf1'] for j in range(-5, 6)) >= 3 or
             flags >= 3 or (c['f1'] and flags >= 2))
    d3 = (not exists) and (age_l + 1) % 16 == 0
    d4 = sum(inside[j] and r[j]['wf2'] for j in range(-5, 6)) >= 3
    left_flags = [r[j]['f2'] for j in range(-1, -6, -1)]
    on = (sum(inside[j] and r[j]['f2'] for j in range(-1, -6, -1)) >= 4 or
          (f1 and sum(left_flags) >= 4) or d3 or d4)
    erase = ((not f1 and sum(inside[j] and r[j]['f2'] for j in range(-1, -6, -1)) <= 1) or
             (f1 and not any(left_flags)))
    f2 = int((d3 or d4 or not erase) if c['f2'] else on)
    addr_l, _ = majority([adjusted[j] for j in range(-1, -6, -1)], c['addr'])
    vote_right = exists and (not f1 or f2)
    age_now = age_r if vote_right else age_l
    return dict(addr=v if vote_right else addr_l, age_now=age_now,
                age=(age_now + 1) % U, f1=f1, f2=f2)
