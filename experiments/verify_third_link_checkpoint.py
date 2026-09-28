"""Independent CPU decoding and provenance audit of a live third-link checkpoint.

Pins one file descriptor, so atomic replacement by a running experiment is safe.
Does not rerun the trajectory or claim completion when only a prefix is saved.
"""
import argparse
import hashlib
import json
from pathlib import Path
import tarfile

import numpy as np

from experiments.third_link_checkpoint import build


def decode_packed_info(physical, outer, middle):
    R, NT, Q = outer.T.R, outer.T.NT, outer.p.Q
    # This experiment has two packed16 control words after Addr/Age/flags.
    assert outer.prog.nested_register_bits == 16 and outer.L.Us <= 65536
    words = (NT + 31) // 32
    assert physical.shape == (1, outer.p.L, 5 + R * words)
    assert outer.T["INFO"] == 0
    sites = np.arange(middle.p.L)[:, None] * Q + outer.L.b0 + np.arange(outer.L.K)
    copies = np.stack([(physical[:, (sites - (r - R // 2)) % outer.p.L, 5 + r * words] & 1).astype(np.uint8)
                       for r in range(R)])
    bits = (copies.sum(0) > R // 2).astype(np.uint8)
    actual = {}
    for name, (start, width) in outer.L.fields.items():
        actual[name.lower()] = (bits[..., start:start + width] * (1 << np.arange(width))).sum(-1).astype(np.int32)
    actual["trk"] = bits[..., outer.L.track_base:].reshape(1, middle.p.L, NT, R)
    return actual, int(bits.size), int(np.count_nonzero(copies != bits[None]))


def audit(path):
    root = Path(__file__).resolve().parents[1]
    with path.open("rb") as source:
        with np.load(source, allow_pickle=False) as data:
            meta = json.loads(str(data["_metadata"]))
            physical = data["physical"]
            expected = {k[7:]:data[k] for k in data.files if k.startswith("middle_")}
        source.seek(0)
        digest = hashlib.sha256()
        while block := source.read(1 << 20): digest.update(block)
    identity = meta["identity"]
    assert identity["experiment"] == "finite_third_link" and identity["full_registers_all_layers"]
    for name, h in identity["fingerprints"].items():
        assert hashlib.sha256((root / name).read_bytes()).hexdigest() == h, name
    archive = Path(meta["source_archive"])
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == meta["source_archive_sha256"]
    with tarfile.open(archive) as tar:
        for name, h in identity["fingerprints"].items():
            assert hashlib.sha256(tar.extractfile(name).read()).hexdigest() == h, name
    outer, middle, top = build(identity["R"], meta["top_cells"])
    assert meta["physical_steps"] == meta["completed_periods"] * outer.p.U
    assert [r["period"] for r in meta["log"]] == list(range(1, meta["completed_periods"] + 1))
    actual, bit_count, copy_disagreement = decode_packed_info(physical, outer, middle)
    mismatch = {k:int(np.count_nonzero(actual[k] != v)) for k,v in expected.items()}
    structure = int(np.count_nonzero((physical[..., 0] != np.arange(outer.p.L) % outer.p.Q) | (physical[..., 1] != 0)))
    logged_failures = sum(sum(r["middle_mismatches"].values()) + r["physical_bad_structure"] for r in meta["log"])
    top_failures = sum(sum(r["physical"].values()) + sum(r["direct"].values()) for r in meta["top_checks"])
    complete = meta["status"] == "complete"
    assert not complete or meta["completed_periods"] == identity["target_middle_transitions"]
    assert len(meta["top_checks"]) == meta["completed_periods"] // middle.p.U
    result = dict(input=str(path), input_sha256=digest.hexdigest(), completed_periods=meta["completed_periods"],
                  physical_steps=meta["physical_steps"], target_middle_transitions=identity["target_middle_transitions"],
                  run_complete=complete, encoded_bits_checked=bit_count, mismatches=mismatch,
                  physical_bad_structure=structure, encoded_info_copy_disagreements=copy_disagreement,
                  logged_failures=logged_failures, top_checks=len(meta["top_checks"]), top_failures=top_failures,
                  source_archive_verified=True, top_neighborhood_aliasing=meta["top_neighborhood_aliasing"],
                  script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  scope="independent packed CPU decoding of saved prefix versus stored NumPy reference; not a fresh trajectory replay")
    result["passed"] = not (structure or logged_failures or top_failures or any(mismatch.values()))
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("input", type=Path)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    if args.output.exists(): p.error("refusing to overwrite verification record")
    result = audit(args.input)
    with args.output.open("x") as stream: json.dump(result, stream, indent=2)
    print(json.dumps(result), flush=True)
    if not result["passed"]: raise SystemExit(1)


if __name__ == "__main__":
    main()
