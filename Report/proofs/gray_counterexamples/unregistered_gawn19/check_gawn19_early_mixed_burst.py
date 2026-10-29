"""Finite supplements to the new early native/Info/current-U proof.

No evolving14337-step full-SF trajectory, physical-U run or iid theorem.
"""
import argparse,hashlib,json,random,sys,time
from dataclasses import replace
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
OUT=ROOT/'figs/gray_counterexamples/unregistered_gawn19'
sys.path.insert(0,str(HERE.parent/'unregistered_gawn10'))
import check_gawn10_two_offset_projection as c
sys.path.insert(0,str(HERE.parent/'unregistered_gawn4'))
import check_late_sf_gawn4 as h
k=c.k;own=c.own;DELTA=100*k.Q+1;R=14337
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def add(d,x):d.update((json.dumps(x,separators=(',',':'))+'\n').encode())
def native(v):return [getattr(v,n) for n in k.NATIVE_NAMES]
def raw(v):return [hex(z) for z in k.cell_words(v)]
def compute():
    rng=random.Random(0x4741574e313901);scalar_digest=hashlib.sha256();scalars=0
    for x in range(k.Q):
        for pattern in range(4):
            t=1+(x+pattern*257)%14440
            cells={j:dict(addr=(x+j)%k.Q,age=t+(j*j+pattern*23+x)%105,
                **{n:((x+(j+5)*17+pattern*31)>>(index%6))&1
                   for index,n in enumerate(('f1','f2','wf1','wf2'))}) for j in range(-5,6)}
            translated={j:{**v,'age':v['age']+DELTA} for j,v in cells.items()}
            a=k.scalar_native(cells);b=k.scalar_native(translated)
            assert a['addr']==b['addr']==x
            assert b['age']==a['age']+DELTA
            assert all(a[n]==b[n] for n in ('f1','f2','wf1','wf2'))
            add(scalar_digest,[x,pattern,t,list(cells.values()),a,b]);scalars+=1
    full=hashlib.sha256();full_cases=0
    for index in range(256):
        x=(0,1,2,3,4,5,k.Q-5,k.Q-3,k.Q-1,index*31%k.Q)[index%10]
        t=1+(index*59)%14440;early={};late={}
        for j in range(-8,9):
            n=dict(addr=(x+j)%k.Q,age=t+rng.randrange(105),
                **{name:rng.randrange(2) for name in ('f1','f2','wf1','wf2')})
            sf=lambda:{name:tuple(rng.getrandbits(c.WIDTHS.get(name,k.WORD)) for _ in k.SLOTS) for name in c.SF}
            early[j]=k.Cell(**n,**sf())
            late[j]=k.Cell(**{**n,'age':n['age']+DELTA},**sf())
        a=k.local_transition(early,own.ROM);b=k.local_transition(late,own.ROM)
        assert a.addr==b.addr==x and b.age==a.age+DELTA
        assert native(b)==[a.addr,a.age+DELTA,a.f1,a.f2,0,0]
        assert a.wf1==a.wf2==0
        assert a.age<=14545<96*k.Q and b.age>=100*k.Q+3>98*k.Q
        add(full,[x,t,[raw(early[j]) for j in range(-8,9)],
            [raw(late[j]) for j in range(-8,9)],native(a),native(b)])
        full_cases+=1
    single=hashlib.sha256();single_cases=0
    for case in range(64):
        # Full D replacement, including arbitrary native representation padding.
        words=[rng.getrandbits(k.WORD) for _ in range(k.FRAME_WORDS)]
        v=k.cell_from_words(words)
        for x in range(-8,9):
            dirty={j:v if x+j==0 else h.H(x+j) for j in range(-8,9)}
            got=k.local_transition(dirty,own.ROM);expected=h.C1(x)
            assert got==expected,(case,x,native(got),native(expected))
            add(single,[case,x,[hex(z) for z in words],raw(got)])
            single_cases+=1
    assert single_cases==64*17==1088
    holders=hashlib.sha256();holder_cases=intervals=0
    for b in range(k.Q):
        for width in range(1,min(104,k.Q-b)+1):
            end=b+width
            for y in (b-3,b-2,b-1,end,end+1,end+2):
                count=sum(b<=y-s<end for s in k.SLOTS)
                assert count<=2
                add(holders,[b,width,y,count]);holder_cases+=1
            intervals+=1
    # All farther exterior coordinates have still fewer interval intersections.
    assert intervals==sum(min(104,k.Q-b) for b in range(k.Q))==420628
    assert holder_cases==6*intervals==2523768
    deadlines=[]
    for d in range(104):
        last=1+d;q=last+R
        assert q+104<96*k.Q and 1<=q<32*k.Q
        assert 96*k.Q-1<=1+DELTA and 1+d+104+DELTA<=k.U-4*k.Q-1
        assert 98*k.Q<1+DELTA and q+104+DELTA<k.U
        deadlines.append([d,last,q,q+104,q+104+DELTA])
    assert deadlines[-1]==[103,104,14441,14545,424146]
    p18=ROOT/'figs/gray_counterexamples/unregistered_gawn18/GAWN18_two_good_gathers_certificate.json'
    antecedent=json.loads(p18.read_text())
    assert antecedent['complete_current_U_boundary_conditional_repair_proved']
    sources=(Path(__file__),HERE/'GAWN19_EARLY_MIXED_BURST_CURRENT_PERIOD_REPAIR.md',
        HERE.parent/'unregistered_gawn2/small_rule_gawn2.py',
        HERE.parent/'unregistered_gawn9/GAWN9_LATE_MIXED_BURST_PAIR_REPAIR.md',
        HERE.parent/'unregistered_gawn18/GAWN18_TWO_GOOD_GATHERS_REPAIR.md',p18)
    return dict(name='GAWN19 early bounded-clock mixed bursts complete current-U repair',passed=True,
        Q=k.Q,U=k.U,lambda_original=24,error_separation=104,
        unchanged_GAWN2_all_Gray_departures_required=True,
        initial_actual_H2_physical_row=1,after_row_fault_window_maximum=[1,104],
        fixed_interval_in_true_colony0_max_width=104,maximum_additional_fault_rows=103,
        Address_retained=True,replacement_Age_at_row_t_inclusive='[t,t+104]',
        all4_flags_all13_SF_arbitrary_adaptive=True,no_other_errors_required=True,
        clock_translation=DELTA,native_recovery_after_last_possible_fault=R,
        latest_native_quiet_physical_row=14441,largest_early_raw_clock_bound=14545,
        largest_translated_clock_bound=424146,translated_replacement_clock_range=[409602,409809],
        whole_word_closed_native_clock_covariance_proved=True,
        universal_stated_early_native_recovery_proved=True,
        voted_Info_damage_confined_to_interval_A_proved=True,
        arbitrary_D_single_upper_cell_at_H2_one_update_correction_proved=True,
        complete_actual_current_U_and_all_later_repair_proved=True,
        early_to_late_full_SF_schedule_or_full_history_correspondence_claimed=False,
        original_error_class_from_support_geometry_assigned=False,
        arbitrary_GF_Age_other_phases_E0surroundings_higher_iid_memory_proved=False,
        faithful_Gray_G17_refutation_or_minimum_sufficient_fix_proved=False,
        evolving_fullSF14337step_or_physicalU_simulation_performed=False,
        rule_ROM_constants_CURRENT_changed=False,
        selected_scalar_covariance_pairs=scalars,scalar_covariance_sha256=scalar_digest.hexdigest(),
        selected_allSF_full_kernel_covariance_pairs=full_cases,
        full_kernel_covariance_inputs_outputs_sha256=full.hexdigest(),
        actual_H2_single_D_upper_fault_full_kernel_cases=single_cases,
        single_upper_fault_inputs_outputs_sha256=single.hexdigest(),
        all_contiguous_intervals=intervals,exterior_boundary_holder_cases=holder_cases,
        exterior_holder_count_sha256=holders.hexdigest(),fault_window_deadline_rows=deadlines,
        source_sha256={str(p.relative_to(ROOT)):sha(p) for p in sources})
def main():
    p=argparse.ArgumentParser();p.add_argument('--issue',action='store_true');args=p.parse_args()
    start=time.perf_counter();OUT.mkdir(parents=True,exist_ok=True)
    pp=ROOT/'figs/gray_counterexamples/unregistered_gawn18/GAWN18_standalone_assets.json'
    parent=json.loads(pp.read_text());assert len(parent['assets_sha256'])==740
    cp=OUT/'GAWN19_early_mixed_burst_certificate.json';mp=OUT/'GAWN19_standalone_assets.json'
    for path,value in parent['assets_sha256'].items():assert sha(ROOT/path)==value,path
    if args.issue:
        assert not cp.exists() and not mp.exists()
        result=compute();cp.write_text(json.dumps(result,indent=2)+'\n')
        assets=dict(parent['assets_sha256'])
        for path in (pp,ROOT/'figs/gray_counterexamples/unregistered_gawn18/GAWN18_readonly_run01.log',
                     Path(__file__),HERE/'GAWN19_EARLY_MIXED_BURST_CURRENT_PERIOD_REPAIR.md',cp):
            assets[str(path.relative_to(ROOT))]=sha(path)
        manifest=dict(name=result['name'],inherited_assets=740,assets_sha256=assets,
            universal_stated_early_burst_complete_current_U_repair_proved=True,
            global_reliability_proved=False,rule_ROM_constants_CURRENT_changed=False)
        mp.write_text(json.dumps(manifest,indent=2)+'\n')
    else:
        manifest=json.loads(mp.read_text());assert manifest['inherited_assets']==740
        for path,value in parent['assets_sha256'].items():assert manifest['assets_sha256'][path]==value,path
        for path,value in manifest['assets_sha256'].items():assert sha(ROOT/path)==value,path
        result=compute();assert result==json.loads(cp.read_text()),'Fresh supplements differ'
    for path,value in manifest['assets_sha256'].items():assert sha(ROOT/path)==value,path
    print(json.dumps(dict(passed=True,issued=args.issue,readonly=not args.issue,
        assets=len(manifest['assets_sha256']),inherited_assets=740,
        all_new_covariance_single_upper_holder_clock_bound_checks_recomputed=True,
        complete_actual_current_U_and_all_later_repair_proved=True,
        native_deadline_after_last_fault=R,latest_native_quiet=14441,
        global_reliability_proved=False,rule_ROM_constants_CURRENT_changed=False,
        certificate_sha256=sha(cp),manifest_sha256=sha(mp),elapsed=time.perf_counter()-start)),flush=True)
if __name__=='__main__':main()
