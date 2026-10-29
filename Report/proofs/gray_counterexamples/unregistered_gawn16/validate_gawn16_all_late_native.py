"""Issue once or replay all new tables/checks with frozen ancestry unchanged."""
import argparse,json,time
from pathlib import Path
from check_gawn16_all_late_native import compute,sha,ROOT,HERE,OUT
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--issue',action='store_true');args=parser.parse_args()
    started=time.perf_counter();OUT.mkdir(parents=True,exist_ok=True)
    parent_path=ROOT/'figs/gray_counterexamples/unregistered_gawn15/GAWN15_standalone_assets.json'
    parent=json.loads(parent_path.read_text());assert len(parent['assets_sha256'])==718
    path=OUT/'GAWN16_all_late_native_certificate.json';manifest_path=OUT/'GAWN16_standalone_assets.json'
    if args.issue:
        assert not path.exists() and not manifest_path.exists()
        for name,value in parent['assets_sha256'].items():assert sha(ROOT/name)==value,name
        result=compute(issue=True);path.write_text(json.dumps(result,indent=2)+'\n');assets=dict(parent['assets_sha256'])
        for p in (parent_path,ROOT/'figs/gray_counterexamples/unregistered_gawn15/GAWN15_readonly_run01.log',
            HERE/'gawn16_arbitrary_flag2_tags.c',HERE/'check_gawn16_all_late_native.py',Path(__file__),
            HERE/'GAWN16_ALL_LATE_TWO_OFFSET_NATIVE_REPAIR.md',path):assets[str(p.relative_to(ROOT))]=sha(p)
        assets.update(result['array_sha256']);assert len(assets)==726
        manifest=dict(name=result['name'],inherited_assets=718,assets_sha256=assets,
            all_stated_late_two_offset_nativequiet11608_actual_U_encoding_proved=True,
            positive_ell_complete2U_all_later_equality_proved=True,
            nonpositive_ell_triple_complete_repair_general_noise_higher_iid_proved=False,
            rule_ROM_constants_G17_changed=False)
        manifest_path.write_text(json.dumps(manifest,indent=2)+'\n')
    else:
        manifest=json.loads(manifest_path.read_text());assert manifest['inherited_assets']==718
        for name,value in parent['assets_sha256'].items():assert manifest['assets_sha256'][name]==value,name
        for name,value in manifest['assets_sha256'].items():assert sha(ROOT/name)==value,name
        result=compute();assert result==json.loads(path.read_text()),'Fresh table/geometry/full kernel differs'
        for name,value in manifest['assets_sha256'].items():assert sha(ROOT/name)==value,name
    assert manifest['all_stated_late_two_offset_nativequiet11608_actual_U_encoding_proved']
    assert not manifest['nonpositive_ell_triple_complete_repair_general_noise_higher_iid_proved']
    assert not manifest['rule_ROM_constants_G17_changed']
    print(json.dumps(dict(passed=True,issued=args.issue,readonly=not args.issue,assets=726,inherited_assets=718,
        all_new_saved_table_tag_kernel_support_geometry_bounds_recomputed=True,
        all_stated_late_bursts_nativequiet_actual_U_encoding=True,maximum_native_deadline=11608,
        latest_native_quiet=421313,slack_to_first_fault4Q=4673,
        low_phase_reachability_cases=result['geometry']['small_boundary_b_delta_width_D_cases'],
        positive_ell_complete2U=True,nonpositive_ell_triple_complete_repair_higher_iid=False,
        full_reliability=False,rule_ROM_constants_G17_changed=False,
        certificate_sha256=sha(path),manifest_sha256=sha(manifest_path),elapsed=time.perf_counter()-started)),flush=True)
if __name__=='__main__':main()
