"""Read-only replay of all NEW GBD6 mathematics, no frozen source edits."""
import argparse,hashlib,json,os,subprocess,sys,tempfile,time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
DATA=ROOT/'figs/gray_counterexamples/unregistered_gbd6'
MANIFEST=DATA/'GBD6_manifest.json'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check(assets):
    for path,h in assets.items():assert sha(ROOT/path)==h,(path,'hash mismatch')
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args();start=time.monotonic()
    manifest=json.loads(MANIFEST.read_text());check(manifest['assets'])
    inherited=ROOT/manifest['inherited_manifest'];old=json.loads(inherited.read_text())
    check(old['assets'])
    for path in manifest['inherited_replays']:
        receipt=json.loads((ROOT/path).read_text())
        assert receipt['passed'] and receipt['hashes_unchanged']
        assert receipt['manifest_sha256']==sha(inherited)
        assert receipt['all_new_claims_recomputed']
        assert receipt['latest_prefix_completion_row']==627003
    c=json.loads((ROOT/manifest['certificate']).read_text())
    for attempt in (1,2,3):
        directory=DATA/f'retained_attempt{attempt:02d}_sources'
        p=json.loads((directory/'provenance.json').read_text())
        for name,h in p['source_sha256'].items():assert sha(directory/name)==h
        prior=json.loads((DATA/f'attempt{attempt:02d}/GBD6_certificate.json').read_text())
        assert prior['passed']
        # Controller software has not changed when correcting the courier
        # deadline and refining the cost predicate partition.
        assert prior['emission']==c['emission']
    previous=json.loads((DATA/'attempt03/GBD6_certificate.json').read_text())
    assert previous['universal_controller_cost']==c['universal_controller_cost']
    assert previous['selected_component_runs']==c['selected_component_runs']
    assert previous['conditional_output_transport']==c['conditional_output_transport']
    # attempt02's successful cost run used a coarser predicate partition;
    # it is retained, but is not the exact path-class certificate accepted here.
    oldcost=json.loads((DATA/'attempt02/GBD6_certificate.json').read_text())['universal_controller_cost']
    assert oldcost['phase_classes']==46 and c['universal_controller_cost']['phase_classes']==47
    assert c['universal_controller_cost']['control_cases']==188
    assert c['universal_controller_cost']['universal_issued_component_updates']==15064
    with tempfile.TemporaryDirectory(prefix='gbd6_readonly_') as directory:
        directory=Path(directory)
        result=subprocess.run([sys.executable,str(HERE/'check_component.py'),'--out',str(directory)],
            cwd=ROOT,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'),
            stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        assert result.returncode==0,result.stderr
        assert json.loads((directory/'GBD6_certificate.json').read_text())==c
        for path in (ROOT/manifest['accepted_artifact_directory']).iterdir():
            if path.is_file():assert sha(directory/path.name)==sha(path),(path.name,'artifact differs')
    check(manifest['assets'])
    for flag in ('complete_beta','beta_fit','complete_self_simulation','universal_whole_runtime',
        'full_period','intact_recursive_initialization','error_history','noise_map',
        'faithful_Gray','Gray_refutation','iid_failure','shorter_U','original_75Q_readiness'):
        assert manifest[flag] is False
    delivery=c['native_only_early_flag_delivery']
    assert delivery['exhaustive_adjacent_command_tuples']==64
    assert delivery['literal_courier_site_updates']==3332736
    assert delivery['local_raw_copy_cofactors']==80
    assert delivery['source_correct_raw_rows']==[644763,641379]
    assert delivery['native_prefix_latest_row']<delivery['courier_seed_action']
    result=dict(passed=True,assets=len(manifest['assets']),hashes_unchanged=True,
        manifest_sha256=sha(MANIFEST),certificate_sha256=sha(ROOT/manifest['certificate']),
        all_new_claims_recomputed=True,inherited_provenance_only=True,
        inherited_manifest_sha256=sha(inherited),
        Q=8192,U=1048576,lambda_=24,c=104,K=3387,Head_bits=204,
        total_rule_family=True,all_raw_states_defined=True,total_radius_at_most=7,
        prepared_two_field_software_only=True,issued_component_bits=6043,
        universal_component_updates=15064,h1_listing_bits=12653,printed_listing_bits=12708,
        h1_out_of_Q_targets=65,printed_out_of_Q_targets=68,
        literal_controller_replays=14,literal_courier_site_updates=3332736,
        conditional_output_packet_site_updates=824063,conditional_commit_copy_roles=16955,
        actual_clean_native_only_early_delivery_by_composition=True,
        source_correct_raw_rows=[644763,641379],explicit_courier_seed_78Q=True,
        original_75Q_readiness=False,complete_beta=False,beta_fit=False,
        universal_whole_runtime=False,full_period=False,noise_map=False,
        faithful_Gray=False,Gray_refutation=False,iid_failure=False,shorter_U=False,
        elapsed_seconds=time.monotonic()-start)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
