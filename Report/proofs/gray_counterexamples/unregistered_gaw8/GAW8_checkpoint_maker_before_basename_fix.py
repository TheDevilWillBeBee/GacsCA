"""Write NEW GAW8 assets only; all accepted previous assets stay read-only."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[4];S=Path(__file__).resolve().parent
D=ROOT/'figs/gray_counterexamples/unregistered_gaw8'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    previous_path=ROOT/'figs/gray_counterexamples/unregistered_gaw7/GAW7_standalone_assets.json'
    previous_hash=sha(previous_path);previous=json.loads(previous_path.read_text())
    assets=dict(previous['assets_sha256'])
    for name,h in assets.items():assert sha(ROOT/name)==h,('accepted source changed',name)
    receipt_path=D/'GAW8_mixed_clock_repair_receipt.json';result=json.loads(receipt_path.read_text())
    assert len(result['cases'])==795 and result['maximum_clock_recovery']==5111
    assert result['maximum_whole_raw_shadow_recovery']==8182
    certificate_path=D/'GAW8_mixed_clock_certificate.json'
    certificate=dict(name='GAW8 actual intact mixed-clock/control positive repair certificate',
        Q=8192,U=1048576,error_lambda=24,error_separation=104,
        proof_sha256=sha(S/'GAW8_MIXED_CLOCK_REPAIR.md'),receipt_sha256=sha(receipt_path),
        prior_GAW7_manifest_sha256=previous_hash,
        source_dependencies_sha256={str(p.relative_to(ROOT)):sha(p) for p in
            (S/'gaw8_categorical_native.c',S/'gaw8_categorical_native_initial.c',
             S/'search_gaw8_clock_controls.py',S/'search_gaw8_clock_controls_initial.py',
             S/'check_gaw8_mixed_clock_repair.py',S/'validate_gaw8_mixed_clock_repair.py',S/'make_gaw8_checkpoint.py')},
        actual_simulator_identity={str(p.relative_to(ROOT)):sha(p) for p in
            (D/'gaw8_categorical_native.so',D/'gaw8_categorical_native_initial.so')},
        actual_recursively_intact_H=True,same_chronological_physical_error_history=True,
        replacement_clock_offsets=[1,16],source_phase_interval_elapsed=[1,32768],
        actual_source_phase_interval_proved=True,actual_new_Workspace_zero_derived=True,
        canonical_GF_native_factor_proved=True,exact795_case_event_replay=True,
        actual_changed_support_original_c104_real1=True,complete_global_shadow_before97Q=True,
        maximum_clock_recovery=5111,maximum_whole_raw_shadow_recovery=8182,
        first_U_and_all_later_physical_decoded_shadow=True,integer_Q_translates_proved=True,
        initial_query_stop_provenance_preserved=True,
        arbitrary_full_range_Age_control_repair_proved=False,mixed_GF_SF_repair_proved=False,
        all_real1_repair_proved=False,Gray_or_G17_refutation=False,iid_reliability_or_failure=False,
        shorter_U_proved=False,new_rule_created=False,active_rule_modified=False,registered_main_modified=False)
    certificate_path.write_text(json.dumps(certificate,indent=2)+'\n')
    assets[str(previous_path.relative_to(ROOT))]=previous_hash
    for parent,names in ((S,('GAW8_MIXED_CLOCK_REPAIR.md','gaw8_categorical_native.c','gaw8_categorical_native_initial.c',
        'search_gaw8_clock_controls.py','search_gaw8_clock_controls_initial.py','check_gaw8_mixed_clock_repair.py',
        'validate_gaw8_mixed_clock_repair.py','make_gaw8_checkpoint.py')),
        (D,('gaw8_categorical_native.so','gaw8_categorical_native_initial.so','GAW8_clock_control_campaign.json',
        'GAW8_clock_control_generation.log','GAW8_case628_extended.json','GAW8_mixed_clock_generation.log',
        'GAW8_mixed_clock_repair_receipt.json','GAW8_mixed_clock_certificate.json'))):
        for name in names:
            p=parent/name;assets[str(p.relative_to(ROOT))]=sha(p)
    manifest_path=D/'GAW8_standalone_assets.json'
    manifest=dict(name='GAW8 standalone actual positive mixed-clock repair checkpoint',
        assets_sha256=dict(sorted(assets.items())),prior_GAW7_manifest_sha256=previous_hash,
        prior_assets_unchanged=True,exact795_positive_operational_instances=True,
        full_range_or_mixed_GF_recovery_proved=False,Gray_iid_or_shorter_U=False,
        active_rule_modified=False,registered_main_modified=False,new_rule_created=False)
    manifest_path.write_text(json.dumps(manifest,indent=2)+'\n')
    assert sha(previous_path)==previous_hash,'accepted GAW7 manifest changed'
    print(json.dumps(dict(assets=len(assets),proof_sha256=sha(S/'GAW8_MIXED_CLOCK_REPAIR.md'),
        receipt_sha256=sha(receipt_path),certificate_sha256=sha(certificate_path),
        manifest_sha256=sha(manifest_path))),flush=True)

if __name__=='__main__':main()
