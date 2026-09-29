"""Check whether the complete evaluator can allocate local output sinks.

This is a static inventory only. It does not add output acceptance to the
physical rule or reschedule packet launches and gate switches.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

from gacsca.fixed_rule import spatial_epoch as physical
from gacsca.fixed_rule import spatial_fanout_compiler as compiler
from gacsca.fixed_rule import stream28_holder_program as reference
from experiments.fixed_rule.explore_spatial_topology import explore


def inventory():
    program=reference.compiled_description()
    layout=reference.layout()
    compiled=compiler.compile_capacity()
    placement=explore()
    output_gate_wires=[wire for wire in program.outputs if wire>=program.inputs]
    output_raw_wires=[wire for wire in program.outputs if wire<program.inputs]
    routed_raw_sites={use.source_site for use in compiled.uses
                      if use.source_gate<0}
    raw_output_sites={layout.wires[wire] for wire in output_raw_wires}
    raw_source_sites=routed_raw_sites|raw_output_sites
    free_memory=[site for site in range(layout.memory_count)
                 if site not in raw_source_sites]
    assert len(set(program.outputs))==len(program.outputs)
    assert len(free_memory)>=len(output_gate_wires)
    source_load=Counter()
    for node in compiled.nodes:
        source_load[placement.sites[(node.gate_index,node.copy)]]+=node.route_count
    gate_source_sites=[placement.sites[(wire-program.inputs,0)]
                       for wire in output_gate_wires]
    assert len(set(gate_source_sites))==len(gate_source_sites)
    assert None not in raw_output_sites
    after=source_load.copy()
    for site in gate_source_sites:after[site]+=1
    assert max(after.values())<=physical.ROUTE_SLOTS
    return dict(description_sha256=program.digest(),Q=physical.Q,
                fixed_rule_width_bits=physical.WIDTH,
                output_words=len(program.outputs),direct_raw_output_words=len(output_raw_wires),
                gate_output_words=len(output_gate_wires),
                raw_source_sites=len(raw_source_sites),memory_sites=layout.memory_count,
                raw_output_only_source_sites=len(raw_output_sites-routed_raw_sites),
                unused_memory_sites=len(free_memory),
                proposed_sink_sites=free_memory[:len(output_gate_wires)],
                maximum_output_source_site_routes_before=max(source_load[site]
                                                            for site in gate_source_sites),
                maximum_output_source_site_routes_after=max(after[site]
                                                           for site in gate_source_sites),
                maximum_routes_any_gate_site_after=max(after.values()),
                limitation='Static bank/route capacity only; no physical '
                           'OUTPUT transition, output packet schedule, '
                           'continuous replay, or self-reference closure.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    result=inventory()
    result['source_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    print(json.dumps({key:value for key,value in result.items()
                      if key!='proposed_sink_sites'},indent=2))
    if args.output:
        if args.output.exists():raise FileExistsError(args.output)
        args.output.write_text(json.dumps(result,indent=2)+'\n')
