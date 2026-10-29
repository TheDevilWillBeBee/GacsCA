# Issue/replay corrected Age-triple/Flag1-packet supplements.
import argparse,hashlib,json,random,sys,time
from dataclasses import replace
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
OUT=ROOT/'figs/gray_counterexamples/unregistered_gawn17'
sys.path.insert(0,str(HERE.parent/'unregistered_gawn10'))
import check_gawn10_two_offset_projection as c
sys.path.insert(0,str(HERE.parent/'unregistered_gawn4'))
import check_late_sf_gawn4 as h
k=c.k;own=c.own
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def add(d,x):d.update((json.dumps(x,separators=(',',':'))+'\n').encode())
def native(v):return [getattr(v,n) for n in k.NATIVE_NAMES]
def packet(row):
    if row>=2049:return None
    return max(-k.Q,-1-3*row),-2*row
def inside_packet(x,row):
    p=packet(row);return p is not None and p[0]<=x<=p[1]
def compute():
    actual=hashlib.sha256();records=[]
    for x in range(-8,9):
        clean={j:h.C1(x+j) for j in range(-8,9)}
        dirty={j:replace(v,age=2) if -1<=x+j<=1 else v for j,v in clean.items()}
        good=k.local_transition(clean,own.ROM);bad=k.local_transition(dirty,own.ROM)
        assert native(good)==[x%k.Q,2,0,0,0,0]
        assert native(bad)==[x%k.Q,2,int(-4<=x<=-2),0,0,0]
        records.append(dict(x=x,clean_native=native(good),faulty_native=native(bad)))
        add(actual,[x,[[hex(z) for z in k.cell_words(dirty[j])] for j in range(-8,9)],
            [hex(z) for z in k.cell_words(good)],[hex(z) for z in k.cell_words(bad)]])
    cof=hashlib.sha256();count=0
    for x in range(k.Q):
        for mask in range(64):
            cells={j:dict(addr=(x+j)%k.Q,age=2,f1=int((mask>>(j-1))&1) if j>0 else 0,
                f2=0,wf1=0,wf2=0) for j in range(-5,6)}
            cells[0]['f1']=(mask>>5)&1
            rf=sum(0<=x+j<k.Q and bool(mask&(1<<(j-1))) for j in range(1,6))
            got=k.scalar_native(cells);values=[got[n] for n in k.NATIVE_NAMES]
            assert values==[x,3,int(rf>=3 or bool(mask&32) and rf>=2),0,0,0]
            add(cof,[x,mask,values]);count+=1
    assert count==262144
    arithmetic=hashlib.sha256()
    for row in range(1,2049):
        a,b=packet(row);following=packet(row+1)
        predicted=None if a==b else (max(-k.Q,a-3),b-2)
        assert predicted==following
        targets=set(range(-k.Q-6,-k.Q+7))|set(range(-6,7))
        targets|=set(range(a-6,a+7))|set(range(b-6,b+7))
        for x in sorted(targets):
            phase=x%k.Q
            rf=sum(0<=phase+j<k.Q and inside_packet(x+j,row) for j in range(1,6))
            flag=rf>=3 or inside_packet(x,row) and rf>=2
            assert bool(flag)==inside_packet(x,row+1)
        add(arithmetic,[row,a,b,following,sorted(targets)])
    rng=random.Random(0x4741574e313702);full=hashlib.sha256()
    rows=(1,2,20,1000,2047,2048,2049)
    for index in range(256):
        row=rows[index%len(rows)];p=packet(row)
        targets=list(range(-k.Q-6,-k.Q+7))+list(range(-6,7))
        if p:targets+=list(range(p[0]-6,p[0]+7))+list(range(p[1]-6,p[1]+7))
        x=rng.choice(targets);cells={}
        for j in range(-8,9):
            cells[j]=k.Cell(addr=(x+j)%k.Q,age=row+1,f1=int(inside_packet(x+j,row)),
                **{n:tuple(rng.getrandbits(c.WIDTHS.get(n,k.WORD)) for _ in k.SLOTS) for n in c.SF})
        got=k.local_transition(cells,own.ROM)
        assert native(got)==[x%k.Q,row+2,int(inside_packet(x,row+1)),0,0,0]
        add(full,[x,row,[[hex(v) for v in k.cell_words(cells[j])] for j in range(-8,9)],
            [hex(v) for v in k.cell_words(got)]])
    failure_path=OUT/'GAWN17_rejected_glider_attempt01.json';failure=json.loads(failure_path.read_text())
    assert failure['terminal_exit']==1
    rejected=HERE/'rejected_attempt01'
    assert sha(rejected/'check_gawn17_clock_triple.py')==failure['failed_source_sha256']
    assert sha(rejected/'GAWN17_UPPER_TRIPLE_CLOCK_OBSTRUCTION.md')==failure['rejected_proof_sha256']
    assert sha(ROOT/'figs/robustness/GAWN17_upper_triple_clock_issue_run01.log')==failure['failed_log_sha256']
    assert packet(1)==(-4,-2) and packet(2047)==(-4096,-4094)
    assert packet(2048)==(-4096,-4096) and packet(2049) is None and 2050<96*k.Q
    sources=(Path(__file__),HERE/'GAWN17_UPPER_TRIPLE_CLOCK_OBSTRUCTION.md',
        HERE.parent/'literal_maintenance.py',HERE.parent/'unregistered_gawn4/check_late_sf_gawn4.py',
        HERE.parent/'unregistered_gawn2/small_rule_gawn2.py',
        HERE.parent/'unregistered_gawn2/small_compositional_cost.py')
    return dict(name='GAWN17 Age-only upper triple leaves a finite Flag1 packet',passed=True,
        Q=k.Q,U=k.U,lambda_original=24,error_separation=104,
        unchanged_GAWN2_all_Gray_departures_required=True,
        actual_C1_from_H2_only_Age_replacements_sites=[-1,0,1],replacement_Age=2,no_later_errors=True,
        one_tick_all_Address_Age_correct=True,one_tick_Flag1_sites=[-4,-3,-2],
        actual_Age_consistency_clause_required=True,
        exact_inclusive_Flag1_interval='[max(-Q,-1-3k),-2k], 1<=k<=2048',
        last_Flag1_row=2048,last_Flag1_site=-k.Q,full_native_quiet_row=2049,
        universal_actual_SF_independent_native_induction_proved=True,
        arbitrary_upper_triple_one_tick_equality_identity=False,
        explicit_counterexample_to_arbitrary_upper_triple_one_tick_identity_proved=True,
        prepared_normalized_encoding_consequence_by_prior_period_proof=True,
        actual_J279_lower_fault_reachable_triple_proved=False,
        restricted_reachable_triple_full_or_eventual_general_repair_proved=False,
        original_error_class_from_support_geometry_assigned=False,
        fullSF2049step_or_encodedU_physical_simulation_performed=False,
        rejected_clock_glider_claim_proved=False,rejected_glider_failure_preserved=True,
        Gray_G17_iid_or_alltime_memory_failure_proved=False,
        positive_noise_rate_or_minimum_sufficient_change_proved=False,rule_ROM_constants_G17_changed=False,
        actual_C1_full_kernel_targets=17,actual_C1_native_outputs=records,
        actual_C1_full_raw_inputs_outputs_sha256=actual.hexdigest(),
        all_Q_residue_self_right_Flag1_cofactors=count,native_cofactor_sha256=cof.hexdigest(),
        exact_packet_arithmetic_transitions=2048,packet_arithmetic_sha256=arithmetic.hexdigest(),
        arbitrary_SF_full_kernel_comparisons=256,full_kernel_packet_rows=list(rows),
        arbitrary_SF_full_raw_inputs_outputs_sha256=full.hexdigest(),
        rejected_glider_failure_receipt_sha256=sha(failure_path),
        source_sha256={str(p.relative_to(ROOT)):sha(p) for p in sources})
def main():
    p=argparse.ArgumentParser();p.add_argument('--issue',action='store_true');args=p.parse_args()
    start=time.perf_counter();OUT.mkdir(parents=True,exist_ok=True)
    parent_path=ROOT/'figs/gray_counterexamples/unregistered_gawn16/GAWN16_standalone_assets.json'
    parent=json.loads(parent_path.read_text());assert len(parent['assets_sha256'])==726
    path=OUT/'GAWN17_upper_triple_clock_certificate.json';mp=OUT/'GAWN17_standalone_assets.json'
    for name,value in parent['assets_sha256'].items():assert sha(ROOT/name)==value,name
    if args.issue:
        assert not path.exists() and not mp.exists()
        result=compute();path.write_text(json.dumps(result,indent=2)+'\n')
        assets=dict(parent['assets_sha256'])
        for q in (parent_path,ROOT/'figs/gray_counterexamples/unregistered_gawn16/GAWN16_readonly_run01.log',
            Path(__file__),HERE/'GAWN17_UPPER_TRIPLE_CLOCK_OBSTRUCTION.md',path,
            HERE/'rejected_attempt01/check_gawn17_clock_triple.py',
            HERE/'rejected_attempt01/GAWN17_UPPER_TRIPLE_CLOCK_OBSTRUCTION.md',
            OUT/'GAWN17_rejected_glider_attempt01.json',
            ROOT/'figs/robustness/GAWN17_upper_triple_clock_issue_run01.log'):
            assets[str(q.relative_to(ROOT))]=sha(q)
        assert len(assets)==735
        manifest=dict(name=result['name'],inherited_assets=726,assets_sha256=assets,
            prepared_upper_triple_one_tick_identity_refuted_native_quiet2049_proved=True,
            rejected_glider_claim_accepted=False,
            actual_lower_burst_reachability_general_recovery_Gray_iid_proved=False,
            rule_ROM_constants_G17_changed=False)
        mp.write_text(json.dumps(manifest,indent=2)+'\n')
    else:
        manifest=json.loads(mp.read_text());assert manifest['inherited_assets']==726
        for name,value in parent['assets_sha256'].items():assert manifest['assets_sha256'][name]==value,name
        for name,value in manifest['assets_sha256'].items():assert sha(ROOT/name)==value,name
        result=compute();assert result==json.loads(path.read_text()),'Fresh native/kernel checks differ'
    for name,value in manifest['assets_sha256'].items():assert sha(ROOT/name)==value,name
    print(json.dumps(dict(passed=True,issued=args.issue,readonly=not args.issue,
        assets=735,inherited_assets=726,all_new_native_full_kernel_packet_checks_recomputed=True,
        prepared_upper_triple_one_tick_identity_refuted=True,full_native_quiet_row=2049,
        rejected_glider_claim_accepted=False,actual_lower_burst_reachable_triple_proved=False,
        full_eventual_repair_Gray_G17_iid_or_memory_failure_proved=False,
        full_reliability=False,rule_ROM_constants_G17_changed=False,
        certificate_sha256=sha(path),manifest_sha256=sha(mp),elapsed=time.perf_counter()-start)),flush=True)
if __name__=='__main__':main()
