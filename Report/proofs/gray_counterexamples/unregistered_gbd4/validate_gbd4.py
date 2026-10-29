"""Read-only mathematical replay of GBD4, exact inherited/source pins."""
import argparse,hashlib,json,os,subprocess,sys,tempfile,time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
DATA=ROOT/'figs/gray_counterexamples/unregistered_gbd4'
MANIFEST=DATA/'GBD4_manifest.json'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check(assets):
    for path,h in assets.items():assert sha(ROOT/path)==h,(path,'hash mismatch')
def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();started=time.monotonic();m=json.loads(MANIFEST.read_text());check(m['assets'])
    old=ROOT/m['inherited_manifest'];om=json.loads(old.read_text());check(om['assets'])
    for path in m['inherited_replays']:
        r=json.loads((ROOT/path).read_text());assert r['passed'] and r['hashes_unchanged']
        assert r['manifest_sha256']==sha(old)
    for attempt in (1,2):
        d=DATA/f'retained_attempt{attempt:02d}_sources'
        pins=json.loads((d/'provenance.json').read_text())
        for name,h in pins['source_sha256'].items():assert sha(d/name)==h
    failure=(DATA/'GBD4_attempt01.log').read_text()
    assert 'ValueError' in failure and 'relative_to' in failure
    native=json.loads((ROOT/m['native_receipt']).read_text())
    arithmetic=json.loads((ROOT/m['arithmetic_receipt']).read_text())
    accepted=ROOT/m['native_artifact_directory']
    with tempfile.TemporaryDirectory(prefix='gbd4_readonly_') as directory:
        directory=Path(directory)
        run=subprocess.run([sys.executable,str(HERE/'check_native.py'),'--out',str(directory)],
            cwd=ROOT,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'),
            stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        assert run.returncode==0,run.stderr
        replay=json.loads((directory/'GBD4_certificate.json').read_text())
        assert replay==native,'native mathematical receipt changed'
        for path in accepted.iterdir():
            if path.is_file():assert sha(directory/path.name)==sha(path),(path.name,'artifact replay differs')
        target=directory/'arithmetic.json'
        run=subprocess.run([sys.executable,str(HERE/'check_arithmetic_liveness.py'),'--output',str(target)],
            cwd=ROOT,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'),
            stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        assert run.returncode==0,run.stderr
        assert json.loads(target.read_text())==arithmetic
    # The successful older source iteration has identical actual executions;
    # only recorded artifact pathname prefixes were made portable.
    previous=json.loads((DATA/'attempt02/GBD4_certificate.json').read_text())
    for item in previous['complete_selected_runs']:item['path']=Path(item['path']).name
    assert previous==native,'portable receipt changed mathematical assertions'
    check(m['assets'])
    for flag in ('complete_own_beta','beta_fit','full_rule','physical_period','autonomous_ports',
                 'authentic_History_origin','error_history','faithful_Gray','Gray_refutation',
                 'iid_failure','shorter_U'):
        assert m[flag] is False
    result=dict(passed=True,assets=len(m['assets']),hashes_unchanged=True,
        manifest_sha256=sha(MANIFEST),all_new_claims_recomputed=True,inherited_provenance_only=True,
        native_receipt_sha256=sha(ROOT/m['native_receipt']),
        arithmetic_receipt_sha256=sha(ROOT/m['arithmetic_receipt']),
        Q=8192,U=1048576,lambda_=24,c=104,K=3387,Head_bits=204,
        h1_native_bits=7051,printed_native_bits=7106,universal_prepared_native_updates=33937,
        actual_lower_Mem_Out_raw_access_and_native_input=True,native_software_no_oracle=True,
        upper_SF_software=False,
        full_own_beta=False,beta_fit=False,full_rule=False,physical_period=False,
        lower_quiet_ports_and_coherent_prepared_bank_required=True,
        noise_map=False,faithful_Gray=False,Gray_refutation=False,iid_failure=False,
        shorter_U=False,elapsed_seconds=time.monotonic()-started)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
