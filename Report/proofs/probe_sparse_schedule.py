#!/usr/bin/env python3
"""Isolated scheduling probe for the proposed sparse circuit.

The active rule/compiler is unchanged. The probe uses the circuit's own
field-specific input map in this Python process only. A successful listing
is not an own-ROM candidate: its required constants must be incorporated
into a rebuilt circuit and verified again. Random replay is finite evidence.
"""
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import numpy as np
from gacsca import candidates, compiler, jobsched
from gacsca.netlist import Compiled
from check_fast_mail_proposal import concrete_sparse_net


def main():
    started = time.monotonic()
    out = ROOT / "figs/robustness"
    source_receipt = out / "fast_mail_proposal_certificate.json"
    proof = json.loads(source_receipt.read_text())
    table = proof["sparse_profile"]["profile"]
    p = candidates.load("G17").p
    net, _ = concrete_sparse_net(p, table)
    assert net.digest() == proof["sparse_profile"]["concrete_circuit_digest"]
    comp = Compiled(net)
    layout = np.array([row["address"] for row in table], dtype=np.int64)
    where = {(row["field"], row["bit"]): row for row in table}
    live = set(comp.outputs.values())
    for _, a, b in comp.gates:
        live.update((a, b))

    def sparse_locations(params, compiled, supplied_layout):
        assert params is p and compiled is comp and np.array_equal(supplied_layout, layout)
        codes = {name: code for code, name in enumerate(params.fam().source_names(params))}
        locations = {}
        for name, node in compiled.index.items():
            if name[0] != "x" or node not in live:
                continue
            _, offset, field, bit = name
            row = where[field, bit]
            code = codes["info", 0] if offset == 0 else codes["ln", row["offsets"].index(offset)]
            locations[node] = (row["address"], code)
        assert len(set(locations.values())) == len(locations)
        return locations

    result = dict(
        driver_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        source_receipt_sha256=hashlib.sha256(source_receipt.read_bytes()).hexdigest(),
        source_checker_sha256=proof["checker_sha256"],
        jobscheduler_sha256=hashlib.sha256((ROOT / "gacsca/jobsched.py").read_bytes()).hexdigest(),
        compiler_sha256=hashlib.sha256((ROOT / "gacsca/compiler.py").read_bytes()).hexdigest(),
        proposed_circuit_digest=comp.digest,
        active_rule_modified=False, complete_candidate=False,
        global_reliability_established=False,
        scope="isolated finite scheduling probe; no own ROM or all-time theorem")
    original = compiler.lane_locations
    compiler.lane_locations = sparse_locations
    try:
        print("Scheduling the isolated sparse circuit.", flush=True)
        engine = jobsched.Engine(p, comp, layout, MP=None, max_pages=128)
        try:
            engine.run()
            usage = engine.usage()
            mismatches = jobsched.replay(p, engine, seed=0)
            assert mismatches == 0
            listing = out / "sparse_schedule_listing.json"
            listing.write_text(json.dumps(engine.prog.listing, separators=(",", ":")) + "\n")
            result.update(schedule_complete=True, usage=usage,
                          listing_sha256=hashlib.sha256(listing.read_bytes()).hexdigest(),
                          instructions=len(engine.prog.listing), random_replay_vectors=64,
                          random_replay_mismatches=mismatches, stats=engine.summary(),
                          fits_current_NP=usage["NP"] <= p.NP,
                          fits_current_NPe=usage["NPe"] <= p.NPe,
                          same_current_MP=usage["MP"] == p.MP)
        except compiler.CompileError as exc:
            result.update(schedule_complete=False, scheduler_error=str(exc), stats=engine.summary())
    finally:
        compiler.lane_locations = original
    result["elapsed_seconds"] = time.monotonic() - started
    destination = out / "sparse_schedule_probe.json"
    destination.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
