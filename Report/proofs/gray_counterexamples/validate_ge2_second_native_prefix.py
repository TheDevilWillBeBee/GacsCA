#!/usr/bin/env python3
"""Read-only conditional GE2 physical-second-prefix reproduction."""
from pathlib import Path
import hashlib,json,time
import check_ge2_second_native_prefix as check
ROOT=Path(__file__).resolve().parents[3]


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate():
    source=Path(__file__).parent;directory=ROOT/'figs/gray_counterexamples'
    path=directory/'GE2_second_native_prefix_certificate.json';r=json.loads(path.read_text())
    assert (r['Q'],r['U'],r['lambda_original'],r['c_original'])==(8192,1048576,24,104)
    assert r['checker_sha256']==digest(check.__file__)
    assert r['proof_sha256']==digest(source/'GE2_SECOND_NATIVE_PREFIX.md')
    for name,value in r['source_dependencies_sha256'].items():assert digest(source/name)==value
    for name,value in r['receipt_dependencies_sha256'].items():assert digest(directory/name)==value
    for name,value in r['retained_initial_assets_sha256'].items():assert digest(directory/name)==value
    initial=json.loads((directory/'GE2_second_prefix_initial_certificate.json').read_text())
    revision=r['proof_only_reissue_after_finite_run']
    assert revision['initial_receipt_sha256']==digest(directory/'GE2_second_prefix_initial_certificate.json')
    assert revision['initial_proof_sha256']==initial['proof_sha256']
    assert not revision['checker_and_all_computed_results_changed']
    assert initial['checker_sha256']==r['checker_sha256'] and initial['results']==r['results']
    assert r['primary_Gray_text_sha256']==digest(ROOT/'papers_txt/gray_readers_guide.txt')
    assert r['results']==json.loads(json.dumps(check.calculate()))
    assert r['same_shared_row0_Age_only_real2_support']==[0,17*8192] and r['no_later_errors']
    assert r['own_beta_final_layout_intact_completion_and_literal_final_computed_Workspace_remain_premises']
    assert r['GE1_native_only_mirror_departure_unchanged_and_remaining_ports_explicit']
    assert r['actual_second_native_prefix_and_pulse_proved_conditionally']
    for key in ('global_common_upper_Age_assumed','second_Flag2_source_or_repaired_common_clock',
            'faithful_Gray_refutation_full_period_iid_or_shorter_U_theorem','accepted_components_or_main_checkpoint_modified'):
        assert not r[key]
    return dict(receipt_sha256=digest(path),conditional_actual_second_prefix_validated=True,
        faithful_Gray_or_iid_or_common_clock_repair=False)


if __name__=='__main__':
    started=time.monotonic();r=validate();r['elapsed_seconds']=time.monotonic()-started;print(json.dumps(r))
