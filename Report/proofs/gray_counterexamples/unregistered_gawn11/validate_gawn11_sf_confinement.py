"""Issue/freeze and read-only replay GAWN11's finite supplements."""
from pathlib import Path
import argparse,hashlib,json,time
from check_gawn11_sf_confinement import compute,ROOT,HERE
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--issue',action='store_true');args=parser.parse_args()
    start=time.perf_counter();out=ROOT/'figs/gray_counterexamples/unregistered_gawn11'
    base=ROOT/'figs/gray_counterexamples/unregistered_gawn10/GAWN10_standalone_assets.json'
    parent=json.loads(base.read_text());assert len(parent['assets_sha256'])==661
    path=out/'GAWN11_SF_confinement_certificate.json';certificate=json.loads(path.read_text())
    manifest_path=out/'GAWN11_standalone_assets.json'
    manifest=None if args.issue else json.loads(manifest_path.read_text())
    if manifest is not None:
        assert manifest['inherited_assets']==661
        for name,value in parent['assets_sha256'].items():assert manifest['assets_sha256'][name]==value,name
        for name,value in manifest['assets_sha256'].items():assert sha(ROOT/name)==value,name
    assert compute()==certificate,'Fresh geometry/raw-holder transcriptions differ from receipt'
    failure_path=out/'GAWN11_initial_coverage_failure.json';failure=json.loads(failure_path.read_text())
    assert (failure['cases'],failure['full_kernel_calls'],failure['actually_foreign_computed_minority_controls'])==(160,1600,0)
    assert failure['external_computed_Flag1_positive_outputs']>0 and not failure['rule_changed']
    assert sha(ROOT/failure['failed_checker'])==failure['failed_checker_sha256']
    assert sha(ROOT/failure['failed_log'])==failure['failed_log_sha256']
    for key in ('passed','GAWN10_exact_fault_hypotheses_required',
        'universal_logical_SF_confinement_without_nativequiet_proved',
        'conditional_nativequiet_after_last_fault_beforeU_required',
        'actual_U_represented_D_encoding_proved_conditionally',
        'adjacent_pair_complete2U_alllater_proved_conditionally',
        'triple_exact2U_encoding_reduction_proved_conditionally'):
        assert certificate[key],key
    for key in ('universal_Address_termination_upper_triple_repair_general_higher_iid_proved',
        'faithful_Gray_G17_refutation_shorterU_or_global_minimum_proved',
        'new_evolving_fullSF_Address_burst_or_complete2U_physical_simulation',
        'rule_ROM_constants_G17_changed'):
        assert not certificate[key],key
    if args.issue:
        assert not manifest_path.exists(),'Never overwrite a frozen manifest'
        assets=dict(parent['assets_sha256'])
        new=(base,ROOT/'figs/gray_counterexamples/unregistered_gawn10/GAWN10_readonly_run01.log',
            HERE/'GAWN11_ADDRESS_BURST_SF_CONFINEMENT.md',HERE/'check_gawn11_sf_confinement.py',Path(__file__),path,
            out/'GAWN11_initial_no_forced_minority_checker.py',failure_path,
            ROOT/'figs/robustness/GAWN11_initial_cofactor_run01.log',
            ROOT/'figs/robustness/GAWN11_initial_cofactor_run02.log')
        for p in new:assets[str(p.relative_to(ROOT))]=sha(p)
        manifest=dict(name='GAWN11 exact two-offset late SF confinement/conditional nativequiet boundary',
            inherited_assets=661,assets_sha256=assets,unconditional_logical_SF_confinement_proved=True,
            nativequiet_premise_still_required_for_U_encoding_and_pair2U=True,
            general_Address_termination_triple_repair_higher_iid_proved=False,
            rule_ROM_constants_G17_changed=False)
        manifest_path.write_text(json.dumps(manifest,indent=2)+'\n')
        print(json.dumps(dict(issued=True,assets=len(assets),inherited_assets=661,
            manifest_sha256=sha(manifest_path),elapsed=time.perf_counter()-start)));return
    for name,value in manifest['assets_sha256'].items():assert sha(ROOT/name)==value,name
    assert manifest['unconditional_logical_SF_confinement_proved']
    assert manifest['nativequiet_premise_still_required_for_U_encoding_and_pair2U']
    assert not manifest['general_Address_termination_triple_repair_higher_iid_proved']
    assert not manifest['rule_ROM_constants_G17_changed']
    print(json.dumps(dict(passed=True,readonly=True,assets=len(manifest['assets_sha256']),inherited_assets=661,
        all_new_geometry_and_full_kernel_holder_comparisons_recomputed=True,
        certificate_sha256=sha(path),manifest_sha256=sha(manifest_path),
        unconditional_logical_SF_confinement=True,nativequiet_still_required_for_boundary=True,
        general_Address_termination_triple_repair=False,full_reliability=False,
        rule_ROM_constants_G17_changed=False,elapsed=time.perf_counter()-start)))
if __name__=='__main__':main()
