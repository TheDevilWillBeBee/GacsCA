"""Write only NEW GAW10 provenance; all prior accepted assets stay frozen."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[4];S=Path(__file__).resolve().parent
D=ROOT/'figs/gray_counterexamples/unregistered_gaw10'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    previous_path=ROOT/'figs/gray_counterexamples/unregistered_gaw9/GAW9_standalone_assets.json'
    previous_hash=sha(previous_path);previous=json.loads(previous_path.read_text());assets=dict(previous['assets_sha256'])
    for name,h in assets.items():assert sha(ROOT/name)==h,('accepted source changed',name)
    receipt_path=D/'GAW10_shifted_birth_receipt.json';result=json.loads(receipt_path.read_text())
    assert result['actual_bank_and_output_map']['first_boundary_bad_upper_cells']==[0]
    sources=('GAW10_SHIFTED_BIRTH_REPAIR.md','trace_gaw10_birth.py','gaw10_postbirth_factor.c',
        'check_gaw10_shifted_birth.py','validate_gaw10_shifted_birth.py','make_gaw10_checkpoint.py')
    certificate_path=D/'GAW10_shifted_birth_certificate.json'
    certificate=dict(name='GAW10 actual shifted late-Head birth permitted U/2U repair certificate',
        Q=8192,U=1048576,error_lambda=24,error_separation=104,
        proof_sha256=sha(S/'GAW10_SHIFTED_BIRTH_REPAIR.md'),receipt_sha256=sha(receipt_path),
        prior_GAW9_manifest_sha256=previous_hash,
        source_dependencies_sha256={str((S/n).relative_to(ROOT)):sha(S/n) for n in sources},
        actual_simulator_sha256=sha(D/'gaw10_postbirth_factor.so'),
        actual_recursively_intact_H=True,same_chronological_physical_error_history=True,
        actual_error_row=786432,actual_error_interval=[3842,3858],actual_original_c104_real1=True,
        raw_replacement_GF_shift=1,raw_replacement_Age=835584,all_actual_SF_retained=True,
        full_actual_local_R_prefix_replayed=True,extra_Head_counts=[5,2,0],
        extra_Head_disappearance_and_no_write_proved=True,
        actual_postbirth_Info_History_Workspace_factor_proved=True,
        actual_same_history_bank_derived=True,geometry_quiet_elapsed=1450,native_flags_quiet_elapsed=5545,
        actual_erased_History_logical_interval=[3842,8190],postbirth_exact_updated_sites=51493604,
        actual_reset_birth_commit_composition_proved=True,actual_late_execution_updates=65117,
        one_permitted_upper_Flag1_error_at_U=True,complete_global_raw_shadow_at2U_and_all_later=True,
        arbitrary_birth_near_real1_repair_proved=False,direct_whole_period_grid_simulation_claimed=False,
        Gray_or_G17_refutation=False,iid_reliability_or_failure=False,shorter_U_proved=False,
        new_rule_created=False,active_rule_modified=False,registered_main_modified=False)
    certificate_path.write_text(json.dumps(certificate,indent=2)+'\n')
    assets[str(previous_path.relative_to(ROOT))]=previous_hash
    for parent,names in ((S,sources),(D,('gaw10_postbirth_factor.so','GAW10_factor_generation.json',
        'GAW10_shifted_birth_prefix.json','GAW10_shifted_birth_prefix_generation01.log',
        'GAW10_shifted_birth_generation01.log','GAW10_shifted_birth_generation02.log',
        'GAW10_shifted_birth_receipt.json','GAW10_shifted_birth_certificate.json'))):
        for name in names:
            p=parent/name;assets[str(p.relative_to(ROOT))]=sha(p)
    manifest_path=D/'GAW10_standalone_assets.json'
    manifest=dict(name='GAW10 standalone actual intact shifted-Head history and permitted2U repair checkpoint',
        assets_sha256=dict(sorted(assets.items())),prior_GAW9_manifest_sha256=previous_hash,
        prior_assets_unchanged=True,one_actual_positive_operational_instance=True,
        arbitrary_birth_near_real1_or_Gray_iid_or_shorter_U=False,new_rule_created=False,
        active_rule_modified=False,registered_main_modified=False)
    manifest_path.write_text(json.dumps(manifest,indent=2)+'\n')
    assert sha(previous_path)==previous_hash,'accepted GAW9 manifest changed'
    print(json.dumps(dict(assets=len(assets),proof_sha256=sha(S/'GAW10_SHIFTED_BIRTH_REPAIR.md'),
        receipt_sha256=sha(receipt_path),certificate_sha256=sha(certificate_path),manifest_sha256=sha(manifest_path))),flush=True)

if __name__=='__main__':main()
