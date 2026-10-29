"""Pin GBD6 and exactly reuse the accepted actual-prefix dependencies."""
import hashlib,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
DATA=ROOT/'figs/gray_counterexamples/unregistered_gbd6'
MANIFEST=DATA/'GBD6_manifest.json'
OLD=ROOT/'figs/gray_counterexamples/unregistered_gbd5/GBD5_manifest.json'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    old=json.loads(OLD.read_text());assets=dict(old['assets'])
    for path,h in assets.items():assert sha(ROOT/path)==h,(path,'old asset changed')
    replays=[ROOT/'figs/gray_counterexamples/unregistered_gbd5'/name for name in
        ('GBD5_readonly_own_validation01.json','GBD5_parent_readonly_validation.json')]
    for path in replays:
        receipt=json.loads(path.read_text())
        assert receipt['passed'] and receipt['hashes_unchanged']
        assert receipt['manifest_sha256']==sha(OLD)
    added=[OLD,*replays,
        ROOT/'figs/gray_counterexamples/unregistered_gbd5/GBD5_readonly_own_replay01.log',
        ROOT/'figs/robustness/GBD5_parent_readonly_run01.log',
        ROOT/'papers_txt/gray_readers_guide.txt',
        ROOT/"papers/A Reader's Guide to Gacs's ``Positive Rates'' Paper.pdf",
        ROOT/'gacsca/candidates.py']
    for directory in (HERE,DATA):
        added.extend(p for p in directory.rglob('*') if p.is_file()
            and '__pycache__' not in p.parts and p!=MANIFEST
            and not p.name.startswith('GBD6_readonly')
            and not p.name.startswith('GBD6_parent'))
    for path in added:assets[str(path.relative_to(ROOT))]=sha(path)
    certificate=DATA/'attempt04/GBD6_certificate.json'
    c=json.loads(certificate.read_text());assert c['passed']
    assert c['emission']['h1']['total_bits']==12653
    assert c['emission']['printed']['total_bits']==12708
    assert c['universal_controller_cost']['universal_issued_component_updates']==15064
    assert c['native_only_early_flag_delivery']['courier_seed_action']==638976
    assert c['native_only_early_flag_delivery']['source_correct_raw_rows']==[644763,641379]
    m=dict(schema='GBD6 total rule family / two-field encoder rejection v1',
        assets=assets,inherited_manifest=str(OLD.relative_to(ROOT)),
        inherited_replays=[str(p.relative_to(ROOT)) for p in replays],
        inherited_provenance_only=True,certificate=str(certificate.relative_to(ROOT)),
        accepted_artifact_directory=str(certificate.parent.relative_to(ROOT)),
        Q=8192,U=1048576,lambda_=24,c=104,K=3387,Head_bits=204,
        stored_instruction_dictionary_bits=0,total_rule_family=True,
        total_rule_radius_at_most=7,all_raw_states_defined=True,
        native_Mailbox_History_only=True,issued_component_bits=6043,
        universal_prepared_component_updates=15064,
        h1_rejected_listing_bits=12653,printed_rejected_listing_bits=12708,
        h1_out_of_Q_targets=65,printed_out_of_Q_targets=68,
        actual_clean_native_only_source_provenance=True,
        actual_source_correct_raw_rows=[644763,641379],
        explicit_78Q_courier_seed=True,original_75Q_readiness=False,
        conditional_output_transport=True,final_computed_self_Info_order=True,
        stronger_wipe_departure=True,immutable_code_departure=True,
        extended_stage5_rest_departure=True,complete_beta=False,beta_fit=False,
        complete_self_simulation=False,universal_whole_runtime=False,full_period=False,
        intact_recursive_initialization=False,error_history=False,noise_map=False,
        faithful_Gray=False,Gray_refutation=False,iid_failure=False,shorter_U=False)
    MANIFEST.write_text(json.dumps(m,indent=2)+'\n')
    print(json.dumps(dict(passed=True,assets=len(assets),manifest_sha256=sha(MANIFEST)),indent=2))

if __name__=='__main__':main()
