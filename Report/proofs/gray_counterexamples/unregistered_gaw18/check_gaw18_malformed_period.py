"""Selected physical second period after GAW17's unmasked U record.

No native projection or legal-upper evaluator theorem is used on receiver0.
This is a diagnostic continuation of the same frozen rule/error history.
The companion proof supplies the physical gather/reset/quiet/exterior lift.
"""
from pathlib import Path
from dataclasses import replace
from functools import lru_cache
import hashlib,json,sys,time

S=Path(__file__).resolve().parent;ROOT=S.parents[3]
D=ROOT/'figs/gray_counterexamples/unregistered_gaw18'
sys.path.insert(0,str(S.parent/'unregistered_gaw2'))
sys.path.insert(0,str(S.parent/'unregistered_gaw4'))
import gray_three_gather_gaw2r as k
import gaw2r_compositional_cost as own
import check_gaw4_real1_mail as base
P=k.PRIMARY_START
PREVIOUS=ROOT/'figs/gray_counterexamples/unregistered_gaw17/native_program104_complete.json'
PREVIOUS_SHA='48b7dd60ae4d402153c47a3a508c5e0f72fbf6f71d23c4d4edec306607a1f2f0'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def previous():
    assert sha(PREVIOUS)==PREVIOUS_SHA
    r=json.loads(PREVIOUS.read_text());b=r['actual_U_and2U_boundary']
    assert r['full_planned_error_burst_executed'] and r['actual_same_intact_H']
    assert not b['actual_U_legal_E_encoding'] and not b['legal_record_period_theorem_applied']
    assert b['actual_U_bad_normal_receivers']==[0]
    assert not b['actual_U_nonzero_unused_Info']
    assert b['actual_U_illegal_native_words']==[[0,i,hex(k.MASK),limit] for i,limit in enumerate((k.Q,k.U,2,2,2,2)) if i]
    records={int(g):tuple(int(v,16) for v in ws) for g,ws in b['actual_U_normal_full_words'].items()}
    assert records[0][:6]==(0,k.MASK,k.MASK,k.MASK,k.MASK,k.MASK)
    for g,ws in records.items():
        if g:assert ws==tuple(k.cell_words(base.nextH(g)))
    return r,records

R,RECORDS=previous()

@lru_cache(None)
def words(g):return RECORDS[g] if g in RECORDS else tuple(k.cell_words(base.nextH(g)))

@lru_cache(None)
def data(y):
    g,a=divmod(y,k.Q);i=a-P
    return words(g)[i] if 0<=i<k.FRAME_WORDS else 0

@lru_cache(None)
def bank(y):return sum(data(y+j*k.Q)<<((j+8)*k.WORD) for j in range(-8,9))

def raw_record(g):
    z=k.cell_from_words(list(words(g)))
    assert tuple(k.cell_words(z))==words(g),'raw Word100 native words were normalized'
    return z

def execute(g,early=False,retain=False,physical=False):
    p=k.Packet(p=1,pc=own.ROM.early_pc if early else 0);address=P
    out={};scratch={};signature=hashlib.sha256();lo=hi=address;stores=0;events=[]
    checks=0;coverage=set()
    limit=75*k.Q-1-k.EARLY_BIRTH if early else 120*k.Q-(102*k.Q+1)
    for tick in range(1,limit+1):
        oldaddress=address;oldp=p
        address+=1 if p.move==1 else -1 if p.move==2 else 0
        assert P<=address<P+k.FRAME_WORDS,(g,early,tick,address,'escaped physical frame')
        lo=min(lo,address);hi=max(hi,address)
        p,ow,sw=k.step_packet(p,address,bank(g*k.Q+address),out.get(address,0),scratch.get(address,0),k.beta_bit(own.ROM,address),own.ROM)
        if physical:
            key=(oldp.mode,p.mode,oldp.move,p.move,oldp.args&3)
            if ow is not None or key not in coverage or tick<=3:
                checks+=check_execution_step(g,early,tick,oldaddress,oldp,address,p,ow,sw,out,scratch)
            coverage.add(key)
        if ow is not None:out[address]=ow;stores+=1
        if sw is not None:scratch[address]=sw
        signature.update(json.dumps([address,hex(k.pack(p)),None if ow is None else hex(ow),None if sw is None else hex(sw)],separators=(',',':')).encode()+b'\n')
        if retain:events.append((tick,address,p,ow,sw))
        if p.mode in (k.HALT,k.ERROR):break
    outputs=tuple(out.get(P+i,0) for i in range(k.FRAME_WORDS))
    expected=tuple(k.cell_words(k.local_transition({j:raw_record(g+j) for j in range(-8,9)},own.ROM))) if not early else None
    shadow=tuple(k.cell_words(base.next2H(g))) if not early else None
    mismatch=[] if early else [i for i,(a,b) in enumerate(zip(outputs,expected)) if a!=b]
    shadowdiff=[] if early else [i for i,(a,b) in enumerate(zip(outputs,shadow)) if a!=b]
    r=dict(receiver=g,early=early,physical_birth=k.EARLY_BIRTH if early else 102*k.Q+1,
        updates=tick,available_updates=limit,last_computed_age=(k.EARLY_BIRTH if early else 102*k.Q+1)+tick,
        HALT=p.mode==k.HALT,ERROR=p.mode==k.ERROR,
        input_bank_all100bits_derived_from_actual_U=True,legal_upper_theorem_used=False,
        actual_gather_bank_sha256=hashlib.sha256(json.dumps([hex(bank(g*k.Q+P+i)) for i in range(k.FRAME_WORDS)],separators=(',',':')).encode()).hexdigest(),
        min_head_address=lo,max_head_address=hi,stores=stores,
        final_address=address,final_packet_hex=hex(k.pack(p)),
        execution_digest_sha256=signature.hexdigest(),
        actual_output_words=[hex(v) for v in outputs],
        actual_scratch_words=[[a,hex(v)] for a,v in sorted(scratch.items())],
        courier_seed_low_bits=[outputs[3]&1,outputs[2]&1] if early else None,
        literal_raw_helper_output=None if early else [hex(v) for v in expected],
        literal_raw_helper_mismatched_indices=mismatch,
        shadow_mismatched_indices=shadowdiff,
        illegal_native_output_words=[[i,hex(outputs[i]),limit] for i,limit in enumerate((k.Q,k.U,2,2,2,2)) if not 0<=outputs[i]<limit])
    if physical:r.update(actual_full_local_R_execution_checks=checks,
        actual_mode_movement_coverage=[list(v) for v in sorted(coverage)])
    return r,dict(out=out,scratch=scratch,packet=p,address=address,events=events)

def history(y,age,g):
    if age<k.GATHER_STARTS[g-1]:return 0
    if age>=k.capture(g,0) and age>=k.capture(g,16):return bank(y)
    return sum(data(y+(lane-8)*k.Q)<<(lane*k.WORD) for lane in range(17) if k.capture(g,lane)<=age)

def prefix_cell(x,age):
    """Derived coherent gather/control fields; interpreter fields separately lifted.

    Courier/Workspace0 is justified by the actual early executions, not
    imposed as an independent command history.  This constructor is used
    only after that zero-seed premise has been checked in physical_run.
    """
    assert 0<=age<k.U
    start=max(s for s in k.STAGE_STARTS if s<=age)
    if start in k.GATHER_STARTS and age>start:
        distance=min(age-start-1,16*k.Q-2)
        ml=lambda y:data(y+distance);mr=lambda y:data(y-distance)
    else:ml=mr=lambda y:0
    fullmem=k.EARLY_RESET<=age<96*k.Q or 102*k.Q+1<=age<k.U
    return k.Cell(addr=x%k.Q,age=age,
        info=tuple(data(x+s) for s in k.SLOTS),
        program=tuple(k.beta_bit(own.ROM,(x+s)%k.Q) for s in k.SLOTS),
        mem=tuple(bank(x+s) if fullmem else 0 for s in k.SLOTS),
        mail_l=tuple(ml(x+s) for s in k.SLOTS),mail_r=tuple(mr(x+s) for s in k.SLOTS),
        history1=tuple(history(x+s,age,1) for s in k.SLOTS),
        history2=tuple(history(x+s,age,2) for s in k.SLOTS),
        history3=tuple(history(x+s,age,3) for s in k.SLOTS))

def work_cell(x,age,g,address,packet,out,scratch):
    origin=g*k.Q
    return replace(prefix_cell(x,age),
        heads=tuple(k.pack(packet) if x+s==origin+address else 0 for s in k.SLOTS),
        out=tuple(out.get(x+s-origin,0) for s in k.SLOTS),
        scratch=tuple(scratch.get(x+s-origin,0) for s in k.SLOTS))

def check_execution_step(g,early,tick,oldaddress,oldp,address,p,ow,sw,out,scratch):
    age=(k.EARLY_BIRTH if early else 102*k.Q+1)+tick;origin=g*k.Q
    @lru_cache(None)
    def old(x):return work_cell(x,age-1,g,oldaddress,oldp,out,scratch)
    newout=out if ow is None else {**out,address:ow}
    newscratch=scratch if sw is None else {**scratch,address:sw}
    xs={origin+a-s for a in (oldaddress,address) for s in k.SLOTS}
    for x in xs:
        actual=k.local_transition({j:old(x+j) for j in range(-8,9)},own.ROM)
        expected=work_cell(x,age,g,address,p,newout,newscratch)
        assert actual==expected,(g,early,tick,x,'actual five-holder interpreter update')
    return len(xs)

def control_checks(early_work):
    """Actual resets, captures, temporal-majority load and source closures."""
    signature=hashlib.sha256();checks=0
    # Every gather/lane capturing the actual malformed record, every one of
    # its five native words, and every actual holder.  No lane is preloaded.
    events=[]
    for stage in (1,2,3):
        for lane in range(17):
            delta=lane-8;g=-delta;age=k.capture(stage,lane)
            for i in range(1,6):
                y=g*k.Q+P+i
                assert (history(y,age,stage)>>(lane*k.WORD))&k.MASK==k.MASK
                for s in k.SLOTS:events.append((y-s,age))
    # Reset/LOAD/birth/guard edges at the frame and physical colony edges.
    ages=sorted(set(k.STAGE_STARTS[1:])|{1,32*k.Q+1,64*k.Q+1,k.EARLY_RESET,k.EARLY_BIRTH,102*k.Q+1,
        75*k.Q,80*k.Q-1,96*k.Q-1,96*k.Q+1,98*k.Q-1,98*k.Q,99*k.Q})
    for g in range(-8,9):
        for age in ages:
            for a in (0,1,2,3,4,5,P-2,P,P+1,P+2,P+3,P+4,P+5,P+k.FRAME_WORDS-1,P+k.FRAME_WORDS+1,k.Q-5,k.Q-4,k.Q-3,k.Q-2,k.Q-1):
                events.append((g*k.Q+a,age))
    for x,age in events:
        g=x//k.Q
        def old(y):
            if k.EARLY_BIRTH<=age-1<96*k.Q:
                w=early_work[g]
                return work_cell(y,age-1,g,w['address'],w['packet'],w['out'],w['scratch'])
            return prefix_cell(y,age-1)
        actual=k.local_transition({j:old(x+j) for j in range(-8,9)},own.ROM)
        expected=prefix_cell(x,age)
        if age==k.EARLY_BIRTH or age==102*k.Q+1:
            expected=replace(expected,heads=tuple(k.pack(k.Packet(p=1,pc=own.ROM.early_pc if age==k.EARLY_BIRTH else 0))
                if (x+s)%k.Q==P else 0 for s in k.SLOTS))
        elif k.EARLY_BIRTH<age<96*k.Q:
            w=early_work[g]
            expected=work_cell(x,age,g,w['address'],w['packet'],w['out'],w['scratch'])
        assert actual==expected,(x,age,'actual gather/reset/birth/courier/WF control')
        signature.update(json.dumps([x,age,k.cell_words(actual)],separators=(',',':')).encode())
        checks+=1
    return dict(actual_full_local_R_control_checks=checks,control_signature_sha256=signature.hexdigest(),
        malformed_capture_cases=3*17*5*5,
        all100bit_capture_words_unmasked=True,actual_three_banks_bitwise_temporal_majority=True,
        actual_early_and_late_reset_birth=True,actual_early_zero_couriers_and_final_primary_WF=True)

def commit_checks(late_work):
    signature=hashlib.sha256();checks=0
    def expected(x):return base.encoded(x,base.next2H)
    for g in range(-8,9):
        w=late_work[g]
        xs={g*k.Q+a for a in range(P-4,P+k.FRAME_WORDS+5)}
        xs.update(g*k.Q+a for a in (-5,-3,-2,-1,0,1,2,3,4,5,k.Q-5,k.Q-4,k.Q-3,k.Q-2,k.Q-1))
        @lru_cache(None)
        def old(x):return work_cell(x,k.U-1,g,w['address'],w['packet'],w['out'],w['scratch'])
        for x in sorted(xs):
            actual=k.local_transition({j:old(x+j) for j in range(-8,9)},own.ROM)
            assert actual==expected(x),(g,x,'full unmasked old-Out commit/reset at2U')
            signature.update(json.dumps([x,k.cell_words(actual)],separators=(',',':')).encode());checks+=1
    return dict(actual_2U_full_local_R_commit_reset_checks=checks,
        actual_2U_commit_signature_sha256=signature.hexdigest(),
        complete_raw_reset_native_SF_programme_and_Info=True,
        unused_Info_at2U_zero=True,all_affected496normal_words_equal_clean_shadow=True)

def raw_shadow_checks():
    """Selected raw-helper comparison only, never a malformed quotient."""
    differences=[i for i,(a,b) in enumerate(zip(words(0),k.cell_words(base.nextH(0)))) if a!=b]
    assert differences==list(range(1,220))
    attrs=('heads','mem','out','info','scratch','program','courier_l','courier_r','mail_l','mail_r','history1','history2','history3')
    native=sf=0
    for g in range(-8,9):
        raw={j:raw_record(g+j) for j in range(-8,9)}
        clean={j:base.nextH(g+j) for j in range(-8,9)}
        got=k.native_at(raw)
        assert got==k.native_at(clean)==dict(addr=g%k.Q,age=2,f1=0,f2=0,wf1=0,wf2=0)
        native+=1
        for name in attrs:
            for y in range(-3,4):
                assert k.logical(raw,name,y)==k.logical(clean,name,y),(g,name,y,'single raw holder absorption')
                sf+=1
        assert k.local_transition(raw,own.ROM)==base.next2H(g)
    return dict(exact_malformed_receiver0_different_word_indices=differences,
        malformed_native_illegal_word_indices=[1,2,3,4,5],
        exact_unmasked_raw_record_roundtrip=True,selected_raw_native_checks=native,
        selected_raw_SF_vote_checks=sf,
        all_selected_raw_helper_successors_equal_shadow=True,
        universal_padding_projection_or_emitter_identity=False)

def physical_run():
    cases=[];early_work={};late_work={}
    for g in range(-8,9):
        early,e=execute(g,True,physical=True);late,l=execute(g,physical=True)
        assert early['HALT'] and early['updates']==150 and early['courier_seed_low_bits']==[0,0]
        assert late['HALT'] and late['updates']==65062 and not late['illegal_native_output_words']
        assert not late['literal_raw_helper_mismatched_indices'] and not late['shadow_mismatched_indices']
        early_work[g]=e;late_work[g]=l;cases.append(dict(receiver=g,early=early,late=late))
        print(json.dumps(dict(stage='physical_interpreter_coupling',receiver=g,checks=early['actual_full_local_R_execution_checks']+late['actual_full_local_R_execution_checks'])),flush=True)
    controls=control_checks(early_work);commit=commit_checks(late_work);rawcheck=raw_shadow_checks()
    return dict(Q=k.Q,U=k.U,error_lambda=24,error_separation=104,
        prior_complete_receipt_sha256=sha(PREVIOUS),prior_original_error_history_unchanged=True,
        no_new_errors=True,unmasked_record0=[hex(v) for v in words(0)],unused_Info_at_actual_U=[],
        cases=cases,actual_control_contract=controls,actual_2U_commit_contract=commit,
        selected_unmasked_raw_comparison=rawcheck,
        selected_malformed_physical_period_composed=True,complete2U_and_all_later_no_error_shadow=True,
        universal_malformed_evaluator_or_Gray_or_iid_claim=False,
        legal_upper_theorem_on_malformed_record=False,new_CA_or_shorter_U=False)

def run():
    cases=[]
    for g in range(-8,9):
        early,_=execute(g,True);late,_=execute(g)
        cases.append(dict(receiver=g,early=early,late=late))
        print(json.dumps(dict(stage='actual_bank_selected_execution',receiver=g,early_updates=early['updates'],
            seed=early['courier_seed_low_bits'],late_updates=late['updates'],HALT=late['HALT'],
            literal_raw_mismatch=late['literal_raw_helper_mismatched_indices'],shadow_mismatch=late['shadow_mismatched_indices'],
            illegal=late['illegal_native_output_words'])),flush=True)
    return dict(Q=k.Q,U=k.U,error_lambda=24,error_separation=104,
        prior_complete_receipt_sha256=sha(PREVIOUS),prior_original_error_history_unchanged=True,
        no_new_errors=True,unmasked_record0=[hex(v) for v in words(0)],unused_Info_at_actual_U=[],
        cases=cases,universal_malformed_evaluator_or_Gray_or_iid_claim=False,
        legal_upper_theorem_on_malformed_record=False,new_CA_or_shorter_U=False)

if __name__=='__main__':
    start=time.monotonic();physical='--physical' in sys.argv
    r=physical_run() if physical else run();p=D/('GAW18_malformed_period_certificate02.json' if physical else 'GAW18_selected_execution_discovery02.json')
    if '--issue' in sys.argv:
        assert not p.exists();p.write_text(json.dumps(r,indent=2)+'\n')
    else:assert r==json.loads(p.read_text())
    print(json.dumps(dict(passed=True,stage='physical_period_composed' if physical else 'selected_executions_only',cases=len(r['cases']),elapsed_seconds=time.monotonic()-start)),flush=True)
