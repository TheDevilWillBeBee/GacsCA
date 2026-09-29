"""Measured healthy-path timing inequalities for the fixed U=2^20 rule.

This composes three endpoint/schedule audits. It does not evolve a complete
colony for one work period, nor prove that their endpoint states compose.
"""
import argparse
import hashlib
import json
from pathlib import Path
import time

from gacsca.fixed_rule import spatial_epoch8 as evaluator
from gacsca.fixed_rule import stream28_dual_parameters20 as parameters
from gacsca.fixed_rule import stream28_dual_pass20 as physical
from experiments.fixed_rule.audit_stream28_compact_gather import check as gather
from experiments.fixed_rule.audit_dual_holder_send20 import check as send
from experiments.fixed_rule.measure_compact_output_phase import check as output


def check():
    started=time.perf_counter()
    g=gather(u20=True)
    s=send()
    o=output(eight_q=True,dual_pass=True,u20=True)
    assert g['passed'] and s['passed'] and o['passed']
    q=parameters.Q
    assert physical.Q==q and physical.U==parameters.U
    assert g['stage_window']==16*q
    assert len(g['last_arrival_by_stage'])==3
    gather_deadlines=[]
    for stage,arrival in enumerate(g['last_arrival_by_stage']):
        reset=parameters.RESET_AGES[stage]
        deadline=reset+16*q
        absolute=reset+arrival
        assert absolute<deadline
        gather_deadlines.append(dict(stage=stage,absolute_last_arrival=absolute,
                                     active_end=deadline,margin=deadline-absolute))
    assert gather_deadlines[-1]['absolute_last_arrival']<parameters.VOTE_AGES[0]
    assert physical.EARLY_RUN_START+o['latest_output_arrival']<physical.EARLY_RUN_STOP
    early_last_hold=physical.EARLY_RUN_START+o['latest_output_arrival']
    send_halt=physical.EARLY_RUN_STOP+s['last_head_halt_tick']
    send_last_delivery=(physical.EARLY_RUN_STOP+
                        s['last_boundary_data_delivery_tick'])
    assert early_last_hold<physical.EARLY_RUN_STOP
    assert send_last_delivery<parameters.ACTIVE_ENDS[2]<parameters.CAPTURE_AGE
    assert send_halt<parameters.ACTIVE_ENDS[2]
    assert parameters.CAPTURE_AGE<parameters.WF_START<parameters.WF_END
    assert parameters.WF_END<parameters.RESET_AGES[4]
    final_start=parameters.RESET_AGES[4]+2
    final_last_hold=final_start+o['latest_output_arrival']
    final_stop=final_start+evaluator.PERIOD
    assert final_last_hold<final_stop<parameters.U
    return dict(passed=True,Q=q,U=parameters.U,
                fixed_physical_width_bits=physical.WIDTH,
                fixed_radius=max(abs(delta) for delta in physical.NEIGHBORHOOD),
                gather_deadlines=gather_deadlines,
                first_vote_age=parameters.VOTE_AGES[0],
                early_run_start=physical.EARLY_RUN_START,
                early_last_hold=early_last_hold,
                early_run_stop=physical.EARLY_RUN_STOP,
                send_halt=send_halt,
                send_last_delivery=send_last_delivery,
                send_margin_to_stage3_end=(parameters.ACTIVE_ENDS[2]-
                                           send_last_delivery),
                stage3_end=parameters.ACTIVE_ENDS[2],
                signal_capture=parameters.CAPTURE_AGE,
                wf_start=parameters.WF_START,wf_end=parameters.WF_END,
                final_run_start=final_start,
                final_last_hold=final_last_hold,
                final_run_stop=final_stop,
                margin_after_final_stop=parameters.U-final_stop,
                description_sha256=o['description_sha256'],
                seconds=time.perf_counter()-started,
                limitation='Composed healthy-path endpoint and timing witness; '
                           'no continuous U-period physical colony or decoded '
                           'successive upper macrosteps.')


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
