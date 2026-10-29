#!/usr/bin/env python3
"""Actual third protected/zero banks; no complete fourth enclosure/pulse."""
from itertools import product
from pathlib import Path
import hashlib,json,sys,time
import numpy as np
ROOT=Path(__file__).resolve().parents[2];S=ROOT/'Report/proofs';OUT=ROOT/'figs/robustness'
sys.path[:0]=[str(ROOT),str(S),str(S/'unregistered_terminal'),str(S/'unregistered_sp31_third_sources')]
from gacsca import rule_g
from gacsca.netlist import Compiled,const_word
from probe_sp30_symbolic_left_absorption import AbsorptionNet
from probe_sp31_third_true_sources import third_left_value,NATIVE
from check_native_command1024_first_pulse import blocked
import proposed_native_command1024 as proposed
PROOF=S/'SP31_THIRD_BOUNDARY_BANKS.md'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    start=time.monotonic();p=proposed.parameters();c=proposed.load_artifact();build,_=proposed.proposed_build()
    pulsepath=OUT/'SP31_third_pulse_certificate.json';pulse=json.loads(pulsepath.read_text())
    sourcepath=OUT/'SP31_third_source_enclosure_certificate.json';sources=json.loads(sourcepath.read_text())
    assert pulse['actual_third_native_pulse_proved'] and sources['actual_full_third_source_enclosure_proved']
    assert c.digest()==pulse['candidate_sha256']==sources['candidate_sha256']
    metrics=np.memmap(OUT/'unregistered_sp31_third_gpu/all4096/metrics.bin',dtype='<u4',mode='r',shape=(4096,6145,9))
    assert np.all(metrics[:,:,0]>0) and not np.any(metrics[:,:,8])
    assert np.all(metrics[:,:,1]<=196608-144896) and np.all(metrics[:,:,2]<=155648)
    hullrows=metrics.shape[0]*metrics.shape[1];del metrics
    phases={(r['field'],r['bit']):r['address'] for r in proposed.dependency_table(p)}
    strips=((141*p.Q,142*p.Q-512),(149*p.Q-512,149*p.Q))
    def capture(n,j,d,f,b,a,q):
        return 0 if blocked(strips,j,d,phases[f,b],p.Q) else third_left_value(n,p,j+d,f,b,a,q)
    sig=hashlib.sha256();cofs=0
    for a,j in product(range(2),range(90,141)):
        for q in range(p.Q) if 126<=j<=139 else (0,):
            n=AbsorptionNet();cells={d:{f:[capture(n,j,d,f,b,a,q) for b in range(p.k if f=='addr' else p.m)] if f in ('addr','age') else capture(n,j,d,f,0,a,q) for f in NATIVE} for d in range(-5,9)}
            got=build(n,cells,p.k,p.m,Q=p.Q,nb=p.nb,radix=p.R,pos_bits=p.PB,service_force=0)
            gf=j if j<=132 else 133*a if j==133 else q if j==134 else 0
            assert got['addr']==const_word(gf,p.k) and got['f1']==int(j>=112),(a,j,q,'GF/F1')
            if j<=132:assert got['age_now']==const_word(p.age_code(2),p.m) and got['age']==const_word(p.age_code(3),p.m),(a,j,q,'Age')
            if j<=130:assert got['f2']==0,(a,j,q,'F2')
            cofs+=1;sig.update(f'{a},{j},{q},{gf};'.encode())
    print(json.dumps(dict(third_true_all_q_cofactors=cofs,hull_rows=hullrows)),flush=True)
    full=[]
    for a,j,q in product(range(2),range(124,141),(0,134,1023)):
        class TrueBank(AbsorptionNet):
            def input(self,key):
                if isinstance(key,tuple) and len(key)==4 and key[0]=='x':
                    _,d,f,b=key
                    if f in NATIVE:return capture(self,j,d,f,b,a,q)
                return super().input(key)
        n,_=proposed.full_net(p,TrueBank)
        gf=j if j<=132 else 133*a if j==133 else q if j==134 else 0
        assert [n.outputs['y','addr',b] for b in range(p.k)]==const_word(gf,p.k)
        assert n.outputs['y','f1',0]==1 and n.outputs['y','wf2',0]==0
        if j!=134:assert n.outputs['y','wf1',0]==0
        if j<=132:assert [n.outputs['y','age',b] for b in range(p.m)]==const_word(p.age_code(3),p.m)
        full.append(dict(a=a,j=j,q=q,netlist_sha256=Compiled(n).digest))
    right=[]
    for j in range(152,191):
        class Right(AbsorptionNet):
            def input(self,key):
                if isinstance(key,tuple) and len(key)==4 and key[0]=='x':
                    _,d,f,b=key
                    if f in NATIVE:
                        if blocked(strips,j,d,phases[f,b],p.Q):return 0
                        v=(j+d)%p.Q if f=='addr' else p.age_code(2) if f=='age' else 0
                        return (v>>b)&1
                return super().input(key)
        n,_=proposed.full_net(p,Right)
        for f,v in dict(addr=j,age=p.age_code(3),f1=0,f2=0,wf1=0,wf2=0).items():
            assert [n.outputs['y',f,b] for b in range(dict(c.schema)[f])]==const_word(v,dict(c.schema)[f]),(j,f)
        right.append(dict(j=j,netlist_sha256=Compiled(n).digest))
    listingpath=OUT/'SP31_program_listing.json';listing=json.loads(listingpath.read_text());stores=[]
    for phase,shift in product((*range(59,69),88,89),(0,512)):
        actual=phase+shift;rows=[r for r in listing if r[4]==actual and r[6]==rule_g.K_HOLD];assert len(rows)==1
        row=rows[0];column=row[1]+(row[3]<<p.logNP);issue=p.E0+row[1]*p.PL+row[2]
        assert np.flatnonzero(((c.rom[actual]>>2)&3)==rule_g.K_HOLD).tolist()==[column]
        assert issue+2<p.T_wf if shift==0 else issue>p.T_wf+6144
        stores.append(dict(phase=actual,column=column,issue_age=issue,materialized_age=issue+2))
    recovered=[]
    for j,phase in product(range(142,149),(*range(59,69),88,89)):
        y=j*p.Q+phase
        assert 142*p.Q-512<=y-2-37 and y+2+37<149*p.Q
        assert y+2+37<149*p.Q-512
        recovered.append(dict(j=j,phase=phase,primary=y,value=0))
    foreign=[]
    for h,phase in product(range(149,153),(*range(571,581),601)):
        y=(h-1)*p.Q+phase
        assert 149*p.Q-512<=y-2-37 and y+2+37<152*p.Q
        if h>=150:assert y-2-37>=149*p.Q
        foreign.append(dict(h=h,phase=phase,primary=y,value=None if h==149 else 0))
    d=OUT/'unregistered_sp31_fourth_sources'
    experimental={str(path.relative_to(ROOT)):sha(path) for path in sorted(d.rglob('*')) if path.is_file()}
    result=dict(proposal='SP31',scope='Same actual J225 original-c16 native-only real2/all initial upperInfo/no latererrors; protected true3U and recovered/one-exception foreign GF-F2 banks only',
        Q=p.Q,U=p.U,radius=37,candidate_sha256=c.digest(),netlist_sha256=c.comp.digest,
        proof_sha256=sha(PROOF),checker_sha256=sha(__file__),listing_sha256=sha(listingpath),
        receipt_dependencies_sha256={name:sha(OUT/name) for name in ('SP31_third_pulse_certificate.json','SP31_third_source_enclosure_certificate.json','SP31_encoded_certificate.json','SP31_symbolic_schedule.json','SP31_interface_certificate.json')},
        proof_dependencies_sha256={name:sha(S/name) for name in ('SP31_OWN_RULE.md','SP31_FIRST_PULSE.md','SP31_THIRD_SOURCE_ENCLOSURE.md','SP31_THIRD_PULSE.md','SP31_SECOND_BANK_FOREIGN_SOURCES.md')},
        source_dependencies_sha256={str(path.relative_to(ROOT)):sha(path) for path in (Path(proposed.__file__),ROOT/'gacsca/rule_g.py',ROOT/'gacsca/netlist.py',S/'unregistered_sp31_third_sources/probe_sp31_third_true_sources.py',S/'check_native_command1024_first_pulse.py',S/'unregistered_terminal/probe_sp30_symbolic_left_absorption.py')},
        all4096_third_GF_hull_rows=hullrows,protected_true_left_max=140,protected_true_right_min=152,
        third_true_all_q_cofactors=cofs,native_cofactor_signature_sha256=sig.hexdigest(),
        selected_left_full_cofactors=full,right_full_cofactors=right,selected_full_checks_measured_supplements=True,
        actual24phase_ROM_keys=24*c.rom.shape[1],Hold_store_records=stores,
        recovered_true_zero_bank_records=recovered,foreign_GF_F2_bank_records=foreign,
        actual_protected_third_true_native_banks_proved=True,actual_recovered_true_GF_F1_F2_zero_banks_proved=True,
        actual_one_exception_third_foreign_GF_F2_banks_proved=True,
        current_foreign_Age_Workspace_banks_characterized=False,
        prepared_fourth_studies_assets_sha256=experimental,
        actual_fourth_source_enclosure_or_pulse_proved=False,
        all_prepared21bit_masks_shrink=False,prepared_mask_reachability_proved=False,
        full_upper_successor_or_arbitrary_higher_repair_or_positive_iid_or_minimum_proved=False,
        additional_rule_change=False,active_G17_modified=False,Gray_or_G17_refutation=False,global_reliability_established=False,
        seconds=time.monotonic()-start)
    (OUT/'SP31_third_boundary_banks_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(passed=True,third_true_all_q_cofactors=cofs,selected_left_full_cofactors=len(full),right_full_cofactors=len(right),recovered_zero_primaries=len(recovered),foreign_GF_F2_primaries=len(foreign),actual_fourth_source_enclosure_or_pulse_proved=False,seconds=result['seconds'])),flush=True)
if __name__=='__main__':main()
