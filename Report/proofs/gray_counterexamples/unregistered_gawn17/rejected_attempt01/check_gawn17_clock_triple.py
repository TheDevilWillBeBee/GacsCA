"""Issue once or replay supplements to the written clock-triple induction."""
import argparse,hashlib,json,random,sys,time
from dataclasses import replace
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
OUT=ROOT/'figs/gray_counterexamples/unregistered_gawn17'
sys.path.insert(0,str(HERE.parent/'unregistered_gawn10'))
import check_gawn10_two_offset_projection as c
sys.path.insert(0,str(HERE.parent/'unregistered_gawn4'))
import check_late_sf_gawn4 as h
k=c.k;own=c.own;K=96*k.Q-3
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def add(d,x):d.update((json.dumps(x,separators=(',',':'))+'\n').encode())
def native(v):return [getattr(v,n) for n in k.NATIVE_NAMES]
def expected(x,a,elapsed=0):return [x%k.Q,elapsed+3 if a-3<=x<a else elapsed+2,0,0,0,0]
def compute():
    actual=hashlib.sha256();records=[]
    for x in range(-8,9):
        clean={j:h.C1(x+j) for j in range(-8,9)}
        dirty={j:replace(v,age=2) if -1<=x+j<=1 else v for j,v in clean.items()}
        good=k.local_transition(clean,own.ROM);bad=k.local_transition(dirty,own.ROM)
        assert native(good)==[x%k.Q,2,0,0,0,0]
        assert native(bad)==expected(x,-1)
        row=dict(x=x,clean_native=native(good),faulty_native=native(bad))
        records.append(row)
        add(actual,[x,[[hex(z) for z in k.cell_words(dirty[j])] for j in range(-8,9)],
            [hex(z) for z in k.cell_words(good)],[hex(z) for z in k.cell_words(bad)]])
    cof=hashlib.sha256();count=0
    for a in range(k.Q):
        for relative in range(-6,7):
            x=a+relative
            cells={j:dict(addr=(x+j)%k.Q,age=2 if a<=x+j<a+3 else 1,
                f1=0,f2=0,wf1=0,wf2=0) for j in range(-5,6)}
            got=k.scalar_native(cells);values=[got[n] for n in k.NATIVE_NAMES]
            assert values==expected(x,a)
            add(cof,[a,relative,values]);count+=1
    assert count==53248
    rng=random.Random(0x4741574e313701);full=hashlib.sha256()
    elapseds=(0,1,4095,32767,K-1)
    for index in range(256):
        elapsed=elapseds[index%len(elapseds)];a=rng.randrange(-2*k.Q,2*k.Q)
        x=a+rng.randrange(-6,7);cells={}
        for j in range(-8,9):
            cells[j]=k.Cell(addr=(x+j)%k.Q,age=elapsed+2 if a<=x+j<a+3 else elapsed+1,
                **{n:tuple(rng.getrandbits(c.WIDTHS.get(n,k.WORD)) for _ in k.SLOTS) for n in c.SF})
        got=k.local_transition(cells,own.ROM)
        assert native(got)==expected(x,a,elapsed)
        add(full,[a,x,elapsed,[[hex(v) for v in k.cell_words(cells[j])] for j in range(-8,9)],
            [hex(v) for v in k.cell_words(got)]])
    assert K==393213 and K+2==96*k.Q-1<k.U and 3*K==1179639
    sources=(Path(__file__),HERE/'GAWN17_UPPER_TRIPLE_CLOCK_OBSTRUCTION.md',
        HERE.parent/'unregistered_gawn4/check_late_sf_gawn4.py',
        HERE.parent/'unregistered_gawn2/small_rule_gawn2.py',
        HERE.parent/'unregistered_gawn2/small_compositional_cost.py')
    return dict(name='GAWN17 prepared upper Age triple defeats one-tick correction',passed=True,
        Q=k.Q,U=k.U,lambda_original=24,error_separation=104,
        unchanged_GAWN2_all_Gray_departures_required=True,
        actual_C1_from_H2_only_Age_replacements_sites=[-1,0,1],replacement_Age=2,
        no_later_errors=True,one_tick_bad_Age_sites=[-4,-3,-2],one_tick_bad_Age=3,
        all_other_native_fields_canonical_zero_flags=True,
        universal_SF_independent_clock_shift_closed_guard_induction_proved=True,
        exact_interval_formula='[-1-3k,2-3k)',proved_elapsed_window=[0,K],
        last_proved_left_displacement=3*K,last_proved_bad_Age=K+2,
        arbitrary_upper_triple_one_tick_correction_identity=False,
        explicit_counterexample_to_arbitrary_upper_triple_one_tick_correction_proved=True,
        prepared_normalized_encoding_consequence_by_prior_period_proof=True,
        actual_J279_lower_fault_reachable_triple_proved=False,
        restricted_reachable_triple_or_eventual_general_repair_proved=False,
        original_error_class_from_support_geometry_assigned=False,
        fullSF393213step_or_encodedU_physical_simulation_performed=False,
        Gray_G17_iid_or_alltime_memory_failure_proved=False,
        positive_noise_rate_or_minimum_sufficient_change_proved=False,
        rule_ROM_constants_G17_changed=False,actual_C1_full_kernel_targets=17,
        actual_C1_native_outputs=records,actual_C1_full_raw_inputs_outputs_sha256=actual.hexdigest(),
        all_Q_residue_relative_native_cofactors=count,native_cofactor_sha256=cof.hexdigest(),
        arbitrary_SF_full_kernel_comparisons=256,full_kernel_elapseds=list(elapseds),
        arbitrary_SF_full_raw_inputs_outputs_sha256=full.hexdigest(),
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
            Path(__file__),HERE/'GAWN17_UPPER_TRIPLE_CLOCK_OBSTRUCTION.md',path):
            assets[str(q.relative_to(ROOT))]=sha(q)
        assert len(assets)==731
        manifest=dict(name=result['name'],inherited_assets=726,assets_sha256=assets,
            prepared_upper_triple_one_tick_obstruction_clock_shift393213_proved=True,
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
        assets=731,inherited_assets=726,all_new_native_and_full_kernel_checks_recomputed=True,
        prepared_upper_triple_one_tick_correction_refuted=True,
        proved_clock_shift_window=[0,K],actual_lower_burst_reachable_triple_proved=False,
        eventual_repair_Gray_G17_iid_or_memory_failure_proved=False,
        full_reliability=False,rule_ROM_constants_G17_changed=False,
        certificate_sha256=sha(path),manifest_sha256=sha(mp),elapsed=time.perf_counter()-start)),flush=True)
if __name__=='__main__':main()
