#!/usr/bin/env python3
"""Exact phase populations, physical routes and margins; no rule mutation."""
from collections import Counter
from itertools import product
from pathlib import Path
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT),str(ROOT/'Report/proofs'),str(ROOT/'Report/proofs/unregistered_terminal')]
import proposed_native_command1024 as proposed
from gacsca.netlist import Compiled
from probe_sp30_symbolic_left_absorption import AbsorptionNet
from check_native_command1024_first_pulse import blocked
NATIVE=('addr','age','f1','f2','wf1','wf2')
OUT=ROOT/'figs/robustness/unregistered_sp31_moving_front'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def phase_populations(p):
    trace=hashlib.sha256();cases=0;counts=Counter()
    # Right capture: erased raw pair to the left, canonical/common pair
    # on the right. Refined erased GF stays0 by the written valid-block proof.
    for r,joff in product(range(5,p.Q-2),range(8)):
        j=r+joff;gf=j%p.Q
        mm=sum(0<=gf+d<p.Q and j+d<r and (gf+d)%p.Q!=0 for d in range(-5,0))
        assert (mm>=3)==(joff<=2),(r,joff,mm)
        # New F2 has no right-quorum, WF or old-F2 source in this table.
        # Above the front all flags are0, and right geometry is canonical.
        counts[str(joff)]+=1;cases+=1
        trace.update(f'{r},{joff},{mm};'.encode())
    assert cases==8136
    excluded=[]
    for r in (1022,1023):
        excluded.append(dict(R_modQ=r,left_mismatches=[sum(0<=((r+j)%p.Q)+d<p.Q and r+j+d<r and (((r+j)%p.Q)+d)%p.Q!=0 for d in range(-5,0)) for j in range(3)]))
    assert excluded[0]['left_mismatches']==[5,4,0]
    return dict(cases=cases,sufficient_R_modQ_interval=[5,1021],digest_sha256=trace.hexdigest(),
                offset_counts=dict(counts),excluded_boundary_examples=excluded,
                all_legal_upper_Ages_below_TF_covered_by_written_guard_argument=True)

def full_cofactors(p):
    rows=[]
    for r,off in product((5,6,155,1019,1020,1021),range(8)):
        j=r+off
        class Right(AbsorptionNet):
            def input(self,key):
                if isinstance(key,tuple) and len(key)==4 and key[0]=='x':
                    _,d,f,b=key;t=j+d
                    if f in NATIVE:
                        v=(t%p.Q if f=='addr' else p.age_code(4) if f=='age' else 0) if t>=r else 0
                        return (v>>b)&1
                return super().input(key)
        n,_=proposed.full_net(p,Right)
        assert n.outputs['y','f1',0]==int(off<=2) and n.outputs['y','f2',0]==0,(r,off)
        rows.append(dict(R_modQ=r,receiver_offset=off,F1=int(off<=2),F2=0,full_net_sha256=Compiled(n).digest))
    return dict(selected_full_F31_cofactors=rows,selected_upper_Age=4,
                measured_supplement_not_a_universal_upper_Age_proof=True)

def routes_and_margins(p):
    L,R=152,155;a=L*p.Q-512;b=R*p.Q;strip=((b-512,b),)
    counts=Counter();trace=hashlib.sha256()
    for row in proposed.dependency_table(p):
        if row['field'] not in NATIVE:continue
        phase=row['address']
        for j in range(R,R+41):
            for d in row['offsets']:
                for gather in p.gathers_q:
                    hit=blocked(strip,j,d,phase,p.Q)
                    assert hit==(j+d<R),(j,d,phase)
                    counts['right_actual_native_capture_routes']+=1
                    trace.update(f'{j},{d},{phase},{gather},{hit};'.encode())
        for h in range(L,R):
            for d in row['offsets']:
                for gather in p.gathers_q:
                    hit=blocked(strip,h-1,d,phase+512,p.Q)
                    assert hit==(h+d>=R),(h,d,phase)
                    counts['complete_foreign_native_capture_routes']+=1
    work=[]
    for h in range(L,R):
        o=(h-1)*p.Q+512
        assert a<=o+58-39 and o+965+39<b-512
        assert a<=o+1 and o+1023<b-512
        work.append(dict(h=h,work_margin=[o+19,o+1004],courier_holders=[o+1,o+1023]))
    newa=(L+3)*p.Q-512;newb=(R+3)*p.Q
    zeros=[]
    for h,phase in product(range(L+4,R+4),(*range(571,581),600,601)):
        y=(h-1)*p.Q+phase
        assert y-39>=newa and y+39<newb
        assert y-39>=b
        assert phase-512 in (*range(59,69),88,89)
        zeros.append(dict(h=h,physical_primary=y,normal_phase=phase-512,opposite_phase=phase,
                          fixed_core_native_margin=[y-39,y+39]))
    assert len(zeros)==36
    native=[]
    for t in range(R-35,R+46):
        valid=[]
        for c in (-30,-10,10,30):
            members=[t+c+u for u in range(-2,3)]
            clean=sum(s>=R for s in members)
            # Every valid adjusted joint triple has canonical GF/commonAge.
            # Erased zero GF adjusted words are distinct; an erased triple is invalid.
            valid.append(clean>=3)
        if t<R:assert sum(valid)<=2
        native.append(dict(reader_offset=t-R,valid_canonical_blocks=valid,raw_pair_erased=t<R))
    assert proposed.local.CENTERS==(-30,-10,10,30)
    # Translation by integer Q preserves every physical residue used above.
    return dict(route_counts=dict(counts),route_digest_sha256=trace.hexdigest(),
                foreign_work_margins=work,new_zero_foreign_GF_F1_F2_targets=zeros,
                right_joint_refinement_cases=native,all_integer_Q_translations_preserve_physical_residues=True)

def finite_induction(p):
    rows=[]
    for n in range(4,294):
        L=152+3*(n-4);R=155+3*(n-4)
        if n<293:assert 5<=R%p.Q<=1021 and n<p.T_wf
        rows.append(dict(n=n,L=L,R=R,time=n*p.U,wrong_GF_core=[L*p.Q-512,R*p.Q],
                         renewal_phase_premise=5<=R%p.Q<=1021))
    assert rows[-1]['R']==1022 and not rows[-1]['renewal_phase_premise']
    assert rows[-2]['R']==1019
    return dict(boundaries=rows,first_boundary=4,last_proved_boundary=293,
                first_uncovered_period=293,core_width=3584,displacement_from4U=867*p.Q,
                all_time_translation_claimed=False)

def compute():
    start=time.monotonic();p=proposed.parameters();c=proposed.load_artifact()
    return dict(Q=p.Q,U=p.U,TF=p.T_wf,candidate_sha256=c.digest(),netlist_sha256=c.comp.digest,
                probe_sha256=sha(__file__),phase_population=phase_populations(p),
                full_cofactors=full_cofactors(p),routes_and_margins=routes_and_margins(p),
                finite_boundary_induction=finite_induction(p),
                actual_physical_renewal_supplied_by_separate_written_proof=False,
                all_time_glider_eventual_repair_higher_iid_or_minimum_proved=False,
                rule_ROM_constants_or_G17_changed=False,global_reliability_established=False,
                seconds=time.monotonic()-start)
def main():
    OUT.mkdir(parents=True,exist_ok=True);path=OUT/'front_contract_probe_receipt.json'
    assert not path.exists(),'Existing receipts are immutable; use compute() read-only.'
    r=compute();path.write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps(dict(passed=True,phase_cases=r['phase_population']['cases'],
                         full_cofactors=len(r['full_cofactors']['selected_full_F31_cofactors']),
                         boundaries=len(r['finite_boundary_induction']['boundaries']),seconds=r['seconds'])),flush=True)
if __name__=='__main__':main()
