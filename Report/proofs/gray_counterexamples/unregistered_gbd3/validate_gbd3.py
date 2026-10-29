"""Read-only GBD3 recomputation, immutable failed/successful source pins."""
import argparse,hashlib,json,os,subprocess,sys,tempfile,time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
DATA=ROOT/'figs/gray_counterexamples/unregistered_gbd3'
MANIFEST=DATA/'GBD3_manifest.json'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def check(assets):
    for path,h in assets.items():assert sha(ROOT/path)==h,(path,'hash mismatch')


def histories():
    # Successful historical source versions are retained exactly. They
    # are not represented as matches to the later extended source.
    for attempt in (1,2,5):
        old=json.loads((DATA/f'GBD3_certificate_attempt{attempt:02d}.json').read_text())
        assert old['passed']
        for path,h in old['source_hashes'].items():
            snap=DATA/(f'GBD3_attempt{attempt:02d}_source_'+Path(path).name)
            assert sha(snap)==h,(attempt,path,'retained old source')
    for attempt in (3,4):
        failed=json.loads((DATA/f'GBD3_failed_attempt{attempt:02d}_provenance.json').read_text())
        assert failed['passed'] is False and failed['process_exit']==1
        assert failed['rule_changed'] is False and failed['Gray_failure'] is False
        check(failed['source_and_log_hashes'])


def main():
    a=argparse.ArgumentParser();a.add_argument('--output',type=Path,required=True)
    args=a.parse_args();started=time.monotonic();m=json.loads(MANIFEST.read_text())
    check(m['assets']);histories()
    old=ROOT/m['inherited_manifest'];om=json.loads(old.read_text());check(om['assets'])
    for path in m['inherited_replays']:
        r=json.loads((ROOT/path).read_text())
        assert r['passed'] and r['hashes_unchanged'] and r['manifest_sha256']==sha(old)
    receipts={}
    with tempfile.TemporaryDirectory(prefix='gbd3_readonly_') as d:
        for name,script in (('controller','check_controller.py'),('packing','check_packing.py'),
                            ('binding','check_binding.py')):
            out=Path(d)/(name+'.json');cmd=[sys.executable,str(HERE/script),'--output',str(out)]
            if name=='controller':cmd+=['--witness-output',str(Path(d)/'radius.json')]
            run=subprocess.run(cmd,cwd=ROOT,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'),
                               stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
            assert run.returncode==0,(name,run.stderr)
            new=json.loads(out.read_text());accepted=json.loads((ROOT/m['receipts'][name]).read_text())
            assert new==accepted,(name,'new mathematical receipt differs')
            receipts[name]=new
            if name=='controller':
                assert sha(Path(d)/'radius.json')==sha(ROOT/m['radius_witness'])
    check(m['assets'])
    c,p,b=receipts['controller'],receipts['packing'],receipts['binding']
    assert c['shared_helpers_bits']==dict(FGET=140,FPUT=137,caller_with_both=396)
    assert c['actual_shared_helper_callers'][0]['contract']['updates']==155
    assert c['actual_shared_helper_callers'][5]['contract']['updates']==190
    assert c['generic_diagonal_field_access'] and c['captured_raw_records_not_prevoted']
    assert p['K']==3387 and p['chunks']==170 and p['complete_transport_rows']==3217
    assert p['done_age']==593064 and p['packed_by_before73Q']
    assert all(r['actual_reset_and_birth'] and r['packed_memory_from_literal_history']
               for r in b['actual_reset_birth_and_helper_runs'])
    for flag in ('full_rule','physical_period','faithful_Gray','Gray_refutation','iid_failure','shorter_U'):
        assert p[flag] is False and b[flag] is False
    for flag in ('complete_own_beta','beta_fit','full_rule','physical_period','noise_map',
                 'faithful_Gray','Gray_refutation','iid_failure','shorter_U'):
        assert m[flag] is False
    result=dict(passed=True,assets=len(m['assets']),hashes_unchanged=True,
        manifest_sha256=sha(MANIFEST),all_new_claims_recomputed=True,inherited_provenance_only=True,
        receipts_sha256={name:sha(ROOT/path) for name,path in m['receipts'].items()},
        Q=8192,U=1048576,lambda_=24,c=104,Head_bits=204,K=3387,twoK=6774,
        literal_controller_radius=7,one_sided16_alternative_radius=8,
        one_sided20_radius9_stipulated_obstruction=True,
        FGET_bits=140,FPUT_bits=137,caller_bits=396,
        actual_caller_updates=[r['contract']['updates'] for r in c['actual_shared_helper_callers']],
        fresh_packing_chunks=170,packing_transport_rows=3217,
        packing_merge_identities=p['symbolic_merge_source_set_identities'],
        literal_packing_site_updates=p['transport_site_updates'],
        actual_computed_port_reset_birth_binding=True,
        explicit_quiet_native_ports_and_two_good_History_premises=True,
        complete_own_beta=False,beta_fit=False,full_rule=False,physical_period=False,
        error_history=False,noise_map=False,faithful_Gray=False,Gray_refutation=False,
        iid_failure=False,shorter_U=False,elapsed_seconds=time.monotonic()-started)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))


if __name__=='__main__':main()
