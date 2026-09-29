"""Optimistic dependency-time bound for the greedy compact gate placement.

Every routed operand takes its rightward physical distance; every gate takes
one tick. The bound chooses the earliest of each producer's copies and omits
contention, phase conflicts, gate-site switches and the required Age buffer.
If it exceeds 4Q, this placement cannot be scheduled in the current window.
"""
import argparse
import hashlib
import json
from pathlib import Path

from gacsca.fixed_rule import spatial_codec,spatial_epoch
from gacsca.fixed_rule import stream28_holder_rule as holder
from gacsca.fixed_rule import stream28_compact_layout as layout_module
from gacsca.fixed_rule.wordcode_and import LIT
from experiments.fixed_rule.measure_stream28_spatial_capacity import (
    PROJECTED_OUTPUT_FIELDS,SPATIAL_DYNAMIC_FIELDS)
from experiments.fixed_rule.place_stream28_compact_gates import check as place


def bound(facts,positions,program,copies,period=spatial_epoch.PERIOD):
    layout=layout_module.build()
    stride=holder.FIELDS+spatial_codec.FIELDS
    static_sites={wire:facts['site_start']-len(layout.static_inputs)+rank
                  for rank,wire in enumerate(layout.static_inputs)}
    dynamic_rank={item:rank for rank,item in enumerate(layout.gathered)}

    def raw_site(wire):
        if wire in static_sites:return static_sites[wire]
        neighbor,field=divmod(wire,stride)
        if field<holder.FIELDS:
            assert field>=len(holder.STATIC)
            projected=field-len(holder.STATIC)
        else:
            field-=holder.FIELDS
            assert field in SPATIAL_DYNAMIC_FIELDS
            projected=len(holder.SCHEMA)-len(holder.STATIC)+\
                      SPATIAL_DYNAMIC_FIELDS.index(field)
        return 8+3*dynamic_rank[(neighbor,projected)]+1

    def routed(wire):
        return wire<program.inputs or program.operations[wire-program.inputs][0]!=LIT

    earliest=[]
    maximal_gate=(0,-1)
    for index,(opcode,a,b) in enumerate(program.operations):
        times=[]
        for copy in range(copies[index]):
            at=positions[(index,copy)][0]
            arrivals=[]
            for operand in (a,b) if opcode!=LIT else ():
                if not routed(operand):continue  # locally preloaded literal
                if operand<program.inputs:
                    source_times=((0,raw_site(operand)),)
                else:
                    source=operand-program.inputs
                    source_times=tuple((earliest[source][c],
                                        positions[(source,c)][0])
                                       for c in range(copies[source]))
                arrivals.append(min(t+((at-site)%spatial_epoch.Q or
                                       spatial_epoch.Q)
                                    for t,site in source_times))
            completion=max(arrivals,default=0)+1
            times.append(completion)
            if completion>maximal_gate[0]:maximal_gate=(completion,index)
        earliest.append(tuple(times))

    latest_output=0
    last_field=-1
    for projected_field,full_field in enumerate(PROJECTED_OUTPUT_FIELDS):
        wire=program.outputs[full_field]
        sink=layout.hold[projected_field]
        if wire<program.inputs:
            candidates=((0,raw_site(wire)),)
        else:
            index=wire-program.inputs
            candidates=tuple((earliest[index][copy],positions[(index,copy)][0])
                             for copy in range(copies[index]))
        commit=min(t+((site-sink)%spatial_epoch.Q or spatial_epoch.Q)
                   for t,site in candidates)
        if commit>latest_output:latest_output,last_field=commit,projected_field
    return dict(passed=True,description_sha256=program.digest(),
                physical_period=period,
                optimistic_latest_gate_completion=maximal_gate[0],
                latest_gate_index=maximal_gate[1],
                optimistic_latest_output_arrival=latest_output,
                latest_output_field=last_field,
                gate_excess_over_period=max(0,maximal_gate[0]-period),
                output_excess_over_period=max(0,latest_output-period),
                limitation='Optimistic lower bound for this particular greedy '
                           'site placement, not for all placements; excludes '
                           'packet conflicts, switches, buffer and lookup.')


def check():
    return bound(*place(include_state=True))


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
