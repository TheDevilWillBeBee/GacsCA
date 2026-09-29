"""Noise models (Gray Sec. 1: error set E with rate eps; noise distribution nu).

Masumori et al.: 'at each time step, a number of cells are destroyed according to the error
rate. The entire contents of the cell is replaced with a random bit string.'
"""
import numpy as np


def splitmix64(value):
    """Scalar bit-exact oracle for the GPU PRNG (arithmetic modulo 2^64)."""
    mask = (1 << 64) - 1
    value = (value + 0x9E3779B97F4A7C15) & mask
    value = ((value ^ (value >> 30)) * 0xBF58476D1CE4E5B9) & mask
    value = ((value ^ (value >> 27)) * 0x94D049BB133111EB) & mask
    return value ^ (value >> 31)


def cell_noise_word(seed, t, batch, site, version=2):
    """Counter-based GPU noise oracle. Version 1 only reproduces historical data.

    Version 2 accepts 64-bit times and non-overlapping 32-bit batch/site indices.
    Neither version is a cryptographic generator.
    """
    if not (0 <= seed < 1 << 64 and 0 <= t < 1 << 64 and
            0 <= batch < 1 << 32 and 0 <= site < 1 << 32):
        raise ValueError("counter outside its unsigned field width")
    if version == 1:
        counter = ((t << 40) ^ (batch << 28) ^ site) & ((1 << 64) - 1)
        return splitmix64(seed ^ splitmix64(counter))
    if version != 2:
        raise ValueError("unknown noise version")
    key = splitmix64(seed ^ 0xD2B74407B1CE6E93)
    key = splitmix64(key ^ t)
    return splitmix64(key ^ ((batch << 32) | site))


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
