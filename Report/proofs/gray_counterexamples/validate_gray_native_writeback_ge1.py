#!/usr/bin/env python3
"""Read-only replay of the explicitly changed GE1 conditional bridge."""
from pathlib import Path
import hashlib,json,time
import check_gray_native_writeback_ge1 as check
ROOT=Path(__file__).resolve().parents[3]


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate():
    source=Path(__file__).parent;directory=ROOT/'figs/gray_counterexamples'
    path=directory/'GE1_native_writeback_second_bank_certificate.json';r=json.loads(path.read_text())
    assert (r['Q'],r['U'],r['lambda_original'],r['c_original'])==(8192,1048576,24,104)
    assert r['checker_sha256']==digest(check.__file__)
    assert r['proof_sha256']==digest(source/'GE1_NATIVE_WRITEBACK_SECOND_BANK.md')
    for name,value in r['source_dependencies_sha256'].items():assert digest(source/name)==value
    for name,value in r['receipt_dependencies_sha256'].items():assert digest(directory/name)==value
    for name,value in r['assets_sha256'].items():assert digest(directory/name)==value
    assert r['primary_Gray_text_sha256']==digest(ROOT/'papers_txt/gray_readers_guide.txt')
    assert r['results']==json.loads(json.dumps(check.calculate()))
    assert r['same_shared_clock_only_row0_fault']==[0,17*8192] and r['no_later_errors']
    assert r['original_real2_geometry_reused'] and r['actual_first_native_result_not_preloaded']
    assert r['explicit_native_only_fifth_store_change'] and r['remaining_ports_are_declared']
    assert r['own_beta_final_layout_intact_completion_and_literal_Workspace_are_premises']
    assert r['conditional_native_first_commit_and_actual_next_bank_proved']
    assert not r['universal_noisy_extension_or_full_period_or_positive_Flag2_repair']
    assert not r['faithful_Gray_refutation_or_iid_theorem']
    assert not r['shorter_U_or_active_rule_change']
    return dict(receipt_sha256=digest(path),conditional_GE1_native_commit_and_actual_next_bank_validated=True,
        faithful_Gray_or_iid_result=False)


if __name__=='__main__':
    started=time.monotonic();r=validate();r['elapsed_seconds']=time.monotonic()-started
    print(json.dumps(r))
