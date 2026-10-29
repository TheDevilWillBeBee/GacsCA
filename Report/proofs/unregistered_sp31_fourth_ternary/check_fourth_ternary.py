#!/usr/bin/env python3
"""Read-only replay by default; --issue freezes the new analysis receipt."""
from pathlib import Path
import argparse,ctypes,hashlib,json,random,subprocess,tempfile,time

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
OUT=ROOT/'figs/robustness/unregistered_sp31_fourth_ternary'
SOURCE=HERE/'sp31_fourth_ternary.c'
EXACT=ROOT/'Report/proofs/sp31_two_flag2_sources.c'
CERT=OUT/'ternary_enclosure_certificate.json'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rows(p):return [json.loads(s) for s in Path(p).read_text().splitlines()]
def compile_to(source,target,shared=False):
    args=['gcc','-O3','-std=c11','-Wall','-Wextra']
    if shared:args+=['-shared','-fPIC']
    run=subprocess.run([*args,str(source),'-o',str(target)],capture_output=True,text=True)
    assert run.returncode==0,(run.returncode,run.stdout,run.stderr)
    assert not run.stdout and not run.stderr,(run.stdout,run.stderr)

def cofactors(tmp):
    abstract=tmp/'abstract.so';exact=tmp/'exact.so'
    compile_to(SOURCE,abstract,True);compile_to(EXACT,exact,True)
    A=ctypes.CDLL(str(abstract)).sp31_fourth_ternary_cofactor
    E=ctypes.CDLL(str(exact)).sp31_two_sources_cofactor
    A.argtypes=[ctypes.POINTER(ctypes.c_uint16),ctypes.POINTER(ctypes.c_uint8),ctypes.c_int,ctypes.c_int]
    E.argtypes=[ctypes.POINTER(ctypes.c_uint8),ctypes.POINTER(ctypes.c_uint8),ctypes.c_int,ctypes.c_int]
    A.restype=E.restype=ctypes.c_uint
    rng=random.Random(2481024);exact_checks=0;inclusion_checks=0
    trace=hashlib.sha256()
    def eval_exact(n,inf,p,t):
        z=E((ctypes.c_uint8*81)(*n),(ctypes.c_uint8*81)(*inf),p,t)
        native=[(z>>j)&1 for j in range(5)]
        native.append(int(not(native[1] and native[0]!=((z>>5)&1))))
        return native
    for p in range(1024):
        t=(0,2047,2048,6143)[p%4]
        n=[rng.randrange(32) for _ in range(81)];inf=[rng.randrange(2) for _ in range(81)]
        packed=[sum(((v>>j)&1)<<(2*j) for j in range(5)) for v in n]
        z=A((ctypes.c_uint16*81)(*packed),(ctypes.c_uint8*81)(*inf),p,t)
        actual=eval_exact(n,inf,p,t);domains=[(z>>(2*j))&3 for j in range(6)]
        assert domains==actual,(p,t,domains,actual)
        trace.update(json.dumps([p,t,domains],separators=(',',':')).encode());exact_checks+=1
    for case in range(128):
        p=rng.randrange(1024);t=(0,2047,2048,6143)[case%4]
        n=[[rng.randrange(3) for _ in range(5)] for _ in range(81)]
        inf=[rng.randrange(3) for _ in range(81)]
        packed=[sum(v<<(2*j) for j,v in enumerate(row)) for row in n]
        z=A((ctypes.c_uint16*81)(*packed),(ctypes.c_uint8*81)(*inf),p,t)
        domains=[(z>>(2*j))&3 for j in range(6)]
        assert all(d<=2 for d in domains)
        for sample in range(8):
            cn=[sum((rng.randrange(2) if v==2 else v)<<j for j,v in enumerate(row)) for row in n]
            ci=[rng.randrange(2) if v==2 else v for v in inf]
            actual=eval_exact(cn,ci,p,t)
            assert all(d==2 or d==v for d,v in zip(domains,actual)),(case,sample,p,t,domains,actual)
            trace.update(json.dumps([case,sample,p,t,domains,actual],separators=(',',':')).encode());inclusion_checks+=1
    return dict(exact_all_phase_checks=exact_checks,selected_ternary_realization_checks=inclusion_checks,
                deterministic_trace_sha256=trace.hexdigest(),checks_are_measured_supplements=True)

def trajectory_summary(records):
    r=[x for x in records if 'native_possible_ones' in x]
    assert [x['row'] for x in r]==list(range(len(r)))
    assert all(x['border_violations']==0 for x in r)
    return dict(rows=len(r),endpoint=r[-1],minimum_possible_GF_left=min(x['GF_possible_left'] for x in r),
                maximum_possible_GF_right=max(x['GF_possible_right_exclusive'] for x in r),
                first_unknown_GF_row=next(x['row'] for x in r if x['native_unknown'][0]),all_exterior_guards_zero=True,
                max_native_possible_ones=[max(x['native_possible_ones'][j] for x in r) for j in range(5)])

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--issue',action='store_true');args=parser.parse_args()
    start=time.monotonic()
    if args.issue:assert not CERT.exists(),'Already frozen; use read-only default.'
    else:
        frozen=json.loads(CERT.read_text())
        for path,h in frozen['assets_sha256'].items():assert sha(ROOT/path)==h,path
    with tempfile.TemporaryDirectory(prefix='sp31_ternary_') as d:
        tmp=Path(d);binary=tmp/'ternary';compile_to(SOURCE,binary)
        cofactor_result=cofactors(tmp)
        results={}
        for name,ticks,stop in [('pulse',6144,0),('fixed',196735,1)]:
            output=tmp/(name+'.jsonl');state=tmp/(name+'.bin')
            with output.open('w') as fh:
                run=subprocess.run([str(binary),str(state),str(ticks),str(stop)],stdout=fh,stderr=subprocess.PIPE,text=True)
            assert run.returncode==0 and not run.stderr,(name,run.returncode,run.stderr)
            oldlog=OUT/('trajectory.jsonl' if name=='pulse' else 'fixed_point_trajectory.jsonl')
            oldstate=OUT/('terminal_domains.bin' if name=='pulse' else 'fixed_point_domains.bin')
            assert output.read_bytes()==oldlog.read_bytes(),name
            assert state.read_bytes()==oldstate.read_bytes(),name
            result=trajectory_summary(rows(output));result['terminal_marker']=rows(output)[-1]
            results[name]=result
        fixed=results['fixed']['terminal_marker']
        assert fixed['native_abstract_fixed_point'] and fixed['row']>=2049
    dependencies=[SOURCE,EXACT,Path(__file__),ROOT/'Report/proofs/SP31_FIRST_PULSE.md',
                  ROOT/'Report/proofs/SP31_FOURTH_SOURCE_ENCLOSURE.md',
                  ROOT/'figs/robustness/SP31_fourth_source_enclosure_certificate.json']
    assets={str(p.relative_to(ROOT)):sha(p) for p in [*dependencies,*sorted(OUT.iterdir())]
            if p.is_file() and p.name not in ('ternary_enclosure_certificate.json','issue_run.log','readonly_run.log')}
    cert=dict(passed=True,Q=1024,U=475136,TF=278401,radius=37,free_initial_votes=21,enclosure_members=1<<21,
        domain_encoding={'0':[0],'1':[1],'2':[0,1]},native_order=['GF','F1','WF1','F2','WF2'],
        source_sha256=sha(SOURCE),checker_sha256=sha(__file__),exact_factor_sha256=sha(EXACT),
        actual_fourth_source_enclosure_used=True,ternary_soundness_by_powerset_induction=True,
        native_only_quiet_extension_uses_guard_and_fixed_point=True,
        actual_full_fourth_boundary_or_upper_successor_or_repair_proved=False,
        full_Info_or_interpreter_or_higher_or_iid_reliability_proved=False,
        smallest_sufficient_change_proved=False,active_G17_or_isolated_F31_rule_modified=False,
        Gray_counterexample=False,global_reliability_established=False,
        cofactor_checks=cofactor_result,results=results,assets_sha256=assets)
    if args.issue:CERT.write_text(json.dumps(cert,indent=2)+'\n')
    else:assert cert==frozen,'Read-only replay changed the frozen mathematical result.'
    print(json.dumps(dict(passed=True,readonly=not args.issue,certificate_sha256=sha(CERT),
        pulse_rows=results['pulse']['rows'],fixed_point_row=fixed['row'],cofactor_checks=cofactor_result,
        actual_full_fourth_boundary_or_repair_proved=False,global_reliability_established=False,
        seconds=time.monotonic()-start)),flush=True)
if __name__=='__main__':main()
