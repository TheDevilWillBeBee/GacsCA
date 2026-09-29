"""Certify the complete explicit-input combined-rule WordCode on local steps.

The fixture exercises real spatial packet and gate states and coherent holder
replicas. It does not assert that an address-projected static ROM is closed.
"""
import argparse
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import random
import resource
import time

from gacsca.fixed_rule import spatial_epoch
from gacsca.fixed_rule import stream28_holder_rule as holder
from gacsca.fixed_rule import stream28_spatial_description as description
from gacsca.fixed_rule import stream28_spatial_optimized as optimized
from gacsca.fixed_rule import stream28_spatial_overlay as physical
from experiments.fixed_rule.audit_stream28_spatial_overlay import Fixture


def check():
    started=time.perf_counter()
    fixture=Fixture()
    program=description.build()
    optimized_program=optimized.build()
    assert program.inputs==15*physical.FIELDS
    assert len(program.outputs)==physical.FIELDS
    assert (optimized_program.inputs,len(optimized_program.outputs))==(
        program.inputs,len(program.outputs))
    rng=random.Random(2026092843)
    count=0
    branches=dict(capture=0,running=0,hold=0,info=0,wrap=0,
                  clear=0,mail=0,typed=0)

    def verify(site,age,t,capture=False,mutate=None):
        nonlocal count
        before=fixture.neighborhood(site,age,t,capture)
        if mutate is not None:before=mutate(before)
        expected=physical.encode_cell(physical.local_step(before))
        input_words=tuple(word for row in before for word in
                          physical.encode_cell(row))
        actual=program.evaluate(input_words)
        if actual!=expected:
            mismatches=[(i,a,e) for i,(a,e) in enumerate(zip(actual,expected))
                        if a!=e]
            raise AssertionError(('combined own-description mismatch',
                                  site,age,t,count,mismatches[:10]))
        simplified=optimized_program.evaluate(input_words)
        if simplified!=expected:
            mismatches=[(i,a,e) for i,(a,e) in enumerate(zip(simplified,expected))
                        if a!=e]
            raise AssertionError(('optimized combined description mismatch',
                                  site,age,t,count,mismatches[:10]))
        assert physical.decode_cell(actual)==physical.local_step(before)
        branches['capture']+=int(age==physical.CAPTURE_AGE)
        branches['running']+=int(physical.RUN_START<=age<physical.RUN_STOP)
        branches['hold']+=int(before[7].evaluator.kind==spatial_epoch.OUTPUT
                              and physical.RUN_START<=age<physical.RUN_STOP)
        branches['info']+=int(age==holder.U-1)
        branches['wrap']+=int((age+1)%holder.U==0)
        branches['clear']+=int(before[7].holder.f1!=0)
        branches['mail']+=int(any(row.evaluator.mail.valid for row in before))
        count+=1

    source_sites=list(fixture.sources)
    for site in (source_sites[0],source_sites[len(source_sites)//2],
                 source_sites[-1]):
        verify(site,physical.CAPTURE_AGE,0,True)
    for _ in range(30):
        verify(rng.choice(source_sites),physical.CAPTURE_AGE,0,True)

    for site,(wire,arrival) in fixture.outputs.items():
        for offset in range(-2,3):
            if rng.randrange(4)==0:
                verify((site-offset)%holder.Q,
                       physical.RUN_START+arrival-1,arrival-1)
    for field in (0,len(fixture.program.outputs)//2,
                  len(fixture.program.outputs)-1):
        site=fixture.layout.info[field]
        verify(site,holder.U-1,
               fixture.timing.summary['latest_output_commit'])

    def mark_flag(before):
        rows=list(before)
        rows[7]=replace(rows[7],holder=replace(rows[7].holder,f1=1))
        return tuple(rows)
    for site in (0,source_sites[0],next(iter(fixture.outputs))):
        verify(site,physical.RUN_START+100,100,mutate=mark_flag)

    def corrupt_holder_address(before):
        rows=list(before)
        rows[7]=replace(rows[7],holder=replace(
            rows[7].holder,address=(rows[7].holder.address+17)%holder.Q))
        return tuple(rows)
    verify(source_sites[0],physical.CAPTURE_AGE,0,True,
           mutate=corrupt_holder_address)

    for _ in range(75):
        site=rng.randrange(holder.Q)
        tick=rng.randrange(spatial_epoch.PERIOD)
        verify(site,physical.RUN_START+tick,tick)
    for age in (0,holder.RESET_AGES[4],physical.RUN_STOP,
                holder.U-2,holder.U-1):
        for site in (0,17,holder.Q-1):
            verify(site,age,0,age==physical.CAPTURE_AGE)

    # Typed raw controller state must not disappear into a healthy-only
    # fixture. A genuinely descriptive program also handles arbitrary
    # encoded replica/controller words in the local neighborhood.
    for _ in range(10):
        site=rng.randrange(holder.Q)
        age=rng.randrange(holder.U)
        tick=rng.randrange(spatial_epoch.PERIOD)
        def mutate(before):
            rows=[]
            for row in before:
                values={f's{slot}_{name}':rng.getrandbits(width)
                        for slot in range(5)
                        for name,width in holder.PROCEDURE}
                rows.append(replace(row,holder=replace(row.holder,**values)))
            return tuple(rows)
        verify(site,age,tick,mutate=mutate)
        branches['typed']+=1

    assert all(value>0 for value in branches.values()),branches
    return dict(passed=True,description_sha256=program.digest(),
                optimized_description_sha256=optimized_program.digest(),
                input_words=program.inputs,output_words=len(program.outputs),
                wordcode_operations=len(program.operations),
                optimized_wordcode_operations=len(optimized_program.operations),
                scalar_local_cases=count,branches=branches,
                max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                seconds=time.perf_counter()-started,
                physical_rule_source_sha256=hashlib.sha256(
                    Path(physical.__file__).read_bytes()).hexdigest(),
                descriptor_source_sha256=hashlib.sha256(
                    Path(description.__file__).read_bytes()).hexdigest(),
                limitation='Complete full-state F with all static fields as '
                           'explicit inputs, not an address-projected '
                           'self-ROM or complete lower work period.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    result=check()
    result['source_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    print(json.dumps(result,indent=2))
    if args.output:
        if args.output.exists():raise FileExistsError(args.output)
        args.output.write_text(json.dumps(result,indent=2)+'\n')
