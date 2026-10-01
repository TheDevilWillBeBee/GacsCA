"""Analytical ninth-DAG-layer site/packet reuse certificate; no new CA rule.

The executable spatial pilot currently stops after dependency layer eight.
This file checks whether its first space obstruction has a static two-epoch
layout. It does not claim that the required local reset has been implemented.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

from gacsca.fixed_rule import spatial_layer1 as spatial
from gacsca.fixed_rule import stream28_holder_program as program_module
from gacsca.fixed_rule.wordcode_and import LIT


def plan():
    program=program_module.compiled_description()
    rom=program_module.layout()
    first=spatial.layout(8,'earliest')
    depth=[0]*program.inputs
    ninth=[]
    for index,(opcode,a,b) in enumerate(program.operations):
        layer=1 if opcode==LIT else 1+max(depth[a],depth[b])
        depth.append(layer)
        if layer==9:ninth.append(index)

    fresh_capacity=spatial.Q-5-(rom.memory_count+len(first.gate_operations))
    assert fresh_capacity>0
    placement={program.inputs+index:address for index,address in
               zip(first.gate_operations,first.gate_addresses)}
    reused=[]
    for ordinal,index in enumerate(ninth):
        if ordinal<fresh_capacity:
            address=rom.memory_count+len(first.gate_operations)+ordinal
        else:
            address=rom.memory_count+ordinal-fresh_capacity
            reused.append(address)
        placement[program.inputs+index]=address
    reused=frozenset(reused)
    assert len(reused)==len(ninth)-fresh_capacity
    assert max(placement.values())<spatial.Q-5

    # All first-epoch packets are consumed by first.last_completion. A
    # second epoch can reuse any phase after that time, provided its own
    # trajectories use distinct phases. Keep old gate results until reset.
    reset=2*spatial.Q
    completion={program.inputs+index:tick for index,tick in
                zip(first.gate_operations,first.gate_completion)}
    routes=Counter(edge.source for edge in first.edges)
    phases=set()
    new_edges=[]
    preloaded=0
    for index in ninth:
        opcode,a,b=program.operations[index]
        if opcode==LIT:
            completion[program.inputs+index]=1
            continue
        target=placement[program.inputs+index]
        arrivals=[]
        for slot,wire in enumerate((a,b)):
            if wire>=program.inputs and program.operations[wire-program.inputs][0]==LIT:
                preloaded+=1
                continue
            source=rom.wires[wire] if wire<program.inputs else placement[wire]
            assert source is not None
            distance=(target-source)%spatial.Q or spatial.Q
            ready=0 if wire<program.inputs else completion[wire]
            # The packet is emitted while the old site still owns its old
            # result. At a reused target it may only arrive after reset.
            launch=max(first.last_completion+1,ready+1,
                       reset-distance if target in reused else 0)
            while (source-launch)%spatial.Q in phases:launch+=1
            assert launch<reset,('old result overwritten before launch',index,slot)
            arrival=launch+distance
            assert target not in reused or arrival>=reset
            phase=(source-launch)%spatial.Q
            assert phase not in phases
            phases.add(phase)
            routes[source]+=1
            new_edges.append((source,target,slot,launch,arrival,phase,
                              wire,program.inputs+index))
            arrivals.append(arrival)
        completion[program.inputs+index]=max(arrivals,default=0)+1

    assert first.last_arrival<min(edge[3] for edge in new_edges)
    assert len(phases)==len(new_edges)
    assert max(routes.values())<=spatial.ROUTE_SLOTS
    assert max(completion[program.inputs+index] for index in ninth)<spatial.PERIOD
    assert all(0<=edge[0]<spatial.Q and 0<=edge[1]<spatial.Q for edge in new_edges)
    summary=dict(description_sha256=program.digest(),Q=spatial.Q,
                fixed_first_epoch_rule_width_bits=spatial.WIDTH,
                first_epoch_gates=len(first.gate_operations),
                first_epoch_last_completion=first.last_completion,
                ninth_layer_gates=len(ninth),fresh_gate_sites=fresh_capacity,
                reused_gate_sites=len(reused),reset_tick=reset,
                ninth_layer_packets=len(new_edges),
                ninth_layer_local_constant_operands=preloaded,
                first_ninth_launch=min(edge[3] for edge in new_edges),
                last_ninth_launch=max(edge[3] for edge in new_edges),
                first_ninth_arrival=min(edge[4] for edge in new_edges),
                last_ninth_arrival=max(edge[4] for edge in new_edges),
                ninth_layer_last_completion=max(completion[program.inputs+index]
                                                for index in ninth),
                max_routes_per_source=max(routes.values()),
                distinct_second_epoch_phases=len(phases),
                limitation='Analytical schedule certificate only. The local '
                           'reset is tested separately in measure_spatial_epoch; '
                           'the integrated own-rule closure and complete '
                           'macrostep remain absent.')
    return summary,first,tuple(ninth),placement,reused,tuple(new_edges)


def certificate():return plan()[0]


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    result=certificate()
    result['source_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    print(json.dumps(result,indent=2))
    if args.output:
        if args.output.exists():raise FileExistsError(args.output)
        args.output.write_text(json.dumps(result,indent=2)+'\n')
