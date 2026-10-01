"""Conditional 8Q leftward Hold phase after all compact operands clear.

This is *not executable by the current 4Q spatial rule*: an 8Q Age field and
late emission from a marked, ready output latch are required. It isolates the
remaining physical-rule change and exact output packet geometry.
"""
import argparse
from collections import Counter,defaultdict
import hashlib
import json
from pathlib import Path

from gacsca.fixed_rule import spatial_epoch
from experiments.fixed_rule import stream28_compact_routes as compiler
from experiments.fixed_rule.schedule_compact_operands import schedule


def check(*,eight_q=False,dual_pass=False,u20=False):
    operands=schedule(8*spatial_epoch.Q,eight_q=eight_q,
                      dual_pass=dual_pass,u20=u20)
    assert operands['passed']
    routes=compiler.build(eight_q,dual_pass,u20)
    outputs=tuple(e for e in routes.edges if e.target_kind=='output')
    assert len(outputs)==119
    start=operands['latest_event']+1
    phases=Counter((e.source_site+start)%spatial_epoch.Q for e in outputs)
    sources=Counter(e.source_site for e in outputs)
    sinks=Counter(e.target_site for e in outputs)
    assert max(phases.values())==max(sources.values())==max(sinks.values())==1
    site_nodes=defaultdict(list)
    for key,(site,slot,weight) in routes.gate_positions.items():
        site_nodes[site].append((slot,key))
    earlier_output_gates=[]
    opcodes=Counter()
    for edge in outputs:
        key=edge.source_id
        assert edge.source_kind=='gate'
        slot=routes.gate_positions[key][1]
        if slot!=max(row[0] for row in site_nodes[edge.source_site]):
            earlier_output_gates.append(key)
        opcodes[routes.program.operations[key[0]][0]]+=1
    latest=max(start+edge.distance for edge in outputs)
    assert latest<8*spatial_epoch.Q
    return dict(passed=True,mode='dual_pass_u20_8q_rule' if u20 else
                'dual_pass_8q_rule' if dual_pass else
                '8q_rule' if eight_q else '4q_rule',
                description_sha256=routes.program.digest(),
                operand_schedule_last_tick=operands['latest_event'],
                output_launch_tick=start,
                output_packets=len(outputs),
                distinct_output_sources=len(sources),
                distinct_hold_sinks=len(sinks),
                distinct_leftward_phases=len(phases),
                output_source_gates_reused_later=earlier_output_gates,
                output_source_opcodes=dict(opcodes),
                latest_output_arrival=latest,
                margin_to_8q=8*spatial_epoch.Q-latest,
                limitation=('Analytical output phase under actual fixed 8Q '
                            'local rule; no continuous physical replay, '
                            'static ROM lookup, or fixed-point closure.'
                            if eight_q else
                            'Conditional topology/timing only. Current 4Q '
                            'local rule cannot emit after gate reuse.'))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--eight-q',action='store_true')
    parser.add_argument('--dual-pass',action='store_true')
    parser.add_argument('--u20',action='store_true')
    args=parser.parse_args()
    result=check(eight_q=args.eight_q,dual_pass=args.dual_pass,u20=args.u20)
    result['source_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    print(json.dumps(result,indent=2))
    if args.output:
        if args.output.exists():raise FileExistsError(args.output)
        args.output.write_text(json.dumps(result,indent=2)+'\n')
