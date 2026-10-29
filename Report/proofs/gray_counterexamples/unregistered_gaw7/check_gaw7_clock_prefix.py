"""Actual reset/source-cone and exact binary-clock quotient audit for GAW7.

The universal statement is a native-prefix theorem only. It does not
simulate prepared History as an independently chosen physical input.
"""
from pathlib import Path
from dataclasses import replace
import ctypes,csv,hashlib,json,random,sys,time
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'Report/proofs/gray_counterexamples/unregistered_gaw6'))
import check_gaw6_actual_bank_map as prior
base=prior.base;k=base.k;own=base.own
S=Path(__file__).resolve().parent;D=ROOT/'figs/gray_counterexamples/unregistered_gaw7'
Q,U,P=k.Q,k.U,k.PRIMARY_START

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def distance(y,residue):
    p=(y-residue)%Q
    return min(p,Q-p)

def native_matrix():
    lib=ctypes.CDLL(str(D/'gaw7_clock_events.so'))
    lib.gaw7_cofactor.argtypes=[ctypes.c_uint,ctypes.c_uint,ctypes.c_int]
    lib.gaw7_cofactor.restype=ctypes.c_uint
    checks=0;signature=hashlib.sha256()
    phases=list(range(5))+[5]+list(range(Q-5,Q))
    # The left old Flag1 and centre old Age are irrelevant to the
    # displayed factor; both five-neighbour Age majorities always exist.
    for p in phases:
        for labels in range(1<<10):
            for flags in range(64):
                states={};bit=0
                for j in range(-5,6):
                    label=(labels>>bit)&1 if j else 0
                    if j:bit+=1
                    f=(flags>>5)&1 if not j else (flags>>(j-1))&1 if j>0 else 0
                    states[j]=dict(addr=(p+j)%Q,age=0 if label else 96*Q,
                        f1=f,f2=0,wf1=0,wf2=0)
                v=lib.gaw7_cofactor(labels,flags,p)
                got=k.predecessor.scalar_native(states)
                expected=dict(addr=p,age=1 if v&1 else 96*Q+1,
                    f1=(v>>1)&1,f2=0,wf1=0,wf2=0)
                assert got==expected,(p,labels,flags,got,expected)
                checks+=1;signature.update(bytes([v]))
        print(json.dumps(dict(native_phase=p,cumulative_actual_scalar_checks=checks)),flush=True)
    # Count equality and modular successor are the only numeric Age uses
    # in this canonical-GF/F2zero factor. Supplement wrap/large-offset
    # correspondence; the written argument quantifies every distinct pair.
    rng=random.Random(0x7c104);wrap_checks=0
    for theta,phi in ((U-1,0),(0,U-1),(U//2,0),(U-2,U-1),(96*Q,72*Q+3)):
        for p in phases:
            for case in range(32):
                labels=rng.randrange(1<<10);flags=rng.randrange(64);v=lib.gaw7_cofactor(labels,flags,p)
                states={};bit=0
                for j in range(-5,6):
                    z=(labels>>bit)&1 if j else 0
                    if j:bit+=1
                    f=(flags>>5)&1 if not j else (flags>>(j-1))&1 if j>0 else rng.randrange(2)
                    states[j]=dict(addr=(p+j)%Q,age=phi if z else theta,f1=f,f2=0,wf1=0,wf2=0)
                got=k.predecessor.scalar_native(states)
                assert got==dict(addr=p,age=((phi if v&1 else theta)+1)%U,
                    f1=(v>>1)&1,f2=0,wf1=0,wf2=0)
                wrap_checks+=1
    return dict(exhaustive_actual_scalar_checks=checks,all_ten_label_and_six_Flag1_bits=True,
        all_inside_predicate_classes=True,signature_sha256=signature.hexdigest(),
        supplementary_modular_wrap_checks=wrap_checks)

def signal_cofactors():
    rng=random.Random(0x7a8192);checks=0;signature=hashlib.sha256()
    names=base.NAMES
    for t in (0,1,16,2736,3843,3844):
        for centre in list(range(5))+list(range(Q-5,Q)):
            for case in range(8):
                cells={}
                for x in range(centre-8,centre+9):
                    fields={}
                    for name in names:
                        width=2200 if name=='heads' else 1700 if name in ('mem','history1','history2','history3') else 100
                        vals=[]
                        for offset in k.SLOTS:
                            y=x+offset;v=rng.getrandbits(width)
                            if name in ('heads','out') and distance(y,P)>t:v=0
                            if name=='courier_l' and distance(y,P+3)>t:v=0
                            if name=='courier_r' and distance(y,P+2)>t:v=0
                            if name=='info' and y%Q in (3,Q-3):v=0
                            vals.append(v)
                        fields[name]=tuple(vals)
                    cells[x]=k.Cell(addr=x%Q,age=rng.randrange(U),
                        f1=rng.randrange(2),f2=rng.randrange(2),wf1=rng.randrange(2),wf2=rng.randrange(2),**fields)
                new=k.local_transition({j:cells[centre+j] for j in range(-8,9)},own.ROM)
                assert new.addr==centre%Q and new.wf1==new.wf2==0
                for h,offset in enumerate(k.SLOTS):
                    y=centre+offset
                    if y%Q in (3,Q-3):assert new.info[h]==0
                    if distance(y,P)>t+1:assert new.heads[h]==new.out[h]==0
                    if distance(y,P+3)>t+1:assert new.courier_l[h]==0
                    if distance(y,P+2)>t+1:assert new.courier_r[h]==0
                checks+=1;signature.update(json.dumps(k.cell_words(new),separators=(',',':')).encode()+b'\n')
    return dict(actual_total_local_R_checks=checks,arbitrary_native_Age_and_flags_in_cone_checks=True,
        other_raw_private_fields_free=True,head_Out_courier_cone_premises_explicit=True,
        actual_source_WF_zero_checked=True,signature_sha256=signature.hexdigest())

def actual_faults():
    starts=(0,1,2,3,P-8,Q-16,Q-8,Q-1)
    phases=(0,1,96*Q-1,U-1,72*Q+3,75*Q-1,80*Q-2,102*Q)
    cases=[];first_checks=0
    for b in starts:
        support={(x,96*Q) for x in range(b,b+16)}
        cl=base.gray_errors.classify(support,support,Q=Q,U=U,sep=104)
        assert cl['level0']==0 and cl['level1'] and cl['extent']==(16,1)
        for phi in phases:
            cells={x:prior.row96(x) for x in range(b-24,b+40)};payload=[]
            for x in range(b,b+16):
                old=cells[x];new=replace(old,age=phi)
                assert all(getattr(old,n)==getattr(new,n) for n in old.__dataclass_fields__ if n!='age')
                cells[x]=new;payload.append(dict(x=x,t=96*Q,old_words=[hex(v) for v in k.cell_words(old)],
                    replacement_words=[hex(v) for v in k.cell_words(new)]))
            first=[]
            for x in range(b-8,b+24):
                actual=k.local_transition({j:cells[x+j] for j in range(-8,9)},own.ROM)
                native=k.predecessor.scalar_native({j:{n:getattr(cells[x+j],n) for n in k.NATIVE_NAMES} for j in range(-5,6)})
                assert [getattr(actual,n) for n in k.NATIVE_NAMES]==[native[n] for n in k.NATIVE_NAMES]
                assert actual.addr==x%Q and actual.f2==actual.wf1==actual.wf2==0
                first_checks+=1;first.append([x,[getattr(actual,n) for n in k.NATIVE_NAMES]])
            cases.append(dict(start=b,replacement_Age=phi,support=sorted(support),classification=cl,
                whole_cell_payloads=payload,actual_first_native_row=first,
                only_raw_Age_changed=True,no_later_errors=True))
    return dict(cases=cases,actual_first_row_checks=first_checks,
        initial_row='actual GAW2R row96Q from frozen intact H, three actual retained banks',
        independent_prepared_history_assumed=False)

def events():
    table=list(csv.DictReader((D/'clock_uniform_width16.csv').open()))
    assert len(table)==Q
    count=0;worst_clock=worst_flags=0;worst=[]
    for b,r in enumerate(table):
        v={name:int(value) for name,value in r.items()}
        assert v['b']==b and v['width']==16
        assert 1<=v['clock_recovery']<=2736 and v['clock_recovery']<=v['flag_recovery']<=6831
        assert v['max_segments']<=6
        lo,hi=v['min_hull'],v['max_hull'];cols=set(range(lo//Q,(hi-1)//Q+1))
        assert len(cols)<=2 and cols in ({-1,0},{0},{0,1})
        assert lo<=b and b+16<=hi
        count+=v['event_checks'];worst_clock=max(worst_clock,v['clock_recovery']);worst_flags=max(worst_flags,v['flag_recovery'])
        if v['clock_recovery']==2736:worst.append(b)
    assert (count,worst_clock,worst_flags)==(1064790382,2736,6831)
    assert worst==[1,2]
    return dict(all_Q_colony_phases=Q,uniform_error_sites=16,event_segments_checked=count,
        maximum_clock_recovery=worst_clock,maximum_native_quiet=worst_flags,
        worst_clock_phases=worst,fixed_adjacent_colony_pair_for_entire_native_trajectory=True,
        maximum_simultaneous_segment_count=6,table_sha256=sha(D/'clock_uniform_width16.csv'))

def main(write=True):
    start=time.monotonic()
    result=dict(name='GAW7 actual uniform Age-only original-real1 native prefix',Q=Q,U=U,
        error_lambda=24,error_separation=104,native_factor=native_matrix(),
        source_cone_cofactors=signal_cofactors(),selected_actual_faults=actual_faults(),all_phase_events=events(),
        universal_replacement_Age_range=[0,U-1],unchanged_replacement_Age_excluded=96*Q,
        all_integer_colony_translates_proved=True,actual_shared_history_from_intact_H=True,
        actual_WF_zero_derived_not_selected=True,actual_native_recovery_by_96Q_plus6831=True,
        no_physical_later_errors=True,arbitrary_mixed_Age_payloads_recovery_proved=False,
        physical_History_head_late_output_or_decoded2U_map_proved=False,
        original_Gray_or_G17_construction_refuted=False,iid_or_shorter_U_proved=False,
        changed_rule_or_constants=False,main_registered_docs_modified=False,
        elapsed_seconds=time.monotonic()-start)
    p=D/'GAW7_clock_prefix_receipt.json'
    if write:p.write_text(json.dumps(result,indent=2)+'\n')
    else:
        old=json.loads(p.read_text());old.pop('elapsed_seconds');current=dict(result);current.pop('elapsed_seconds')
        assert json.loads(json.dumps(current))==old
    print(json.dumps(dict(passed=True,maximum_clock=2736,maximum_native_quiet=6831,
        actual_scalar_checks=result['native_factor']['exhaustive_actual_scalar_checks'],
        actual_total_local_R_checks=result['source_cone_cofactors']['actual_total_local_R_checks'],
        actual_fault_cases=len(result['selected_actual_faults']['cases']),
        actual_WF_derived=True,whole_period_or_Gray_failure=False,elapsed_seconds=time.monotonic()-start)),flush=True)
    return result

if __name__=='__main__':main()
