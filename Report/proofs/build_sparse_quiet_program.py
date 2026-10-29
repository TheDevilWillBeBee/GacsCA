#!/usr/bin/env python3
"""SP2 verifier/build copy of build_sparse_program.py; distinct source and receipt pins."""
"""Build SP2's own ROM, entirely outside the active rule and manifest.

Successful scheduling and random replay are evidence of a compilable
proposal. The universal symbolic verifier is a separate required step.
No positive-noise reliability follows from this build.
"""
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import numpy as np
from gacsca import compiler, jobsched, machine
import proposed_sparse_quiet as proposed

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    started = time.monotonic()
    p = proposed.parameters()
    net, comp = proposed.cached(p)
    layout = proposed.layout(p)
    out = ROOT / "figs/robustness"
    result = dict(proposal="SP2", proposed_rule_change=True, active_G17_modified=False,
                  proposed_params=asdict(p), Q=p.Q, U=p.U, raw_width=proposed.width(p), radius=12,
                  proposed_netlist_sha256=comp.digest, gates=len(comp.gates),
                  driver_sha256=digest(Path(__file__)),
                  proposal_source_sha256=digest(Path(proposed.__file__)),
                  transport_checker_sha256=digest(ROOT / "Report/proofs/check_fast_mail_proposal.py"),
                  fast_flag_checker_sha256=digest(ROOT / "Report/proofs/check_fast_flag_proposal.py"),
                  jobscheduler_sha256=digest(ROOT / "gacsca/jobsched.py"),
                  compiler_sha256=digest(ROOT / "gacsca/compiler.py"),
                  global_reliability_established=False,
                  scope="own-ROM build and finite replay; physical self-simulation and reliability separate")
    print("Building SP2's own program with its rebuilt circuit and fixed MP.", flush=True)
    with proposed.compiler_input_map():
        engine = jobsched.Engine(p, comp, layout, MP=p.MP, max_pages=128)
        assert (engine.lo, engine.hi, engine.PL) == (p.lo, p.hi, p.PL)
        try:
            engine.run()
            usage = engine.usage()
            assert usage["MP"] == p.MP
            assert usage["NPe"] <= p.NPe and usage["NP"] <= p.NP, usage
            assert jobsched.replay(p, engine, seed=0) == 0
            program = compiler.Program(p, layout)
            for _, page, _, front, cell, op, kind, a, b, dest, note in engine.prog.listing:
                program.put(page + (front << p.logNP), cell, op, kind, a, b, dest, note)
            candidate = machine.Candidate(p, program.rom, layout)
            asset = out / "SP2_program.npz"
            np.savez_compressed(asset, rom=candidate.rom, layout=layout)
            listing = out / "SP2_program_listing.json"
            listing.write_text(json.dumps(engine.prog.listing, separators=(",", ":")) + "\n")
            profile = out / "SP2_capture_table.json"
            profile.write_text(json.dumps(proposed.dependency_table(p), indent=2) + "\n")
            result.update(build_complete=True, usage=usage,
                          proposed_candidate_sha256=candidate.digest(),
                          proposed_rom_sha256=hashlib.sha256(candidate.rom.tobytes()).hexdigest(),
                          proposed_layout_sha256=hashlib.sha256(layout.tobytes()).hexdigest(),
                          asset_sha256=digest(asset), listing_sha256=digest(listing),
                          profile_sha256=digest(profile), rom_shape=list(candidate.rom.shape),
                          instructions=len(engine.prog.listing),
                          random_replay_vectors=64, random_replay_mismatches=0,
                          stats=engine.summary())
        except (compiler.CompileError, AssertionError) as exc:
            result.update(build_complete=False, scheduler_error=str(exc), stats=engine.summary())
    result["elapsed_seconds"] = time.monotonic() - started
    (out / "SP2_program_build.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    main()
