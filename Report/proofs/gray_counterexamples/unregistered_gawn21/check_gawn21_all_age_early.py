"""Finite all-Age gate/front/holder supplements; written proof is universal.

No evolving10238-step full-SF trajectory or physical-U simulation.
"""
import argparse,hashlib,itertools,json,random,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
OUT=ROOT/'figs/gray_counterexamples/unregistered_gawn21'
sys.path.insert(0,str(HERE.parent/'unregistered_gawn10'))
import check_gawn10_two_offset_projection as c
k=c.k;own=c.own;R0=k.Q-2;CLOCK=2*k.Q-2;R=CLOCK+k.Q//2
LAST=32*k.Q-1-R
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def add(d,x):d.update((json.dumps(x,separators=(',',':'))+'\n').encode())
def native(v):return [getattr(v,n) for n in k.NATIVE_NAMES]
def raw(v):return [hex(z) for z in k.cell_words(v)]
def sf(rng):
    return {name:tuple(rng.getrandbits(c.WIDTHS.get(name,k.WORD)) for _ in k.SLOTS) for name in c.SF}
def scalar_cells(x,t):
    return {j:dict(addr=(x+j)%k.Q,age=t,f1=0,f2=0,wf1=0,wf2=0) for j in range(-5,6)}
def tags(cells,cats,t):
    for j,cat in enumerate(cats,1):
        cells[j]['age']=t if cat<2 else (0,k.U-1,96*k.Q-1,98*k.Q-1)[j%4]
        assert cat<2 or cells[j]['age']!=t
        cells[j]['f1']=int(cat>0)
def compute():
    rng=random.Random(0x4741574e323101)
    tagged=hashlib.sha256();tagged_n=0
    phases=(0,1,2,3,4,5,k.Q-6,k.Q-5,k.Q-4,k.Q-3,k.Q-2,k.Q-1)
    critical=(0,k.U-1,96*k.Q-1,96*k.Q,98*k.Q-1,72*k.Q+3,80*k.Q-2)
    for index in range(320):
        x=phases[index%len(phases)];theta=(2,104,10342,120833,131071)[index%5]
        cells={}
        for j in range(-8,9):
            inside=0<=x+j<k.Q
            flags={name:rng.randrange(2) if inside else 0 for name in ('f1','f2','wf1','wf2')}
            if -k.Q<=x+j<0:flags['f1']=rng.randrange(2)
            age=critical[(index+j)%len(critical)] if inside else theta-1
            if 1<=j<=5:
                cat=rng.randrange(3) if inside else 0
                age=theta-1 if cat<2 else age
                flags['f1']=int(cat>0)
            cells[j]=k.Cell(addr=(x+j)%k.Q,age=age,**flags,**sf(rng))
        got=k.local_transition(cells,own.ROM)
        assert got.addr==x and (got.age==theta or got.f1==1)
        assert got.wf2==0,(index,x,theta,native(got))
        add(tagged,[index,x,theta,[raw(cells[j]) for j in range(-8,9)],native(got)]);tagged_n+=1
    assert tagged_n==320
    controls=hashlib.sha256();control_n=0
    for x in range(5):
        for f1 in (0,1):
            cells={j:k.Cell(addr=(x+j)%k.Q,age=96*k.Q-1,
                f1=f1 if 0<=x+j<k.Q else 0,
                info=(1,)*5,**{name:sf(rng)[name] for name in c.SF if name!='info'}) for j in range(-8,9)}
            got=k.local_transition(cells,own.ROM)
            assert got.age==96*k.Q and got.f1==f1 and got.wf2==1-f1
            add(controls,[x,f1,[raw(cells[j]) for j in range(-8,9)],native(got)]);control_n+=1
    x=k.Q-5
    cells={j:k.Cell(addr=(x+j)%k.Q,age=96*k.Q-1,
        f1=int(0<=x+j<k.Q),info=(1,)*5) for j in range(-8,9)}
    got=k.local_transition(cells,own.ROM)
    assert got.f1==1 and got.wf1==1 and got.wf2==0
    add(controls,[x,[raw(cells[j]) for j in range(-8,9)],native(got)]);control_n+=1
    assert control_n==11
    first=hashlib.sha256();first_n=0
    for x in (0,1,2):
        internal=tuple(j for j in range(-5,0) if x+j>=0)
        for left in itertools.product((0,k.U-1,96*k.Q-1,98*k.Q-1),repeat=len(internal)):
            for cats in itertools.product(range(3),repeat=5):
                for self_bits in range(4):
                    for wf1 in (0,1):
                        t=4096;cells=scalar_cells(x,t);tags(cells,cats,t)
                        for j,v in zip(internal,left):cells[j]['age']=v
                        for j in cells:cells[j]['wf1']=wf1
                        cells[0].update(age=k.U-1,f1=self_bits&1,f2=(self_bits>>1)&1)
                        got=k.scalar_native(cells)
                        assert got['f2']==0 and got['age']==t+1 and got['addr']==x
                        add(first,[x,left,cats,self_bits,wf1,got]);first_n+=1
    assert first_n==21*243*4*2==40824
    prefix=hashlib.sha256();prefix_n=0
    for x in (3,4,5,k.Q-1):
        for right in itertools.product((0,k.U-1,96*k.Q-1,8189),repeat=5):
            for self_bits in range(4):
                for wf1 in (0,1):
                    t=8189;cells=scalar_cells(x,t)
                    for j,v in enumerate(right,1):cells[j]['age']=v
                    for j in cells:cells[j]['wf1']=wf1
                    cells[0].update(age=k.U-1,f1=self_bits&1,f2=(self_bits>>1)&1)
                    got=k.scalar_native(cells)
                    assert got['f2']==0 and got['age']==t+1 and got['addr']==x
                    add(prefix,[x,right,self_bits,wf1,got]);prefix_n+=1
    assert prefix_n==4*4**5*4*2==32768
    front=hashlib.sha256();front_n=0
    for x in range(k.Q):
        for pattern in range(8):
            cells=scalar_cells(x,8189)
            for j,v in cells.items():
                v.update(age=(0,k.U-1,96*k.Q-1,8189)[(j+pattern)%4],
                    f1=(x+j+pattern)&1,wf1=(pattern>>2)&1)
                if j>=0:v['f2']=(pattern>>1)&1
            got=k.scalar_native(cells);assert got['f2']==0 and got['addr']==x
            add(front,[x,pattern,got]);front_n+=1
    assert front_n==8*k.Q==32768
    holder=hashlib.sha256();holder_n=outside_n=0
    def info(y):return ((y+1000033)*0x987654321abcdef1234567)&k.MASK
    for y in (-2,-1,k.Q,k.Q+1):
        outside_slots=tuple(s for s in k.SLOTS if not 0<=y-s<k.Q)
        assert len(outside_slots)>=3
        for theta in (2,104,10342,120833,131071):
            for pattern in range(8):
                global_cells={}
                for x in range(y-10,y+11):
                    inside=0<=x<k.Q
                    flags={name:rng.randrange(2) if inside else 0 for name in ('f1','f2','wf1','wf2')}
                    if -k.Q<=x<0:flags['f1']=rng.randrange(2)
                    words=sf(rng)
                    words['info']=tuple(rng.getrandbits(k.WORD) if inside else info(x+s) for s in k.SLOTS)
                    global_cells[x]=k.Cell(addr=x%k.Q,
                        age=critical[(x+pattern)%len(critical)] if inside else theta-1,
                        **flags,**words)
                values=[]
                for s in k.SLOTS:
                    x=y-s;cells={j:global_cells[x+j] for j in range(-8,9)}
                    got=k.local_transition(cells,own.ROM);value=got.info[k.SLOTS.index(s)];values.append(value)
                    if s in outside_slots:
                        assert got.addr==x%k.Q and got.age==theta and got.wf1==got.wf2==0
                        assert value==info(y),(y,theta,pattern,s,value,info(y));outside_n+=1
                    add(holder,[y,theta,pattern,s,[raw(cells[j]) for j in range(-8,9)],native(got),hex(value)]);holder_n+=1
                assert sum(v==info(y) for v in values)>=3
    assert (holder_n,outside_n)==(800,560)
    deadline=hashlib.sha256();deadline_n=0
    for last in range(1,LAST+1):
        q=last+R
        assert 1<=last<=120833 and q<=131071<96*k.Q and q<=32*k.Q-1
        add(deadline,[last,last+R0,last+CLOCK,q]);deadline_n+=1
    assert (R0,CLOCK,R,LAST,deadline_n)==(4094,8190,10238,120833,120833)
    prefix_rows=[]
    for s in range(3,k.Q+1):
        r=R0+s
        assert r>=4097 and r<=8190 and s==min(k.Q,r-R0)
        prefix_rows.append([s,r,s])
    assert len(prefix_rows)==4094 and prefix_rows[-1]==[4096,8190,4096]
    p18=ROOT/'figs/gray_counterexamples/unregistered_gawn18/GAWN18_two_good_gathers_certificate.json'
    p19=ROOT/'figs/gray_counterexamples/unregistered_gawn19/GAWN19_early_mixed_burst_certificate.json'
    assert json.loads(p18.read_text())['complete_current_U_boundary_conditional_repair_proved']
    assert json.loads(p19.read_text())['arbitrary_D_single_upper_cell_at_H2_one_update_correction_proved']
    sources=(Path(__file__),HERE/'GAWN21_ALL_AGE_EARLY_ONE_COLONY_REPAIR.md',
        HERE.parent/'unregistered_gawn2/small_rule_gawn2.py',
        HERE.parent/'unregistered_gawn6/GAWN6_CANONICAL_ADDRESS_CLOCK_CONFINEMENT.md',
        HERE.parent/'unregistered_gawn7/GAWN7_FLAG2_DEADLINE_AND_FIVE_CLOCK_REDUCTION.md',
        HERE.parent/'unregistered_gawn8/GAWN8_TAGGED_SUFFIX_AND_UNIVERSAL_LATE_REPAIR.md',
        HERE.parent/'unregistered_gawn18/GAWN18_TWO_GOOD_GATHERS_REPAIR.md',
        HERE.parent/'unregistered_gawn19/GAWN19_EARLY_MIXED_BURST_CURRENT_PERIOD_REPAIR.md',p18,p19)
    return dict(name='GAWN21 all-Age early one-colony address-preserving current-period repair',passed=True,
        Q=k.Q,U=k.U,lambda_original=24,error_separation=104,
        unchanged_GAWN2_all_Gray_departures_required=True,initial_actual_H2_physical_row=1,
        maximum_last_possible_after_row_fault=LAST,arbitrary_subset_of_entire_true_colony0_allowed=True,
        Address_retained=True,all_legal_replacement_Age_inclusive=[0,k.U-1],
        all4_flags_all13_SF_arbitrary_adaptive=True,no_other_errors_required=True,
        arbitrary_clock_wrap_and_computed_age0_inside_allowed=True,
        tagged_normal_output_implies_actual_Workspace2_zero_proved=True,
        global_Workspace2_zero_after_last_possible_fault=R0,
        global_Workspace1_zero_at_that_tag_deadline_claimed=False,
        native_clock_recovery_after_last_possible_fault=CLOCK,
        native_complete_recovery_after_last_possible_fault=R,
        latest_native_quiet_physical_row=32*k.Q-1,
        universal_stated_early_native_recovery_proved=True,
        voted_Info_damage_confined_to_true_colony_I_proved=True,
        complete_actual_current_U_and_all_later_repair_proved=True,
        global_inside_clock_range_or_closed_Workspace_guard_assumed=False,
        original_error_class_from_support_geometry_assigned=False,
        arbitrary_GF_multiple_colonies_late_phases_E0_higher_iid_memory_proved=False,
        faithful_Gray_G17_refutation_or_minimum_sufficient_fix_proved=False,
        evolving_fullSF10238step_or_physicalU_simulation_performed=False,
        rule_ROM_constants_CURRENT_changed=False,
        tagged_arbitrary_SF_full_kernel_comparisons=tagged_n,
        tagged_actual_Workspace2_zero_inputs_outputs_sha256=tagged.hexdigest(),
        actual_Workspace2_positive_negative_and_Workspace1_positive_controls=control_n,
        actual_Workspace_gate_controls_sha256=controls.hexdigest(),
        first_three_WF1_allowed_clock_cofactors=first_n,first_three_clock_sha256=first.hexdigest(),
        correct_left_WF1_allowed_prefix_cofactors=prefix_n,correct_left_prefix_sha256=prefix.hexdigest(),
        h1_WF1_allowed_Flag2_zero_front_cofactors=front_n,h1_Flag2_zero_front_sha256=front.hexdigest(),
        exterior_Info_holder_full_kernel_comparisons=holder_n,
        clean_outside_physical_holder_comparisons=outside_n,
        exterior_Info_holder_inputs_outputs_sha256=holder.hexdigest(),
        all_last_fault_deadline_rows_checked=deadline_n,last_fault_deadline_rows_sha256=deadline.hexdigest(),
        clock_prefix_integer_rows=prefix_rows,
        source_sha256={str(p.relative_to(ROOT)):sha(p) for p in sources})
def main():
    p=argparse.ArgumentParser();p.add_argument('--issue',action='store_true');args=p.parse_args()
    start=time.perf_counter();OUT.mkdir(parents=True,exist_ok=True)
    pp=ROOT/'figs/gray_counterexamples/unregistered_gawn20/GAWN20_standalone_assets.json'
    parent=json.loads(pp.read_text());assert len(parent['assets_sha256'])==750
    cp=OUT/'GAWN21_all_age_early_certificate.json';mp=OUT/'GAWN21_standalone_assets.json'
    for path,value in parent['assets_sha256'].items():assert sha(ROOT/path)==value,path
    if args.issue:
        assert not cp.exists() and not mp.exists()
        result=compute();cp.write_text(json.dumps(result,indent=2)+'\n')
        assets=dict(parent['assets_sha256'])
        for path in (pp,ROOT/'figs/gray_counterexamples/unregistered_gawn20/GAWN20_readonly_run01.log',
                     Path(__file__),HERE/'GAWN21_ALL_AGE_EARLY_ONE_COLONY_REPAIR.md',cp):
            assets[str(path.relative_to(ROOT))]=sha(path)
        manifest=dict(name=result['name'],inherited_assets=750,assets_sha256=assets,
            universal_stated_all_Age_early_one_colony_current_U_repair_proved=True,
            global_reliability_proved=False,rule_ROM_constants_CURRENT_changed=False)
        mp.write_text(json.dumps(manifest,indent=2)+'\n')
    else:
        manifest=json.loads(mp.read_text());assert manifest['inherited_assets']==750
        for path,value in parent['assets_sha256'].items():assert manifest['assets_sha256'][path]==value,path
        for path,value in manifest['assets_sha256'].items():assert sha(ROOT/path)==value,path
        result=compute();assert result==json.loads(cp.read_text()),'Fresh supplements differ'
    for path,value in manifest['assets_sha256'].items():assert sha(ROOT/path)==value,path
    print(json.dumps(dict(passed=True,issued=args.issue,readonly=not args.issue,
        assets=len(manifest['assets_sha256']),inherited_assets=750,
        all_new_native_gate_holder_integer_supplements_recomputed=True,
        all_legal_Age_early_one_colony_complete_current_U_repair_proved=True,
        maximum_last_fault=LAST,Workspace2_deadline=R0,clock_deadline=CLOCK,
        native_deadline=R,latest_native_quiet=32*k.Q-1,
        global_reliability_proved=False,rule_ROM_constants_CURRENT_changed=False,
        certificate_sha256=sha(cp),manifest_sha256=sha(mp),elapsed=time.perf_counter()-start)),flush=True)
if __name__=='__main__':main()
