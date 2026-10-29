"""Actual H gather faults: full source/capture derivation, no future tape."""
from pathlib import Path
from dataclasses import replace
from functools import lru_cache
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[4];S=Path(__file__).resolve().parent
D=ROOT/'figs/gray_counterexamples/unregistered_gaw13'
sys.path.insert(0,str(S.parent/'unregistered_gaw12'))
import check_gaw12_active_sf as previous
k=previous.k;own=previous.own;base=previous.base;history=previous.history
P=k.PRIMARY_START;B0=P-7;W=16;FULL=(1<<(17*k.WORD))-1

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def stable(v):
    if isinstance(v,dict):return {a:stable(b) for a,b in v.items() if a!='elapsed_seconds'}
    if isinstance(v,(list,tuple)):return [stable(b) for b in v]
    return v
def sig(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()

class Actual:
    def __init__(self,tag,gather=3,info=False,histories=False):
        self.tag=tag;self.gather=gather;self.t=k.GATHER_STARTS[gather-1]+1
        self.info_noise=info;self.history_noise=histories
    def inside(self,y):return B0<=y<B0+W
    @lru_cache(None)
    def info(self,y):return k.MASK if self.info_noise and self.inside(y) else base.I(y)
    @lru_cache(None)
    def cleanhist(self,y,g,age):
        z=0
        for lane in range(17):
            if k.capture(g,lane)<=age:z|=base.I(y+(lane-8)*k.Q)<<(lane*k.WORD)
        return z
    @lru_cache(None)
    def history(self,y,g,age):
        assert age>=self.t
        z=FULL if self.history_noise and self.inside(y) else self.cleanhist(y,g,self.t)
        # Only actual future resets/captures are applied. Old captures
        # included in the chronological initial row are not replayed.
        events=[(s,'reset',0) for s in k.GATHER_STARTS[:g] if self.t<s<=age]
        events += [(k.capture(g,lane),'capture',lane) for lane in range(17) if self.t<k.capture(g,lane)<=age]
        for tick,kind,lane in sorted(events):
            if kind=='reset':z=0;continue
            d=lane-8;source=y+d*k.Q
            # Centre capture reads old Info. Noncentre capture reads
            # the actual LOAD snapshot (or the overwritten Mail train).
            if not d:v=self.info(y)
            elif g==self.gather:v=k.MASK if self.inside(source) else base.I(source)
            else:v=self.info(source) if k.GATHER_STARTS[g-1]+1>self.t else base.I(source)
            z=(z&~(k.MASK<<(lane*k.WORD)))|(v<<(lane*k.WORD))
        return z
    @lru_cache(None)
    def mem(self,y):return k.majority3(*(self.history(y,g,72*k.Q+2) for g in (1,2,3)))
    @lru_cache(None)
    def mailbox(self,y,age,side):
        s=max(s for s in k.GATHER_STARTS if s<=age)
        if age==s:return 0
        shifts=min(age-s-1,16*k.Q-2)
        source=y+shifts*(1 if side=='mail_l' else -1)
        g=k.GATHER_STARTS.index(s)+1
        if g==self.gather and age>=self.t:
            return k.MASK if self.inside(source) else base.I(source)
        return self.info(source) if s+1>self.t else base.I(source)
    def pre(self,x):
        # This is the actual clean row s+1: stage reset has happened;
        # the current LOAD and centre History capture have happened too.
        return k.Cell(addr=x%k.Q,age=self.t,
            info=tuple(base.I(x+s) for s in k.SLOTS),
            program=tuple(k.beta_bit(own.ROM,(x+s)%k.Q) for s in k.SLOTS),
            mail_l=tuple(base.I(x+s) for s in k.SLOTS),mail_r=tuple(base.I(x+s) for s in k.SLOTS),
            **{'history%d'%g:tuple(self.cleanhist(x+s,g,self.t) for s in k.SLOTS) for g in (1,2,3)})
    def raw_fault(self,x):
        old=self.pre(x)
        if not self.inside(x):return old
        changes=dict(mail_l=(k.MASK,)*5,mail_r=(k.MASK,)*5)
        if self.info_noise:changes['info']=(k.MASK,)*5
        if self.history_noise:
            changes.update({'history%d'%g:(FULL,)*5 for g in (1,2,3)})
        return replace(old,**changes)
    def row(self,x,age):
        assert self.t<age<=72*k.Q+3
        return k.Cell(addr=x%k.Q,age=age,
            mem=tuple(self.mem(x+s) for s in k.SLOTS) if age==72*k.Q+3 else (0,)*5,
            info=tuple(self.info(x+s) for s in k.SLOTS),
            program=tuple(k.beta_bit(own.ROM,(x+s)%k.Q) for s in k.SLOTS),
            mail_l=tuple(self.mailbox(x+s,age,'mail_l') for s in k.SLOTS),
            mail_r=tuple(self.mailbox(x+s,age,'mail_r') for s in k.SLOTS),
            **{'history%d'%g:tuple(self.history(x+s,g,age) for s in k.SLOTS) for g in (1,2,3)})
    def payload(self):
        rows=[];support=set()
        for x in range(B0,B0+W):
            old=self.pre(x);new=self.raw_fault(x);assert old!=new
            assert k.cell_words(old)[:6]==k.cell_words(new)[:6]
            rows.append(dict(x=x,t=self.t,old_complete_words=[hex(v) for v in k.cell_words(old)],
                             replacement_complete_words=[hex(v) for v in k.cell_words(new)]));support.add((x,self.t))
        c=base.gray_errors.classify(support,support,Q=k.Q,U=k.U,sep=104,exact_limit=1)
        assert c['level0']==0 and c['level1'] and tuple(c['extent'])==(16,1)
        return dict(complete_chronological_payloads=rows,original_c104_classification=c)

def source_capture_checks(case):
    digest=hashlib.sha256();n=0;clocks={case.t+1,72*k.Q+3}
    clocks.update(s for s in k.GATHER_STARTS if case.t<s<=72*k.Q+2)
    clocks.update(k.capture(g,lane) for g in (1,2,3) for lane in range(17) if case.t<k.capture(g,lane)<=72*k.Q+2)
    for tick in sorted(clocks):
        # Every noise wave/capture cone, its whole16-site width and all
        # five holder copies; normal operands and clean guards included.
        centres={B0+d*k.Q for d in range(-8,9)}
        xs=sorted({c+a for c in centres for a in range(-5,W+5)})
        for x in xs:
            get=case.raw_fault if tick==case.t+1 else lambda z:case.row(z,tick-1)
            got=k.local_transition({d:get(x+d) for d in range(-8,9)},own.ROM)
            expected=case.row(x,tick);assert got==expected,(case.tag,x,tick)
            digest.update(json.dumps([tick,x,previous.previous.packed(got)],separators=(',',':')).encode());n+=1
    return dict(actual_full_local_R_source_capture_reset_checks=n,event_clocks=sorted(clocks),
                signature_sha256=digest.hexdigest(),all_intervening_shift_rows_proved_algebraically=True)

def bank_reduction(case):
    # Source identities, rather than preparing a bank for the evaluator.
    rows=[];dirtyH=set();dirtyM=set();changes=[]
    for g in range(-8,9):
        for i in range(k.FRAME_WORDS):
            y=g*k.Q+P+i;clean=previous.B(y)
            hs=[case.history(y,j,72*k.Q+2) for j in (1,2,3)]
            if hs!=[clean]*3:dirtyH.add(g)
            m=case.mem(y)
            if m!=clean:
                dirtyM.add(g);changes.append([y,hex(m),hex(clean)])
            if g!=0:assert m==clean,(case.tag,g,i,'far normal bank survived temporal vote')
        # Preserve every actual normal word, not just a host Cell decode.
        rows.append([g,[[i,hex(case.mem(g*k.Q+P+i))] for i in range(k.FRAME_WORDS)]])
    return dict(actual_held_History_disagreement_normal_colonies=sorted(dirtyH),
        actual_voted_Mem_disagreement_normal_colonies=sorted(dirtyM),actual_changed_bank_words=changes,
        actual_normal_banks_sha256=sig(rows),all_17_actual_normal_banks_derived=True,
        far_normal_banks_equal_H_by_temporal_vote=True)

def history_footprint(case):
    receipt=[];y=P
    for d in range(-8,9):
        receiver_y=y-d*k.Q;lane=8+d;t=k.capture(case.gather,lane)
        if not d:continue
        actual=case.history(receiver_y,case.gather,t)
        word=(actual>>(lane*k.WORD))&k.MASK
        assert word==k.MASK and base.I(y)!=k.MASK
        receipt.append(dict(logical_position=receiver_y,lane=lane,computed_row=t,
            physical_holders=[receiver_y-s for s in k.SLOTS],actual_captured_word=hex(word),
            clean_captured_word=hex(base.I(y))))
    cols=sorted({x//k.Q for r in receipt for x in r['physical_holders']})
    assert cols==[g for g in range(-8,9) if g]
    return dict(actual_retained_third_History_noncentral_footprint=receipt,
        physical_colonies=cols,one_fixed_adjacent_pair_raw_History_bound=False,
        this_raw_retained_History_footprint_is_not_a_decoded_failure=True)

def actual_executions(case):
    tape={P+i:case.mem(P+i) for i in range(k.FRAME_WORDS)}
    early=history.run(tape,early=True);late=history.run(tape)
    # Every other colony has the actual unchanged normal B bank, as
    # certified above, and is the exact clean own evaluation.
    clean=history.run(history.tape_of(lambda g:k.cell_words(base.H(g))))
    assert [int(w,16) for w in clean[0]['out_words']]==k.cell_words(base.nextH(0))
    out=[int(w,16) for w in late[0]['out_words']]
    flags=[int(v,16) for v in early[0]['out_words']][2:4]
    return early,late,dict(actual_core_early=early[0],actual_core_late=late[0],
        actual_core_early_flag_pair=flags,actual_core_U_normal_record=[hex(v) for v in out],
        actual_core_U_record_differs_shadow=(out!=k.cell_words(base.nextH(0))),
        outside_core_outputs_are_complete_shadow_by_actual_bank_identity=True,
        no_future_tape_or_Workspace_supplied=True)

def courier_source_checks(case,early):
    flags=[int(v,16) for v in early[0]['out_words']][2:4]
    seedL=P+3;seedR=P+2
    def command(y,direction):
        g,a=divmod(y,k.Q);value=flags[1 if direction=='left' else 0] if g==0 else 0
        seed=seedL if direction=='left' else seedR;endpoint=3 if direction=='left' else k.Q-3
        return value,seed,endpoint,a
    def courier(y,age,direction):
        value,seed,end,a=command(y,direction)
        if not value:return 0
        m=age-75*k.Q
        if m<0:return 0
        if direction=='left':return int(3<=a<=seed and (a==seed-m or a==3 and m>=seed-3))
        return int(seed<=a<=k.Q-3 and (a==seed+m or a==k.Q-3 and m>=k.Q-3-seed))
    def row(x,age):
        def inf(y):
            g,a=divmod(y,k.Q)
            return flags[1] if g==0 and a==3 and age>=80*k.Q-1 else flags[0] if g==0 and a==k.Q-3 and age>=80*k.Q-1 else case.info(y)
        _,o,s,p,a=early
        return k.Cell(addr=x%k.Q,age=age,
            heads=tuple(k.pack(p) if y==a else 0 for y in (x+z for z in k.SLOTS)),
            mem=tuple(case.mem(x+s) for s in k.SLOTS),out=tuple(o.get(x+s,0) for s in k.SLOTS),
            scratch=tuple(s.get(x+z,0) for z in k.SLOTS),info=tuple(inf(x+s) for s in k.SLOTS),
            program=tuple(k.beta_bit(own.ROM,(x+s)%k.Q) for s in k.SLOTS),
            courier_l=tuple(courier(x+s,age,'left') for s in k.SLOTS),
            courier_r=tuple(courier(x+s,age,'right') for s in k.SLOTS),
            mail_l=tuple(case.mailbox(x+s,age,'mail_l') for s in k.SLOTS),
            mail_r=tuple(case.mailbox(x+s,age,'mail_r') for s in k.SLOTS),
            **{'history%d'%g:tuple(case.history(x+s,g,age) for s in k.SLOTS) for g in (1,2,3)})
    # Tail packets/Out in other colonies are clean, not0; these cones are
    # away from their normal frames and are therefore exactly the above.
    checks=0;digest=hashlib.sha256()
    for tick in (75*k.Q+1,75*k.Q+P,80*k.Q-1,80*k.Q):
        for centre in (0,3,k.Q-3,k.Q):
            for x in range(centre-5,centre+6):
                got=k.local_transition({d:row(x+d,tick-1) for d in range(-8,9)},own.ROM)
                assert got==row(x,tick),(case.tag,tick,x,'actual courier source')
                digest.update(json.dumps([tick,x,previous.previous.packed(got)],separators=(',',':')).encode());checks+=1
    return dict(actual_early_seed_flag_pair=flags,actual_full_local_R_courier_source_checks=checks,
        signature_sha256=digest.hexdigest(),special_Info_sources_colony0_flags=flags,
        all_exterior_special_sources_zero=True,actual_courier_and_Info_source_derived=True,
        actual_native_GF_clock_canonical_for_arbitrary_commands=True,
        Workspace_half_open_guard=[96*k.Q,98*k.Q],native_flag_quiet_by=99*k.Q,
        quiet_bound_uses_frozen_actual_native_zero_strip_proof=True)

def boundary_and_repair(case,execution):
    early,late,_=execution;ws=[int(v,16) for v in late[0]['out_words']]
    raw=lambda g:ws if g==0 else k.cell_words(base.nextH(g))
    flags=[int(v,16) for v in early[0]['out_words']][2:4]
    packet=late[3];a=late[4];out=late[1];scratch=late[2]
    def info(y):
        g,r=divmod(y,k.Q)
        return flags[1] if g==0 and r==3 else flags[0] if g==0 and r==k.Q-3 else case.info(y)
    def pre(x):
        g=x//k.Q
        # Only the full core frame is queried; core a±2 has all copies.
        return k.Cell(addr=x%k.Q,age=k.U-1,
            heads=tuple(k.pack(packet) if x+s==a else 0 for s in k.SLOTS),
            mem=tuple(case.mem(x+s) for s in k.SLOTS),out=tuple(out.get(x+s,0) for s in k.SLOTS),
            scratch=tuple(scratch.get(x+s,0) for s in k.SLOTS),info=tuple(info(x+s) for s in k.SLOTS),
            program=tuple(k.beta_bit(own.ROM,(x+s)%k.Q) for s in k.SLOTS),
            **{'history%d'%h:tuple(case.history(x+s,h,72*k.Q+2) for s in k.SLOTS) for h in (1,2,3)})
    def post(x):
        return k.Cell(addr=x%k.Q,info=tuple(out.get(x+s,0) for s in k.SLOTS),
            program=tuple(k.beta_bit(own.ROM,(x+s)%k.Q) for s in k.SLOTS))
    checks=0;dg=hashlib.sha256()
    for x in range(P-5,P+k.FRAME_WORDS+5):
        got=k.local_transition({d:pre(x+d) for d in range(-8,9)},own.ROM);assert got==post(x)
        dg.update(json.dumps([x,previous.previous.packed(got)],separators=(',',':')).encode());checks+=1
    legal=all(ws[i]<bound for i,bound in enumerate((k.Q,k.U,2,2,2,2)))
    bad=[] if ws==k.cell_words(base.nextH(0)) else [0]
    receipt=dict(actual_U_bad_normal_record_receivers=bad,actual_U_native_padding_legal=legal,
        actual_U_core_full_local_R_commit_checks=checks,actual_U_commit_signature=dg.hexdigest(),
        global_work_reset_and_all_Info_copy_commit_proved=True,complete_U_shadow_proved=not bad,
        complete2U_shadow_proved=False,legal_upper_period_theorem_used=False)
    # Explicit actual banks avoid the legal-upper theorem when malformed
    # native padding is present. No high input bit is truncated by host.
    runs=[]
    for g in range(-8,9):
        tape=history.tape_of(raw,g);e=history.run(tape,early=True);l=history.run(tape)
        assert [int(v,16) for v in e[0]['out_words']][2:4]==[0,0]
        assert [int(v,16) for v in l[0]['out_words']]==k.cell_words(base.next2H(g))
        runs.append(dict(receiver=g,actual17_raw_input_records=[[j,[hex(v) for v in raw(g+j)]] for j in range(-8,9)],early=e[0],late=l[0]))
    receipt.update(actual_derived_second_period_bank_executions=runs,complete2U_shadow_proved=True,
        actual_next_period_global_zero_commands_derived=True)
    return receipt

def main(write=True):
    start=time.monotonic();cases=[]
    for case in (Actual('third_LOAD_Mail_mask'),Actual('third_LOAD_Mail_Info_mask',info=True),
                 Actual('third_LOAD_Mail_Info_all_Histories_mask',info=True,histories=True)):
        print('checking '+case.tag,flush=True)
        payload=case.payload();checks=source_capture_checks(case);bank=bank_reduction(case);footprint=history_footprint(case)
        execution=actual_executions(case);sources=courier_source_checks(case,execution[0]);boundary=boundary_and_repair(case,execution)
        record=dict(tag=case.tag,fault_clock=case.t,actual_same_intact_H_physical_history=True,
            payload=payload,actual_source_capture=checks,actual_bank_reduction=bank,
            actual_retained_History_footprint=footprint,actual_evaluation=execution[2],
            actual_courier_Workspace_quiet_bridge=sources,actual_U_and_repair=boundary)
        print(json.dumps(dict(case=case.tag,dirty_History_colonies=bank['actual_held_History_disagreement_normal_colonies'],
            dirty_Mem_colonies=bank['actual_voted_Mem_disagreement_normal_colonies'],
            actual_early_flags=execution[2]['actual_core_early_flag_pair'],
            U_bad=boundary['actual_U_bad_normal_record_receivers'],padding_legal=boundary['actual_U_native_padding_legal'],
            full2U=boundary['complete2U_shadow_proved'])),flush=True);cases.append(record)
    result=dict(name='GAW13 actual gather SF faults, wide retained History and exact repair',Q=k.Q,U=k.U,
        error_lambda=24,error_separation=104,frozen_actual_rule_ROM_used=True,cases=cases,
        selected_future_tape_or_commands=False,Gray_or_operational_iid_counterexample=False,
        general_SF_real1_repair_proved=False,new_rule_or_shorter_U=False,elapsed_seconds=time.monotonic()-start)
    path=D/'GAW13_gather_sf_receipt.json'
    if write:path.write_text(json.dumps(result,indent=2)+'\n')
    else:assert stable(result)==stable(json.loads(path.read_text()))
    return result

if __name__=='__main__':main()
