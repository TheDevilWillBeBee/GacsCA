#!/usr/bin/env python3
"""Build isolated SP23; finite scheduling/replay only, no reliability claim."""
from dataclasses import asdict
import hashlib,json,time
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
import numpy as np
from gacsca import compiler,jobsched,machine
import proposed_sparse_distant960 as proposed
import xor_multiplicity_scheduler as safe


def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    started=time.monotonic();out=ROOT/'figs/robustness';p=proposed.parameters()
    n,comp=proposed.cached(p);layout=proposed.layout(p)
    receipt=dict(proposal='SP23',proposed_rule_change=True,active_G17_modified=False,SP22_modified=False,
        driver_sha256=digest(Path(__file__)),proposal_source_sha256=digest(Path(proposed.__file__)),
        parent_local_source_sha256=digest(Path(proposed.local.__file__)),
        parent_proposal_source_sha256=digest(Path(proposed.previous.__file__)),
        helpers_sha256=digest(ROOT/'gacsca/netlist.py'),jobscheduler_sha256=digest(ROOT/'gacsca/jobsched.py'),
        compiler_sha256=digest(ROOT/'gacsca/compiler.py'),isolated_scheduler_helper_sha256=digest(Path(safe.__file__)),
        proposed_params=asdict(p),Q=p.Q,U=p.U,width=proposed.width(p),radius=37,history_ranks=64,
        proposed_netlist_sha256=comp.digest,gates=len(comp.gates),
        actual_maintenance_source_sha256=hashlib.sha256(proposed.proposed_build()[1].encode()).hexdigest(),
        scheduler_drain_ticks=300,measured_only=True,universal_programme_verified=False,
        complete_encoded_simulation_or_higher_error_map_established=False,
        global_reliability_established=False,
        scope='isolated own-ROM scheduler build and64 replay vectors; universal programme/native/data/higher-error proofs separate')
    print(json.dumps(dict(Q=p.Q,U=p.U,W=proposed.width(p),gates=len(comp.gates),NPe=p.NPe,MP=p.MP,NP=p.NP)),flush=True)
    with proposed.compiler_input_map():
        engine,source_sha=safe.engine(p,comp,layout,MP=p.MP,max_pages=p.NP,drain_ticks=300)
        receipt['isolated_scheduler_generated_source_sha256']=source_sha
        try:
            engine.run();receipt['usage']=engine.usage()
            assert receipt['usage']['NPe']<=p.NPe and receipt['usage']['NP']<=p.NP,receipt['usage']
            assert receipt['usage']['MP']==p.MP
            mismatches=jobsched.replay(p,engine,seed=0)
            receipt.update(random_replay_vectors=64,random_replay_mismatches=mismatches)
            assert mismatches==0,mismatches
            program=compiler.Program(p,layout)
            for _,page,_,front,cell,op,kind,a,b,dest,note in engine.prog.listing:
                program.put(page+(front<<p.logNP),cell,op,kind,a,b,dest,note)
            candidate=machine.Candidate(p,program.rom,layout)
            np.savez_compressed(out/'SP23_program.npz',rom=candidate.rom,layout=layout)
            (out/'SP23_program_listing.json').write_text(json.dumps(engine.prog.listing,separators=(',',':'))+'\n')
            (out/'SP23_capture_table.json').write_text(json.dumps(proposed.dependency_table(p),indent=2)+'\n')
            receipt.update(build_complete=True,proposed_candidate_sha256=candidate.digest(),
                proposed_rom_sha256=hashlib.sha256(candidate.rom.tobytes()).hexdigest(),
                proposed_layout_sha256=hashlib.sha256(layout.tobytes()).hexdigest(),
                asset_sha256=digest(out/'SP23_program.npz'),listing_sha256=digest(out/'SP23_program_listing.json'),
                profile_sha256=digest(out/'SP23_capture_table.json'),rom_shape=list(candidate.rom.shape),
                instructions=len(engine.prog.listing))
        except (compiler.CompileError,AssertionError) as exc:
            receipt.update(build_complete=False,scheduler_error=str(exc),exception_type=type(exc).__name__)
        (out/'SP23_attempt_listing.json').write_text(json.dumps(engine.prog.listing,separators=(',',':'))+'\n')
        receipt['attempt_listing_sha256']=digest(out/'SP23_attempt_listing.json')
        receipt['stats']=engine.summary()
    receipt['elapsed_seconds']=time.monotonic()-started
    (out/'SP23_program_build.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:receipt[k] for k in ('build_complete','usage','scheduler_error','proposed_candidate_sha256','elapsed_seconds') if k in receipt}),flush=True)


if __name__=='__main__': main()
