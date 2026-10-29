#!/usr/bin/env python3
"""Read-only replay of the conditional right-local native template."""
from pathlib import Path
import hashlib,json,time
import check_ge3_right_template as check
ROOT=Path(__file__).resolve().parents[4]


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate():
    source=Path(__file__).parent;registered=source.parent
    directory=ROOT/'figs/gray_counterexamples/unregistered_ge3'
    path=directory/'GE3_right_template_certificate.json';r=json.loads(path.read_text())
    assert (r['Q'],r['U'],r['lambda_original'],r['c_original'])==(8192,1048576,24,104)
    assert r['checker_sha256']==digest(check.__file__)
    assert r['kernel_sha256']==digest(source/'ge3_right_three_colony_pulse.c')
    assert r['proof_sha256']==digest(source/'GE3_RIGHT_TEMPLATE.md')
    assert r['native_scalar_sha256']==digest(registered/'literal_maintenance.py')
    assert r['accepted_quotient_proof_sha256']==digest(registered/'GE0_FIRST_WORKSPACE_NATIVE.md')
    assert r['accepted_quotient_receipt_sha256']==digest(ROOT/'figs/gray_counterexamples/GE0_first_workspace_native_certificate.json')
    assert r['retained_initial_checker_failure_manifest_sha256']==digest(directory/'GE3_right_template_initial_failure_manifest.json')
    for name,value in r['retained_initial_checker_failure_assets_sha256'].items():assert digest(directory/name)==value
    assert r['results']==json.loads(json.dumps(check.calculate()))
    assert r['conditional_right_local_pulse_theorem']
    assert r['exact_new_right_commands_and_held_final_sources_are_premises']
    assert r['left_commands_and_left_boundary_evolution_not_suppressed']
    assert not r['later_actual_bank_mirror_head_or_positive_Flag2_history_proved']
    assert not r['full_Gray_own_beta_iid_or_shorter_U_result_proved']
    assert not r['registered_artifacts_changed']
    return dict(receipt_sha256=digest(path),conditional_right_template_validated=True,
        fixed_left_endpoint_later_physical_banks_Gray_or_iid_proved=False)


if __name__=='__main__':
    started=time.monotonic();r=validate();r['elapsed_seconds']=time.monotonic()-started;print(json.dumps(r))
