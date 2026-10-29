"""Write NEW GAW7 receipts only; frozen GAW6 manifest is read-only input."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[4]
S=Path(__file__).resolve().parent
D=ROOT/'figs/gray_counterexamples/unregistered_gaw7'

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    previous_manifest_path=ROOT/'figs/gray_counterexamples/unregistered_gaw6/GAW6_standalone_assets.json'
    previous_manifest_hash=sha(previous_manifest_path)
    previous=json.loads(previous_manifest_path.read_text())
    assets=dict(previous['assets_sha256'])
    for name,digest in assets.items():assert sha(ROOT/name)==digest,('frozen asset changed',name)
    certificate_path=D/'GAW7_clock_prefix_certificate.json'
    certificate=dict(name='GAW7 actual intact uniform Age-only original-real1 native-prefix certificate',
        Q=8192,U=1048576,error_lambda=24,error_separation=104,
        proof_sha256=sha(S/'GAW7_UNIFORM_CLOCK_PREFIX.md'),receipt_sha256=sha(D/'GAW7_clock_prefix_receipt.json'),
        source_dependencies_sha256={str(path.relative_to(ROOT)):sha(path) for path in
            (S/'gaw7_clock_events.c',S/'check_gaw7_clock_prefix.py',S/'validate_gaw7_clock_prefix.py',S/'make_gaw7_checkpoint.py')},
        prior_GAW6_manifest_sha256=previous_manifest_hash,
        actual_simulator_identity={str(path.relative_to(ROOT)):sha(path) for path in
            (D/'gaw7_clock_events',D/'gaw7_clock_events.so')},
        intact_H_actual96Q_same_fault=True,arbitrary_uniform_replacement_Age_proved=True,
        uniform_Age_range=[0,1048575],nontrivial_Age_excluded=786432,
        canonical_GF_all_raw_clock_closure_proved=True,actual_source_cone_proved=True,
        actual_WF_zero_derived=True,universal_binary_native_factor_proved=True,
        source_silence_through_elapsed=3844,minimum_head_Out_distance_to_special_primary=3845,
        all_Q_phases_exact_event_replay=True,maximum_clock_recovery=2736,maximum_native_quiet=6831,
        native_recovery_before97Q_proved=True,fixed_two_adjacent_colonies_entire_native_trajectory_proved=True,
        native_correct_through_first_U_boundary_proved=True,
        arbitrary_mixed_Age_or_control_recovery_proved=False,actual_late_History_or_output_map_proved=False,
        Gray_or_G17_refutation_proved=False,iid_memory_failure_proved=False,shorter_U_proved=False,
        new_rule_created=False,active_rule_modified=False,registered_main_modified=False)
    certificate_path.write_text(json.dumps(certificate,indent=2)+'\n')
    assets[str(previous_manifest_path.relative_to(ROOT))]=previous_manifest_hash
    for parent,names in (
        (S,('GAW7_UNIFORM_CLOCK_PREFIX.md','gaw7_clock_events.c','check_gaw7_clock_prefix.py',
            'validate_gaw7_clock_prefix.py','make_gaw7_checkpoint.py')),
        (D,('gaw7_clock_events','gaw7_clock_events.so','clock_uniform_width16.csv','clock_uniform_width16.log',
            'GAW7_clock_prefix_receipt.json','GAW7_clock_prefix_certificate.json','GAW7_clock_prefix_generation.log'))):
        for name in names:
            asset_path=parent/name
            assets[str(asset_path.relative_to(ROOT))]=sha(asset_path)
    manifest_path=D/'GAW7_standalone_assets.json'
    manifest=dict(name='GAW7 standalone actual uniform-Age native-prefix checkpoint',
        assets_sha256=dict(sorted(assets.items())),prior_GAW6_manifest_sha256=previous_manifest_hash,
        prior_assets_unchanged=True,actual_uniform_native_prefix_proved=True,
        arbitrary_mixed_clock_or_decoded_period_proved=False,Gray_iid_or_shorter_U=False,
        active_rule_modified=False,registered_main_modified=False,new_rule_created=False)
    manifest_path.write_text(json.dumps(manifest,indent=2)+'\n')
    assert sha(previous_manifest_path)==previous_manifest_hash,'frozen GAW6 manifest changed'
    print(json.dumps(dict(assets=len(assets),proof_sha256=sha(S/'GAW7_UNIFORM_CLOCK_PREFIX.md'),
        certificate_sha256=sha(certificate_path),receipt_sha256=sha(D/'GAW7_clock_prefix_receipt.json'),
        manifest_sha256=sha(manifest_path))),flush=True)

if __name__=='__main__':main()
