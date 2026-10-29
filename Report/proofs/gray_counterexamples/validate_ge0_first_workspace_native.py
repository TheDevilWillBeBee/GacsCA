#!/usr/bin/env python3
"""Read-only conditional GE0 first-Workspace native-prefix reproduction."""
from pathlib import Path
import hashlib,json,time
import check_ge0_first_workspace_native as check
ROOT=Path(__file__).resolve().parents[3]


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate():
    source=Path(__file__).parent;directory=ROOT/'figs/gray_counterexamples'
    path=directory/'GE0_first_workspace_native_certificate.json';r=json.loads(path.read_text())
    assert (r['Q'],r['U'],r['lambda_original'],r['c_original'])==(8192,1048576,24,104)
    assert r['checker_sha256']==digest(check.__file__)
    assert r['proof_sha256']==digest(source/'GE0_FIRST_WORKSPACE_NATIVE.md')
    for name,value in r['source_dependencies_sha256'].items():assert digest(source/name)==value
    for name,value in r['receipt_dependencies_sha256'].items():assert digest(directory/name)==value
    assert r['primary_Gray_text_sha256']==digest(ROOT/'papers_txt/gray_readers_guide.txt')
    assert r['results']==json.loads(json.dumps(check.calculate()))
    result=r['results']['finite_native_prefix']
    assert result['first_exact_20Q_clock_row']==797352
    assert result['first_exact_quiet_20Q_native_row']==806912
    assert r['no_later_errors']
    assert r['intact_final_GE0_completion_own_beta_and_literal_late_Workspace_equations_remain_premises']
    assert r['actual_p41_computed_final_SimBit_held_on_this_prefix']
    assert r['first_pulse_conditional_native_clock_expansion_17Q_to20Q_proved']
    assert not r['first_pulse_recovers_common_clock']
    assert not r['full_faithful_Gray_rule_or_counterexample_or_iid_memory_result']
    assert not r['shorter_U_or_active_rule_or_registered_component_changes']
    return dict(receipt_sha256=digest(path),conditional_first_Workspace_native_prefix_validated=True,
        full_Gray_rule_later_repair_or_iid_result=False)


if __name__=='__main__':
    started=time.monotonic();r=validate();r['elapsed_seconds']=time.monotonic()-started
    print(json.dumps(r))
