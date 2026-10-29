#!/usr/bin/env python3
"""Read-only replay of the new conditional command/source interface proof."""
from pathlib import Path
import hashlib,json,time
import check_gray_flag_command_contract as check
ROOT=Path(__file__).resolve().parents[3]


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate():
    directory=ROOT/'figs/gray_counterexamples';source=Path(__file__).parent
    path=directory/'Gray_flag_command_contract_certificate.json';r=json.loads(path.read_text())
    assert (r['Q'],r['U'],r['lambda_original'],r['c_original'])==(8192,1048576,24,104)
    assert r['checker_sha256']==digest(check.__file__)
    assert r['proof_sha256']==digest(source/'GRAY_FLAG_COMMAND_CONTRACT.md')
    for name,value in r['source_dependencies_sha256'].items():assert digest(source/name)==value
    for name,value in r['receipt_dependencies_sha256'].items():assert digest(directory/name)==value
    for name,value in r['retained_initial_checker_failure_assets_sha256'].items():assert digest(directory/name)==value
    assert r['initial_checker_bitwise_vs_whole_word_vote_assertion_removed']
    assert r['root_initializer_source_sha256']==digest(check.initial.__file__)
    assert r['root_initializer_proof_sha256']==digest(ROOT/'Report/proofs/GMW7_INTACT_HIERARCHY.md')
    assert r['primary_gray_text_sha256']==digest(ROOT/'papers_txt/gray_readers_guide.txt')
    assert r['results']==check.calculate()
    assert r['Workspace_SimBit_premise_is_final_computed_not_pre_wipe']
    assert r['changed_GMW7_first_window_interface_gap_only']
    for name in ('actual_damaged_Gray_input_bank_Age_progression_and_early_evaluator_refinement',
        'full_corrected_Gray_rule_reconstruction_or_reliability','active_rule_modified',
        'modified_candidate_emitted','Gray_Gacs_Address_decoded_memory_or_iid_refuted'):
        assert r[name] is False
    return dict(receipt_sha256=digest(path),conditional_bank_and_pulse_lemmas=True,
        first_window_GMW7_interface_gap=True,modified_rule_emitted=False,
        actual_Gray_context_or_iid_result=False)


if __name__=='__main__':
    started=time.monotonic();result=validate();result['elapsed_seconds']=time.monotonic()-started
    print(json.dumps(result))
