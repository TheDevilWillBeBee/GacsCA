"""Separate decoded, active-track, unused-Info and packed-padding recovery.

Static analysis works on archived checkpoints. An optional one-step reset probe
requires every original source/binary hash to match; it never overwrites or
silently resumes an archived trajectory under a different implementation.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import torch

from gacsca.build import make_system
from gacsca.params import Variant


def differences(state, system):
    """Compare each scenario with its same-time clean control, counting raw copies."""
    T, layout = system.T, system.L
    nw = (T.NT + 31) // 32
    track_base = state.shape[-1] - T.R * nw
    if track_base not in (4, 5):
        raise ValueError("unknown packed state layout")
    address = np.arange(state.shape[1]) % system.p.Q
    payload = (address >= layout.b0) & (address < layout.b0 + layout.K)
    signal = (address == 3) | (address == system.p.Q - 3)
    rows = []
    for batch in range(state.shape[0]):
        xor = state[batch] ^ state[0]
        tracks, padding = {}, 0
        for t in range(nw * 32):
            count = sum(int(np.count_nonzero((xor[:, track_base + r * nw + t // 32] >> (t % 32)) & 1))
                        for r in range(T.R))
            if t < T.NT and count:
                tracks[T.names[t]] = count
            elif t >= T.NT:
                padding += count
        info = ((xor[:, track_base + (T.R // 2) * nw] >> T["INFO"]) & 1).astype(bool)
        rows.append(dict(header_word_mismatches=np.count_nonzero(xor[:, :track_base], axis=0).tolist(),
                         active_track_copy_bit_mismatches=tracks,
                         inactive_packed_padding_bit_mismatches=padding,
                         primary_info_payload_mismatches=int(np.count_nonzero(info & payload)),
                         primary_info_signal_mismatches=int(np.count_nonzero(info & signal)),
                         primary_info_unused_positions=np.flatnonzero(info & ~payload & ~signal).tolist()))
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checkpoint", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--reset-probe", action="store_true")
    args = parser.parse_args()
    if args.output.exists():
        parser.error("refusing to overwrite analysis")
    with np.load(args.checkpoint, allow_pickle=False) as data:
        meta = json.loads(str(data["_metadata"]))
        state = data["physical"].copy()
    ident = meta["identity"]
    if ident["protocol"] != "gray-physical-transients" or meta["status"] != "complete":
        parser.error("expected a completed Gray physical-fault run")
    variant = Variant(**ident.get("variant", {}))
    system = make_system(Q=ident["Q"], U=ident["U"], ncol=ident["ncol"],
                         R=5, D=1, Qs=16, Us=2048, schedule="gray", variant=variant)
    if system.L.K != ident["encoded_bits"]:
        parser.error("encoding changed")
    result = dict(checkpoint=str(args.checkpoint), checkpoint_sha256=hashlib.sha256(args.checkpoint.read_bytes()).hexdigest(),
                  variant=variant.flag2_healthy_erase, steps=meta["steps"],
                  analysis_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  boundary=differences(state, system), after_reset=None)
    if args.reset_probe:
        root = Path(__file__).resolve().parents[1]
        for name, expected in ident["fingerprints"].items():
            path = root / name
            if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
                parser.error(f"reset probe requires exact original source/binary: {name}")
        if not np.all(state[..., 1] == 0):
            parser.error("reset probe requires all physical clocks at stage-one start")
        gpu = system.gpu_engine()
        packed = torch.from_numpy(state).cuda()
        reset = gpu.step(packed, torch.empty_like(packed), meta["steps"] + 1).cpu().numpy()
        result["after_reset"] = differences(reset, system)
        result["reset_probe_fingerprints"] = ident["fingerprints"]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
