"""Freeze/replay GAWN12 finite supplements to the native obstruction proof."""
from pathlib import Path
import argparse,hashlib,json,time
from check_gawn12_stationary_native import compute,ROOT,HERE
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--issue',action='store_true');args=parser.parse_args()
    start=time.perf_counter();out=ROOT/'figs/gray_counterexamples/unregistered_gawn12'
    base=ROOT/'figs/gray_counterexamples/unregistered_gawn11/GAWN11_standalone_assets.json'
    parent=json.loads(base.read_text());assert len(parent['assets_sha256'])==671
    path=out/'GAWN12_stationary_native_certificate.json';certificate=json.loads(path.read_text())
    manifest_path=out/'GAWN12_standalone_assets.json'
    manifest=None if args.issue else json.loads(manifest_path.read_text())
    if manifest is not None:
        assert manifest['inherited_assets']==671
        for name,value in parent['assets_sha256'].items():assert manifest['assets_sha256'][name]==value,name
        for name,value in manifest['assets_sha256'].items():assert sha(ROOT/name)==value,name
    assert compute()==certificate,'Fresh native/cofactor transcription differs from receipt'
    for key in ('passed','actual_one_row_native_only_overwrite_from_H2',
        'oldSF_clock_Flag2_Workspace_retained','no_later_errors','stationary_native_through_currentU_proved'):
        assert certificate[key],key
    for key in ('invariant_alone_implies_native_recovery_byU','actual104site104row_class_reachability_proved',
        'admitted_burst_termination_counterexample_Gray_G17_iid_or_bitfailure_proved',
        'persistence_after_reopened_Workspace_pulse_proved',
        'fullSF_evolution_or_fullperiod_physical_simulation_performed','rule_ROM_constants_G17_changed'):
        assert not certificate[key],key
    assert certificate['exact_overwritten_sites']==8192 and certificate['native_site_checks']==65664
    assert certificate['selected_full_kernel_comparisons']==544 and len(certificate['records'])==8
    if args.issue:
        assert not manifest_path.exists(),'Never overwrite a frozen manifest'
        assets=dict(parent['assets_sha256'])
        new=(base,ROOT/'figs/gray_counterexamples/unregistered_gawn11/GAWN11_readonly_run01.log',
            HERE/'GAWN12_STATIONARY_NATIVE_PROFILE.md',HERE/'check_gawn12_stationary_native.py',
            Path(__file__),path,ROOT/'figs/robustness/GAWN12_initial_stationary_run01.log')
        for p in new:assets[str(p.relative_to(ROOT))]=sha(p)
        manifest=dict(name='GAWN12 native invariant alone fails to imply current-U recovery',
            inherited_assets=671,assets_sha256=assets,
            actual_wider_native_only_fault_and_stationary_profile_throughU_proved=True,
            admitted104site_burst_Gray_G17_iid_or_memory_refutation_proved=False,
            rule_ROM_constants_G17_changed=False)
        manifest_path.write_text(json.dumps(manifest,indent=2)+'\n')
        print(json.dumps(dict(issued=True,assets=len(assets),inherited_assets=671,
            manifest_sha256=sha(manifest_path),elapsed=time.perf_counter()-start)));return
    for name,value in manifest['assets_sha256'].items():assert sha(ROOT/name)==value,name
    assert manifest['actual_wider_native_only_fault_and_stationary_profile_throughU_proved']
    assert not manifest['admitted104site_burst_Gray_G17_iid_or_memory_refutation_proved']
    assert not manifest['rule_ROM_constants_G17_changed']
    print(json.dumps(dict(passed=True,readonly=True,assets=len(manifest['assets_sha256']),inherited_assets=671,
        all_new_native_sites_and_full_kernel_arbitrarySF_cofactors_recomputed=True,
        certificate_sha256=sha(path),manifest_sha256=sha(manifest_path),
        actual_wider_fault_native_profile_throughU=True,admitted_small_burst_refutation=False,
        full_reliability=False,rule_ROM_constants_G17_changed=False,elapsed=time.perf_counter()-start)))
if __name__=='__main__':main()
