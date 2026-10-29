#!/usr/bin/env python3
"""Build GR0's own ROM with an isolated repeated-XOR compiler workaround."""
from pathlib import Path
from dataclasses import asdict
import hashlib
import inspect
import json
import sys
import time
import textwrap
from types import MethodType
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT/'Report/proofs'))
import numpy as np
from gacsca import compiler, jobsched, machine, rule_g
import xor_multiplicity_scheduler as safe
import gray_scale_rule as proposed


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def allow_deliberate_match_wait(engine):
    """Retain all visits, permitting intended NOP pages before fixed MP.

    The active scheduler aborts after six idle pages even if the key is
    already complete and its fixed match pass has deliberately been placed
    later. Only that diagnostic is changed; the listing still needs the
    universal verifier.
    """
    source = textwrap.dedent(inspect.getsource(jobsched.Engine.run))
    old = 'if self.T - max(f.last_act for f in self.fronts) > 6 * PL:'
    new = ('if self.T - max(f.last_act for f in self.fronts) > 6 * PL '
           'and (self.post_match or self.keys_left):')
    assert source.count(old) == 1
    source = source.replace(old, new)
    namespace = dict(jobsched.__dict__)
    exec(compile(source, '<isolated deliberate fixed-match wait>', 'exec'), namespace)
    engine.run = MethodType(namespace['run'], engine)
    return hashlib.sha256(source.encode()).hexdigest()


def main():
    started = time.monotonic()
    out = ROOT/'figs/gray_counterexamples'
    p = proposed.parameters()
    _, comp = proposed.cached(p)
    layout = proposed.layout(p)
    report = proposed.metadata()
    report.update(params=asdict(p), driver_sha256=digest(__file__),
        proposal_sha256=digest(proposed.__file__), literal_module_sha256=digest(ROOT/'Report/proofs/gray_counterexamples/literal_maintenance.py'),
        base_rule_sha256=digest(rule_g.__file__), compiler_sha256=digest(compiler.__file__),
        scheduler_sha256=digest(jobsched.__file__), isolated_scheduler_sha256=digest(safe.__file__),
        active_rule_modified=False, global_reliability_established=False)
    engine, source_digest = safe.engine(p, comp, layout, MP=p.MP, max_pages=p.NP,
                                        drain_ticks=300)
    report['isolated_scheduler_generated_sha256'] = source_digest
    report['isolated_match_wait_source_sha256'] = allow_deliberate_match_wait(engine)
    print(json.dumps(dict(started=True,Q=p.Q,U=p.U,gates=len(comp.gates),width=proposed.width(p),MP=p.MP)), flush=True)
    try:
        engine.run()
        usage = engine.usage()
        report['usage'] = usage
        assert usage['NPe'] <= p.NPe and usage['NP'] <= p.NP, usage
        mismatches = jobsched.replay(p, engine, seed=0)
        report.update(random_replay_vectors=64, random_replay_mismatches=mismatches)
        assert mismatches == 0, mismatches
        programme = compiler.Program(p, layout)
        for _, page, _, front, cell, op, kind, a, b, dest, note in engine.prog.listing:
            programme.put(page+(front<<p.logNP), cell, op, kind, a, b, dest, note)
        candidate = machine.Candidate(p, programme.rom, layout)
        asset = out/'GR0_program.npz'
        np.savez_compressed(asset, rom=candidate.rom, layout=layout)
        report.update(build_complete=True, candidate_sha256=candidate.digest(),
            rom_sha256=hashlib.sha256(candidate.rom.tobytes()).hexdigest(),
            layout_sha256=hashlib.sha256(layout.tobytes()).hexdigest(),
            asset_sha256=digest(asset), instructions=len(engine.prog.listing))
    except (compiler.CompileError, AssertionError) as error:
        report.update(build_complete=False, scheduler_error=str(error), exception_type=type(error).__name__)
    listing = out/'GR0_program_listing.json'
    listing.write_text(json.dumps(engine.prog.listing,separators=(',',':'))+'\n')
    report.update(listing_sha256=digest(listing), stats=engine.summary(), elapsed_seconds=time.monotonic()-started)
    (out/'GR0_program_build.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({key:report[key] for key in ('build_complete','usage','instructions','scheduler_error','elapsed_seconds') if key in report}),flush=True)


if __name__ == '__main__':
    main()
