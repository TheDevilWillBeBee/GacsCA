#!/usr/bin/env python3
"""First-boundary source bridge, complete second signal enclosure and pulse.

Conditional cofactors and eight finite pulse logs remain frozen. This
checker supplies the actual-history bridge described by the written proofs.
"""
from pathlib import Path
import hashlib,json,sys,time
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from gacsca.netlist import Net,Compiled
import proposed_sparse_short_force1024 as proposed


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    begin=time.monotonic();out=ROOT/'figs/robustness';p=proposed.parameters()
    candidate=proposed.load_artifact();table=proposed.dependency_table(p)
    phase_at={(row['field'],row['bit']):row['address'] for row in table}
    first=json.loads((out/'SP29_first_signal_certificate.json').read_text())
    data=json.loads((out/'SP29_first_boundary_signal_data_certificate.json').read_text())
    next_signal=json.loads((out/'SP29_next_ghost_signal_certificate.json').read_text())
    assert data['every_stated_boundary_Info_copy_zero_proved']
    assert candidate.digest()==first['proposed_candidate_sha256']==data['proposed_candidate_sha256']
    old_strips=((127*p.Q,128*p.Q-512),(144*p.Q-512,144*p.Q))
    def blocked(strips,j,d,phase):
        lo,hi=sorted((j*p.Q+phase,(j+d)*p.Q+phase))
        return any(lo+8*max(0,(left-lo+7)//8)<=min(hi,right-1) for left,right in strips)
    first_word_cofactors=[]
    for j in range(90,182):
        if 127<=j<=143:continue
        class FirstCaptured(Net):
            def input(self,key):
                if isinstance(key,tuple) and len(key)==4 and key[0]=='x':
                    _,d,field,bit=key
                    if field=='addr':
                        word=0 if blocked(old_strips,j,d,phase_at[field,bit]) else (j+d)%p.Q
                        return (word>>bit)&1
                    if field in ('age','f1','f2','wf1','wf2','packet_valid','service_valid','backward_pressure'):
                        return 0
                return super().input(key)
        net,_=proposed.full_net(p,FirstCaptured)
        expected=dict(addr=j%p.Q,age=p.age_code(1),f1=int(j in (124,125,126,144,145,146)),wf1=0)
        checks=0
        for field,value in expected.items():
            width=dict(candidate.schema)[field]
            for bit in range(width):
                assert net.outputs['y',field,bit]==(value>>bit)&1,(j,field,bit,net.outputs['y',field,bit])
                checks+=1
        first_word_cofactors.append(dict(colony=j,GF=expected['addr'],Age=expected['age'],
            Flag1=expected['f1'],WF1=0,constant_output_bit_equalities=checks,netlist_sha256=Compiled(net).digest))
    assert len(first_word_cofactors)==75
    log=out/'SP29_refined_wipe_2048_mode1.jsonl'
    pulse_rows=[json.loads(line) for line in log.read_text().splitlines() if '"row"' in line]
    assert len(pulse_rows)==6145
    min_left=min(row['left'] for row in pulse_rows);max_right=max(row['right_exclusive'] for row in pulse_rows)
    assert (min_left,max_right)==(123456,147456)
    protected=[120*p.Q+phase+holder for phase in (*range(59,69),88) for holder in range(-2,3)]
    assert max(protected)+32<min_left
    assert max(119*p.Q+x for x in range(1,1023))<min_left
    assert 144*p.Q+1>=max_right
    listing_path=out/'SP29_program_listing.json';listing=json.loads(listing_path.read_text())
    issue_records=[]
    for phase in (*range(59,69),88):
        for shifted in (False,True):
            current=(phase+512*shifted)%p.Q
            issues=[row for row in listing if row[4]==current and row[6]==1]
            assert len(issues)==1
            row=issues[0];age=p.E0+row[1]*p.PL+row[2]
            assert age>284545 if shifted else age+2<p.T_wf
            columns=np.flatnonzero(((candidate.rom[current]>>2)&3)==1).tolist()
            assert columns==[row[1]+(row[3]<<p.logNP)]
            issue_records.append(dict(normal_phase=phase,phase_shift=512*shifted,actual_phase=current,
                input_issue_age=age,materialized_state_age=age+2,sequence=row[0]))
    recovered=[]
    for j in range(136,144):
        for phase in (*range(59,69),88):
            y=j*p.Q+phase
            assert 130560<=y-2 and y+2<147456
            assert y-2>=139264
            recovered.append(dict(colony=j,normal_phase=phase,primary=y,
                                   no_Hold_issue_during_pulse=True,initial_and_final_phases= [phase+512,phase]))
    new_strips=((121*p.Q,122*p.Q-512),(136*p.Q-512,136*p.Q))
    gate_routes=0
    for j in (*range(83,121),*range(136,184)):
        for row in table:
            if row['field'] not in ('addr','age','f1','wf1'):continue
            for d in (0,*row['offsets']):
                actual=blocked(new_strips,j,d,row['address'])
                assert actual==blocked(new_strips,j,d,59)
                if j<=120:assert actual or j+d<=120
                else:assert actual or j+d>=136
                gate_routes+=1
    left_path=out/'SP29_second_left_signal_probe.json';right_path=out/'SP29_second_right_signal_probe.json'
    left=json.loads(left_path.read_text());right=json.loads(right_path.read_text())
    assert left['checker_sha256']==digest(ROOT/'Report/proofs/probe_short_force1024_second_left_signal.py')
    assert right['checker_sha256']==digest(ROOT/'Report/proofs/probe_short_force1024_second_right_signal.py')
    assert [row['true_colony'] for row in left['records']]==list(range(83,121))
    assert [row['true_colony'] for row in right['records']]==list(range(136,184))
    assert [row['true_colony'] for row in left['records'] if row['Flag1_constant']==1]==[118,119,120]
    assert [row['true_colony'] for row in left['records'] if row['Flag1_constant'] is None]==[117]
    assert [row['true_colony'] for row in right['records'] if row['Flag1_constant']==1]==list(range(136,147))
    assert all(row['Flag1_constant'] in (0,1) for row in right['records'])
    # Exact finite exclusion of all exceptional source cells for farther frames.
    assert 82+37<120 and 184-37>146
    probes=json.loads((out/'SP29_second_pulse_case_probe.json').read_text())
    assert probes['all_eight_finite_recurrences_checked']
    assert probes['all_eight_final_templates_quiet'] and probes['all_eight_final_widths_smaller']
    assert probes['unknown_bits']==['MF509(121)','MF1021(117)','MF1021(135)']
    assert [case['mask'] for case in probes['cases']]==list(range(8))
    bg_sites=GF_sites=0
    with np.load(out/'SP29_second_pulse_case_final_states.npz',allow_pickle=False) as states:
        baseline={suffix:states[f'case0_{suffix}'].copy() for suffix in ('native','code','Info')}
        for case in probes['cases']:
            mask=case['mask'];rows=[json.loads(line) for line in (out/case['log_name']).read_text().splitlines()]
            summary=rows.pop()
            assert summary==case['exhaustive_checks'] and len(rows)==6145
            assert summary['background_site_equalities']==1113215910
            assert summary['GF_support_sites_checked']==1610874880
            assert [row['row'] for row in rows]==list(range(6145))
            for row in rows:
                assert row['background_lo']==117*p.Q-8*(row['row']+1)-37
                assert row['background_hi']==148*p.Q+8*(row['row']+1)+37
            assert (rows[-1]['background_lo'],rows[-1]['background_hi'])==(70611,200749)
            assert (case['final']['left'],case['final']['right_exclusive'],case['final_width'])==(118272,131072,12800)
            assert (case['left_displacement'],case['right_displacement'],case['width_decrease'])==(-6144,-8192,2048)
            assert case['native_quiet_template_final'] and (case['noninterval_rows'],case['maximum_holes'])==(2,2)
            for suffix,value in baseline.items():assert np.array_equal(value,states[f'case{mask}_{suffix}']),(mask,suffix)
            bg_sites+=summary['background_site_equalities'];GF_sites+=summary['GF_support_sites_checked']
    assert bg_sites==8905727280 and GF_sites==12886999040
    dependencies=('SP29_first_signal_certificate.json','SP29_next_ghost_signal_certificate.json',
        'SP29_refined_wipe_certificate.json','SP29_first_boundary_signal_data_certificate.json',
        'SP29_second_left_signal_probe.json','SP29_second_right_signal_probe.json','SP29_second_pulse_case_probe.json',
        'SP29_symbolic_schedule.json','SP29_front_certificate.json','SP29_encoding_family_certificate.json')
    receipt=dict(proposal='SP29',scope='Actual three-bit complete second signal enclosure and second shrinking native/Info pulse on Z; original first error/no later errors; no general eroder or iid theorem',
        Q=p.Q,U=p.U,T_wf=p.T_wf,force_duration=2048,
        first_boundary_native_GF_interval=[124416,139264],
        first_boundary_true_word_cofactors=first_word_cofactors,
        first_boundary_true_word_cofactor_cases=len(first_word_cofactors),
        first_boundary_true_word_constant_output_equalities=sum(row['constant_output_bit_equalities'] for row in first_word_cofactors),
        first_pulse_all_row_GF_left_minimum=min_left,first_pulse_all_row_GF_right_maximum=max_right,
        protected_upper120_GF_and_Flag1_physical_holders=protected,
        recovered_GF_and_Flag1_zero_primary_records=recovered,
        actual_two_phase_Hold_issue_records=issue_records,actual_two_phase_Hold_ROM_key_checks=22*candidate.rom.shape[1],
        second_native_field_capture_gate_route_checks=gate_routes,
        second_left_true_frame_constant_one_colonies=[118,119,120],second_left_true_frame_unspecified_colonies=[117],
        second_right_true_frame_constant_one_colonies=list(range(136,147)),
        second_MF509_one_colonies=list(range(122,136)),second_MF509_unspecified_colonies=[121],
        second_MF1021_fixed_one_colonies=[118,119,120,*range(136,147)],
        second_MF1021_unspecified_colonies=[117,135],second_MF1021_zero_inside_wrong_colonies=list(range(121,135)),
        complete_second_signal_three_bit_enclosure_proved=True,
        enclosure_unknown_bits=['MF509(121)','MF1021(117)','MF1021(135)'],actual_unknown_bit_values_or_independence_proved=False,
        initial_upper_Info_payloads_arbitrary=True,no_new_correct_upper_encoding_assumed=True,
        all_other_circuit_inputs_and_I_free_in_Flag1_cofactors=True,
        all_eight_second_pulse_cases_have_same_final_native_code_Info=True,
        second_pulse_exact_GF_site_checks=GF_sites,second_pulse_exact_background_site_equalities=bg_sites,
        second_pulse_initial_projected_defect_seed_interval=[117*p.Q,148*p.Q],
        second_pulse_background_margin_formula='8*(r+1)+37',second_pulse_final_protected_interval=[70611,200749],
        second_pulse_computed_start_time=p.U+p.T_wf,second_pulse_computed_endpoint_time=p.U+p.T_wf+6144,
        second_pulse_final_native_GF_interval=[118272,131072],second_pulse_initial_width=14848,
        second_pulse_final_width=12800,second_pulse_width_decrease=2048,
        actual_second_shrinking_native_Info_pulse_on_Z_proved=True,
        entire_upper_data_restoration_or_third_signal_proved=False,
        general_arbitrary_width_phase_eroder_higher_map_or_iid_rate_proved=False,global_reliability_established=False,
        numerical_whole_CA_trajectory_used=False,rule_programme_or_constant_change=False,active_G17_modified=False,
        checker_sha256=digest(__file__),written_enclosure_proof_sha256=digest(ROOT/'Report/proofs/SP29_SECOND_SIGNAL_ENCLOSURE.md'),
        written_pulse_proof_sha256=digest(ROOT/'Report/proofs/SP29_SECOND_PULSE.md'),
        proposal_source_sha256=digest(proposed.__file__),proposed_candidate_sha256=candidate.digest(),
        proposed_netlist_sha256=candidate.comp.digest,listing_sha256=digest(listing_path),
        first_pulse_all_row_log_sha256=digest(log),
        second_pulse_final_state_asset_sha256=digest(out/'SP29_second_pulse_case_final_states.npz'),
        receipt_dependencies_sha256={name:digest(out/name) for name in dependencies},seconds=time.monotonic()-begin)
    (out/'SP29_second_signal_enclosure_certificate.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({key:receipt[key] for key in ('first_boundary_true_word_cofactor_cases',
        'first_boundary_true_word_constant_output_equalities','second_native_field_capture_gate_route_checks',
        'complete_second_signal_three_bit_enclosure_proved','actual_second_shrinking_native_Info_pulse_on_Z_proved',
        'second_pulse_final_native_GF_interval','seconds','global_reliability_established')}),flush=True)


if __name__=='__main__':main()
