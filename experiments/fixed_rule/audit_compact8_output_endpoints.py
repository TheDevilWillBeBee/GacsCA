"""Literal late output/receiver/Hold endpoints of the 8Q own-F schedule.

The WordCode oracle supplies each completed gate's expected value. This does
not replay the 25,862 operand packets or solve the static-ROM fixed point.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import random
import resource
import time

from gacsca.fixed_rule import spatial_epoch8 as spatial
from gacsca.fixed_rule import stream28_holder_rule as holder
from gacsca.fixed_rule import stream28_dual_holder_rule20 as holder20
from gacsca.fixed_rule import stream28_compact_vote8 as prior
from gacsca.fixed_rule import stream28_dual_pass8 as dual
from gacsca.fixed_rule import stream28_dual_pass20 as dual20
from gacsca.fixed_rule import stream28_compact_vote_optimized8 as optimized
from gacsca.fixed_rule import stream28_dual_pass_optimized8 as dual_optimized
from gacsca.fixed_rule import stream28_dual_pass_optimized20 as dual_optimized20
from gacsca.fixed_rule import stream28_spatial_overlay8 as late
from gacsca.fixed_rule import stream28_spatial_overlay20 as late20
from experiments.fixed_rule import stream28_compact_routes as compiler
from experiments.fixed_rule.measure_stream28_spatial_capacity import (
    PROJECTED_OUTPUT_FIELDS)
from experiments.fixed_rule.measure_compact_output_phase import check as timing


def check(*,dual_pass=False,u20=False):
    started=time.perf_counter()
    if u20 and not dual_pass:raise ValueError('U20 requires dual pass')
    combined=dual20 if u20 else dual if dual_pass else prior
    raw_rule=holder20 if u20 else holder
    early=dual20 if u20 else dual
    final=late20 if u20 else late
    plan=timing(eight_q=True,dual_pass=dual_pass,u20=u20)
    routes=compiler.build(True,dual_pass,u20)
    program=routes.program
    rng=random.Random(2026092846)
    widths=(dual_optimized20 if u20 else
            dual_optimized if dual_pass else optimized).WIDTHS
    words=tuple(rng.getrandbits(width) for width in widths)
    expected=program.evaluate(words)
    launch=plan['output_launch_tick']
    output_edges=tuple(edge for edge in routes.edges
                       if edge.target_kind=='output')
    assert len(output_edges)==119
    site_slot_max=Counter()
    for site,slot,weight in routes.gate_positions.values():
        site_slot_max[site]=max(site_slot_max[site],slot)
    source_steps=target_steps=holder_steps=early_holder_steps=0
    earlier_gate_outputs=0
    for edge in output_edges:
        value=expected[PROJECTED_OUTPUT_FIELDS[edge.target_id]]
        gate_index,copy=edge.source_id
        opcode=program.operations[gate_index][0]
        mark=spatial.OUTPUT_OPCODE[opcode]
        source_slot=routes.gate_positions[edge.source_id][1]
        final_slot=site_slot_max[edge.source_site]
        earlier_gate_outputs+=int(source_slot<final_slot)
        gates=list(spatial.EMPTY_GATES)
        gates[source_slot]=spatial.GateSpec(1,mark)
        route=spatial.Route(1,edge.target_site,0,3,source_slot,launch)
        source=spatial.Cell(address=edge.source_site,age=launch-1,
              kind=spatial.GATE,active_slot=final_slot,
              gates=tuple(gates),
              routes=(route,)+(spatial.EMPTY_ROUTE,)*
                     (spatial.ROUTE_SLOTS-1),
              source_value=value,done=0)
        after=spatial.local_step((spatial.Cell(),source,spatial.Cell()))
        packet=spatial.Packet(1,edge.target_site,0,3,value)
        if after.mail!=packet or after.collision:
            raise AssertionError(('late latch source',edge.target_id))
        source_steps+=1

        arrival=launch+edge.distance
        assert arrival<spatial.PERIOD
        sink=spatial.Cell(address=edge.target_site,age=arrival-1,
                          kind=spatial.OUTPUT)
        right=spatial.Cell(mail=packet)
        accepted=spatial.local_step((spatial.Cell(),sink,right))
        if accepted.source_value!=value or not accepted.done:
            raise AssertionError(('output receiver',edge.target_id))
        target_steps+=1

        for offset in raw_rule.OFFSETS:
            physical_site=(edge.target_site-offset)%raw_rule.Q
            for early in ((False,True) if dual_pass else (False,)):
                neighbors=[]
                for delta in combined.NEIGHBORHOOD:
                    site=(physical_site+delta)%raw_rule.Q
                    spatial_cell=spatial.Cell(address=site,age=arrival-1,
                        kind=spatial.OUTPUT if site==edge.target_site else
                             spatial.INERT,
                        mail=(packet if site==(edge.target_site+1)%raw_rule.Q
                              else spatial.EMPTY_PACKET))
                    raw=raw_rule.Cell(address=site,
                                    age=((combined.EARLY_RUN_START if early else
                                          final.RUN_START)+arrival-1))
                    neighbors.append(combined.Cell(raw,spatial_cell))
                after=combined.local_step(tuple(neighbors))
                want_data=(value if not early or
                           edge.target_site in combined.EARLY_FLAG_HOLD_ADDRESSES
                           else 0)
                if getattr(after.holder,f's{offset+2}_data')!=want_data:
                    raise AssertionError(('fivefold Hold receiver',
                                          edge.target_id,offset,early))
                if early:early_holder_steps+=1
                else:holder_steps+=1
    assert (source_steps,target_steps,holder_steps)==(119,119,595)
    assert earlier_gate_outputs==2
    assert early_holder_steps==(595 if dual_pass else 0)
    return dict(passed=True,description_sha256=program.digest(),
                dual_pass_own_rule=dual_pass,
                upper_work_period=(1<<20 if u20 else 1<<28),
                output_launch_tick=launch,
                latest_output_arrival=plan['latest_output_arrival'],
                literal_source_steps=source_steps,
                literal_output_receiver_steps=target_steps,
                literal_fivefold_holder_steps=holder_steps,
                literal_early_holder_steps=early_holder_steps,
                output_gates_reused_before_late_emission=earlier_gate_outputs,
                max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                seconds=time.perf_counter()-started,
                combined_source_sha256=hashlib.sha256(
                    Path(combined.__file__).read_bytes()).hexdigest(),
                limitation='Oracle-initialized local output endpoints, not '
                           'a continuous combined-rule U-period or a '
                           'dynamically maintained address-indexed ROM.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--dual-pass',action='store_true')
    parser.add_argument('--u20',action='store_true')
    args=parser.parse_args()
    result=check(dual_pass=args.dual_pass,u20=args.u20)
    result['source_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    print(json.dumps(result,indent=2))
    if args.output:
        if args.output.exists():raise FileExistsError(args.output)
        args.output.write_text(json.dumps(result,indent=2)+'\n')
