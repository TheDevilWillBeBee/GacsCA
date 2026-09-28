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
        bits = L.encode(s["addr"], s["age"], s["f1"], s["f2"], s.get("tracks"), s.get("wf1", 0), s.get("wf2", 0),
                        s.get("simage", 0), s.get("simaddr", 0))
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
                wf1=np.zeros((1, len(level1)), np.int8), wf2=np.zeros((1, len(level1)), np.int8),
                simage=np.array([[s.get("simage", 0) for s in level1]], np.int32),
                simaddr=np.array([[s.get("simaddr", 0) for s in level1]], np.int32))


def encode_state_info(state, layout: Layout, Q):
    """Batched dict-of-arrays -> primary Info, preserving every raw track copy.

    No majority repair is performed here: inconsistent copies are valid states
    of a simulated cell, and must not be silently normalized by its encoder.
    """
    if any(name in state and name.upper() not in layout.fields for name in ("simage2", "simaddr2")):
        raise ValueError("layout cannot encode the second control pair; refusing to discard state")
    B, ncell = state["addr"].shape
    info = np.zeros((B, ncell, Q), np.uint8)
    for name, (start, width) in layout.fields.items():
        value = np.asarray(state[name.lower()])
        if value.shape != (B, ncell) or np.any(value < 0) or np.any(value >= 1 << width):
            raise ValueError(f"invalid shape or out-of-range field {name}")
        info[..., layout.b0 + start:layout.b0 + start + width] = (
            value[..., None] >> np.arange(width)) & 1
    if layout.with_tracks:
        tracks = np.asarray(state["trk"])
        expected = (B, ncell, layout.tracks.NT, layout.tracks.R)
        if tracks.shape != expected or np.any((tracks != 0) & (tracks != 1)):
            raise ValueError("invalid raw track copies")
        info[..., layout.b0 + layout.track_base:layout.b0 + layout.K] = tracks.reshape(B, ncell, -1)
    return info.reshape(B, ncell * Q)


def decode_state_info(info, layout: Layout, Q):
    """Batched primary Info -> dict-of-arrays; caller chooses repair convention."""
    info = np.asarray(info)
    if info.ndim != 2 or info.shape[1] % Q:
        raise ValueError("Info must be a batch of whole colonies")
    B, length = info.shape
    bits = info.reshape(B, length // Q, Q)[..., layout.b0:layout.b0 + layout.K]
    state = {}
    for name, (start, width) in layout.fields.items():
        state[name.lower()] = (bits[..., start:start + width] * (1 << np.arange(width))).sum(-1).astype(np.int32)
    if layout.with_tracks:
        state["trk"] = bits[..., layout.track_base:].reshape(B, length // Q, layout.tracks.NT, layout.tracks.R).astype(np.uint8)
    return state
