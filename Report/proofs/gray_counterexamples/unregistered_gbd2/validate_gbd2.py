"""Read-only exact GBD2 recomputation with accepted old provenance pinned."""
import argparse,hashlib,json,os,subprocess,sys,tempfile,time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
MANIFEST=ROOT/'figs/gray_counterexamples/unregistered_gbd2/GBD2_manifest.json'

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
    # Historical attempt01 preceded the added literal merge trace.  Its
    # own source snapshot, rather than the later checker, reproduces its pin.
    oldr=json.loads((ROOT/'figs/gray_counterexamples/unregistered_gbd2/GBD2_certificate_attempt01.json').read_text())
    assert oldr['passed']
    oldcheck='Report/proofs/gray_counterexamples/unregistered_gbd2/check_packing.py'
    snapshot=ROOT/'figs/gray_counterexamples/unregistered_gbd2/GBD2_check_packing_attempt01_source.py'
    assert sha(snapshot)==oldr['source_hashes'][oldcheck]
    with tempfile.TemporaryDirectory(prefix='gbd2_replay_') as d:
        out=Path(d)/'receipt.json'
        run=subprocess.run([sys.executable,str(HERE/'check_packing.py'),'--output',str(out)],
            cwd=ROOT,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'),
            stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        assert run.returncode==0,run.stderr
        r=json.loads(out.read_text());accepted=json.loads((ROOT/m['receipt']).read_text())
        assert r==accepted,'new receipt differs'
    check(m['assets'])
    for flag in ('controller_native_composition_proved','actual_autonomous_gathers_supplied',
                 'own_software_emitted','beta_fit','full_rule','full_execution_deadline',
                 'physical_period','faithful_Gray','Gray_refutation','iid_failure','shorter_U'):
        assert r[flag] is False
    assert r['conditional_quiet_coherent_packing']
    result=dict(passed=True,assets=len(m['assets']),hashes_unchanged=True,
        manifest_sha256=sha(MANIFEST),receipt_sha256=sha(ROOT/m['receipt']),
        all_new_claims_recomputed=True,inherited_provenance_only=True,
        symbolic_merge_identities=r['symbolic_merge_source_set_identities'],
        literal_seed_updates=r['literal_seed_updates'],
        literal_merge_updates=r['literal_merge_updates'],
        literal_chunk_load_updates=r['literal_chunk_load_updates'],
        transport_rows=r['complete_transport_rows'],
        transport_site_updates=r['transport_site_updates'],
        raw_slot_identities=r['raw_source_slot_identities'],
        raw_output_copy_checks=r['raw_output_copy_checks'],
        done_age=r['done_age'],block_radius=r['block_radius'],
        conditional_quiet_coherent_packing=True,
        native_ports_are_explicit_premise=True,
        autonomous_gathers=False,full_rule=False,own_beta=False,
        universal_full_execution_runtime=False,physical_period=False,
        faithful_Gray=False,gray_refutation=False,iid_failure=False,shorter_U=False,
        elapsed_seconds=time.monotonic()-start)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
