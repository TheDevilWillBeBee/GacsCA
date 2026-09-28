"""Literal, per-cell transcription of Gray's level-0 transition rules (Reader's Guide, Sec. 5.2).

This module is deliberately scalar and slow.  It is the *specification*; the vectorized NumPy
and CUDA implementations are tested against it on random configurations.

Fields of the local structure + Flags at site x:
    addr(x) in [0, Q)      Address
    age(x)  in [0, U)      Age
    f1(x), f2(x) in {0,1}  Flag1, Flag2
Also read (for the coupling with the simulation structure):
    wf1(x), wf2(x) in {0,1}  Workspace.Flag1, Workspace.Flag2  (Gray Sec. 5.5)

Notation (Gray p.20):  R(x) = {x+1..x+5},  L(x) = {x-1..x-5},  N(x) = {x-5..x+5}.
The lattice is a ring of length L (periodic); all indices are taken mod L.
"""
from collections import Counter
from .params import RANGE, Variant


class Cfg:
    """A configuration: plain python lists (or arrays) indexed by site, periodic."""

    def __init__(self, addr, age, f1, f2, wf1=None, wf2=None):
        self.addr, self.age, self.f1, self.f2 = addr, age, f1, f2
        n = len(addr)
        self.wf1 = wf1 if wf1 is not None else [0] * n
        self.wf2 = wf2 if wf2 is not None else [0] * n
        self.L = n


def _majority(values, current, variant: Variant):
    """Gray p.22: 'if the voting does not produce a clear majority ... the outcome ... is
    defined to be the current value at x'."""
    cnt = Counter(values).most_common()
    top, ntop = cnt[0]
    if variant.majority == "strict":
        return top if ntop >= 3 else current
    # plurality with tie -> current
    if len(cnt) > 1 and cnt[1][1] == ntop:
        return current
    return top


def apparent_colony(cfg: Cfg, x: int, Q: int):
    """Gray p.20.  Returns v = position of x inside C(x) (so C(x) = [x-v, x-v+Q)), or None.

    Each site y = x+i in R(x) 'votes' for x's address to be (addr(y) - i) mod Q.  C(x) exists
    iff at least three of the five votes agree (the agreeing value is then unique)."""
    votes = [(cfg.addr[(x + i) % cfg.L] - i) % Q for i in range(1, RANGE + 1)]
    v, n = Counter(votes).most_common(1)[0]
    return v if n >= 3 else None


def sites_in_C(x, v, Q, L, side):
    """Sites of R(x) (side=+1) or L(x) (side=-1) that lie inside C(x)=[x-v, x-v+Q).
    Returns list of (site, offset i>0)."""
    out = []
    for i in range(1, RANGE + 1):
        if side > 0:
            inside = v + i <= Q - 1
        else:
            inside = v - i >= 0
        if inside:
            out.append(((x + side * i) % L, i))
    return out


def inconsistency(cfg: Cfg, x: int, Q: int, v):
    """Gray p.20 conditions (i)-(iv)."""
    L = cfg.L
    if v is None:                                                     # (i)
        return True
    bad = 0
    for y, i in sites_in_C(x, v, Q, L, -1):                            # (ii)
        if cfg.addr[y] != (v - i):
            bad += 1
    if bad >= 3:
        return True
    ages_R = [cfg.age[(x + i) % L] for i in range(1, RANGE + 1)]
    a, n = Counter(ages_R).most_common(1)[0]
    if n < 3:                                                          # (iii)
        return True
    diff = sum(1 for y, i in sites_in_C(x, v, Q, L, -1) if cfg.age[y] != a)
    if diff >= 3:                                                      # (iv)
        return True
    return False


def step_cell(cfg: Cfg, x: int, Q: int, U: int, variant: Variant = Variant()):
    """Compute the new (addr, age, f1, f2) at site x.  Returns also a dict of intermediate
    computed values for inspection."""
    L = cfg.L
    v = apparent_colony(cfg, x, Q)
    incons = inconsistency(cfg, x, Q, v)

    R_all = [((x + i) % L, i) for i in range(1, RANGE + 1)]
    L_all = [((x - i) % L, i) for i in range(1, RANGE + 1)]
    R_C = sites_in_C(x, v, Q, L, +1) if v is not None else []
    L_C = sites_in_C(x, v, Q, L, -1) if v is not None else []
    N_C = ([(x, 0)] + R_C + L_C) if v is not None else []

    # ---- Flag1 (Gray p.21) ----
    c_i = incons
    c_ii = sum(cfg.f1[y] for y, _ in (R_C if variant.flag1_ii_in_colony else R_all)) >= 3
    c_iii = sum(cfg.wf1[y] for y, _ in N_C) >= 3
    if cfg.f1[x] == 0:
        F1 = 1 if (c_i or c_ii or c_iii) else 0
    else:
        a = sum(cfg.f1[y] for y, _ in R_C) <= 1
        F1 = 0 if ((not c_i) and (not c_iii) and a) else 1

    # ---- Age vote needed for Flag2 cond (iii) when C(x) does not exist ----
    # When C(x) does not exist the Age rule below always votes in L(x), independent of Flag2,
    # so the 'computed value of Age' in cond (iii) is well defined.
    ages_L = [cfg.age[y] for y, _ in L_all]
    ages_R = [cfg.age[y] for y, _ in R_all]
    age_from_L = (_majority(ages_L, cfg.age[x], variant) + 1) % U

    # ---- Flag2 (Gray p.21) ----
    d_i = sum(cfg.f2[y] for y, _ in L_C) >= 4
    d_ii = (F1 == 1) and sum(cfg.f2[y] for y, _ in L_all) >= 4
    if variant.flag2_iii_age == "computed":
        d_iii = (v is None) and (age_from_L % 16 == 0)
    else:
        d_iii = (v is None) and (cfg.age[x] % 16 == 0)
    d_iv = sum(cfg.wf2[y] for y, _ in N_C) >= 3
    if cfg.f2[x] == 0:
        F2 = 1 if (d_i or d_ii or d_iii or d_iv) else 0
    else:
        a = (F1 == 0) and all(cfg.f2[y] == 1 for y, _ in L_C)   # 'no site in L&C has Flag2 = 0'
        if variant.flag2_healthy_erase != "printed":
            limit = 0 if variant.flag2_healthy_erase == "no_ones" else 1
            a = (F1 == 0) and sum(cfg.f2[y] for y, _ in L_C) <= limit
        b = (F1 == 1) and all(cfg.f2[y] == 0 for y, _ in L_all)  # 'no site in L has Flag2 = 1'
        F2 = 0 if ((not d_iii) and (not d_iv) and (a or b)) else 1

    # ---- Address and Age (Gray p.22) ----
    vote_right = (v is not None) and (F1 == 0 or F2 == 1)
    if vote_right:
        addr_votes = [(cfg.addr[y] - i) % Q for y, i in R_all]
        age_votes = ages_R
    else:
        addr_votes = [(cfg.addr[y] + i) % Q for y, i in L_all]
        age_votes = ages_L
    ADDR = _majority(addr_votes, cfg.addr[x], variant)
    m = _majority(age_votes, cfg.age[x], variant)
    AGE = (m + 1) % U if variant.age_increment_always else (
        (m + 1) % U if m != cfg.age[x] or Counter(age_votes).most_common(1)[0][1] >= 3 else cfg.age[x])

    info = dict(v=v, incons=incons, vote_right=vote_right, c_ii=c_ii, d_i=d_i, d_ii=d_ii, d_iii=d_iii)
    return ADDR, AGE, F1, F2, info


def step(cfg: Cfg, Q: int, U: int, variant: Variant = Variant()) -> Cfg:
    """Synchronous update of the whole ring (local structure + Flags only)."""
    n = cfg.L
    addr, age, f1, f2 = [0] * n, [0] * n, [0] * n, [0] * n
    for x in range(n):
        addr[x], age[x], f1[x], f2[x], _ = step_cell(cfg, x, Q, U, variant)
    return Cfg(addr, age, f1, f2, list(cfg.wf1), list(cfg.wf2))


def initial(Q: int, ncol: int) -> Cfg:
    """Gray p.14-15: Address(x) = x mod Q, Age = 0, Flags = 0."""
    n = Q * ncol
    return Cfg([x % Q for x in range(n)], [0] * n, [0] * n, [0] * n)
