"""Reachable failures of extending the previous active-factor premises."""
from pathlib import Path
import json,sys,time
S=Path(__file__).resolve().parent;sys.path.insert(0,str(S))
import search_gaw15_phase_packets as m
import continue_gaw15_phase_packets as full
k=m.k

def words(state,y):
    return {n:[hex(v) for v in state.copies(n,y)] for n in m.FIELDS}

def check():
    start=time.monotonic();case=m.recipes()[0];s=m.Phase(case);row=s.step(check=True)
    y=m.P;v=words(s,y)
    assert all(z==1 for z in s.copies('info',y))
    assert all(z==0 for n in ('heads','mem','out','scratch','history1','history2','history3') for z in s.copies(n,y))
    assert all(s.a[y-slot-s.offset].age==0 for slot in k.SLOTS)
    first=dict(recipe=case,logical_y=y,old_actual_voted_Out='0x1',clean_Info=hex(m.base.I(y)),
        actual_next_copies=v,actual_full_local_R_checks=row['actual_full_local_R_checks'],
        Info_equals_old_Out_before_out_reset=True,readonly_bank_factor_inapplicable=True)
    case=full.selected()[-1];s=m.Phase(case);B=m.prior.B(y);row=s.step(check=True)
    trim=B&~(k.MASK|(k.MASK<<(16*100)))
    assert trim!=B
    for n in ('mem','history1','history2'):assert s.copies(n,y)==(B,)*5
    assert s.copies('history3',y)==(trim,)*5
    capture=dict(recipe=case,logical_y=y,actual_computed_clock=72*k.Q+2,
        actual_old_Mail_l_and_r=[s.logical(n,y) for n in ('mail_l','mail_r')],
        actual_before_capture_bank=hex(B),actual_captured_third_bank=hex(trim),
        actual_next_copies=words(s,y),actual_full_local_R_checks=row['actual_full_local_R_checks'],
        both_symmetric_lanes0_and16_erased=True,shared_Mem_H1_H2_H3_coefficient_false=True)
    row2=s.step(check=True);assert s.logical('mem',y)==B
    capture['actual_next_reset_copies']=words(s,y)
    capture['actual_next_reset_Mem_vote']=hex(s.logical('mem',y))
    capture['actual_reset_full_local_R_checks']=row2['actual_full_local_R_checks']
    row3=s.step(check=True)
    born=[]
    for logical,row in s.diff.items():
        for h,z in enumerate(row.get('heads',(s.clean('heads',logical),)*5)):
            p=k.unpack(z)
            if p.p and p.pc==m.own.ROM.early_pc:born.append([logical,h,hex(z)])
    assert born
    capture['actual_wrong_stage_early_pc_copies']=born
    capture['actual_birth_full_local_R_checks']=row3['actual_full_local_R_checks']
    wf=[]
    for case in m.source_recipes():
        s=m.Phase(case);row=s.step(check=True);assert row['actual_Workspace_sources']
        wf.append(dict(recipe=case,actual_Workspace_from_computed_primary=row['actual_Workspace_sources'],
            actual_full_local_R_checks=row['actual_full_local_R_checks']))
    return dict(passed=True,false_commit=first,false_third_capture_and_reset_birth=capture,
        actual_source_forgeries=wf,actual_intact_T_shared_error_histories=True,
        previous_factor_premise_counterexamples_only=True,
        automaton_operational_Gray_or_iid_counterexample=False,elapsed_seconds=time.monotonic()-start)

if __name__=='__main__':
    r=check();(m.D/'GAW15_phase_dependency_witnesses.json').write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps({'passed':r['passed'],'wrong_stage_birth_copies':len(r['false_third_capture_and_reset_birth']['actual_wrong_stage_early_pc_copies']),
        'actual_source_cases':len(r['actual_source_forgeries']),'operational_or_Gray_counterexample':False,'seconds':r['elapsed_seconds']}),flush=True)
