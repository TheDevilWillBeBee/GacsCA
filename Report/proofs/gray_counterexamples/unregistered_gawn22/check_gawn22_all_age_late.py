"""Finite literal supplements for the written all-Age late recovery proof.

No evolving repair trajectory, physical2U simulation or iid proof.
"""
import argparse,hashlib,itertools,json,random,sys,time
from dataclasses import replace
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
OUT=ROOT/'figs/gray_counterexamples/unregistered_gawn22'
sys.path.insert(0,str(HERE.parent/'unregistered_gawn10'))
import check_gawn10_two_offset_projection as c
k=c.k;own=c.own;SF=c.SF
T0=100*k.Q+2;R0=k.Q-2;CLOCK=2*k.Q-2;R=CLOCK+k.Q//2
LAST=k.U-1-R
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def add(d,x):d.update((json.dumps(x,separators=(',',':'))+'\n').encode())
def native(v):return [getattr(v,n) for n in k.NATIVE_NAMES]
def raw(v):return [hex(z) for z in k.cell_words(v)]
def sf(rng):return {n:tuple(rng.getrandbits(c.WIDTHS.get(n,k.WORD)) for _ in k.SLOTS) for n in SF}
def no_bit(v,bit):
    p=k.unpack(v);return k.pack(replace(p,move=p.move&~(1<<bit)))
def branch(age):
    if age in k.STAGE_STARTS or age==k.EARLY_RESET:return 'reset'
    if age in (k.EARLY_BIRTH,100*k.Q+1):return 'birth'
    if k.EARLY_BIRTH<age<75*k.Q or 100*k.Q+1<age<=127*k.Q:return 'active'
    return 'hold'
def gate():
    rng=random.Random(0x4741574e323201);dig=hashlib.sha256()
    phases=(0,1,2,3,4,5,k.Q-6,k.Q-5,k.Q-4,k.Q-3,k.Q-2,k.Q-1)
    critical=(0,k.U-1,96*k.Q-1,98*k.Q-1,72*k.Q+2,80*k.Q-2)
    for index in range(320):
        x=phases[index%len(phases)];theta=(T0+1,T0+103+R,LAST,127*k.Q,k.U-1)[index%5]
        cells={}
        for j in range(-8,9):
            inside=0<=x+j<k.Q
            flags={n:rng.randrange(2) if inside else 0 for n in ('f1','f2','wf1','wf2')}
            if -k.Q<=x+j<0:flags['f1']=rng.randrange(2)
            age=critical[(index+j)%len(critical)] if inside else theta-1
            if 1<=j<=5:
                cat=rng.randrange(3) if inside else 0
                age=theta-1 if cat<2 else age;flags['f1']=int(cat>0)
            cells[j]=k.Cell(addr=(x+j)%k.Q,age=age,**flags,**sf(rng))
        got=k.local_transition(cells,own.ROM)
        assert got.addr==x and (got.age==theta or got.f1==1) and got.wf2==0
        add(dig,[index,x,theta,[raw(cells[j]) for j in range(-8,9)],native(got)])
    return dict(full_kernel_tagged_late_gate_comparisons=320,
                inputs_outputs_sha256=dig.hexdigest())
def endpoints():
    rng=random.Random(0x4741574e323202);dig=hashlib.sha256()
    events=(0,1,32*k.Q,32*k.Q+1,64*k.Q,64*k.Q+1,
        72*k.Q+3,72*k.Q+4,72*k.Q+5,75*k.Q,75*k.Q+1,
        80*k.Q-1,80*k.Q,96*k.Q,98*k.Q-1,100*k.Q,100*k.Q+1,
        T0,127*k.Q,127*k.Q+1,k.U-1)
    pool=tuple((a-1)%k.U for a in events)
    groups=list(itertools.combinations(range(5),3));count=calls=post=mixed_n=hetero=0
    branches={n:0 for n in ('reset','birth','active','hold')};observed=set()
    for endpoint in (0,k.Q-1):
        bit=1 if endpoint==0 else 0
        cases=[(a,False,g) for a in events for g in groups]
        cases += [(None,True,groups[n%10]) for n in range(32)]
        for age,mixed,good in cases:
            state={}
            for x in range(endpoint-10,endpoint+11):
                inside=0<=x<k.Q
                old_age=rng.choice(pool) if mixed and inside else T0+100 if mixed else (age-1)%k.U
                flags={n:rng.randrange(2) if inside else 0 for n in ('f1','f2','wf1','wf2')}
                if -k.Q<=x<0:flags['f1']=rng.randrange(2)
                state[x]=k.Cell(addr=x%k.Q,age=old_age,**flags,**sf(rng))
            for h,s in enumerate(k.SLOTS):
                x=endpoint-s;words=list(state[x].heads)
                if h in good:words[h]=no_bit(words[h],bit)
                state[x]=replace(state[x],heads=tuple(words))
            assert not(k.unpack(k.vote([state[endpoint-s].heads[h] for h,s in enumerate(k.SLOTS)])).move&(1<<bit))
            values=[];ages=[];outputs=[]
            for h,s in enumerate(k.SLOTS):
                x=endpoint-s;got=k.local_transition({j:state[x+j] for j in range(-8,9)},own.ROM)
                assert got.addr==x%k.Q
                assert not(k.unpack(got.heads[h]).move&(1<<bit))
                values.append(got.heads[h]);ages.append(got.age);outputs.append(raw(got))
                branches[branch(got.age)]+=1;observed.add(got.age);calls+=1
            if mixed:mixed_n+=1;hetero+=len(set(ages))>1
            else:assert ages==[age]*5
            for bad in itertools.combinations(range(5),2):
                changed=list(values)
                for h in bad:changed[h]=(1<<k.HEAD_BITS)-1
                assert not(k.unpack(k.vote(changed)).move&(1<<bit));post+=1
            add(dig,[endpoint,age,mixed,list(good),[raw(state[x]) for x in range(endpoint-10,endpoint+11)],ages,outputs]);count+=1
    assert (count,calls,mixed_n,post)==(484,2420,64,4840)
    assert hetero>0 and all(branches.values()) and 0 in observed
    return dict(selected_endpoint_configurations=count,actual_full_kernel_calls=calls,
        mixed_clock_configurations=mixed_n,heterogeneous_computed_clock_configurations=hetero,
        all_three_holder_subsets_for_common_events=True,post_overwrite_two_holder_vote_checks=post,
        actual_Head_branch_counts=branches,actual_computed_Ages_observed=sorted(observed),
        age0_reset_observed=True,inputs_outputs_sha256=dig.hexdigest())
def exterior():
    rng=random.Random(0x4741574e323203);dig=hashlib.sha256()
    phases=(T0+1,T0+103,T0+R,T0+103+R,LAST,127*k.Q,127*k.Q+1,k.U-1)
    old_inside=(k.U-1,32*k.Q-1,32*k.Q,32*k.Q+4097,
        75*k.Q-1,75*k.Q,80*k.Q-2,72*k.Q+2,72*k.Q+3,
        72*k.Q+4,100*k.Q-1,100*k.Q,k.U-2)
    groups=list(itertools.combinations(range(5),3))
    configs=calls=outside_calls=word_checks=0;inside_ages=set();inside_branches={n:0 for n in ('reset','birth','active','hold')}
    for p0,p1 in ((-k.Q,k.Q),(0,2*k.Q)):
        for y in (p0-2,p0-1,p1,p1+1):
            outside_slots=[h for h,s in enumerate(k.SLOTS) if not 0<=y-s<k.Q]
            assert len(outside_slots)>=3
            for theta in phases:
                for pattern in range(6):
                    cache={}
                    def ref_value(n,z):
                        key=(n,z)
                        if key not in cache:
                            v=0 if n in ('mail_l','mail_r') else rng.getrandbits(c.WIDTHS.get(n,k.WORD))
                            if n=='heads' and z in (p0,p1-1):v=no_bit(v,1 if z==p0 else 0)
                            cache[key]=v
                        return cache[key]
                    reference={};dirty={}
                    good=groups[(pattern+phases.index(theta))%len(groups)]
                    for x in range(y-10,y+11):
                        reference[x]=k.Cell(addr=x%k.Q,age=theta-1,
                            **{n:tuple(ref_value(n,x+s) for s in k.SLOTS) for n in SF})
                        words={}
                        for n in SF:
                            arr=[]
                            for h,s in enumerate(k.SLOTS):
                                z=x+s
                                v=ref_value(n,z) if not p0<=z<p1 and h in good else rng.getrandbits(c.WIDTHS.get(n,k.WORD))
                                if n=='heads' and z in (p0,p1-1) and h in good:v=no_bit(v,1 if z==p0 else 0)
                                arr.append(v)
                            words[n]=tuple(arr)
                        inside=0<=x<k.Q
                        flags={n:rng.randrange(2) if inside else 0 for n in ('f1','f2','wf1','wf2')}
                        if -k.Q<=x<0:flags['f1']=rng.randrange(2)
                        age=old_inside[(x+pattern)%len(old_inside)] if inside else theta-1
                        # Deliberately open the age0 branch on selected inside
                        # outputs by forcing source4; canonical GF retained.
                        if inside and pattern==0:
                            age=k.U-1;flags['wf2']=1
                        dirty[x]=k.Cell(addr=x%k.Q,age=age,**flags,**words)
                    # Premises concern votes; raw work is deliberately incoherent.
                    for z in range(y-5,y+6):
                        if not p0<=z<p1:
                            for n in SF:
                                vals=[getattr(dirty[z-s],n)[h] for h,s in enumerate(k.SLOTS)]
                                assert k.vote(vals)==ref_value(n,z)
                    for z,bit in ((p0,1),(p1-1,0)):
                        if y-5<=z<=y+5:
                            assert not(k.unpack(k.vote([dirty[z-s].heads[h] for h,s in enumerate(k.SLOTS)])).move&(1<<bit))
                    output_words={n:[] for n in SF};expected={}
                    for h,s in enumerate(k.SLOTS):
                        x=y-s
                        got=k.local_transition({j:dirty[x+j] for j in range(-8,9)},own.ROM)
                        clean=k.local_transition({j:reference[x+j] for j in range(-8,9)},own.ROM)
                        for n in SF:
                            value=getattr(got,n)[h];output_words[n].append(value)
                            if n in expected:assert expected[n]==getattr(clean,n)[h]
                            else:expected[n]=getattr(clean,n)[h]
                            if h in outside_slots:assert value==expected[n],(p0,p1,y,theta,pattern,h,n)
                        if h in outside_slots:
                            assert got.addr==x%k.Q and got.age==theta and got.f2==got.wf1==got.wf2==0
                            outside_calls+=1;word_checks+=len(SF)
                        else:
                            inside_ages.add(got.age);inside_branches[branch(got.age)]+=1
                        add(dig,[p0,p1,y,theta,pattern,h,[raw(dirty[x+j]) for j in range(-8,9)],native(got),
                                 [hex(getattr(got,n)[h]) for n in SF],[hex(expected[n]) for n in SF]])
                        calls+=1
                    for n in SF:assert k.vote(output_words[n])==expected[n]
                    configs+=1
    assert (configs,calls,outside_calls,word_checks)==(384,1920,1632,21216)
    assert 0 in inside_ages
    return dict(selected_exterior_logical_configurations=configs,
        dirty_actual_full_kernel_calls=calls,clean_reference_full_kernel_calls=calls,
        correct_outside_physical_holder_comparisons=outside_calls,
        all13_SF_outside_holder_word_comparisons=word_checks,
        raw_outside_work_coherence_assumed=False,inside_actual_computed_Ages_observed=sorted(inside_ages),
        inside_actual_Head_branch_counts=inside_branches,inside_computed_age0_observed=True,
        inputs_outputs_sha256=dig.hexdigest())
def commit():
    rng=random.Random(0x4741574e323204);dig=hashlib.sha256();calls=0
    for y in (0,1,k.PRIMARY_START,k.PRIMARY_START+k.FRAME_WORDS-1,k.Q-1,k.Q,k.Q+1):
        for pattern in range(8):
            state={x:k.Cell(addr=x%k.Q,age=k.U-1,**sf(rng)) for x in range(y-10,y+11)}
            old_out=k.vote([state[y-s].out[h] for h,s in enumerate(k.SLOTS)])&k.MASK
            outputs=[]
            for h,s in enumerate(k.SLOTS):
                x=y-s;got=k.local_transition({j:state[x+j] for j in range(-8,9)},own.ROM)
                assert native(got)==[x%k.Q,0,0,0,0,0]
                assert got.info[h]==old_out and got.program[h]==k.beta_bit(own.ROM,y%k.Q)
                assert all(getattr(got,n)[h]==0 for n in SF if n not in ('info','program'))
                outputs.append(raw(got));calls+=1
            add(dig,[y,pattern,[raw(state[x]) for x in range(y-10,y+11)],hex(old_out),outputs])
    assert calls==280
    return dict(actual_age0_common_native_incoherent_raw_work_full_kernel_calls=calls,
                coherent_Info_old_Out_commit_and_all_work_reset=True,inputs_outputs_sha256=dig.hexdigest())
def deadlines():
    dig=hashlib.sha256();count=0
    for last in range(T0,LAST+1):
        q=last+R
        assert T0<=last<=LAST and q<=k.U-1 and 100*k.Q<last+R0<=q<k.U
        add(dig,[last,last+R0,last+CLOCK,q,k.U-q]);count+=1
    assert (T0,R0,CLOCK,R,LAST,count)==(409602,4094,8190,10238,514049,104448)
    assert T0+103+R==419943 and LAST+R==k.U-1
    return dict(all_last_possible_fault_rows_checked=count,first_possible_last_fault=T0,
        last_possible_last_fault=LAST,latest_native_quiet=k.U-1,
        latest104row_corollary_native_quiet=T0+103+R,deadline_rows_sha256=dig.hexdigest())
def compute():
    g=gate();e=endpoints();s=exterior();u=commit();d=deadlines()
    p21=ROOT/'figs/gray_counterexamples/unregistered_gawn21/GAWN21_all_age_early_certificate.json'
    p9=ROOT/'figs/gray_counterexamples/unregistered_gawn9/GAWN9_mixed_burst_certificate.json'
    a21=json.loads(p21.read_text());a9=json.loads(p9.read_text())
    assert a21['tagged_normal_output_implies_actual_Workspace2_zero_proved']
    assert a9['interval_geometry']['all_allowed_intervals']==420628
    sources=(Path(__file__),HERE/'GAWN22_ALL_AGE_LATE_PAIR_REPAIR.md',
        HERE.parent/'unregistered_gawn2/small_rule_gawn2.py',
        HERE.parent/'unregistered_gawn6/GAWN6_CANONICAL_ADDRESS_CLOCK_CONFINEMENT.md',
        HERE.parent/'unregistered_gawn7/GAWN7_FLAG2_DEADLINE_AND_FIVE_CLOCK_REDUCTION.md',
        HERE.parent/'unregistered_gawn8/GAWN8_TAGGED_SUFFIX_AND_UNIVERSAL_LATE_REPAIR.md',
        HERE.parent/'unregistered_gawn9/GAWN9_LATE_MIXED_BURST_PAIR_REPAIR.md',
        HERE.parent/'unregistered_gawn21/GAWN21_ALL_AGE_EARLY_ONE_COLONY_REPAIR.md',p21,p9)
    return dict(name='GAWN22 arbitrary-Age late repeated address-preserving fixed-support pair repair',passed=True,
        Q=k.Q,U=k.U,lambda_original=24,error_separation=104,
        unchanged_GAWN2_all_Gray_departures_required=True,initial_actual_H2_physical_row=T0,
        last_possible_after_row_fault=LAST,fixed_support_inside_true_colony0_width_at_most104=True,
        arbitrary_subset_of104448_possible_fault_rows=True,Address_retained=True,
        all_legal_replacement_Age_inclusive=[0,k.U-1],all4_flags_all13_SF_arbitrary_adaptive=True,
        no_other_errors_required=True,native_Workspace2_deadline_after_last_fault=R0,
        native_clock_deadline_after_last_fault=CLOCK,native_complete_deadline_after_last_fault=R,
        universal_stated_late_native_recovery_proved=True,
        protected_pair_all13_logical_SF_confinement_proved=True,
        complete_actual_U_represented_D_encoding_including_q_Uminus1_proved=True,
        complete_actual2U_and_alllater_equality_proved=True,
        global_inside_clock_band_or_inactive_inside_SF_schedule_assumed=False,
        original_error_class_from_support_geometry_assigned=False,
        GF_changes_multiple_moving_supports_other_phases_E0_higher_iid_memory_proved=False,
        faithful_Gray_G17_refutation_or_minimum_sufficient_fix_proved=False,
        evolving_fullSF_repair_or_physical2U_simulation_performed=False,
        rule_ROM_constants_CURRENT_changed=False,late_tagged_gate=g,all_clock_endpoint=e,
        three_correct_exterior_holder_allSF=s,actual_U_commit=u,all_deadlines=d,
        inherited_geometry=a9['interval_geometry'],
        inherited_WF1_allowed_first3_clock_cofactors=a21['first_three_WF1_allowed_clock_cofactors'],
        inherited_WF1_allowed_clock_prefix_cofactors=a21['correct_left_WF1_allowed_prefix_cofactors'],
        inherited_h1_WF1_allowed_front_cofactors=a21['h1_WF1_allowed_Flag2_zero_front_cofactors'],
        source_sha256={str(p.relative_to(ROOT)):sha(p) for p in sources})
def main():
    p=argparse.ArgumentParser();p.add_argument('--issue',action='store_true');args=p.parse_args()
    start=time.perf_counter();OUT.mkdir(parents=True,exist_ok=True)
    pp=ROOT/'figs/gray_counterexamples/unregistered_gawn21/GAWN21_standalone_assets.json'
    parent=json.loads(pp.read_text());assert len(parent['assets_sha256'])==755
    cp=OUT/'GAWN22_all_age_late_certificate.json';mp=OUT/'GAWN22_standalone_assets.json'
    for path,value in parent['assets_sha256'].items():assert sha(ROOT/path)==value,path
    if args.issue:
        assert not cp.exists() and not mp.exists()
        result=compute();cp.write_text(json.dumps(result,indent=2)+'\n')
        assets=dict(parent['assets_sha256'])
        for path in (pp,ROOT/'figs/gray_counterexamples/unregistered_gawn21/GAWN21_readonly_run01.log',
                     Path(__file__),HERE/'GAWN22_ALL_AGE_LATE_PAIR_REPAIR.md',cp):assets[str(path.relative_to(ROOT))]=sha(path)
        manifest=dict(name=result['name'],inherited_assets=755,assets_sha256=assets,
            universal_stated_all_Age_late_fixed_support_complete2U_repair_proved=True,
            global_reliability_proved=False,rule_ROM_constants_CURRENT_changed=False)
        mp.write_text(json.dumps(manifest,indent=2)+'\n')
    else:
        manifest=json.loads(mp.read_text());assert manifest['inherited_assets']==755
        for path,value in parent['assets_sha256'].items():assert manifest['assets_sha256'][path]==value,path
        for path,value in manifest['assets_sha256'].items():assert sha(ROOT/path)==value,path
        result=compute();assert result==json.loads(cp.read_text()),'Fresh supplements differ'
    for path,value in manifest['assets_sha256'].items():assert sha(ROOT/path)==value,path
    print(json.dumps(dict(passed=True,issued=args.issue,readonly=not args.issue,
        assets=len(manifest['assets_sha256']),inherited_assets=755,
        all_new_native_gate_endpoint_allSF_holder_commit_integer_supplements_recomputed=True,
        all_legal_Age_late_fixed_support_complete2U_repair_proved=True,
        maximum_last_fault=LAST,Workspace2_deadline=R0,clock_deadline=CLOCK,native_deadline=R,
        latest_native_quiet=k.U-1,global_reliability_proved=False,rule_ROM_constants_CURRENT_changed=False,
        certificate_sha256=sha(cp),manifest_sha256=sha(mp),elapsed=time.perf_counter()-start)),flush=True)
if __name__=='__main__':main()
