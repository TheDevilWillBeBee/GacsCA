"""Audit every literal tick with the complete native full-state transition."""
import argparse
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import time
from gacsca.fixed_rule import signal_rule as r,signal_native as native
from gacsca.fixed_rule.signal_world import SignalWorld


def audit(source,output):
    source,output=Path(source),Path(output)
    if output.exists():raise FileExistsError('preserve prior evidence')
    start=time.monotonic();x=json.loads(source.read_text());root=Path(__file__).resolve().parents[2]
    for name,digest in x['source_sha256'].items():assert hashlib.sha256((root/name).read_bytes()).hexdigest()==digest,name
    assert x['identity']==json.loads(json.dumps(r.identity()))
    lib=native.library();assert hashlib.sha256(Path(lib._name).read_bytes()).hexdigest()==x['binary_sha256']
    checks=0;literal=0;quiet=0
    for name,case in x['records'].items():
        first=case['frames'][0];world=SignalWorld(dict(first['states']),data=dict(case['data']),age=first['age'])
        def verify_literal():
            nonlocal checks,literal
            support={((p+j)%r.Q) for p in world.states for j in range(-5,6)}|set(world.data)|{r.Q//2}
            expected={p:native.local_step(tuple(world.record(p+j) for j in range(-5,6)),lib) for p in support}
            world.step();checks+=len(support);literal+=1
            assert set(world.states).issubset(support)
            for p,out in expected.items():assert world.record(p)==out,(name,world.time,p)
        for frame in case['frames'][1:]:
            if frame['label']=='before_Wf_window':
                # Additional complete-kernel probes at both sides of the active
                # to rest boundary. The interval guard and fixed-point proof
                # cover all unsampled times; these probes are not that proof.
                support={((p+j)%r.Q) for p in world.states for j in range(-5,6)}|set(world.data)|{r.Q//2}
                for age in (world.age,80*r.Q-1,80*r.Q,96*r.Q-2):
                    for p in support:
                        cells=tuple(replace(world.record(p+j),age=age) for j in range(-5,6))
                        expected=replace(world.record(p),age=age+1)
                        assert native.local_step(cells,lib)==expected
                        checks+=1
                ticks=frame['tick']-world.time;world.skip_quiet(ticks);quiet+=ticks
            else:
                while world.time<frame['tick']:verify_literal()
            assert sorted(world.states.items())==[tuple(row) for row in frame['states']]
            assert world.age==frame['age'] and world.time==frame['tick'] and world.quiet_ticks==frame['quiet_ticks']
            assert world.evaluations==frame['evaluations']
            assert [sum(bool(v&(1<<b)) for v in world.states.values()) for b in range(4)]==frame['flags']
    result=dict(source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),cases=len(x['records']),source_files=len(x['source_sha256']),
                complete_native_local_checks=checks,literal_ticks=literal,guarded_quiet_ticks=quiet,
                elapsed_seconds=time.monotonic()-start,passed=True,
                limitation='locally initialized payload; no upper-flag computation/delivery, compiled self-simulation ROM, full trickle window or noise robustness')
    output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--input',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();audit(args.input,args.output)
