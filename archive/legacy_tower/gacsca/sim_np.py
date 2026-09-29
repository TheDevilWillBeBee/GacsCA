"""Simulation driver for the NumPy level-0 automaton with recording of space-time data."""
import numpy as np
from .params import Params, Variant
from . import level0_np as l0
from .noise import apply_noise_np


def run(p: Params, T: int, eps_schedule, B=1, seed=0, variant=Variant(), record=("addr", "age", "f1", "f2", "hit"),
        init=None, noise_mask=None, every=1):
    """eps_schedule: float or callable t -> eps.  Returns dict of recorded arrays (T//every+1, B, L)."""
    rng = np.random.default_rng(seed)
    S = l0.initial(p, B) if init is None else init
    eps_f = eps_schedule if callable(eps_schedule) else (lambda t: eps_schedule)
    rec = {k: [] for k in record}

    def snap(S, hit):
        for k in record:
            if k == "hit":
                rec[k].append(hit.copy())
            else:
                rec[k].append(S[k].copy())
    snap(S, np.zeros(S["addr"].shape, bool))
    for t in range(1, T + 1):
        S = l0.step(S, p, variant)
        S = apply_noise_np(S, p, eps_f(t), rng, mask=noise_mask)
        hit = S.pop("_hit", np.zeros(S["addr"].shape, bool))
        S.pop("_info", None)
        if t % every == 0:
            snap(S, hit)
    return {k: np.stack(v) for k, v in rec.items()}, S


def damage(S, p, t=None):
    """Boolean (B,L): sites whose Address (and Age, if t given) differ from the ground state."""
    L = p.L
    bad = S["addr"] != (np.arange(L) % p.Q)
    if t is not None:
        bad |= S["age"] != (t % p.U)
    return bad
