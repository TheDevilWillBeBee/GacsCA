"""Issue/verify GAWN8 provenance and recompute its finite supplements."""
from pathlib import Path
import argparse,hashlib,json,time
from check_gawn8_tagged_suffix import compute,ROOT,HERE
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--issue',action='store_true');args=parser.parse_args()
    start=time.perf_counter();out=ROOT/'figs/gray_counterexamples/unregistered_gawn8'
    base=ROOT/'figs/gray_counterexamples/unregistered_gawn7/GAWN7_standalone_assets.json'
    parent=json.loads(base.read_text());assert len(parent['assets_sha256'])==571
    path=out/'GAWN8_tagged_suffix_certificate.json';certificate=json.loads(path.read_text())
    assert compute()==certificate,'Finite transcriptions differ from frozen receipt'
    manifest_path=out/'GAWN8_standalone_assets.json'
    if args.issue:
        assets=dict(parent['assets_sha256'])
        new=(base,HERE/'GAWN8_TAGGED_SUFFIX_AND_UNIVERSAL_LATE_REPAIR.md',
            HERE/'check_gawn8_tagged_suffix.py',Path(__file__),path,
            ROOT/'figs/gray_counterexamples/unregistered_gawn7/GAWN7_readonly_run01.log',
            ROOT/'figs/robustness/GAWN8_initial_cofactor_run01.log')
        for p in new:assets[str(p.relative_to(ROOT))]=sha(p)
        manifest=dict(name='GAWN8 universal tagged suffix/native termination/restricted complete2U',
            inherited_assets=len(parent['assets_sha256']),assets_sha256=assets,
            universal_native_recovery_for_admitted_late_class=True,
            restricted_complete2U_proved=True,general_native_higher_iid_proved=False,
            rule_ROM_constants_G17_changed=False)
        manifest_path.write_text(json.dumps(manifest,indent=2)+'\n')
        print(json.dumps(dict(issued=True,assets=len(assets),inherited_assets=571,
            manifest_sha256=sha(manifest_path),elapsed=time.perf_counter()-start)));return
    manifest=json.loads(manifest_path.read_text())
    assert manifest['inherited_assets']==571
    for name,value in parent['assets_sha256'].items():assert manifest['assets_sha256'][name]==value,name
    for name,value in manifest['assets_sha256'].items():assert sha(ROOT/name)==value,name
    assert manifest['universal_native_recovery_for_admitted_late_class'] and manifest['restricted_complete2U_proved']
    assert not manifest['general_native_higher_iid_proved'] and not manifest['rule_ROM_constants_G17_changed']
    assert certificate['universal_full_native_quiet_row']==14337 and certificate['margin_before4Q']==2047
    assert certificate['first5_clock_premise_for_every_admitted_payload_proved']
    assert certificate['complete2U_and_alllater_for_only_Age_flags_Info_faults_proved']
    for key in ('broad_arbitrary_SF_complete2U','GF_changing_earlier_E0_surroundings_higher_iid',
        'faithful_Gray_G17_refutation_shorterU_or_global_minimum',
        'new_native_quiet_trajectory_or_full2U_simulation','rule_ROM_constants_G17_changed'):
        assert not certificate[key],key
    print(json.dumps(dict(passed=True,readonly=True,assets=len(manifest['assets_sha256']),inherited_assets=571,
        all_new_cofactors_full_kernel_checks_recomputed=True,certificate_sha256=sha(path),
        manifest_sha256=sha(manifest_path),universal_native_quiet=14337,
        first5_premise_closed_for_admitted_late_class=True,restricted_complete2U_proved=True,
        full_reliability=False,rule_ROM_constants_G17_changed=False,elapsed=time.perf_counter()-start)))
if __name__=='__main__':main()
