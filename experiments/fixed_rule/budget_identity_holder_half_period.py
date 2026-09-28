"""Prospective half-period budget, explicitly not an installed transition rule."""
import argparse
import hashlib
import json
from pathlib import Path
from gacsca.fixed_rule import identity_holder_program as p,small_holder_rule as f
from experiments.fixed_rule.audit_small_holder_position_events import sha


def budget():
    g=p.layout();old=g.timing_certificate();U=1<<31
    resets=(0,150000000,290000000,1230000000,1232000000)
    ends=(149000000,288000000,1228000000,1231000000,2025000000)
    votes=(430000000,resets[4]);capture=1224000000
    wf_start=resets[3];wf_end=wf_start+2*f.Q
    rows=[]
    for stage,row in enumerate(old['gathers']):
        last=resets[stage]+max(row['head_stopped'],row['last_arrival'])
        deadline=votes[0] if stage==2 else ends[stage]
        assert last<deadline
        rows.append(dict(phase=f'gather_{stage}',last_event=last,deadline=deadline,margin=deadline-last))
    third=votes[0]+max(old['stage3_head_stopped'],old['stage3_last_delivery'])
    assert third<capture-1<ends[2]<wf_start
    rows.append(dict(phase='third_evaluation',last_event=third,deadline=capture-1,margin=capture-1-third))
    precommit=resets[3]+g.schedule(*g.stage_ranges[3])[0]
    assert precommit<ends[3]<resets[4]
    assert wf_end+f.Q<resets[4]
    rows.append(dict(phase='precommit_halt',last_event=precommit,deadline=ends[3],margin=ends[3]-precommit))
    final=resets[4]+old['evaluation_ticks']
    assert final<ends[4]<U-1
    rows.append(dict(phase='final_evaluation',last_event=final,deadline=ends[4],margin=ends[4]-final))
    return dict(passed=True,proposal_only=True,Q=f.Q,proposed_U=U,RESET_AGES=resets,ACTIVE_ENDS=ends,
                VOTE_AGES=votes,CAPTURE_AGE=capture,WF_START=wf_start,WF_END=wf_end,
                checked_current_program_paths=rows,flag_clear_margin=resets[4]-wf_end-f.Q,
                physical_descriptor_unchanged=True,installed_U=f.U,
                limitation='Budget uses the current optimized program only. Changing clock constants and wrap changes the self-described rule and may change its ROM/layout/timings. Compile the resulting fixed point and recertify paths, boundaries, recurrence and execution before claiming a halved U. No accelerated evolution is installed by this calculation.')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();out=Path(args.output)
    if out.exists():raise FileExistsError('preserve evidence')
    result=budget();result['source_sha256']={str(path):sha(path) for path in (Path(__file__),Path(p.__file__))}
    result['current_rom_sha256']=hashlib.sha256(p.base_rom().tobytes()).hexdigest()
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':main()
