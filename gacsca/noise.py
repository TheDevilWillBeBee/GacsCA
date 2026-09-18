"""Noise models (Gray Sec. 1: error set E with rate eps; noise distribution nu).

Masumori et al.: 'at each time step, a number of cells are destroyed according to the error
rate. The entire contents of the cell is replaced with a random bit string.'
"""
import numpy as np


def apply_noise_np(S, p, eps, rng, mask=None, addr_mode="valid"):
    """Replace each cell (independently, prob eps) by a random state.
    mask: optional (B,L) bool restricting where errors may occur (e.g. spatial bursts).
    addr_mode: 'valid' -> Address uniform in [0,Q), Age uniform in [0,U);
               'bits'  -> uniform over the bit-string width (values may exceed Q-1 / U-1)."""
    if eps <= 0:
        return S
    B, L = S["addr"].shape
    hit = rng.random((B, L)) < eps
    if mask is not None:
        hit &= mask
    n = int(hit.sum())
    if n == 0:
        return S
    if addr_mode == "valid":
        qa, qu = p.Q, p.U
    else:
        qa, qu = 1 << (p.Q - 1).bit_length(), 1 << (p.U - 1).bit_length()
    out = dict(S)
    for k, hi in (("addr", qa), ("age", qu)):
        a = S[k].copy(); a[hit] = rng.integers(0, hi, n, dtype=a.dtype); out[k] = a
    for k in ("f1", "f2", "wf1", "wf2"):
        if k in S:
            a = S[k].copy(); a[hit] = rng.integers(0, 2, n).astype(a.dtype); out[k] = a
    out["_hit"] = hit
    return out
