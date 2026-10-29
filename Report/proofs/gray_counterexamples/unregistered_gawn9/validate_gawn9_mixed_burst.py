"""Issue/verify GAWN9 provenance and recompute its finite supplements."""
from pathlib import Path
import argparse,hashlib,json,time
from check_gawn9_mixed_burst import compute,ROOT,HERE
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--issue',action='store_true');args=parser.parse_args()
    start=time.perf_counter();out=ROOT/'figs/gray_counterexamples/unregistered_gawn9'
    base=ROOT/'figs/gray_counterexamples/unregistered_gawn8/GAWN8_standalone_assets.json'
    parent=json.loads(base.read_text());assert len(parent['assets_sha256'])==578
    path=out/'GAWN9_mixed_burst_certificate.json';certificate=json.loads(path.read_text())
    assert compute()==certificate,'Finite transcriptions differ from frozen receipt'
    manifest_path=out/'GAWN9_standalone_assets.json'
    if args.issue:
        assets=dict(parent['assets_sha256'])
        new=(base,HERE/'GAWN9_LATE_MIXED_BURST_PAIR_REPAIR.md',HERE/'check_gawn9_mixed_burst.py',
            Path(__file__),path,ROOT/'figs/gray_counterexamples/unregistered_gawn8/GAWN8_readonly_run01.log',
            ROOT/'figs/robustness/GAWN9_initial_cofactor_run01.log')
        for p in new:assets[str(p.relative_to(ROOT))]=sha(p)
        manifest=dict(name='GAWN9 universal specified late mixed104x104 full2U burst recovery',
            inherited_assets=578,assets_sha256=assets,universal_stated_mixed_burst_complete2U_proved=True,
            general_native_higher_iid_proved=False,rule_ROM_constants_G17_changed=False)
        manifest_path.write_text(json.dumps(manifest,indent=2)+'\n')
        print(json.dumps(dict(issued=True,assets=len(assets),inherited_assets=578,
            manifest_sha256=sha(manifest_path),elapsed=time.perf_counter()-start)));return
    manifest=json.loads(manifest_path.read_text());assert manifest['inherited_assets']==578
    for name,value in parent['assets_sha256'].items():assert manifest['assets_sha256'][name]==value,name
    for name,value in manifest['assets_sha256'].items():assert sha(ROOT/name)==value,name
    assert manifest['universal_stated_mixed_burst_complete2U_proved']
    assert not manifest['general_native_higher_iid_proved'] and not manifest['rule_ROM_constants_G17_changed']
    assert certificate['complete2U_and_alllater_equality_proved']
    assert certificate['native_quiet_relative_to_last_fault']==14337
    assert certificate['native_margin_before_initial4Q_minimum']==1944
    for key in ('conditional_native_quiet_premise_required',
        'new_evolving_mixed_burst_nativequiet_or_full2U_simulation',
        'GF_changing_earlier_arbitrary_Age_E0_surroundings_separated_higher_iid_proved',
        'faithful_Gray_G17_refutation_shorterU_or_global_minimum','rule_ROM_constants_G17_changed'):
        assert not certificate[key],key
    print(json.dumps(dict(passed=True,readonly=True,assets=len(manifest['assets_sha256']),inherited_assets=578,
        all_new_geometry_arithmetic_full_kernel_checks_recomputed=True,
        certificate_sha256=sha(path),manifest_sha256=sha(manifest_path),
        universal_stated_late_mixed_burst_complete2U=True,native_quiet_after_last_fault=14337,
        full_reliability=False,rule_ROM_constants_G17_changed=False,elapsed=time.perf_counter()-start)))
if __name__=='__main__':main()
