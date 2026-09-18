"""Encoding a level-(k+1) configuration into level-k colonies and decoding it back."""
import numpy as np
from .microcode import Layout, Tracks
from .engine_np import repair, redistribute


def encode_info(level1, L: Layout, Q):
    """level1: list of dicts (addr, age, f1, f2[, tracks]) for ncol simulated cells ->
    (ncol*Q,) primary Info bits."""
    ncol = len(level1)
    info = np.zeros(ncol * Q, np.uint8)
    for i, s in enumerate(level1):
        bits = L.encode(s["addr"], s["age"], s["f1"], s["f2"], s.get("tracks"))
        info[i * Q + L.b0: i * Q + L.b0 + L.K] = bits
    return info


def decode_info(S, L: Layout, T: Tracks, Q):
    """-> list over batch of lists over colonies of decoded dicts (from repaired Info)."""
    V = repair(S["trk"])[:, :, T["INFO"]]
    B, Ltot = V.shape
    out = []
    for b in range(B):
        cols = []
        for i in range(Ltot // Q):
            cols.append(L.decode(V[b, i * Q + L.b0: i * Q + L.b0 + L.K]))
        out.append(cols)
    return out


def level1_to_arrays(level1):
    return dict(addr=np.array([[s["addr"] for s in level1]], np.int32),
                age=np.array([[s["age"] for s in level1]], np.int32),
                f1=np.array([[s["f1"] for s in level1]], np.int8),
                f2=np.array([[s["f2"] for s in level1]], np.int8),
                wf1=np.zeros((1, len(level1)), np.int8), wf2=np.zeros((1, len(level1)), np.int8))
