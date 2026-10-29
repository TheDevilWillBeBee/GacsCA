"""GAW3: original-E0 geometry/fronts and an actual encoded WF wake.

Uses frozen GAW2R unchanged. Whole-word and infinite-line induction are
proved in the companion document; this checks the actual reduced equations.
"""
from pathlib import Path
from dataclasses import replace
from itertools import product,combinations
import sys,json,time,hashlib
ROOT=Path(__file__).resolve().parents[4]
P=ROOT/'Report/proofs/gray_counterexamples/unregistered_gaw2'
sys.path.insert(0,str(P));sys.path.insert(0,str(ROOT))
import gray_three_gather_gaw2r as k
import gaw2r_compositional_cost as own
from gacsca import gray_errors
D=ROOT/'figs/gray_counterexamples/unregistered_gaw3'
FIVE_FIELDS=('heads','mem','out','info','scratch','program','courier_l','courier_r','mail_l','mail_r','history1','history2','history3')

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def metric_and_votes():
    # Any two points in the actual radius8 two-row cone are linked(24,24).
    points=list(product(range(-8,9),(-1,0)))
    pairs=list(combinations(points,2))
    assert all(abs(x-y)<24 and abs(t-u)<24 for (x,t),(y,u) in pairs)
    count=0;holders={y:tuple(y-s for s in k.SLOTS) for y in range(-3,4)}
    for y,group in holders.items():
        assert len(set(group))==5 and min(group)>=-5 and max(group)<=5
        for size in range(3):
            for support in combinations(range(5),size):
                for payload in product((0,1),repeat=size):
                    for correct in (0,1):
                        bits=[correct]*5
                        for i,v in zip(support,payload):bits[i]=v
                        assert k.vote(bits)==correct;count+=1
    exclusions=[(dt,2*dt+4) for dt in range(1,10)]
    assert all(dt<24 and dx<24 for dt,dx in exclusions)
    rows=next(n for n in range(k.Q+1) if 2*(n-(n+9)//10)>=k.Q)
    assert rows==4552
    return dict(cone_pair_metric_checks=len(pairs),cone_spatial_diameter=16,cone_tick_diameter=1,
        actual_vote_holders=holders,exhaustive_majority_bit_patterns=count,
        charge_exclusions=exclusions,charge_spacing=10,sweep_updates=rows,
        quiet_row=98*k.Q+2*rows,quiet_before_R_birth=98*k.Q+2*rows<102*k.Q)


def front_cofactors():
    phases=sorted({0,k.Q}|set(range(1,6))|set(range(k.Q-5,k.Q)))[:-1]
    reduced_cases=payload_cases=0
    for which,positions in (('f1',(0,-1,-2)),('f2',(0,1,2))):
        for delta in positions:
            for pair in (None,*range(-6,6)):
                fault=set() if pair is None else {pair,pair+1}
                strip=set(range(-delta,5-delta)) if which=='f1' else set(range(-4-delta,1-delta))
                if delta and fault&strip:continue
                local=sorted(fault&set(range(-5,6)))
                for phase in phases:
                    reduced_cases+=1
                    for values in product(range(16),repeat=len(local)):
                        cells={}
                        for x in range(-5,6):
                            flags=dict(f1=int(delta+x<0),f2=1,wf1=0,wf2=0) if which=='f1' else dict(f1=0,f2=int(delta+x>0),wf1=0,wf2=0)
                            cells[x]=dict(addr=(phase+x)%k.Q,age=0,**flags)
                        for x,value in zip(local,values):
                            for i,name in enumerate(('f1','f2','wf1','wf2')):cells[x][name]=(value>>i)&1
                        result=k.predecessor.scalar_native(cells)
                        assert result[which]==0,(which,delta,pair,phase,values,result)
                        if which=='f2':assert result['f1']==0
                        assert result['addr']==phase and result['age']==1
                        payload_cases+=1
    assert reduced_cases==616
    return dict(reduced_native_front_cases=reduced_cases,exhaustive_replacement_flag_payloads=payload_cases,
        native='actual inherited h1 scalar_native',GF_Age_payload_independence='proved three-correct-word lemma',
        clock_independence='with restored geometry, common clock cancels all mismatch predicates and source3 is false')


def upper(g):
    # Fully specified arbitrary raw upper configuration, not a preloaded bank.
    return k.Cell(addr=g%k.Q,age=0,f1=1)


def input_Info(y):
    g,a=divmod(y,k.Q)
    if k.PRIMARY_START<=a<k.PRIMARY_START+k.FRAME_WORDS:return k.cell_words(upper(g))[a-k.PRIMARY_START]
    return k.MASK


def upper_flags(g):
    return k.native_at({j:upper(g+j) for j in range(-8,9)})


def prefix_Info(y):
    g,a=divmod(y,k.Q)
    if a==3:return upper_flags(g)['f2']
    if a==k.Q-3:return upper_flags(g)['f1']
    return input_Info(y)


def early_evaluations():
    records=[]
    for g in (-1,0,1):
        cells={j:upper(g+j) for j in range(-8,9)}
        out,ticks,head,trace=k.execute(own.ROM,k.input_tape(cells),early=True,record=True)
        expected=k.native_at(cells)
        assert head.mode==k.HALT and ticks<=213
        assert [out[k.PRIMARY_START+i] for i in range(6)]==[expected[n] for n in k.NATIVE_NAMES]
        assert set(out)==set(range(k.PRIMARY_START,k.PRIMARY_START+6))
        assert min(t[0] for t in trace)==k.PRIMARY_START and max(t[0] for t in trace)==k.PRIMARY_START+5
        assert all(t[4] is None for t in trace)
        records.append(dict(colony=g,updates=ticks,native_output=expected,head_min=k.PRIMARY_START,head_max=k.PRIMARY_START+5,Scratch_writes=0))
    return records


def initial_cell(x):
    return k.Cell(addr=x%k.Q,age=0,info=tuple(input_Info(x+s) for s in k.SLOTS),
        program=tuple(k.beta_bit(own.ROM,(x+s)%k.Q) for s in k.SLOTS))


def derived_pre96(x):
    # This finite cone is outside every normal primary/head/Scratch frame.
    # All three captures at its unused residue read initial A=MASK, before80Q.
    for s in k.SLOTS:
        for j in range(-8,9):assert input_Info(x+s+j*k.Q)==k.MASK
    g,a=divmod(x,k.Q);full=(1<<(17*k.WORD))-1
    return k.Cell(addr=a,age=96*k.Q-1,info=tuple(prefix_Info(x+s) for s in k.SLOTS),
        program=tuple(k.beta_bit(own.ROM,(x+s)%k.Q) for s in k.SLOTS),
        mem=(full,)*5,history1=(full,)*5,history2=(full,)*5,history3=(full,)*5,
        mail_l=(k.MASK,)*5,mail_r=(k.MASK,)*5,
        courier_r=tuple(upper_flags((x+s)//k.Q)['f1'] if (x+s)%k.Q==k.Q-3 else 0 for s in k.SLOTS))


def update(state):
    return {x:k.local_transition({j:state[x+j] for j in range(-8,9)},own.ROM)
        for x in range(min(state)+8,max(state)-7)}


def words(state):return [[x,[hex(v) for v in k.cell_words(c)]] for x,c in sorted(state.items())]


def wave_witness(write):
    point=k.Q-3;tick=96*k.Q+1
    initial={x:initial_cell(x) for x in range(point-48,point+49)}
    pre96={x:derived_pre96(x) for x in initial}
    row96=update(pre96)
    for x,c in row96.items():
        g,a=divmod(x,k.Q)
        assert c.addr==a and c.age==96*k.Q and c.f1==c.f2==0
        assert c.wf1==int(a>=k.Q-5 and upper_flags(g)['f1']) and c.wf2==0
        assert all(getattr(c,n)==(0,)*5 for n in ('heads','mem','out','scratch','courier_l','courier_r','mail_l','mail_r'))
    row=update(row96)
    for x,c in row.items():
        g,a=divmod(x,k.Q)
        assert c.addr==a and c.age==tick and c.f1==int(a>=k.Q-8 and upper_flags(g)['f1']) and c.f2==0
    assert k.logical({j:row[point+j] for j in range(-8,9)},'info',0)==1
    error=replace(row[point],addr=(row[point].addr+1)%k.Q)
    noisy=dict(row);noisy[point]=error
    support={(point,tick)}
    assert gray_errors.level0_points(support)==support
    classification=gray_errors.classify(support,support,Q=k.Q,U=k.U,sep=104)
    assert classification['level0']==1 and not classification['candidate_level1'] and not classification['level1']
    clean1=update(row);noisy1=update(noisy)
    gap=[x for x in clean1 if noisy1[x].wf1!=clean1[x].wf1]
    assert gap==list(range(k.Q-5,k.Q))
    assert all(clean1[x].wf1==1 and noisy1[x].wf1==0 for x in gap)
    assert noisy1[point].addr==point and noisy1[point].f1==1
    assert noisy1[point].info==(0,)*5 and clean1[point].info!=(0,)*5
    sf_gap=[x for x in clean1 if any(getattr(noisy1[x],n)!=getattr(clean1[x],n) for n in FIVE_FIELDS)]
    assert sf_gap==[point]
    corrected=k.logical({j:noisy1[point+j] for j in range(-8,9)},'info',0)
    assert corrected==1
    clean2=update(clean1);noisy2=update(noisy1)
    assert all(all(getattr(noisy2[x],n)==getattr(clean2[x],n) for n in FIVE_FIELDS) for x in clean2)
    assert all(noisy2[x].wf1==clean2[x].wf1 for x in clean2)
    result=dict(name='GAW2R actually encoded GF-only original-E0 WF discrepancy',
        Q=k.Q,U=k.U,start='global E(C,A): C[g]=Cell(addr=g modQ,Age0,Flag1one,all other fields0); A=WORD100_MASK',
        initial_local_words=words(initial),derived_pre96_words=words(pre96),
        forward_prefix_rows=[words(row96),words(row)],
        error=dict(x=point,t=tick,replaced_raw_words=[hex(v) for v in k.cell_words(error)],only_changed_field='Address8189->8190'),
        original_error_classification=classification,
        clean_rows=[words(clean1),words(clean2)],noisy_rows=[words(noisy1),words(noisy2)],
        computed_WF_disagreement_sites=gap,SF_wake_sites=sf_gap,voted_Info_after_wake=corrected,
        actual_global_prefix_proved_by_reset_capture_and_courier_induction=True,
        recursively_intact_start_claimed=False,period_or_Gray_or_iid_counterexample=False)
    if write:(D/'GAW3_E0_WF_witness.json').write_text(json.dumps(result,indent=2)+'\n')
    else:assert json.loads(json.dumps(result))==json.loads((D/'GAW3_E0_WF_witness.json').read_text())
    return dict(error_support=[[point,tick]],WF_gap_sites=gap,SF_wake_sites=sf_gap,
        next_row_all_SF_and_WF_rejoin=True,original_E0=True,recursive_intact_claim=False)


def main(write=True):
    start=time.monotonic();metric=metric_and_votes();front=front_cofactors();early=early_evaluations();wave=wave_witness(write)
    result=dict(name='GAW3 pure-E0 actual GAW2R contracts',metric=metric,fronts=front,actual_early=early,actual_WF_wake=wave,
        Q=k.Q,U=k.U,error_lambda=24,error_separation=104,
        old_GAW2R_rule_modified=False,measured_evidence_of_iid_failure=False,
        full_error_value_quantifier='all legal native13/20/1-bit and WORD100 SF replacements; GF/Age and word algebra proved separately',
        elapsed_seconds=time.monotonic()-start)
    if write:(D/'GAW3_E0_contracts.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(passed=True,metric=metric,fronts=front,actual_WF_wake=wave,elapsed=result['elapsed_seconds'])))
    return result

if __name__=='__main__':main()
