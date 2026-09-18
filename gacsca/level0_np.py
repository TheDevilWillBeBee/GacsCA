"""Vectorized NumPy implementation of Gray's level-0 rules (local structure + Flags).

State arrays have shape (B, L): B independent trials, L = ncol*Q sites on a ring.
Semantics are defined by gacsca.level0_spec; tests/test_level0.py checks equivalence.
"""
import numpy as np
from .params import RANGE, Params, Variant

OFFS = np.arange(1, RANGE + 1)  # 1..5


def roll(a, k):
    """b[..., x] = a[..., x + k]  (periodic)."""
    return np.roll(a, -k, axis=-1)


def stack_R(a):
    """(B, L, 5): values at x+1..x+5"""
    return np.stack([roll(a, i) for i in OFFS], axis=-1)


def stack_L(a):
    """(B, L, 5): values at x-1..x-5"""
    return np.stack([roll(a, -i) for i in OFFS], axis=-1)


def majority5(votes, current, variant: Variant):
    """votes: (..., 5) ints; current: (...).  Gray's 'clear majority' convention."""
    # count, for each vote, how many of the 5 equal it
    eq = (votes[..., :, None] == votes[..., None, :]).sum(-1)          # (..., 5)
    best = eq.argmax(-1)                                               # index of a most-frequent vote
    nbest = np.take_along_axis(eq, best[..., None], -1)[..., 0]
    val = np.take_along_axis(votes, best[..., None], -1)[..., 0]
    if variant.majority == "strict":
        return np.where(nbest >= 3, val, current)
    # plurality: tie if another distinct value has the same count
    tie = ((eq == nbest[..., None]) & (votes != val[..., None])).any(-1)
    return np.where(tie, current, val)


def apparent_colony(addr, Q):
    """Returns (exists (B,L) bool, v (B,L) int).  v = position of x in C(x)."""
    votes = (stack_R(addr) - OFFS) % Q                                  # (B,L,5)
    eq = (votes[..., :, None] == votes[..., None, :]).sum(-1)
    best = eq.argmax(-1)
    nbest = np.take_along_axis(eq, best[..., None], -1)[..., 0]
    v = np.take_along_axis(votes, best[..., None], -1)[..., 0]
    return nbest >= 3, v


def step(S, p: Params, variant: Variant = Variant()):
    """S: dict with 'addr','age','f1','f2' (and optionally 'wf1','wf2') arrays of shape (B,L).
    Returns new dict with updated addr, age, f1, f2 (wf1/wf2 passed through)."""
    Q, U = p.Q, p.U
    addr, age, f1, f2 = S["addr"], S["age"], S["f1"], S["f2"]
    wf1 = S.get("wf1", np.zeros_like(f1))
    wf2 = S.get("wf2", np.zeros_like(f2))

    exists, v = apparent_colony(addr, Q)
    # membership masks of R(x), L(x) sites in C(x): offset i is inside iff v+i<=Q-1 / v-i>=0
    inR_C = exists[..., None] & ((v[..., None] + OFFS) <= Q - 1)        # (B,L,5)
    inL_C = exists[..., None] & ((v[..., None] - OFFS) >= 0)

    addr_R, addr_L = stack_R(addr), stack_L(addr)
    age_R, age_L = stack_R(age), stack_L(age)
    f1_R, f1_L = stack_R(f1), stack_L(f1)
    f2_R, f2_L = stack_R(f2), stack_L(f2)
    wf1_R, wf1_L = stack_R(wf1), stack_L(wf1)
    wf2_R, wf2_L = stack_R(wf2), stack_L(wf2)

    # ---- inconsistency (i)-(iv) ----
    bad_addr = (inL_C & (addr_L != (v[..., None] - OFFS))).sum(-1) >= 3           # (ii)
    eqR = (age_R[..., :, None] == age_R[..., None, :]).sum(-1)
    bestR = eqR.argmax(-1)
    n_a = np.take_along_axis(eqR, bestR[..., None], -1)[..., 0]
    a = np.take_along_axis(age_R, bestR[..., None], -1)[..., 0]
    no3 = n_a < 3                                                                   # (iii)
    diff = (inL_C & (age_L != a[..., None])).sum(-1) >= 3                           # (iv)
    incons = (~exists) | bad_addr | no3 | (~no3 & diff)

    # ---- Flag1 ----
    if variant.flag1_ii_in_colony:
        c_ii = (f1_R * inR_C).sum(-1) >= 3
    else:
        c_ii = f1_R.sum(-1) >= 3
    c_iii = ((wf1_R * inR_C).sum(-1) + (wf1_L * inL_C).sum(-1) + wf1 * exists) >= 3
    on = incons | c_ii | c_iii
    off = (~incons) & (~c_iii) & ((f1_R * inR_C).sum(-1) <= 1)
    F1 = np.where(f1 == 0, on.astype(f1.dtype), np.where(off, 0, 1).astype(f1.dtype))

    # ---- Age from L (needed for Flag2 (iii)) ----
    age_from_L = (majority5(age_L, age, variant) + 1) % U

    # ---- Flag2 ----
    d_i = (f2_L * inL_C).sum(-1) >= 4
    d_ii = (F1 == 1) & (f2_L.sum(-1) >= 4)
    if variant.flag2_iii_age == "computed":
        d_iii = (~exists) & (age_from_L % 16 == 0)
    else:
        d_iii = (~exists) & (age % 16 == 0)
    d_iv = ((wf2_R * inR_C).sum(-1) + (wf2_L * inL_C).sum(-1) + wf2 * exists) >= 3
    on2 = d_i | d_ii | d_iii | d_iv
    a2 = (F1 == 0) & (((1 - f2_L) * inL_C).sum(-1) == 0)
    b2 = (F1 == 1) & (f2_L.sum(-1) == 0)
    off2 = (~d_iii) & (~d_iv) & (a2 | b2)
    F2 = np.where(f2 == 0, on2.astype(f2.dtype), np.where(off2, 0, 1).astype(f2.dtype))

    # ---- Address / Age ----
    vote_right = exists & ((F1 == 0) | (F2 == 1))
    addr_votes = np.where(vote_right[..., None], (addr_R - OFFS) % Q, (addr_L + OFFS) % Q)
    age_votes = np.where(vote_right[..., None], age_R, age_L)
    ADDR = majority5(addr_votes, addr, variant)
    AGE = (majority5(age_votes, age, variant) + 1) % U

    out = dict(S)
    out.update(addr=ADDR.astype(addr.dtype), age=AGE.astype(age.dtype), f1=F1, f2=F2)
    # Workspace.Flag1/2 are recomputed every step from the simulation structure (Gray Sec. 5.5:
    # 1 -> 0 whenever any of their conditions fails).  Without a simulation structure they are 0.
    out["wf1"] = np.zeros_like(wf1); out["wf2"] = np.zeros_like(wf2)
    out["_info"] = dict(exists=exists, v=v, incons=incons, vote_right=vote_right)
    return out


def initial(p: Params, B: int = 1, dtype=np.int32):
    L = p.L
    x = np.arange(L)
    S = dict(addr=np.tile((x % p.Q).astype(dtype), (B, 1)),
             age=np.zeros((B, L), dtype),
             f1=np.zeros((B, L), np.int8), f2=np.zeros((B, L), np.int8),
             wf1=np.zeros((B, L), np.int8), wf2=np.zeros((B, L), np.int8))
    return S


def random_state(p: Params, B: int, rng, dtype=np.int32):
    L = p.L
    return dict(addr=rng.integers(0, p.Q, (B, L), dtype=dtype), age=rng.integers(0, p.U, (B, L), dtype=dtype),
                f1=rng.integers(0, 2, (B, L)).astype(np.int8), f2=rng.integers(0, 2, (B, L)).astype(np.int8),
                wf1=np.zeros((B, L), np.int8), wf2=np.zeros((B, L), np.int8))
