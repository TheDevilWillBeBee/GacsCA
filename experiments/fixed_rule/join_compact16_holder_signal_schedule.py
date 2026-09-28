"""Conditional join of actual SEND schedules, capture buffers and flag windows."""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import time

from gacsca.fixed_rule import compact16_holder_rule as f, compact16_holder_core as c, compact16_holder_program as p
from experiments.fixed_rule.audit_small_holder_position_events import sha


def check(schedule,boundary):
    assert schedule['passed'] and boundary['passed']
    assert schedule['descriptor_sha256']==boundary['descriptor_sha256']==f.self_description().digest()
    assert boundary['formulas']['all_clock_ages']==f.U and boundary['formulas']['arbitrary_raw_fields']
    assert boundary['clearing']['total_clearing_ticks']==f.Q
    phases={row['name']:row for row in schedule['phases']}
    packets=[row for phase in phases.values() for row in phase['packets']]
    assert packets and all(row[-1]<c.CAPTURE_AGE-1<c.WF_START for row in packets)
    assert not phases['precommit_halt']['packets'] and not phases['final_evaluation']['packets']
    assert all(phase['packet_summary']['all_destination_accesses_before_delivery'] for phase in phases.values())
    third=phases['third_evaluation'];g=p.layout();signals=[]
    expected_targets={c.LEFT:set(range(1,6)),c.RIGHT:set(range(f.Q-5,f.Q))}
    for direction,field,target in ((c.LEFT,'f2',3),(c.RIGHT,'f1',f.Q-3)):
        group=[row for row in third['packets'] if row[4]==direction]
        source=g.hold[f.COL[field]]
        assert len(group)==5 and {row[3] for row in group}==expected_targets[direction]
        assert all(row[2]==source and row[4]>>1==0 for row in group)
        first_pc,last_pc=min(row[0] for row in group),max(row[0] for row in group)
        assert all(op.kind==c.SEND for op in g.instructions[first_pc:last_pc+1])
        assert source not in {row[3] for row in third['packets']}
        assert third['head_stopped']<c.CAPTURE_AGE-1
        signals.append(dict(field=field,primary=target,source=source,targets=sorted(expected_targets[direction]),
                            last_delivery_age=max(row[-1] for row in group),capture_old_age=c.CAPTURE_AGE-1,
                            old_Data_margin=c.CAPTURE_AGE-1-max(row[-1] for row in group),
                            common_source_unchanged_between_SENDs=True))
    # No clock override can change a delivered buffer before capture; the
    # schedule has no later access and its head has halted before capture.
    last_delivery=max(row[-1] for row in third['packets'])
    assert not any(last_delivery<=age<c.CAPTURE_AGE for age in (*c.RESET_AGES,*c.VOTE_AGES,f.U-1))
    assert boundary['off_window']['both_flags_zero_by_age']<phases['final_evaluation']['origin']
    # Previous-period clearing and zero Wf across wrap restore the zero-flag
    # prefix premise. Actual entry/Data/schedule refinement is still separate.
    return dict(passed=True,packet_occurrences_checked=len(packets),signal_buffers=signals,
                all_packet_lifetimes_end_before_forcing=True,no_SEND_during_or_after_forcing=True,
                latest_packet_delivery_age=max(row[-1] for row in packets),forcing_entry_age=c.WF_START,
                both_flags_zero_by_age=boundary['off_window']['both_flags_zero_by_age'],
                final_evaluation_origin=phases['final_evaluation']['origin'],
                conditional_conclusion='Given the actual checked instruction/packet trajectory, initial empty mail and zero Flag1/Flag2/Wf, flag clearing cannot erase any scheduled packet; equal five-buffer low bits reach each Signal primary before capture, and flags clear before final evaluation and next-period gather.',
                limitation='No claim here that this trajectory is produced from every encoded entry. Semantic Data/instruction induction and the physical-to-simulated macrostep relation remain open.')

