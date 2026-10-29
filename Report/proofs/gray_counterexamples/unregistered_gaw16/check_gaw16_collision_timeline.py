"""Actual interacting-prefix collision and derived phase/WF timelines."""
from pathlib import Path
import hashlib,json,sys,time
S=Path(__file__).resolve().parent;ROOT=S.parents[3];sys.path.insert(0,str(S))
import search_gaw16_word_bursts as m
k=m.k

def check():
    started=time.monotonic();r=m.recipes()[3];state=m.Phase(r);y=k.Q-1
    packets=[k.unpack(state.logical('heads',y+j)) for j in (-1,0,1)]
    assert all(p.p for p in packets) and [p.move for p in packets]==[1,1,2]
    incoming=k.incoming(packets);assert incoming.mode==k.ERROR and incoming.move==0
    row=state.step(check=True)
    collision=dict(recipe=r,logical_y=y,actual_old_voted_Head_words=[hex(k.pack(p)) for p in packets],
        actual_incoming_collision_packet=hex(k.pack(incoming)),
        actual_next_raw_Head_copies=[hex(v) for v in state.copies('heads',y)],
        actual_full_local_R_checks=row['actual_full_local_R_checks'],
        no_future_collision_packet_or_tape_supplied=True,not_an_operational_failure=True)
    timeline=[]
    for recipe in m.recipes():
        name=recipe['tag']+'_complete.json';p=m.D/name;z=json.loads(p.read_text());rows=z['actual_rows']
        support={(v['x'],v['t']) for v in z['complete_chronological_error_payload']}
        assert len(support)==256 and {t for _,t in support}==set(range(m.T,m.T+16))
        assert {x for x,_ in support}==set(range(recipe['start'],recipe['start']+16))
        c=m.base.gray_errors.classify(support,support,Q=k.Q,U=k.U,sep=104,exact_limit=1)
        assert m.previous.stable(c)==m.previous.stable(z['original_c104_classification'])
        assert all(q['actual_old_nonboolean_Programme_sites']==16 for q in rows[:16])
        assert all(q['actual_old_nonboolean_Programme_sites']==0 for q in rows[16:])
        phase_dates=sorted({age for q in rows for x,age in q['actual_phase_events']})
        wf=[[q['tick'],q['actual_Workspace_sources']] for q in rows if q['actual_Workspace_sources']]
        if recipe['tag']=='cycle_commit_capture16':assert phase_dates==[0,1,72*k.Q+2,72*k.Q+3,72*k.Q+4]
        if recipe['tag']=='word_source16':assert [len(q[1]) for q in wf]==[8]*16+[1]
        else:assert not wf
        timeline.append(dict(tag=recipe['tag'],complete_receipt_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
            actual256_point_shared_history_original_real1=True,
            actual_nonboolean_Programme_inputs_256_sites_then_boolean=True,
            actual_computed_phase_event_dates=phase_dates,actual_computed_Workspace_rows=wf,
            explicit_Workspace_NOT_a_future_tape=True))
    return dict(passed=True,actual_interacting_incoming_collision=collision,actual_four_timelines=timeline,
        full_original_classifier_rechecked=True,actual_Workspace129_outputs_and17rows=True,
        general_interacting_or_control_repair_or_Gray_iid=False,elapsed_seconds=time.monotonic()-started)

if __name__=='__main__':
    r=check();(m.D/'GAW16_collision_phase_certificate.json').write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps(dict(passed=True,timelines=len(r['actual_four_timelines']),
        first_collision_mode=k.ERROR,seconds=r['elapsed_seconds'])),flush=True)
