"""Count the staged lookup successor against the unchanged 8Q ROM geometry."""
from collections import Counter
from math import ceil
import json
from pathlib import Path

from gacsca.fixed_rule import spatial_codec8
from gacsca.fixed_rule import stream28_dual_holder_rule20 as holder
from gacsca.fixed_rule.word_allocation_and import allocate
from gacsca.fixed_rule.wordcode_and import LIT
from gacsca.fixed_rule.u20_repair import successor,successor_optimized


def check():
    program=successor_optimized.build()
    static_fields=set(range(len(holder.STATIC)))
    spatial_dynamic={1,3,*range(spatial_codec8.FIELDS-12,
                                spatial_codec8.FIELDS)}
    for i in range(spatial_codec8.FIELDS):
        if i not in spatial_dynamic:static_fields.add(holder.FIELDS+i)
    static_fields.update(range(successor.base_rule.FIELDS,
                               successor.base_rule.FIELDS+3))
    outputs=tuple(i for i in range(successor.FIELDS) if i not in static_fields)
    used={wire for opcode,a,b in program.operations if opcode!=LIT
          for wire in (a,b) if wire<program.inputs}
    used.update(wire for wire in program.outputs if wire<program.inputs)
    static_inputs=sum(wire%successor.FIELDS in static_fields for wire in used)
    dynamic_inputs=len(used)-static_inputs
    limit=38
    def routed(wire):
        return wire<program.inputs or program.operations[wire-program.inputs][0]!=LIT
    demand=Counter()
    for op,a,b in program.operations:
        if op!=LIT:
            if routed(a):demand[a]+=1
            if routed(b):demand[b]+=1
    for field in outputs:demand[program.outputs[field]]+=1
    copies=[1]*len(program.operations)
    for index in range(len(copies)-1,-1,-1):
        wire=program.inputs+index
        copies[index]=max(1,ceil(demand[wire]/limit))
        op,a,b=program.operations[index]
        if op!=LIT:
            if routed(a):demand[a]+=copies[index]-1
            if routed(b):demand[b]+=copies[index]-1
    scratch=allocate(program).count
    recipe=8+3*dynamic_inputs+2*len(outputs)+scratch
    gate_sites=successor.Q-5-recipe-static_inputs
    raw_over=[(wire,demand[wire]) for wire in range(program.inputs)
              if demand[wire]>limit]
    return dict(Q=successor.Q,U=successor.U,alphabet_bits=successor.WIDTH,
                raw_fields=successor.FIELDS,
                optimized_sha256=program.digest(),
                optimized_operations=len(program.operations),
                used_static_inputs=static_inputs,
                gathered_dynamic_inputs=dynamic_inputs,
                represented_dynamic_outputs=len(outputs),
                scratch_words=scratch,memory_recipe_words=recipe,
                static_source_sites=static_inputs,
                available_gate_sites=gate_sites,
                available_gate_slots=gate_sites*3,
                required_gate_copies=sum(copies),
                gate_slot_margin=gate_sites*3-sum(copies),
                raw_inputs_over_38=raw_over,
                limitation='Counted layout only; no placement or physical full-U trajectory')


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,
                        default=Path('figs/fixed_rule/u20_repair/successor_capacity.json'))
    args=parser.parse_args()
    result=check()
    if args.output.exists():raise FileExistsError(args.output)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,indent=2,sort_keys=True))
