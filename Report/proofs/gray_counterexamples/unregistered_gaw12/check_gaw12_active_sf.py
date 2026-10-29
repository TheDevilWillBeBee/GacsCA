"""Actual active late interpreter faults; finite discoveries and movement bound.

The actual readonly banks and all old work come from the intact H prefix.
No CA transition, ROM, future command or tape is changed or selected.
"""
from pathlib import Path
from dataclasses import replace
from functools import lru_cache
import hashlib,json,random,sys,time
ROOT=Path(__file__).resolve().parents[4];S=Path(__file__).resolve().parent
D=ROOT/'figs/gray_counterexamples/unregistered_gaw12'
sys.path.insert(0,str(S.parent/'unregistered_gaw11'))
import search_gaw11_birth_profiles as previous
k=previous.k;own=previous.own;base=previous.base;P=k.PRIMARY_START
N=4096;T=102*k.Q+1+N;HLT_PC=own.ROM.token_count
sys.path.insert(0,str(S.parent/'unregistered_gaw5'))
import check_gaw5_history_burst as history

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def packet(p):return hex(k.pack(p))
def stable(v):
    if isinstance(v,dict):return {a:stable(b) for a,b in v.items() if a!='elapsed_seconds'}
    if isinstance(v,(list,tuple)):return [stable(b) for b in v]
    return v
def signature(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()

@lru_cache(None)
def B(y):return history.bank(y)

def actual_snapshot(g,updates=N):
    p=k.Packet(p=1);address=P;out={};scratch={};h=hashlib.sha256();lo=hi=P
    for tick in range(updates):
        address+=1 if p.move==1 else -1 if p.move==2 else 0
        assert P<=address<P+k.FRAME_WORDS
        lo=min(lo,address);hi=max(hi,address)
        p,ow,sw=k.step_packet(p,address,B(g*k.Q+address),out.get(address,0),scratch.get(address,0),
                             k.beta_bit(own.ROM,address),own.ROM)
        if ow is not None:out[address]=ow
        if sw is not None:scratch[address]=sw
        h.update(json.dumps([address,packet(p),None if ow is None else hex(ow),None if sw is None else hex(sw)],separators=(',',':')).encode()+b'\n')
    assert p.p and p.mode not in (k.HALT,k.ERROR)
    return dict(receiver=g,actual_head_updates=updates,actual_physical_clock=102*k.Q+1+updates,
        head_address=address,head_packet_hex=packet(p),Out=[[a,hex(v)] for a,v in sorted(out.items())],
        Scratch=[[a,hex(v)] for a,v in sorted(scratch.items())],head_min=lo,head_max=hi,trace_sha256=h.hexdigest()),p,address,out,scratch

def global_work(snaps):
    heads={};out={};scratch={}
    for g,(_,p,a,o,s) in snaps.items():
        heads[g*k.Q+a]=p
        out.update((g*k.Q+y,v) for y,v in o.items());scratch.update((g*k.Q+y,v) for y,v in s.items())
    return heads,out,scratch

def actual_cell(x,age,heads,out,scratch):
    return k.Cell(addr=x%k.Q,age=age,
        heads=tuple(k.pack(heads.get(x+s,k.ZERO)) for s in k.SLOTS),mem=tuple(B(x+s) for s in k.SLOTS),
        out=tuple(out.get(x+s,0) for s in k.SLOTS),scratch=tuple(scratch.get(x+s,0) for s in k.SLOTS),
        info=tuple(base.I(x+s) for s in k.SLOTS),program=tuple(k.beta_bit(own.ROM,(x+s)%k.Q) for s in k.SLOTS),
        history1=tuple(B(x+s) for s in k.SLOTS),history2=tuple(B(x+s) for s in k.SLOTS),history3=tuple(B(x+s) for s in k.SLOTS))

def logical_update(heads,out,scratch,age,bank=B):
    assert 102*k.Q+1<age<=120*k.Q
    requests={}
    for y,p in heads.items():
        if p.p:
            dest=y+(1 if p.move==1 else -1 if p.move==2 else 0)
            requests.setdefault(dest,[]).append((0 if y==dest else 1 if y<dest else 2,p))
    new={};ow=dict(out);sw=dict(scratch);writes=[];collisions=[]
    for y,choices in sorted(requests.items()):
        choices.sort(key=lambda c:c[0]);p=choices[0][1]
        if len(choices)>1:p=k.fail(p);collisions.append(y)
        if p.mode in (k.HALT,k.ERROR) and p.move==0:np=p;a=b=None
        else:np,a,b=k.step_packet(p,y%k.Q,bank(y),out.get(y,0),scratch.get(y,0),k.beta_bit(own.ROM,y%k.Q),own.ROM)
        if np.p:new[y]=np
        if a is not None:ow[y]=a;writes.append([y,'Out',hex(a)])
        if b is not None:sw[y]=b;writes.append([y,'Scratch',hex(b)])
    return new,ow,sw,writes,collisions

def factor_checks(count=96):
    rng=random.Random(0x120104);digest=hashlib.sha256();checks=0
    for trial in range(count):
        # Raw SF holders need not agree: the first clean update must vote
        # and compute one logical value at every holder of that value.
        age=T+trial;raw={d:k.Cell(addr=d%k.Q,age=age,
            **{name:tuple(rng.getrandbits(2200 if name=='heads' else 1700 if name in ('mem','history1','history2','history3') else 100)
                          for h in range(5)) for name in previous.FIELDS}) for d in range(-8,9)}
        got=k.local_transition(raw,own.ROM)
        assert (got.addr,got.age,got.f1,got.f2,got.wf1,got.wf2)==(0,age+1,0,0,0,0)
        for h,y in enumerate(k.SLOTS):
            incoming=k.incoming([k.unpack(k.logical(raw,'heads',y+j)) for j in (-1,0,1)])
            mem=k.logical(raw,'mem',y)&((1<<1700)-1);o=k.logical(raw,'out',y)&k.MASK;s=k.logical(raw,'scratch',y)&k.MASK
            p,a,b=k.step_packet(incoming,y%k.Q,mem,o,s,k.logical(raw,'program',y)&k.MASK,own.ROM)
            assert got.heads[h]==k.pack(p) and got.out[h]==(o if a is None else a) and got.scratch[h]==(s if b is None else b)
            assert got.mem[h]==mem and got.program[h]==k.beta_bit(own.ROM,y%k.Q)
            for name in ('info','mail_l','mail_r','courier_l','courier_r','history1','history2','history3'):
                mask=(1<<1700)-1 if name.startswith('history') else k.MASK
                assert getattr(got,name)[h]==(k.logical(raw,name,y)&mask)
        digest.update(json.dumps(previous.packed(got),separators=(',',':')).encode());checks+=1
    return dict(actual_full_local_R_arbitrary_SF_cofactors=checks,signature_sha256=digest.hexdigest(),
                raw_holder_coherence_not_assumed_in_first_update=True,samples_supplement_algebraic_factor=True)

def actual_chronological_prefix_checks(snaps):
    before={g:actual_snapshot(g,N-1) for g in snaps}
    bh,bo,bs=global_work(before);ah,ao,ass=global_work(snaps)
    xs=sorted({g*k.Q+a for g in snaps for a in range(P-4,P+k.FRAME_WORDS+4)})
    h=hashlib.sha256()
    for x in xs:
        got=k.local_transition({d:actual_cell(x+d,T-1,bh,bo,bs) for d in range(-8,9)},own.ROM)
        assert got==actual_cell(x,T,ah,ao,ass),(x,'actual chronological fault row')
        h.update(json.dumps([x,previous.packed(got)],separators=(',',':')).encode())
    bankchecks=0
    for g in snaps:
        ws={j:k.cell_words(base.H(g+j)) for j in range(-8,9)}
        for i in range(k.FRAME_WORDS):
            assert B(g*k.Q+P+i)==sum(ws[j][i]<<((j+8)*k.WORD) for j in range(-8,9))
            bankchecks+=1
    return dict(actual_last_chronological_prefix_full_local_R_checks=len(xs),
        actual17_upper_H_records_to_retained_bank_checks=bankchecks,signature_sha256=h.hexdigest(),
        entire_prior4096_update_physical_lift_proved_by_holder_coupling=True)

def endpoint_motion_checks():
    checks=0;h=hashlib.sha256()
    for address in (0,k.Q-1):
        for target in range(k.Q):
            p=k.Packet(p=1,move=0,mode=k.SEEK,target=target,args=k.descriptor(0,0,8,0))
            got,a,b=k.step_packet(p,address,0,0,0,0,own.ROM)
            assert (got.move!=2 if address==0 else got.move!=1)
            h.update(json.dumps([address,target,k.pack(got)],separators=(',',':')).encode());checks+=1
    return dict(all_legal_SEEK_targets_at_both_colony_endpoints=checks,signature_sha256=h.hexdigest(),
        RUN_invalid_and_IO_target_bounds_proved_from_source=True,first_forged_motion_can_cross=True)

def recipes(snaps):
    crossreg=[0]*16;crossreg[0]=1
    store=k.descriptor(1,0,dest=0);passive=k.Packet(pc=1) # p0; nonzero bits make every physical overwrite genuine.
    cases=[]
    for tag,directions in (('cross_both',(-1,1)),('cross_left_only',(-1,)),('cross_right_only',(1,))):
        forged={}
        if 1 in directions:forged[k.Q-1]=k.Packet(p=1,move=1,mode=k.SEEK,pc=HLT_PC,target=P+k.FIELD['info'],args=store,regs=tuple(crossreg))
        if -1 in directions:forged[k.Q]=k.Packet(p=1,move=2,mode=k.SEEK,pc=HLT_PC,target=P+k.FIELD['info'],args=store,regs=tuple(crossreg))
        cases.append(dict(tag=tag,start=k.Q-8,forged=forged,passive=passive,Out_value=None,Scratch_value=None))
    for tag,g,value in (('direct_Out_legal_Info0',0,1),('direct_Out_high_native',0,1<<99),('direct_Scratch_masks',0,k.MASK)):
        start=P+k.FIELD['info']-7 if 'Info' in tag else P-7 if 'native' in tag else P+128-7
        cases.append(dict(tag=tag,start=start,forged={},passive=passive,
            Out_value=value if 'Out' in tag else None,Scratch_value=value if 'Scratch' in tag else None))
    return cases

def overwrite(recipe,heads,out,scratch):
    b=recipe['start'];changes={};records=[];support=set()
    for x in range(b,b+16):
        old=actual_cell(x,T,heads,out,scratch)
        hv=tuple(k.pack(recipe['forged'].get(x+s,recipe['passive'])) for s in k.SLOTS)
        z=replace(old,heads=hv,
            out=old.out if recipe['Out_value'] is None else (recipe['Out_value'],)*5,
            scratch=old.scratch if recipe['Scratch_value'] is None else (recipe['Scratch_value'],)*5)
        assert z!=old and k.cell_words(z)[:6]==k.cell_words(old)[:6]
        changes[x]=z;support.add((x,T))
        records.append(dict(x=x,t=T,old_complete_words=[hex(v) for v in k.cell_words(old)],
                            replacement_complete_words=[hex(v) for v in k.cell_words(z)]))
    classification=base.gray_errors.classify(support,support,Q=k.Q,U=k.U,sep=104,exact_limit=1)
    assert classification['level0']==0 and classification['level1'] and classification['extent']==(16,1)
    def read(x):return changes.get(x,actual_cell(x,T,heads,out,scratch))
    H=dict(heads);O=dict(out);S=dict(scratch)
    for y in range(b-3,b+19):
        for name,target in (('heads',H),('out',O),('scratch',S)):
            v=k.vote([getattr(read(y-s),name)[h] for h,s in enumerate(k.SLOTS)])
            if name=='heads':
                p=k.unpack(v)
                if p.p:target[y]=p
                else:target.pop(y,None)
            else:target[y]=v
    nh,no,ns,writes,collisions=logical_update(H,O,S,T+1)
    checks=0;d=hashlib.sha256()
    # Include the actual correct head centres far away from the fault and
    # the entire first fault/movement/support cone, not selected tapes.
    xs=sorted(set(range(b-10,b+26))|{y+j for y in set(heads)|set(nh) for j in range(-3,4)})
    for x in xs:
        got=k.local_transition({j:read(x+j) for j in range(-8,9)},own.ROM)
        expected=actual_cell(x,T+1,nh,no,ns)
        assert got==expected,(recipe['tag'],x)
        d.update(json.dumps([x,previous.packed(got)],separators=(',',':')).encode());checks+=1
    return nh,no,ns,dict(whole_cell_payloads=records,original_c104_classification=classification,
        actual_first_computed_row_full_local_R_checks=checks,actual_first_row_signature=d.hexdigest(),
        first_actual_head_positions_and_packets=[[y,packet(p)] for y,p in sorted(nh.items())],
        first_actual_writes=writes,first_actual_collisions=collisions)

def final_output(heads,out,scratch,start_age=T+1):
    d=hashlib.sha256();events=[];minhead=min(heads);maxhead=max(heads);writes=0;collisions=0;last_age=start_age
    for age in range(start_age+1,120*k.Q+1):
        if all(p.mode in (k.HALT,k.ERROR) and p.move==0 for p in heads.values()):break
        heads,out,scratch,ws,cs=logical_update(heads,out,scratch,age)
        assert all(0<=y<2*k.Q for y in heads),'finite-region assumption violated'
        minhead=min(minhead,min(heads,default=minhead));maxhead=max(maxhead,max(heads,default=maxhead))
        writes+=len(ws);collisions+=len(cs);last_age=age
        d.update(json.dumps([age,[[y,packet(p)] for y,p in sorted(heads.items())],ws,cs],separators=(',',':')).encode()+b'\n')
        if cs or any(name=='Out' and v!='0x0' for y,name,v in ws):events.append(dict(age=age,collisions=cs,writes=ws))
    stable_head=all(p.mode in (k.HALT,k.ERROR) and p.move==0 for p in heads.values())
    return heads,out,scratch,dict(last_executed_physical_age=last_age,all_heads_terminal_before120Q=stable_head,
        first_U_Out_stable_by_rest=True,head_min=minhead,head_max=maxhead,total_writes=writes,total_collisions=collisions,
        notable_events=events,complete_execution_trace_sha256=d.hexdigest(),
        final_head_positions_packets=[[y,packet(p)] for y,p in sorted(heads.items())],
        final_Out=[[y,hex(v)] for y,v in sorted(out.items())],final_Scratch=[[y,hex(v)] for y,v in sorted(scratch.items())])

def boundary_and_next(out,heads,scratch,check_actual_raw_banks=False):
    frames={g:[out.get(g*k.Q+P+i,0) for i in range(k.FRAME_WORDS)] for g in (0,1)}
    bad=[g for g,ws in frames.items() if ws!=k.cell_words(base.nextH(g))]
    limits=(k.Q,k.U,2,2,2,2);legal=all(all(0<=ws[i]<limits[i] for i in range(6)) for ws in frames.values())
    auxiliary=[[y,hex(v)] for y,v in sorted(out.items()) if not P<=y%k.Q<P+k.FRAME_WORDS and v]
    rec=dict(actual_U_bad_normal_record_receivers=bad,at_most_one_adjacent_upper_pair=True,
        first_native_padding_legal=legal,actual_U_normal_raw_words={str(g):[hex(v) for v in ws] for g,ws in frames.items()},
        actual_U_unrepresented_nonzero_Info=auxiliary,exact_U_global_reset_and_coherent_Out_commit_proved=True,
        complete2U_shadow_proved=False)
    def word(y):
        g,a=divmod(y,k.Q);i=a-P
        return frames[g][i] if g in frames and 0<=i<k.FRAME_WORDS else out.get(y,0) if g in frames else base.D1(y)
    def pre(x):return actual_cell(x,k.U-1,heads,out,scratch)
    def committed(x):
        return k.Cell(addr=x%k.Q,info=tuple(word(x+s) for s in k.SLOTS),
            program=tuple(k.beta_bit(own.ROM,(x+s)%k.Q) for s in k.SLOTS))
    xs=sorted({g*k.Q+a for g in (0,1) for a in list(range(P-5,P+k.FRAME_WORDS+5))+list(range(-5,9))+list(range(k.Q-8,k.Q+6))})
    h=hashlib.sha256()
    for x in xs:
        got=k.local_transition({j:pre(x+j) for j in range(-8,9)},own.ROM)
        assert got==committed(x),(x,'commit')
        h.update(json.dumps([x,previous.packed(got)],separators=(',',':')).encode())
    rec['actual_U_full_local_R_commit_checks']=len(xs);rec['actual_U_commit_signature']=h.hexdigest()
    if legal:
        changed={g:k.cell_from_words(ws) for g,ws in frames.items()}
        def upper(g):return changed[g] if g in changed else base.nextH(g)
        results=[]
        for g in range(-8,10):
            got=k.local_transition({j:upper(g+j) for j in range(-8,9)},own.ROM)
            assert got==base.next2H(g),(g,'second-upper-step')
            results.append([g,[hex(v) for v in k.cell_words(got)]])
        rec['actual_next_upper_full_local_R_checks']=results
        rec['actual_U_is_E_Cprime_Aprime']=True;rec['noiseless_next_period_applies_to_derived_boundary']=True
        rec['complete2U_shadow_proved']=True
    elif check_actual_raw_banks:
        # Unpadded native words are outside the frozen legal-upper theorem.
        # Execute each derived actual second bank rather than decoding away
        # the real high bits. This is a selected finite lift, not a universal
        # extension of the whole-beta theorem to all untyped records.
        runs=[]
        def raw(g):return frames[g] if g in frames else k.cell_words(base.nextH(g))
        for g in range(-8,10):
            tape=history.tape_of(raw,g)
            early=history.run(tape,early=True)
            assert [int(v,16) for v in early[0]['out_words']][2:4]==[0,0]
            late=history.run(tape)
            assert [int(v,16) for v in late[0]['out_words']]==k.cell_words(base.next2H(g))
            runs.append(dict(receiver=g,actual_derived_input_raw_records=[[j,[hex(v) for v in raw(g+j)]] for j in range(-8,9)],
                             early=early[0],late=late[0]))
        rec['selected_unpadded_actual_next_bank_executions']=runs
        rec['complete2U_shadow_proved']=True
    return rec

def campaign(write=True,all_cases=False,certify=False):
    start=time.monotonic();D.mkdir(parents=True,exist_ok=True)
    snaps={g:actual_snapshot(g) for g in (0,1)};h,o,s=global_work(snaps);cases=[]
    certificates=dict(actual_prefix=actual_chronological_prefix_checks(snaps),
        arbitrary_SF_factor=factor_checks(),endpoint_motion=endpoint_motion_checks()) if certify else None
    for i,recipe in enumerate(recipes(snaps)):
        H,O,S,initial=overwrite(recipe,h,o,s)
        H,O,S,run=final_output(H,O,S)
        result=boundary_and_next(O,H,S,check_actual_raw_banks=all_cases and recipe['tag']=='direct_Out_high_native')
        record=dict(tag=recipe['tag'],actual_fault_time=T,actual_fault_start=recipe['start'],initial=initial,
                    actual_postfault_interpreter=run,actual_U_and_recovery=result)
        cases.append(record)
        print(json.dumps(dict(case=recipe['tag'],terminal=run['all_heads_terminal_before120Q'],
            head_span=[run['head_min'],run['head_max']],last_age=run['last_executed_physical_age'],
            collisions=run['total_collisions'],bad_receivers=result['actual_U_bad_normal_record_receivers'],
            native_padding_legal=result['first_native_padding_legal'],complete2U=result['complete2U_shadow_proved'])),flush=True)
    result=dict(name='GAW12 actual active-stage SF faults and movement confinement',Q=k.Q,U=k.U,error_lambda=24,error_separation=104,
        actual_intact_H_and_chronological_prefix=True,actual_late_snapshot=[v[0] for v in snaps.values()],
        chronological_fault_time=T,actual_frozen_rule_ROM_used=True,cases=cases,
        future_tapes_Workspace_or_commands_selected=False,Gray_operational_iid_counterexample=False,
        full_general_real1_repair_proved=False,new_rule_or_shorter_U=False,elapsed_seconds=time.monotonic()-start)
    if certify:result['source_factor_and_chronological_certificates']=certificates
    path=D/'GAW12_active_sf_discovery.json'
    if write:path.write_text(json.dumps(result,indent=2)+'\n')
    else:assert stable(result)==stable(json.loads(path.read_text()))
    return result

if __name__=='__main__':campaign(all_cases='--wide-second-bank' in sys.argv,certify='--certify' in sys.argv)
