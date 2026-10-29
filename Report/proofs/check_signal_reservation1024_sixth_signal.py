#!/usr/bin/env python3
"""SP30 sixth actual signal/translating pulse; terminal/iid still open."""
from itertools import product
from pathlib import Path
from types import FunctionType
import hashlib,json,sys,time
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(Path(__file__).resolve().parent/'unregistered_terminal'))
import proposed_sparse_signal_reservation1024 as proposed
import probe_sp30_sixth_signal as probe
import probe_sp30_sixth_pulse_domains as driver
import check_short_force1024_GF_bank_closure as bank
from gacsca import rule_g


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    start=time.monotonic();p=proposed.parameters();c=proposed.load_artifact()
    out=ROOT/'figs/robustness';dest=out/'unregistered_sixth'
    prior=json.loads((out/'SP30_fifth_signal_certificate.json').read_text())
    signal=json.loads((dest/'signal_receipt.json').read_text());domain=json.loads((dest/'pulse_receipt.json').read_text())
    primitive=json.loads((out/'SP29_third_domain_pulse_certificate.json').read_text())
    assert prior['actual_fifth_shrinking_projected_pulse_on_Z_proved']
    assert prior['actual_fifth_bank_and_sixth_complete_foreign_sources_proved']
    assert c.digest()==prior['proposed_candidate_sha256']==signal['proposed_candidate_sha256']
    assert c.comp.digest==signal['proposed_netlist_sha256']
    assert signal['checker_sha256']==digest(probe.__file__)
    assert signal['prior_fifth_certificate_sha256']==digest(out/'SP30_fifth_signal_certificate.json')
    assert signal['all_H2_Info_unmentioned_native_private_fields_and_instruction_inputs_free']
    assert not signal['actual_fifth_boundary_or_sixth_signal_or_pulse_or_terminal_history_proved']
    result=probe.calculate();assert result==signal['results']
    source=result['fifth_boundary_native_source_cofactors'];left=[r for r in source if r['colony']<=96];right=[r for r in source if r['colony']>=112]
    assert (len(left),len(right),result['native_left_constant_bit_equalities'],result['native_right_constant_bit_equalities'],result['native_constant_bit_equalities'])==(32,92,992,1673,2665)
    for r in left:assert r['constant_output_words']==dict(addr=r['colony'],age=p.age_code(5),f1=0,wf1=0)
    for r in right:
        j=r['colony'];expected=(dict(addr=0,age=None,f1=1,wf1=0) if j<=125 else
            dict(addr=None,age=None,f1=None,wf1=None) if j<=152 else
            dict(addr=j,age=None,f1=None,wf1=0) if j<=159 or 162<=j<=165 else
            dict(addr=j,age=p.age_code(5),f1=0,wf1=0))
        assert r['constant_output_words']==expected,(j,r['constant_output_words'])
    oldrows=[json.loads(line) for line in (out/'SP30_fifth_pulse_domains.jsonl').read_text().splitlines()];oldrows.pop()
    hull=[min(r['left'] for r in oldrows),max(r['right_exclusive'] for r in oldrows)]
    assert hull==[98880,114688]
    assert prior['domain_assets_sha256']['SP30_fifth_pulse_domains.jsonl']==digest(out/'SP30_fifth_pulse_domains.jsonl')
    protected=[96*p.Q+phase+s for phase in (*range(59,69),88) for s in proposed.SLOTS]
    assert max(protected)+37==98431<98880
    assert 95*p.Q+1022<98880 and 112*p.Q+1>114688
    assert 64+37<102 and 204-37>152 and 58+37<96 and 216-37>165
    listing=json.loads((out/'SP30_program_listing.json').read_text());issues=[];keys=0
    for phase,shift in product((*range(59,69),88),(0,512)):
        actual=phase+shift;selected=[r for r in listing if r[4]==actual and r[6]==rule_g.K_HOLD];assert len(selected)==1
        row=selected[0];column=row[1]+(row[3]<<p.logNP);age=p.E0+row[1]*p.PL+row[2]
        assert np.flatnonzero(((c.rom[actual]>>2)&3)==rule_g.K_HOLD).tolist()==[column]
        assert age+2<p.T_wf if shift==0 else age>p.T_wf+6144
        issues.append(dict(phase=actual,input_issue_age=age,materialized_age=age+2,ROM_column=column));keys+=c.rom.shape[1]
    assert keys==90112
    recovered=[]
    for j,phase in product(range(104,112),(*range(59,69),88)):
        y=j*p.Q+phase;assert 105984<=y-2 and y+2<114688 and y-2>=106496
        recovered.append(dict(colony=j,normal_phase=phase,primary=y))
    assert len(recovered)*5==440
    mask=(set(range(58,901))-{509,515})|{901,902,965}
    for phase,shift,s in product((3,509,515,1021),(0,512),proposed.SLOTS):
        assert ((phase-s+shift)%p.Q+s)%p.Q not in mask
    aliases=[]
    for j,phase in product(range(82,190),(509,1021)):
        y=j*p.Q+phase;labels=[int(99840<=y-s<106496) for s in proposed.SLOTS];assert len(set(labels))==1
        virtual=(phase+512*labels[0])%p.Q;active=virtual==1021
        assert active==((98<=j<=103) if phase==509 else (j<=96 or j>=104))
        aliases.append(dict(colony=j,physical_phase=phase,virtual_primary=virtual,special_write=active))
    assert [r['virtual_primary'] for r in aliases if (r['colony'],r['physical_phase']) in ((97,509),(103,1021))]==[509,509]
    ones=[94,95,96,*range(104,121)];optional=[93,*range(121,179)]
    assert result['sixth_MF1021_fixed_one_colonies']==ones and result['sixth_MF1021_unspecified_colonies']==optional
    assert len(result['sixth_true_Flag1_cofactors'])==150 and result['sixth_native_capture_routes']==285750
    assert (result['optional_bit_count'],result['concrete_enclosure_masks'])==(59,1<<59)
    assert domain['checker_sha256']==digest(driver.__file__) and domain['signal_receipt_sha256']==digest(dest/'signal_receipt.json')
    assert domain['finite_domain_recurrence_complete'] and domain['exit_code']==0 and domain['first_unresolved_GF'] is None
    assert not domain['actual_sixth_signal_pulse_or_terminal_history_or_general_eroder_proved']
    for key,path in (('inherited_wrapper_sha256',out/'SP30_fifth_pulse_domains_generated.c'),
        ('frozen_factor_sha256',out/'SP29_third_pulse_domains_factor_generated.c'),
        ('wrapper_sha256',dest/'pulse_generated.c'),('run_log_sha256',dest/'pulse.jsonl'),('endpoint_asset_sha256',dest/'endpoint.npz')):
        assert domain[key]==digest(path)
    assert domain['frozen_factor_sha256']==primitive['domain_factor_C_source_sha256']
    assert primitive['actual_domain_inclusion_proved_by_induction']
    assert (primitive['domain_primitive_set_image_checks'],primitive['domain_GF_selector_set_image_checks'])==(1062,36)
    assert (dest/'pulse_generated.c').read_text()==driver.expected_wrapper(result)
    rows=[json.loads(line) for line in (dest/'pulse.jsonl').read_text().splitlines()];summary=rows.pop()
    assert summary==domain['summary'] and summary['certificate_complete']
    assert len(rows)==summary['rows_checked']==6145 and [r['row'] for r in rows]==list(range(6145))
    assert summary['GF_support_sites_checked']==1610874880
    equalities=sum(262144-r['background_hi']+r['background_lo'] for r in rows);assert summary['background_site_equalities']==equalities
    for r in rows:
        assert r['background_lo']==93*p.Q-8*(r['row']+1)-37 and r['background_hi']==180*p.Q+8*(r['row']+1)+37
        assert 17*p.Q<r['background_lo'] and r['background_hi']<262144-37
    assert domain['endpoint']==dict(wrong_GF_interval=[93696,100352],width=6656,width_decrease=0,native_quiet_template=True,template_L_R=[92,98])
    assert domain['final_protected_interval']==[46035,233517]
    pulse_hull=[min(r['left'] for r in rows),max(r['right_exclusive'] for r in rows)]
    retained=list(range(121,179))
    with np.load(dest/'endpoint.npz',allow_pickle=False) as a:
        x=np.arange(262144);assert np.array_equal(a['native'][0],(93696<=x)&(x<100352))
        assert np.array_equal(a['native'][1],((93184<=x)&(x<93696))|((99840<=x)&(x<100352)))
        assert not a['native'][2:].any() and not a['code'].any() and not a['Info'][509::1024].any()
        assert np.flatnonzero(a['Info']==1).tolist()==[j*p.Q+1021 for j in range(104,121)]
        assert np.flatnonzero(a['Info']==2).tolist()==[j*p.Q+1021 for j in retained]
        assert not a['Info'][93*p.Q+1021]
    assert 92<=98 and 98<=104-1 and 92<98
    targets=[];true=foreign=0
    for j,bit in product(range(91,98),range(10)):
        y=j*p.Q+571+bit;assert 93696<=y-2-37 and y+2+37<100352
        if j<97:
            assert y+2<99840;origin=None;true+=1
        else:
            origin=98*p.Q-512;assert 99840<=origin and origin+p.Q<=106496
            assert y-origin==59+bit;foreign+=1
        targets.append(dict(primary=y,bit=bit,previous_complete_foreign_origin=origin))
    assert (len(targets)*5,true,foreign)==(350,60,10)
    routes=FunctionType(bank.routes.__code__,dict(bank.__dict__,proposed=proposed),'routes')(p,92,98)
    assert (routes['routes'],routes['direct_checks'])==(11700,180)
    failure=json.loads((dest/'initial_signal_driver_failure.json').read_text())
    for name,value in failure['assets_sha256'].items():assert digest(dest/name)==value
    assert not failure['rule_equations_or_cofactors_changed'] and not failure['actual_history_or_global_reliability_proved']
    forecast=json.loads((dest/'unexecuted_shrinking_forecast_manifest.json').read_text())
    assert forecast['draft_source_sha256']==digest(dest/'unexecuted_sixth_shrinking_forecast_checker.py.txt')
    assert forecast['prepared_domain_receipt_sha256']==digest(dest/'pulse_receipt.json')
    assert not forecast['draft_executed'] and not forecast['rule_equations_or_domain_results_changed']
    assert not forecast['global_reliability_established']
    sources=('gacsca/rule_g.py','gacsca/netlist.py','Report/proofs/unregistered_terminal/probe_sp30_sixth_signal.py',
        'Report/proofs/unregistered_terminal/probe_sp30_sixth_pulse_domains.py','Report/proofs/check_signal_reservation1024_second_signal.py',
        'Report/proofs/check_short_force1024_GF_bank_closure.py','Report/proofs/SP30_FIFTH_SIGNAL.md','Report/proofs/SP30_NATIVE_PULSE.md',
        'Report/proofs/SP29_THIRD_DOMAIN_PULSE.md')
    deps=('SP30_fifth_signal_certificate.json','SP30_GF_bank_closure_certificate.json','SP30_native_pulse_certificate.json',
        'SP30_encoded_certificate.json','SP30_front_certificate.json','SP30_symbolic_schedule.json','SP29_third_domain_pulse_certificate.json')
    assets=('signal_receipt.json','pulse_receipt.json','pulse_generated.c','pulse.jsonl','endpoint.npz','compile.log','stderr.log',
        'initial_signal_driver_failure.json','initial_signal_driver.py.txt','initial_signal_driver_failure.log',
        'unexecuted_sixth_shrinking_forecast_checker.py.txt','unexecuted_shrinking_forecast_manifest.json')
    receipt=dict(proposal='SP30',scope='J205 actual fifth-boundary native bit box, sixth translating pulse on Z without shrink and next zero bank; seventh/terminal/full data/general eroder/higher/iid unproved',
        Q=p.Q,U=p.U,T_wf=p.T_wf,force_duration=2048,checker_sha256=digest(__file__),written_proof_sha256=digest(ROOT/'Report/proofs/SP30_SIXTH_SIGNAL.md'),
        proposal_source_sha256=digest(proposed.__file__),proposed_candidate_sha256=c.digest(),proposed_netlist_sha256=c.comp.digest,
        source_dependencies_sha256={name:digest(ROOT/name) for name in sources},receipt_dependencies_sha256={name:digest(out/name) for name in deps},
        domain_assets_sha256={str((dest/name).relative_to(out)):digest(dest/name) for name in assets},
        fifth_GF_all_row_hull=hull,protected_upper96_GF_F1_holders=protected,
        fifth_native_source_cofactor_records=source,fifth_native_constant_bit_equalities=2665,
        fifth_left_native_constant_bit_equalities=992,fifth_right_native_constant_bit_equalities=1673,
        actual_fifth_boundary_native_fixed_bit_enclosure_proved=True,unmentioned_H2_Info_private_fields_and_I_free=True,
        GF_shared_selector_assumption_used=False,new_Hold_issue_records=issues,Hold_ROM_key_checks=90112,
        recovered_GF_F1_primary_records=recovered,recovered_zero_Info_copies=440,
        actual_commit_alias_and_partial_zeros_proved=True,sixth_alias_write_classes=aliases,
        sixth_Flag1_cofactors=result['sixth_true_Flag1_cofactors'],sixth_native_capture_gate_routes=285750,
        sixth_MF509_fixed_one_colonies=list(range(98,104)),sixth_MF1021_fixed_one_colonies=ones,sixth_MF1021_unspecified_colonies=optional,
        sixth_partial_MF509_97_and_MF1021_103_zero=True,actual_complete_fifty_nine_bit_sixth_signal_proved=True,
        actual_optional_bit_values_or_independence_proved=False,optional_bit_count=59,concrete_enclosure_masks=1<<59,
        primitive_set_images_reused=1062,GF_selector_set_images_reused=36,frozen_factor_reused_after_actual_J192_projection=True,
        actual_unobserved_private_or_Info_trajectory_transferred=False,
        sixth_start_time=5*p.U+p.T_wf,sixth_endpoint_time=5*p.U+p.T_wf+6144,
        sixth_initial_wrong_GF_interval=[99840,106496],sixth_final_wrong_GF_interval=[93696,100352],sixth_width_decrease=0,
        sixth_endpoint_template_L_R=[92,98],sixth_GF_all_row_hull=pulse_hull,
        GF_site_checks=1610874880,background_domain_equalities=equalities,final_protected_interval_on_Z=[46035,233517],
        all_domain_masks_same_native_endpoint_proved=True,actual_sixth_translating_projected_pulse_on_Z_proved=True,
        automatic_two_Q_shrink_extrapolation_false=True,sixth_width_preserved_at_6656=True,
        native_endpoint_singleton_and_other_auxiliaries_zero=True,intermediate_noninterval_GF_rows=sum(r['holes_in_support_hull']>0 for r in rows),
        final_MF509_one_colonies=[],final_MF1021_fixed_one_colonies=list(range(104,121)),final_MF1021_unspecified_colonies=retained,
        domain_code_sums_used_as_concrete_proof=False,sixth_boundary_time=6*p.U,sixth_boundary_zero_GF_Info_copies=350,
        sixth_boundary_zero_primary_records=targets,boundary_initially_true_primaries=true,boundary_old_foreign_primaries=foreign,
        seventh_source_time=6*p.U+p.T_wf,seventh_complete_foreign_MF509_one_colonies=list(range(92,98)),
        seventh_foreign_source_routes=routes,actual_sixth_bank_and_seventh_complete_foreign_sources_proved=True,
        initial_signal_metadata_failure_retained=True,
        seventh_complete_signal_or_terminal_history_or_all_data_proved=False,
        general_phase_width_clock_private_fault_or_continuing_E0_eroder_proved=False,
        higher_error_map_or_positive_iid_epsilon_or_globally_minimal_change_proved=False,
        additional_rule_programme_layout_or_constant_change=False,numerical_whole_CA_trajectory_used=False,
        active_G17_modified=False,global_reliability_established=False,seconds=time.monotonic()-start)
    (out/'SP30_sixth_signal_certificate.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({key:receipt[key] for key in ('actual_complete_fifty_nine_bit_sixth_signal_proved',
        'actual_sixth_translating_projected_pulse_on_Z_proved','sixth_endpoint_time','sixth_boundary_zero_GF_Info_copies',
        'seventh_complete_foreign_MF509_one_colonies','seconds','global_reliability_established')}),flush=True)


if __name__=='__main__':main()
