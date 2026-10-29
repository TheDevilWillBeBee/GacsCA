#!/usr/bin/env python3
"""Same-history F31 full third-source enclosure; not a pulse/eroder theorem."""
from itertools import product
from pathlib import Path
import hashlib,json,sys,time
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(ROOT/'Report/proofs'),str(ROOT/'Report/proofs/unregistered_terminal'),str(ROOT/'Report/proofs/unregistered_sp31_third_sources')]
from gacsca import rule_g
from gacsca.netlist import Compiled,const_word
from probe_sp30_symbolic_left_absorption import AbsorptionNet
import proposed_native_command1024 as proposed
import proposed_distant_native448 as distant
from check_native_command1024_second_source_enclosure import left_value
from check_native_command1024_first_pulse import blocked
from probe_sp31_third_true_sources import third_left_value,primitive,NATIVE
OUT=ROOT/'figs/robustness'
PROOF=Path(__file__).with_name('SP31_THIRD_SOURCE_ENCLOSURE.md')
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    start=time.monotonic();p=proposed.parameters();c=proposed.load_artifact();build,maintenance=proposed.proposed_build()
    assert (p.Q,p.U,p.T_wf)==(1024,475136,278401)
    second=json.loads((OUT/'SP31_second_pulse_certificate.json').read_text())
    foreign=json.loads((OUT/'SP31_second_bank_foreign_sources_certificate.json').read_text())
    assert c.digest()==second['candidate_sha256']==foreign['candidate_sha256']
    assert foreign['actual_seven_third_foreign_Flag1_Flag2_commands_proved']
    runs=json.loads((OUT/'unregistered_sp31_seven_bit_second_pulse/receipt.json').read_text())
    hulls=[];tracehashes={};rowschecked=0
    for case in runs['cases']:
        mask=case['enclosure_mask'];path=OUT/'unregistered_sp31_seven_bit_second_pulse'/f'mask{mask}_trace.jsonl'
        assert sha(path)==case['trace_sha256']
        rows=[json.loads(line) for line in path.read_text().splitlines() if '"row"' in line]
        assert len(rows)==6145 and [r['row'] for r in rows]==list(range(6145))
        hull=[min(r['GF_left'] for r in rows),max(r['GF_right_exclusive'] for r in rows)]
        assert hull==[135*p.Q-512,149*p.Q]
        hulls.append(hull);tracehashes[str(path.relative_to(ROOT))]=sha(path);rowschecked+=len(rows)
    assert len(hulls)==128
    phases={(r['field'],r['bit']):r['address'] for r in proposed.dependency_table(p)}
    secondstrips=((134*p.Q,135*p.Q-512),(146*p.Q-512,146*p.Q))
    def first(n,s,f,b,q,j):
        return 0 if blocked(secondstrips,j,s-j,phases[f,b],p.Q) else left_value(n,p,s,f,b,q)
    bankcofs=0;sig=hashlib.sha256()
    for j,q in product(range(124,134),range(p.Q)):
        n=AbsorptionNet();cells={d:{f:[first(n,j+d,f,b,q,j) for b in range(p.k if f=='addr' else p.m)] if f in ('addr','age') else first(n,j+d,f,0,q,j) for f in NATIVE} for d in range(-5,9)}
        got=build(n,cells,p.k,p.m,Q=p.Q,nb=p.nb,radix=p.R,pos_bits=p.PB,service_force=0)
        expected=j if j<=129 else 130 if j==130 and q==127 else 0
        assert got['addr']==const_word(expected,p.k) and got['f1']==1,(j,q,'GF/F1')
        if 125<=j<=129:assert got['age']==const_word(p.age_code(2),p.m) and got['f2']==0,(j,q,'Age/F2')
        assert expected<p.Q-5 and got['f1']==1 # both actual Workspace guards false
        bankcofs+=1;sig.update(f'{j},{q},{expected},WF0;'.encode())
    print(json.dumps(dict(second_true_all_q_cofactors=bankcofs,actual_Workspace0_guard=True)),flush=True)
    bankfull=[]
    for j,q in product(range(124,134),(0,127,1023)):
        class Bank(AbsorptionNet):
            def input(self,key):
                if isinstance(key,tuple) and len(key)==4 and key[0]=='x':
                    _,d,f,b=key
                    if f in NATIVE:return first(self,j+d,f,b,q,j)
                return super().input(key)
        n,_=proposed.full_net(p,Bank)
        for f in ('wf1','wf2'):assert n.outputs['y',f,0]==0,(j,q,f)
        bankfull.append(dict(j=j,q=q,netlist_sha256=Compiled(n).digest))
    properfull=[]
    for j in (*range(90,124),*range(149,187)):
        class Proper(AbsorptionNet):
            def input(self,key):
                if isinstance(key,tuple) and len(key)==4 and key[0]=='x':
                    _,d,f,b=key
                    if f in NATIVE:
                        if blocked(secondstrips,j,d,phases[f,b],p.Q):return 0
                        if j<=123:return left_value(self,p,j+d,f,b)
                        value=(j+d)%p.Q if f=='addr' else p.age_code(1) if f=='age' else 0
                        return (value>>b)&1
                return super().input(key)
        n,_=proposed.full_net(p,Proper)
        expected=dict(addr=j%p.Q,age=p.age_code(2),f1=int(118<=j<=123),f2=0,wf1=0,wf2=0)
        for f,v in expected.items():assert [n.outputs['y',f,b] for b in range(dict(c.schema)[f])]==const_word(v,dict(c.schema)[f]),(j,f)
        properfull.append(dict(j=j,**expected,netlist_sha256=Compiled(n).digest))
    listingpath=OUT/'SP31_program_listing.json';listing=json.loads(listingpath.read_text());stores=[]
    for phase,shift in product((*range(59,69),88,89),(0,512)):
        actual=phase+shift;rs=[r for r in listing if r[4]==actual and r[6]==rule_g.K_HOLD];assert len(rs)==1
        row=rs[0];column=row[1]+(row[3]<<p.logNP)
        assert np.flatnonzero(((c.rom[actual]>>2)&3)==rule_g.K_HOLD).tolist()==[column]
        issue=p.E0+row[1]*p.PL+row[2]
        assert issue+2<p.T_wf if shift==0 else issue>p.T_wf+6144
        stores.append(dict(phase=actual,column=column,issue_age=issue,materialized_age=issue+2))
    recovered=[]
    for j,phase in product(range(135,142),(*range(59,69),88,89)):
        y=j*p.Q+phase
        assert 135*p.Q-512<=y-2-37 and y+2+37<146*p.Q and y+2+37<142*p.Q-512
        recovered.append(dict(j=j,phase=phase,primary=y,value=0))
    strips=((141*p.Q,142*p.Q-512),(149*p.Q-512,149*p.Q));routechecks=0
    for j,row,gather in product((*range(90,141),*range(149,187)),[r for r in proposed.dependency_table(p) if r['field'] in NATIVE],p.gathers_q):
        phase=row['address']
        for d in (0,*row['offsets']):
            erased=blocked(strips,j,d,phase,p.Q)
            assert erased==(j+d>=141 if j<=140 else j+d<=148),(j,d,phase,erased)
            if d:assert gather*p.Q+abs(d)*(p.Q//8)+1<p.E0
            routechecks+=1
    # First-boundary GF/Age tail is wholly canonical through126; flags
    # use the native radius8. For the third left tail use the proved
    # shared-table refinement identity, not a wholly-canonical radius37.
    assert 89+37<127 and 104+8<118 and 187-37>=149
    cohorts=0
    for a,q,t,center in product(range(2),range(p.Q),range(120,147),distant.CENTERS):primitive(a,q,t,center,p.Q);cohorts+=1
    nativecofs=0;nativesig=hashlib.sha256()
    for a,j in product(range(2),range(105,141)):
        for q in range(p.Q) if 126<=j<=139 else (0,):
            n=AbsorptionNet();cells={d:{f:[third_left_value(n,p,j+d,f,b,a,q) for b in range(p.k if f=='addr' else p.m)] if f in ('addr','age') else third_left_value(n,p,j+d,f,0,a,q) for f in NATIVE} for d in range(-5,9)}
            got=build(n,cells,p.k,p.m,Q=p.Q,nb=p.nb,radix=p.R,pos_bits=p.PB,service_force=0)
            assert got['f1']==int(112<=j<=140),(a,j,q,'F1')
            if j<=130:assert got['f2']==0,(a,j,q,'F2')
            nativecofs+=1;nativesig.update(f'{a},{j},{q},F1{int(j>=112)},F2{0 if j<=130 else "free"};'.encode())
    print(json.dumps(dict(third_native_all_GF_cofactors=nativecofs,GF_cohort_checks=cohorts)),flush=True)
    full=[]
    for a,j,q in product(range(2),range(105,141),(0,1023)):
        class Third(AbsorptionNet):
            def input(self,key):
                if isinstance(key,tuple) and len(key)==4 and key[0]=='x':
                    _,d,f,b=key
                    if f in NATIVE:return 0 if blocked(strips,j,d,phases[f,b],p.Q) else third_left_value(self,p,j+d,f,b,a,q)
                return super().input(key)
        n,_=proposed.full_net(p,Third)
        assert n.outputs['y','f1',0]==int(j>=112),(a,j,q,'fullF1')
        if j<=130:assert n.outputs['y','f2',0]==0,(a,j,q,'fullF2')
        full.append(dict(a=a,j=j,q=q,netlist_sha256=Compiled(n).digest))
    right=[]
    for j in range(149,187):
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
        assert n.outputs['y','f1',0]==int(j<=151) and n.outputs['y','f2',0]==0,(j,'right')
        right.append(dict(j=j,F1=int(j<=151),F2=0,netlist_sha256=Compiled(n).digest))
    aliases=[]
    for j,phase in product(range(105,160),(3,509,515,1021)):
        y=j*p.Q+phase;labels=[int(142*p.Q-512<=y-s<149*p.Q) for s in proposed.SLOTS];assert len(set(labels))==1
        virtual=(phase+512*labels[0])%p.Q;special=virtual in (3,1021)
        expected=(j<=141 or j>=149) if phase==3 else (142<=j<=148) if phase==509 else (141<=j<=148) if phase==515 else (j<=140 or j>=149)
        assert special==expected,(j,phase)
        aliases.append(dict(j=j,phase=phase,virtual_phase=virtual,special_write=special))
    f2free=[dict(physical_phase=3,colony=j) for j in range(131,142)]+[dict(physical_phase=515,colony=148)]
    deps=('SP31_OWN_RULE.md','SP31_FIRST_PULSE.md','SP31_SECOND_SOURCE_ENCLOSURE.md','SP31_PROTECTED_FOREIGN_AGE_BANK.md','SP31_SECOND_PULSE.md','SP31_SECOND_BANK_FOREIGN_SOURCES.md')
    receipts=('SP31_first_pulse_certificate.json','SP31_second_source_enclosure_certificate.json','SP31_second_pulse_certificate.json','SP31_second_bank_foreign_sources_certificate.json','SP31_encoded_certificate.json','SP31_symbolic_schedule.json','SP31_interface_certificate.json')
    result=dict(proposal='SP31',scope='Same actual J225 original-c16 native-only dense16Q real2/all initial upperInfo/no latererrors; full third native command enclosure only',
        Q=p.Q,U=p.U,T_wf=p.T_wf,candidate_sha256=c.digest(),netlist_sha256=c.comp.digest,
        checker_sha256=sha(__file__),proof_sha256=sha(PROOF),proposal_source_sha256=sha(proposed.__file__),
        listing_sha256=sha(listingpath),maintenance_source_sha256=hashlib.sha256(maintenance.encode()).hexdigest(),
        proof_dependencies_sha256={name:sha(PROOF.parent/name) for name in deps},receipt_dependencies_sha256={name:sha(OUT/name) for name in receipts},
        source_dependencies_sha256={str(path.relative_to(ROOT)):sha(path) for path in (ROOT/'gacsca/rule_g.py',ROOT/'gacsca/netlist.py',PROOF.parent/'proposed_distant_native448.py',PROOF.parent/'check_native_command1024_first_pulse.py',PROOF.parent/'check_native_command1024_second_source_enclosure.py',PROOF.parent/'unregistered_terminal/probe_sp30_symbolic_left_absorption.py',PROOF.parent/'unregistered_sp31_third_sources/probe_sp31_third_true_sources.py')},
        retained_exploration_assets_sha256={str(path.relative_to(ROOT)):sha(path) for path in sorted((OUT/'unregistered_sp31_third_sources').iterdir()) if path.is_file()},
        second_all128_trace_sha256=tracehashes,second_all128_GF_hulls=hulls,second_all_rows_checked=rowschecked,
        second_true_all_q_native_cofactors=bankcofs,second_native_cofactor_signature_sha256=sig.hexdigest(),
        selected_second_true_Workspace_full_cofactors=bankfull,proper_second_true_native_full_cofactors=properfull,
        actual24phase_ROM_keys=24*c.rom.shape[1],Hold_store_records=stores,recovered_true_zero_bank_records=recovered,
        actual_third_true_native_capture_routes=routechecks,all_GF_cohort_cases=cohorts,
        third_native_all_GF_cofactors=nativecofs,third_native_cofactor_signature_sha256=nativesig.hexdigest(),
        selected_third_left_full_cofactors=full,right_third_full_cofactors=right,selected_full_checks_measured_supplements=True,
        physical_alias_records=aliases,actual_third_source_time=2*p.U+p.T_wf,
        third_MF509_one_colonies=list(range(142,149)),third_MF1021_one_colonies=[*range(112,141),149,150,151],
        third_Flag2_free_source_bits=f2free,third_Flag2_enclosure_free_bits=len(f2free),third_source_enclosure_members=1<<len(f2free),
        actual_second_protected_true_Workspace0_banks_proved=True,actual_full_third_source_enclosure_proved=True,
        all_initial_upper_Info_allowed=True,no_future_tape_or_Workspace_or_controller_supplied=True,
        all_source_combinations_reachable_or_independent_proved=False,actual_third_pulse_proved=False,
        whole_upper_successor_or_repeated_bank_invariant_proved=False,general_higher_repair_or_positive_iid_or_minimum_change_proved=False,
        additional_rule_change=False,active_G17_modified=False,Gray_or_G17_refutation=False,global_reliability_established=False,
        seconds=time.monotonic()-start)
    (OUT/'SP31_third_source_enclosure_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(passed=True,second_all_rows_checked=rowschecked,second_true_all_q_native_cofactors=bankcofs,
        actual_third_true_native_capture_routes=routechecks,all_GF_cohort_cases=cohorts,third_native_all_GF_cofactors=nativecofs,
        actual_third_source_enclosure_proved=True,third_Flag2_enclosure_free_bits=len(f2free),third_pulse_proved=False,
        global_reliability_established=False,seconds=result['seconds'])),flush=True)
if __name__=='__main__':main()
