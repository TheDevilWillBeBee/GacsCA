"""Read-only new GBC6 replay, with hash-checked accepted inheritance."""
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
from pathlib import Path
import argparse,json,subprocess,sys,tempfile,time
ROOT=Path(__file__).resolve().parents[4];S=Path(__file__).resolve().parent
D=ROOT/'figs/gray_counterexamples/unregistered_gbc6';sys.path.insert(0,str(S))
def digest(p):return sha256(p.read_bytes()).hexdigest()
def normalize(x):
    if isinstance(x,dict):return {k:normalize(v) for k,v in x.items() if k!='elapsed_seconds'}
    if isinstance(x,list):return [normalize(v) for v in x]
    return x
def run(output):
    start=time.monotonic();mp=D/'GBC6_manifest.json';m=json.loads(mp.read_text())
    before={rel:digest(ROOT/rel) for rel in m['assets']};assert before==m['assets']
    assert (m['Q'],m['U'],m['lambda'],m['c'])==(8192,1048576,24,104)
    for flag in ('whole_own_beta','universal_full_emitter','universal_full_runtime','physical_period',
                 'faithful_Gray','gray_refutation','iid_failure','shorter_U_proved'):assert m[flag] is False
    import register_control_emitter as emitter,register_branch_cost as cost
    unfolded=emitter.old.emit_complete_structural_listing();folded=emitter.emit_complete_structural_listing()
    for r,name in ((unfolded,'GBC6_complete_unfolded_attempt01.json'),
                   (folded,'GBC6_complete_register_attempt01.json')):
        assert json.loads(json.dumps(r))==json.loads((D/name).read_text()),name
    assert (unfolded['programme_bits'],unfolded['instructions'],len(unfolded['invalid_references']))==(42942,3272,385)
    assert (folded['programme_bits'],folded['instructions'],len(folded['invalid_references']))==(42716,3140,384)
    assert folded['register_accounting']['REG_blocks']==4 and folded['register_accounting']['REGI_blocks']==58
    bound=cost.bound(folded);assert bound==json.loads((D/'GBC6_register_branch_cost_attempt01.json').read_text())
    assert bound['maximum_uniform_updates']==58171 and bound['branches']['cpu_regi_entry']['uniform_updates']==41817
    old=ROOT/'figs/gray_counterexamples/unregistered_gbc5/GBC5_manifest.json'
    for name in ('GBC5_readonly_own_validation01.json','GBC5_parent_readonly_validation.json'):
        r=json.loads((old.parent/name).read_text())
        assert r['passed'] and r['hashes_unchanged'] and r['manifest_sha256']==digest(old)
        assert all(x['terminal_exit']==0 and x['matched'] for x in r['new_replays'])
    jobs=[('check_register_component.py','GBC6_register_component_attempt01.json'),
          ('check_register_reader.py','GBC6_register_reader_attempt01.json')]
    with tempfile.TemporaryDirectory(prefix='GBC6_readonly_') as td:
        def replay(job):
            script,name=job;out=Path(td)/name
            p=subprocess.run([sys.executable,str(S/script),'--output',str(out)],cwd=ROOT,
                             stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
            assert p.returncode==0,(script,p.stdout[-6000:])
            actual=json.loads(out.read_text());old=json.loads((D/name).read_text())
            assert actual['passed'] and normalize(actual)==normalize(old),name
            return {'receipt':name,'accepted_sha256':digest(D/name),'terminal_exit':0,'matched':True}
        with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(replay,jobs))
    c=json.loads((D/'GBC6_register_component_attempt01.json').read_text())
    reader=json.loads((D/'GBC6_register_reader_attempt01.json').read_text())
    assert c['opcode_cofactors']==116736 and len(c['selected_own_branch_cases'])==14
    assert len(reader['component_cases'])==480 and reader['caller_abi']['helper_work_writes']==[320,340]
    assert all(r['passed'] for r in c['selected_own_branch_cases'])
    after={rel:digest(ROOT/rel) for rel in m['assets']};assert after==before
    out={'passed':True,'assets':len(before),'hashes_unchanged':True,'manifest_sha256':digest(mp),
         'new_replays':results,'accepted_inheritance_hash_checked':True,
         'opcode_cofactors':116736,'issued_register_reader_cases':480,'selected_complete_comparisons':14,
         'complete_bits':42716,'instructions':3140,'out_of_Q_references':384,
         'conditional_branch_deadlines':m['conditional_branch_deadlines'],
         'Q':8192,'U':1048576,'lambda':24,'c':104,'rule_changed_REG_REGI':True,'state_bits_added':0,
         'raw_opcode_semantics_proved':True,'conditional_listed_own_branch_proved':True,
         'whole_own_beta':False,'universal_full_emitter':False,'universal_full_runtime':False,
         'physical_period':False,'faithful_Gray':False,'gray_refutation':False,
         'iid_failure':False,'shorter_U_proved':False,'elapsed_seconds':time.monotonic()-start}
    output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);run(p.parse_args().output)
