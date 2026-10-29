#!/usr/bin/env python3
"""F31 actual second Flag1 signal and conservative Flag2 source enclosure.

Also correct the historical J227 right-command coordinates. The frozen
rule and historical proof/checker/receipt are preserved. No second pulse
or globally reliable CA is asserted.
"""
from collections import Counter
from itertools import product
from pathlib import Path
import hashlib,json,sys,time
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/'Report/proofs/unregistered_terminal'))
from gacsca import rule_g
from gacsca.netlist import Net,Compiled,const_word
from probe_sp30_symbolic_left_absorption import AbsorptionNet
import proposed_native_command1024 as proposed
import proposed_distant_native448 as distant
from check_native_command1024_first_pulse import blocked
OUT=ROOT/'figs/robustness'
PROOF=Path(__file__).with_name('SP31_SECOND_SOURCE_ENCLOSURE.md')

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def left_value(n,p,col,f,b,q=None):
    if col<=126:
        value=col%p.Q if f=='addr' else p.age_code(1) if f=='age' else int(col in (124,125,126)) if f=='f1' else 0
        return (value>>b)&1
    if f=='addr':return n.input(('partialGF',b)) if col==127 and q is None else ((q>>b)&1) if col==127 else 0
    if f in ('f1','f2'):return n.input(('partial'+f,b)) if col==127 else 0
    return n.input(('upper',col,f,b))

def main():
    started=time.monotonic();p=proposed.parameters();c=proposed.load_artifact()
    assert (p.Q,p.U,p.T_wf)==(1024,475136,278401)
    historical_paths=('Report/proofs/SP31_ONE_EXCEPTION_BANK.md','Report/proofs/check_native_command1024_one_exception_bank.py',
        'figs/robustness/SP31_one_exception_bank_certificate.json','figs/robustness/SP31_one_exception_bank_run.log')
    expected=('b05919c8b8c882566c5cdc275eb3d7d911939071980bda3de59b85f02e2212ca',
        '48646338574b7fe6486372e22a86f73a1e062e2df26f712e7abdd05a3c54c11e',
        '2e9bcb1c1d7948c4b29a4fc2563664d457b0fb40145eb46cb896e2da44f0abc8',
        '82d79406b07b381a955198ce8a18efb9cc3b44a9cfff97abf3ebd842da608e88')
    historical={name:sha(ROOT/name) for name in historical_paths}
    assert tuple(historical.values())==expected
    oldbank=json.loads((OUT/'SP31_one_exception_bank_certificate.json').read_text())
    first=json.loads((OUT/'SP31_first_pulse_certificate.json').read_text())
    assert oldbank['candidate_sha256']==first['candidate_sha256']==c.digest()
    assert oldbank['same_actual_J225_first_boundary_one_exception_bank_proved']
    corrected=[]
    for row in oldbank['next_complete_foreign_frames']:
        h=row['virtual_colony'];origin=row['origin']
        assert origin==h*p.Q-512
        assert row['physical_MF509_primary']==(h-1)*p.Q+509 # retained erroneous receipt
        primary=origin+1021
        assert primary==h*p.Q+509 and primary-row['physical_MF509_primary']==p.Q
        corrected.append(dict(virtual_colony=h,origin=origin,Flag1=row['Flag1'],GF=row['GF'],
            physical_MF509_primary=primary,physical_colony=h))
    assert [r['physical_colony'] for r in corrected]==list(range(135,146))
    traces={};hulls=[]
    for mask in range(4):
        path=OUT/'SP31_two_sources'/f'mask{mask}_trace.jsonl'
        rows=[json.loads(line) for line in path.read_text().splitlines() if '"row"' in line]
        assert len(rows)==6145 and [r['row'] for r in rows]==list(range(6145))
        # Each recorded GF segment is an exact event interval, not an
        # endpoint approximation; J225 pins and verifies those runs.
        assert sha(path)==first['exact_four_runs'][mask]['trace_sha256']
        hull=(min(r['GF_left'] for r in rows),max(r['GF_right_exclusive'] for r in rows))
        assert hull==(128*p.Q-512,146*p.Q)
        traces[str(path.relative_to(ROOT))]=sha(path);hulls.append(list(hull))
    phases={(r['field'],r['bit']):r['address'] for r in proposed.dependency_table(p)}
    oldstrips=((127*p.Q,128*p.Q-512),(143*p.Q-512,143*p.Q))
    records=[];equalities=0
    for j in (*range(90,127),*range(146,182)):
        class First(AbsorptionNet):
            def input(self,key):
                if isinstance(key,tuple) and len(key)==4 and key[0]=='x':
                    _,d,f,b=key
                    if f=='addr':return ((0 if blocked(oldstrips,j,d,phases[f,b],p.Q) else (j+d)%p.Q)>>b)&1
                    if f in ('age','f1','f2','wf1','wf2'):return 0
                return super().input(key)
        n,_=proposed.full_net(p,First)
        expected_words=dict(addr=j%p.Q,age=p.age_code(1),f1=int(j in (124,125,126)),f2=0,wf1=0,wf2=0)
        for f,value in expected_words.items():
            width=dict(c.schema)[f]
            assert [n.outputs['y',f,b] for b in range(width)]==const_word(value,width),(j,f)
            equalities+=width
        records.append(dict(colony=j,**expected_words,netlist_sha256=Compiled(n).digest))
    assert len(records)==73 and 89+37<127 and 182-37>143
    # Both possible GF phases: native GF/F1/F2 stores are early, their
    # opposite-phase Hold stores occur after the same actual pulse settles.
    listing_path=OUT/'SP31_program_listing.json'
    assert sha(listing_path)==oldbank['listing_sha256']
    listing=json.loads(listing_path.read_text());issues=[]
    normalphases=(*range(59,69),88,89)
    for phase,shift in product(normalphases,(0,512)):
        actual=phase+shift;selected=[r for r in listing if r[4]==actual and r[6]==rule_g.K_HOLD]
        assert len(selected)==1;row=selected[0];column=row[1]+(row[3]<<p.logNP)
        assert np.flatnonzero(((c.rom[actual]>>2)&3)==rule_g.K_HOLD).tolist()==[column]
        age=p.E0+row[1]*p.PL+row[2]
        assert age+2<p.T_wf if shift==0 else age>p.T_wf+6144
        issues.append(dict(normal_phase=phase,phase_shift=shift,input_issue_age=age,materialized_age=age+2,ROM_column=column))
    recovered=[dict(colony=j,normal_phase=phase,primary=j*p.Q+phase)
        for j,phase in product(range(128,135),normalphases)]
    assert len(recovered)==84
    for row in recovered:
        y=row['primary'];assert 128*p.Q-512<=y-2 and y+2<143*p.Q and y+2<135*p.Q-512
    f2bank=[]
    for j in range(134,146):
        y=j*p.Q+601;assert 135*p.Q-512<=y-2-37 and y+2+37<146*p.Q
        f2bank.append(dict(colony=j,primary=y,first_boundary_value='r' if j==142 else 0,
            provenance='old_complete_foreign' if j<=141 else 'old_partial_foreign' if j==142 else 'newly_entered_true'))
    strips=((134*p.Q,135*p.Q-512),(146*p.Q-512,146*p.Q))
    foreign_f2_routes=0;foreign_f2_route_rows=[]
    f2row=next(row for row in proposed.dependency_table(p) if row['field']=='f2')
    assert f2row['address']==89
    for h,gather,d in product(range(135,146),p.gathers_q,(0,*f2row['offsets'])):
        source=(h+d-1)*p.Q+601
        crossed=blocked(strips,h-1,d,601,p.Q)
        inbank=135*p.Q-512<=source<146*p.Q
        if inbank:
            assert source in {r['primary'] for r in f2bank}
            if h+d==143:assert not crossed
        else:assert crossed
        if d!=0:assert gather*p.Q+abs(d)*(p.Q//8)+1<p.E0
        foreign_f2_route_rows.append(dict(frame=h,gather=gather,raw_offset=d,source=source,erased=crossed,
            captured_value='r' if h+d==143 else 0))
        foreign_f2_routes+=1
    routechecks=0;secondsources=[]
    nativefields=('addr','age','f1','f2','wf1','wf2')
    for j in (*range(90,134),*range(146,184)):
        for row in proposed.dependency_table(p):
            if row['field'] not in nativefields:continue
            for d in (0,*row['offsets']):
                erased=blocked(strips,j,d,row['address'],p.Q)
                assert erased==blocked(strips,j,d,59,p.Q)
                assert erased or (j+d<=133 if j<=133 else j+d>=146)
                routechecks+=1
        class Second(AbsorptionNet):
            def input(self,key):
                if isinstance(key,tuple) and len(key)==4 and key[0]=='x':
                    _,d,f,b=key;col=j+d
                    if f in nativefields:
                        if blocked(strips,j,d,phases[f,b],p.Q):return 0
                        if j<=133:return left_value(self,p,col,f,b)
                        value=col%p.Q if f=='addr' else p.age_code(1) if f=='age' else 0
                        return (value>>b)&1
                return super().input(key)
        n,_=proposed.full_net(p,Second)
        f1=n.outputs['y','f1',0];f2=n.outputs['y','f2',0]
        expect=int(118<=j<=133 or 146<=j<=148)
        if j not in (124,126):assert f1==expect,(j,f1,expect)
        if j not in (124,126,130,131,132,133):assert f2==0,(j,f2)
        secondsources.append(dict(colony=j,Flag1=expect,full_net_Flag1_constant=f1 if f1 in (0,1) else None,
            full_net_Flag2_constant=f2 if f2 in (0,1) else None,netlist_sha256=Compiled(n).digest))
    assert len(secondsources)==82 and 89+37<127 and 184-37>146
    print(json.dumps(dict(first_boundary_words=len(records),second_full_net_cofactors=len(secondsources))),flush=True)
    # Written joint-refinement cohort argument: any valid corner on a
    # canonical receiving raw cell returns that same GF/Age1; at127 or
    # above the two positive corners are invalid. The checker also exhausts
    # the GF count for every q/offset/corner touching the uncertain band.
    cohortchecks=0
    for q,t,center in product(range(p.Q),range(119,139),distant.CENTERS):
        vals=[];canonical=[]
        for v in range(-2,3):
            col=t+center+v
            gf=col%p.Q if col<=126 else q if col==127 else 0
            vals.append((gf-center-v)%p.Q)
            if col<=126:canonical.append(len(vals)-1)
        counts=Counter(vals)
        for word,count in counts.items():
            if count>=3:
                assert word==t%p.Q and any(vals[i]==word for i in canonical),(q,t,center)
        if t>=127 and center>0:assert max(counts.values())<=2
        cohortchecks+=1
    build,maintenance_source=proposed.proposed_build();nativeallq=0;selectedfull=0
    for j,q in product((124,125,126),range(p.Q)):
        n=AbsorptionNet();cells={}
        for d in range(-5,9):
            col=j+d
            cells[d]=dict(addr=[left_value(n,p,col,'addr',b,q) for b in range(p.k)],
                age=[left_value(n,p,col,'age',b,q) for b in range(p.m)],
                **{f:left_value(n,p,col,f,0,q) for f in ('f1','f2','wf1','wf2')})
        got=build(n,cells,p.k,p.m,Q=p.Q,nb=p.nb,radix=p.R,pos_bits=p.PB,service_force=0)
        assert got['f1']==1,(j,q)
        if j in (125,126):assert got['f2']==0,(j,q,'f2')
        nativeallq+=1
    assert nativeallq==3072
    for j,q in product((124,125,126),(0,1,2,3,4,5,7,15,31,63,127,255,511,512,1022,1023)):
        class Selected(AbsorptionNet):
            def input(self,key):
                if isinstance(key,tuple) and len(key)==4 and key[0]=='x':
                    _,d,f,b=key;col=j+d
                    if f in nativefields:
                        if blocked(strips,j,d,phases[f,b],p.Q):return 0
                        return left_value(self,p,col,f,b,q)
                return super().input(key)
        n,_=proposed.full_net(p,Selected)
        assert n.outputs['y','f1',0]==1,(j,q)
        if j in (125,126):assert n.outputs['y','f2',0]==0,(j,q,'fullf2')
        selectedfull+=1
    aliases=[]
    for j,phase in product(range(110,160),(3,509,515,1021)):
        y=j*p.Q+phase;labels=[int(135*p.Q-512<=y-s<146*p.Q) for s in proposed.SLOTS]
        assert len(set(labels))==1
        virtual=(phase+512*labels[0])%p.Q
        special=virtual in (3,1021)
        assert special==((j<=134 or j>=146) if phase==3 else
            (135<=j<=145) if phase==509 else (134<=j<=145) if phase==515 else (j<=133 or j>=146))
        aliases.append(dict(colony=j,physical_phase=phase,virtual_phase=virtual,special_write=special))
    f2free=[dict(physical_phase=3,colony=j) for j in (124,130,131,132,133,134)]
    f2free +=[dict(physical_phase=515,colony=j) for j in range(134,146)]
    result=dict(proposal='SP31',scope='J229 corrected J227 command coordinates, actual second Flag1 source enclosure and conservative Flag2 enclosure; no second pulse',
        Q=p.Q,U=p.U,T_wf=p.T_wf,candidate_sha256=c.digest(),netlist_sha256=c.comp.digest,
        checker_sha256=sha(__file__),proof_sha256=sha(PROOF),proposal_source_sha256=sha(proposed.__file__),
        generated_source_sha256=hashlib.sha256(proposed.generated_source(p).encode()).hexdigest(),
        listing_sha256=sha(listing_path),
        proof_dependencies_sha256={name:sha(PROOF.parent/name) for name in ('SP31_OWN_RULE.md','SP31_FIRST_PULSE.md')},
        maintenance_source_sha256=hashlib.sha256(maintenance_source.encode()).hexdigest(),
        historical_J227_assets_sha256=historical,historical_J227_coordinate_conclusion_withdrawn=True,
        retained_initial_parser_failure_assets_sha256={name:sha(OUT/name) for name in
            ('SP31_second_source_enclosure_initial_checker.py.txt','SP31_second_source_enclosure_initial_parser_failure.log',
             'SP31_second_source_enclosure_initial_tail_checker.py.txt','SP31_second_source_enclosure_initial_tail_failure.log',
             'SP31_second_source_enclosure_initial_cohort_checker.py.txt','SP31_second_source_enclosure_initial_cohort_failure.log')},
        retained_exploration_assets_sha256={str(path.relative_to(ROOT)):sha(path) for path in
            (Path(__file__).with_name('probe_native_command1024_second_sources.py'),OUT/'SP31_second_sources_exploration.json',OUT/'SP31_second_sources_exploration.log')},
        corrected_complete_foreign_frames=corrected,corrected_foreign_MF509_one_colonies=list(range(135,146)),
        actual_first_pulse_trace_sha256=traces,all_four_actual_GF_hulls=hulls,
        source_dependencies_sha256={str(Path(name).relative_to(ROOT)):sha(name) for name in
            (ROOT/'gacsca/rule_g.py',ROOT/'gacsca/netlist.py',ROOT/'Report/proofs/proposed_distant_native448.py',
             ROOT/'Report/proofs/check_native_command1024_first_pulse.py',ROOT/'Report/proofs/unregistered_terminal/probe_sp30_symbolic_left_absorption.py')},
        receipt_dependencies_sha256={name:sha(OUT/name) for name in ('SP31_first_pulse_certificate.json',
            'SP31_encoded_certificate.json','SP31_front_certificate.json','SP31_native_certificate.json','SP31_interface_certificate.json',
            'SP31_program_build.json','SP31_symbolic_schedule.json')},
        first_boundary_complete_true_words=records,first_boundary_constant_output_bit_equalities=equalities,
        actual_twentyfour_phase_ROM_keys=24*c.rom.shape[1],Hold_issue_records=issues,
        recovered_true_GF_Flag1_Flag2_zero_primaries=recovered,foreign_Flag2_bank=f2bank,
        actual_second_foreign_Flag2_capture_routes=foreign_f2_routes,foreign_Flag2_route_records=foreign_f2_route_rows,
        actual_second_native_gate_route_checks=routechecks,second_true_source_cofactors=secondsources,
        joint_refinement_all_q_GF_cohort_checks=cohortchecks,actual_maintenance_all_q_left_exception_cofactors=nativeallq,
        selected_full_F31_left_exception_cofactors=selectedfull,selected_full_F31_checks_measured_only=True,
        physical_alias_special_write_classes=aliases,actual_second_source_time=p.U+p.T_wf,
        second_MF509_one_colonies=list(range(135,146)),second_MF1021_proved_one_colonies=[*range(118,134),146,147,148],
        second_MF1021_other_colonies_zero=True,
        second_Flag2_free_source_bits=f2free,second_Flag2_enclosure_free_bits=len(f2free),
        all_unmentioned_captured_fields_and_I_free=True,no_independent_future_tape_or_Workspace_prescribed=True,
        actual_second_Flag1_source_enclosure_proved=True,actual_second_Flag2_source_enclosure_proved=True,
        additional_rule_change=False,active_G17_modified=False,numerical_whole_CA_trajectory_used=False,
        exact_full_second_Flag1_mask_proved=True,all_second_Flag2_values_determined=False,second_pulse_proved=False,
        repeated_bank_invariant_or_general_higher_repair_proved=False,positive_iid_epsilon_proved=False,
        smallest_globally_sufficient_change_proved=False,Gray_or_G17_refutation=False,global_reliability_established=False,
        seconds=time.monotonic()-started)
    (OUT/'SP31_second_source_enclosure_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('historical_J227_coordinate_conclusion_withdrawn',
        'corrected_foreign_MF509_one_colonies','actual_second_Flag1_source_enclosure_proved',
        'second_Flag2_enclosure_free_bits','global_reliability_established','seconds')}),flush=True)

if __name__=='__main__':main()
