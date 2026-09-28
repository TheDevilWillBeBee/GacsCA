"""Audit repair of a faulty middle holder using preserved physical boundaries."""
import argparse
import hashlib
import json
from pathlib import Path
import tarfile

import numpy as np

from gacsca.engine_np import repair
from experiments.third_link_checkpoint import build
from experiments.verify_third_link_checkpoint import decode_packed_info


def read(path):
    with np.load(path, allow_pickle=False) as data:
        meta = json.loads(str(data["_metadata"]))
        arrays = {k:data[k] for k in data.files if k != "_metadata"}
    root = Path(__file__).resolve().parents[1]
    archive = Path(meta["source_archive"])
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == meta["source_archive_sha256"]
    with tarfile.open(archive) as tar:
        for name, expected in meta["identity"]["fingerprints"].items():
            assert hashlib.sha256((root / name).read_bytes()).hexdigest() == expected, name
            assert hashlib.sha256(tar.extractfile(name).read()).hexdigest() == expected, name
    return meta, arrays


def analyze(first_path, final_path):
    a, first = read(first_path)
    b, final = read(final_path)
    assert a["status"] == b["status"] == "complete"
    assert a["identity"]["periods"] == 1 and b["identity"]["periods"] == 2
    assert {k:v for k,v in a["identity"].items() if k != "periods"} == {k:v for k,v in b["identity"].items() if k != "periods"}
    assert a["commits"][0] == b["commits"][0]
    outer, middle, _ = build(a["identity"]["R"], a["identity"]["top_cells"])
    def decode(arrays):
        rows = [decode_packed_info(arrays["physical"][i:i+1], outer, middle)[0]
                for i in range(len(a["identity"]["labels"]))]
        decoded = {k:np.concatenate([r[k] for r in rows]) for k in rows[0]}
        for k,v in decoded.items(): np.testing.assert_array_equal(v, arrays["previous_" + k], err_msg=f"stored.{k}")
        return decoded
    damaged, recovered = decode(first), decode(final)
    ground1 = {k[7:]:v for k,v in first.items() if k.startswith("ground_")}
    ground2 = {k[7:]:v for k,v in final.items() if k.startswith("ground_")}
    diff = damaged["trk"] != ground1["trk"]
    repaired_diff = repair(damaged["trk"]) != repair(ground1["trk"])
    raw_controls = {k:int(np.count_nonzero(damaged[k] != v)) for k,v in ground1.items() if k != "trk"}
    assert not any(raw_controls.values()) and not repaired_diff.any()
    fresh_next = middle.np_engine().step(damaged)
    for k,v in fresh_next.items():
        np.testing.assert_array_equal(v, recovered[k], err_msg=f"physical second period.{k}")
        np.testing.assert_array_equal(v, np.broadcast_to(ground2[k], v.shape), err_msg=f"clean second period.{k}")
    rows = []
    for i,label in enumerate(a["identity"]["labels"]):
        wrong_tracks = np.count_nonzero(diff[i], axis=(0, 2))
        rows.append(dict(**label, damaged_middle_holders=np.flatnonzero(diff[i].any(axis=(1, 2))).tolist(),
                         raw_track_copy_errors=int(diff[i].sum()),
                         raw_primary_errors=int(diff[i, :, :, middle.T.R // 2].sum()),
                         repaired_track_bit_errors=int(repaired_diff[i].sum()),
                         tracks={middle.T.names[t]:int(n) for t,n in enumerate(wrong_tracks) if n}))
    assert sum(bool(r["damaged_middle_holders"]) for r in rows) == 8
    assert all(len(r["damaged_middle_holders"]) <= 1 for r in rows)
    return dict(first=str(first_path), first_sha256=hashlib.sha256(first_path.read_bytes()).hexdigest(),
                final=str(final_path), final_sha256=hashlib.sha256(final_path.read_bytes()).hexdigest(),
                first_commit_reproduced=True, independently_decoded_both_boundaries=True,
                raw_control_mismatches=raw_controls, rows=rows,
                fresh_middle_transition_matches_physical_and_clean=True, passed=True,
                script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                scope="eight single-holder middle-track faults repaired by the represented threefold majority; sampled state at middle ages 385 to 386, not a depth-scaling theorem")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("first", type=Path)
    p.add_argument("final", type=Path)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    if args.output.exists(): p.error("refusing to overwrite analysis")
    result = analyze(args.first, args.final)
    with args.output.open("x") as f: json.dump(result, f, indent=2)
    print(json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
