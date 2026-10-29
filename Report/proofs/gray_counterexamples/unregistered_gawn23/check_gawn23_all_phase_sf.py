"""Literal/integer supplements for the written all-phase SF-only burst proof.

No evolving U/2U physical simulation; selected compiled runs are supplements.
"""
import argparse,hashlib,itertools,json,random,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
OUT=ROOT/'figs/gray_counterexamples/unregistered_gawn23'
sys.path.insert(0,str(HERE.parent/'unregistered_gawn10'))
sys.path.insert(0,str(HERE.parent/'unregistered_gawn4'))
import check_gawn10_two_offset_projection as c
import check_late_sf_gawn4 as h
k=c.k;own=c.own;SF=c.SF
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def add(d,x):d.update((json.dumps(x,separators=(',',':'))+'\n').encode())
def raw(v):return [hex(z) for z in k.cell_words(v)]
def sf(rng):return {n:tuple(rng.getrandbits(c.WIDTHS.get(n,k.WORD)) for _ in k.SLOTS) for n in SF}
def native(v):return [getattr(v,n) for n in k.NATIVE_NAMES]
def geometry_and_flags():
    rng=random.Random(0x4741574e323301);dig=hashlib.sha256()
    phases=(0,1,2,3,4,5,k.Q-6,k.Q-5,k.Q-4,k.Q-3,k.Q-2,k.Q-1)
    ages=(0,k.U-1,32*k.Q-1,64*k.Q,72*k.Q+2,75*k.Q-1,
        80*k.Q-2,96*k.Q-1,96*k.Q,98*k.Q-1,99*k.Q,100*k.Q,127*k.Q)
    for index in range(320):
        x=phases[index%len(phases)];old=ages[index%len(ages)]
        cells={j:k.Cell(addr=(x+j)%k.Q,age=old,
            **{n:rng.randrange(2) for n in ('f1','f2','wf1','wf2')},**sf(rng)) for j in range(-8,9)}
        got=k.local_transition(cells,own.ROM)
        assert got.addr==x and got.age==(old+1)%k.U
        add(dig,[index,x,old,[raw(cells[j]) for j in range(-8,9)],native(got)])
    f1=hashlib.sha256();f2=hashlib.sha256();n1=n2=0
    for count in range(6):
        for bits in range(64):
            x=k.Q-1-count
            cells={j:dict(addr=(x+j)%k.Q,age=98*k.Q,f1=0,f2=rng.randrange(2),wf1=0,wf2=0) for j in range(-5,6)}
            cells[0]['f1']=bits&1
            for j in range(1,6):cells[j]['f1']=(bits>>j)&1
            total=sum(cells[j]['f1'] for j in range(1,count+1))
            got=k.scalar_native(cells)
            want=int(total>=3 or (cells[0]['f1'] and total>=2))
            assert got['f1']==want and (got['addr'],got['age'])==(x,98*k.Q+1)
            add(f1,[x,bits,total,got]);n1+=1
            x=count
            cells={j:dict(addr=(x+j)%k.Q,age=98*k.Q+k.Q//2,f1=0,f2=0,wf1=0,wf2=0) for j in range(-5,6)}
            cells[0]['f2']=bits&1
            for j in range(1,6):cells[-j]['f2']=(bits>>j)&1
            total=sum(cells[-j]['f2'] for j in range(1,count+1))
            got=k.scalar_native(cells)
            want=int(total>=4 or (cells[0]['f2'] and total>=2))
            assert got['f1']==0 and got['f2']==want and (got['addr'],got['age'])==(x,98*k.Q+k.Q//2+1)
            add(f2,[x,bits,total,got]);n2+=1
    assert (n1,n2)==(384,384)
    front=hashlib.sha256()
    for r in range(1,k.Q//2+1):
        length=2*r
        assert 2*(r-1)<k.Q and length<=k.Q
        # Each next pair has at most one positive neighbor inside its own
        # true colony; every guaranteed old zero remains zero.
        for positives in (0,1):
            for oldself in (0,1):
                assert not (positives>=3 or oldself and positives>=2)
                assert not (positives>=4 or oldself and positives>=2)
        add(front,[r,length,98*k.Q+r,98*k.Q+k.Q//2+r])
    assert 98*k.Q+k.Q==99*k.Q==405504<100*k.Q
    return dict(common_geometry_arbitrary_flag_SF_full_kernels=320,geometry_sha256=dig.hexdigest(),
        all6_mask_classes_times64_Flag1_cofactors=n1,Flag1_sha256=f1.hexdigest(),
        all6_mask_classes_times64_h1_Flag2_cofactors=n2,Flag2_sha256=f2.hexdigest(),
        simultaneous_front_arithmetic_rows=k.Q//2,front_sha256=front.hexdigest(),
        universal_stated_native_quiet_physical_row=99*k.Q)
def windows():
    intervals=[(s,s+8*k.Q+1) for s in k.GATHER_STARTS]
    dig=hashlib.sha256();counts=[0]*4
    for tau in range(k.U):
        last=min(k.U-1,tau+103)
        touched=[g for g,(lo,hi) in enumerate(intervals,1) if tau<=hi and last>=lo]
        assert len(touched)<=1
        counts[touched[0] if touched else 0]+=1
        add(dig,[tau,last,touched])
    assert sum(counts)==k.U
    assert all(intervals[g+1][0]-intervals[g][1]==24*k.Q-1==98303>103 for g in range(2))
    return dict(all_possible_first_fault_rows=k.U,max_window_rows=104,
        conservative_capture_fault_windows=intervals,zero_or_one_bank_start_counts=counts,
        all_window_rows_sha256=dig.hexdigest())
def captures():
    rng=random.Random(0x4741574e323302);dig=hashlib.sha256();configs=calls=0
    field_rows=(0,3,6,206,495)
    for bank in (1,2,3):
        for distance in range(9):
            age=k.capture(bank,8+distance)
            start=k.GATHER_STARTS[bank-1]
            assert age==start+1 if distance==0 else age==start+2+distance*k.Q
            if distance:assert age-1-(start+1)==distance*k.Q
            for colony in (-2,-1,1,2):
                for i in field_rows:
                    y=colony*k.Q+k.PRIMARY_START+i;cache={}
                    def snapshot(z):
                        if not 0<=z<k.Q:return h.intact_info(z)
                        key=('info',z)
                        if key not in cache:cache[key]=rng.getrandbits(k.WORD)
                        return cache[key]
                    def old_hist(z):
                        key=('hist',z)
                        if key not in cache:cache[key]=rng.getrandbits(17*k.WORD)
                        return cache[key]
                    state={}
                    for x in range(y-10,y+11):
                        words=sf(rng)
                        words['info']=tuple(snapshot(x+s) for s in k.SLOTS)
                        words['mail_l']=tuple(snapshot(x+s+distance*k.Q) for s in k.SLOTS)
                        words['mail_r']=tuple(snapshot(x+s-distance*k.Q) for s in k.SLOTS)
                        words['history'+str(bank)]=tuple(old_hist(x+s) for s in k.SLOTS)
                        state[x]=k.Cell(addr=x%k.Q,age=age-1,**words)
                    wanted=old_hist(y)
                    lanes=[lane for lane in range(17) if k.capture(bank,lane)==age]
                    assert lanes==[8] if distance==0 else lanes==[8-distance,8+distance]
                    for lane in lanes:
                        z=y+(lane-8)*k.Q
                        wanted=(wanted&~(k.MASK<<(lane*k.WORD)))|(snapshot(z)<<(lane*k.WORD))
                    outputs=[]
                    for q,s in enumerate(k.SLOTS):
                        x=y-s;got=k.local_transition({j:state[x+j] for j in range(-8,9)},own.ROM)
                        assert getattr(got,'history'+str(bank))[q]==wanted
                        assert got.addr==x%k.Q and got.age==age and got.f1==got.f2==0
                        outputs.append(raw(got));calls+=1
                    add(dig,[bank,distance,colony,i,age,lanes,[raw(state[x]) for x in range(y-10,y+11)],hex(wanted),outputs]);configs+=1
    assert (configs,calls)==(540,2700)
    return dict(selected_source_capture_configurations=configs,actual_full_kernel_calls=calls,
        all3_banks_all17_lanes_covered=True,old_mail_distances_checked=True,
        inputs_outputs_sha256=dig.hexdigest())
def temporal_loads():
    rng=random.Random(0x4741574e323303);dig=hashlib.sha256();configs=calls=0
    groups=list(itertools.combinations(range(5),3));irows=(0,1,3,4,5,6,206,495)
    for age in (k.EARLY_RESET,100*k.Q+1):
        for colony in (-2,-1,1,2):
            for badbank in (0,1,2,None):
                for i in irows:
                    for pattern in range(4):
                        y=colony*k.Q+k.PRIMARY_START+i;cache={}
                        def bank_value(bank,z):
                            key=(bank,z)
                            if key not in cache:
                                if bank==badbank:cache[key]=rng.getrandbits(17*k.WORD)
                                else:
                                    cache[key]=sum((rng.getrandbits(k.WORD) if 0<=z+j*k.Q<k.Q else h.intact_info(z+j*k.Q))<<((j+8)*k.WORD) for j in range(-8,9))
                            return cache[key]
                        good=groups[(pattern+i+colony)%10];state={}
                        for x in range(y-10,y+11):
                            words=sf(rng)
                            for bank in range(3):
                                words['history'+str(bank+1)]=tuple(bank_value(bank,x+s) if q in good else rng.getrandbits(17*k.WORD) for q,s in enumerate(k.SLOTS))
                            state[x]=k.Cell(addr=x%k.Q,age=age-1,**words)
                        bs=[bank_value(bank,y) for bank in range(3)]
                        wanted=k.majority3(*bs)
                        for j in range(-8,9):
                            if colony+j!=0:assert (wanted>>((j+8)*k.WORD))&k.MASK==h.intact_info(y+j*k.Q)
                        outputs=[]
                        for q,s in enumerate(k.SLOTS):
                            x=y-s;got=k.local_transition({j:state[x+j] for j in range(-8,9)},own.ROM)
                            assert got.mem[q]==wanted
                            assert native(got)==[x%k.Q,age,0,0,0,0]
                            outputs.append(raw(got));calls+=1
                        add(dig,[age,colony,badbank,i,pattern,list(good),[raw(state[x]) for x in range(y-10,y+11)],hex(wanted),outputs]);configs+=1
    assert (configs,calls)==(1024,5120)
    return dict(selected_actual_temporal_Mem_load_configurations=configs,actual_full_kernel_calls=calls,
        old_raw_History_coherence_assumed=False,all3_bad_bank_roles_plus_no_bad_bank=True,
        each_nonzero_source_upper_record_restored=True,inputs_outputs_sha256=dig.hexdigest())
def executions():
    rng=random.Random(0x4741574e323304);dig=hashlib.sha256();records=[]
    for colony in (-2,-1,1,2):
        for badbank in (0,2):
            tape={}
            for i in range(k.FRAME_WORDS):
                y=colony*k.Q+k.PRIMARY_START+i;values=[]
                for bank in range(3):
                    if bank==badbank:values.append(rng.getrandbits(17*k.WORD))
                    else:values.append(sum((rng.getrandbits(k.WORD) if colony+j==0 else h.intact_info(y+j*k.Q))<<((j+8)*k.WORD) for j in range(-8,9)))
                tape[k.PRIMARY_START+i]=k.majority3(*values)
                for j in range(-8,9):
                    if colony+j!=0:assert (tape[k.PRIMARY_START+i]>>((j+8)*k.WORD))&k.MASK==k.cell_words(h.H(colony+j))[i]
            expected=k.cell_words(h.C1(colony));outputs=[];costs=[]
            for early in (True,False):
                out,ticks,packet,trace=k.execute(own.ROM,tape,limit=110591,early=early)
                assert packet.mode==k.HALT
                count=6 if early else k.FRAME_WORDS
                wanted={k.PRIMARY_START+i:expected[i] for i in range(count)}
                assert out==wanted,(colony,badbank,early,'compiled output differs')
                assert ticks<=(221 if early else 104572)
                outputs.append([[a,hex(v)] for a,v in sorted(out.items())]);costs.append(ticks)
            add(dig,[colony,badbank,[[a,hex(v)] for a,v in sorted(tape.items())],costs,outputs])
            records.append(dict(colony=colony,badbank=badbank,early_ticks=costs[0],late_ticks=costs[1]))
    return dict(selected_derived_tapes=8,actual_early_runs=8,actual_complete_late_runs=8,
        whole496_output_words_equal_actual_C1=True,records=records,inputs_outputs_sha256=dig.hexdigest(),
        universal_evaluator_bound_source='GAWN2 S1; selected executions do not supply the universal bound')
def courier_boundaries():
    rng=random.Random(0x4741574e323305);dig=hashlib.sha256();calls=0
    for p0,p1 in ((-k.Q,k.Q),(0,2*k.Q)):
        for y in (p0-2,p0-1,p1,p1+1):
            for age in (75*k.Q,75*k.Q+1,80*k.Q-2):
                state={}
                def cv(z):return rng.getrandbits(k.WORD) if p0<=z<p1 else 0
                cache={}
                def val(n,z):
                    key=(n,z)
                    if key not in cache:cache[key]=cv(z)
                    return cache[key]
                for x in range(y-10,y+11):
                    words=sf(rng)
                    for n in ('courier_l','courier_r','out'):words[n]=tuple(val(n,x+s) for s in k.SLOTS)
                    state[x]=k.Cell(addr=x%k.Q,age=age-1,**words)
                outputs=[]
                for q,s in enumerate(k.SLOTS):
                    x=y-s;got=k.local_transition({j:state[x+j] for j in range(-8,9)},own.ROM)
                    assert got.courier_l[q]==got.courier_r[q]==0
                    outputs.append(raw(got));calls+=1
                add(dig,[p0,p1,y,age,[raw(state[x]) for x in range(y-10,y+11)],outputs])
    assert calls==120
    return dict(selected_actual_courier_pair_boundary_full_kernels=calls,
                arbitrary_inside_pair_couriers_do_not_cross=True,inputs_outputs_sha256=dig.hexdigest())
def compute():
    g=geometry_and_flags();w=windows();cap=captures();m=temporal_loads();e=executions();b=courier_boundaries()
    p22=ROOT/'figs/gray_counterexamples/unregistered_gawn22/GAWN22_all_age_late_certificate.json'
    old=json.loads(p22.read_text());assert old['protected_pair_all13_logical_SF_confinement_proved']
    sources=(Path(__file__),HERE/'GAWN23_ALL_PHASE_SF_BURST_REPAIR.md',
        HERE.parent/'unregistered_gawn2/small_rule_gawn2.py',
        HERE.parent/'unregistered_gawn2/GAWN2_HALF_SCALE_NOISELESS_PERIOD.md',
        HERE.parent/'unregistered_gawn4/GAWN4_LATE_SF_BURST_REPAIR.md',
        HERE.parent/'unregistered_gawn19/GAWN19_EARLY_MIXED_BURST_CURRENT_PERIOD_REPAIR.md',
        HERE.parent/'unregistered_gawn22/GAWN22_ALL_AGE_LATE_PAIR_REPAIR.md',p22)
    return dict(name='GAWN23 all-phase SF-only fixed104-site104-row burst complete2U repair',passed=True,
        Q=k.Q,U=k.U,lambda_original=24,error_separation=104,unchanged_GAWN2_all_Gray_departures_required=True,
        initial_actual_recursive_H2_required=True,fixed_support_inside_true_colony0_width_at_most104=True,
        all_first_fault_phases_inclusive=[0,k.U-1],last_possible_fault_before_actual_U_required=True,
        burst_after_row_duration_at_most104=True,all13_SF_arbitrary_adaptive=True,
        all6_actual_native_fields_retained=True,no_other_errors_required=True,
        actual_common_GF_Age_and_native99Q_quiet_proved=True,
        protected_pair_Head_endpoints_proved=True,
        at_most_one_transported_bad_bank_outside_pair_proved=True,
        two_snapshot_banks_restore_all_nonzero_source_records_proved=True,
        derived_each_outside_evaluator_tape_only_record0_arbitrary_proved=True,
        global_consistency_of_erroneous_record0_across_evaluators_assumed=False,
        actual_early_late_preparation_and_completed_outside_pair_Out_proved=True,
        all_SF_private_execution_shadow_equality_claimed=False,
        actual_complete_U_D_encoding_and2U_alllater_equality_proved=True,
        original_error_class_from_geometry_assigned=False,
        general_native_changing_longer_moving_multiple_E0_higher_iid_memory_proved=False,
        faithful_Gray_G17_refutation_or_minimum_sufficient_fix_proved=False,
        evolving_physical_U_2U_simulation_performed=False,rule_ROM_constants_CURRENT_changed=False,
        common_geometry_and_flag_front=g,all_phase_capture_windows=w,literal_captures=cap,
        literal_temporal_loads=m,selected_compiled_executions=e,literal_courier_boundaries=b,
        inherited_all_clock_endpoint_configurations=old['all_clock_endpoint']['selected_endpoint_configurations'],
        inherited_actual_U_commit_kernels=old['actual_U_commit']['actual_age0_common_native_incoherent_raw_work_full_kernel_calls'],
        source_sha256={str(p.relative_to(ROOT)):sha(p) for p in sources})
def main():
    p=argparse.ArgumentParser();p.add_argument('--issue',action='store_true');args=p.parse_args()
    start=time.perf_counter();OUT.mkdir(parents=True,exist_ok=True)
    pp=ROOT/'figs/gray_counterexamples/unregistered_gawn22/GAWN22_standalone_assets.json'
    parent=json.loads(pp.read_text());assert len(parent['assets_sha256'])==760
    cp=OUT/'GAWN23_all_phase_SF_certificate.json';mp=OUT/'GAWN23_standalone_assets.json'
    for path,value in parent['assets_sha256'].items():assert sha(ROOT/path)==value,path
    if args.issue:
        assert not cp.exists() and not mp.exists()
        result=compute();cp.write_text(json.dumps(result,indent=2)+'\n')
        assets=dict(parent['assets_sha256'])
        for path in (pp,ROOT/'figs/gray_counterexamples/unregistered_gawn22/GAWN22_readonly_run01.log',
                     Path(__file__),HERE/'GAWN23_ALL_PHASE_SF_BURST_REPAIR.md',cp):assets[str(path.relative_to(ROOT))]=sha(path)
        manifest=dict(name=result['name'],inherited_assets=760,assets_sha256=assets,
            universal_stated_all_phase_SF_only_complete2U_repair_proved=True,
            global_reliability_proved=False,rule_ROM_constants_CURRENT_changed=False)
        mp.write_text(json.dumps(manifest,indent=2)+'\n')
    else:
        manifest=json.loads(mp.read_text());assert manifest['inherited_assets']==760
        for path,value in parent['assets_sha256'].items():assert manifest['assets_sha256'][path]==value,path
        for path,value in manifest['assets_sha256'].items():assert sha(ROOT/path)==value,path
        result=compute();assert result==json.loads(cp.read_text()),'Fresh supplements differ'
    for path,value in manifest['assets_sha256'].items():assert sha(ROOT/path)==value,path
    print(json.dumps(dict(passed=True,issued=args.issue,readonly=not args.issue,
        assets=len(manifest['assets_sha256']),inherited_assets=760,
        all_new_geometry_flag_window_capture_Mem_execution_courier_supplements_recomputed=True,
        all_stated_all_phase_SF_only_complete2U_repair_proved=True,
        all524288_first_fault_phases_checked=True,native_quiet_physical_row=99*k.Q,
        global_reliability_proved=False,rule_ROM_constants_CURRENT_changed=False,
        certificate_sha256=sha(cp),manifest_sha256=sha(mp),elapsed=time.perf_counter()-start)),flush=True)
if __name__=='__main__':main()
