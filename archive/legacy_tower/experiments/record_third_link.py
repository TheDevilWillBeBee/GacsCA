"""CPU-only diagnostic sampling of an atomically replaced third-link checkpoint.

Samples the actual packed physical state, not just the reference. Does not alter
the running experiment. Missing early/intermediate checkpoints are not invented.
"""
import argparse
import hashlib
import json
from pathlib import Path
import time

import numpy as np

from gacsca.checkpoint import save_checkpoint, load_checkpoint
from experiments.third_link_checkpoint import build
from experiments.verify_third_link_checkpoint import decode_packed_info


def sample(path):
    with path.open("rb") as source:
        with np.load(source, allow_pickle=False) as data:
            meta = json.loads(str(data["_metadata"]))
            physical = data["physical"]
            reference = {k[7:]:data[k] for k in data.files if k.startswith("middle_")}
    outer, middle, _ = build(meta["identity"]["R"], meta["top_cells"])
    actual, _, disagreement = decode_packed_info(physical, outer, middle)
    counts = {k:int(np.count_nonzero(actual[k] != v)) for k,v in reference.items()}
    structure = int(np.count_nonzero((physical[..., 0] != np.arange(outer.p.L) % outer.p.Q) | (physical[..., 1] != 0)))
    snapshot = {"middle_" + k:v[0] for k,v in actual.items()}
    snapshot.update(period=np.array(meta["completed_periods"], np.int64),
                    physical_steps=np.array(meta["physical_steps"], np.int64),
                    decoded_mismatches=np.array(sum(counts.values()), np.int64),
                    physical_bad_structure=np.array(structure, np.int64),
                    info_copy_disagreements=np.array(disagreement, np.int64),
                    physical_flags_nonzero=np.array(np.count_nonzero(physical[..., 2]), np.int64))
    return meta, snapshot, middle.T.names


def run(args):
    if not 0 < args.interval <= 60 or args.idle_timeout < args.interval:
        raise ValueError("interval must be 0..60 seconds and no greater than idle-timeout")
    source_meta, first, names = sample(args.input)
    root = Path(__file__).resolve().parents[1]
    for name, expected in source_meta["identity"]["fingerprints"].items():
        if hashlib.sha256((root / name).read_bytes()).hexdigest() != expected:
            raise ValueError(f"source fingerprint mismatch: {name}")
    identity = dict(schema=1, source_identity=source_meta["identity"],
                    recorder_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                    decoder_sha256=hashlib.sha256(Path(__file__).with_name("verify_third_link_checkpoint.py").read_bytes()).hexdigest())
    path = args.output.with_suffix(".npz")
    if args.resume:
        meta, arrays = load_checkpoint(path, identity)
        history = {k:list(v) for k,v in arrays.items()}
    else:
        if path.exists(): raise FileExistsError("existing trace requires --resume")
        meta = dict(identity=identity, source=str(args.input), status="sampling", track_names=names,
                    first_available_period=int(first["period"]),
                    scope="irregular saved-checkpoint samples; actual CPU-decoded middle fields/raw copies; missing periods not reconstructed")
        history = {k:[] for k in first}
    last_new = time.monotonic()
    while True:
        period = int(first["period"])
        previous = int(history["period"][-1]) if history["period"] else -1
        if period < previous: raise ValueError("source checkpoint moved backward")
        if period > previous:
            for name, value in first.items(): history[name].append(value)
            meta["last_period"], meta["samples"] = period, len(history["period"])
            last_new = time.monotonic()
            meta["source_status"] = source_meta["status"]
            meta["status"] = "complete" if source_meta["status"] == "complete" else "failed" if source_meta["status"] == "failed" else "sampling"
            save_checkpoint(path, meta, {k:np.stack(v) for k,v in history.items()})
            print(json.dumps(dict(period=period, samples=meta["samples"], status=meta["status"],
                                  mismatches=int(first["decoded_mismatches"]))), flush=True)
        if source_meta["status"] in ("complete", "failed"): return meta
        if time.monotonic() - last_new >= args.idle_timeout:
            meta["status"] = "idle_timeout"
            save_checkpoint(path, meta, {k:np.stack(v) for k,v in history.items()})
            return meta
        time.sleep(args.interval)
        source_meta, first, _ = sample(args.input)
        if source_meta["identity"] != identity["source_identity"]:
            raise ValueError("source identity changed during recording")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("input", type=Path)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--interval", type=float, default=30)
    p.add_argument("--idle-timeout", type=float, default=600)
    p.add_argument("--resume", action="store_true")
    run(p.parse_args())


if __name__ == "__main__":
    main()
