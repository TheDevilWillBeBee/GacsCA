#!/usr/bin/env python3
"""Actual fourth F31 command enclosure; reachability/pulse/iid unproved."""
from collections import Counter
from contextlib import redirect_stdout
from itertools import product
from pathlib import Path
import hashlib,io,json,sys,tempfile,time
import numpy as np

ROOT=Path(__file__).resolve().parents[2];S=ROOT/'Report/proofs';OUT=ROOT/'figs/robustness'
sys.path[:0]=[str(ROOT),str(S),str(S/'unregistered_terminal'),str(S/'unregistered_sp31_fourth_enclosure')]
from gacsca.netlist import Compiled,const_word
from probe_sp30_symbolic_left_absorption import AbsorptionNet
from check_native_command1024_first_pulse import blocked
import probe_sp31_fourth_enclosure as explore
import proposed_native_command1024 as proposed

PROOF=S/'SP31_FOURTH_SOURCE_ENCLOSURE.md'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def native_side_counts(p):
    count=0;signature=hashlib.sha256()
    for a,j,sign in product(range(2),range(96,148),(-1,1)):
        sources=[j+sign*d for d in range(1,6)]
        free=[s for s in sources if s in (134,141)];assert len(free)<=1
        for q in range(p.Q) if free else (0,):
            raw=[s%p.Q if s<=132 else 133*a if s==133 else q if s in (134,141) else 0 for s in sources]
            votes=Counter((word+j-s)%p.Q for word,s in zip(raw,sources))
            quorum=[word for word,n in votes.items() if n>=3]
            assert len(quorum)<=1 and (not quorum or quorum==[j%p.Q])
            if sign==1:
                if j<=129:assert quorum==[j%p.Q]
                if j>=132:assert not quorum
                if quorum and j>=106:assert sum(112<=s<=140 for s in range(j+1,j+9))>=3
                if j<=105:assert sum(112<=s<=140 for s in range(j+1,j+9))<=2
            count+=1;signature.update(f'{a},{j},{sign},{q},{bool(quorum)};'.encode())
    return dict(cases=count,signature_sha256=signature.hexdigest())

def main():
    start=time.monotonic();p=proposed.parameters();c=proposed.load_artifact()
    banks=json.loads((OUT/'SP31_third_boundary_banks_certificate.json').read_text())
    third=json.loads((OUT/'SP31_third_pulse_certificate.json').read_text())
    assert (p.Q,p.U,p.T_wf)==(1024,475136,278401)
    assert c.digest()==banks['candidate_sha256']==third['candidate_sha256']
    assert banks['actual_protected_third_true_native_banks_proved'] and banks['actual_recovered_true_GF_F1_F2_zero_banks_proved']
    assert banks['actual_one_exception_third_foreign_GF_F2_banks_proved']
    assert third['actual_third_native_boundary_and807_private_alias_zero_reset_proved']
    path=OUT/'unregistered_sp31_fourth_enclosure/cofactor_receipt.json'
    retained=json.loads(path.read_text());assert retained['probe_sha256']==sha(explore.__file__)
    with tempfile.TemporaryDirectory(prefix='sp31-fourth-cofactor-') as tmp:
        explore.OUT=Path(tmp);captured=io.StringIO()
        with redirect_stdout(captured):explore.main()
        replay=json.loads((Path(tmp)/'cofactor_receipt.json').read_text())
        for key in retained:
            if key!='seconds':assert replay[key]==retained[key],key
    print(json.dumps(dict(readonly_cofactor_replay_equal=True,selected_native_cofactors=len(retained['selected_native_cofactors']),GF_cohort_cases=retained['GF_cohort_cases'])),flush=True)
    side=native_side_counts(p)
    strips=((148*p.Q,149*p.Q-512),(152*p.Q-512,152*p.Q))
    table=[r for r in proposed.dependency_table(p) if r['field'] in explore.NATIVE]
    phases={(r['field'],r['bit']):r['address'] for r in table}
    routes=[]
    for j,row,gather in product((*range(96,148),*range(152,191)),table,p.gathers_q):
        phase=row['address']
        for d in (0,*row['offsets']):
            erased=blocked(strips,j,d,phase,p.Q)
            assert erased==(j+d>=148 if j<=147 else j+d<=151),(j,d,phase)
            if d:assert gather*p.Q+abs(d)*(p.Q//8)+1<p.E0
            routes.append(dict(frame=j,field=row['field'],bit=row['bit'],offset=d,gather=gather,erased=erased))
    foreignroutes=[]
    for h,row,gather in product(range(149,152),table,p.gathers_q):
        phase=row['address']+512
        for d in (0,*row['offsets']):
            erased=blocked(strips,h-1,d,phase,p.Q)
            assert erased==(h+d<=148 or h+d>=152),(h,d,phase)
            if d:assert gather*p.Q+abs(d)*(p.Q//8)+1<p.E0
            foreignroutes.append(dict(frame=h,field=row['field'],bit=row['bit'],offset=d,gather=gather,erased=erased))
    right=[]
    for j in range(152,191):
        class Right(AbsorptionNet):
            def input(self,key):
                if isinstance(key,tuple) and len(key)==4 and key[0]=='x':
                    _,d,f,b=key
                    if f in explore.NATIVE:
                        if blocked(strips,j,d,phases[f,b],p.Q):return 0
                        value=(j+d)%p.Q if f=='addr' else p.age_code(3) if f=='age' else 0
                        return (value>>b)&1
                return super().input(key)
        n,_=proposed.full_net(p,Right)
        assert n.outputs['y','f1',0]==int(j<=154) and n.outputs['y','f2',0]==0,(j,'right')
        right.append(dict(j=j,Flag1=int(j<=154),Flag2=0,netlist_sha256=Compiled(n).digest))
    assert 95+37<=132 and 191-37>=152
    aliases=[]
    for j,phase in product(range(96,161),(3,509,515,1021)):
        y=j*p.Q+phase;labels=[int(149*p.Q-512<=y-s<152*p.Q) for s in proposed.SLOTS]
        assert len(set(labels))==1
        virtual=(phase+512*labels[0])%p.Q;special=virtual in (3,1021)
        expected=(j<=148 or j>=152) if phase==3 else (149<=j<=151) if phase==509 else (148<=j<=151) if phase==515 else (j<=147 or j>=152)
        assert special==expected,(j,phase)
        aliases.append(dict(j=j,physical_phase=phase,virtual_phase=virtual,special_write=special))
    cornerspath=OUT/'unregistered_sp31_fourth_sources/pulse_corners/receipt.json';corners=json.loads(cornerspath.read_text())
    assert corners['free_bits']==21 and corners['initial_template']==[149,152]
    assert corners['frozen_factor_sha256']==sha(S/'sp31_two_flag2_sources.c')
    assets={}
    for case in corners['cases']:
        mask=case['mask'];trace=cornerspath.parent/f'mask{mask}_trace.jsonl';stderr=cornerspath.parent/f'mask{mask}_stderr.log'
        assert sha(trace)==case['trace_sha256'] and sha(stderr)==case['stderr_sha256']
        records=[json.loads(line) for line in trace.read_text().splitlines()]
        assert len(records)==6146 and [r['row'] for r in records[:-1]]==list(range(6145))
        assert records[-1]==case['endpoint'] and records[-2]==case['final_row']
        assert case['final_row']['GF_sites']==(9728 if mask==2097151 else 3584)
        assert not case['endpoint']['physical_reachability_of_mask_proved']
        assets[str(trace.relative_to(ROOT))]=sha(trace);assets[str(stderr.relative_to(ROOT))]=sha(stderr)
    free=[dict(physical_phase=3,colony=j) for j in range(132,149)]+[dict(physical_phase=515,colony=j) for j in range(148,152)]
    result=dict(proposal='SP31',scope='Same actual J225 original-c16 native-only dense16Q real2/all original upperInfo/no latererrors; complete actual fourth21bit source enclosure only',
        Q=p.Q,U=p.U,T_wf=p.T_wf,radius=37,candidate_sha256=c.digest(),netlist_sha256=c.comp.digest,
        proof_sha256=sha(PROOF),checker_sha256=sha(__file__),exploration_receipt_sha256=sha(path),
        proof_dependencies_sha256={name:sha(S/name) for name in ('SP31_OWN_RULE.md','SP31_FIRST_PULSE.md','SP31_THIRD_SOURCE_ENCLOSURE.md','SP31_THIRD_PULSE.md','SP31_THIRD_BOUNDARY_BANKS.md')},
        receipt_dependencies_sha256={name:sha(OUT/name) for name in ('SP31_third_pulse_certificate.json','SP31_third_boundary_banks_certificate.json','SP31_encoded_certificate.json','SP31_symbolic_schedule.json','SP31_interface_certificate.json')},
        source_dependencies_sha256={str(Path(name).relative_to(ROOT)):sha(name) for name in (proposed.__file__,explore.__file__,S/'check_native_command1024_first_pulse.py',S/'unregistered_terminal/probe_sp30_symbolic_left_absorption.py',ROOT/'gacsca/rule_g.py',ROOT/'gacsca/netlist.py',S/'proposed_distant_native448.py',S/'sp31_two_flag2_sources.c')},
        retained_exploration_assets_sha256={str(name.relative_to(ROOT)):sha(name) for name in (path,OUT/'unregistered_sp31_fourth_enclosure_cofactor_run.log')},
        readonly_all_cofactor_replay_equal=True,selected_left_native_cofactors=936,GF_cohort_cases=82528,
        selected_left_full_cofactors=176,foreign_all_q_native_cofactors=3072,native_GF_side_quorums=side,
        selected_cofactors_measured_supplements=True,actual_true_capture_routes=len(routes),actual_foreign_capture_routes=len(foreignroutes),
        actual_capture_route_signature_sha256=hashlib.sha256(json.dumps([routes,foreignroutes],sort_keys=True,separators=(',',':')).encode()).hexdigest(),
        right_full_cofactors=right,physical_alias_records=aliases,actual_fourth_source_time=3*p.U+p.T_wf,
        fourth_MF509_one_colonies=list(range(149,152)),fourth_MF1021_one_colonies=[*range(106,148),152,153,154],
        fourth_Flag2_free_source_bits=free,fourth_source_enclosure_free_bits=len(free),fourth_source_enclosure_members=1<<len(free),
        actual_full_fourth_source_enclosure_proved=True,all_initial_upper_Info_allowed=True,
        no_future_tape_or_Workspace_or_controller_supplied=True,additional_rule_change=False,active_G17_modified=False,
        finite_quotient_corner_receipt_sha256=sha(cornerspath),retained_finite_corner_assets_sha256=assets,
        finite_quotient_corners_measured_only=True,all_enclosure_members_native_GF_shrink=False,
        individual_mask_reachability_or_independence_proved=False,actual_fourth_native_pulse_or_boundary_proved=False,
        current_foreign_Age_Workspace_banks_characterized=False,
        whole_upper_successor_or_arbitrary_higher_repair_or_positive_iid_or_minimum_change_proved=False,
        Gray_or_G17_refutation=False,global_reliability_established=False,seconds=time.monotonic()-start)
    (OUT/'SP31_fourth_source_enclosure_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(passed=True,actual_fourth_source_enclosure_proved=True,free_bits=len(free),GF_cohort_cases=82528,native_GF_side_cases=side['cases'],actual_true_capture_routes=len(routes),actual_foreign_capture_routes=len(foreignroutes),right_full_cofactors=len(right),actual_fourth_pulse_proved=False,global_reliability_established=False,seconds=result['seconds'])),flush=True)
if __name__=='__main__':main()
