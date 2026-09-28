"""Independent packed decoding of each nested-phase fault boundary.

Distinguishes restoration of the clean state, correct simulation of the damaged
state, redundant-track repair, and persistent unprotected control-field errors.
"""
import argparse
import hashlib
import json
from pathlib import Path
import tarfile

import numpy as np

from gacsca.engine_np import repair
from experiments.third_link_checkpoint import build
from experiments.verify_third_link_checkpoint import decode_packed_info
from experiments.third_link_faults import decoded_metrics
from experiments.replay_third_link_completion import initial_top, decode_top


def read(path):
    """Verify old/new run archives while keeping decoder/core semantics pinned.

    Only the experiment's runner may differ from the working tree. Its exact
    original bytes are still hash-verified in the archive; it is not executed
    by this auditor. This permits auditing the preserved failed schema-1 setup.
    """
    with np.load(path, allow_pickle=False) as data:
        meta = json.loads(str(data["_metadata"]))
        arrays = {k:data[k] for k in data.files if k != "_metadata"}
    root = Path(__file__).resolve().parents[1]
    archive = Path(meta["source_archive"])
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == meta["source_archive_sha256"]
    with tarfile.open(archive) as tar:
        for name, expected in meta["identity"]["fingerprints"].items():
            assert hashlib.sha256(tar.extractfile(name).read()).hexdigest() == expected, name
            if name != "experiments/nested_phase_faults.py":
                assert hashlib.sha256((root / name).read_bytes()).hexdigest() == expected, name
    return meta, arrays


def error_details(actual, ground, middle):
    diff = actual["trk"] != ground["trk"]
    voted = repair(actual["trk"]) != repair(ground["trk"])
    rows = []
    for b in range(actual["addr"].shape[0]):
        fields = {k:int(np.count_nonzero(actual[k][b] != v[0])) for k,v in ground.items() if k != "trk"}
        holders = diff[b].any(axis=(1, 2))
        for k,v in ground.items():
            if k != "trk": holders |= actual[k][b] != v[0]
        tracks = diff[b].sum(axis=(0, 2))
        rows.append(dict(fields=fields, damaged_holders=np.flatnonzero(holders).tolist(),
                         raw_track_copy_errors=int(diff[b].sum()),
                         repaired_track_errors=int(voted[b].sum()),
                         repaired_info_errors=int(voted[b, :, middle.T["INFO"]].sum()),
                         repaired_hold_errors=int(voted[b, :, middle.T["HOLD"]].sum()),
                         tracks={middle.T.names[i]:int(n) for i,n in enumerate(tracks) if n}))
    return rows


def analyze(prefix):
    final_path = prefix.with_suffix(".npz")
    final_meta, final_arrays = read(final_path)
    identity = final_meta["identity"]
    assert identity["protocol"] == "reference-prepared-nested-phase-physical-islands"
    assert final_meta["status"] == "complete"
    outer, middle, top = build(3, identity["top_cells"])
    initial = {k[8:]:v for k,v in final_arrays.items() if k.startswith("initial_")}
    B = len(identity["labels"])
    previous = {k:np.repeat(v, B, axis=0) for k,v in initial.items()}
    ground = {k:v.copy() for k,v in initial.items()}
    records = []
    hashes = {str(final_path):hashlib.sha256(final_path.read_bytes()).hexdigest()}
    for period in range(1, identity["periods"] + 1):
        path = prefix.with_name(prefix.name + f"_boundary{period}.npz")
        meta, arrays = read(path)
        assert meta["identity"] == identity and meta["steps"] == period * outer.p.U
        hashes[str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
        decoded_rows = [decode_packed_info(arrays["physical"][i:i+1], outer, middle) for i in range(B)]
        actual = {k:np.concatenate([row[0][k] for row in decoded_rows]) for k in decoded_rows[0][0]}
        ground = middle.np_engine().step(ground)
        conditional = middle.np_engine().step(previous)
        for k,v in actual.items():
            np.testing.assert_array_equal(v, arrays["previous_" + k], err_msg=f"period {period} decoded.{k}")
            np.testing.assert_array_equal(ground[k], arrays["ground_" + k], err_msg=f"period {period} ground.{k}")
            np.testing.assert_array_equal(initial[k], arrays["initial_" + k], err_msg=f"period {period} initial.{k}")
            np.testing.assert_array_equal(v[0], ground[k][0], err_msg=f"period {period} clean.{k}")
        observed = dict(period=period, middle_age=int(ground["age"][0, 0]),
                        ground=decoded_metrics(actual, ground, middle.T),
                        conditional_transition=decoded_metrics(actual, conditional, middle.T))
        assert observed == meta["commits"][-1] == final_meta["commits"][period - 1]
        packed = arrays["physical"]
        structure = np.count_nonzero((packed[..., 0] != np.arange(outer.p.L) % outer.p.Q) | (packed[..., 1] != 0), axis=1)
        assert structure.tolist() == meta["samples"][-1]["bad_structure"]
        top_check = {}
        if identity["spec"]["phase"] == "rollover" and observed["middle_age"] == 0:
            expected_top = top.np_engine().step(initial_top(top, identity["top_cells"], identity["initialization_seed"]))
            upper_rows = [decode_top({k:v[i:i+1] for k,v in actual.items()}, middle, top) for i in range(B)]
            errors = {k:[int(np.count_nonzero(row[k] != v)) for row in upper_rows] for k,v in expected_top.items()}
            top_check = dict(mismatches=errors, all_match=not any(sum(v) for v in errors.values()),
                             scope="fresh top microstep versus twice-decoded physical boundary; CPU-prepared prior middle prefix")
            if identity["schema"] >= 2: assert top_check["all_match"]
        records.append(dict(**observed, rows=error_details(actual, ground, middle), top_transition=top_check,
                            physical_bad_structure=structure.tolist(),
                            physical_flag1=meta["samples"][-1]["flag1"], physical_flag2=meta["samples"][-1]["flag2"],
                            physical_info_copy_disagreements=[row[2] for row in decoded_rows]))
        previous = actual
    for k,v in previous.items():
        np.testing.assert_array_equal(v, final_arrays["previous_" + k])
    np.testing.assert_array_equal(packed, final_arrays["physical"])
    holder = identity["spec"]["middle_holder"]
    first_clean = {k:v[:1] for k,v in initial.items()}
    first_clean = middle.np_engine().step(first_clean)
    selected = []
    if identity["spec"]["phase"] == "evaluation":
        age, addr = int(first_clean["simage"][0, holder]), int(first_clean["simaddr"][0, holder])
        active = top.prog.ops_at(age)
        index = identity["spec"]["opcode_index"]
        kind = active[index].kind if len(active) > index else None
        active_bitop = kind == "BITOP" and active[index].lo <= addr < active[index].hi
        selected = dict(simage=age, simaddr=addr, opcode_index=index, kind=kind,
                        active_bitop=active_bitop, destination_holder=holder,
                        middle_age=int(first_clean["age"][0, holder]))
        after = middle.np_engine().step(first_clean)
        old = int(repair(first_clean["trk"])[0, holder, middle.T["HOLD"]])
        new = int(repair(after["trk"])[0, holder, middle.T["HOLD"]])
        selected.update(hold_before=old, hold_after=new, value_changes=old != new)
        if identity["schema"] >= 2:
            assert active_bitop and old != new, "corrected setup must be non-vacuous"
    return dict(passed=True, independently_decoded_boundaries=len(records), identity=identity,
                input_sha256=hashes, records=records, selected_evaluation=selected,
                physical_elapsed_seconds=final_meta["elapsed_seconds"],
                active_evaluation_verified=bool(selected and selected["active_bitop"]),
                script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                scope="independent packed decoding and fresh per-boundary CPU transitions, not a physical prefix or asymptotic depth law")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("prefix", type=Path)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    if args.output.exists(): p.error("refusing to overwrite analysis")
    result = analyze(args.prefix)
    with args.output.open("x") as f: json.dump(result, f, indent=2)
    print(json.dumps(dict(passed=result["passed"], boundaries=result["independently_decoded_boundaries"],
                          errors=[r["ground"]["any_state_cells"] for r in result["records"]],
                          selected_evaluation=result["selected_evaluation"])), flush=True)


if __name__ == "__main__":
    main()
