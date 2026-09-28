"""Read-only CPU recheck of a completed whole-colony Gray checkpoint.

Decode directly from packed words without the GPU Info decoder; recompute the
upper transition from saved input and verify every encoded field/raw copy.
"""
import argparse
import hashlib
import json
from pathlib import Path
import tarfile

import numpy as np

from gacsca.build import make_tower


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("refusing to overwrite a verification record")
    root = Path(__file__).resolve().parents[1]
    # One descriptor pins the exact snapshot through decoding and hashing.
    with args.input.open("rb") as source:
        with np.load(source, allow_pickle=False) as z:
            meta = json.loads(str(z["_metadata"]))
            if meta["status"] != "complete" or meta["steps"] != meta["identity"]["U0"]:
                parser.error("need a completed lower period")
            physical = z["physical"]
            initial = {k[8:]:z[k] for k in z.files if k.startswith("initial_")}
            expected = {k[9:]:z[k] for k in z.files if k.startswith("expected_")}
        source.seek(0)
        digest = hashlib.sha256()
        while block := source.read(1 << 20):
            digest.update(block)
    for name, expected_hash in meta["identity"]["fingerprints"].items():
        assert hashlib.sha256((root / name).read_bytes()).hexdigest() == expected_hash, name
    archive = Path(meta["source_archive"])
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == meta["source_archive_sha256"]
    with tarfile.open(archive) as tar:
        for name, expected_hash in meta["identity"]["fingerprints"].items():
            assert hashlib.sha256(tar.extractfile(name).read()).hexdigest() == expected_hash, name
    lower, upper = make_tower(Q0=8192, U0=1048576, Q1=8192, U1=1048576,
                              ncol0=8192, R=5, D=1, schedule="gray")
    assert physical.shape == (1, lower.p.L, 20)
    fresh = upper.np_engine().step(initial)
    for name in expected:
        np.testing.assert_array_equal(expected[name], fresh[name], err_msg=f"reference.{name}")
    structure = 0
    for start in range(0, lower.p.L, 1 << 20):
        stop = min(start + (1 << 20), lower.p.L)
        structure += int(np.count_nonzero((physical[:, start:stop, 0] != np.arange(start, stop) % lower.p.Q) |
                                          (physical[:, start:stop, 1] != 0)))
    # Info is track zero; this backend has separate wide registers (base 5),
    # three uint32 words per copy, five independently held copies.
    sites = np.arange(upper.p.L)[:, None] * lower.p.Q + lower.L.b0 + np.arange(lower.L.K)
    copies = np.stack([(physical[:, (sites - (r - 2)) % lower.p.L, 5 + 3 * r] & 1).astype(np.uint8)
                       for r in range(5)])
    bits = (copies.sum(0) >= 3).astype(np.uint8)
    actual = {}
    for name, (start, width) in lower.L.fields.items():
        actual[name.lower()] = (bits[..., start:start + width] * (1 << np.arange(width))).sum(-1).astype(np.int32)
    actual["trk"] = bits[..., lower.L.track_base:].reshape(1, upper.p.L, upper.T.NT, 5)
    mismatch = {k:int(np.count_nonzero(actual[k] != expected[k])) for k in expected}
    result = dict(protocol="independent-packed-cpu-gray-check", input=str(args.input),
                  input_sha256=digest.hexdigest(), encoded_bits_checked=int(bits.size),
                  mismatches=mismatch, physical_bad_structure=structure,
                  encoded_info_copy_disagreements=int(np.count_nonzero(copies != bits[None])),
                  fresh_reference_checked=True, source_archive_verified=True,
                  script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  scope="one whole upper transition after one lower work period; no full upper period")
    result["passed"] = not structure and not any(mismatch.values())
    with args.output.open("x") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(json.dumps(result), flush=True)
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
