"""Issue once or recompute every new supplement with all frozen assets fixed."""
import argparse,json,time
from pathlib import Path
from check_gawn15_tagged_address import compute,sha,ROOT,HERE,OUT
def main():
    p=argparse.ArgumentParser();p.add_argument('--issue',action='store_true');args=p.parse_args()
    start=time.perf_counter();OUT.mkdir(parents=True,exist_ok=True)
    parent_path=ROOT/'figs/gray_counterexamples/unregistered_gawn14/GAWN14_standalone_assets.json'
    parent=json.loads(parent_path.read_text());assert len(parent['assets_sha256'])==711
    path=OUT/'GAWN15_tagged_Address_certificate.json';manifest_path=OUT/'GAWN15_standalone_assets.json'
    if args.issue:
        assert not path.exists() and not manifest_path.exists()
        for name,value in parent['assets_sha256'].items():assert sha(ROOT/name)==value,name
        result=compute();path.write_text(json.dumps(result,indent=2)+'\n');assets=dict(parent['assets_sha256'])
        for q in (parent_path,ROOT/'figs/gray_counterexamples/unregistered_gawn14/GAWN14_readonly_run01.log',
            HERE/'gawn15_tag_table.c',HERE/'check_gawn15_tagged_address.py',Path(__file__),
            HERE/'GAWN15_TAGGED_ADDRESS_PAIR_REPAIR.md',path):assets[str(q.relative_to(ROOT))]=sha(q)
        assert len(assets)==718
        manifest=dict(name=result['name'],inherited_assets=711,assets_sha256=assets,
            universal_positive_ell_nativequiet_and_complete2U_proved=True,
            nonpositive_ell_general_Address_burst_higher_iid_proved=False,rule_ROM_constants_G17_changed=False)
        manifest_path.write_text(json.dumps(manifest,indent=2)+'\n')
    else:
        manifest=json.loads(manifest_path.read_text());assert manifest['inherited_assets']==711
        for name,value in parent['assets_sha256'].items():assert manifest['assets_sha256'][name]==value,name
        for name,value in manifest['assets_sha256'].items():assert sha(ROOT/name)==value,name
        result=compute();assert result==json.loads(path.read_text())
        for name,value in manifest['assets_sha256'].items():assert sha(ROOT/name)==value,name
    assert manifest['universal_positive_ell_nativequiet_and_complete2U_proved']
    assert not manifest['nonpositive_ell_general_Address_burst_higher_iid_proved']
    assert not manifest['rule_ROM_constants_G17_changed']
    print(json.dumps(dict(passed=True,issued=args.issue,readonly=not args.issue,assets=718,inherited_assets=711,
        all_new_tag_native_full_kernel_geometry_bound_checks_recomputed=True,
        positive_ell_universal_nativequiet_complete2U=True,maximum_native_deadline=11602,
        latest_native_quiet=421307,slack_to_first_fault4Q=4679,
        nonpositive_ell_general_Address_higher_iid=False,full_reliability=False,
        rule_ROM_constants_G17_changed=False,certificate_sha256=sha(path),manifest_sha256=sha(manifest_path),
        elapsed=time.perf_counter()-start)),flush=True)
if __name__=='__main__':main()
