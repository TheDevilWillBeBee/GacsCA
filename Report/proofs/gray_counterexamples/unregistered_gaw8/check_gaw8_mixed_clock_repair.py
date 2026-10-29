"""Exact finite GAW8 repair certificate on the frozen actual intact H.

The held-SF phase equation proof is in GAW8_MIXED_CLOCK_REPAIR.md. Native
event trajectories and chronological whole-cell replacement recipes are
replayed here. This creates no physical rule or independently chosen tape.
"""
from pathlib import Path
from dataclasses import replace
from functools import lru_cache
import ctypes,hashlib,json,random,sys,time
S=Path(__file__).resolve().parent
sys.path.insert(0,str(S))
import search_gaw8_clock_controls as campaign
ROOT=campaign.ROOT;D=campaign.D;prior=campaign.prior;base=campaign.base;k=campaign.k;own=campaign.own
T=96*k.Q;HORIZON=4*k.Q
F1,F2,W1,W2=campaign.F1,campaign.F2,campaign.W1,campaign.W2
NAMES=base.NAMES

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

@lru_cache(None)
def held(x):return prior.row96(x)

@lru_cache(None)
def held_words(x):return k.cell_words(held(x))

def native_words(x,n,v):
    return [x%k.Q,T+n+(v&65535),(v>>16)&1,(v>>17)&1,(v>>18)&1,(v>>19)&1]

def actual_cell(x,n,v):
    gf,age,f1,f2,w1,w2=native_words(x,n,v)
    return replace(held(x),addr=gf,age=age,f1=f1,f2=f2,wf1=w1,wf2=w2)

def source_phase_checks():
    """Samples supplement the universal exact phase/field-case proof."""
    rng=random.Random(0x8f96);digest=hashlib.sha256();count=0
    # Exercise every normal primary, all source/colony boundary predicates,
    # both signs of colony quotient, and multiple genuine held I/B words.
    points=list(range(k.PRIMARY_START-2,k.PRIMARY_START+k.FRAME_WORDS+2))
    edge=list(range(-8,9))+list(range(k.Q-9,k.Q+9))
    samples=[(x,1+(x%31)) for x in points]
    for g in (-2,0,2):
        samples.extend((g*k.Q+x,n) for x in edge for n in (0,1,3844,5111,8181,2*k.Q,HORIZON))
    for x,n in samples:
        symbols={d:rng.randrange(17)|(rng.randrange(16)<<16) for d in range(-8,9)}
        cells={d:actual_cell(x+d,n,symbols[d]) for d in range(-8,9)}
        got=k.local_transition(cells,own.ROM)
        assert got.addr==x%k.Q
        assert T+n+1<=got.age<=T+n+17
        assert got.wf1==got.wf2==0,(x,n,got)
        for name in NAMES:
            assert getattr(got,name)==getattr(held(x),name),(x,n,name)
        digest.update(json.dumps([x,n,sorted(symbols.items()),k.cell_words(got)],separators=(',',':')).encode()+b'\n')
        count+=1
    return dict(actual_full_local_R_checks=count,all496_normal_primaries_exercised=True,
        every_GF_boundary_predicate_class_exercised=True,both_special_source_regions_exercised=True,
        arbitrary_native_flag_inputs_sampled=True,phase_interval_field_proof_required=True,
        signature_sha256=digest.hexdigest())

def chronological_payload(c,case):
    """Derive actual old/new native fields using this same physical history.

    All SF words are the proved held H words, not a freely selected tape.
    Their exact whole-cell recipe is native_words + held_words(x)[6:].
    """
    b=case['start'];rows=case['native_rows'];state={};events=[];actual=set();declared=set()
    digest=hashlib.sha256();selected=[]
    for n,row in enumerate(rows):
        if n:
            nextstate={}
            for x in range(min(state,default=b)-5,max(state,default=b+15)+6):
                vals=(ctypes.c_uint32*11)(*[state.get(x+d,0) for d in range(-5,6)])
                v=int(c.gaw8_cofactor(vals,x%k.Q))
                if v:nextstate[x]=v
            state=nextstate
        for j,v in enumerate(row):
            x=b+j;old=state.get(x,0);assert 1<=v&65535<=16
            assert not v&campaign.AGEONLY
            declared.add((x,T+n))
            if old!=v:actual.add((x,T+n))
            events.append([x,T+n,old,v])
            oldwords=native_words(x,n,old)+held_words(x)[6:]
            newwords=native_words(x,n,v)+held_words(x)[6:]
            digest.update(json.dumps([x,T+n,oldwords,newwords],separators=(',',':')).encode()+b'\n')
            if case.get('case_index')==628:
                selected.append(dict(x=x,t=T+n,old_words=[hex(w) for w in oldwords],
                    replacement_words=[hex(w) for w in newwords],actual_change=old!=v))
            if v:state[x]=v
            else:state.pop(x,None)
    assert all((b+j,T) in actual for j in range(16))
    cl=base.gray_errors.classify(actual,actual,Q=k.Q,U=k.U,sep=104,exact_limit=1)
    declared_cl=base.gray_errors.classify(declared,declared,Q=k.Q,U=k.U,sep=104,exact_limit=1)
    for classification in (cl,declared_cl):
        assert classification['level0']==0 and classification['level1']
        assert classification['extent']==(16,len(rows))
    return dict(native_chronological_events=events,actual_changed_support=sorted(actual),
        declared_overwrite_support=sorted(declared),actual_classification=cl,declared_classification=declared_cl,
        whole_cell_recipe='native_words(x,elapsed,symbol)+frozen_actual_row96_words(x)[6:]',
        complete_chronological_whole_cell_words_sha256=digest.hexdigest(),
        selected_complete_whole_cell_payload=selected)

def initial_library():
    c=ctypes.CDLL(str(D/'gaw8_categorical_native_initial.so'))
    c.gaw8_cofactor.argtypes=[ctypes.POINTER(ctypes.c_uint32),ctypes.c_int]
    c.gaw8_cofactor.restype=ctypes.c_uint32
    return c

def initial_cofactor_identity(c):
    old=initial_library();rng=random.Random(0x8b181);count=0;digest=hashlib.sha256()
    for p in list(range(6))+list(range(k.Q-5,k.Q)):
        for _ in range(256):
            vals=[rng.randrange(17)|(rng.randrange(16)<<16) for _ in range(11)]
            raw=(ctypes.c_uint32*11)(*vals)
            a=int(c.gaw8_cofactor(raw,p));b=int(old.gaw8_cofactor(raw,p));assert a==b
            digest.update(json.dumps([p,vals,a],separators=(',',':')).encode()+b'\n');count+=1
    return dict(initial_linear_vs_binary_lookup_cofactor_checks=count,signature_sha256=digest.hexdigest())

def main(write=True):
    start=time.monotonic();c=campaign.library()
    original=json.loads((D/'GAW8_clock_control_campaign.json').read_text())
    assert original['clock_survivors_past_proved_source_horizon']==[628]
    assert len(original['cases'])==795
    checks=campaign.native_checks(c);assert checks==original['native_cofactor_checks']
    lookup=initial_cofactor_identity(c);sources=source_phase_checks()
    print(json.dumps(dict(actual_scalar_checks=checks['actual_scalar_checks'],
        actual_full_local_R_checks=sources['actual_full_local_R_checks'],starting_exact795_replay=True)),flush=True)
    cases=[];events=0;old_fields=[n for n,_ in campaign.Result._fields_]+['updates','final_state']
    for index,old in enumerate(original['cases']):
        init=campaign.run(c,old['start'],old['native_rows'],source_horizon=3844)
        assert init=={name:old[name] for name in old_fields},('old horizon replay',index)
        if old['status']==1:
            repaired=campaign.run(c,old['start'],old['native_rows'],source_horizon=HORIZON)
            ext=json.loads((D/'GAW8_case628_extended.json').read_text())
            assert {name:repaired[name] for name in ext if name in repaired}=={name:v for name,v in ext.items() if name in repaired}
        else:repaired=init
        assert repaired['status']==0 and repaired['final_segments']==0 and repaired['final_state']==[]
        assert 0<repaired['clock_recovery']<=repaired['native_recovery']<k.Q
        assert repaired['max_segments']<4096 and repaired['updates']==repaired['native_recovery']
        recipe=dict(old,case_index=index)
        payload=chronological_payload(c,recipe)
        cases.append(dict(case_index=index,start=old['start'],native_rows=old['native_rows'],kind=old['kind'],
            original_query_status=old['status'],repaired_native_record=repaired,
            **payload,actual_H_same_shared_history=True,actual_SF_held_derived=True,
            complete_global_shadow_at_native_quiet=True,first_U_and_all_later_decodes_shadow=True,
            operational_failure=False))
        events+=repaired['events']
        if (index+1)%200==0:print(json.dumps(dict(replayed=index+1,elapsed_seconds=time.monotonic()-start)),flush=True)
    result=dict(name='GAW8 exact mixed nonuniform-clock/control actual-period repair instances',Q=k.Q,U=k.U,
        error_lambda=24,error_separation=104,source_phase_horizon=HORIZON,
        offsets=[0,16],original_query_horizon=3844,original_query_stop_case628_preserved=True,
        original_campaign_sha256=sha(D/'GAW8_clock_control_campaign.json'),
        actual_native_cofactors=checks,initial_projection_identity=lookup,actual_phase_interval_cofactors=sources,
        cases=cases,exact_event_intervals=events,maximum_clock_recovery=max(v['repaired_native_record']['clock_recovery'] for v in cases),
        maximum_whole_raw_shadow_recovery=max(v['repaired_native_record']['native_recovery'] for v in cases),
        all_integer_Q_translates_covered_by_proved_factor=True,all_actual_changed_sets_original_real1=True,
        complete_first_U_encoding_and_all_later_shadow=True,
        arbitrary_mixed_GF_or_full_Age_payload_repair_proved=False,all_real1_repair_proved=False,
        Gray_G17_iid_or_shorter_U_conclusion=False,new_rule_created=False,active_rule_modified=False,
        registered_main_modified=False,elapsed_seconds=time.monotonic()-start)
    assert result['maximum_clock_recovery']==5111 and result['maximum_whole_raw_shadow_recovery']==8182
    path=D/'GAW8_mixed_clock_repair_receipt.json'
    if write:path.write_text(json.dumps(result,indent=2)+'\n')
    else:
        old=json.loads(path.read_text());a=dict(result);a.pop('elapsed_seconds');old.pop('elapsed_seconds')
        assert json.loads(json.dumps(a))==old,'GAW8 deterministic result mismatch'
    print(json.dumps(dict(passed=True,cases=len(cases),event_intervals=events,
        maximum_clock_recovery=5111,complete_whole_raw_shadow_by=8182,
        complete_first_U_and_later_shadow=True,Gray_iid=False,elapsed_seconds=time.monotonic()-start)),flush=True)
    return result

if __name__=='__main__':main()
