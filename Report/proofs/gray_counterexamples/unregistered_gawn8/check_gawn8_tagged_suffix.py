"""Finite transcriptions of GAWN8's written universal native proof.

No evolving colony recovery or complete physical period is simulated.
Right correctness/Flag1 masks are exhausted where stated; arbitrary
left words and all histories are covered by the written proof, not samples.
"""
from pathlib import Path
from dataclasses import replace
import argparse,hashlib,itertools,json,random,sys,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(HERE.parent/'unregistered_gawn2'))
import small_rule_gawn2 as k
import small_compositional_cost as own
T=100*k.Q+2;L=4*k.Q;TB=2*k.Q+1
NATIVE=('addr','age','f1','f2','wf1','wf2')
SF=('heads','mem','out','info','scratch','program','courier_l','courier_r',
    'mail_l','mail_r','history1','history2','history3')
WIDTHS=dict(heads=k.HEAD_BITS,mem=17*k.WORD,history1=17*k.WORD,
            history2=17*k.WORD,history3=17*k.WORD)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def add(d,row):d.update((json.dumps(row,separators=(',',':'))+'\n').encode())

def native_row(rng,x,reference):
    row={}
    for j in range(-5,6):
        y=x+j;outside=not 0<=y<k.Q
        row[j]=dict(addr=y%k.Q,age=reference if outside or rng.randrange(3)==0 else 96*k.Q+100+17*rng.randrange(11),
            f1=0 if y>=k.Q else rng.randrange(2),f2=0 if outside else rng.randrange(2),
            wf1=0 if outside else rng.randrange(2),wf2=0 if outside else rng.randrange(2))
    return row

def physical_check(rng,row,x,reference,expected_age,tag_required,dig):
    state={}
    for j in range(-8,9):
        y=x+j
        cell=k.Cell(addr=y%k.Q,age=reference if not 0<=y<k.Q else reference+23,
            **{name:tuple(rng.getrandbits(WIDTHS.get(name,k.WORD)) for _ in k.SLOTS) for name in SF})
        if j in row:cell=replace(cell,**row[j])
        state[j]=cell
    out=k.local_transition(state,own.ROM);native=k.scalar_native(row)
    assert all(getattr(out,name)==native[name] for name in ('addr','age','f1','f2'))
    if expected_age:assert out.age==reference+1
    if tag_required:assert out.age==reference+1 or out.f1==1
    add(dig,[x,[[hex(v) for v in k.cell_words(state[j])] for j in range(-8,9)],
             [getattr(out,name) for name in NATIVE]])

def tagged():
    rng=random.Random(0x4741574e3801);dig=hashlib.sha256();phys=hashlib.sha256()
    count=full=0;reference=T+47
    phases=(0,1,2,3,4,5,k.Q-5,k.Q-4,k.Q-3,k.Q-2,k.Q-1)
    # 0: correct/F1=0; 1: incorrect/F1=1; 2: correct/F1=1.
    for x in phases:
        for pattern in itertools.product(range(3),repeat=5):
            if any(x+j>=k.Q and pattern[j-1]!=0 for j in range(1,6)):continue
            for self_flags in range(4):
                row=native_row(rng,x,reference)
                row[0]['f1']=self_flags&1;row[0]['f2']=(self_flags>>1)&1
                for j,code in enumerate(pattern,1):
                    row[j]['age']=reference if code!=1 else 96*k.Q+100+17*rng.randrange(11)
                    row[j]['f1']=int(code!=0)
                out=k.scalar_native(row)
                assert out['addr']==x and (out['age']==reference+1 or out['f1']==1),(x,pattern,row,out)
                add(dig,[x,list(pattern),[[row[j][n] for n in NATIVE] for j in range(-5,6)],
                         [out[n] for n in NATIVE]])
                if count%97==0:
                    physical_check(rng,row,x,reference,False,True,phys);full+=1
                count+=1
    assert count==6316
    return dict(native_cases=count,all_admitted_right_correctness_Flag1_disjunction_masks_enumerated=True,
        left_words_and_flags_selected_not_exhausted=True,Flag2_Workspace_arbitrary_selected=True,
        full_kernel_cases=full,native_sha256=dig.hexdigest(),full_kernel_sha256=phys.hexdigest())

def first_three():
    rng=random.Random(0x4741574e3802);dig=hashlib.sha256();phys=hashlib.sha256()
    count=full=0;reference=T+TB+2
    for x in range(3):
        for pattern in itertools.product(range(3),repeat=5):
            for self_flags in range(4):
                row=native_row(rng,x,reference)
                for j in range(-5,6):row[j]['wf1']=row[j]['wf2']=0
                for j in range(-5,0):
                    row[j]['f2']=0
                    row[j]['age']=reference if x+j<0 else 96*k.Q+100+17*rng.randrange(11)
                row[0]['f1']=self_flags&1;row[0]['f2']=(self_flags>>1)&1
                for j,code in enumerate(pattern,1):
                    row[j]['age']=reference if code!=1 else 96*k.Q+100+17*rng.randrange(11)
                    row[j]['f1']=int(code!=0)
                out=k.scalar_native(row)
                assert out['addr']==x and out['f2']==0 and out['age']==reference+1,(x,pattern,row,out)
                add(dig,[x,list(pattern),[[row[j][n] for n in NATIVE] for j in range(-5,6)],
                         [out[n] for n in NATIVE]])
                if count%97==0:
                    physical_check(rng,row,x,reference,True,True,phys);full+=1
                count+=1
    assert count==2916
    return dict(native_cases=count,all_right_tag_masks_and_self_Flag1_Flag2_enumerated=True,
        minimum_three_correct_exterior_left_clocks=True,full_kernel_cases=full,
        native_sha256=dig.hexdigest(),full_kernel_sha256=phys.hexdigest())

def prefix():
    rng=random.Random(0x4741574e3803);dig=hashlib.sha256();phys=hashlib.sha256()
    count=full=0;reference=T+TB+7;branches={'right_clear':0,'right_absent':0}
    phases=(3,4,5,6,7,k.Q-6,k.Q-5,k.Q-4,k.Q-3,k.Q-2,k.Q-1)
    for x in phases:
        for pattern in itertools.product(range(3),repeat=5):
            if any(x+j>=k.Q and pattern[j-1]!=0 for j in range(1,6)):continue
            for self_flags in range(4):
                row=native_row(rng,x,reference)
                for j in range(-5,6):row[j]['wf1']=row[j]['wf2']=0
                for j in range(-5,0):row[j]['f2']=0;row[j]['age']=reference
                row[0]['f1']=self_flags&1;row[0]['f2']=(self_flags>>1)&1
                for j,code in enumerate(pattern,1):row[j]['age']=reference if code==0 else 96*k.Q+100+17*code
                right=[row[j]['age'] for j in range(1,6)]
                branches['right_clear' if max(map(right.count,right))>=3 else 'right_absent']+=1
                out=k.scalar_native(row)
                assert out['addr']==x and out['f2']==0 and out['age']==reference+1,(x,pattern,row,out)
                add(dig,[x,list(pattern),[[row[j][n] for n in NATIVE] for j in range(-5,6)],
                         [out[n] for n in NATIVE]])
                if count%97==0:
                    physical_check(rng,row,x,reference,True,True,phys);full+=1
                count+=1
    assert count==6316 and all(branches.values())
    return dict(native_cases=count,correct_left_five_words_and_at_least_three_left_inside=True,
        selected_right_clear_absent_counts=branches,full_kernel_cases=full,
        native_sha256=dig.hexdigest(),full_kernel_sha256=phys.hexdigest())

def compute():
    tag=tagged();three=first_three();front=prefix()
    assert k.Q-2<TB and (TB+3,TB+5,TB+k.Q,TB+k.Q+(k.Q+1)//2)==(8196,8198,12289,14337)
    proof=HERE/'GAWN8_TAGGED_SUFFIX_AND_UNIVERSAL_LATE_REPAIR.md'
    sources=(Path(__file__),proof,HERE.parent/'unregistered_gawn2/small_rule_gawn2.py',
             HERE.parent/'unregistered_gawn2/small_compositional_cost.py')
    return dict(name='GAWN8 unchanged GAWN2 universal tagged suffix and restricted late recovery',
        passed=True,Q=k.Q,U=k.U,lambda_original=24,error_separation=104,fault_row=T,
        retained_Address_required=True,Age_interval=[96*k.Q-1,k.U-L-1],no_later_errors=True,
        tagged_suffix_all_colony_row=k.Q-2,universal_Workspace_zero_row=TB,
        universal_first3_correct_clock_row=TB+3,universal_first5_correct_clock_row=TB+5,
        universal_Flag2_and_clock_zero_damage_row=TB+k.Q,
        remaining_Flag1_updates_bound=(k.Q+1)//2,universal_full_native_quiet_row=14337,
        margin_before4Q=L-14337,native_quiet_persists_through_current_U=True,
        first5_clock_premise_for_every_admitted_payload_proved=True,
        universal_native_termination_for_stated_late_class_proved=True,
        complete2U_and_alllater_for_only_Age_flags_Info_faults_proved=True,
        broad_arbitrary_SF_complete2U=False,GF_changing_earlier_E0_surroundings_higher_iid=False,
        faithful_Gray_G17_refutation_shorterU_or_global_minimum=False,
        new_native_quiet_trajectory_or_full2U_simulation=False,rule_ROM_constants_G17_changed=False,
        tagged_neighbor_cofactors=tag,first3_clock_cofactors=three,clock_prefix_cofactors=front,
        actual_full_kernel_cases=sum(v['full_kernel_cases'] for v in (tag,three,front)),
        source_sha256={str(p.relative_to(ROOT)):sha(p) for p in sources})

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');args=parser.parse_args()
    start=time.perf_counter();result=compute()
    if args.write:
        out=ROOT/'figs/gray_counterexamples/unregistered_gawn8/GAWN8_tagged_suffix_certificate.json'
        out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(passed=True,tag_cases=result['tagged_neighbor_cofactors']['native_cases'],
        first3_cases=result['first3_clock_cofactors']['native_cases'],prefix_cases=result['clock_prefix_cofactors']['native_cases'],
        actual_full_kernel_cases=result['actual_full_kernel_cases'],native_quiet=14337,
        universal_stated_late_recovery=True,full_reliability=False,elapsed=time.perf_counter()-start)))
if __name__=='__main__':main()
