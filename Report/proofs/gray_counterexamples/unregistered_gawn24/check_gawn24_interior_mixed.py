"""Literal/word-index supplements for the written GAWN24 theorem.

No evolving native/full-SF U/2U execution; the induction is in the proof.
"""
import argparse, hashlib, json, random, sys, time
from dataclasses import replace
from pathlib import Path

HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[3]
OUT=ROOT/'figs/gray_counterexamples/unregistered_gawn24'
sys.path.insert(0,str(HERE.parent/'unregistered_gawn10'))
sys.path.insert(0,str(HERE.parent/'unregistered_gawn4'))
import check_gawn10_two_offset_projection as c
import check_late_sf_gawn4 as h
k=c.k; own=c.own; SF=c.SF
R0=k.Q-2; CLOCK=2*k.Q-2; R=CLOCK+k.Q//2
LAST=k.U-1-R; LAST_CAPTURE_OPERAND=72*k.Q+1
PARENT=ROOT/'figs/gray_counterexamples/unregistered_gawn23/GAWN23_validation_assets.json'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def add(d,x):d.update((json.dumps(x,separators=(',',':'))+'\n').encode())
def raw(v):return [hex(z) for z in k.cell_words(v)]
def native(v):return [getattr(v,n) for n in k.NATIVE_NAMES]
def sf(rng):return {n:tuple(rng.getrandbits(c.WIDTHS.get(n,k.WORD)) for _ in k.SLOTS) for n in SF}

def exterior_state(rng,lo,hi,old):
    """Native exterior premise; arbitrary actual SF except derived Info/courier0."""
    state={}
    for x in range(lo,hi+1):
        inside=0<=x<k.Q
        words=sf(rng)
        words['info']=tuple(rng.getrandbits(k.WORD) if inside else h.intact_info(x+s)
                            for s in k.SLOTS)
        # There are no SF hypotheses on the other tracks. At the actual
        # 80Q-1 write only, supply the already proved outside courier0.
        if old==80*k.Q-2:
            for n in ('courier_l','courier_r'):
                words[n]=tuple(rng.getrandbits(k.WORD) if inside else 0 for _ in k.SLOTS)
        flags={n:rng.randrange(2) if inside else 0 for n in ('f1','f2','wf1','wf2')}
        if -k.Q<=x<0:flags['f1']=rng.randrange(2)
        state[x]=k.Cell(addr=x%k.Q,age=rng.randrange(k.U) if inside else old,
                         **flags,**words)
    return state

def native_exterior():
    rng=random.Random(0x4741574e323401);dig=hashlib.sha256();calls=0
    xs=(-k.Q-6,-k.Q-5,-k.Q-1,-6,-5,-4,-3,-2,-1,k.Q,k.Q+1,k.Q+2,k.Q+3,k.Q+4,k.Q+5)
    phases=(0,1,32*k.Q-1,64*k.Q-1,72*k.Q+2,80*k.Q-2,
            96*k.Q-1,96*k.Q,98*k.Q-2,98*k.Q-1,100*k.Q,127*k.Q,k.U-2)
    for x in xs:
        for old in phases:
            for pattern in range(4):
                state=exterior_state(rng,x-8,x+8,old)
                cells={j:state[x+j] for j in range(-8,9)}
                got=k.local_transition(cells,own.ROM)
                assert (got.addr,got.age,got.f2,got.wf1,got.wf2)==(x%k.Q,old+1,0,0,0)
                if not -k.Q<=x<0:assert got.f1==0
                add(dig,[x,old,pattern,[raw(cells[j]) for j in range(-8,9)],native(got)]);calls+=1
    assert calls==780
    controls=hashlib.sha256();n=0
    for x,field in ((-3,'wf1'),(k.Q+3,'wf2')):
        for bit in (0,1):
            cells={j:k.Cell(addr=(x+j)%k.Q,age=96*k.Q-1,info=(bit,)*5)
                   for j in range(-8,9)}
            got=k.local_transition(cells,own.ROM)
            assert (got.addr,got.age,got.f1,got.f2)==(x%k.Q,96*k.Q,0,0)
            assert getattr(got,field)==bit
            add(controls,[x,field,bit,[raw(cells[j]) for j in range(-8,9)],native(got)]);n+=1
    return dict(full_kernel_native_exterior_cases=calls,old_reference_phases=list(phases),
        open_workspace_guard_uses_actual_outside_Info_zero=True,
        exterior_inputs_outputs_sha256=dig.hexdigest(),actual_positive_negative_source_controls=n,
        source_controls_sha256=controls.hexdigest())

def tagged_gates():
    rng=random.Random(0x4741574e323402);dig=hashlib.sha256();calls=zero=0
    xs=(0,1,2,3,4,5,k.Q-6,k.Q-5,k.Q-4,k.Q-3,k.Q-2,k.Q-1)
    phases=(1,72*k.Q+2,75*k.Q-1,96*k.Q,98*k.Q-1,98*k.Q,99*k.Q,k.U-1)
    for x in xs:
        for theta in phases:
            for pattern in range(4):
                state=exterior_state(rng,x-8,x+8,theta-1)
                cells={j:state[x+j] for j in range(-8,9)}
                for j in range(1,6):
                    v=cells[j]
                    if not 0<=x+j<k.Q:continue
                    cat=rng.randrange(3)
                    age=theta-1 if cat<2 else (0,k.U-1,96*k.Q-1,98*k.Q-1)[(j+pattern)%4]
                    cells[j]=replace(v,age=age,f1=int(cat>0))
                got=k.local_transition(cells,own.ROM)
                assert got.addr==x and (got.age==theta or got.f1==1)
                if theta<96*k.Q or theta>=98*k.Q:
                    assert got.wf2==0;zero+=1
                add(dig,[x,theta,pattern,[raw(cells[j]) for j in range(-8,9)],native(got)]);calls+=1
    assert (calls,zero)==(384,288)
    return dict(actual_tagged_normal_output_kernels=calls,actual_tagged_WF2_zero_cases=zero,
                open_pulse_tagged_WF2_zero_claimed=False,inputs_outputs_sha256=dig.hexdigest())

def holder_equations():
    rng=random.Random(0x4741574e323403);dig=hashlib.sha256();configs=calls=outside=words=0
    ys=(-2,-1,k.Q,k.Q+1)
    phases=(0,32*k.Q-1,32*k.Q,64*k.Q-1,64*k.Q,72*k.Q+1,72*k.Q+2,72*k.Q+3,
            75*k.Q-1,75*k.Q,80*k.Q-2,96*k.Q-1,98*k.Q-1,100*k.Q-1,100*k.Q,127*k.Q,k.U-2)
    fields=tuple(n for n in SF if n not in ('mail_l','mail_r'))
    assert len(fields)==11
    for y in ys:
        for old in phases:
            for pattern in range(3):
                state=exterior_state(rng,y-10,y+10,old)
                reference={x:replace(v,age=old,f1=0,f2=0,wf1=0,wf2=0) for x,v in state.items()}
                outputs=[];wanted={};dirty=[]
                for q,s in enumerate(k.SLOTS):
                    x=y-s
                    got=k.local_transition({j:state[x+j] for j in range(-8,9)},own.ROM)
                    ref=k.local_transition({j:reference[x+j] for j in range(-8,9)},own.ROM)
                    for n in fields:
                        v=getattr(ref,n)[q]
                        if n in wanted:assert wanted[n]==v,(y,old,n,'reference outputs incoherent')
                        else:wanted[n]=v
                        if not 0<=x<k.Q:
                            assert getattr(got,n)[q]==v;words+=1
                    if not 0<=x<k.Q:
                        assert (got.addr,got.age,got.f2,got.wf1,got.wf2)==(x%k.Q,old+1,0,0,0)
                        outside+=1
                    outputs.append(got);dirty.append(0<=x<k.Q);calls+=2
                for n in fields:
                    values=[getattr(v,n)[q] for q,v in enumerate(outputs)]
                    assert k.vote(values)==wanted[n]
                    overwritten=[rng.getrandbits(c.WIDTHS.get(n,k.WORD)) if dirty[q] else v
                                 for q,v in enumerate(values)]
                    assert k.vote(overwritten)==wanted[n]
                add(dig,[y,old,pattern,[raw(state[x]) for x in range(y-10,y+11)],
                         [raw(v) for v in outputs],{n:hex(v) for n,v in wanted.items()}]);configs+=1
    assert (configs,calls,outside,words)==(204,2040,714,7854)
    return dict(mixed_clock_actual_holder_configurations=configs,actual_plus_reference_full_kernels=calls,
        correct_outside_physical_holder_checks=outside,eleven_SF_actual_holder_word_equalities=words,
        arbitrary_inside_holder_outputs_and_post_overwrites_allowed=True,inputs_outputs_sha256=dig.hexdigest())

def arithmetic():
    intervals=[[s,s+8*k.Q+1] for s in k.GATHER_STARTS]
    support=hashlib.sha256();n=0
    end_holders=[range(-2,3),range(k.Q-3,k.Q+2)]
    for b in range(1,k.Q-1):
        for w in range(1,min(104,k.Q-1-b)+1):
            counts=[sum(b<=x<b+w for x in group) for group in end_holders]
            assert max(counts)<=2
            add(support,[b,w,counts]);n+=1
    assert n==420420
    deadlines=hashlib.sha256();window=hashlib.sha256();counts=[0]*4
    for last in range(LAST+1):
        B=max(last+R0,98*k.Q);q=B+k.Q+k.Q//2
        assert q==max(last+R,407552) and q<=k.U-1
        assert B>=98*k.Q and B>=last+R0 and B+k.Q>=99*k.Q
        add(deadlines,[last,B,B+3,B+k.Q,q])
    for tau in range(LAST+1):
        last=min(LAST,tau+103)
        if tau<=LAST_CAPTURE_OPERAND:
            q=last+R
            assert q<=305254<75*k.Q<96*k.Q and q-tau<=10341
            touched=[g for g,(lo,hi) in enumerate(intervals,1) if tau<=hi and q>=lo]
        else:q=None;touched=[]
        assert len(touched)<=1
        counts[touched[0] if touched else 0]+=1
        add(window,[tau,last,q,touched])
    assert sum(counts)==LAST+1==514050
    return dict(interior_supports_checked=n,support_endpoint_sha256=support.hexdigest(),
        all_last_fault_deadline_rows=LAST+1,native_deadline_rows_sha256=deadlines.hexdigest(),
        all_first_fault_phase_rows=LAST+1,conservative_capture_windows=intervals,
        zero_or_one_bank_phase_counts=counts,all_phase_bank_rows_sha256=window.hexdigest(),
        maximum_early_native_disturbance_endpoint_distance=10341,
        maximum_early_quiet_physical_row=305254,latest_global_quiet_physical_row=k.U-1,
        native_quiet_bound='max(L+10238,407552)')

def compute():
    e=native_exterior();t=tagged_gates();v=holder_equations();a=arithmetic()
    sources=(Path(__file__),HERE/'GAWN24_INTERIOR_ALL_AGE_MIXED_PHASE_REPAIR.md',
        HERE.parent/'unregistered_gawn2/small_rule_gawn2.py',
        HERE.parent/'unregistered_gawn6/GAWN6_CANONICAL_ADDRESS_CLOCK_CONFINEMENT.md',
        HERE.parent/'unregistered_gawn8/GAWN8_TAGGED_SUFFIX_AND_UNIVERSAL_LATE_REPAIR.md',
        HERE.parent/'unregistered_gawn21/GAWN21_ALL_AGE_EARLY_ONE_COLONY_REPAIR.md',
        HERE.parent/'unregistered_gawn23/GAWN23_ALL_PHASE_SF_BURST_REPAIR.md',PARENT)
    return dict(name='GAWN24 interior all-Age mixed-phase address-preserving complete2U repair',passed=True,
        Q=k.Q,U=k.U,lambda_original=24,error_separation=104,
        unchanged_GAWN2_all_Gray_departures_required=True,initial_actual_recursive_H2_required=True,
        fixed_support_inside_true_colony0_width_at_most104=True,
        support_excludes_physical_boundary_sites_0_and_Qminus1=True,
        all_first_fault_phases_inclusive=[0,LAST],maximum_last_possible_after_row_fault=LAST,
        burst_after_row_duration_at_most104=True,actual_Address_retained=True,
        all_legal_replacement_Age_inclusive=[0,k.U-1],all4_flags_all13_SF_arbitrary_adaptive=True,
        no_other_errors_required=True,both_actual_true_colony_Head_endpoints_protected_proved=True,
        actual_native_exterior_through_open_workspace_guard_proved=True,
        actual_early_Out_courier_and_outside_Info_source_zero_proved=True,
        two_actual_banks_and_each_outside_tape_only_upper_record0_arbitrary_proved=True,
        global_consistency_of_erroneous_record0_across_evaluators_assumed=False,
        actual_tagged_Workspace2_zero_at_max_Lplus4094_98Q_proved=True,
        actual_native_quiet_max_Lplus10238_407552_proved=True,
        actual_late_preparation_completed_Out_and_U_encoding_proved=True,
        complete_actual_2U_and_all_later_repair_proved=True,
        original_error_class_from_support_geometry_assigned=False,
        boundary_touching_GF_changes_later_multiple_supports_E0_higher_iid_memory_proved=False,
        faithful_Gray_G17_refutation_or_minimum_sufficient_fix_proved=False,
        evolving_fullSF_native_trajectory_or_physicalU2U_simulation_performed=False,
        rule_ROM_constants_CURRENT_changed=False,native_exterior_supplements=e,
        tagged_gate_supplements=t,three_holder_SF_supplements=v,integer_supplements=a,
        source_sha256={str(p.relative_to(ROOT)):sha(p) for p in sources})

def main():
    p=argparse.ArgumentParser();p.add_argument('--issue',action='store_true');args=p.parse_args()
    start=time.perf_counter();OUT.mkdir(parents=True,exist_ok=True)
    parent=json.loads(PARENT.read_text());assert len(parent['assets_sha256'])==770
    for path,value in parent['assets_sha256'].items():assert sha(ROOT/path)==value,path
    cp=OUT/'GAWN24_interior_mixed_certificate.json';mp=OUT/'GAWN24_standalone_assets.json'
    if args.issue:
        assert not cp.exists() and not mp.exists()
        result=compute();cp.write_text(json.dumps(result,indent=2)+'\n')
        assets=dict(parent['assets_sha256'])
        additions=(PARENT,PARENT.parent/'GAWN23_readonly_validation02.json',
                   PARENT.parent/'GAWN23_readonly_run02.log',Path(__file__),
                   HERE/'GAWN24_INTERIOR_ALL_AGE_MIXED_PHASE_REPAIR.md',cp)
        for path in additions:assets[str(path.relative_to(ROOT))]=sha(path)
        failure=OUT/'GAWN24_failed_attempt01_provenance.json'
        fv=json.loads(failure.read_text())
        assert not fv['passed'] and fv['terminal_exit']==1 and not fv['mathematical_counterexample']
        assets[str(failure.relative_to(ROOT))]=sha(failure)
        for path,value in fv['source_and_log_sha256'].items():
            assert sha(ROOT/path)==value,path
            assets[path]=value
        manifest=dict(name=result['name'],inherited_assets=770,assets_sha256=assets,
            interior_all_Age_mixed_phase_complete2U_repair_proved=True,
            global_reliability_proved=False,rule_ROM_constants_CURRENT_changed=False)
        mp.write_text(json.dumps(manifest,indent=2)+'\n')
    else:
        manifest=json.loads(mp.read_text());assert manifest['inherited_assets']==770
        for path,value in parent['assets_sha256'].items():assert manifest['assets_sha256'][path]==value,path
        for path,value in manifest['assets_sha256'].items():assert sha(ROOT/path)==value,path
        result=compute()
        assert result==json.loads(cp.read_text()),'Fresh supplements differ'
    for path,value in manifest['assets_sha256'].items():assert sha(ROOT/path)==value,path
    print(json.dumps(dict(passed=True,issued=args.issue,readonly=not args.issue,
        assets=len(manifest['assets_sha256']),inherited_assets=770,
        all_new_native_gate_holder_and_phase_supplements_recomputed=True,
        interior_all_Age_mixed_phase_complete2U_repair_proved=True,
        maximum_last_fault=LAST,native_quiet_bound='max(L+10238,407552)',
        latest_native_quiet=k.U-1,global_reliability_proved=False,
        rule_ROM_constants_CURRENT_changed=False,certificate_sha256=sha(cp),
        manifest_sha256=sha(mp),elapsed=time.perf_counter()-start)),flush=True)
if __name__=='__main__':main()
