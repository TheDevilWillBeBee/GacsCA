#!/usr/bin/env python3
"""Separate fourth-boundary bank cofactors; no fifth source/pulse theorem."""
from collections import Counter
from itertools import product
from pathlib import Path
import hashlib,json,sys,time
import numpy as np

ROOT=Path(__file__).resolve().parents[3];S=ROOT/'Report/proofs'
sys.path[:0]=[str(ROOT),str(S),str(S/'unregistered_terminal'),str(S/'unregistered_sp31_fourth_enclosure')]
from gacsca import rule_g
from gacsca.netlist import Compiled,const_word
from probe_sp30_symbolic_left_absorption import AbsorptionNet
from probe_sp31_fourth_enclosure import fourth_left_value,NATIVE
from check_native_command1024_first_pulse import blocked
import proposed_native_command1024 as proposed
OUT=ROOT/'figs/robustness/unregistered_sp31_fourth_banks'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def expected_GF(j,a,q134,q141):
    if j<=135:return j%1024
    if j==136:return j if a or q134==134 else 0
    if j==137:return j if a and q134==134 else 0
    return q141 if j==141 else 0

def native_case(p,build,a,j,q134,q141):
    n=AbsorptionNet()
    cells={d:{f:[fourth_left_value(n,p,j+d,f,b,a,q134,q141) for b in range(p.k if f=='addr' else p.m)]
              if f in ('addr','age') else fourth_left_value(n,p,j+d,f,0,a,q134,q141) for f in NATIVE}
           for d in range(-5,9)}
    got=build(n,cells,p.k,p.m,Q=p.Q,nb=p.nb,radix=p.R,pos_bits=p.PB,service_force=0)
    assert got['addr']==const_word(expected_GF(j,a,q134,q141),p.k),(a,j,q134,q141,'GF')
    assert got['f1']==int(j>=106),(a,j,q134,q141,'F1')
    if j<=135:
        assert got['age_now']==const_word(p.age_code(3),p.m),(a,j,q134,q141,'current_Age')
        assert got['age']==const_word(p.age_code(4),p.m),(a,j,q134,q141,'new_Age')
    if j<=131:assert got['f2']==0,(a,j,q134,q141,'F2')

def side_quorums(p):
    cases=0;sig=hashlib.sha256()
    # The two free GF words never occur together on a native side.
    for a,j,sign in product(range(2),range(96,142),(-1,1)):
        sources=[j+sign*d for d in range(1,6)]
        free=[s for s in sources if s in (134,141)];assert len(free)<=1
        for q in range(p.Q) if free else (0,):
            q134=q if free==[134] else 0;q141=q if free==[141] else 0
            raw=[s if s<=132 else 133*a if s==133 else q134 if s==134 else q141 if s==141 else 0 for s in sources]
            pop=Counter((v+j-s)%p.Q for v,s in zip(raw,sources));quorum=[v for v,k in pop.items() if k>=3]
            assert len(quorum)<=1
            if sign==1:
                if j<=129:assert quorum==[j]
                if j>=132:assert not quorum
                if quorum:assert quorum==[j]
            else:
                answer=[j] if j<=135 or j==136 and (a or q134==134) or j==137 and a and q134==134 else []
                assert quorum==answer,(a,j,sign,q,quorum,answer)
            cases+=1;sig.update(f'{a},{j},{sign},{q},{quorum};'.encode())
    return dict(cases=cases,signature_sha256=sig.hexdigest())

def compute():
    p=proposed.parameters();c=proposed.load_artifact();build,source=proposed.proposed_build()
    assert c.digest()=='dc456bac4904647b66ee1f922788cdeb4428df91e21858fd8de0b3ccb4a69421'
    enclosure_path=ROOT/'figs/robustness/unregistered_sp31_fourth_ternary/ternary_enclosure_certificate.json'
    enclosure=json.loads(enclosure_path.read_text())
    assert enclosure['actual_fourth_source_enclosure_used'] and enclosure['native_only_quiet_extension_uses_guard_and_fixed_point']
    assert enclosure['results']['fixed']['terminal_marker']['row']==3698
    sig=hashlib.sha256();count=0
    # Exhaust q134 where it participates; q141's separate no-right-quorum
    # proof makes the other value irrelevant to these native outputs.
    for a,j in product(range(2),range(96,142)):
        for q134 in range(p.Q) if 129<=j<=139 else (0,):
            native_case(p,build,a,j,q134,0);count+=1
            sig.update(f'a={a},j={j},q134={q134},q141=0;'.encode())
    q141count=0
    for a,j,q134,q141 in product(range(2),range(136,142),(0,134),range(p.Q)):
        native_case(p,build,a,j,q134,q141);q141count+=1
        sig.update(f'a={a},j={j},q134={q134},q141={q141};'.encode())
    side=side_quorums(p)
    print(json.dumps(dict(stage='native_sides_and_shared_word_cofactors',q134_cases=count,q141_cases=q141count,side_cases=side['cases'])),flush=True)
    phases={(r['field'],r['bit']):r['address'] for r in proposed.dependency_table(p)}
    strips=((148*p.Q,149*p.Q-512),(152*p.Q-512,152*p.Q))
    full=[]
    for a,j,q134,q141 in product(range(2),range(124,142),(0,134,1023),(0,141,1023)):
        class Left(AbsorptionNet):
            def input(self,key):
                if isinstance(key,tuple) and len(key)==4 and key[0]=='x':
                    _,d,f,b=key
                    if f in NATIVE:return 0 if blocked(strips,j,d,phases[f,b],p.Q) else fourth_left_value(self,p,j+d,f,b,a,q134,q141)
                return super().input(key)
        n,_=proposed.full_net(p,Left)
        assert [n.outputs['y','addr',b] for b in range(p.k)]==const_word(expected_GF(j,a,q134,q141),p.k)
        assert n.outputs['y','f1',0]==1 and n.outputs['y','wf2',0]==0
        if j<=135:assert [n.outputs['y','age',b] for b in range(p.m)]==const_word(p.age_code(4),p.m)
        if j<=131:assert n.outputs['y','f2',0]==0
        if j!=141:assert n.outputs['y','wf1',0]==0
        full.append(dict(a=a,j=j,q134=q134,q141=q141,netlist_sha256=Compiled(n).digest))
    right=[]
    for j in range(155,191):
        class Right(AbsorptionNet):
            def input(self,key):
                if isinstance(key,tuple) and len(key)==4 and key[0]=='x':
                    _,d,f,b=key
                    if f in NATIVE:
                        if blocked(strips,j,d,phases[f,b],p.Q):return 0
                        v=(j+d)%p.Q if f=='addr' else p.age_code(3) if f=='age' else 0
                        return (v>>b)&1
                return super().input(key)
        n,_=proposed.full_net(p,Right)
        for f,v in dict(addr=j,age=p.age_code(4),f1=0,f2=0,wf1=0,wf2=0).items():
            assert [n.outputs['y',f,b] for b in range(dict(c.schema)[f])]==const_word(v,dict(c.schema)[f]),(j,f)
        right.append(dict(j=j,netlist_sha256=Compiled(n).digest))
    footprint=proposed.work_range(p);assert footprint==(58,966)
    assert 141*p.Q+footprint[1]-1+2+37<142*p.Q+1
    assert 155*p.Q+footprint[0]-2-37>=155*p.Q
    listing_path=ROOT/'figs/robustness/SP31_program_listing.json';listing=json.loads(listing_path.read_text());stores=[]
    for phase,shift in product((*range(59,69),88,89),(0,512)):
        target=phase+shift;hits=[r for r in listing if r[4]==target and r[6]==rule_g.K_HOLD];assert len(hits)==1
        row=hits[0];column=row[1]+(row[3]<<p.logNP);issue=p.E0+row[1]*p.PL+row[2]
        assert np.flatnonzero(((c.rom[target]>>2)&3)==rule_g.K_HOLD).tolist()==[column]
        assert issue+2<p.T_wf if shift==0 else issue>p.T_wf+6144
        stores.append(dict(phase=target,column=column,issue_age=issue,materialized_age=issue+2))
    foreign=[]
    for h,phase in product(range(153,156),(*range(571,581),600,601)):
        y=(h-1)*p.Q+phase
        assert 152*p.Q-512<=y-2-37 and y+2+37<155*p.Q
        assert not (149*p.Q-512<=y<152*p.Q) # old true phase, before pulse
        foreign.append(dict(h=h,physical_phase=phase,primary=y,value=0))
    return dict(Q=p.Q,U=p.U,radius=37,candidate_sha256=c.digest(),netlist_sha256=c.comp.digest,
        probe_sha256=sha(__file__),enclosure_certificate_sha256=sha(enclosure_path),listing_sha256=sha(listing_path),
        maintenance_source_sha256=hashlib.sha256(source.encode()).hexdigest(),
        source_dependencies_sha256={str(x.relative_to(ROOT)):sha(x) for x in (Path(proposed.__file__),S/'unregistered_sp31_fourth_enclosure/probe_sp31_fourth_enclosure.py',S/'unregistered_terminal/probe_sp30_symbolic_left_absorption.py',S/'check_native_command1024_first_pulse.py',ROOT/'gacsca/rule_g.py',ROOT/'gacsca/netlist.py')},
        q134_native_cofactors=count,q141_native_cofactors=q141count,native_signature_sha256=sig.hexdigest(),side_quorums=side,
        selected_left_full_cofactors=full,right_full_cofactors=right,selected_full_checks_measured_supplements=True,
        protected_left_work_frame_max=141,protected_right_work_frame_min=155,work_range=footprint,
        Hold_store_records=stores,new_foreign_GF_F1_F2_zero_primary_records=foreign,
        actual_fourth_boundary_bank_lift_supplied_by_written_proof=False,
        full_fourth_Info_SF_or_fifth_source_or_pulse_or_general_higher_iid_or_minimum_proved=False,
        additional_rule_change=False,active_G17_modified=False,Gray_or_G17_refutation=False,global_reliability_established=False)

def main():
    start=time.monotonic();OUT.mkdir(parents=True,exist_ok=True)
    target=OUT/'bank_cofactor_receipt.json';assert not target.exists(),'Do not overwrite a frozen receipt.'
    r=compute();r['seconds']=time.monotonic()-start
    target.write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps(dict(passed=True,q134_native_cofactors=r['q134_native_cofactors'],q141_native_cofactors=r['q141_native_cofactors'],
        selected_left_full_cofactors=len(r['selected_left_full_cofactors']),right_full_cofactors=len(r['right_full_cofactors']),
        new_foreign_zero_primaries=len(r['new_foreign_GF_F1_F2_zero_primary_records']),seconds=r['seconds'])),flush=True)
if __name__=='__main__':main()
