"""Read-only provenance and complete NEW GBC3 result replay.

Accepted GBC2 mathematical receipts are only hash-checked, not rerun.
All new GBC3 listings, primitive cofactors, selected raw branches and
dense exact cutoff are recomputed and compared without timing values.
No registered source/receipt is mutated by this validator.
"""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from hashlib import sha256
from pathlib import Path
import argparse,importlib,json,subprocess,sys,tempfile,time

ROOT=Path(__file__).resolve().parents[4]
S=Path(__file__).resolve().parent
D=ROOT/'figs/gray_counterexamples/unregistered_gbc3'
sys.path.insert(0,str(S))


def digest(p):return sha256(p.read_bytes()).hexdigest()


def normalized(x):
    if isinstance(x,dict):return {k:normalized(v) for k,v in x.items() if k!='elapsed_seconds'}
    if isinstance(x,list):return [normalized(v) for v in x]
    return x


def run(output):
    t0=time.monotonic();mp=D/'GBC3_manifest.json';m=json.loads(mp.read_text())
    before={rel:digest(ROOT/rel) for rel in m['assets']}
    assert before==m['assets'],'frozen checkpoint source/receipt mismatch'
    assert m['Q']==8192 and m['U']==1048576 and m['lambda']==24 and m['c']==104
    for flag in ('complete_emitted_equivalence_proved','whole_own_beta',
                 'universal_whole_deadline_proved','physical_period',
                 'gray_refutation','iid_failure','shorter_U_proved'):
        assert m[flag] is False,flag
    import complete_branch_emitter as full
    import compact_complete_emitter as compact
    import compact_completion_rule as b
    for module,name,bits,instructions,refs in (
        (full,'GBC3_complete_structural_attempt01.json',46155,3487,315),
        (compact,'GBC3_complete_tailmerge_attempt01.json',42394,3228,316)):
        actual=module.emit_complete_structural_listing();old=json.loads((D/name).read_text())
        assert normalized(json.loads(json.dumps(actual)))==normalized(old),name
        assert actual['programme_bits']==bits and actual['instructions']==instructions
        assert len(actual['invalid_references'])==refs and actual['Q_fit'] is False
        coverage=actual['structural_branch_coverage']
        assert coverage['raw_modes']==list(range(8))
        assert coverage['ext_opcodes']==['SELF','ALUI','PUSH','FILL','PUTWORD']
        assert coverage['pending_wordout'] and coverage['packed_descriptor_errors']
    jobs=[('check_wordout_contract.py',[], 'GBC3_wordout_contract_attempt01.json'),
          ('check_complete_listing_diagnostic.py',['--cases','one'],'GBC3_complete_diagnostic_attempt01.json'),
          ('check_complete_listing_diagnostic.py',['--cases','run'],'GBC3_complete_run_diagnostic_attempt01.json'),
          ('check_complete_listing_diagnostic.py',['--cases','stages'],'GBC3_complete_stage_diagnostic_attempt01.json'),
          ('check_complete_listing_extended.py',[], 'GBC3_complete_extended_attempt01.json'),
          ('check_wordout_listing.py',[], 'GBC3_wordout_listing_attempt01.json'),
          ('check_complete_deadline_diagnostic.py',[], 'GBC3_complete_deadline_diagnostic_attempt01.json')]
    results=[]
    with tempfile.TemporaryDirectory(prefix='GBC3_readonly_') as td:
        def replay(job):
            script,args,expected=job;new=Path(td)/expected
            log=subprocess.run([sys.executable,str(S/script),*args,'--output',str(new)],
                               cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
            assert log.returncode==0,(script,log.stdout[-5000:])
            actual=json.loads(new.read_text());old=json.loads((D/expected).read_text())
            assert actual['passed'] and normalized(actual)==normalized(old),expected
            return {'receipt':expected,'source':script,'matched':True,
                    'accepted_sha256':digest(D/expected),'new_terminal_exit':log.returncode}
        with ThreadPoolExecutor(max_workers=3) as pool:
            results=list(pool.map(replay,jobs))
    primitive=json.loads((D/'GBC3_wordout_contract_attempt01.json').read_text())
    assert primitive['counts']=={'encode_decode':64,'pending':4270,'entry':2511,'physical_holder':1792}
    sizes=[]
    for f,n in (('stage',14),('run',27),('extended',52),('wordout',22)):
        p={'stage':'GBC3_complete_stage_diagnostic_attempt01.json',
           'run':'GBC3_complete_run_diagnostic_attempt01.json',
           'extended':'GBC3_complete_extended_attempt01.json',
           'wordout':'GBC3_wordout_listing_attempt01.json'}[f]
        r=json.loads((D/p).read_text());assert len(r['cases'])==n and all(x['passed'] for x in r['cases'])
        sizes.append({'family':f,'cases':n})
    cut=json.loads((D/'GBC3_complete_deadline_diagnostic_attempt01.json').read_text())
    assert cut['full_completion_updates']==94394 and cut['cutoff']['updates']==65534
    assert cut['cutoff']['wrong_raw_bits']==[355,356,365,366,375,376,380,381]
    assert not cut['final_wrong_raw_bits'] and cut['cutoff']['written_columns']==3087
    actual=b.unpack_cell(sum(int(v)<<i for i,v in enumerate(cut['cutoff']['actual_bits'])))
    desired=b.unpack_cell(sum(int(v)<<i for i,v in enumerate(cut['cutoff']['desired_bits'])))
    assert [b.unpack(z).pc for z in actual.head]==[42,42,42,31,31]
    assert [b.unpack(z).pc for z in desired.head]==[42]*5
    for f,_ in (*b.NATIVE,*b.FIELDS):
        if f!='head':assert getattr(actual,f)==getattr(desired,f),f
    for a,z in zip(actual.head,desired.head):
        ah,zh=asdict(b.unpack(a)),asdict(b.unpack(z))
        assert {k:v for k,v in ah.items() if k!='pc'}=={k:v for k,v in zh.items() if k!='pc'}
    after={rel:digest(ROOT/rel) for rel in m['assets']};assert after==before
    out={'passed':True,'assets':len(before),'hashes_unchanged':True,
         'manifest_sha256':digest(mp),'primitive_contract_checked':True,
         'complete_listing_rebuilt':True,'replayed_new_results':results,
         'selected_case_counts':sizes,'selected_cases':115,
         'selected_completion_updates':94394,'selected_cutoff_wrong_raw_count':8,
         'Q':8192,'U':1048576,'lambda':24,'c':104,
         'complete_emitter_equivalence_proved':False,'whole_own_beta':False,
         'physical_period':False,'gray_refutation':False,'iid_failure':False,
         'shorter_U_proved':False,'elapsed_seconds':time.monotonic()-t0}
    output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    run(p.parse_args().output)
