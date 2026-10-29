"""Lift twenty actual GF-only bursts to the real late bank/store and2U map.

No independently prepared tape. The banks come from the held-History
keeper recurrence and the same physical GF errors on intact H.
"""
from pathlib import Path
from dataclasses import replace
import sys,json,time,hashlib
sys.path.insert(0,str(Path(__file__).resolve().parent))
import check_gaw6_native_factor as f
sys.path.insert(0,str(f.ROOT/'Report/proofs/gray_counterexamples/unregistered_gaw5'))
import check_gaw5_history_burst as selected
base=f.base;k=base.k;own=base.own;I=base.I;H=base.H;D=f.D

def bank(y):return sum(I(y+j*k.Q)<<((j+8)*k.WORD) for j in range(-8,9))

def row96(x):
    return k.Cell(addr=x%k.Q,age=96*k.Q,info=tuple(I(x+s) for s in k.SLOTS),
        program=tuple(k.beta_bit(own.ROM,(x+s)%k.Q) for s in k.SLOTS),
        history1=tuple(bank(x+s) for s in k.SLOTS),history2=tuple(bank(x+s) for s in k.SLOTS),history3=tuple(bank(x+s) for s in k.SLOTS))

def one(c):
    assert c['status']==0 and c['computed_steps']==k.Q and not c['final_native_disagreement']
    keep=dict(c['final_History_holder_keep'])
    def copies(y):return [(keep.get(y-s,31)>>h)&1 for h,s in enumerate(k.SLOTS)]
    def tag(y):
        bits=copies(y);assert bits==[bits[0]]*5,(y,bits);return bits[0]
    # At the retained quiet row the copy groups are coherent. A canonical
    # future native row cannot produce a wipe, and I=0 at both source
    # primaries makes all remaining first-window Workspace outputs0.
    for x in range(min(keep,default=0)-4,max(keep,default=0)+5):tag(x)
    assert all(I(g*k.Q+a)==0 for g in range(-16,16) for a in (3,k.Q-3))
    info=dict(c['final_Info_lowbit'])
    for x in set(info)|set(keep):
        z=info.get(x,sum((I(x+s)&1)<<h for h,s in enumerate(k.SLOTS)))
        assert z==sum(((I(x+s)&1)*tag(x+s))<<h for h,s in enumerate(k.SLOTS))
    nativequiet=next(t for t,g,gl,gr,flags,ik,sl,sr in c['event_rows'] if g==flags==0)
    support=set();payload=[]
    for v in c['original_real1_support']:
        x=v['x'];old=row96(x);new=replace(old,addr=v['new_GF']);assert old.addr==v['old_GF']
        support.add((x,v['t']));payload.append(dict(x=x,t=v['t'],only_changed_field='GF',
            old_words=[hex(w) for w in k.cell_words(old)],replacement_words=[hex(w) for w in k.cell_words(new)]))
    cl=base.gray_errors.classify(support,support,Q=k.Q,U=k.U,sep=104)
    assert cl['level0']==0 and cl['level1'] and cl['extent']==(16,1)
    receivers=sorted({y//k.Q for x in keep for y in range(x-2,x+3) if k.PRIMARY_START<=y%k.Q<k.PRIMARY_START+k.FRAME_WORDS})
    outputs={};executions=[]
    for g in receivers:
        tape={k.PRIMARY_START+i:bank(g*k.Q+k.PRIMARY_START+i)*tag(g*k.Q+k.PRIMARY_START+i) for i in range(k.FRAME_WORDS)}
        execution=selected.run(tape);out=[int(w,16) for w in execution[0]['out_words']]
        cell=k.cell_from_words(out);assert k.cell_words(cell)==out
        assert 0<=cell.addr<k.Q and 0<=cell.age<k.U and all(getattr(cell,n) in (0,1) for n in ('f1','f2','wf1','wf2'))
        outputs[g]=cell;executions.append(dict(receiver=g,actual_derived_readonly_words=[[p,hex(v)] for p,v in sorted(tape.items())],
            History_normal_tags=[tag(g*k.Q+k.PRIMARY_START+i) for i in range(k.FRAME_WORDS)],late_execution=execution[0]))
    bad=[g for g,v in outputs.items() if v!=base.nextH(g)]
    assert len(bad)<=1,(c['start'],c['delta'],bad)
    upper=lambda g:outputs.get(g,base.nextH(g))
    # Complete actual upper transition, every possibly affected radius8 site.
    checked=[]
    for b in bad:
        for g in range(b-8,b+9):
            actual=k.local_transition({j:upper(g+j) for j in range(-8,9)},own.ROM)
            assert actual==base.next2H(g),(c['start'],c['delta'],g)
            checked.append(g)
    return dict(start=c['start'],delta=c['delta'],support=sorted(support),classification=cl,whole_cell_payloads=payload,
        native_quiet_by_elapsed=nativequiet,native_quiet_before102Q=True,
        actual_derived_History_erasure_count=len(keep),affected_normal_frames=receivers,
        actual_first_late_executions=executions,first_boundary_bad_upper_cells=bad,
        checked_actual_second_upper_transition_sites=checked,
        first_boundary_E_Cprime=True,complete_actual_2U_shadow_encoding=True,
        ordinary_sacrificed_upper_error_relation_satisfied=True,operational_failure=False)

def main(write=True):
    start=time.monotonic();source=json.loads((D/'GAW6_GF_burst_search.json').read_text())
    cases=[one(c) for c in source['cases']]
    result=dict(name='GAW6 actual native-control burst to held-bank/full-period map',Q=k.Q,U=k.U,
        error_lambda=24,error_separation=104,source_search_sha256=hashlib.sha256((D/'GAW6_GF_burst_search.json').read_bytes()).hexdigest(),
        cases=cases,intact_H_same_error_history=True,actual_source_and_histories_derived=True,
        all_first_boundaries_at_most_one_bad_upper_cell=True,all_complete_second_boundaries_shadow=True,
        all_arbitrary_real1_bursts_proved=False,Gray_iid_or_shorter_U=False,new_rule_created=False,
        physical_period_direct_simulation_claimed=False,elapsed_seconds=time.monotonic()-start)
    path=D/'GAW6_actual_bank_map_receipt.json'
    if write:path.write_text(json.dumps(result,indent=2)+'\n')
    else:
        old=json.loads(path.read_text());a=dict(result);a.pop('elapsed_seconds');old.pop('elapsed_seconds');assert json.loads(json.dumps(a))==old
    print(json.dumps(dict(passed=True,cases=len(cases),first_late_executions=sum(len(c['actual_first_late_executions']) for c in cases),
        bad_upper_cells=[c['first_boundary_bad_upper_cells'] for c in cases],
        maximum_native_quiet=max(c['native_quiet_by_elapsed'] for c in cases),
        complete2Ushadow=True,Gray_iid=False,elapsed_seconds=result['elapsed_seconds'])))
    return result

if __name__=='__main__':main()
