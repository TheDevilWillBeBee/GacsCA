#!/usr/bin/env python3
"""Read-only exact full-map and actual emitted execution replay."""
from pathlib import Path
import hashlib,json,time
import check_gray_clock_stroboscopic_native as check
ROOT=Path(__file__).resolve().parents[3]


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate():
    source=Path(__file__).parent;directory=ROOT/'figs/gray_counterexamples'
    path=directory/'GMW7_clock_stroboscopic_native_certificate.json';r=json.loads(path.read_text())
    assert (r['Q'],r['U'],r['lambda_original'],r['c_original'])==(8192,1048576,24,104)
    assert r['checker_sha256']==digest(check.__file__)
    assert r['proof_sha256']==digest(source/'GMW7_CLOCK_STROBOSCOPIC_NATIVE.md')
    for name,value in r['source_dependencies_sha256'].items():assert digest(source/name)==value
    for name,value in r['receipt_dependencies_sha256'].items():assert digest(directory/name)==value
    for name,value in r['retained_initial_instrumentation_failure_assets_sha256'].items():
        assert digest(directory/name)==value
    assert r['root_initializer_source_sha256']==digest(check.initial.__file__)
    assert r['root_initializer_proof_sha256']==digest(ROOT/'Report/proofs/GMW7_INTACT_HIERARCHY.md')
    assert r['results']==json.loads(json.dumps(check.calculate()))
    for name in ('actual_physical_history_lift_proved_by_factor_gather_programme_commit_contracts',
        'intact_recursive_start_and_one_shared_actual_original_real2_history',
        'no_preloaded_bank_or_independent_upper_error_history',
        'decoded_fifth_Age_failure_for_changed_GMW7_proved',
        'inside_Flag2_zero_for_first16_actual_evaluations_proved'):assert r[name]
    for name in ('actual_Gray_gathering_or_simulated_flag_repair_refinement',
        'all_time_stroboscopic_recovery_or_iid_or_memory_failure_proved',
        'active_rule_or_previously_frozen_component_modified','new_rule_or_schedule_emitted'):assert not r[name]
    return dict(receipt_sha256=digest(path),actual_changed_F7_first16_stroboscopic_maps_proved=True,
        first_noncommon_Age_epoch=5,first_noncommon_Age_colony=2,
        no_preloaded_bank_or_separate_upper_history=True,Gray_or_iid_refuted=False)


if __name__=='__main__':
    started=time.monotonic();result=validate();result['elapsed_seconds']=time.monotonic()-started
    print(json.dumps(result))
