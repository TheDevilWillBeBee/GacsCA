"""Finite transcription supplements; universal conclusions use the proof.

Same frozen GAWN2. No evolving2049/full-U physical simulation or iid claim.
"""
import argparse,hashlib,json,random,sys,time
from dataclasses import replace
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
OUT=ROOT/'figs/gray_counterexamples/unregistered_gawn18'
sys.path.insert(0,str(HERE.parent/'unregistered_gawn10'))
import check_gawn10_two_offset_projection as c
k=c.k;own=c.own
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def add(d,x):d.update((json.dumps(x,separators=(',',':'))+'\n').encode())
def raw(v):return [hex(z) for z in k.cell_words(v)]
def native(v):return [getattr(v,n) for n in k.NATIVE_NAMES]
def compute():
    rng=random.Random(0x4741574e313801);reset_digest=hashlib.sha256()
    reset_cases=0
    for case in range(64):
        x=(0,1,3,k.PRIMARY_START,k.PRIMARY_START+17,k.Q-3,k.Q-1)[case%7]
        # Incoherent raw Info is allowed. Compare the actual voted values.
        cells={j:k.Cell(addr=(x+j)%k.Q,age=32*k.Q-1,
            **{n:tuple(rng.getrandbits(c.WIDTHS.get(n,k.WORD)) for _ in k.SLOTS)
               for n in c.SF}) for j in range(-8,9)}
        got=k.local_transition(cells,own.ROM)
        assert native(got)==[x,32*k.Q,0,0,0,0]
        for name in c.SF:
            if name=='history1':expected=tuple(k.logical(cells,name,s) for s in k.SLOTS)
            elif name=='info':expected=tuple(k.logical(cells,name,s)&k.MASK for s in k.SLOTS)
            elif name=='program':expected=tuple(k.beta_bit(own.ROM,(x+s)%k.Q) for s in k.SLOTS)
            else:expected=(0,)*5
            assert getattr(got,name)==expected,(case,name)
        add(reset_digest,[x,[raw(cells[j]) for j in range(-8,9)],raw(got)])
        reset_cases+=1
    phases=set((1,32*k.Q,32*k.Q+1,64*k.Q,64*k.Q+1,k.EARLY_RESET,
        k.EARLY_BIRTH,k.EARLY_BIRTH+1,75*k.Q,80*k.Q-1,96*k.Q,
        96*k.Q+1,98*k.Q,100*k.Q,100*k.Q+1,100*k.Q+2,k.ACTIVE_END,0))
    phases.update(k.capture(g,lane) for g in (2,3) for lane in range(17))
    paired=hashlib.sha256();paired_cases=0;load_cases=0;boundary_cases=0
    # Same arbitrary legal fields and flags, except History1. History2 and
    # History3 are identical (even their arbitrary raw incoherent copies).
    for age in sorted(phases):
        for rep in range(8):
            x=(0,3,k.PRIMARY_START,k.PRIMARY_START+1,k.Q-3,k.Q-1,17,100)[rep]
            cells={}
            for j in range(-8,9):
                sf={n:tuple(rng.getrandbits(c.WIDTHS.get(n,k.WORD)) for _ in k.SLOTS)
                    for n in c.SF}
                sf['history3']=sf['history2']
                cells[j]=k.Cell(addr=(x+j)%k.Q,age=(age-1)%k.U,
                    f1=rng.randrange(2),f2=rng.randrange(2),
                    wf1=rng.randrange(2),wf2=rng.randrange(2),**sf)
            other={j:replace(v,history1=tuple(rng.getrandbits(17*k.WORD) for _ in k.SLOTS))
                for j,v in cells.items()}
            a=k.local_transition(cells,own.ROM);b=k.local_transition(other,own.ROM)
            assert native(a)==native(b) and a.addr==x and a.age==age
            assert a.addr==cells[0].addr # No GF wipe.
            for name in c.SF:
                if name!='history1':assert getattr(a,name)==getattr(b,name),(age,rep,name)
            if age in (k.EARLY_RESET,100*k.Q+1):
                expected=tuple(k.logical(cells,'history2',s) for s in k.SLOTS)
                assert a.mem==b.mem==expected
                load_cases+=1
            if age==0:
                assert a==b
                assert a.info==tuple(k.logical(cells,'out',s)&k.MASK for s in k.SLOTS)
                for name in c.SF:
                    if name not in ('info','program'):assert getattr(a,name)==(0,)*5
                boundary_cases+=1
            add(paired,[age,x,[raw(cells[j]) for j in range(-8,9)],
                [raw(other[j]) for j in range(-8,9)],raw(a),raw(b)])
            paired_cases+=1
    coordinates=hashlib.sha256();coordinate_cases=0
    for g in (2,3):
        start=k.GATHER_STARTS[g-1]
        for lane in range(17):
            delta=lane-8;capture=k.capture(g,lane)
            assert capture==(start+1 if delta==0 else start+2+abs(delta)*k.Q)
            for i in range(k.FRAME_WORDS):
                for slot in k.SLOTS:
                    # A physical holder x=y-slot consumes logical coordinate y.
                    y=7*k.Q+k.PRIMARY_START+i
                    holder=y-slot
                    oldrow=capture-1
                    displacement=0 if delta==0 else oldrow-(start+1)
                    assert displacement==abs(delta)*k.Q
                    source=holder+slot+(displacement if delta>0 else -displacement)
                    assert source==(7+delta)*k.Q+k.PRIMARY_START+i
                    assert 0<=displacement<16*k.Q
                    add(coordinates,[g,lane,i,slot,capture,source]);coordinate_cases+=1
    assert coordinate_cases==2*17*k.FRAME_WORDS*5==84320
    truth=[]
    for a in (0,1):
        for b in (0,1):
            assert k.majority3(a,b,b)==b;truth.append([a,b,b,b])
    assert 2050<=32*k.Q-1 and 1+2049==2050
    parent17=ROOT/'figs/gray_counterexamples/unregistered_gawn17/GAWN17_upper_triple_clock_certificate.json'
    p=json.loads(parent17.read_text())
    assert p['full_native_quiet_row']==2049 and p['universal_actual_SF_independent_native_induction_proved']
    sources=(Path(__file__),HERE/'GAWN18_TWO_GOOD_GATHERS_REPAIR.md',
        HERE.parent/'unregistered_gawn2/small_rule_gawn2.py',
        HERE.parent/'unregistered_gawn2/small_compositional_cost.py',parent17)
    return dict(name='GAWN18 two good gathers give complete conditional current-U repair',passed=True,
        Q=k.Q,U=k.U,lambda_original=24,error_separation=104,
        unchanged_GAWN2_all_Gray_departures_required=True,
        theta_inclusive_range=[1,32*k.Q-1],global_canonical_Address_correct_common_Age_zero_flags_required=True,
        initial_logical_Info_equals_clean_encoding_required=True,arbitrary_other_legal_SF_allowed=True,
        raw_initial_Info_coherence_required=False,no_later_errors_required=True,
        complete_current_U_boundary_conditional_repair_proved=True,
        actual_prepared_Age_only_triple_complete_current_U_repair_proved=True,
        prepared_Age_triple_fault_physical_row=1,prepared_Age_triple_native_quiet_physical_row=2050,
        GAWN17_unrestricted_triple_one_tick_identity_still_refuted=True,
        arbitrary_early_Info_changing_clock_multiple_offset_recovery_proved=False,
        actual_lower_fault_reachable_triple_or_general_upper_triple_repair_proved=False,
        surrounding_E0_higher_iid_positive_rate_alltime_memory_proved=False,
        faithful_Gray_G17_refutation_or_minimum_sufficient_change_proved=False,
        full_evolving2049_or_U_physical_simulation_performed=False,
        rule_ROM_constants_CURRENT_changed=False,
        reset_kernel_cases=reset_cases,reset_kernel_inputs_outputs_sha256=reset_digest.hexdigest(),
        History1_noninterference_kernel_cases=paired_cases,critical_ages=sorted(phases),
        Mem_load_kernel_cases=load_cases,boundary_commit_kernel_cases=boundary_cases,
        paired_kernel_inputs_outputs_sha256=paired.hexdigest(),
        gather_holder_frame_coordinate_cases=coordinate_cases,gather_coordinate_sha256=coordinates.hexdigest(),
        bit_majority_truth_table=truth,source_sha256={str(p.relative_to(ROOT)):sha(p) for p in sources})
def main():
    p=argparse.ArgumentParser();p.add_argument('--issue',action='store_true');args=p.parse_args()
    start=time.perf_counter();OUT.mkdir(parents=True,exist_ok=True)
    pp=ROOT/'figs/gray_counterexamples/unregistered_gawn17/GAWN17_standalone_assets.json'
    parent=json.loads(pp.read_text());assert len(parent['assets_sha256'])==735
    path=OUT/'GAWN18_two_good_gathers_certificate.json';mp=OUT/'GAWN18_standalone_assets.json'
    for name,value in parent['assets_sha256'].items():assert sha(ROOT/name)==value,name
    if args.issue:
        assert not path.exists() and not mp.exists()
        result=compute();path.write_text(json.dumps(result,indent=2)+'\n')
        assets=dict(parent['assets_sha256'])
        for q in (pp,ROOT/'figs/gray_counterexamples/unregistered_gawn17/GAWN17_readonly_run01.log',
                  Path(__file__),HERE/'GAWN18_TWO_GOOD_GATHERS_REPAIR.md',path):
            assets[str(q.relative_to(ROOT))]=sha(q)
        manifest=dict(name=result['name'],inherited_assets=735,assets_sha256=assets,
            conditional_current_U_complete_repair_proved=True,
            prepared_Age_triple_current_U_complete_repair_proved=True,
            global_reliability_proved=False,rule_ROM_constants_CURRENT_changed=False)
        mp.write_text(json.dumps(manifest,indent=2)+'\n')
    else:
        manifest=json.loads(mp.read_text());assert manifest['inherited_assets']==735
        for name,value in parent['assets_sha256'].items():assert manifest['assets_sha256'][name]==value,name
        for name,value in manifest['assets_sha256'].items():assert sha(ROOT/name)==value,name
        result=compute();assert result==json.loads(path.read_text()),'Fresh supplement differs'
    for name,value in manifest['assets_sha256'].items():assert sha(ROOT/name)==value,name
    print(json.dumps(dict(passed=True,issued=args.issue,readonly=not args.issue,
        assets=len(manifest['assets_sha256']),inherited_assets=735,
        all_new_kernel_coordinate_truth_table_checks_recomputed=True,
        conditional_current_U_complete_repair_proved=True,
        prepared_Age_triple_current_U_complete_repair_proved=True,
        global_reliability_proved=False,rule_ROM_constants_CURRENT_changed=False,
        certificate_sha256=sha(path),manifest_sha256=sha(mp),elapsed=time.perf_counter()-start)),flush=True)
if __name__=='__main__':main()
