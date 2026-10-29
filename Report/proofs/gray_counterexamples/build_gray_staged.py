#!/usr/bin/env python3
"""Build GR1's own ROM; preserve every attempt and its exact builder."""
from pathlib import Path
from dataclasses import asdict
import argparse,hashlib,json,shutil,sys,time
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT)); sys.path.insert(0,str(ROOT/'Report/proofs'))
import numpy as np
from gacsca import compiler,jobsched,machine
import xor_multiplicity_scheduler as safe
import gray_staged_rule as proposed
from build_gray_scale import allow_deliberate_match_wait


def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--attempt',type=int,default=1)
    args=parser.parse_args(); started=time.monotonic(); out=ROOT/'figs/gray_counterexamples'
    stem=f'GR1_attempt{args.attempt:02d}'
    assert not (out/(stem+'_build.json')).exists(),'retain old attempt and choose a fresh number'
    p=proposed.parameters(); _,comp=proposed.cached(p); layout=proposed.layout(p)
    report=proposed.metadata(); report.update(params=asdict(p),attempt=args.attempt,
        driver_sha256=digest(__file__),proposal_sha256=digest(proposed.__file__),
        transport_primitive_sha256=digest(ROOT/'Report/proofs/gray_counterexamples/gray_staged_transport.py'),
        active_rule_sha256=digest(ROOT/'gacsca/rule_g.py'),
        active_maintenance_sha256=digest(ROOT/'gacsca/maintenance.py'),
        compiler_sha256=digest(compiler.__file__),scheduler_sha256=digest(jobsched.__file__),
        isolated_scheduler_sha256=digest(safe.__file__),
        match_wait_helper_sha256=digest(ROOT/'Report/proofs/gray_counterexamples/build_gray_scale.py'),
        active_rule_modified=False)
    engine,source_digest=safe.engine(p,comp,layout,MP=p.MP,max_pages=p.NP,drain_ticks=80)
    report['isolated_scheduler_generated_sha256']=source_digest
    report['isolated_match_wait_source_sha256']=allow_deliberate_match_wait(engine)
    print(json.dumps(dict(started=True,Q=p.Q,U=p.U,gates=len(comp.gates),width=proposed.width(p),
                          pass_ticks=p.PL,MP=p.MP,NP=p.NP)),flush=True)
    try:
        engine.run(); usage=engine.usage(); report['usage']=usage
        assert usage['NPe']<=p.NPe and usage['NP']<=p.NP,usage
        mismatches=jobsched.replay(p,engine,seed=20261013)
        report.update(random_replay_vectors=64,random_replay_mismatches=mismatches)
        assert not mismatches,mismatches
        programme=compiler.Program(p,layout)
        for _,page,_,front,cell,op,kind,a,b,dest,note in engine.prog.listing:
            programme.put(page+(front<<p.logNP),cell,op,kind,a,b,dest,note)
        candidate=machine.Candidate(p,programme.rom,layout)
        asset=out/'GR1_program.npz'
        np.savez_compressed(asset,rom=candidate.rom,layout=layout)
        report.update(build_complete=True,candidate_sha256=candidate.digest(),
            rom_sha256=hashlib.sha256(candidate.rom.tobytes()).hexdigest(),
            layout_sha256=hashlib.sha256(layout.tobytes()).hexdigest(),asset_sha256=digest(asset),
            instructions=len(engine.prog.listing))
    except (compiler.CompileError,AssertionError) as error:
        report.update(build_complete=False,scheduler_error=str(error),exception_type=type(error).__name__)
    listing=out/(stem+'_listing.json')
    listing.write_text(json.dumps(engine.prog.listing,separators=(',',':'))+'\n')
    preserved=out/(stem+'_builder.py'); shutil.copyfile(__file__,preserved)
    report.update(listing_sha256=digest(listing),preserved_builder_filename=preserved.name,
        preserved_builder_sha256=digest(preserved),stats=engine.summary(),elapsed_seconds=time.monotonic()-started)
    (out/(stem+'_build.json')).write_text(json.dumps(report,indent=2)+'\n')
    if report['build_complete']:
        shutil.copyfile(listing,out/'GR1_program_listing.json')
        (out/'GR1_program_build.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ('build_complete','usage','instructions','scheduler_error','elapsed_seconds') if k in report}),flush=True)


if __name__=='__main__':
    main()
