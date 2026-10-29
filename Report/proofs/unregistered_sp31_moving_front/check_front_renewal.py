#!/usr/bin/env python3
"""Freeze once with --issue; default replays all new evidence read-only."""
from pathlib import Path
import argparse,ctypes,hashlib,json,random,subprocess,sys,tempfile,time
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
OUT=ROOT/'figs/robustness/unregistered_sp31_moving_front'
CERT=OUT/'front_renewal_certificate.json';SOURCE=HERE/'sp31_moving_front_probe01.c'
PROOF=HERE/'SP31_CONDITIONAL_FRONT_RENEWAL.md'
EXACT=ROOT/'Report/proofs/sp31_two_flag2_sources.c'
PARENT_SOURCE=ROOT/'Report/proofs/unregistered_sp31_fourth_ternary/sp31_fourth_ternary.c'
PARENT_CERT=ROOT/'figs/robustness/unregistered_sp31_fourth_reset/fourth_reset_fifth_source_certificate.json'
sys.path.insert(0,str(HERE));import probe_front_contracts as contracts
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def canon(r):return json.loads(json.dumps(r))
def without_time(r):return {k:v for k,v in canon(r).items() if k!='seconds'}
def read_rows(p):return [json.loads(x) for x in Path(p).read_text().splitlines()]
def compile_to(source,out,shared=False):
    args=['gcc','-O3','-std=c11','-Wall','-Wextra','-Werror']
    if shared:args+=['-shared','-fPIC']
    run=subprocess.run([*args,str(source),'-o',str(out)],capture_output=True,text=True)
    assert run.returncode==0 and not run.stdout and not run.stderr,(run.returncode,run.stdout,run.stderr)

def exact_algebra():
    old=PARENT_SOURCE.read_text();new=SOURCE.read_text().replace('sp31_moving_front_cofactor','sp31_fourth_ternary_cofactor')
    # All representation, prefix/count, refinement, native/keep equations,
    # branch lifting and exported local checker are unchanged byte-for-byte.
    assert old[old.index('typedef struct'):old.index('static int save')]==new[new.index('typedef struct'):new.index('static int save')]
    for s in (old,new):assert 'enum {Q=1024,LO=80*Q,HI=200*Q,NX=HI-LO,BORDER=64};' in s
    assert 'for(int i=BORDER;i<NX-BORDER;i++)' in new
    assert 'for(int i=0;i<BORDER;i++)nextinfo[i]=2;' in new
    assert 'b[j][i]=(j==2||j==4)&&t>=2*Q?0:2;' in new
    assert 'if(i>=NX-2*BORDER)' in new
    return dict(native_domain_algebra_and_exported_local_checker_byte_identical_to_J248=True,
                only_seed_enclosure_boundary_and_entry_name_changed=True,
                omitted_left_domains_are_top=True,right_128_site_guard=True)

def cofactors(tmp):
    Apath=tmp/'abstract.so';Epath=tmp/'exact.so'
    compile_to(SOURCE,Apath,True);compile_to(EXACT,Epath,True)
    A=ctypes.CDLL(str(Apath)).sp31_moving_front_cofactor
    E=ctypes.CDLL(str(Epath)).sp31_two_sources_cofactor
    A.argtypes=[ctypes.POINTER(ctypes.c_uint16),ctypes.POINTER(ctypes.c_uint8),ctypes.c_int,ctypes.c_int]
    E.argtypes=[ctypes.POINTER(ctypes.c_uint8),ctypes.POINTER(ctypes.c_uint8),ctypes.c_int,ctypes.c_int]
    A.restype=E.restype=ctypes.c_uint
    rng=random.Random(2531024);trace=hashlib.sha256();exact=inclusion=0
    def eval_exact(n,inf,p,t):
        z=E((ctypes.c_uint8*81)(*n),(ctypes.c_uint8*81)(*inf),p,t)
        native=[(z>>j)&1 for j in range(5)]
        return native+[int(not(native[1] and native[0]!=((z>>5)&1)))]
    for p in range(1024):
        t=(0,2047,2048,6143)[p%4]
        n=[rng.randrange(32) for _ in range(81)];inf=[rng.randrange(2) for _ in range(81)]
        packed=[sum(((v>>j)&1)<<(2*j) for j in range(5)) for v in n]
        z=A((ctypes.c_uint16*81)(*packed),(ctypes.c_uint8*81)(*inf),p,t)
        domains=[(z>>(2*j))&3 for j in range(6)];actual=eval_exact(n,inf,p,t)
        assert domains==actual,(p,t)
        trace.update(json.dumps([p,t,domains],separators=(',',':')).encode());exact+=1
    for case in range(128):
        p=rng.randrange(1024);t=(0,2047,2048,6143)[case%4]
        n=[[rng.randrange(3) for _ in range(5)] for _ in range(81)];inf=[rng.randrange(3) for _ in range(81)]
        packed=[sum(v<<(2*j) for j,v in enumerate(row)) for row in n]
        z=A((ctypes.c_uint16*81)(*packed),(ctypes.c_uint8*81)(*inf),p,t)
        domains=[(z>>(2*j))&3 for j in range(6)];assert all(d<=2 for d in domains)
        for sample in range(8):
            cn=[sum((rng.randrange(2) if v==2 else v)<<j for j,v in enumerate(row)) for row in n]
            ci=[rng.randrange(2) if v==2 else v for v in inf];actual=eval_exact(cn,ci,p,t)
            assert all(d==2 or d==v for d,v in zip(domains,actual)),(case,sample,p,t)
            trace.update(json.dumps([case,sample,p,t,domains,actual],separators=(',',':')).encode());inclusion+=1
    return dict(exact_all_phase_checks=exact,selected_ternary_realization_checks=inclusion,
                deterministic_trace_sha256=trace.hexdigest(),measured_supplements=True)

def check_state(path):
    data=Path(path).read_bytes();Q=1024;LO=80*Q;HI=200*Q;N=HI-LO
    assert len(data)==6*N
    expected=[]
    for j in range(5):
        row=bytearray(N)
        for i in range(N):
            x=LO+i
            if j in (0,1,3) and x<155*Q-512:row[i]=2
            if j==0 and 155*Q-512<=x<158*Q:row[i]=1
            if j==1 and 158*Q-512<=x<158*Q:row[i]=1
        expected.append(bytes(row))
    assert data[:5*N]==b''.join(expected),'Native fixed-point domains differ from displayed table.'
    assert all(v<=2 for v in data)
    return data[:5*N]

def trajectories(tmp):
    binary=tmp/'front';compile_to(SOURCE,binary);result={}
    for name,ticks,stop,logname,statename in [
        ('fixed',6144,1,'front_trace_probe01.jsonl','front_state_probe01.bin'),
        ('pulse',6144,0,'front_pulse_trace_probe01.jsonl','front_pulse_state_probe01.bin')]:
        log=tmp/(name+'.jsonl');state=tmp/(name+'.bin')
        with log.open('w') as fh:
            run=subprocess.run([str(binary),str(state),str(ticks),str(stop)],stdout=fh,stderr=subprocess.PIPE,text=True)
        assert run.returncode==0 and not run.stderr,(name,run.returncode,run.stderr)
        assert log.read_bytes()==(OUT/logname).read_bytes(),name
        assert state.read_bytes()==(OUT/statename).read_bytes(),name
        native=check_state(state);records=read_rows(log);rows=records[:-1]
        assert [r['row'] for r in rows]==list(range(len(rows)))
        assert all(r['border_violations']==0 for r in rows)
        assert all(r['GF_possible_right_exclusive']<=158*1024 for r in rows)
        assert all(r['native_possible_ones'][2]==r['native_possible_ones'][4]==0 for r in rows if r['row']>=2049)
        result[name]=dict(rows=len(rows),marker=records[-1],native_sha256=hashlib.sha256(native).hexdigest(),
                         maximum_GF_right=max(r['GF_possible_right_exclusive'] for r in rows),
                         all_right_exterior_guards_zero=True,endpoint=rows[-1])
    assert result['fixed']['marker']['native_abstract_fixed_point'] and result['fixed']['marker']['row']==2562
    assert result['fixed']['rows']==2563 and result['pulse']['rows']==6145
    assert result['fixed']['native_sha256']==result['pulse']['native_sha256']
    return result

def assets():
    parent=json.loads(PARENT_CERT.read_text());pinned=dict(parent['assets_sha256'])
    for rel,h in pinned.items():assert sha(ROOT/rel)==h,rel
    pinned[str(PARENT_CERT.relative_to(ROOT))]=sha(PARENT_CERT)
    paths={*HERE.iterdir(),*OUT.iterdir(),ROOT/'figs/robustness/unregistered_sp31_moving_front_preparation.log'}
    for module in list(sys.modules.values()):
        f=getattr(module,'__file__',None)
        if f:
            p=Path(f).resolve()
            if p.suffix=='.py' and p.is_relative_to(ROOT):paths.add(p)
    # New read-only/issue logs are audit receipts, not self-hashed certificate inputs.
    for p in paths:
        if p.is_file() and p.name not in (CERT.name,'issue_run.log','readonly_run.log'):
            rel=str(p.relative_to(ROOT));h=sha(p)
            assert rel not in pinned or pinned[rel]==h,rel
            pinned[rel]=h
    return dict(sorted(pinned.items()))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--issue',action='store_true');args=ap.parse_args();start=time.monotonic()
    if args.issue:assert not CERT.exists(),'Frozen receipt exists; use read-only replay.'
    else:
        frozen=json.loads(CERT.read_text())
        for rel,h in frozen['assets_sha256'].items():assert sha(ROOT/rel)==h,rel
    old=json.loads((OUT/'front_contract_probe_receipt.json').read_text());new=contracts.compute()
    assert without_time(old)==without_time(new),'Exact phase/route/cofactor replay differs.'
    assert old['phase_population']['cases']==8136
    assert len(old['full_cofactors']['selected_full_F31_cofactors'])==48
    assert len(old['routes_and_margins']['new_zero_foreign_GF_F1_F2_targets'])==36
    assert len(old['finite_boundary_induction']['boundaries'])==290
    assert not old['actual_physical_renewal_supplied_by_separate_written_proof']
    algebra=exact_algebra()
    with tempfile.TemporaryDirectory(prefix='sp31_front_') as d:
        tmp=Path(d);samples=cofactors(tmp);runs=trajectories(tmp)
    cert=dict(passed=True,Q=1024,U=475136,TF=278401,radius=37,proof_sha256=sha(PROOF),checker_sha256=sha(__file__),
        candidate_sha256=old['candidate_sha256'],netlist_sha256=old['netlist_sha256'],
        algebra=algebra,cofactor_checks=samples,runs=runs,
        maximal_left_native_Info_domains_sound=True,right_canonical_exterior_guard_proved=True,
        closed_guard_infinite_native_postfixed_enclosure_proved=True,
        conditional_actual_B_one_period_translation_by3Q_proved=True,
        conditional_upper_Age_interval=[0,278400],conditional_R_modQ_interval=[5,1021],
        conditional_bank_reset_fresh_work_capture_courier_and_commit_lift_supplied_by_written_proof=True,
        actual_same_J225_fault_all_original_upper_Info_no_later_errors_core_proved=True,
        actual_first_boundary=4,actual_last_boundary=293,actual_core_width=3584,
        actual_last_L_R=[1019,1022],actual_displacement_from4U=887808,
        upper_colony_boundary_next_period_excluded=True,
        right_phase_population_cases=8136,selected_full_F31_cofactors=48,
        selected_checks_measured_supplements=True,free_left_reachability_or_independence_proved=False,
        complete_upper_SFInfo_state_or_all_time_glider_or_eventual_recovery_proved=False,
        operational_real2_confinement_failure_or_arbitrary_higher_iid_minimum_proved=False,
        Gray_or_G17_refutation=False,rule_ROM_constants_or_G17_changed=False,global_reliability_established=False,
        assets_sha256=assets())
    if args.issue:CERT.write_text(json.dumps(cert,indent=2)+'\n')
    else:assert cert==frozen,'Read-only mathematical certificate differs.'
    print(json.dumps(dict(passed=True,readonly=not args.issue,certificate_sha256=sha(CERT),assets_verified=len(cert['assets_sha256']),
        fixed_point_row=2562,pulse_rows=6145,conditional_front_renewal_proved=True,actual_boundaries=[4,293],
        upper_boundary_next_transition_excluded=True,global_reliability_established=False,seconds=time.monotonic()-start)),flush=True)
if __name__=='__main__':main()
