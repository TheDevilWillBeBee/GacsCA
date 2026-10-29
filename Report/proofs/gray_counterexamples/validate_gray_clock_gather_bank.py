#!/usr/bin/env python3
"""Read-only exact routing and raw-holder replay for the actual first bank."""
from pathlib import Path
import hashlib,json,time
import check_gray_clock_gather_bank as check
ROOT=Path(__file__).resolve().parents[3]


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate():
    source=Path(__file__).parent;directory=ROOT/'figs/gray_counterexamples'
    path=directory/'GMW7_clock_gather_bank_certificate.json';r=json.loads(path.read_text())
    assert (r['Q'],r['U'],r['lambda_original'],r['c_original'])==(8192,1048576,24,104)
    assert r['checker_sha256']==digest(check.__file__) and r['proof_sha256']==digest(source/'GMW7_CLOCK_GATHER_BANK.md')
    for name,value in r['source_dependencies_sha256'].items():assert digest(source/name)==value
    for name,value in r['receipt_dependencies_sha256'].items():assert digest(directory/name)==value
    for name,value in r['retained_initial_validator_failure_assets_sha256'].items():assert digest(directory/name)==value
    assert r['root_initializer_source_sha256']==digest(check.initial.__file__)
    assert r['root_initializer_proof_sha256']==digest(ROOT/'Report/proofs/GMW7_INTACT_HIERARCHY.md')
    assert r['results']==json.loads(json.dumps(check.calculate()))
    assert r['no_preloaded_bank_or_independent_upper_error_history']
    assert r['exact_changed_GMW7_four_and_five_null_first_bank_lemmas_proved']
    for name in ('actual_Gray_three_gather_Mailbox_clear_refinement',
        'progressing_upper_Ages_early_flag_store_or_repair_proved',
        'full_decoded_boundary_memory_or_iid_refuted','active_rule_or_frozen_component_modified',
        'modified_candidate_emitted'):assert r[name] is False
    return dict(receipt_sha256=digest(path),actual_first_gather_bank_on_shared_intact_real2=True,
        prepared_bank_substituted=False,Gray_flag_repair_or_iid_theorem=False)


if __name__=='__main__':
    started=time.monotonic();result=validate();result['elapsed_seconds']=time.monotonic()-started
    print(json.dumps(result))
