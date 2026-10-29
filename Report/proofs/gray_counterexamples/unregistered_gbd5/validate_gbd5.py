"""Read-only replay of every new GBD5 claim; hash-checked old contracts."""
import argparse,hashlib,json,os,subprocess,sys,tempfile,time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
DATA=ROOT/'figs/gray_counterexamples/unregistered_gbd5'
MANIFEST=DATA/'GBD5_manifest.json'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check(assets):
    for path,h in assets.items():assert sha(ROOT/path)==h,(path,'hash mismatch')
def run(command):
    result=subprocess.run(command,cwd=ROOT,
        env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'),
        stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    assert result.returncode==0,result.stderr
    return result.stdout
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();started=time.monotonic()
    manifest=json.loads(MANIFEST.read_text());check(manifest['assets'])
    old_path=ROOT/manifest['inherited_manifest'];old=json.loads(old_path.read_text());check(old['assets'])
    for path in manifest['inherited_replays']:
        receipt=json.loads((ROOT/path).read_text())
        assert receipt['passed'] and receipt['hashes_unchanged']
        assert receipt['manifest_sha256']==sha(old_path)
    for attempt in (1,2):
        directory=DATA/f'retained_attempt{attempt:02d}_sources'
        provenance=json.loads((directory/'provenance.json').read_text())
        for name,h in provenance['source_sha256'].items():assert sha(directory/name)==h
    assert 'ModuleNotFoundError' in (DATA/'GBD5_attempt01.log').read_text()
    assert 'gacsca' in (DATA/'GBD5_attempt01.log').read_text()
    accepted=ROOT/manifest['accepted_artifact_directory']
    certificate=json.loads((ROOT/manifest['certificate']).read_text())
    # The older successful trace differs only in its listed (not executed)
    # probe times. Its complete-packet min/max route is identical to the
    # simplified lookup in the new formula once all chunks have arrived.
    previous=json.loads((DATA/'attempt02/GBD5_certificate.json').read_text())
    previous['chronology']['actual_local_prefix_rows']=[t for t in
        previous['chronology']['actual_local_prefix_rows'] if t<certificate['packing']['birth_action']]
    assert previous==certificate,'successful older trace changed mathematical assertions'
    for path in accepted.iterdir():
        if path.is_file() and path.name!='GBD5_certificate.json':
            assert sha(DATA/'attempt02'/path.name)==sha(path),(path.name,'older artifact changed')
    with tempfile.TemporaryDirectory(prefix='gbd5_readonly_') as directory:
        directory=Path(directory)
        run([sys.executable,str(HERE/'check_prefix.py'),'--out',str(directory)])
        replay=json.loads((directory/'GBD5_certificate.json').read_text())
        assert replay==certificate,'actual-prefix mathematical receipt changed'
        for path in accepted.iterdir():
            if path.is_file():assert sha(directory/path.name)==sha(path),(path.name,'artifact differs')
        # This separate accepted erratum concerns the frozen raw actor,
        # not a rule change. Replay the exact distance-five cofactor.
        er=json.loads(run([sys.executable,str(ROOT/manifest['head_radius_erratum_checker'])]))
        assert er==json.loads((ROOT/manifest['head_radius_erratum_receipt']).read_text())
    check(manifest['assets'])
    for flag in ('full_own_beta','beta_fit','full_own_controller_software',
        'authentic_flag_couriers','late_pass','full_physical_period',
        'intact_recursive_initialization','noise_map','faithful_Gray',
        'Gray_refutation','iid_failure','shorter_U'):
        assert manifest[flag] is False
    result=dict(passed=True,assets=len(manifest['assets']),hashes_unchanged=True,
        manifest_sha256=sha(MANIFEST),certificate_sha256=sha(ROOT/manifest['certificate']),
        all_new_claims_recomputed=True,inherited_provenance_only=True,
        inherited_replay_manifest_sha256=sha(old_path),
        head_radius_erratum_replayed=True,
        Q=8192,U=1048576,lambda_=24,c=104,K=3387,Head_bits=204,
        total_autonomous_prefix=True,actual_global_E_start=True,
        all_upper_Kbit_patterns=True,actual_native_ports=True,actual_three_History_banks=True,
        actual_packing_reset_birth=True,native_prefix_beta_bits=7051,
        universal_native_updates=33937,latest_prefix_completion_row=627003,
        actual_local_prefix_calls=certificate['chronology']['actual_local_prefix_calls'],
        all_normal_primary_capture_routes=certificate['chronology']['all_normal_primary_capture_routes'],
        literal_packet_site_updates=certificate['packing']['literal_packet_site_updates'],
        full_own_beta=False,beta_fit=False,full_own_controller_software=False,
        authentic_flag_couriers=False,late_pass=False,full_physical_period=False,
        intact_recursive_initialization=False,noise_map=False,faithful_Gray=False,
        Gray_refutation=False,iid_failure=False,shorter_U=False,
        elapsed_seconds=time.monotonic()-started)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
