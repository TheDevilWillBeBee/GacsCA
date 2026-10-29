"""Write NEW GAW9 assets only; accepted GAW0--8 stay read-only."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[4];S=Path(__file__).resolve().parent
D=ROOT/'figs/gray_counterexamples/unregistered_gaw9'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    previous_path=ROOT/'figs/gray_counterexamples/unregistered_gaw8/GAW8_standalone_assets.json'
    previous_hash=sha(previous_path);previous=json.loads(previous_path.read_text())
    assets=dict(previous['assets_sha256'])
    for name,h in assets.items():assert sha(ROOT/name)==h,('accepted source changed',name)
    receipt_path=D/'GAW9_native_factor_receipt.json';result=json.loads(receipt_path.read_text())
    assert len(result['cases'])==140 and result['maximum_mixed_geometry_quiet']==5115
    assert result['maximum_uniform_geometry_quiet']==2736
    sources=('GAW9_ACTUAL_NATIVE_FACTOR.md','gaw9_native_info.c','gaw9_geometry_query.c',
        'search_gaw9_mixed_native.py','search_gaw9_uniform_native.py','check_gaw9_native_factor.py',
        'validate_gaw9_native_factor.py','make_gaw9_checkpoint.py')
    certificate_path=D/'GAW9_native_factor_certificate.json'
    certificate=dict(name='GAW9 actual mixed native/Info factor and selected real1 geometry envelopes',
        Q=8192,U=1048576,error_lambda=24,error_separation=104,
        proof_sha256=sha(S/'GAW9_ACTUAL_NATIVE_FACTOR.md'),receipt_sha256=sha(receipt_path),
        prior_GAW8_manifest_sha256=previous_hash,
        source_dependencies_sha256={str((S/n).relative_to(ROOT)):sha(S/n) for n in sources},
        actual_simulator_identity={str((D/n).relative_to(ROOT)):sha(D/n) for n in
            ('gaw9_native_info.so','gaw9_geometry_query.so')},
        actual_recursively_intact_H=True,same_chronological_physical_error_history=True,
        actual_noisy_initial_clock=786432,no_head_birth_horizon=32768,
        admitted_legal_Age_count=983040,full_legal_Age_count=1048576,
        birth_clock_restriction_explicit=True,actual_Info_Workspace_factor_proved=True,
        actual_Head_Out_courier_zero_contract_proved=True,
        infinite_exterior_and_geometry_absorption_proved=True,
        exact140_case_geometry_envelope_replay=True,actual_changed_support_original_c104_real1=True,
        maximum_mixed_geometry_quiet=5115,maximum_uniform_geometry_quiet=2736,
        maximum_mixed_native_flags_quiet=8187,
        actual_nonzero_WF_source_reachable=True,actual_shifted_five_copy_late_birth_reachable=True,
        initial_checker_summary_failure_provenance_preserved=True,
        all_admitted_payloads_geometry_repair_proved=False,all_legal_Age_control_repair_proved=False,
        Flags_U_recovery_proved=False,History_decoder_or_whole_period_map_proved=False,
        all_real1_repair_proved=False,Gray_or_G17_refutation=False,iid_reliability_or_failure=False,
        shorter_U_proved=False,new_rule_created=False,active_rule_modified=False,registered_main_modified=False)
    certificate_path.write_text(json.dumps(certificate,indent=2)+'\n')
    assets[str(previous_path.relative_to(ROOT))]=previous_hash
    for parent,names in ((S,sources+('GAW9_checker_before_recovery_bound_fix.py',
                                    'GAW9_proof_before_recovery_bound_fix.md')),
        (D,('gaw9_native_info.so','gaw9_geometry_query.so','GAW9_geometry_query_generation.json',
        'GAW9_mixed_native_search.json','GAW9_mixed_native_generation01.log',
        'GAW9_uniform_native_search.json','GAW9_uniform_native_generation01.log',
        'GAW9_native_factor_generation01.log','GAW9_native_factor_generation02.log',
        'GAW9_recovery_bound_failure_provenance.json','GAW9_native_factor_receipt.json',
        'GAW9_native_factor_certificate.json'))):
        for name in names:
            p=parent/name;assets[str(p.relative_to(ROOT))]=sha(p)
    manifest_path=D/'GAW9_standalone_assets.json'
    manifest=dict(name='GAW9 standalone actual mixed-native factor and selected geometry envelope checkpoint',
        assets_sha256=dict(sorted(assets.items())),prior_GAW8_manifest_sha256=previous_hash,
        prior_assets_unchanged=True,exact140_positive_geometry_envelope_instances=True,
        full_range_or_all_payloads_repair_proved=False,History_decoder_or_Gray_iid_or_shorter_U=False,
        active_rule_modified=False,registered_main_modified=False,new_rule_created=False)
    manifest_path.write_text(json.dumps(manifest,indent=2)+'\n')
    assert sha(previous_path)==previous_hash,'accepted GAW8 manifest changed'
    print(json.dumps(dict(assets=len(assets),proof_sha256=sha(S/'GAW9_ACTUAL_NATIVE_FACTOR.md'),
        receipt_sha256=sha(receipt_path),certificate_sha256=sha(certificate_path),
        manifest_sha256=sha(manifest_path))),flush=True)

if __name__=='__main__':main()
