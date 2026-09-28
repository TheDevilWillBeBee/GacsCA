"""Paired CPU counterexample/check for compressed interpreter cache initialization.

This changes only the initial encoding, not the automaton's transition rule.
The compressed schedule reads a previous-period AGE/ADDR cache and refreshes it
at the end. A canonical first-period encoding must supply that cache explicitly.
"""
import argparse
import hashlib
import json
from pathlib import Path
import time

import numpy as np

from gacsca.checkpoint import save_checkpoint
from gacsca.hierarchy import encode_state_info
from experiments.phase_size import archive_sources
from experiments.replay_third_link_completion import initial_top, decode_top
from experiments.third_link_checkpoint import build
from experiments.tower_checkpoint import fingerprint, mismatch_counts


def cached_initial(middle, raw):
    """Explicit initialized cache for this compressed, one-control-pair layer.

    Not a new transition, a universal initialization theorem, or an instruction
    to overwrite running states. Arbitrary-state tests still use arbitrary caches.
    """
    if middle.sched.ictx is None or middle.prog.nested_register_bits:
        raise ValueError("requires the compressed middle layer with one control pair")
    s = middle.np_engine().initial(raw["addr"].shape[0], info_bits=encode_state_info(raw, middle.L, middle.p.Q))
    for cache, source in (("simage", "age"), ("simaddr", "addr")):
        s[cache][:] = np.repeat(raw[source], middle.p.Q, axis=1)
    return s


def run(output, n=11, seed=1350):
    archive = output.with_name(output.name + "_sources.tar.gz")
    path = output.with_suffix(".npz")
    summary = output.with_suffix(".json")
    if any(p.exists() for p in (archive, path, summary)): raise FileExistsError(output)
    _, middle, top = build(3, n)
    raw = initial_top(top, n, seed)
    cold = middle.np_engine().initial(1, info_bits=encode_state_info(raw, middle.L, middle.p.Q))
    warm = cached_initial(middle, raw)
    state = {k:np.concatenate((cold[k], warm[k])) for k in cold}
    initial = {k:v.copy() for k,v in state.items()}
    op = next(o for o in top.prog.ops if o.kind == "BITOP")
    index = top.prog.ops_at(op.t0).index(op)
    phase = next(o.t0 for o in middle.prog.ops if o.kind == "IEVAL" and o.param == index)
    events = (phase - 1, phase, phase + 1, middle.p.U - 2, middle.p.U)
    snapshots = {}
    hashes = fingerprint()
    root = Path(__file__).resolve().parents[1]
    for name in (__file__, "experiments/third_link_checkpoint.py", "experiments/replay_third_link_completion.py",
                 "experiments/verify_third_link_checkpoint.py", "experiments/phase_size.py"):
        p = Path(name).resolve()
        hashes[str(p.relative_to(root))] = hashlib.sha256(p.read_bytes()).hexdigest()
    archive_sources(archive, hashes)
    started = time.monotonic()
    for step in range(1, middle.p.U + 1):
        state = middle.np_engine().step(state)
        if step in events:
            for k,v in state.items(): snapshots[f"phase{step}_" + k] = v.copy()
        if step % 2048 == 0:
            print(json.dumps(dict(step=step, target=middle.p.U, elapsed_seconds=time.monotonic()-started)), flush=True)
    expected = top.np_engine().step(raw)
    outcomes = []
    holder = (n // 2) * middle.p.Q + middle.sched.ictx.pos(op.dst, middle.T.R // 2)
    for b, name in enumerate(("cold_zero_cache", "initialized_input_cache")):
        actual = decode_top({k:v[b:b+1] for k,v in state.items()}, middle, top)
        mismatches = mismatch_counts(actual, expected)
        selected_age = int(snapshots[f"phase{phase}_simage"][b, holder])
        selected_addr = int(snapshots[f"phase{phase}_simaddr"][b, holder])
        active = top.prog.ops_at(selected_age)
        selected_kind = active[index].kind if len(active) > index else None
        outcomes.append(dict(initialization=name, top_mismatches=mismatches,
                             changed_top_track_indices=np.argwhere(actual["trk"] != expected["trk"]).tolist(),
                             evaluation_holder=holder, raw_simage=selected_age, raw_simaddr=selected_addr,
                             selected_opcode_index=index, selected_kind=selected_kind,
                             active_bitop=selected_kind == "BITOP" and op.lo <= selected_addr < op.hi))
    meta = dict(protocol="compressed-cache-bootstrap-paired-cpu", status="complete", n=n, seed=seed,
                steps=middle.p.U, phase=phase, elapsed_seconds=time.monotonic()-started,
                source_archive=str(archive), source_archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),
                fingerprints=hashes, outcomes=outcomes,
                scope="CPU-only paired initialization test; not physical hierarchy execution")
    arrays = dict(snapshots)
    arrays.update({"initial_" + k:v for k,v in initial.items()})
    arrays.update({"top_" + k:v for k,v in raw.items()})
    arrays.update({"expected_top_" + k:v for k,v in expected.items()})
    save_checkpoint(path, meta, arrays)
    meta["data_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    with summary.open("x") as f: json.dump(meta, f, indent=2)
    print(json.dumps(meta), flush=True)
    return meta


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--top-cells", type=int, default=11)
    p.add_argument("--seed", type=int, default=1350)
    args = p.parse_args()
    run(args.output, args.top_cells, args.seed)


if __name__ == "__main__": main()
