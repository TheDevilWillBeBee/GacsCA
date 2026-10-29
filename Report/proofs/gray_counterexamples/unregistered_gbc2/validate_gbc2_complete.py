"""Read-only full new-work replay ofGBC2 complete-encoder evidence."""
from pathlib import Path
from hashlib import sha256
from concurrent.futures import ThreadPoolExecutor,as_completed
import argparse,json,subprocess,sys,tempfile,time

ROOT=Path(__file__).resolve().parents[4]
S=ROOT/'Report/proofs/gray_counterexamples/unregistered_gbc2'
D=ROOT/'figs/gray_counterexamples/unregistered_gbc2'

def stable(z):
    if isinstance(z,dict):return {k:stable(v) for k,v in z.items() if k!='elapsed_seconds'}
    if isinstance(z,list):return list(map(stable,z))
    return z

def run(output):
    t0=time.monotonic();manifest=D/'GBC2_complete_manifest.json'
    m=json.loads(manifest.read_text());before={}
    for name,digest in m['assets'].items():
        p=ROOT/name;now=sha256(p.read_bytes()).hexdigest();assert now==digest,name
        before[name]=now
    assert m['scope']['physical_period'] is False
    assert m['scope']['whole_own_beta'] is False
    assert m['scope']['universal_complete_equivalence'] is False
    assert m['scope']['universal_deadline'] is False
    sys.path.insert(0,str(S))
    import complete_branch_emitter as first
    import compact_complete_emitter as merged
    import compact_completion_rule as b
    checks=[]
    for module,receipt,size,refs in (
      (first,'GBC2_complete_structural_attempt01.json',48705,383),
      (merged,'GBC2_complete_tailmerge_attempt01.json',42727,350)):
        actual=module.emit_complete_structural_listing()
        old=json.loads((D/receipt).read_text())
        assert stable(json.loads(json.dumps(actual)))==stable(old),receipt
        assert actual['programme_bits']==size and len(actual['invalid_references'])==refs
        assert len(actual['listing'])==(3645 if module is first else 3229)
        assert sum(x[3] for x in actual['listing'])==size
        assert not actual['Q_fit'] and not actual['whole_own_beta']
        assert actual['structural_branch_coverage']['main_opcodes']==list(b.OP_NAMES)
        assert actual['structural_branch_coverage']['raw_modes']==list(range(8))
        assert all(name in actual['labels'] for name in
                   ('cpu_run','cpu_io','cpu_span','cpu_stream','cpu_fail',
                    'cpu_native','cpu_push','cpu_wget','cpu_wset','cpu_self',
                    'head_collect','head_collect_move','head_birth',
                    'courier_evaluate','final_source_loaded','whole_halt'))
        for pc,name,args,_ in actual['listing']:
            if name=='BR':
                bad=not 0<=args[1]<b.Q
                assert bad==any(x[0]==pc for x in actual['invalid_references'])
                assert args[1] in actual['labels'].values()
        checks.append({'name':receipt,'bits':size,'out_of_Q_references':refs,'exact_listing_equal':True})
    jobs=[('check_completion_build.py',[], 'GBC2_build_checks02.json'),
          ('check_early_stage_emission.py',[],'GBC2_early_stage_checks01.json'),
          ('check_complete_listing_diagnostic.py',['--cases','one'],'GBC2_complete_diagnostic_attempt01.json'),
          ('check_complete_listing_diagnostic.py',['--cases','stages'],'GBC2_complete_stage_diagnostic_attempt01.json'),
          ('check_complete_listing_diagnostic.py',['--cases','run'],'GBC2_complete_run_diagnostic_attempt01.json'),
          ('check_complete_listing_extended.py',[],'GBC2_complete_extended_attempt01.json'),
          ('check_complete_deadline_diagnostic.py',[],'GBC2_complete_deadline_diagnostic_attempt01.json')]
    with tempfile.TemporaryDirectory(prefix='GBC2-readonly-') as tmp:
        def replay(job):
            script,args,expected=job;p=Path(tmp)/expected
            rr=subprocess.run([sys.executable,str(S/script),*args,'--output',str(p)],
                              cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            assert rr.returncode==0,(script,args,rr.returncode,rr.stdout[-2000:],rr.stderr[-2000:])
            actual=json.loads(p.read_text());prior=json.loads((D/expected).read_text())
            assert stable(actual)==stable(prior),(script,expected)
            assert actual['passed'] is True
            return {'name':expected,'exact_replay_equal':True,
                    'cases':len(actual.get('cases',[]))}
        with ThreadPoolExecutor(max_workers=3) as pool:
            futures=[pool.submit(replay,j) for j in jobs]
            for f in as_completed(futures):
                c=f.result();checks.append(c);print(json.dumps(c),flush=True)
    cutoff=json.loads((D/'GBC2_complete_deadline_diagnostic_attempt01.json').read_text())
    a=b.unpack_cell(sum(int(v)<<i for i,v in enumerate(cutoff['cutoff']['actual_bits'])))
    z=b.unpack_cell(sum(int(v)<<i for i,v in enumerate(cutoff['cutoff']['desired_bits'])))
    assert [b.unpack(x).pc for x in a.head]==[42,42,31,31,31]
    assert [b.unpack(x).pc for x in z.head]==[42]*5
    assert all(getattr(a,f)==getattr(z,f) for f,_ in b.NATIVE+b.FIELDS if f!='head')
    assert len(cutoff['cutoff']['wrong_raw_bits'])==12
    assert cutoff['full_completion_updates']==126614
    assert cutoff['cutoff']['updates']==65534 and cutoff['final_wrong_raw_bits']==[]
    after={name:sha256((ROOT/name).read_bytes()).hexdigest() for name in before}
    assert after==before
    result={'passed':True,'assets':len(before),'manifest_sha256':sha256(manifest.read_bytes()).hexdigest(),
            'before_hashes':before,'after_hashes':after,'checks':checks,
            'scope':m['scope'],'cutoff_field':'Head.pc only; Info agrees',
            'active_rule_unchanged':True,'main_Gray_report_unchanged':True,
            'global_reliability_established':False,'elapsed_seconds':time.monotonic()-t0}
    output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('before_hashes','after_hashes')},indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    run(p.parse_args().output)
