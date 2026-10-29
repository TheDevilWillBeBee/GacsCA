"""Retain the initial proof receipt and freeze/replay its clarification."""
from pathlib import Path
import argparse,hashlib,json,time
from check_gawn13_majority_reduction import compute,ROOT,HERE,OUT
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def compare_initial(current):
    initial_path=OUT/'GAWN13_majority_reduction_certificate.json'
    initial=json.loads(initial_path.read_text())
    proof_key=str((HERE/'GAWN13_NATIVE_MAJORITY_REDUCTION.md').relative_to(ROOT))
    retained=OUT/'GAWN13_initial_native_majority_reduction.md'
    assert sha(retained)==initial['source_sha256'][proof_key]
    a=dict(initial);b=dict(current);old_sources=a.pop('source_sha256');new_sources=b.pop('source_sha256')
    assert a==b,'A proof clarification must not change finite values'
    assert set(old_sources)==set(new_sources)
    for name,value in old_sources.items():
        if name!=proof_key:assert new_sources[name]==value==sha(ROOT/name),name
    assert new_sources[proof_key]==sha(ROOT/proof_key)
    return dict(initial_certificate_sha256=sha(initial_path),initial_proof_sha256=sha(retained),
        current_proof_sha256=sha(ROOT/proof_key),initial_checker_sha256=sha(HERE/'check_gawn13_majority_reduction.py'),
        checker_and_all_computed_results_changed=False,current_proof_prefix_preservation_clarified=True,
        exact_initial_proof_retained=True)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--issue',action='store_true');args=parser.parse_args()
    started=time.perf_counter();parent_path=ROOT/'figs/gray_counterexamples/unregistered_gawn12/GAWN12_standalone_assets.json'
    parent=json.loads(parent_path.read_text());assert len(parent['assets_sha256'])==678
    manifest_path=OUT/'GAWN13_standalone_assets.json'
    path=OUT/'GAWN13_majority_reduction_certificate_v2.json'
    manifest=None if args.issue else json.loads(manifest_path.read_text())
    if manifest is not None:
        assert manifest['inherited_assets']==678
        for name,value in parent['assets_sha256'].items():assert manifest['assets_sha256'][name]==value,name
        for name,value in manifest['assets_sha256'].items():assert sha(ROOT/name)==value,name
    current=compute();reissue=compare_initial(current)
    current['proof_only_reissue']=reissue
    if args.issue:
        assert not path.exists() and not manifest_path.exists(),'Never overwrite frozen receipts'
        path.write_text(json.dumps(current,indent=2)+'\n')
        assets=dict(parent['assets_sha256'])
        for p in (parent_path,ROOT/'figs/gray_counterexamples/unregistered_gawn12/GAWN12_readonly_run01.log',
            HERE/'GAWN13_NATIVE_MAJORITY_REDUCTION.md',OUT/'GAWN13_initial_native_majority_reduction.md',
            HERE/'gawn13_sparse_native_probe.c',HERE/'check_sparse_native_probe.py',
            OUT/'GAWN13_sparse_native_probe.json',ROOT/'figs/robustness/GAWN13_sparse_probe_run01.log',
            HERE/'gawn13_majority_table.c',HERE/'check_gawn13_majority_reduction.py',
            OUT/'GAWN13_majority_reduction_certificate.json',ROOT/'figs/robustness/GAWN13_majority_reduction_run01.log',
            Path(__file__),path):assets[str(p.relative_to(ROOT))]=sha(p)
        assert len(assets)==692
        manifest=dict(name='GAWN13 exact majority transport, actual boundary feedback open',
            inherited_assets=678,assets_sha256=assets,
            ordinary_GF_left_majority_exception_bound_clean_prefix_proved=True,
            finite_GF_only_boundary_overapproximation_has_nonzero_cycles=True,
            actual_boundary_termination_Gray_G17_iid_or_bit_failure_proved=False,
            initial_proof_and_receipts_retained_finite_values_unchanged=True,
            rule_ROM_constants_G17_changed=False)
        manifest_path.write_text(json.dumps(manifest,indent=2)+'\n')
        print(json.dumps(dict(issued=True,assets=len(assets),inherited_assets=678,
            manifest_sha256=sha(manifest_path),certificate_sha256=sha(path),
            proof_only_reissue_computed_values_unchanged=True,elapsed=time.perf_counter()-started)));return
    assert current==json.loads(path.read_text()),'Fresh majority/graph/sparse checks differ from receipt'
    assert manifest['ordinary_GF_left_majority_exception_bound_clean_prefix_proved']
    assert manifest['finite_GF_only_boundary_overapproximation_has_nonzero_cycles']
    assert manifest['initial_proof_and_receipts_retained_finite_values_unchanged']
    assert not manifest['actual_boundary_termination_Gray_G17_iid_or_bit_failure_proved']
    assert not manifest['rule_ROM_constants_G17_changed']
    for name,value in manifest['assets_sha256'].items():assert sha(ROOT/name)==value,name
    print(json.dumps(dict(passed=True,readonly=True,assets=len(manifest['assets_sha256']),inherited_assets=678,
        all_new_majority_table_full_kernel_boundary_graph_and990_sparse_histories_recomputed=True,
        certificate_sha256=sha(path),manifest_sha256=sha(manifest_path),
        ordinary_majority_exception_bound_clean_prefix=True,actual_boundary_crossing_or_Address_termination=False,
        proof_only_reissue_computed_values_unchanged=True,full_reliability=False,
        rule_ROM_constants_G17_changed=False,elapsed=time.perf_counter()-started)))
if __name__=='__main__':main()
