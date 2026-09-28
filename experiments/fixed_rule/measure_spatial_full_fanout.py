"""Inventory full own-rule DAG fanout against fixed spatial route slots.

This measures a capacity obstruction and a lower bound for gate duplication;
it does not synthesize the duplicates or schedule their physical packets.
"""
import argparse
from collections import Counter
import hashlib
import json
from math import ceil
from pathlib import Path

from gacsca.fixed_rule import spatial_epoch as physical
from gacsca.fixed_rule import stream28_holder_program as program_module
from gacsca.fixed_rule.wordcode_and import LIT


def inventory():
    program=program_module.compiled_description()
    fanout=Counter()
    depth=[0]*program.inputs
    skipped_literal_operands=0
    for opcode,a,b in program.operations:
        this_depth=1 if opcode==LIT else 1+max(depth[a],depth[b])
        depth.append(this_depth)
        if opcode==LIT:continue
        for wire in (a,b):
            if wire>=program.inputs and program.operations[wire-program.inputs][0]==LIT:
                skipped_literal_operands+=1
            else:fanout[wire]+=1
    limit=physical.ROUTE_SLOTS
    over=[]
    for wire,count in fanout.items():
        if wire<program.inputs or count<=limit:continue
        index=wire-program.inputs
        over.append(dict(gate_index=index,dag_depth=depth[wire],
                         opcode=program.operations[index][0],
                         consumers=count,
                         minimum_total_copies=ceil(count/limit),
                         additional_copies=ceil(count/limit)-1))
    over.sort(key=lambda item:(-item['consumers'],item['gate_index']))
    gate_sites=physical.Q-5-program_module.layout().memory_count
    return dict(description_sha256=program.digest(),Q=physical.Q,
                fixed_rule_width_bits=physical.WIDTH,
                gate_slots_per_site=physical.GATE_SLOTS,
                route_slots_per_site=limit,original_gate_instances=len(program.operations),
                gate_sites=gate_sites,static_gate_capacity=gate_sites*physical.GATE_SLOTS,
                routed_operand_uses=sum(fanout.values()),
                locally_preloaded_literal_operand_uses=skipped_literal_operands,
                high_fanout_gates=over,
                minimum_additional_gate_copies=sum(x['additional_copies'] for x in over),
                limitation='Only a fanout lower bound. Duplicated gates may add '
                           'input fanout and require a new collision-free, '
                           'lifetime-safe physical schedule; no full-DAG fit is proved.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    result=inventory()
    result['source_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    print(json.dumps(result,indent=2))
    if args.output:
        if args.output.exists():raise FileExistsError(args.output)
        args.output.write_text(json.dumps(result,indent=2)+'\n')
