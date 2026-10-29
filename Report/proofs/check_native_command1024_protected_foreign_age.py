#!/usr/bin/env python3
"""Same-history eight foreign Age banks and seven-bit second F2 enclosure.

Written physical composition supplies the interpreter lift. This checker
replays the exact first-pulse observer without mutating prior assets,
checks constant whole-function outputs, actual stores/captures and all-q
maintenance cofactors. Selected full-net cofactors remain supplements.
"""
from concurrent.futures import ThreadPoolExecutor
from itertools import product
from pathlib import Path
import hashlib,importlib.util,json,subprocess,sys,tempfile,time
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/'Report/proofs/unregistered_terminal'))
from gacsca import rule_g
from gacsca.netlist import Net,Compiled,const_word
from probe_sp30_symbolic_left_absorption import AbsorptionNet
import proposed_native_command1024 as proposed
from check_native_command1024_first_pulse import blocked
OUT=ROOT/'figs/robustness';PROOF=Path(__file__).with_name('SP31_PROTECTED_FOREIGN_AGE_BANK.md')
OBSDIR=OUT/'unregistered_sp31_work_protection'
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def observer_replay():
    driver=PROOF.parent/'unregistered_sp31_second_pulse/probe_sp31_first_pulse_work_protection.py'
    spec=importlib.util.spec_from_file_location('readonly_work_observer',driver)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    original=PROOF.parent/'sp31_two_flag2_sources.c';source=original.read_text()
    assert sha(original)=='9dddb6a9661f801f7d625ba1560742aa3310d667dde2efa2f5f771a2f29479d4'
    marker='        append(next,a,b,v&31);events++;'
    assert source.count(marker)==1 and source.count('int main(int argc,char **argv)')==1
    observed=module.GLOBALS+source.replace(marker,module.OBSERVER+marker).replace(
        'int main(int argc,char **argv)','int first_pulse_main(int argc,char **argv)')+module.TAIL
    assert observed==(OBSDIR/'sp31_first_pulse_work_protection.c').read_text()
    receipt=json.loads((OBSDIR/'receipt.json').read_text());records=[]
    with tempfile.TemporaryDirectory(prefix='sp31-protected-age-') as tmp:
        tmp=Path(tmp);path=tmp/'sp31_first_pulse_work_protection.c';path.write_text(observed);binary=tmp/'observer'
        build=subprocess.run(['gcc','-O3','-std=c11','-Wall','-Wextra',str(path),'-o',str(binary)],capture_output=True,text=True)
        assert build.returncode==0 and build.stdout+build.stderr==(OBSDIR/'build.log').read_text()
        assert sha(binary)==receipt['binary_sha256']==sha(OBSDIR/'sp31_first_pulse_work_protection')
        def run(mask):
            trace=tmp/f'mask{mask}.jsonl'
            with trace.open('w') as fh:
                proc=subprocess.run([str(binary),str(mask),'6144'],stdout=fh,stderr=subprocess.PIPE,text=True)
            assert proc.returncode==0 and proc.stderr==(OBSDIR/f'mask{mask}_stderr.log').read_text()
            assert trace.read_bytes()==(OBSDIR/f'mask{mask}_trace.jsonl').read_bytes()
            lines=trace.read_text().splitlines();observer=json.loads(lines[-1])
            assert '\n'.join(lines[:-1])+'\n'==(OUT/'SP31_two_sources'/f'mask{mask}_trace.jsonl').read_text()
            rows=[json.loads(line) for line in lines[:-2]]
            assert len(rows)==6145 and [row['row'] for row in rows]==list(range(6145))
            assert observer['work_protection_observer']
            assert [r['h'] for r in observer['frames']]==list(range(135,143))
            assert observer['frames']==receipt['cases'][mask]['frames']
            assert all(r['bad_mask']==0 and r['checked_intervals']>0 for r in observer['frames'])
            record=dict(mask=mask,frames=observer['frames'],trace_sha256=sha(trace),
                original_trace_sha256=sha(OUT/'SP31_two_sources'/f'mask{mask}_trace.jsonl'),all_rows_exact=True)
            print(json.dumps(dict(readonly_observer_mask=mask,all_eight_frames_protected=True)),flush=True)
            return record
        with ThreadPoolExecutor(max_workers=4) as pool:records=list(pool.map(run,range(4)))
    return records

def age_value(n,p,s,b):
    if s<=134 or s>=146:return 0
    if s<=142:return (p.age_code(1)>>b)&1
    return n.input(('actual_partial_Age',s,b))

def main():
    started=time.monotonic();p=proposed.parameters();c=proposed.load_artifact()
    assert (p.Q,p.U,p.T_wf)==(1024,475136,278401)
    prior=json.loads((OUT/'SP31_second_source_enclosure_certificate.json').read_text())
    assert prior['candidate_sha256']==c.digest()
    assert prior['second_Flag2_enclosure_free_bits']==18 and prior['actual_second_Flag1_source_enclosure_proved']
    observations=observer_replay()
    class InitialForeign(Net):
        def input(self,key):
            if isinstance(key,tuple) and len(key)==4 and key[0]=='x' and key[2] in ('addr','age','f2','wf2'):
                return 0
            return super().input(key)
    n,_=proposed.full_net(p,InitialForeign);expected=dict(addr=0,age=p.age_code(1),f1=1,f2=0,wf1=0,wf2=0)
    bit_equalities=0
    for f,value in expected.items():
        width=dict(c.schema)[f]
        assert [n.outputs['y',f,b] for b in range(width)]==const_word(value,width),f
        bit_equalities+=width
    cofactor_digest=Compiled(n).digest;assert bit_equalities==33
    listing_path=OUT/'SP31_program_listing.json';listing=json.loads(listing_path.read_text());stores=[]
    S=p.T_wf+6144;phases=(*range(69,88),90,91)
    for phase in phases:
        rows=[r for r in listing if r[4]==phase and r[6]==rule_g.K_HOLD];assert len(rows)==1
        row=rows[0];column=row[1]+(row[3]<<p.logNP)
        assert np.flatnonzero(((c.rom[phase]>>2)&3)==rule_g.K_HOLD).tolist()==[column]
        issue=p.E0+row[1]*p.PL+row[2]
        assert S<issue<issue+2<382336<p.U-1
        stores.append(dict(phase=phase,ROM_column=column,input_issue_age=issue,materialized_age=issue+2))
    normal=set(c.layout);a,b=135*p.Q-512,146*p.Q;banks=[]
    for h,phase in product(range(135,143),phases):
        y=h*p.Q-512+phase
        assert phase in normal and a<=y-2-37 and y+2+37<b
        value=(p.age_code(1)>>(phase-69))&1 if phase<88 else 0
        banks.append(dict(foreign_frame=h,virtual_phase=phase,physical_primary=y,first_boundary_value=value))
    assert len(banks)==168 and sum(r['virtual_phase']<88 for r in banks)==152
    age_rows=[r for r in proposed.dependency_table(p) if r['field']=='age'];routes=[]
    assert [r['address'] for r in age_rows]==list(range(69,88))
    strips=((134*p.Q,a),(b-512,b))
    for h,row,gather in product(range(135,146),age_rows,p.gathers_q):
        for d in (0,*row['offsets']):
            s=h+d;phase=row['address']+512;y=(s-1)*p.Q+phase
            erased=blocked(strips,h-1,d,phase,p.Q)
            assert erased==(s<=134 or s>=146),(h,d,phase,erased)
            if d:assert gather*p.Q+abs(d)*(p.Q//8)+1<p.E0
            routes.append(dict(receiver=h,source=s,bit=row['bit'],gather=gather,
                source_primary=y,erased=erased,captured_value=0 if erased else
                (p.age_code(1)>>row['bit'])&1 if s<=142 else 'free'))
    build,maintenance_source=proposed.proposed_build();checks=0;sig=hashlib.sha256()
    for h,q in product(range(135,146),range(p.Q)):
        m=AbsorptionNet();cells={}
        for d in range(-5,9):
            s=h+d
            cells[d]=dict(addr=const_word(q if s==143 else 0,p.k),
                age=[age_value(m,p,s,k) for k in range(p.m)],
                f2=m.input(('actual_partial_F2',)) if s==143 else 0,
                **{f:m.input((f,s)) for f in ('f1','wf1','wf2')})
        got=build(m,cells,p.k,p.m,Q=p.Q,nb=p.nb,radix=p.R,pos_bits=p.PB,service_force=0)
        assert got['f1']==1 and got['f2']==0 and got['age_now']==const_word(p.age_code(1),p.m),(h,q)
        assert got['addr']==cells[0]['addr'],(h,q,'GF')
        checks+=1;sig.update(f'{h},{q},F1one,F2zero,Age1;'.encode())
    assert checks==11264
    print(json.dumps(dict(actual_maintenance_all_q_cofactors=checks,selected_left_Age_always1=True)),flush=True)
    selected=[]
    qvalues=(0,1,2,3,4,5,7,15,31,63,127,255,511,512,1022,1023)
    for h,q in product(range(135,146),qvalues):
        class Second(AbsorptionNet):
            def input(self,key):
                if isinstance(key,tuple) and len(key)==4 and key[0]=='x':
                    _,d,f,k=key;s=h+d
                    if f=='addr':return ((q if s==143 else 0)>>k)&1
                    if f=='age':return age_value(self,p,s,k)
                    if f=='f2':return self.input(('actual_partial_F2',)) if s==143 else 0
                return super().input(key)
        n,_=proposed.full_net(p,Second)
        assert n.outputs['y','f1',0]==1 and n.outputs['y','f2',0]==0,(h,q)
        assert [n.outputs['y','age',k] for k in range(p.m)]==const_word(p.age_code(2),p.m),(h,q,'Age2')
        selected.append(dict(receiver=h,q=q,netlist_sha256=Compiled(n).digest))
    remaining=[r for r in prior['second_Flag2_free_source_bits'] if r['physical_phase']!=515 or r['colony']==145]
    assert remaining==[dict(physical_phase=3,colony=j) for j in (124,130,131,132,133,134)]+[dict(physical_phase=515,colony=145)]
    observed_assets={str(path.relative_to(ROOT)):sha(path) for path in sorted(OBSDIR.iterdir()) if path.is_file()}
    dependencies=('SP31_first_pulse_certificate.json','SP31_second_source_enclosure_certificate.json',
        'SP31_second_enclosure_limit_certificate.json','SP31_encoded_certificate.json',
        'SP31_symbolic_schedule.json','SP31_front_certificate.json','SP31_interface_certificate.json')
    result=dict(proposal='SP31',scope='J232 same actual J225 history; eight protected first-period foreign Age1/WF0 banks and actual seven-bit second F2 enclosure; no second pulse',
        Q=p.Q,U=p.U,T_wf=p.T_wf,candidate_sha256=c.digest(),netlist_sha256=c.comp.digest,
        checker_sha256=sha(__file__),proof_sha256=sha(PROOF),proposal_source_sha256=sha(proposed.__file__),
        generated_source_sha256=hashlib.sha256(proposed.generated_source(p).encode()).hexdigest(),
        listing_sha256=sha(listing_path),maintenance_source_sha256=hashlib.sha256(maintenance_source.encode()).hexdigest(),
        proof_dependencies_sha256={name:sha(PROOF.parent/name) for name in
            ('SP31_OWN_RULE.md','SP31_FIRST_PULSE.md','SP31_SECOND_SOURCE_ENCLOSURE.md','SP31_SECOND_ENCLOSURE_LIMIT.md')},
        receipt_dependencies_sha256={name:sha(OUT/name) for name in dependencies},
        source_dependencies_sha256={str(path.relative_to(ROOT)):sha(path) for path in
            (ROOT/'gacsca/rule_g.py',ROOT/'gacsca/netlist.py',PROOF.parent/'proposed_distant_native448.py',
             PROOF.parent/'check_native_command1024_first_pulse.py',
             PROOF.parent/'unregistered_terminal/probe_sp30_symbolic_left_absorption.py',
             PROOF.parent/'unregistered_sp31_second_pulse/probe_sp31_first_pulse_work_protection.py',
             PROOF.parent/'sp31_two_flag2_sources.c')},
        retained_observer_assets_sha256=observed_assets,
        retained_observer_run_sha256=sha(OUT/'SP31_first_pulse_work_protection_exploration_run.log'),
        retained_initial_binary_filename_failure_assets_sha256={name:sha(OUT/name) for name in
            ('SP31_protected_foreign_age_initial_checker.py.txt','SP31_protected_foreign_age_initial_binary_filename_failure.log')},
        exact_readonly_work_observer_replays=observations,protected_complete_foreign_frames=list(range(135,143)),
        first_boundary_native_words=expected,constant_full_function_native_output_bits=bit_equalities,
        initial_foreign_native_cofactor_sha256=cofactor_digest,all_other_raw_inputs_and_I_free=True,
        actual21phase_ROM_keys=len(phases)*c.rom.shape[1],late_Hold_store_records=stores,
        actual_first_boundary_Age_Workspace_bank_records=banks,Age_primaries=152,Workspace_primaries=16,
        actual_second_Age_capture_route_records=routes,actual_second_Age_capture_routes=len(routes),
        actual_maintenance_all_q_cofactors=checks,maintenance_cofactor_signature_sha256=sig.hexdigest(),
        selected_full_F31_cofactors=selected,selected_full_F31_cofactor_count=len(selected),selected_full_net_checks_measured_only=True,
        all_eleven_selected_left_Age_words_one=True,all_eleven_complete_foreign_Flag2_commands_zero=True,
        second_MF515_proved_zero_colonies=list(range(134,145)),
        actual_second_source_time=p.U+p.T_wf,second_Flag2_free_source_bits=remaining,
        second_Flag2_enclosure_free_bits=len(remaining),actual_seven_bit_source_enclosure_proved=True,
        J231_all_eighteen_one_countercase_excluded_for_actual_history=True,
        no_future_tape_or_Workspace_or_controller_supplied=True,all_initial_upper_Info_allowed=True,
        additional_rule_change=False,active_G17_modified=False,numerical_whole_CA_trajectory_used=False,
        all_second_Flag2_values_determined=False,second_pulse_proved=False,
        repeated_bank_invariant_or_arbitrary_higher_repair_or_positive_iid_or_minimum_change_proved=False,
        Gray_or_G17_refutation=False,global_reliability_established=False,seconds=time.monotonic()-started)
    (OUT/'SP31_protected_foreign_age_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('actual_seven_bit_source_enclosure_proved',
        'second_Flag2_enclosure_free_bits','J231_all_eighteen_one_countercase_excluded_for_actual_history',
        'global_reliability_established','seconds')}),flush=True)
if __name__=='__main__':main()
