"""Check full 267-field WordCode description of the spatial local rule."""
import argparse
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import random
import resource
import time

from gacsca.fixed_rule import spatial_codec as codec
from gacsca.fixed_rule import spatial_description as description
from gacsca.fixed_rule import spatial_epoch as physical
from gacsca.fixed_rule import spatial_fanout_compiler as compiler
from gacsca.fixed_rule import stream28_holder_rule as raw
from experiments.fixed_rule.audit_spatial_full_dag import Witness,oracle
from experiments.fixed_rule.explore_spatial_topology import explore
from experiments.fixed_rule.schedule_spatial_phases import schedule


def check():
    started=time.perf_counter()
    program=description.build()
    assert program.inputs==3*codec.FIELDS
    assert len(program.outputs)==codec.FIELDS
    rng=random.Random(2026092842)
    words=tuple(rng.getrandbits(width) for _ in range(15)
                for _,width in raw.SCHEMA)
    compiled=compiler.compile_capacity()
    placement=explore()
    timing=schedule(True,'hold_left')
    witness=Witness(words,compiled,placement,timing,oracle(words))
    checks=0
    branch_counts=dict(right_mail=0,left_mail=0,output=0,gate=0,
                       switch=0,wrap=0,collision=0)

    def verify(before):
        nonlocal checks
        expected=physical.local_step(before)
        encoded=tuple(word for cell in before for word in codec.encode_cell(cell))
        actual=codec.decode_cell(program.evaluate(encoded))
        if actual!=expected:
            fields=[name for name in physical.Cell.__dataclass_fields__
                    if getattr(actual,name)!=getattr(expected,name)]
            raise AssertionError(('spatial own-description mismatch',checks,fields,
                                  [(name,getattr(actual,name),getattr(expected,name))
                                   for name in fields],before))
        if before[0].mail.valid and before[0].mail.target_gate_slot!=3:
            branch_counts['right_mail']+=1
        if before[2].mail.valid and before[2].mail.target_gate_slot==3:
            branch_counts['left_mail']+=1
        if before[1].kind==physical.OUTPUT:branch_counts['output']+=1
        if before[1].kind==physical.GATE:branch_counts['gate']+=1
        if expected.active_slot!=before[1].active_slot:branch_counts['switch']+=1
        if expected.age==0:branch_counts['wrap']+=1
        if expected.collision:branch_counts['collision']+=1
        checks+=1

    def at(site,t):
        return tuple(witness.cell_at(site+offset,t) for offset in (-1,0,1))

    for edge in (0,1,len(compiled.uses)//2,len(compiled.uses)-1,
                 len(timing.route_launch)-1):
        site=witness.source_sites[edge]
        verify(at(site,timing.route_launch[edge]-1))
        if edge<len(compiled.uses):
            use=compiled.uses[edge]
            target=placement.sites[(use.consumer_gate,use.consumer_copy)]
        else:
            wire=witness.output_wires[edge-len(compiled.uses)]
            target=timing.output_sinks[wire]
        verify(at(target,timing.route_arrival[edge]-1))
    for _ in range(250):
        edge=rng.randrange(len(timing.route_launch))
        if rng.randrange(2):
            site=witness.source_sites[edge]
            t=timing.route_launch[edge]-1
        else:
            if edge<len(compiled.uses):
                use=compiled.uses[edge]
                site=placement.sites[(use.consumer_gate,use.consumer_copy)]
            else:
                wire=witness.output_wires[edge-len(compiled.uses)]
                site=timing.output_sinks[wire]
            t=timing.route_arrival[edge]-1
        verify(at(site,t))
    for _ in range(100):
        site=rng.randrange(physical.Q)
        t=rng.randrange(timing.summary['latest_output_commit']+1)
        verify(at(site,t))
    for site,times in list(timing.site_switches.items())[:25]:
        for age in times:verify(at(site,age-1))
    for site in (0,17,2863,5025,8191):verify(at(site,physical.PERIOD-1))

    # Branch mixtures outside the healthy schedule, still within the fixed
    # finite alphabet, expose stale-ready, packet priority and collision bugs.
    for _ in range(150):
        site=rng.randrange(physical.Q)
        left,center,right=at(site,rng.randrange(physical.PERIOD-1))
        age=rng.randrange(physical.PERIOD)
        if rng.randrange(4)==0:age=physical.PERIOD-1
        center=replace(center,age=age,arg0=rng.getrandbits(64),
                       arg1=rng.getrandbits(64),ready=rng.randrange(4),
                       result=rng.getrandbits(64),done=rng.randrange(2),
                       source_value=rng.getrandbits(64),
                       collision=rng.randrange(2),mail=physical.EMPTY_PACKET)
        packet=physical.Packet(1,center.address,rng.randrange(2),
                               rng.randrange(3),rng.getrandbits(64))
        if rng.randrange(2):left=replace(left,mail=packet)
        if rng.randrange(2):right=replace(right,mail=replace(packet,target_gate_slot=3))
        verify((left,center,right))
    assert all(value>0 for value in branch_counts.values()),branch_counts
    return dict(passed=True,description_sha256=program.digest(),
                spatial_rule_source_sha256=hashlib.sha256(
                    Path(physical.__file__).read_bytes()).hexdigest(),
                spatial_codec_source_sha256=hashlib.sha256(
                    Path(codec.__file__).read_bytes()).hexdigest(),
                description_source_sha256=hashlib.sha256(
                    Path(description.__file__).read_bytes()).hexdigest(),
                input_words=program.inputs,output_words=len(program.outputs),
                wordcode_operations=len(program.operations),
                scalar_local_cases=checks,branches=branch_counts,
                max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                seconds=time.perf_counter()-started,
                limitation='Complete spatial-component F as explicit-input '
                           'WordCode; combined holder coupling/static-ROM '
                           'fixed point and upper macrostep remain open.')


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
