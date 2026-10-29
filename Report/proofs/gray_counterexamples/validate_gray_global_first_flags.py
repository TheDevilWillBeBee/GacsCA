#!/usr/bin/env python3
"""Read-only reproduction of the conditional all-receiver GE0 first bank."""
from pathlib import Path
import hashlib,json,time
import check_gray_global_first_flags as check
ROOT=Path(__file__).resolve().parents[3]


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate():
    source=Path(__file__).parent;directory=ROOT/'figs/gray_counterexamples'
    path=directory/'GE0_global_first_flags_certificate.json';r=json.loads(path.read_text())
    assert (r['Q'],r['U'],r['lambda_original'],r['c_original'])==(8192,1048576,24,104)
    assert r['checker_sha256']==digest(check.__file__)
    assert r['proof_sha256']==digest(source/'GE0_GLOBAL_FIRST_FLAGS.md')
    for name,value in r['source_dependencies_sha256'].items():assert digest(source/name)==value
    for name,value in r['receipt_dependencies_sha256'].items():assert digest(directory/name)==value
    assert r['primary_Gray_text_sha256']==digest(ROOT/'papers_txt/gray_readers_guide.txt')
    assert r['results']==json.loads(json.dumps(check.calculate()))
    assert r['no_later_errors'] and r['original_real2_error_geometry_reused']
    assert r['full_intact_GE0_completion_and_own_beta_are_premises']
    assert r['all_integer_actual_first_GT0_banks_and_GE0_delivery_proved_conditionally']
    assert r['no_preloaded_bank_or_independent_upper_history']
    assert not r['positive_actual_Flag2_command_or_late_Workspace_repair_proved']
    assert not r['full_Gray_or_Gacs_refutation_or_iid_theorem']
    assert not r['new_rule_or_shorter_U_or_registered_component_edits']
    return dict(receipt_sha256=digest(path),all_receiver_first_bank_and_flags_validated_conditionally=True,
        full_Gray_rule_late_repair_or_iid_theorem=False)


if __name__=='__main__':
    started=time.monotonic();r=validate();r['elapsed_seconds']=time.monotonic()-started
    print(json.dumps(r))
