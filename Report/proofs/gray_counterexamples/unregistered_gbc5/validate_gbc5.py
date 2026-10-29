"""Read-only exact replay of every new GBC5 mathematical certificate."""
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
from pathlib import Path
import argparse,json,subprocess,sys,tempfile,time
ROOT=Path(__file__).resolve().parents[4];S=Path(__file__).resolve().parent
D=ROOT/'figs/gray_counterexamples/unregistered_gbc5';sys.path.insert(0,str(S))
def digest(p):return sha256(p.read_bytes()).hexdigest()
def normalize(x):
    if isinstance(x,dict):return {k:normalize(v) for k,v in x.items() if k!='elapsed_seconds'}
    if isinstance(x,list):return [normalize(v) for v in x]
    return x
def run(output):
    t0=time.monotonic();mp=D/'GBC5_manifest.json';m=json.loads(mp.read_text())
    before={rel:digest(ROOT/rel) for rel in m['assets']};assert before==m['assets']
    assert (m['Q'],m['U'],m['lambda'],m['c'])==(8192,1048576,24,104)
    for flag in ('whole_own_beta','universal_emitter_equivalence','universal_full_runtime',
                 'physical_period','gray_refutation','iid_failure','shorter_U_proved'):
        assert m[flag] is False,flag
    import scratch_free_reader_emitter as new
    r=new.emit_complete_structural_listing()
    assert json.loads(json.dumps(r))==json.loads((D/'GBC5_complete_structural_attempt01.json').read_text())
    assert (r['programme_bits'],r['instructions'],len(r['invalid_references']))==(40778,3104,365)
    assert not r['Q_fit'] and r['reader_widths']==[1,2,3,4,5,6,13,15,20]
    jobs=[('check_scratch_free_reader.py','GBC5_scratch_free_reader_attempt03.json'),
          ('check_complete_scratch_free_listing.py','GBC5_complete_diagnostic_attempt01.json')]
    with tempfile.TemporaryDirectory(prefix='GBC5_readonly_') as td:
        def replay(job):
            script,name=job;out=Path(td)/name
            p=subprocess.run([sys.executable,str(S/script),'--output',str(out)],cwd=ROOT,
                             stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
            assert p.returncode==0,(script,p.stdout[-6000:])
            actual=json.loads(out.read_text());old=json.loads((D/name).read_text())
            assert actual['passed'] and normalize(actual)==normalize(old),name
            return {'receipt':name,'accepted_sha256':digest(D/name),'terminal_exit':0,'matched':True}
        with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(replay,jobs))
    co=json.loads((D/'GBC5_scratch_free_reader_attempt03.json').read_text())
    assert len(co['component_cases'])==810 and co['caller_audit']['caller_count']==43
    assert len(co['caller_audit']['calls'])==75 and co['caller_audit']['maximum_nested_calls']==2
    assert co['largest_issued_component_bits']==206 and co['universal_issued_component_bound']==3104
    assert co['largest_selected_component_updates']==3104
    diag=json.loads((D/'GBC5_complete_diagnostic_attempt01.json').read_text())
    assert len(diag['cases'])==104 and all(c['passed'] for c in diag['cases'])
    assert 'AssertionError' in (D/'GBC5_scratch_free_reader_attempt01.log').read_text()
    after={rel:digest(ROOT/rel) for rel in m['assets']};assert after==before
    out={'passed':True,'assets':len(before),'hashes_unchanged':True,'manifest_sha256':digest(mp),
         'new_replays':results,'issued_component_cases':810,'actual_reader_callers':43,
         'counted_CALL_sites':75,'maximum_nested_calls':2,'universal_component_deadline':3104,
         'selected_complete_comparisons':104,'Q':8192,'U':1048576,'lambda':24,'c':104,
         'unchanged_total_rule':True,'whole_own_beta':False,'universal_emitter_equivalence':False,
         'universal_full_runtime':False,'physical_period':False,'gray_refutation':False,
         'iid_failure':False,'shorter_U_proved':False,'elapsed_seconds':time.monotonic()-t0}
    output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    run(p.parse_args().output)
