"""Reproducible routing-pressure inventory for a future local spatial evaluator.

These are DAG/resource measurements, not a local spatial evaluator or a
certificate of Gray's 8Q computation budget.
"""
from collections import Counter
import hashlib
import json
from pathlib import Path

from gacsca.fixed_rule import stream28_holder_rule as f
from gacsca.fixed_rule import stream28_holder_program as p
from gacsca.fixed_rule.wordcode_and import LIT


def backward(program,outputs):
    seen=set();pending=list(outputs)
    while pending:
        wire=pending.pop()
        if wire<program.inputs or wire in seen:continue
        seen.add(wire)
        opcode,a,b=program.operations[wire-program.inputs]
        if opcode!=LIT:pending.extend((a,b))
    return frozenset(seen)


def check():
    program=p.compiled_description();layout=p.layout()
    depths=[0]*program.inputs;layers=Counter();fanout=Counter();edges=0
    for opcode,a,b in program.operations:
        if opcode==LIT:depth=1
        else:
            depth=1+max(depths[a],depths[b]);fanout[a]+=1;fanout[b]+=1;edges+=2
        depths.append(depth);layers[depth]+=1
    for wire in program.outputs:fanout[wire]+=1
    copies={k:backward(program,(program.outputs[i]
             for i,(name,_) in enumerate(f.SCHEMA)
             if name.startswith(f's{k}_'))) for k in range(5)}
    ownership=Counter(wire for cone in copies.values() for wire in cone)
    remaining_nonmemory=f.Q-5-layout.memory_count
    local_budget=8*f.Q
    assert max(depths[w] for w in program.outputs)==73
    assert sum(layers.values())==len(program.operations)
    return dict(Q=f.Q,U=f.U,late_Gray_budget_ticks=local_budget,
                compiled_operations=len(program.operations),
                operand_edges=edges,critical_path_operations=max(depths[w] for w in program.outputs),
                maximum_layer_width=max(layers.values()),
                first_ten_layer_widths=[layers[k] for k in range(1,11)],
                nonmemory_sites_before_tail=remaining_nonmemory,
                ideal_work_ticks_if_all_nonmemory_sites_compute=
                    (len(program.operations)+remaining_nonmemory-1)//remaining_nonmemory,
                average_max_routing_ticks_per_critical_layer=
                    local_budget//max(depths[w] for w in program.outputs),
                maximum_input_fanout=max(fanout[w] for w in range(program.inputs)),
                per_replicated_procedure_copy_cone=[len(copies[k]) for k in range(5)],
                operations_used_by_only_one_copy=sum(count==1 for count in ownership.values()),
                operations_shared_by_multiple_copies=sum(count>=2 for count in ownership.values()),
                operations_outside_procedure_copies=len(program.operations)-len(ownership),
                compiled_sha256=program.digest(),
                scope='DAG and site inventory only; no placed circuit, local routing '
                      'schedule, executable spatial transition, or U=2^20 claim.')


if __name__=='__main__':
    result=check();path=Path('figs/fixed_rule/stream28_spatial_dag_v1.json')
    if path.exists():raise FileExistsError(path)
    path.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
