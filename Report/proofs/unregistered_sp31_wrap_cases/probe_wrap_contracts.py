#!/usr/bin/env python3
"""Exact native cofactors/routes for two wrap cases; physical lift is separate."""
from pathlib import Path
from itertools import product
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT),str(ROOT/'Report/proofs'),str(ROOT/'Report/proofs/unregistered_terminal')]
import proposed_native_command1024 as proposed
from gacsca.netlist import Compiled
from probe_sp30_symbolic_left_absorption import AbsorptionNet
from check_native_command1024_first_pulse import blocked
NATIVE=('addr','age','f1','f2','wf1','wf2')
OUT=ROOT/'figs/robustness/unregistered_sp31_wrap_cases'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def cofs(p):
    rows=[]
    for r,age,off in product((1022,0),(293,294),range(9)):
        j=r+off
        class Right(AbsorptionNet):
            def input(self,key):
                if isinstance(key,tuple) and len(key)==4 and key[0]=='x':
                    _,d,f,b=key;t=j+d
                    if f in NATIVE:
                        v=(t%p.Q if f=='addr' else p.age_code(age) if f=='age' else 0) if t>=r else 0
                        return (v>>b)&1
                return super().input(key)
        n,_=proposed.full_net(p,Right)
        values={f:sum(n.outputs['y',f,b]<<b for b in range(dict(proposed.schema(p))[f]))
                for f in NATIVE if all(n.outputs['y',f,b] in (0,1) for b in range(dict(proposed.schema(p))[f]))}
        expected=dict(addr=j%p.Q,age=p.age_code(age+1),f1=int(r==1022 and off<2),f2=0,wf1=0,wf2=0)
        assert values==expected,(r,age,off,values,expected)
        rows.append(dict(R_modQ=r,Age=age,offset=off,outputs=values,netlist_sha256=Compiled(n).digest))
    # Native half-line calculation at an upper colony boundary. Left native
    # words and all SF/Info/instruction inputs remain symbolic and unrestricted.
    half=[]
    for age,off in product((295,p.T_wf-1),range(38)):
        j=off
        class Half(AbsorptionNet):
            def input(self,key):
                if isinstance(key,tuple) and len(key)==4 and key[0]=='x':
                    _,d,f,b=key;t=j+d
                    if t>=0 and f in NATIVE:
                        v=t%p.Q if f=='addr' else p.age_code(age) if f=='age' else 0
                        return (v>>b)&1
                return super().input(key)
        n,_=proposed.full_net(p,Half)
        values={f:sum(n.outputs['y',f,b]<<b for b in range(dict(proposed.schema(p))[f]))
                for f in NATIVE if all(n.outputs['y',f,b] in (0,1) for b in range(dict(proposed.schema(p))[f]))}
        expected=dict(addr=j,age=p.age_code(age+1),f1=0,f2=0,wf1=0,wf2=0)
        assert values==expected,(age,off,values,expected)
        half.append(dict(Age=age,offset=off,outputs=values,netlist_sha256=Compiled(n).digest))
    return dict(erased_left_wrap_cofactors=rows,free_left_upper_halfline_cofactors=half,
                selected_Ages_measured_supplement_not_universal_Age_proof=True)
def routes(p):
    result=[]
    for m in (3,2):
        R=155;L=R-m;a=L*p.Q-512;b=R*p.Q;strip=((b-512,b),);count=0;trace=hashlib.sha256()
        for row in proposed.dependency_table(p):
            if row['field'] not in NATIVE:continue
            phase=row['address']
            for j in range(R,R+41):
                for d,g in product(row['offsets'],p.gathers_q):
                    hit=blocked(strip,j,d,phase,p.Q)
                    assert hit==(j+d<R),(m,j,d,phase)
                    trace.update(f'{m},{j},{d},{phase},{g},{hit};'.encode());count+=1
            for h in range(L,R):
                for d,g in product(row['offsets'],p.gathers_q):
                    hit=blocked(strip,h-1,d,phase+512,p.Q)
                    assert hit==(h+d>=R),(m,h,d,phase)
                    trace.update(f'{m},{h},{d},{phase},{g},{hit};'.encode());count+=1
        work=[]
        for h in range(L,R):
            o=(h-1)*p.Q+512
            assert a<=o+19 and o+1004<b-512
            assert a<=o+1 and o+1023<b-512
            work.append(dict(h=h,work_margin=[o+19,o+1004],courier_margin=[o+1,o+1023]))
        result.append(dict(width=m,routes=count,route_sha256=trace.hexdigest(),work=work))
    zeros=[];L=152;R=155;newa=(L+3)*p.Q-512;newb=(R+2)*p.Q
    for h,phase in product(range(L+4,R+3),(*range(571,581),600,601)):
        y=(h-1)*p.Q+phase
        assert y-39>=newa and y+39<newb and y-39>=R*p.Q
        zeros.append(dict(h=h,phase=phase,primary=y,margin=[y-39,y+39]))
    assert len(zeros)==24
    return dict(cases=result,new_foreign_zero_targets=zeros,
                physical_halfline_work_minimum_margin=19,
                halfline_boundary_phase=0,
                native_edge_separation_width2=2*p.Q,native_radius=37,
                closed_native_edge_separation_exceeds_twice_radius=True)
def compute():
    t=time.monotonic();p=proposed.parameters();c=proposed.load_artifact()
    return dict(Q=p.Q,U=p.U,TF=p.T_wf,candidate_sha256=c.digest(),netlist_sha256=c.comp.digest,
        probe_sha256=sha(__file__),cofactors=cofs(p),routes=routes(p),
        actual_physical_wrap_and_halfline_lift_supplied_by_separate_written_proof=False,
        all_time_or_eventual_higher_iid_or_minimum_proved=False,
        rule_ROM_constants_or_G17_changed=False,global_reliability_established=False,
        seconds=time.monotonic()-t)
def main():
    path=OUT/'wrap_contracts_probe01_receipt.json';assert not path.exists()
    r=compute();path.write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps(dict(passed=True,wrap_cofactors=len(r['cofactors']['erased_left_wrap_cofactors']),
        halfline_cofactors=len(r['cofactors']['free_left_upper_halfline_cofactors']),seconds=r['seconds'])),flush=True)
if __name__=='__main__':main()
