"""Exercise actual U20 controller and stream branches against three executors.

The generated holder copies are coherent, while the static instruction and
controller words are deliberately chosen to enter branches that independent
random 64-bit fields almost never reach. All 421 raw outputs are compared.
"""
import argparse
from collections import Counter
import inspect
import json
from pathlib import Path
import sys
import time

from gacsca.fixed_rule import spatial_epoch8 as spatial
from gacsca.fixed_rule import stream28_dual_core20 as core
from gacsca.fixed_rule import stream28_dual_holder_rule20 as holder
from gacsca.fixed_rule import stream28_dual_pass20 as physical
from .differential import compare, AGES


ADDRESS=3000
SOURCE_DATA=0xE2D7C8B9563412F0


def coherent_case(age, kind, *, phase=core.FETCH, pc=0, index=0,
                  a=0, b=0, d=0, first=0, last=0, head=1,
                  direction=core.RIGHT, data=SOURCE_DATA):
    """One typed radius-seven neighborhood with consistent procedure copies."""
    static=dict(kind=kind,index=index,a=a,b=b,d=d,first=first,last=last)
    procedure=dict(data=data,head=head,phase=phase,pc=pc,direction=direction)
    rows=[]
    for offset in physical.NEIGHBORHOOD:
        address=(ADDRESS+offset)%physical.Q
        words=dict(address=address,age=age)
        for slot in range(7):
            for name,value in static.items():
                words[f'p{slot}_{name}']=value
        for slot in range(5):
            for name,value in procedure.items():
                words[f's{slot}_{name}']=value
        rows.append(physical.Cell(holder.Cell(**words),
                                  spatial.Cell(address=address,
                                               age=age%spatial.PERIOD)))
    return tuple(rows)


def route_case(offset):
    """Choose the old Age that really launches the requested stream route."""
    if not -7<=offset<=7 or offset==0:
        raise ValueError('nonzero route offset within radius seven required')
    index=offset+7
    wire=index*core.STREAM_FIELDS
    launch=(2+((ADDRESS-wire)%physical.Q) if offset<0 else
            2+((wire-ADDRESS)%physical.Q))
    age=launch-1
    words=coherent_case(age,core.MEM,head=0,
                        b=(1<<core.STREAM_FIELD_SHIFT)|(1<<index))
    return age,words


def _branch_lines():
    lines,start=inspect.getsourcelines(core.advance)
    fragments={
        'alu':'if kind in ALU_KINDS:',
        'send':'elif c.kind==SEND:',
        'loop':'elif c.kind==LOOP:',
        'load':'elif c.kind==LOAD:',
        'meta':'elif c.kind==META:',
        'literal':'elif c.kind==LIT:',
        'if_third':'elif c.kind==IF_THIRD:',
        'branch_third':'elif c.kind==BRANCH_THIRD:',
    }
    found={key:next((start+i for i,line in enumerate(lines)
                     if fragment in line),None)
           for key,fragment in fragments.items()}
    if any(value is None for value in found.values()):
        raise AssertionError('core.advance branch source changed')
    return found


def traced_compare(neighborhood,label):
    executed=set()
    def tracer(frame,event,arg):
        if frame.f_code is core.advance.__code__ and event=='line':
            executed.add(frame.f_lineno)
        return tracer
    previous=sys.gettrace()
    try:
        sys.settrace(tracer)
        compare(neighborhood,label)
    finally:
        sys.settrace(previous)
    return executed


def run():
    started=time.monotonic()
    branch_lines=_branch_lines()
    witnesses={}
    cases=0
    kinds={
        'alu':core.AND,
        'send':core.SEND,
        'loop':core.LOOP,
        'load':core.LOAD,
        'meta':core.META,
        'literal':core.LIT,
        'if_third':core.IF_THIRD,
        'branch_third':core.BRANCH_THIRD,
    }
    for name,kind in kinds.items():
        # The head entering from the left is FETCH at the selected PC.
        age=(core.RESET_AGES[2]+1000 if name=='if_third' else 1000)
        observed=traced_compare(coherent_case(age,kind,a=123,b=456,d=789),
                                f'opcode_{name}')
        if branch_lines[name] not in observed:
            raise AssertionError(('opcode branch not executed',name,sorted(observed)))
        witnesses[name]=dict(kind=kind,old_age=age,
                             source_line=branch_lines[name])
        cases+=1
    # PACK3 dispatches its packed instruction through the same advance path.
    packed=(core.LIT | (23<<4) | (71<<16) | (19<<28))
    pack_b=(1<<40)
    observed=traced_compare(coherent_case(1000,core.PACK3,a=packed,b=pack_b),
                            'packed_literal')
    if branch_lines['literal'] not in observed:
        raise AssertionError('packed literal branch not executed')
    witnesses['packed_literal']=dict(kind=core.PACK3,
                                     source_line=branch_lines['literal'])
    cases+=1
    route_values={}
    for offset in (*range(-7,0),*range(1,8)):
        age,neighborhood=route_case(offset)
        compare(neighborhood,f'route_offset_{offset}_age_{age}')
        result=physical.local_step(neighborhood).holder
        lane='rp' if offset<0 else 'lp'
        hops=getattr(result,f's2_{lane}_remaining')
        valid=getattr(result,f's2_{lane}_valid')
        if (valid,hops)!=(1,abs(offset)):
            raise AssertionError(('route branch not emitted',offset,age,valid,hops))
        route_values[str(offset)]=dict(old_age=age,valid=valid,hops=hops)
        cases+=1
    boundary_count=Counter()
    for age in AGES:
        compare(coherent_case(age,core.MEM,head=0),f'boundary_age_{age}')
        boundary_count[str(age)]+=1
        cases+=1
    return dict(cases=cases,raw_outputs_checked=cases*physical.FIELDS,
                executed_opcode_branches=witnesses,
                executed_route_offsets=route_values,
                coherent_boundary_ages=dict(boundary_count),
                duration_seconds=round(time.monotonic()-started,3),
                scope='all-word literal/WordCode/native parity; dynamic branches explicitly witnessed')


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    receipt=run()
    rendered=json.dumps(receipt,indent=2,sort_keys=True)+'\n'
    args.output.write_text(rendered)
    print(rendered)
