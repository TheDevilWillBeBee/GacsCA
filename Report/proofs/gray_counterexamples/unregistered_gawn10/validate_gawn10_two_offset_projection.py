"""Issue/freeze GAWN10 provenance and replay all finite native supplements.

The written universal projection/exterior argument is separate from the
finite replay. Universal Address termination and noisy reliability are open.
"""
from pathlib import Path
import argparse,hashlib,json,time
from check_gawn10_two_offset_projection import compute,ROOT,HERE

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--issue',action='store_true');args=parser.parse_args()
    start=time.perf_counter();out=ROOT/'figs/gray_counterexamples/unregistered_gawn10'
    base=ROOT/'figs/gray_counterexamples/unregistered_gawn9/GAWN9_standalone_assets.json'
    parent=json.loads(base.read_text());assert len(parent['assets_sha256'])==585
    path=out/'GAWN10_two_offset_native_certificate.json';certificate=json.loads(path.read_text())
    manifest_path=out/'GAWN10_standalone_assets.json'
    manifest=None if args.issue else json.loads(manifest_path.read_text())
    if manifest is not None:
        assert manifest['inherited_assets']==585
        for name,value in parent['assets_sha256'].items():assert manifest['assets_sha256'][name]==value,name
        for name,value in manifest['assets_sha256'].items():assert sha(ROOT/name)==value,name
    assert compute(out,False)==certificate,'Native transcriptions or arrays differ from frozen receipt'
    initial=json.loads((out/'GAWN10_initial_two_offset_native_certificate.json').read_text())
    old_sources=initial.pop('source_sha256');new=dict(certificate);new.pop('source_sha256')
    assert new.pop('conditional_full_native_deadline_within_current_U_required')
    assert initial==new,'Deadline-scope reissue changed a finite result'
    for name,value in old_sources.items():
        filename=Path(name).name
        retained=out/('initial_'+filename)
        assert sha(retained if retained.exists() else ROOT/name)==value,name
    assert certificate['universal_native_projection_and_exterior_proved']
    assert certificate['computed_Workspace_guard_actually_closed']
    assert certificate['conditional_Address_correct_row_implies_full_native_repair_proved']
    for key in ('universal_Address_termination_for_this_class_proved',
        'full_SF_confinement_completeU_2U_or_iid_proved',
        'general_arbitrary_GF_clock_E0_surroundings_higher_iid_proved',
        'faithful_Gray_G17_refutation_shorterU_or_minimum_proved',
        'full_SF_evolution_or_complete2U_physical_simulation_performed',
        'rule_ROM_constants_G17_changed'):
        assert not certificate[key],key
    if args.issue:
        assert not manifest_path.exists(),'Never overwrite a frozen manifest'
        assets=dict(parent['assets_sha256'])
        new_paths=(base,ROOT/'figs/gray_counterexamples/unregistered_gawn9/GAWN9_readonly_run01.log',
            HERE/'GAWN10_TWO_OFFSET_NATIVE_EXTERIOR.md',HERE/'gawn10_two_offset_projection.c',
            HERE/'check_gawn10_two_offset_projection.py',Path(__file__),path,
            out/'initial_GAWN10_TWO_OFFSET_NATIVE_EXTERIOR.md',out/'initial_check_gawn10_two_offset_projection.py',
            out/'GAWN10_initial_two_offset_native_certificate.json',
            ROOT/'figs/robustness/GAWN10_initial_projection_run01.log',
            ROOT/'figs/robustness/GAWN10_initial_projection_run02.log')
        for p in new_paths:assets[str(p.relative_to(ROOT))]=sha(p)
        assets.update(certificate['selected_native_histories']['asset_sha256'])
        manifest=dict(name='GAWN10 exact restricted late common-clock/two-offset native projection',
            inherited_assets=585,assets_sha256=assets,
            universal_stated_native_projection_exterior_and_conditional_native_recovery_proved=True,
            universal_Address_termination_fullSF_complete2U_higher_iid_proved=False,
            initial_receipt_scope_clarification_only_all_finite_results_unchanged=True,
            rule_ROM_constants_G17_changed=False)
        manifest_path.write_text(json.dumps(manifest,indent=2)+'\n')
        print(json.dumps(dict(issued=True,assets=len(assets),inherited_assets=585,
            manifest_sha256=sha(manifest_path),elapsed=time.perf_counter()-start)));return
    for name,value in manifest['assets_sha256'].items():assert sha(ROOT/name)==value,name
    assert manifest['universal_stated_native_projection_exterior_and_conditional_native_recovery_proved']
    assert not manifest['universal_Address_termination_fullSF_complete2U_higher_iid_proved']
    assert manifest['initial_receipt_scope_clarification_only_all_finite_results_unchanged']
    assert not manifest['rule_ROM_constants_G17_changed']
    print(json.dumps(dict(passed=True,readonly=True,assets=len(manifest['assets_sha256']),inherited_assets=585,
        all_new_geometry_full_kernel_native_histories_and_saved_arrays_recomputed=True,
        certificate_sha256=sha(path),manifest_sha256=sha(manifest_path),
        native_projection_and_exterior_proved=True,conditional_native_recovery_proved=True,
        universal_Address_termination=False,full_reliability=False,
        rule_ROM_constants_G17_changed=False,elapsed=time.perf_counter()-start)))
if __name__=='__main__':main()
