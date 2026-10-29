#!/usr/bin/env python3
"""SP5 verifier/build copy of build_sparse_program.py; distinct source and receipt pins."""
"""Build SP5's own ROM, entirely outside the active rule and manifest.

Successful scheduling and random replay are evidence of a compilable
proposal. The universal symbolic verifier is a separate required step.
No positive-noise reliability follows from this build.
"""
from dataclasses import asdict
import hashlib
import inspect
import json
from pathlib import Path
import sys
import time
from types import FunctionType

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import numpy as np
from gacsca import compiler, jobsched, machine
import proposed_sparse_liveness448 as proposed
import xor_multiplicity_scheduler as safe

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def traced_replay(p, engine):
    """Same replay, retaining the locations of its failed assertions."""
    source = inspect.getsource(jobsched.replay)
    source = source.replace('    bad = 0', '    bad = 0\n    failures = []')
    source = source.replace('                    bad += 1', "                    bad += 1\n                    failures.append(dict(stage='key', register=r, value=v))")
    source = source.replace('            bad += 1\n        if kind', "            bad += 1\n            failures.append(dict(stage='write', sequence=seq, page=page, cell=cell, front=j, kind=kind, note=note, value=vid))\n        if kind")
    source = source.replace('            bad += 1\n    return bad', "            bad += 1\n            failures.append(dict(stage='Hold', cell=cell, value=v))\n    return bad, failures")
    namespace = dict(jobsched.__dict__)
    exec(compile(source,'<exact replay with failure locations>', 'exec'), namespace)
    return namespace['replay'](p, engine, seed=0)


def main():
    started = time.monotonic()
    p = proposed.parameters()
    net, comp = proposed.cached(p)
    layout = proposed.layout(p)
    out = ROOT / "figs/robustness"
    result = dict(proposal="SP5", proposed_rule_change=True, active_G17_modified=False,
                  proposed_params=asdict(p), Q=p.Q, U=p.U, raw_width=proposed.width(p), radius=12,
                  proposed_netlist_sha256=comp.digest, gates=len(comp.gates),
                  driver_sha256=digest(Path(__file__)),
                  proposal_source_sha256=digest(Path(proposed.__file__)),
                  transport_checker_sha256=digest(ROOT / "Report/proofs/check_fast_mail_proposal.py"),
                  liveness_helper_sha256=digest(ROOT / 'Report/proofs/check_blank_neighbor_clock.py'),
                  quiet_majority_checker_sha256=digest(ROOT / 'Report/proofs/check_quiet_majority_proposal.py'),
                  fast_flag_checker_sha256=digest(ROOT / "Report/proofs/check_fast_flag_proposal.py"),
                  jobscheduler_sha256=digest(ROOT / "gacsca/jobsched.py"),
                  compiler_sha256=digest(ROOT / "gacsca/compiler.py"),
                  isolated_scheduler_helper_sha256=digest(Path(safe.__file__)),
                  global_reliability_established=False,
                  scope="own-ROM build and finite replay; physical self-simulation and reliability separate")
    print("Building SP5's own program with its rebuilt circuit and fixed MP.", flush=True)
    with proposed.compiler_input_map():
        engine, scheduler_source_hash = safe.engine(p, comp, layout, MP=p.MP, max_pages=128)
        result['isolated_scheduler_generated_source_sha256'] = scheduler_source_hash
        assert (engine.lo, engine.hi, engine.PL) == (p.lo, p.hi, p.PL)
        try:
            engine.run()
            usage = engine.usage()
            result['usage'] = usage
            assert usage["MP"] == p.MP
            assert usage["NPe"] <= p.NPe and usage["NP"] <= p.NP, usage
            mismatch_count, failures = traced_replay(p, engine)
            result.update(random_replay_vectors=64, random_replay_mismatches=mismatch_count,
                          replay_failures=failures)
            attempt = out / 'SP5_attempt_listing.json'
            attempt.write_text(json.dumps(engine.prog.listing,separators=(',',':'))+'\n')
            result['attempt_listing_sha256'] = digest(attempt)
            assert mismatch_count == 0, f'abstract replay has {mismatch_count} mismatches'
            program = compiler.Program(p, layout)
            for _, page, _, front, cell, op, kind, a, b, dest, note in engine.prog.listing:
                program.put(page + (front << p.logNP), cell, op, kind, a, b, dest, note)
            candidate = machine.Candidate(p, program.rom, layout)
            asset = out / "SP5_program.npz"
            np.savez_compressed(asset, rom=candidate.rom, layout=layout)
            listing = out / "SP5_program_listing.json"
            listing.write_text(json.dumps(engine.prog.listing, separators=(",", ":")) + "\n")
            profile = out / "SP5_capture_table.json"
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
            result.update(build_complete=False, scheduler_error=str(exc),
                          exception_type=type(exc).__name__, stats=engine.summary())
    result["elapsed_seconds"] = time.monotonic() - started
    (out / "SP5_program_build.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    main()
