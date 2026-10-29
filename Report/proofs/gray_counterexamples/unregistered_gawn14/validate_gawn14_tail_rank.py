"""Issue once or replay all unchanged finite-tail rank arrays and supplements."""
from pathlib import Path
import argparse,json,time
from check_gawn14_tail_rank import compute,sha,ROOT,HERE,OUT

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--issue',action='store_true');args=parser.parse_args()
    start=time.perf_counter();OUT.mkdir(parents=True,exist_ok=True)
    parent_path=ROOT/'figs/gray_counterexamples/unregistered_gawn13/GAWN13_standalone_assets.json'
    parent=json.loads(parent_path.read_text());assert len(parent['assets_sha256'])==692
    manifest_path=OUT/'GAWN14_standalone_assets.json';receipt_path=OUT/'GAWN14_tail_rank_certificate.json'
    if args.issue:
        assert not manifest_path.exists() and not receipt_path.exists()
        for name,value in parent['assets_sha256'].items():assert sha(ROOT/name)==value,name
        result=compute(issue=True);receipt_path.write_text(json.dumps(result,indent=2)+'\n')
        assets=dict(parent['assets_sha256'])
        for p in (parent_path,ROOT/'figs/gray_counterexamples/unregistered_gawn13/GAWN13_readonly_run01.log',
            HERE/'gawn14_tail_rank.c',HERE/'check_gawn14_tail_rank.py',Path(__file__),
            HERE/'GAWN14_COUPLED_BOUNDARY_TAIL.md',receipt_path):
            assets[str(p.relative_to(ROOT))]=sha(p)
        assets.update(result['array_sha256'])
        manifest=dict(name=result['name'],inherited_assets=692,assets_sha256=assets,
            exact_finite_tail_absorption_delta1_through12=result['all_delta1_through12_finite_tail_absorption_proved'],
            Flag1_packet_triple_conditioned_crossing_proved=True,
            universal_admitted_burst_Address_termination_Gray_G17_iid_proved=False,
            rule_ROM_constants_G17_changed=False)
        manifest_path.write_text(json.dumps(manifest,indent=2)+'\n')
    else:
        manifest=json.loads(manifest_path.read_text())
        assert manifest['inherited_assets']==692
        for name,value in parent['assets_sha256'].items():assert manifest['assets_sha256'][name]==value,name
        for name,value in manifest['assets_sha256'].items():assert sha(ROOT/name)==value,name
        result=compute(issue=False)
        assert result==json.loads(receipt_path.read_text()),'Fresh arrays/ranks/full kernel differ from receipt'
        for name,value in manifest['assets_sha256'].items():assert sha(ROOT/name)==value,name
    assert not result['universal_actual_triple_existence_general_boundary_Address_termination_proved']
    assert not manifest['universal_admitted_burst_Address_termination_Gray_G17_iid_proved']
    assert not manifest['rule_ROM_constants_G17_changed']
    print(json.dumps(dict(passed=True,issued=args.issue,readonly=not args.issue,
        assets=len(manifest['assets_sha256']),inherited_assets=692,
        exhaustive_states=result['exhaustive_states'],
        exact_all_delta1_through12_tail_absorption=result['all_delta1_through12_finite_tail_absorption_proved'],
        maximum_ranks=[r['maximum_rank'] for r in result['records']],
        all_saved_arrays_rank_relations_and_new_supplements_recomputed=True,
        triple_conditioned_crossing=True,universal_Address_termination=False,full_reliability=False,
        rule_ROM_constants_G17_changed=False,certificate_sha256=sha(receipt_path),
        manifest_sha256=sha(manifest_path),elapsed=time.perf_counter()-start)),flush=True)
if __name__=='__main__':main()
