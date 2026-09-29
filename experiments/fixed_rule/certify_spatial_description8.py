"""Compare the fixed 8Q spatial rule and its full WordCode description."""
import argparse
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import random
import resource
import time

from gacsca.fixed_rule import spatial_codec8 as codec
from gacsca.fixed_rule import spatial_description8 as description
from gacsca.fixed_rule import spatial_epoch8 as physical
from gacsca.fixed_rule.wordcode_and import NAND,ADD,SHR,EQ,LT,LIT,AND


def check():
    started=time.perf_counter()
    rng=random.Random(2026092845)
    program=description.build()
    assert (program.inputs,len(program.outputs))==(
        3*codec.FIELDS,codec.FIELDS)
    cases=0
    branches=dict(left_mail=0,right_mail=0,late_latch=0,
                  switch=0,wrap=0,output=0,collision=0)

    def verify(rows):
        nonlocal cases
        expected=physical.local_step(rows)
        words=tuple(word for cell in rows for word in codec.encode_cell(cell))
        actual=codec.decode_cell(program.evaluate(words))
        if actual!=expected:
            diff=[(name,getattr(actual,name),getattr(expected,name))
                  for name in physical.Cell.__dataclass_fields__
                  if getattr(actual,name)!=getattr(expected,name)]
            raise AssertionError(('8Q own-F mismatch',cases,diff))
        left,center,right=rows
        branches['left_mail']+=int(left.mail.valid and
                                   left.mail.target_gate_slot!=3)
        branches['right_mail']+=int(right.mail.valid and
                                    right.mail.target_gate_slot==3)
        branches['late_latch']+=int(center.kind==physical.GATE and
                    any(route.valid and route.launch==expected.age and
                        route.target_gate_slot==3 and
                        center.gates[route.source_gate_slot].opcode in
                        physical.OUTPUT_BASE_OPCODE and
                        route.source_gate_slot!=center.active_slot
                        for route in center.routes))
        branches['switch']+=int(expected.active_slot!=center.active_slot)
        branches['wrap']+=int(expected.age==0)
        branches['output']+=int(center.kind==physical.OUTPUT)
        branches['collision']+=int(expected.collision)
        cases+=1

    marked=physical.GateSpec(1,physical.OUTPUT_OPCODE[NAND])
    route=physical.Route(1,2863,0,3,0,40654)
    center=physical.Cell(address=5000,age=40653,kind=physical.GATE,
                         active_slot=1,
                         gates=(marked,physical.GateSpec(1,AND),
                                physical.EMPTY_GATE),
                         routes=(route,)+
                                (physical.EMPTY_ROUTE,)*
                                (physical.ROUTE_SLOTS-1),
                         source_value=0x123456789abcdef0,done=0)
    verify((physical.Cell(),center,physical.Cell()))
    for age in (physical.PERIOD-1,0,16383,32767,50000):
        verify((physical.Cell(),replace(center,age=age),physical.Cell()))
    for _ in range(400):
        site=rng.randrange(physical.Q)
        age=rng.randrange(physical.PERIOD)
        kind=rng.randrange(4)
        active=rng.randrange(physical.GATE_SLOTS)
        gates=tuple(physical.GateSpec(1,rng.choice((NAND,ADD,SHR,EQ,LT,LIT,
                        AND,*physical.OUTPUT_BASE_OPCODE)),
                        rng.getrandbits(64),rng.randrange(1<<14),
                        rng.getrandbits(64),rng.getrandbits(64),
                        rng.randrange(4))
                    for _ in range(physical.GATE_SLOTS))
        switches=((age+1)%physical.PERIOD if active==0 and rng.randrange(4)==0 else
                  rng.randrange(physical.PERIOD),
                  (age+1)%physical.PERIOD if active==1 and rng.randrange(4)==0 else
                  rng.randrange(physical.PERIOD))
        routes=((physical.Route(1,rng.randrange(physical.Q),
                                rng.randrange(2),rng.randrange(4),
                                rng.randrange(3),(age+1)%physical.PERIOD),)+
                (physical.EMPTY_ROUTE,)*(physical.ROUTE_SLOTS-1))
        center=physical.Cell(address=site,age=age,kind=kind,
            active_slot=active,switch_ages=switches,gates=gates,
            routes=routes,source_value=rng.getrandbits(64),
            arg0=rng.getrandbits(64),arg1=rng.getrandbits(64),
            ready=rng.randrange(4),result=rng.getrandbits(64),
            done=rng.randrange(2),collision=rng.randrange(2))
        packet=physical.Packet(1,site,rng.randrange(2),
                               rng.randrange(3),rng.getrandbits(64))
        left=physical.Cell(mail=packet if rng.randrange(2) else
                           physical.EMPTY_PACKET)
        right=physical.Cell(mail=replace(packet,target_gate_slot=3)
                            if rng.randrange(2) else physical.EMPTY_PACKET)
        verify((left,center,right))
    assert all(branches.values()),branches
    return dict(passed=True,description_sha256=program.digest(),
                input_words=program.inputs,output_words=len(program.outputs),
                wordcode_operations=len(program.operations),
                scalar_local_cases=cases,branches=branches,
                max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                seconds=time.perf_counter()-started,
                physical_source_sha256=hashlib.sha256(
                    Path(physical.__file__).read_bytes()).hexdigest(),
                limitation='Complete 8Q spatial-component F with explicit '
                           'static inputs; combined own-ROM closure open.')


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
