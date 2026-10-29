"""Read-only replay of all new GBC4 mathematical receipts.

Every frozen hash is checked before/after. Prior GBC3 receipts are
provenance dependencies only; all NEW GBC4 listings/control/access/
complete selected diagnostics are rebuilt and compared exactly.
"""
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
from pathlib import Path
import argparse,json,subprocess,sys,tempfile,time
ROOT=Path(__file__).resolve().parents[4];S=Path(__file__).resolve().parent
D=ROOT/'figs/gray_counterexamples/unregistered_gbc4';sys.path.insert(0,str(S))
def digest(p):return sha256(p.read_bytes()).hexdigest()
def normalize(x):
    if isinstance(x,dict):return {k:normalize(v) for k,v in x.items() if k!='elapsed_seconds'}
    if isinstance(x,list):return [normalize(v) for v in x]
    return x
def run(output):
    t0=time.monotonic();mp=D/'GBC4_manifest.json';m=json.loads(mp.read_text())
    before={rel:digest(ROOT/rel) for rel in m['assets']};assert before==m['assets']
    assert (m['Q'],m['U'],m['lambda'],m['c'])==(8192,1048576,24,104)
    for flag in ('whole_own_beta','universal_emitter_equivalence_proved',
                 'universal_full_runtime_proved','physical_period','gray_refutation',
                 'iid_failure','shorter_U_proved'):assert m[flag] is False,flag
    import complete_branch_emitter as full
    import shared_control_emitter as shared
    for module,name,bits,n,refs in ((full,'GBC4_complete_structural_attempt01.json',46407,3447,365),
                                   (shared,'GBC4_complete_shared_control_attempt01.json',41047,3071,365)):
        r=module.emit_complete_structural_listing();old=json.loads((D/name).read_text())
        assert normalize(json.loads(json.dumps(r)))==normalize(old),name
        assert r['programme_bits']==bits and r['instructions']==n and len(r['invalid_references'])==refs
        c=r['structural_branch_coverage'];assert c['raw_modes']==list(range(8))
        assert c['ext_opcodes']==['SELF','ALUI','PUSH','FILL','PUTWORD','CALL','RETURN']
        assert c['raw_call_and_return_words'] and c['final_computed_source_native_wipe'] and not r['Q_fit']
    assert shared.emit_complete_structural_listing()['shared_control_accounting']['header_blocks_merged']==19
    jobs=[('check_control_access_contract.py',[],'GBC4_control_access_contract_attempt02.json'),
          ('check_complete_listing_diagnostic.py',['--cases','run'],'GBC4_complete_run_diagnostic_attempt01.json'),
          ('check_complete_listing_extended.py',[],'GBC4_complete_extended_attempt01.json'),
          ('check_wordout_listing.py',[],'GBC4_wordout_listing_attempt01.json'),
          ('check_shared_control_listing.py',[],'GBC4_shared_control_diagnostic_attempt01.json')]
    with tempfile.TemporaryDirectory(prefix='GBC4_readonly_') as td:
        def replay(job):
            script,args,name=job;out=Path(td)/name
            r=subprocess.run([sys.executable,str(S/script),*args,'--output',str(out)],cwd=ROOT,
                             stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
            assert r.returncode==0,(script,r.stdout[-6000:])
            actual=json.loads(out.read_text());old=json.loads((D/name).read_text())
            assert actual['passed'] and normalize(actual)==normalize(old),name
            return {'receipt':name,'accepted_sha256':digest(D/name),'terminal_exit':r.returncode,'matched':True}
        with ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(replay,jobs))
    co=json.loads((D/'GBC4_control_access_contract_attempt02.json').read_text())
    assert co['counts']=={'call':36,'return':40,'issued_helper':75}
    assert len(co['helper_cases'])==75 and max(x['component_bits'] for x in co['helper_cases'])==287
    assert max(x['updates'] for x in co['helper_cases'])==3109
    for name,n in (('GBC4_complete_run_diagnostic_attempt01.json',29),
                   ('GBC4_complete_extended_attempt01.json',52),
                   ('GBC4_wordout_listing_attempt01.json',22),
                   ('GBC4_shared_control_diagnostic_attempt01.json',104)):
        r=json.loads((D/name).read_text());assert len(r['cases'])==n and all(x['passed'] for x in r['cases'])
    failure=json.loads((D/'GBC4_truncated_fetch_checker_failure_record.json').read_text())
    assert failure['terminal_exit']==1 and failure['failed_source_sha256']==digest(S/'check_control_access_contract_truncated_fetch_failure.py')
    after={rel:digest(ROOT/rel) for rel in m['assets']};assert after==before
    result={'passed':True,'assets':len(before),'hashes_unchanged':True,'manifest_sha256':digest(mp),
            'new_replays':results,'component_cases':75,'control_fetch_cofactors':76,
            'selected_complete_diagnostics':207,'Q':8192,'U':1048576,'lambda':24,'c':104,
            'whole_own_beta':False,'universal_emitter_equivalence':False,
            'universal_full_runtime':False,'physical_period':False,'gray_refutation':False,
            'iid_failure':False,'shorter_U_proved':False,'elapsed_seconds':time.monotonic()-t0}
    output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    run(p.parse_args().output)
