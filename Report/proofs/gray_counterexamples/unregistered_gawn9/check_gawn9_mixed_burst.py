"""Finite transcriptions for GAWN9, not a mixed-burst recovery experiment."""
from pathlib import Path
from dataclasses import replace
import argparse,hashlib,itertools,json,random,sys,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(HERE.parent/'unregistered_gawn2'))
import small_rule_gawn2 as k
import small_compositional_cost as own
T0=100*k.Q+2;R=3*k.Q+1+(k.Q+1)//2;L=4*k.Q
SF=('heads','mem','out','info','scratch','program','courier_l','courier_r',
    'mail_l','mail_r','history1','history2','history3')
WIDTHS=dict(heads=k.HEAD_BITS,mem=17*k.WORD,history1=17*k.WORD,
            history2=17*k.WORD,history3=17*k.WORD)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def add(d,row):d.update((json.dumps(row,separators=(',',':'))+'\n').encode())

def geometry():
    count=0;left_pair=0;dig=hashlib.sha256()
    lh=tuple(range(-2,3));rh=tuple(range(k.Q-3,k.Q+2))
    for width in range(1,105):
        for b in range(k.Q-width+1):
            e=b+width;lc=sum(b<=x<e for x in lh);rc=sum(b<=x<e for x in rh)
            assert not(lc>=3 and rc>=3),(b,width,lc,rc)
            p=(-k.Q,k.Q) if lc>=3 else (0,2*k.Q)
            assert p[0]<=0 and p[1]>=k.Q
            safe_right=lc>=3
            assert (rc if safe_right else lc)<=2
            # Every logical position outside I has at most two holders in I.
            for y in (-3,-2,-1,k.Q,k.Q+1,k.Q+2):
                assert sum(0<=y-s<k.Q for s in k.SLOTS)<=2
            left_pair+=safe_right;count+=1
            add(dig,[b,width,lc,rc,list(p)])
    assert count==420628 and left_pair==102
    return dict(all_allowed_intervals=count,left_pair_choice=left_pair,right_pair_choice=count-left_pair,
        neither_endpoint_simultaneously_has_three_replaced_holders=True,
        outside_I_holder_intersections_at_most_two=True,geometry_sha256=dig.hexdigest())

def shifted_deadlines():
    rows=[]
    for duration in range(104):
        margin=L-duration-R;coherence_margin=margin-1
        assert margin>=1944 and coherence_margin>=1943
        assert k.Q-2<2*k.Q+1<3*k.Q+1<R<=L-duration
        assert (k.U-L-1)+duration+(L-duration)==k.U-1
        assert (96*k.Q-1)+(2*k.Q+1)==98*k.Q
        assert T0+duration+R<k.U
        rows.append([duration,T0+duration,R,margin,coherence_margin])
    return dict(duration_offsets_enumerated=104,max_burst_rows=104,relative_to_last_fault_native_quiet=R,
        last_possible_absolute_native_quiet=T0+103+R,
        native_margin_before_initial4Q_minimum=1944,coherence_margin_minimum=1943,
        all_clock_guards_fit_unwrapped_interval=True,
        arithmetic_sha256=hashlib.sha256(json.dumps(rows,separators=(',',':')).encode()).hexdigest())

def head_word(rng,forbidden_bit_zero=None):
    p=k.unpack(rng.getrandbits(k.HEAD_BITS))
    if forbidden_bit_zero is not None:p=replace(p,move=p.move&~(1<<forbidden_bit_zero))
    return k.pack(p)

def endpoint_kernel():
    rng=random.Random(0x4741574e3901);dig=hashlib.sha256();count=kernels=post_votes=0
    mixed_cases=heterogeneous=0;branches={'reset':0,'birth':0,'active':0,'hold':0}
    computed_ages=set();common=(96*k.Q,96*k.Q+1,100*k.Q,100*k.Q+1,
                               100*k.Q+2,127*k.Q,127*k.Q+1,k.U-1)
    pool=tuple(v-1 for v in common)
    groups=list(itertools.combinations(range(5),3))
    for endpoint in (0,k.Q-1):
        bit=1 if endpoint==0 else 0
        specifications=[(age,False,good) for age in common for good in groups]
        specifications += [(None,True,groups[n%len(groups)]) for n in range(32)]
        for age,mixed,good in specifications:
            state={}
            for x in range(endpoint-10,endpoint+11):
                outside=not 0<=x<k.Q
                raw_age=T0+100 if mixed and outside else rng.choice(pool) if mixed else age-1
                native=dict(addr=x%k.Q,age=raw_age,f1=0 if x>=k.Q else rng.randrange(2),
                    f2=0 if outside else rng.randrange(2),wf1=0 if outside else rng.randrange(2),
                    wf2=0 if outside else rng.randrange(2))
                state[x]=k.Cell(**native,**{name:tuple(rng.getrandbits(WIDTHS.get(name,k.WORD)) for _ in k.SLOTS) for name in SF})
            for h,s in enumerate(k.SLOTS):
                x=endpoint-s;words=list(state[x].heads)
                words[h]=head_word(rng,bit if h in good else None)
                state[x]=replace(state[x],heads=tuple(words))
            old_words=[state[endpoint-s].heads[h] for h,s in enumerate(k.SLOTS)]
            assert not(k.unpack(k.vote(old_words)).move&(1<<bit))
            next_words=[];ages=[];outputs=[]
            for h,s in enumerate(k.SLOTS):
                x=endpoint-s;out=k.local_transition({j:state[x+j] for j in range(-8,9)},own.ROM)
                assert out.addr==x%k.Q
                packet=k.unpack(out.heads[h]);assert not(packet.move&(1<<bit)),(endpoint,age,mixed,h,packet)
                next_words.append(out.heads[h]);ages.append(out.age);outputs.append([hex(v) for v in k.cell_words(out)])
                computed_ages.add(out.age)
                reset=out.age in k.STAGE_STARTS or out.age==k.EARLY_RESET
                birth=out.age in (k.EARLY_BIRTH,100*k.Q+1)
                active=k.EARLY_BIRTH<out.age<75*k.Q or 100*k.Q+1<out.age<=127*k.Q
                branch='reset' if reset else 'birth' if birth else 'active' if active else 'hold'
                branches[branch]+=1;kernels+=1
            if not mixed:assert ages==[age]*5
            else:mixed_cases+=1;heterogeneous+=len(set(ages))>1
            for bad in itertools.combinations(range(5),2):
                replaced=list(next_words)
                for h in bad:replaced[h]=(1<<k.HEAD_BITS)-1
                assert not(k.unpack(k.vote(replaced)).move&(1<<bit)),(endpoint,bad)
                post_votes+=1
            add(dig,[endpoint,age,mixed,list(good),[[hex(v) for v in k.cell_words(state[x])] for x in range(endpoint-10,endpoint+11)],
                     ages,outputs])
            count+=1
    assert (count,kernels,mixed_cases,post_votes)==(224,1120,64,2240)
    assert heterogeneous>0 and all(branches.values())
    return dict(selected_endpoint_configurations=count,actual_full_kernel_calls=kernels,
        selected_mixed_clock_configurations=mixed_cases,actually_heterogeneous_computed_clock_configurations=heterogeneous,
        all_three_holder_subsets_enumerated=True,all_two_holder_post_overwrite_masks_enumerated=True,
        post_overwrite_vote_checks=post_votes,actual_Head_branch_counts=branches,
        actual_computed_clocks_observed=sorted(computed_ages),all13_SF_arbitrary_selected=True,
        inputs_outputs_sha256=dig.hexdigest())

def compute():
    g=geometry();d=shifted_deadlines();p=endpoint_kernel()
    proof=HERE/'GAWN9_LATE_MIXED_BURST_PAIR_REPAIR.md'
    sources=(Path(__file__),proof,HERE.parent/'unregistered_gawn2/small_rule_gawn2.py',
             HERE.parent/'unregistered_gawn2/small_compositional_cost.py')
    return dict(name='GAWN9 unchanged GAWN2 late mixed104x104 Address-retaining burst repair',
        passed=True,Q=k.Q,U=k.U,lambda_original=24,error_separation=104,first_fault_row=T0,
        max_fault_rows=104,max_fault_width=104,support_inside_one_true_colony_required=True,
        retained_Address_required=True,replacement_Age_interval=[96*k.Q-1,k.U-L-1],
        all_four_flags_and_all13_SF_arbitrary_legal=True,no_other_errors=True,
        native_quiet_relative_to_last_fault=R,native_margin_before_initial4Q_minimum=1944,
        protected_endpoint_and_fixed_adjacent_pair_logical_SF_confinement_proved=True,
        raw_holder_halo_two_and_external_native_Flag1_allowed=True,
        actual_complete_U_represented_D_encoding_proved=True,complete2U_and_alllater_equality_proved=True,
        arbitrary_native_padding_at_U_admitted=True,conditional_native_quiet_premise_required=False,
        new_evolving_mixed_burst_nativequiet_or_full2U_simulation=False,
        GF_changing_earlier_arbitrary_Age_E0_surroundings_separated_higher_iid_proved=False,
        faithful_Gray_G17_refutation_shorterU_or_global_minimum=False,rule_ROM_constants_G17_changed=False,
        interval_geometry=g,shifted_arithmetic=d,endpoint_full_kernel_supplements=p,
        source_sha256={str(v.relative_to(ROOT)):sha(v) for v in sources})

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');args=parser.parse_args()
    start=time.perf_counter();r=compute()
    if args.write:
        out=ROOT/'figs/gray_counterexamples/unregistered_gawn9/GAWN9_mixed_burst_certificate.json'
        out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps(dict(passed=True,intervals=r['interval_geometry']['all_allowed_intervals'],
        endpoint_configurations=224,full_kernel_calls=1120,shifted_deadlines=104,
        universal_stated_mixed_burst_complete2U=True,full_reliability=False,elapsed=time.perf_counter()-start)))
if __name__=='__main__':main()
