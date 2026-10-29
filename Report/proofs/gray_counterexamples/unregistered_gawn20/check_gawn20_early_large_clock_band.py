"""Finite transcription supplements to GAWN20's written word proof.

No evolving full-SF repair trajectory, U-tick simulation or iid theorem.
"""
import argparse,hashlib,itertools,json,random,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
OUT=ROOT/'figs/gray_counterexamples/unregistered_gawn20'
sys.path.insert(0,str(HERE.parent/'unregistered_gawn10'))
import check_gawn10_two_offset_projection as c
k=c.k;own=c.own;CLOCK=2*k.Q-4;R=CLOCK+k.Q//2
B=96*k.Q-(104+R)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def add(d,x):d.update((json.dumps(x,separators=(',',':'))+'\n').encode())
def native(v):return [getattr(v,n) for n in k.NATIVE_NAMES]
def raw(v):return [hex(z) for z in k.cell_words(v)]
def scalar_cells(x,t):
    return {j:dict(addr=(x+j)%k.Q,age=t,f1=0,f2=0,wf1=0,wf2=0) for j in range(-5,6)}
def set_tags(cells,cats,t):
    for j,cat in enumerate(cats,1):
        cells[j]['age']=t if cat<2 else (0,B,t+104)[j%3]
        assert cat<2 or cells[j]['age']!=t
        cells[j]['f1']=int(cat>0)
def sf(rng):
    return {name:tuple(rng.getrandbits(c.WIDTHS.get(name,k.WORD)) for _ in k.SLOTS) for name in c.SF}
def compute():
    rng=random.Random(0x4741574e323001)
    tagged=hashlib.sha256();tagged_n=0
    phases=(0,1,2,3,4,5,k.Q-6,k.Q-5,k.Q-4,k.Q-3,k.Q-2,k.Q-1)
    for x in phases:
        for cats in itertools.product(range(3),repeat=5):
            if any(x+j>=k.Q and cats[j-1]!=0 for j in range(1,6)):continue
            for pattern in range(16):
                t=20+pattern;cells=scalar_cells(x,t);set_tags(cells,cats,t)
                for j in range(-5,1):
                    if 0<=x+j<k.Q:
                        cells[j].update(age=(0,B,t+104)[(j+pattern)%3],
                            f1=(pattern>>0)&1,f2=(pattern>>1)&1,
                            wf1=(pattern>>2)&1,wf2=(pattern>>3)&1)
                got=k.scalar_native(cells)
                assert got['addr']==x and (got['age']==t+1 or got['f1']==1)
                add(tagged,[x,cats,pattern,list(cells.values()),got]);tagged_n+=1
    assert tagged_n==1822*16==29152
    first=hashlib.sha256();first_n=0
    for x in (0,1,2):
        internal=tuple(j for j in range(-5,0) if x+j>=0)
        for wrong in itertools.product((0,B),repeat=len(internal)):
            for cats in itertools.product(range(3),repeat=5):
                for self_bits in range(4):
                    t=4094;cells=scalar_cells(x,t);set_tags(cells,cats,t)
                    for j,v in zip(internal,wrong):cells[j]['age']=v
                    cells[0].update(age=B,f1=self_bits&1,f2=(self_bits>>1)&1)
                    got=k.scalar_native(cells)
                    assert got['f2']==0 and got['age']==t+1 and got['addr']==x
                    add(first,[x,wrong,cats,self_bits,list(cells.values()),got]);first_n+=1
    assert first_n==7*243*4==6804
    prefix=hashlib.sha256();prefix_n=0
    for x in (3,4,5,k.Q-5,k.Q-3,k.Q-1):
        for right in itertools.product((0,7,8187,B),repeat=5):
            for self_bits in range(4):
                t=8187;cells=scalar_cells(x,t)
                for j,v in enumerate(right,1):cells[j]['age']=v
                cells[0].update(age=B,f1=self_bits&1,f2=(self_bits>>1)&1)
                got=k.scalar_native(cells)
                assert got['f2']==0 and got['age']==t+1 and got['addr']==x
                add(prefix,[x,right,self_bits,got]);prefix_n+=1
    assert prefix_n==6*4**5*4==24576
    front=hashlib.sha256();front_n=0
    for x in range(k.Q):
        for pattern in range(4):
            cells=scalar_cells(x,20)
            for j,v in cells.items():
                v.update(age=(0,1,B,20)[(j+pattern)%4],f1=(x+j+pattern)&1)
                if j>=0:v['f2']=(pattern>>1)&1
            got=k.scalar_native(cells)
            assert got['f2']==0 and got['addr']==x
            add(front,[x,pattern,got]);front_n+=1
    assert front_n==4*k.Q==16384
    full=hashlib.sha256();full_n=0
    # Every selected common old clock is inside the admitted closed prefix.
    # The scalar calculation intentionally reports WF0; the physical kernel
    # must independently obey the actual guard despite arbitrary SF words.
    critical=(1,2,32*k.Q,64*k.Q,72*k.Q+3,72*k.Q+4,75*k.Q,
        80*k.Q-1,80*k.Q,96*k.Q-1)
    for index in range(160):
        x=phases[index%len(phases)];age=critical[index%len(critical)]
        ns=scalar_cells(x,age-1)
        for j in ns:
            ns[j].update(**{name:rng.randrange(2) for name in ('f1','f2','wf1','wf2')})
        cells={j:k.Cell(**ns[j],**sf(rng)) for j in range(-5,6)}
        for j in (-8,-7,-6,6,7,8):
            cells[j]=k.Cell(addr=(x+j)%k.Q,age=age-1,**sf(rng))
        expected=k.scalar_native(ns);got=k.local_transition(cells,own.ROM)
        assert native(got)==[expected[name] for name in k.NATIVE_NAMES]
        assert got.age==age and got.wf1==got.wf2==0
        add(full,[x,age,[raw(cells[j]) for j in range(-8,9)],native(got)])
        full_n+=1
    assert full_n==160
    holder=hashlib.sha256();holder_n=outside_n=0
    def info(y):return ((y+1000003)*0x123456789abcdef1234567)&k.MASK
    for y in (-2,-1,k.Q,k.Q+1):
        outside_slots=tuple(s for s in k.SLOTS if not 0<=y-s<k.Q)
        assert len(outside_slots)>=3
        for t in (2,104,4095,8188,10340):
            for pattern in range(8):
                # A consistent finite restriction of the global exterior
                # invariant, with arbitrary inside clocks and SF. Info at
                # every exterior logical word has clean outside holders.
                positions=range(y-10,y+11);global_cells={}
                for x in positions:
                    inside=0<=x<k.Q
                    flags={name:rng.randrange(2) if inside else 0 for name in ('f1','f2','wf1','wf2')}
                    if -k.Q<=x<0:flags['f1']=rng.randrange(2)
                    words=sf(rng)
                    words['info']=tuple(rng.getrandbits(k.WORD) if inside else info(x+s) for s in k.SLOTS)
                    global_cells[x]=k.Cell(addr=x%k.Q,
                        age=(0,B,80*k.Q-2)[(x+pattern)%3] if inside else t-1,
                        **flags,**words)
                outputs=[]
                for s in k.SLOTS:
                    x=y-s;cells={j:global_cells[x+j] for j in range(-8,9)}
                    got=k.local_transition(cells,own.ROM)
                    value=got.info[k.SLOTS.index(s)];outputs.append(value)
                    if s in outside_slots:
                        assert got.addr==x%k.Q and got.age==t and got.wf1==got.wf2==0
                        assert value==info(y),(y,t,pattern,s,value,info(y))
                        outside_n+=1
                    add(holder,[y,t,pattern,s,[raw(cells[j]) for j in range(-8,9)],native(got),hex(value)])
                    holder_n+=1
                assert sum(v==info(y) for v in outputs)>=3
    assert holder_n==4*5*8*5==800 and outside_n==4*5*8*4-2*5*8==560
    deadlines=[]
    for d in range(104):
        last=1+d;q=last+R;maximum=B+q-1
        assert 1<=q<=10340<32*k.Q-1 and maximum<96*k.Q<k.U
        deadlines.append([d,last,last+CLOCK,q,maximum])
    assert (CLOCK,R,B)==(8188,10236,382876)
    assert deadlines[-1]==[103,104,8292,10340,393215]
    prefix_rows=[]
    for r in range(k.Q-1,CLOCK+1):
        m=min(k.Q,r-k.Q+4);front_length=min(k.Q,r-1)
        assert front_length>=m
        if m<k.Q:assert min(k.Q,r)>=m+1
        prefix_rows.append([r,m,front_length])
    assert prefix_rows[0]==[4095,3,4094] and prefix_rows[-1][1]==k.Q
    p18=ROOT/'figs/gray_counterexamples/unregistered_gawn18/GAWN18_two_good_gathers_certificate.json'
    p19=ROOT/'figs/gray_counterexamples/unregistered_gawn19/GAWN19_early_mixed_burst_certificate.json'
    assert json.loads(p18.read_text())['complete_current_U_boundary_conditional_repair_proved']
    assert json.loads(p19.read_text())['arbitrary_D_single_upper_cell_at_H2_one_update_correction_proved']
    sources=(Path(__file__),HERE/'GAWN20_EARLY_LARGE_CLOCK_BAND_REPAIR.md',
        HERE.parent/'unregistered_gawn2/small_rule_gawn2.py',
        HERE.parent/'unregistered_gawn6/GAWN6_CANONICAL_ADDRESS_CLOCK_CONFINEMENT.md',
        HERE.parent/'unregistered_gawn7/GAWN7_FLAG2_DEADLINE_AND_FIVE_CLOCK_REDUCTION.md',
        HERE.parent/'unregistered_gawn8/GAWN8_TAGGED_SUFFIX_AND_UNIVERSAL_LATE_REPAIR.md',
        HERE.parent/'unregistered_gawn18/GAWN18_TWO_GOOD_GATHERS_REPAIR.md',
        HERE.parent/'unregistered_gawn19/GAWN19_EARLY_MIXED_BURST_CURRENT_PERIOD_REPAIR.md',p18,p19)
    return dict(name='GAWN20 early large-clock-band mixed burst current-period repair',passed=True,
        Q=k.Q,U=k.U,lambda_original=24,error_separation=104,
        unchanged_GAWN2_all_Gray_departures_required=True,
        initial_actual_H2_physical_row=1,after_row_fault_window_maximum=[1,104],
        fixed_interval_in_true_colony0_max_width=104,maximum_additional_fault_rows=103,
        Address_retained=True,replacement_Age_absolute_inclusive=[0,B],
        all4_flags_all13_SF_arbitrary_adaptive=True,no_other_errors_required=True,
        age_zero_backward_and_far_forward_clocks_allowed=True,
        native_clock_recovery_after_last_possible_fault=CLOCK,
        native_complete_recovery_after_last_possible_fault=R,
        latest_native_quiet_physical_row=10340,largest_actual_prefix_raw_clock=393215,
        actual_Workspace_closed_without_SF_assumption_proved=True,
        computed_age0_excluded_but_80Qminus1_inside_allowed=True,
        universal_stated_early_native_recovery_proved=True,
        voted_Info_damage_confined_to_true_colony_I_proved=True,
        voted_Info_damage_confined_to_interval_A_claimed=False,
        complete_actual_current_U_and_all_later_repair_proved=True,
        original_error_class_from_support_geometry_assigned=False,
        arbitrary_GF_Ages382877to524287_other_phases_E0_higher_iid_memory_proved=False,
        faithful_Gray_G17_refutation_or_minimum_sufficient_fix_proved=False,
        evolving_fullSF10236step_or_physicalU_simulation_performed=False,
        rule_ROM_constants_CURRENT_changed=False,
        tagged_suffix_cofactors=tagged_n,tagged_suffix_sha256=tagged.hexdigest(),
        first_three_clock_cofactors=first_n,first_three_clock_sha256=first.hexdigest(),
        correct_left_prefix_cofactors=prefix_n,correct_left_prefix_sha256=prefix.hexdigest(),
        h1_Flag2_zero_front_cofactors=front_n,h1_Flag2_zero_front_sha256=front.hexdigest(),
        selected_arbitrary_SF_full_kernel_native_cofactors=full_n,
        full_kernel_native_inputs_outputs_sha256=full.hexdigest(),
        exterior_Info_holder_full_kernel_comparisons=holder_n,
        clean_outside_physical_holder_comparisons=outside_n,
        exterior_Info_holder_inputs_outputs_sha256=holder.hexdigest(),
        fault_window_deadline_rows=deadlines,clock_prefix_integer_rows=prefix_rows,
        source_sha256={str(p.relative_to(ROOT)):sha(p) for p in sources})
def main():
    p=argparse.ArgumentParser();p.add_argument('--issue',action='store_true');args=p.parse_args()
    start=time.perf_counter();OUT.mkdir(parents=True,exist_ok=True)
    pp=ROOT/'figs/gray_counterexamples/unregistered_gawn19/GAWN19_standalone_assets.json'
    parent=json.loads(pp.read_text());assert len(parent['assets_sha256'])==745
    cp=OUT/'GAWN20_early_large_clock_band_certificate.json';mp=OUT/'GAWN20_standalone_assets.json'
    for path,value in parent['assets_sha256'].items():assert sha(ROOT/path)==value,path
    if args.issue:
        assert not cp.exists() and not mp.exists()
        result=compute();cp.write_text(json.dumps(result,indent=2)+'\n')
        assets=dict(parent['assets_sha256'])
        for path in (pp,ROOT/'figs/gray_counterexamples/unregistered_gawn19/GAWN19_readonly_run01.log',
                     Path(__file__),HERE/'GAWN20_EARLY_LARGE_CLOCK_BAND_REPAIR.md',cp):
            assets[str(path.relative_to(ROOT))]=sha(path)
        manifest=dict(name=result['name'],inherited_assets=745,assets_sha256=assets,
            universal_stated_early_large_clock_band_current_U_repair_proved=True,
            global_reliability_proved=False,rule_ROM_constants_CURRENT_changed=False)
        mp.write_text(json.dumps(manifest,indent=2)+'\n')
    else:
        manifest=json.loads(mp.read_text());assert manifest['inherited_assets']==745
        for path,value in parent['assets_sha256'].items():assert manifest['assets_sha256'][path]==value,path
        for path,value in manifest['assets_sha256'].items():assert sha(ROOT/path)==value,path
        result=compute();assert result==json.loads(cp.read_text()),'Fresh supplements differ'
    for path,value in manifest['assets_sha256'].items():assert sha(ROOT/path)==value,path
    print(json.dumps(dict(passed=True,issued=args.issue,readonly=not args.issue,
        assets=len(manifest['assets_sha256']),inherited_assets=745,
        all_new_native_holder_integer_supplements_recomputed=True,
        complete_actual_current_U_and_all_later_repair_proved=True,
        admitted_absolute_Age=[0,B],clock_deadline=CLOCK,native_deadline=R,
        latest_native_quiet=10340,global_reliability_proved=False,
        rule_ROM_constants_CURRENT_changed=False,certificate_sha256=sha(cp),
        manifest_sha256=sha(mp),elapsed=time.perf_counter()-start)),flush=True)
if __name__=='__main__':main()
