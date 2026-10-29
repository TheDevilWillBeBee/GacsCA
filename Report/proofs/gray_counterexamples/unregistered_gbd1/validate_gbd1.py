"""Read-only recomputation of new GBD1, exact prior provenance retained."""
import argparse,hashlib,json,os,subprocess,sys,tempfile,time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
MANIFEST=ROOT/'figs/gray_counterexamples/unregistered_gbd1/GBD1_manifest.json'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def check(assets):
    for path,h in assets.items():assert sha(ROOT/path)==h,(path,'hash mismatch')

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();start=time.monotonic();m=json.loads(MANIFEST.read_text())
    check(m['assets']);old=ROOT/m['inherited_manifest']
    om=json.loads(old.read_text());check(om['assets'])
    orr=json.loads((ROOT/m['inherited_replay']).read_text())
    assert orr['passed'] and orr['hashes_unchanged'] and orr['manifest_sha256']==sha(old)
    with tempfile.TemporaryDirectory(prefix='gbd1_replay_') as d:
        out=Path(d)/'receipt.json'
        run=subprocess.run([sys.executable,str(HERE/'check_slots.py'),'--output',str(out)],
            cwd=ROOT,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'),
            stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        assert run.returncode==0,run.stderr
        r=json.loads(out.read_text());accepted=json.loads((ROOT/m['receipt']).read_text())
        assert r==accepted,'new receipt differs'
    check(m['assets'])
    for flag in ('full_rule','own_programme','actual_packing','runtime_bound',
                 'physical_period','noise_theorem','Gray_refutation','iid_failure','shorter_U'):
        assert r[flag] is False
    result=dict(passed=True,assets=len(m['assets']),hashes_unchanged=True,
        manifest_sha256=sha(MANIFEST),receipt_sha256=sha(ROOT/m['receipt']),
        all_new_claims_recomputed=True,inherited_provenance_only=True,
        source_port_identities=r['physical_slot_bit_identities'],
        inverse_slot=r['inverse_slot'],exact_stencil=r['exact_stencil'],
        corrected_raw_slot_reader=True,old_GBD0_physical_claim_incomplete=True,
        full_rule=False,own_beta=False,actual_packing=False,
        universal_runtime=False,physical_period=False,
        faithful_Gray=False,gray_refutation=False,iid_failure=False,shorter_U=False,
        elapsed_seconds=time.monotonic()-start)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
