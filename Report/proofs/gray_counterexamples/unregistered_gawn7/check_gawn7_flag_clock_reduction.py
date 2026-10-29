"""Finite supplements to GAWN7's written universal native reductions.

No native trajectory or physical period is simulated; the two-update
prefix checks are exact local full-kernel comparisons only.
"""
from pathlib import Path
from dataclasses import replace
import argparse,hashlib,json,random,sys,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(HERE.parent/'unregistered_gawn2'))
import small_rule_gawn2 as k
import small_compositional_cost as own
T=100*k.Q+2;L=4*k.Q;T0=3*k.Q+1
NATIVE=('addr','age','f1','f2','wf1','wf2')
SF=('heads','mem','out','info','scratch','program','courier_l','courier_r',
    'mail_l','mail_r','history1','history2','history3')
WIDTHS=dict(heads=k.HEAD_BITS,mem=17*k.WORD,history1=17*k.WORD,
            history2=17*k.WORD,history3=17*k.WORD)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def majority(values,fallback):
    for value in values:
        if values.count(value)>=3:return value
    return fallback
def add(dig,row):dig.update((json.dumps(row,separators=(',',':'))+'\n').encode())
def physical(rng,x,age):
    return k.Cell(addr=x%k.Q,age=age,f1=rng.randrange(2),
        **{name:tuple(rng.getrandbits(WIDTHS.get(name,k.WORD)) for _ in k.SLOTS) for name in SF})

def bulk():
    rng=random.Random(0x4741574e3701);dig=hashlib.sha256();branches={0:0,1:0};count=0
    phases=(5,6,7,17,k.Q-6,k.Q-5,k.Q-4,k.Q-3,k.Q-2,k.Q-1)
    for index in range(1200):
        a=phases[index%len(phases)];values=[rng.randrange(k.U) for _ in range(5)]
        c={j:dict(addr=(a+j)%k.Q,age=values[rng.randrange(len(values))],
             f1=rng.randrange(2),f2=0,wf1=rng.randrange(2),wf2=0) for j in range(-5,6)}
        if index%4==0:
            for j in range(-5,6):c[j]['wf1']=0
        out=k.scalar_native(c);expected=(majority([c[j]['age'] for j in range(-1,-6,-1)],c[0]['age'])+1)%k.U
        assert out['f2']==0 and out['age']==expected,(index,c,out,expected)
        branches[out['f1']]+=1
        add(dig,[a,[[c[j][n] for n in NATIVE] for j in range(-5,6)],[out[n] for n in NATIVE]])
        count+=1
    assert all(branches.values()),branches
    return dict(selected_cases=count,computed_F1_branch_counts={str(key):value for key,value in branches.items()},
        arbitrary_word_quantifier_proved_by_three_equal_left_words=True,inputs_outputs_sha256=dig.hexdigest())

def zero_front():
    rng=random.Random(0x4741574e3702);dig=hashlib.sha256();count=0
    phases=(0,1,2,3,4,5,6,17,k.Q-1)
    for a in phases:
        for selfbit in range(2):
            for rightmask in range(32):
                c={j:dict(addr=(a+j)%k.Q,age=rng.randrange(k.U),f1=rng.randrange(2),
                    f2=0,wf1=rng.randrange(2),wf2=0) for j in range(-5,6)}
                c[0]['f2']=selfbit
                for j in range(1,6):c[j]['f2']=(rightmask>>(j-1))&1
                out=k.scalar_native(c);assert out['f2']==0,(a,selfbit,rightmask,out)
                add(dig,[a,[[c[j][n] for n in NATIVE] for j in range(-5,6)],[out[n] for n in NATIVE]])
                count+=1
    return dict(selected_native_cases=count,left_Flag2_all_zero=True,old_Workspace2_all_zero=True,
        h1_required=True,inputs_outputs_sha256=dig.hexdigest())

def suffix():
    dig=hashlib.sha256();count=0;a=T+T0+1364
    lengths=(0,1,2,3,4,5,k.Q-5,k.Q-4,k.Q-3,k.Q-2,k.Q-1)
    for length in lengths:
        edge=k.Q-length
        for x in (edge-1,edge-2):
            if x<0:continue
            for mask in range(64):
                c={j:dict(addr=(x+j)%k.Q,age=a,f1=0,f2=0,wf1=0,wf2=0) for j in range(-5,6)}
                for j in range(-5,6):
                    y=x+j;c[j]['f1']=0 if edge<=y<k.Q else ((mask>>(j%6))&1)
                out=k.scalar_native(c);assert out['f1']==0 and out['age']==a+1,(length,x,mask,out)
                add(dig,[length,x,mask,[out[n] for n in NATIVE]]);count+=1
    return dict(selected_native_cases=count,selected_suffix_lengths=list(lengths),
        both_preceding_targets_checked=True,inputs_outputs_sha256=dig.hexdigest())

def full_prefix():
    rng=random.Random(0x4741574e3703);dig=hashlib.sha256();count=0;site2_bad=0
    a=T+T0
    for index in range(32):
        state={}
        for x in range(-16,29):
            age=(a if x<5 else a+17) if index==0 else a if x<5 or rng.randrange(3)==0 else a+1+rng.randrange(63)
            cell=physical(rng,x,age)
            state[x]=replace(cell,f1=0) if index==0 else cell
        first={x:k.local_transition({j:state[x+j] for j in range(-8,9)},own.ROM)
               for x in range(-8,21)}
        second={x:k.local_transition({j:first[x+j] for j in range(-8,9)},own.ROM)
                for x in range(11)}
        assert all(first[x].age==a+1 for x in (0,1,3,4,5,6,7))
        site2_bad+=first[2].age!=a+1
        assert all(second[x].age==a+2 for x in range(11))
        assert all(c.f2==c.wf1==c.wf2==0 for c in first.values())
        row=[index,[[hex(v) for v in k.cell_words(state[x])] for x in range(-16,29)],
            [[getattr(first[x],n) for n in NATIVE] for x in range(11)],
            [[getattr(second[x],n) for n in NATIVE] for x in range(11)]]
        add(dig,row);count+=1
    assert site2_bad>=1,'missing actual first-update site2 transient cofactor'
    return dict(selected_two_update_cones=count,initial_first5_reference_clocks=True,
        first_update_site2_wrong_count=site2_bad,initial_all13_SF_arbitrary=True,
        actual_five_holder_physical_kernel=True,radius8_two_update_cone_complete=True,
        inputs_outputs_sha256=dig.hexdigest(),evolving_full_colony_recovery_experiment=False)

def workspace():
    rng=random.Random(0x4741574e3704);dig=hashlib.sha256();count=0
    phases=(0,1,2,3,4,5,k.Q-6,k.Q-5,k.Q-4,k.Q-3,k.Q-2,k.Q-1)
    ages=(98*k.Q-1,98*k.Q,T+2*k.Q+1,k.U-2)
    for a in phases:
        for age in ages:
            state={j:physical(rng,a+j,age) for j in range(-8,9)}
            out=k.local_transition(state,own.ROM)
            assert out.age==age+1 and out.wf1==out.wf2==0,(a,age,out)
            add(dig,[a,age,[[hex(v) for v in k.cell_words(state[j])] for j in range(-8,9)],
                [getattr(out,n) for n in NATIVE]]);count+=1
    return dict(selected_actual_full_kernel_cases=count,selected_computed_guard_clocks=list(ages),
        arbitrary_Info_and_other_SF=True,inputs_outputs_sha256=dig.hexdigest())

def compute():
    b=bulk();z=zero_front();s=suffix();p=full_prefix();w=workspace()
    clock_updates=2+(k.Q-11+2)//3;f1_updates=(k.Q+1)//2
    quiet=T0+clock_updates+f1_updates
    assert (T0,clock_updates,f1_updates,quiet,L-quiet)==(12289,1364,2048,15701,683)
    sources=[Path(__file__),HERE/'GAWN7_FLAG2_DEADLINE_AND_FIVE_CLOCK_REDUCTION.md',
             HERE.parent/'unregistered_gawn2/small_rule_gawn2.py',
             HERE.parent/'unregistered_gawn2/small_compositional_cost.py']
    return dict(name='GAWN7 unchanged GAWN2 universal native component deadlines and conditional five-clock reduction',
        passed=True,Q=k.Q,U=k.U,lambda_original=24,error_separation=104,
        fault_row=T,retained_Address_required=True,Age_interval=[96*k.Q-1,k.U-L-1],
        no_later_errors=True,universal_Workspace_zero_row=2*k.Q+1,
        universal_Flag2_zero_row=T0,bulk_clock_identity_Address_minimum=5,
        correct_first5_actual_raw_clocks_at_T_plus_3Q_plus1_REQUIRED=True,
        remaining_clock_updates_bound=clock_updates,remaining_Flag1_updates_bound=f1_updates,
        conditional_full_native_quiet_row=quiet,margin_before4Q=L-quiet,
        conditional_complete2U_for_only_Age_flags_Info_faults=True,
        first5_clock_premise_for_every_payload_proved=False,
        universal_full_native_quiet_deadline_proved=False,
        new_native_quiet_trajectory_or_full2U_simulation=False,
        GF_changing_E0_surroundings_higher_iid=False,faithful_Gray_G17_refutation_or_minimum=False,
        rule_ROM_constants_G17_changed=False,
        bulk_clock_identity=b,Flag2_zero_front=z,Flag1_suffix=s,
        physical_prefix_supplements=p,Workspace_guard_supplements=w,
        source_sha256={str(path.relative_to(ROOT)):sha(path) for path in sources})

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--outdir',type=Path,
        default=ROOT/'figs/gray_counterexamples/unregistered_gawn7');args=parser.parse_args()
    started=time.monotonic();d=compute();args.outdir.mkdir(parents=True,exist_ok=True)
    (args.outdir/'GAWN7_flag_clock_certificate.json').write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(passed=True,bulk_cases=d['bulk_clock_identity']['selected_cases'],
        F2_front_cases=d['Flag2_zero_front']['selected_native_cases'],
        F1_suffix_cases=d['Flag1_suffix']['selected_native_cases'],
        physical_prefix_cones=d['physical_prefix_supplements']['selected_two_update_cones'],
        full_Workspace_cases=d['Workspace_guard_supplements']['selected_actual_full_kernel_cases'],
        conditional_native_quiet=d['conditional_full_native_quiet_row'],
        first5_premise_unproved=True,full_reliability=False,elapsed=time.monotonic()-started)),flush=True)
if __name__=='__main__':main()
