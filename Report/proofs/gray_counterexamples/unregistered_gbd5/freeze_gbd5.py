"""Pin GBD5 actual-prefix evidence and unchanged accepted dependencies."""
import hashlib,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
DATA=ROOT/'figs/gray_counterexamples/unregistered_gbd5'
MANIFEST=DATA/'GBD5_manifest.json'
OLD=ROOT/'figs/gray_counterexamples/unregistered_gbd4/GBD4_manifest.json'
ERR=ROOT/'Report/proofs/gray_counterexamples/unregistered_gbd4_root_review'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    old=json.loads(OLD.read_text());assets=dict(old['assets'])
    for path,h in assets.items():assert sha(ROOT/path)==h,(path,'inherited source changed')
    replays=[ROOT/'figs/gray_counterexamples/unregistered_gbd4'/name for name in
             ('GBD4_readonly_own_validation01.json','GBD4_parent_readonly_validation.json')]
    for path in replays:
        receipt=json.loads(path.read_text())
        assert receipt['passed'] and receipt['hashes_unchanged']
        assert receipt['manifest_sha256']==sha(OLD)
    erratum=ROOT/'figs/gray_counterexamples/unregistered_gbd4_root_review/GBD4_head_radius_certificate.json'
    er=json.loads(erratum.read_text())
    assert er['passed'] and er['raw_role_movement_radius']==5
    assert er['accepted_component_radius_at_most']==7
    assert er['manifest_sha256']==sha(OLD)
    added=[OLD,*replays,
        ROOT/'figs/gray_counterexamples/unregistered_gbd4/GBD4_readonly_own_replay01.log',
        ROOT/'figs/robustness/GBD4_parent_readonly_run01.log',
        ERR/'GBD4_HEAD_RADIUS_ERRATUM.md',ERR/'check_gbd4_head_radius.py',erratum,
        ROOT/'gacsca/netlist.py',ROOT/'gacsca/maintenance.py',
        ROOT/'Report/proofs/gray_counterexamples/literal_maintenance.py']
    for directory in (HERE,DATA):
        added.extend(p for p in directory.rglob('*') if p.is_file()
            and '__pycache__' not in p.parts and p!=MANIFEST
            and not p.name.startswith('GBD5_readonly')
            and not p.name.startswith('GBD5_parent'))
    for path in added:assets[str(path.relative_to(ROOT))]=sha(path)
    certificate=DATA/'attempt03/GBD5_certificate.json'
    result=json.loads(certificate.read_text())
    assert result['passed'] and result['universal_complete_prefix_row']==627003
    assert result['universal_native_programme_updates']==33937
    assert result['packing']['packing_complete_raw_row']==593065
    assert result['packing']['born_raw_row']==593066
    assert result['actual_global_E_start'] and result['autonomous_native_ports']
    assert result['actual_all3_History_banks'] and result['full_own_beta'] is False
    m=dict(schema='GBD5 autonomous actual clean-prefix component v1',assets=assets,
        inherited_manifest=str(OLD.relative_to(ROOT)),
        inherited_replays=[str(p.relative_to(ROOT)) for p in replays],
        head_radius_erratum_receipt=str(erratum.relative_to(ROOT)),
        head_radius_erratum_checker=str((ERR/'check_gbd4_head_radius.py').relative_to(ROOT)),
        certificate=str(certificate.relative_to(ROOT)),
        accepted_artifact_directory=str(certificate.parent.relative_to(ROOT)),
        Q=8192,U=1048576,lambda_=24,c=104,K=3387,Head_bits=204,
        native_prefix_beta_bits=7051,stored_instruction_dictionary_bits=0,
        actual_autonomous_native_ports=True,actual_three_History_banks=True,
        actual_packing_reset_birth=True,universal_clean_prefix=True,
        all_raw_upper_Kbit_patterns=True,unused_lower_Info_arbitrary=True,
        raw_role_Head_movement_radius=5,total_prefix_radius_at_most=7,
        universal_native_updates=33937,latest_prefix_completion_row=627003,
        actual_immutable_programme_departure=True,total_autonomous_prefix=True,
        full_own_beta=False,beta_fit=False,full_own_controller_software=False,
        authentic_flag_couriers=False,late_pass=False,full_physical_period=False,
        intact_recursive_initialization=False,noise_map=False,faithful_Gray=False,
        Gray_refutation=False,iid_failure=False,shorter_U=False)
    MANIFEST.write_text(json.dumps(m,indent=2)+'\n')
    print(json.dumps(dict(passed=True,assets=len(assets),manifest_sha256=sha(MANIFEST)),indent=2))

if __name__=='__main__':main()
