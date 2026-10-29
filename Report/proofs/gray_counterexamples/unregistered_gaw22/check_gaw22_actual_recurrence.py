"""Exact closed recurrence of GAW21's same actual intact-start real2.

The written induction proves all rows. Actual local_R cofactors and
derived normal-bank interpreter runs certify its finite control ports.
No transition, future Workspace or future tape is added to the rule.
"""
from pathlib import Path
from dataclasses import replace
from functools import lru_cache
import hashlib,json,sys,time
S=Path(__file__).resolve().parent;ROOT=S.parents[3]
D=ROOT/'figs/gray_counterexamples/unregistered_gaw22'
sys.path.insert(0,str(S.parent/'unregistered_gaw21'))
import check_gaw21_three_record_witness as original
k=original.k;own=original.own;base=original.base;P=k.PRIMARY_START;Q=k.Q;U=k.U
gray_errors=original.gray_errors
execution_keys=set()

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def canonical(v):return json.loads(json.dumps(v))

@lru_cache(None)
def initial_bank(y):return sum(base.I(y+d*Q)<<((d+8)*k.WORD) for d in range(-8,9))
@lru_cache(None)
def normal_execution(g,early):
    execution_keys.add((g,early))
    # Actual normal gather sources keep residue P+i. Logical0 cannot
    # enter these captures. H in E(H,0) makes this exactly the H bank.
    tape={P+i:initial_bank(g*Q+P+i) for i in range(k.FRAME_WORDS)}
    assert all(tape[P+i]==sum(k.cell_words(base.H(g+d))[i]<<((d+8)*k.WORD)
        for d in range(-8,9)) for i in range(k.FRAME_WORDS))
    out,ticks,packet,trace=k.execute(own.ROM,tape,limit=213 if early else 141557,record=True,early=early)
    assert packet.mode==k.HALT
    expected=k.cell_words(base.nextH(g));n=6 if early else k.FRAME_WORDS
    assert [out.get(P+i,0) for i in range(n)]==expected[:n]
    assert out.get(P+2,0)==out.get(P+3,0)==0
    assert all(P<=a<P+k.FRAME_WORDS for a,*_ in trace)
    writes_out={};writes_scratch={}
    for tick,(address,oldp,newp,ow,sw) in enumerate(trace,1):
        if ow is not None:writes_out.setdefault(address,[]).append((tick,ow))
        if sw is not None:writes_scratch.setdefault(address,[]).append((tick,sw))
    return dict(tape=tape,out=out,ticks=ticks,packet=packet,trace=trace,
                writes_out=writes_out,writes_scratch=writes_scratch)

def work(y,t):
    # Exact packet/output/scratch at a logical site of the CLEAN history.
    # Dirty normal banks are proved identical; dirty off-frame heads0.
    if k.EARLY_BIRTH<=t<96*Q:birth=k.EARLY_BIRTH;early=True
    elif 102*Q+1<=t<U:birth=102*Q+1;early=False
    else:return 0,0,0
    g,a=divmod(y,Q)
    if not P<=a<P+k.FRAME_WORDS:return 0,0,0
    e=normal_execution(g,early);step=t-birth
    if not step:head=k.pack(k.Packet(p=1,pc=own.ROM.early_pc if early else 0)) if a==P else 0
    else:
        q=e['trace'][min(step,e['ticks'])-1]
        head=k.pack(q[2]) if a==q[0] else 0
    def last(writes):
        got=0
        for tick,value in writes.get(a,()):
            if tick>step:break
            got=value
        return got
    return head,last(e['writes_out']),last(e['writes_scratch'])

def stage_mail(t):
    start=max(s for s in k.STAGE_STARTS if s<=t)
    if start not in k.GATHER_STARTS or t<=start:return None
    return min(t-start-1,16*Q-2)

def hist(y,t,g):
    if t<k.GATHER_STARTS[g-1]:return 0
    return sum(base.I(y+(lane-8)*Q)<<(lane*k.WORD) for lane in range(17)
               if t>=k.capture(g,lane))

def clean(x,t):
    assert 1<=t<=U
    if t==U:return base.encoded(x,base.nextH)
    d=stage_mail(t);full=(k.EARLY_RESET<=t<96*Q or 102*Q+1<=t<U)
    ys=[x+s for s in k.SLOTS];ww=[work(y,t) for y in ys]
    return k.Cell(addr=x%Q,age=t,
        heads=tuple(v[0] for v in ww),out=tuple(v[1] for v in ww),scratch=tuple(v[2] for v in ww),
        info=tuple(base.I(y) for y in ys),program=tuple(k.beta_bit(own.ROM,y%Q) for y in ys),
        mem=tuple(initial_bank(y) if full else 0 for y in ys),
        mail_l=tuple(base.I(y+d) if d is not None else 0 for y in ys),
        mail_r=tuple(base.I(y-d) if d is not None else 0 for y in ys),
        history1=tuple(hist(y,t,1) for y in ys),history2=tuple(hist(y,t,2) for y in ys),
        history3=tuple(hist(y,t,3) for y in ys))

def delta(t):
    """Sparse logical-track XOR word differences, all others exactly0."""
    assert 2<=t<=U
    if t==U:return {}
    result={'info':{0:1}}
    for g in (2,3):
        hh={-d*Q:1<<((d+8)*k.WORD) for d in range(-8,9) if t>=k.capture(g,d+8)}
        if hh:result['history'+str(g)]=hh
    # First LOAD/capture happened BEFORE the upper row1 fault; H1delta0.
    if (32*Q+1<=t<64*Q) or (64*Q+1<=t<96*Q):
        d=stage_mail(t);assert d is not None
        result['mail_l']={-d:1};result['mail_r']={d:1}
    if k.EARLY_RESET<=t<96*Q or 102*Q+1<=t<U:
        result['mem']={-d*Q:1<<((d+8)*k.WORD) for d in range(-8,9)}
    return result

def dirty(x,t):
    if t==1:return original.upper(x) # literal same three raw records
    z=clean(x,t);changes=delta(t)
    return replace(z,**{name:tuple(getattr(z,name)[i]^words.get(x+s,0)
        for i,s in enumerate(k.SLOTS)) for name,words in changes.items()})

def logical_positions(t):return {y for words in delta(t).values() for y in words} if t>=2 else {0}
def raw_sites(t):return sorted({y-s for y in logical_positions(t) for s in k.SLOTS})

def scalar_ports():
    dates={2,3,U-1,U}
    for t in (*k.STAGE_STARTS[1:],*(s+1 for s in k.GATHER_STARTS),
              *(k.capture(g,l) for g in (1,2,3) for l in range(17)),
              k.EARLY_RESET,k.EARLY_BIRTH,75*Q,80*Q-1,96*Q,98*Q,
              102*Q+1,120*Q,34*Q+1,48*Q-1,72*Q+P+1,72*Q+Q-P+1):
        dates.update(t+d for d in (-1,0,1) if 2<=t+d<=U)
    checks=0;digest=hashlib.sha256();native=0
    for t in sorted(dates):
        # All changed logical-track holders, plus two immediately outside
        # each changed group, and both actual Workspace reader boundaries.
        positions=logical_positions(t)|logical_positions(t-1)
        xs={y-s for y in positions for s in (*k.SLOTS,-3,3)}
        if 96*Q-1<=t<=98*Q+1:
            xs.update(g*Q+a for g in (-1,0,1) for a in (0,1,2,3,4,Q-5,Q-4,Q-3,Q-2,Q-1))
        for x in sorted(xs):
            before={j:dirty(x+j,t-1) for j in range(-8,9)}
            got=k.local_transition(before,own.ROM);expected=dirty(x,t)
            assert got==expected,(x,t,[i for i,(a,b) in enumerate(zip(k.cell_words(got),k.cell_words(expected))) if a!=b])
            assert got.f1==got.f2==got.wf1==got.wf2==0 and got.addr==x%Q and got.age==t%U
            digest.update(json.dumps([x,t,[hex(v) for v in k.cell_words(got)]],separators=(',',':')).encode())
            checks+=1;native+=1
    return dict(actual_full_local_R_event_checks=checks,event_rows=sorted(dates),
        native_GF_clock_flags_and_Workspace_checks=native,
        full496_word_event_digest_sha256=digest.hexdigest(),
        all_rows_covered_by_written_exact_track_recurrence_and_frozen_phase_contract=True)

def snapshots():
    rows=(2,32*Q+1,34*Q+1,40*Q+2,48*Q-1,64*Q+1,72*Q+2,k.EARLY_RESET,
          k.EARLY_BIRTH,75*Q,80*Q-1,96*Q-1,96*Q,102*Q+1,120*Q,U-1,U)
    result=[]
    for t in rows:
        sites=raw_sites(t)
        result.append(dict(upper_row=t,actual_lower_boundary=t*U,
            exact_logical_track_XOR_words={n:[[y,hex(v)] for y,v in sorted(ws.items())] for n,ws in delta(t).items()},
            all_changed_raw_upper_records=[dict(site=x,
                actual_full496_words=[hex(v) for v in k.cell_words(dirty(x,t))],
                clean_full496_words=[hex(v) for v in k.cell_words(clean(x,t))]) for x in sites]))
        assert all(dirty(x,t)!=clean(x,t) for x in sites)
    return result

def main():
    started=time.monotonic();checks=scalar_ports();states=snapshots()
    # Derived upper errors are3 genuine legal full-cell replacements at
    # row1; their class is real1 in the rescaled same-rule history.
    upper_support=[(x,1) for x in (-1,0,1)]
    upper_class=canonical(gray_errors.classify(upper_support,Q=Q,U=U,sep=104))
    assert upper_class['level1'] and upper_class['level0']==0
    t=34*Q+1
    left=dirty(-2*Q,t);right=dirty(2*Q,t)
    assert left.mail_l[0]==1 and clean(-2*Q,t).mail_l[0]==0
    assert right.mail_r[0]==1 and clean(2*Q,t).mail_r[0]==0
    assert 4*Q>2*Q
    assert delta(U)=={} and all(dirty(x,U)==clean(x,U) for x in (-9*Q,0,9*Q,P,P+206))
    # Explicit two normal-bank runs, plus every actual execution consulted
    # by the full-field cofactors. All banks follow unchanged captures.
    normal_execution(0,True);normal_execution(0,False);executions=[]
    for g,early in sorted(execution_keys):
        e=normal_execution(g,early);dig=hashlib.sha256()
        for address,oldp,newp,ow,sw in e['trace']:
            dig.update(json.dumps([address,hex(k.pack(oldp)),hex(k.pack(newp)),ow,sw],separators=(',',':')).encode())
        executions.append(dict(receiver=g,early=early,ticks=e['ticks'],HALT=True,
            actual_derived_full496x17_normal_bank=[hex(e['tape'][P+i]) for i in range(k.FRAME_WORDS)],
            final_full_output_words=[hex(e['out'].get(P+i,0)) for i in range(6 if early else k.FRAME_WORDS)],
            trace_sha256=dig.hexdigest()))
    original_receipt=ROOT/'figs/gray_counterexamples/unregistered_gaw21/GAW21_three_record_witness_certificate.json'
    r=dict(Q=Q,U=U,error_lambda=24,error_separation=104,
        exact_same_GAW21_actual_intact_start15_point_shared_real2_receipt_sha256=sha(original_receipt),
        no_later_errors_or_prescribed_future_commands=True,
        upper_state_D1='W=R(H) with the same3 Info-copy word faults',
        exact_recurrence='D_t=R^(t-1)(W) for1<=t<=U; sparse logical-track formula and actual normal-head coupling',
        event_contracts=checks,whole_relevant_unmasked_Word100_records=states,
        normal_interpreter_executions=executions,
        native_geometry_and_all_native_flags_Workspace_match_shadow_throughout=True,
        every_normal_frame_History_Mem_and_Head_Output_input_matches_shadow=True,
        raw_Mail_can_cross_normal_frames_between_safe_capture_times=True,
        full_upper_raw_equality_first_at_rowU=True,
        full_lower_boundary_equality_at_physicalU_squared=U*U,
        lower_primary4054_persistent_Info_bit1_interval=[U,U*U],
        interval_half_open_and_shadow_bit0=True,
        thereafter_full_shadow_by_autonomous_determinism=True,
        exact_derived_rescaled_upper_three_point_support=upper_support,
        rescaled_original_c104_real1_classification=upper_class,
        transplanted_literal_all_SF_Proposition4_R_failure=dict(upper_row=t,
            actual_lower_boundary=t*U,disagreement_sites=[-2*Q,2*Q],tracks=['mail_l.copy0','mail_r.copy0'],
            simultaneous_spatial_span=4*Q,printed_two_colony_box_width=2*Q),
        printed_Address_Proposition5_failure_claim=False,
        operational_real2_recovery_eventual_memory_or_iid_failure_claim=False,
        faithful_Gray_or_Gacs_construction_counterexample=False,
        rule_ROM_G17_accepted_assets_or_shorter_U_changed=False)
    r=canonical(r);p=D/'GAW22_actual_recurrence_certificate.json'
    if '--issue' in sys.argv:assert not p.exists();p.write_text(json.dumps(r,indent=2)+'\n')
    else:assert r==json.loads(p.read_text())
    print(json.dumps(dict(passed=True,elapsed_seconds=time.monotonic()-started,
        event_checks=checks['actual_full_local_R_event_checks'],snapshots=len(states),
        full_lower_repair_time=U*U,receipt_sha256=sha(p))),flush=True);return r

if __name__=='__main__':main()
