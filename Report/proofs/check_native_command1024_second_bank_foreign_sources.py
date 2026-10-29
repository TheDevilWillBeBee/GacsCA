#!/usr/bin/env python3
"""Actual F31 second banks/seven third foreign sources; no global theorem."""
from concurrent.futures import ThreadPoolExecutor
from itertools import product
from collections import Counter
from pathlib import Path
import hashlib,importlib.util,json,subprocess,sys,tempfile,time
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/'Report/proofs/unregistered_terminal'))
from gacsca import rule_g
from gacsca.netlist import Compiled,const_word
from probe_sp30_symbolic_left_absorption import AbsorptionNet
import proposed_native_command1024 as proposed
import check_native_command1024_protected_foreign_age as prior_age
from check_native_command1024_first_pulse import blocked
OUT=ROOT/'figs/robustness';OBS=OUT/'unregistered_sp31_second_work_protection'
PROOF=Path(__file__).with_name('SP31_SECOND_BANK_FOREIGN_SOURCES.md')
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def observer_replay():
    path=PROOF.parent/'unregistered_sp31_second_pulse/probe_sp31_second_pulse_work_protection.py'
    spec=importlib.util.spec_from_file_location('second_work_observer',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    factor=PROOF.parent/'sp31_two_flag2_sources.c'
    wrapper=path.parent/'sp31_second_enclosure_cases.c'
    marker='        append(next,a,b,v&31);events++;'
    src=factor.read_text().replace(marker,module.OBSERVER+marker).replace(
        'int main(int argc,char **argv)','int sp31_previous_first_pulse_main(int argc,char **argv)')
    second=wrapper.read_text().split('int main(int argc,char **argv)',1)[1]
    generated=module.GLOBALS+src+'\nint second_pulse_main(int argc,char **argv)'+second+module.TAIL
    assert generated==(OBS/'sp31_second_pulse_work_protection.c').read_text()
    receipt=json.loads((OBS/'receipt_all128.json').read_text())
    assert receipt['driver_sha256']==sha(path) and receipt['complete128_member_enclosure']
    assert receipt['frozen_factor_sha256']==sha(factor) and receipt['frozen_wrapper_sha256']==sha(wrapper)
    assert receipt['generated_C_source_sha256']==sha(OBS/'sp31_second_pulse_work_protection.c')
    assert receipt['binary_sha256']==sha(OBS/'sp31_second_pulse_work_protection')
    assert receipt['protected_frames_in_all_listed_cases']==list(range(142,146))
    assert [r['enclosure_mask'] for r in receipt['cases']]==list(range(128))
    total_rows=total_intervals=0
    for case in receipt['cases']:
        index=case['enclosure_mask'];mask=(index&63)|((index>>6)<<17)
        assert case['diagnostic18_mask']==mask and case['exact_old_trace_unchanged']
        trace=OBS/f'mask{index}_trace.jsonl'
        assert sha(trace)==case['trace_sha256']
        assert not (OBS/f'mask{index}_stderr.log').read_text()
        lines=trace.read_text().splitlines()
        old=OUT/'unregistered_sp31_seven_bit_second_pulse'/f'mask{index}_trace.jsonl'
        assert sha(old)==case['old_trace_sha256']
        assert '\n'.join(lines[:-1])+'\n'==old.read_text()
        records=[json.loads(line) for line in lines]
        assert len(records)==6147 and [r['row'] for r in records[:-2]]==list(range(6145))
        assert records[-2]['mask']==mask and records[-2]['exact_event_execution_complete']
        assert records[-1]['work_protection_observer'] and records[-1]['frames']==case['frames']
        assert [r['h'] for r in case['frames']]==list(range(142,146))
        assert all(r['bad_mask']==0 and r['checked_intervals']>0 for r in case['frames'])
        total_rows+=6145;total_intervals+=sum(r['checked_intervals'] for r in case['frames'])
    with tempfile.TemporaryDirectory(prefix='sp31-second-bank-') as tmp:
        tmp=Path(tmp);srcpath=tmp/'sp31_second_pulse_work_protection.c';srcpath.write_text(generated)
        binary=tmp/'observer';build=subprocess.run(['gcc','-O3','-std=c11','-Wall','-Wextra',str(srcpath),'-o',str(binary)],capture_output=True,text=True)
        assert build.returncode==0 and build.stdout+build.stderr==(OBS/'build.log').read_text()
        assert sha(binary)==receipt['binary_sha256']
        def run(index):
            mask=(index&63)|((index>>6)<<17);trace=tmp/f'mask{index}.jsonl'
            with trace.open('w') as fh:proc=subprocess.run([str(binary),str(mask),'6144'],stdout=fh,stderr=subprocess.PIPE,text=True)
            assert proc.returncode==0 and not proc.stderr
            assert trace.read_bytes()==(OBS/f'mask{index}_trace.jsonl').read_bytes()
            return dict(enclosure_mask=index,trace_sha256=sha(trace),all_rows_and_observer_equal=True)
        with ThreadPoolExecutor(max_workers=2) as pool:replays=list(pool.map(run,(0,127)))
    return receipt,replays,total_rows,total_intervals

def third_value(n,p,s,field,bit=0):
    if field=='addr':return ((n.q if s==143 else n.r if s==146 else 0)>>bit)&1
    if field=='age':
        if s<=141 or s>=149:return 0
        if s<=145:return (p.age_code(2)>>bit)&1
        return n.input(('free_third_Age',s,bit))
    if field=='f2':return n.input(('free_third_F2_146',)) if s==146 else 0
    if field=='wf2':return n.input(('free_third_WF2',s)) if 146<=s<=148 else 0
    return n.input(('free_third_'+field,s))

def main():
    start=time.monotonic();p=proposed.parameters();c=proposed.load_artifact()
    assert (p.Q,p.U,p.T_wf)==(1024,475136,278401)
    pulse=json.loads((OUT/'SP31_second_pulse_certificate.json').read_text())
    assert pulse['candidate_sha256']==c.digest() and pulse['actual_second_native_pulse_proved']
    assert pulse['endpoint_native_template']==[142,149]
    obs,replays,rows,intervals=observer_replay()
    build,maintenance_source=proposed.proposed_build();checks=0
    for h,q in product(range(142,146),range(p.Q)):
        n=AbsorptionNet();cells={}
        for d in range(-5,9):
            s=h+d;cells[d]=dict(addr=const_word(q if s==143 else 0,p.k),
                age=[prior_age.age_value(n,p,s,b) for b in range(p.m)],
                f2=n.input(('partial_second_F2',)) if s==143 else 0,
                **{f:n.input((f,s)) for f in ('f1','wf1','wf2')})
        got=build(n,cells,p.k,p.m,Q=p.Q,nb=p.nb,radix=p.R,pos_bits=p.PB,service_force=0)
        assert got['f1']==1 and got['f2']==0 and got['addr']==cells[0]['addr']
        assert got['age_now']==const_word(p.age_code(1),p.m)
        assert got['age']==const_word(p.age_code(2),p.m)
        checks+=1
    assert checks==4096
    listingpath=OUT/'SP31_program_listing.json';listing=json.loads(listingpath.read_text());stores=[]
    S=p.T_wf+6144;phases=(*range(59,92),*range(571,581),601)
    for phase in phases:
        values=[r for r in listing if r[4]==phase and r[6]==rule_g.K_HOLD];assert len(values)==1
        row=values[0];column=row[1]+(row[3]<<p.logNP)
        assert np.flatnonzero(((c.rom[phase]>>2)&3)==rule_g.K_HOLD).tolist()==[column]
        issue=p.E0+row[1]*p.PL+row[2]
        assert not p.T_wf<=issue+2<=S
        if phase in (*range(59,69),88,89):assert issue+2<p.T_wf
        else:assert S<issue<issue+2<382336<p.U-1
        stores.append(dict(phase=phase,ROM_column=column,input_issue_age=issue,materialized_age=issue+2))
    normal=set(c.layout);a,b=142*p.Q-512,149*p.Q;protected=[];gfbanks=[];f2banks=[]
    for h,phase in product(range(142,146),range(59,92)):
        y=h*p.Q-512+phase;assert phase in normal and a<=y-2-37 and y+2+37<b
        field='addr' if phase<69 else 'age' if phase<88 else {88:'f1',89:'f2',90:'wf1',91:'wf2'}[phase]
        value=('q_bit' if h==143 else 0) if field=='addr' else ((p.age_code(2)>>(phase-69))&1) if field=='age' else int(field=='f1')
        protected.append(dict(frame=h,phase=phase,field=field,primary=y,value=value))
    for h,k in product(range(142,150),range(10)):
        y=(h-1)*p.Q+571+k;assert a<=y-2-37 and y+2+37<b and 59+k in normal
        gfbanks.append(dict(frame=h,bit=k,primary=y,value='q_bit' if h==143 else 'r_bit' if h==146 else 0))
    for h in range(142,150):
        y=(h-1)*p.Q+601;assert a<=y-2-37 and y+2+37<b and 89 in normal
        f2banks.append(dict(frame=h,primary=y,value='free_bit' if h==146 else 0))
    strips=((141*p.Q,a),(b-512,b));routes=[]
    for h,row,gather in product(range(142,149),[r for r in proposed.dependency_table(p) if r['field'] in ('addr','age','f2','wf2')],p.gathers_q):
        phase=row['address']+512
        for d in (0,*row['offsets']):
            s=h+d;erased=blocked(strips,h-1,d,phase,p.Q)
            assert erased==(s<=141 or s>=149),(h,s,phase,erased)
            if d:assert gather*p.Q+abs(d)*(p.Q//8)+1<p.E0
            routes.append(dict(receiver=h,source=s,field=row['field'],bit=row['bit'],gather=gather,
                primary=(s-1)*p.Q+phase,erased=erased))
    primdir=OUT/'unregistered_sp31_second_bank_structure'
    primitive=json.loads((primdir/'primitive_receipt.json').read_text())
    primsource=PROOF.parent/'unregistered_sp31_second_pulse/sp31_two_exception_foreign_response.c'
    assert primitive['source_sha256']==sha(primsource)=='18c0899f13797c004dc64a9835bc4d57a14c10bb0d5673666a64f0d0f371c6b6'
    assert primitive['binary_sha256']==sha(primdir/'gf_response')
    run=subprocess.run([str(primdir/'gf_response')],capture_output=True,text=True)
    assert run.returncode==0 and run.stdout+run.stderr==(primdir/'primitive_run.log').read_text()
    assert json.loads(run.stdout)==primitive['result']
    assert primitive['result']['native_side_cases']==7340032
    pairs=((1,4),(1023,2),(1022,1),(1020,1023),(0,0),(0,3),(1021,0),(1023,1023))
    selected=[];selected_full=[]
    for h,(q,r) in product(range(142,149),pairs):
        n=AbsorptionNet();n.q=q;n.r=r
        cells={d:dict(addr=[third_value(n,p,h+d,'addr',k) for k in range(p.k)],
            age=[third_value(n,p,h+d,'age',k) for k in range(p.m)],
            **{f:third_value(n,p,h+d,f) for f in ('f1','f2','wf1','wf2')}) for d in range(-5,9)}
        got=build(n,cells,p.k,p.m,Q=p.Q,nb=p.nb,radix=p.R,pos_bits=p.PB,service_force=0)
        assert got['f1']==1 and got['f2']==0 and got['age_now']==const_word(p.age_code(2),p.m),(h,q,r)
        assert got['age']==const_word(p.age_code(3),p.m)
        left=[((q if h-d==143 else r if h-d==146 else 0)+d)%p.Q for d in range(1,6)]
        voted=next((v for v,count in Counter(left).items() if count>=3),q if h==143 else r if h==146 else 0)
        assert got['addr']==const_word(voted,p.k)
        selected.append(dict(receiver=h,q=q,r=r,GF=voted,Age=3,F1=1,F2=0))
        class Third(AbsorptionNet):
            def input(self,key):
                if isinstance(key,tuple) and len(key)==4 and key[0]=='x':
                    _,d,f,k=key
                    if f in ('addr','age','f2','wf2'):return third_value(self,p,h+d,f,k)
                return super().input(key)
        Third.q=q;Third.r=r
        n,_=proposed.full_net(p,Third)
        for f,value in dict(addr=voted,age=p.age_code(3),f1=1,f2=0,wf1=0,wf2=0).items():
            assert [n.outputs['y',f,k] for k in range(dict(c.schema)[f])]==const_word(value,dict(c.schema)[f]),(h,q,r,f)
        selected_full.append(dict(receiver=h,q=q,r=r,netlist_sha256=Compiled(n).digest))
    proofdeps=('SP31_OWN_RULE.md','SP31_FIRST_PULSE.md','SP31_ONE_EXCEPTION_BANK.md',
        'SP31_SECOND_SOURCE_ENCLOSURE.md','SP31_PROTECTED_FOREIGN_AGE_BANK.md','SP31_SECOND_PULSE.md')
    receiptdeps=('SP31_encoded_certificate.json','SP31_first_pulse_certificate.json','SP31_one_exception_bank_certificate.json',
        'SP31_second_source_enclosure_certificate.json','SP31_protected_foreign_age_certificate.json','SP31_second_pulse_certificate.json')
    result=dict(proposal='SP31',scope='Same actual J225 fault; four second Age2/native banks and two-exception GF bank yield seven third foreign F1one/F2zero sources; full third commands/pulse/global reliability unproved',
        Q=p.Q,U=p.U,T_wf=p.T_wf,candidate_sha256=c.digest(),netlist_sha256=c.comp.digest,
        checker_sha256=sha(__file__),proof_sha256=sha(PROOF),listing_sha256=sha(listingpath),
        maintenance_source_sha256=hashlib.sha256(maintenance_source.encode()).hexdigest(),
        proof_dependencies_sha256={name:sha(PROOF.parent/name) for name in proofdeps},
        receipt_dependencies_sha256={name:sha(OUT/name) for name in receiptdeps},
        source_dependencies_sha256={str(path.relative_to(ROOT)):sha(path) for path in
            (Path(proposed.__file__),Path(prior_age.__file__),ROOT/'gacsca/rule_g.py',ROOT/'gacsca/netlist.py',
             PROOF.parent/'proposed_distant_native448.py',PROOF.parent/'check_native_command1024_first_pulse.py',
             PROOF.parent/'unregistered_terminal/probe_sp30_symbolic_left_absorption.py',
             PROOF.parent/'unregistered_sp31_second_pulse/probe_sp31_second_pulse_work_protection.py',primsource)},
        retained_observer_assets_sha256={str(path.relative_to(ROOT)):sha(path) for path in sorted(OBS.iterdir()) if path.is_file()},
        retained_primitive_assets_sha256={str(path.relative_to(ROOT)):sha(path) for path in sorted(primdir.iterdir()) if path.is_file()},
        all128_old_traces_unchanged=True,observer_all_rows_checked=rows,observer_protected_event_intervals=intervals,
        exact_readonly_observer_replays=replays,protected_complete_foreign_frames=list(range(142,146)),
        protected_actual_second_native_bank_records=protected,protected_native_primaries=len(protected),
        second_actual_native_all_q_cofactors=checks,actual_ROM_store_keys=len(phases)*c.rom.shape[1],Hold_store_records=stores,
        actual_second_boundary_GF_bank_records=gfbanks,actual_second_boundary_Flag2_bank_records=f2banks,
        second_GF_exception_frames=[143,146],second_GF_bank_primaries=80,second_GF_zero_primaries=60,
        actual_third_capture_records=routes,actual_third_capture_routes=len(routes),primitive_full_GF_pair_result=primitive['result'],
        selected_maintenance_cofactors=selected,selected_full_F31_cofactors=selected_full,selected_checks_measured_supplements=True,
        second_boundary_time=2*p.U,third_source_time=2*p.U+p.T_wf,
        third_MF509_proved_one_colonies=list(range(142,149)),third_MF515_proved_zero_colonies=list(range(141,148)),
        actual_four_second_Age2_Workspace0_banks_proved=True,actual_two_exception_second_GF_bank_proved=True,
        actual_seven_third_foreign_Flag1_Flag2_commands_proved=True,
        no_future_tape_or_Workspace_or_controller_supplied=True,all_initial_upper_Info_allowed=True,
        full_third_source_enclosure_or_pulse_proved=False,complete_upper_successor_or_repeated_bank_invariant_proved=False,
        general_higher_repair_or_positive_iid_or_minimum_change_proved=False,additional_rule_change=False,
        active_G17_modified=False,Gray_or_G17_refutation=False,global_reliability_established=False,
        seconds=time.monotonic()-start)
    (OUT/'SP31_second_bank_foreign_sources_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(passed=True,observer_masks=128,observer_rows=rows,protected_frames=list(range(142,146)),
        protected_native_primaries=len(protected),all_q_native_cofactors=checks,complete_GF_pairs=1048576,
        selected_maintenance_cofactors=len(selected),selected_full_F31_cofactors=len(selected_full),
        actual_third_foreign_commands_proved=True,global_reliability_established=False,seconds=result['seconds'])),flush=True)
if __name__=='__main__':main()
