#!/usr/bin/env python3
"""Issue once or replay the 24 exact enclosures and separately pinned lift."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import argparse,hashlib,json,subprocess,sys,tempfile,time
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
OUT=ROOT/'figs/robustness/unregistered_sp31_wrap_cases'
CERT=OUT/'wrap_disjunction_certificate.json';SOURCE=HERE/'sp31_wrap_cases01.c'
PROOF=HERE/'SP31_WRAP_DISJUNCTION.md'
PARENT=ROOT/'figs/robustness/unregistered_sp31_moving_front/front_renewal_certificate.json'
PARENT_SOURCE=ROOT/'Report/proofs/unregistered_sp31_moving_front/sp31_moving_front_probe01.c'
sys.path.insert(0,str(HERE));import probe_wrap_contracts02 as contracts
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def strip_time(r):return {k:v for k,v in r.items() if k!='seconds'}
def exact_algebra():
    old=PARENT_SOURCE.read_text();new=SOURCE.read_text().replace('sp31_wrap_cases_cofactor','sp31_moving_front_cofactor')
    assert old[old.index('typedef struct'):old.index('static int save')]==new[new.index('typedef struct'):new.index('static int save')]
    assert 'for(int i=BORDER;i<NX-BORDER;i++)' in new
    assert 'for(int i=0;i<BORDER;i++)nextinfo[i]=2;' in new
    assert 'b[j][i]=(j==2||j==4)&&t>=2*Q?0:2;' in new
    assert 'if(i>=NX-2*BORDER)' in new
    assert 'int same=t>=2*Q&&!memcmp(a,b,sizeof(a));' in new
    return dict(native_domain_algebra_byte_identical_to_J253_and_J248=True,
                analysis_seed_disjunction_only=True,omitted_left_top_and_right128_guard=True)
def expected_native(m,mask):
    Q=1024;LO=80*Q;N=120*Q;rows=[]
    for j in range(5):
        v=bytearray(N)
        for i in range(N):
            x=LO+i
            if m==3:
                if j in (0,1,3) and x<155*Q-512:v[i]=2
                if j==0 and 155*Q-512<=x<157*Q:v[i]=1
                if j==1 and 157*Q-512<=x<157*Q:v[i]=1
            elif j in (0,1,3) and x<(154 if mask in (3,7) else 155)*Q:v[i]=2
        rows.append(bytes(v))
    return b''.join(rows)
def trajectories(tmp):
    binary=tmp/'cases';run=subprocess.run(['gcc','-O3','-std=c11','-Wall','-Wextra','-Werror',str(SOURCE),'-o',str(binary)],capture_output=True,text=True)
    assert run.returncode==0 and not run.stdout and not run.stderr
    discovery={m:json.loads((OUT/name).read_text()) for m,name in ((3,'wrap_cases_probe01_receipt.json'),(2,'zero_right_cases_probe01_receipt.json'))}
    tasks=[(m,k) for m in (3,2) for k in range(16 if m==3 else 8)]
    fixed3=[2050,2808,2306,2808,2220,2808,2306,2808,2562,2808,2562,2808,2562,2808,2562,2808]
    def one(task):
        m,k=task;stem=('mask' if m==3 else 'zero_mask')+f'{k:02d}'
        log=tmp/(stem+'.jsonl');state=tmp/(stem+'.bin')
        with log.open('w') as f:
            r=subprocess.run([str(binary),str(state),'6144','1',str(m),'2' if m==3 else '0',str(k)],stdout=f,stderr=subprocess.PIPE,text=True)
        assert r.returncode==0 and not r.stderr,(m,k,r.returncode,r.stderr)
        assert log.read_bytes()==(OUT/(stem+'_trace01.jsonl')).read_bytes(),(m,k,'trace')
        data=state.read_bytes();assert data==(OUT/(stem+'_state01.bin')).read_bytes(),(m,k,'state')
        N=120*1024;assert len(data)==6*N and all(v<=2 for v in data)
        assert data[:5*N]==expected_native(m,k),(m,k,'native endpoint')
        rows=[json.loads(x) for x in log.read_text().splitlines()];nums=rows[:-1];marker=rows[-1]
        assert [r['row'] for r in nums]==list(range(len(nums)))
        fixed=fixed3[k] if m==3 else 2228 if k in (1,5) else 2050
        assert marker['native_abstract_fixed_point'] and marker['row']==fixed and nums[-1]['row']==fixed
        assert not marker['actual_Info_or_full_boundary_or_repair_proved'] and not marker['global_reliability_established']
        assert nums[-2]['native_possible_ones']==nums[-1]['native_possible_ones']
        assert all(r['border_violations']==0 for r in nums)
        assert all(r['GF_possible_right_exclusive']<=(157 if m==3 else 155)*1024 for r in nums)
        assert all(r['native_possible_ones'][2]==r['native_possible_ones'][4]==0 for r in nums if r['row']>=2049)
        d=discovery[m]['results'][k];assert d['mask']==k
        assert sha(log)==d['trace_sha256'] and sha(state)==d['state_sha256']
        assert sha(OUT/(stem+'_stderr01.log'))==d['stderr_sha256'] and not (OUT/(stem+'_stderr01.log')).read_bytes()
        return dict(width=m,mask=k,fixed_row=fixed,rows=len(nums),native_sha256=hashlib.sha256(data[:5*N]).hexdigest(),
                    all_right_guards_zero=True,maximum_possible_GF_right=max(r['GF_possible_right_exclusive'] for r in nums),
                    trace_sha256=sha(log),state_sha256=sha(state))
    with ThreadPoolExecutor(max_workers=4) as pool:result=list(pool.map(one,tasks))
    assert len({r['native_sha256'] for r in result if r['width']==3})==1
    for m,d in discovery.items():
        assert not d['global_reliability_established'] and not d['rule_ROM_constants_or_G17_changed']
        assert not d['actual294U_or_later_physical_boundary_proved' if m==3 else 'actual295U_or_later_physical_boundary_proved']
    return result
def assets():
    parent=json.loads(PARENT.read_text());pinned=dict(parent['assets_sha256'])
    for rel,h in pinned.items():assert sha(ROOT/rel)==h,rel
    pinned[str(PARENT.relative_to(ROOT))]=sha(PARENT)
    paths={*HERE.iterdir(),*OUT.iterdir()}
    for d in (ROOT/'Report/proofs/unregistered_sp31_front_wrap_probe',ROOT/'figs/robustness/unregistered_sp31_front_wrap_probe'):
        paths.update(d.iterdir())
    for mod in list(sys.modules.values()):
        f=getattr(mod,'__file__',None)
        if f:
            p=Path(f).resolve()
            if p.suffix=='.py' and p.is_relative_to(ROOT):paths.add(p)
    for p in paths:
        if p.is_file() and p.name not in (CERT.name,'issue_run.log','readonly_run.log'):
            rel=str(p.relative_to(ROOT));h=sha(p);assert rel not in pinned or pinned[rel]==h,rel;pinned[rel]=h
    return dict(sorted(pinned.items()))
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--issue',action='store_true');args=ap.parse_args();t=time.monotonic()
    if args.issue:assert not CERT.exists(),'Existing certificate immutable; use read-only replay.'
    else:
        frozen=json.loads(CERT.read_text())
        for rel,h in frozen['assets_sha256'].items():assert sha(ROOT/rel)==h,rel
    old=json.loads((OUT/'wrap_contracts_probe02_receipt.json').read_text());new=contracts.compute()
    assert strip_time(old)==strip_time(new)
    assert len(old['cofactors']['erased_left_wrap_cofactors'])==36
    assert not old['cofactors']['free_left_upper_halfline_cofactors'][0]['all_native_outputs_resolved']
    assert len(old['routes']['new_foreign_zero_targets'])==24
    algebra=exact_algebra()
    with tempfile.TemporaryDirectory(prefix='sp31_wrap_disjunction_') as d:runs=trajectories(Path(d))
    cert=dict(passed=True,Q=1024,U=475136,TF=278401,radius=37,
        proof_sha256=sha(PROOF),checker_sha256=sha(__file__),candidate_sha256=old['candidate_sha256'],netlist_sha256=old['netlist_sha256'],
        algebra=algebra,runs=runs,exact_disjunctive_cases=24,selected_full_wrap_cofactors=36,
        maximal_left_domains_and_actual_Info_erasures_included=True,
        infinite_closed_guard_postfixed_enclosures_proved=True,
        conditional_B3_residue1022_to_B2_translation_left3Q_right2Q_proved=True,
        conditional_B2_residue0_to_canonical_right_and_proper_native_banks_proved=True,
        physical_source_bank_Hold_and_reset_lift_supplied_by_written_proof=True,
        same_J225_fault_all_original_Info_no_later_errors_actual294U_wrong_GF_core=[1022*1024-512,1024*1024],
        actual294U_B2=[294,1022,1024],actual295U_canonical_GF_flags_WF_halfline_start=1024*1024,
        actual295U_true_native_banks_canonical_GF_Age295_flags_WF0=True,
        full_left_repair_or_future_halfline_persistence_or_all_time_or_operational_higher_or_iid_minimum_proved=False,
        selected_cofactors_measured_supplements=True,free_left_unresolved_cofactor_not_a_counterexample=True,
        Gray_or_G17_refutation=False,rule_ROM_constants_or_G17_changed=False,global_reliability_established=False,
        assets_sha256=assets())
    if args.issue:CERT.write_text(json.dumps(cert,indent=2)+'\n')
    else:assert cert==frozen,'Replay differs from frozen certificate.'
    print(json.dumps(dict(passed=True,readonly=not args.issue,assets_verified=len(cert['assets_sha256']),
        certificate_sha256=sha(CERT),cases=24,wrap_cofactors=36,actual_boundaries=[294,295],
        all_time_or_iid_or_minimum_proved=False,seconds=time.monotonic()-t)),flush=True)
if __name__=='__main__':main()
