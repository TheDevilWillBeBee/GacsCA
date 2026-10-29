#!/usr/bin/env python3
"""Finite scheduling search, measured only; active rule remains unchanged.

Retain every attempted listing, parameter tuple and literal netlist digest.
The selected constants require a separate built proposal and universal proof.
"""
from dataclasses import asdict,replace
import hashlib,json
from pathlib import Path
import sys,time
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from gacsca import compiler
import proposed_sparse_backward_timing448 as interface
import xor_multiplicity_scheduler as safe


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out=ROOT/'figs/robustness'
    attempts=[]
    for NPe,MP in ((65,75),(65,77),(65,79),(66,77),(66,79),(67,79),(68,79)):
        started=time.monotonic()
        p=replace(interface.parameters(),NPe=NPe,MP=MP)
        p.check()
        n,comp=interface.cached(p)
        with interface.compiler_input_map():
            engine,source_hash=safe.engine(p,comp,interface.layout(p),MP=p.MP,max_pages=p.NP,drain_ticks=300)
            result=dict(NPe=NPe,MP=MP,parameters=asdict(p),netlist_sha256=comp.digest,
                isolated_scheduler_generated_source_sha256=source_hash,gates=len(comp.gates))
            try:
                engine.run()
                usage=engine.usage()
                result['usage']=usage
                assert usage['MP']==p.MP and usage['NPe']<=p.NPe and usage['NP']<=p.NP,usage
                result['fit']=True
            except (compiler.CompileError,AssertionError) as exc:
                result.update(fit=False,error=str(exc))
            result['stats']=engine.summary()
            listing=out/f'backward_schedule_search_{NPe}_{MP}_listing.json'
            listing.write_text(json.dumps(engine.prog.listing,separators=(',',':'))+'\n')
            result.update(listing_file=listing.name,listing_sha256=digest(listing),elapsed_seconds=time.monotonic()-started)
        attempts.append(result)
        receipt=dict(proposal='backward_program_schedule_search',proposed_rule_change=True,
            active_G17_modified=False,global_reliability_established=False,measured_only=True,
            driver_sha256=digest(Path(__file__)),interface_source_sha256=digest(Path(interface.__file__)),
            local_transition_source_sha256=digest(Path(interface.local.__file__)),
            isolated_scheduler_helper_sha256=digest(Path(safe.__file__)),attempts=attempts,
            selected_parameters=asdict(p) if result['fit'] else None,
            scope='finite isolated scheduling search; no replay, symbolic schedule, physical simulation or iid proof')
        (out/'backward_schedule_search.json').write_text(json.dumps(receipt,indent=2)+'\n')
        print(json.dumps({k:result[k] for k in ('NPe','MP','fit','usage','elapsed_seconds') if k in result}),flush=True)
        if result['fit']:
            break


if __name__=='__main__':
    main()
