#!/usr/bin/env python3
"""Actual SP30 fifth signal, shrinking projected pulse and next zero bank.

The written proof supplies the physical programme/store and Z inductions.
General-fault repair, higher-error induction and positive iid ε are open.
"""
from itertools import product
from pathlib import Path
from types import FunctionType
import hashlib,json,sys,time
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from gacsca import rule_g
import proposed_sparse_signal_reservation1024 as proposed
import probe_signal_reservation1024_fifth_signal as probe
import probe_signal_reservation1024_fifth_pulse_domains as domain_driver
import check_short_force1024_GF_bank_closure as inherited_bank


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    start=time.monotonic();p=proposed.parameters();c=proposed.load_artifact();out=ROOT/'figs/robustness'
    fourth=json.loads((out/'SP30_fourth_signal_certificate.json').read_text())
    cofactor=json.loads((out/'SP30_fifth_signal_probe.json').read_text())
    domain=json.loads((out/'SP30_fifth_pulse_domain_probe.json').read_text())
    inherited=json.loads((out/'SP29_third_domain_pulse_certificate.json').read_text())
    assert fourth['actual_fourth_shrinking_projected_pulse_on_Z_proved']
    assert fourth['actual_fourth_bank_and_fifth_complete_foreign_sources_proved']
    assert c.digest()==fourth['proposed_candidate_sha256']==cofactor['proposed_candidate_sha256']
    assert c.comp.digest==cofactor['proposed_netlist_sha256']
    assert cofactor['checker_sha256']==digest(probe.__file__)
    assert cofactor['fourth_signal_receipt_sha256']==digest(out/'SP30_fourth_signal_certificate.json')
    assert cofactor['source_helper_sha256']==digest(ROOT/'Report/proofs/check_signal_reservation1024_second_signal.py')
    assert cofactor['all_H2_Info_and_unmentioned_source_fields_and_I_free']
    assert not cofactor['physical_fourth_boundary_or_complete_fifth_signal_or_pulse_proved']
    result=probe.calculate();assert result==cofactor['results']
    sources=result['fourth_boundary_native_source_cofactors']
    left=[r for r in sources if r['colony']<=102];right=[r for r in sources if r['colony']>=120]
    fixed=lambda rows:sum(v is not None for r in rows for bits in r['constant_output_bits'].values() for v in bits)
    assert (len(left),len(right),fixed(left),fixed(right),fixed(sources))==(32,72,992,1374,2366)
    for row in left:assert row['constant_output_words']==dict(addr=row['colony'],age=p.age_code(4),f1=0,wf1=0)
    for row in right:
        j=row['colony'];expected=(dict(addr=0,age=None,f1=1,wf1=0) if j<=130 else
            dict(addr=None,age=None,f1=None,wf1=None) if j<=149 else
            dict(addr=j,age=None,f1=None,wf1=0) if j<=152 else
            dict(addr=j,age=p.age_code(4),f1=0,wf1=0))
        assert row['constant_output_words']==expected,(j,row['constant_output_words'],expected)
    oldrows=[json.loads(line) for line in (out/'SP30_fourth_pulse_domains.jsonl').read_text().splitlines()]
    oldrows.pop();hull=[min(r['left'] for r in oldrows),max(r['right_exclusive'] for r in oldrows)]
    assert len(oldrows)==6145 and hull==[105024,122880]
    assert fourth['domain_assets_sha256']['SP30_fourth_pulse_domains.jsonl']==digest(out/'SP30_fourth_pulse_domains.jsonl')
    protected=[102*p.Q+phase+s for phase in (*range(59,69),88) for s in proposed.SLOTS]
    assert max(protected)+37==104575<105024
    assert 101*p.Q+1022<105024 and 120*p.Q+1>122880
    assert 70+37<108 and 192-37>149
    listing=json.loads((out/'SP30_program_listing.json').read_text());issues=[];keys=0
    for phase,shift in product((*range(59,69),88),(0,512)):
        current=phase+shift;selected=[r for r in listing if r[4]==current and r[6]==rule_g.K_HOLD]
        assert len(selected)==1
        row=selected[0];column=row[1]+(row[3]<<p.logNP);age=p.E0+row[1]*p.PL+row[2]
        assert np.flatnonzero(((c.rom[current]>>2)&3)==rule_g.K_HOLD).tolist()==[column]
        assert age+2<p.T_wf if shift==0 else age>p.T_wf+6144
        issues.append(dict(phase=current,phase_shift=shift,input_issue_age=age,materialized_age=age+2,ROM_column=column))
        keys+=c.rom.shape[1]
    assert keys==90112
    recovered=[]
    for j,phase in product(range(112,120),(*range(59,69),88)):
        y=j*p.Q+phase
        assert 112128<=y-2 and y+2<122880 and y-2>=114688
        recovered.append(dict(colony=j,normal_phase=phase,primary=y,initial_final_phases=[phase+512,phase]))
    assert len(recovered)*5==440
    mask=(set(range(58,901))-{509,515})|{901,902,965}
    for phase,shift,slot in product((3,509,515,1021),(0,512),proposed.SLOTS):
        assert ((phase-slot+shift)%p.Q+slot)%p.Q not in mask
    aliases=[]
    for j,phase in product(range(88,178),(509,1021)):
        y=j*p.Q+phase;labels=[int(105984<=y-s<114688) for s in proposed.SLOTS]
        assert len(set(labels))==1
        virtual=(phase+512*labels[0])%p.Q;active=virtual==1021
        assert active==((104<=j<=111) if phase==509 else (j<=102 or j>=112))
        aliases.append(dict(colony=j,physical_phase=phase,virtual_primary=virtual,special_write=active))
    assert [r['virtual_primary'] for r in aliases if (r['colony'],r['physical_phase']) in ((103,509),(111,1021))]==[509,509]
    ones=result['fifth_MF1021_fixed_one_colonies'];optional=result['fifth_MF1021_unspecified_colonies']
    assert ones==[100,101,102,*range(112,126)] and optional==[99,*range(126,160),162,163,164,165]
    assert result['fifth_native_capture_routes']==224790 and len(result['fifth_true_Flag1_cofactors'])==118
    assert result['optional_bit_count']==len(optional)==39 and result['concrete_enclosure_masks']==549755813888
    assert 64+37<102 and 192-37>152
    assert domain['checker_sha256']==digest(domain_driver.__file__)
    assert domain['enclosure_receipt_sha256']==digest(out/'SP30_fifth_signal_probe.json')
    assert domain['finite_domain_recurrence_complete'] and domain['all6144_GF_selections_determined']
    assert domain['exit_code']==0 and domain['first_unresolved_GF'] is None
    assert not domain['actual_fifth_signal_or_pulse_on_Z_proved_by_this_probe']
    assert (domain['optional_bit_count'],domain['concrete_enclosure_masks'])==(39,549755813888)
    for key,name in (
        ('inherited_domain_factor_sha256','SP29_third_pulse_domains_factor_generated.c'),
        ('inherited_domain_wrapper_sha256','SP30_fourth_pulse_domains_generated.c'),
        ('generated_wrapper_sha256','SP30_fifth_pulse_domains_generated.c'),
        ('run_log_sha256','SP30_fifth_pulse_domains.jsonl'),
        ('endpoint_asset_sha256','SP30_fifth_pulse_domain_states.npz'),
        ('stderr_sha256','SP30_fifth_pulse_domains_stderr.log')):assert domain[key]==digest(out/name)
    assert inherited['domain_factor_C_source_sha256']==domain['inherited_domain_factor_sha256']
    assert inherited['actual_domain_inclusion_proved_by_induction']
    assert (inherited['domain_primitive_set_image_checks'],inherited['domain_GF_selector_set_image_checks'])==(1062,36)
    assert (out/'SP30_fifth_pulse_domains_generated.c').read_text()==domain_driver.expected_wrapper(result)
    rows=[json.loads(line) for line in (out/'SP30_fifth_pulse_domains.jsonl').read_text().splitlines()]
    summary=rows.pop();assert len(rows)==6145 and [r['row'] for r in rows]==list(range(6145))
    assert summary==domain['summary'] and summary['certificate_complete'] and summary['rows_checked']==6145
    assert summary['GF_support_sites_checked']==len(rows)*262144==1610874880
    assert summary['background_site_equalities']==sum(262144-r['background_hi']+r['background_lo'] for r in rows)==880394150
    for row in rows:
        assert row['background_lo']==99*p.Q-8*(row['row']+1)-37
        assert row['background_hi']==167*p.Q+8*(row['row']+1)+37
        assert 17*p.Q<row['background_lo'] and row['background_hi']<262144
    assert [rows[0]['left'],rows[0]['right_exclusive']]==[105984,114688]
    assert [rows[-1]['left'],rows[-1]['right_exclusive'],rows[-1]['wrong_Addresses']]==[99840,106496,6656]
    assert [min(r['left'] for r in rows),max(r['right_exclusive'] for r in rows)]==[98880,114688]
    assert sum(r['holes_in_support_hull']>0 for r in rows)==1
    assert domain['endpoint']==dict(wrong_GF_interval=[99840,106496],width=6656,width_decrease=2048,
        native_quiet_template=True,template_L_R=[98,104])
    assert domain['final_protected_interval']==[52179,220205]
    retained_optional=[*range(126,160),162,163,164,165]
    with np.load(out/'SP30_fifth_pulse_domain_states.npz',allow_pickle=False) as arrays:
        native,code,info=arrays['native'],arrays['code'],arrays['Info'];x=np.arange(262144)
        assert native.shape==(8,262144) and code.shape==info.shape==(262144,)
        assert np.array_equal(native[0],(99840<=x)&(x<106496))
        assert np.array_equal(native[1],((99328<=x)&(x<99840))|((105984<=x)&(x<106496)))
        assert not native[2:].any() and not code.any()
        assert not info[509::1024].any()
        assert np.flatnonzero(info[1021::1024]==1).tolist()==list(range(112,126))
        assert np.flatnonzero(info==2).tolist()==[j*p.Q+1021 for j in retained_optional]
        assert (int((info==1).sum()),int((info==2).sum()))==(14,38)
        assert all(info[j*p.Q+phase]==0 for j,phase in ((99,1021),(103,509),(111,1021)))
    assert (98<=104,104<=112-1,98<104)==(True,True,True)
    targets=[];true=foreign=0
    for j,bit in product(range(97,104),range(10)):
        y=j*p.Q+571+bit
        assert 99840<=y-2-37 and y+2+37<106496
        if j<103:origin=None;true+=1
        else:
            origin=(j+1)*p.Q-512
            assert 105984<=origin and origin+p.Q<=114688 and y-origin==59+bit;foreign+=1
        targets.append(dict(primary=y,bit=bit,previous_complete_foreign_origin=origin))
    assert (len(targets),true,foreign)==(70,60,10)
    namespace=dict(inherited_bank.__dict__,proposed=proposed)
    foreign_routes=FunctionType(inherited_bank.routes.__code__,namespace,'routes')(p,98,104)
    assert (foreign_routes['routes'],foreign_routes['direct_checks'])==(11700,180)
    deps=('SP30_fourth_signal_certificate.json','SP30_fifth_signal_probe.json','SP30_fifth_pulse_domain_probe.json',
        'SP30_GF_bank_closure_certificate.json','SP30_native_pulse_certificate.json','SP30_encoded_certificate.json',
        'SP30_front_certificate.json','SP30_symbolic_schedule.json','SP29_third_domain_pulse_certificate.json')
    assets=('SP29_third_pulse_domains_factor_generated.c','SP30_fourth_pulse_domains_generated.c',
        'SP30_fourth_pulse_domains.jsonl','SP30_fifth_pulse_domains_generated.c','SP30_fifth_pulse_domains.jsonl',
        'SP30_fifth_pulse_domain_states.npz','SP30_fifth_pulse_domains_compile.log','SP30_fifth_pulse_domains_stderr.log')
    receipt=dict(proposal='SP30',scope='J203 actual fourth-boundary bit enclosure/complete39-bit fifth signal/fifth shrinking projected pulse on Z, next zero bank/six sixth foreign sources; general eroder/iid unproved',
        Q=p.Q,U=p.U,T_wf=p.T_wf,force_duration=2048,checker_sha256=digest(__file__),
        written_proof_sha256=digest(ROOT/'Report/proofs/SP30_FIFTH_SIGNAL.md'),
        proposal_source_sha256=digest(proposed.__file__),proposed_candidate_sha256=c.digest(),proposed_netlist_sha256=c.comp.digest,
        full_generated_source_sha256=hashlib.sha256(proposed.generated_source(p).encode()).hexdigest(),listing_sha256=digest(out/'SP30_program_listing.json'),
        source_dependencies_sha256={name:digest(ROOT/name) for name in ('gacsca/rule_g.py','gacsca/netlist.py',
            'Report/proofs/probe_signal_reservation1024_fifth_signal.py','Report/proofs/probe_signal_reservation1024_fifth_pulse_domains.py',
            'Report/proofs/check_signal_reservation1024_second_signal.py','Report/proofs/check_short_force1024_GF_bank_closure.py',
            'Report/proofs/SP30_FOURTH_SIGNAL.md','Report/proofs/SP29_THIRD_DOMAIN_PULSE.md',
            'Report/proofs/check_short_force1024_third_domain_pulse.py')},
        receipt_dependencies_sha256={name:digest(out/name) for name in deps},domain_assets_sha256={name:digest(out/name) for name in assets},
        fourth_pulse_all_row_GF_support_hull=hull,protected_upper102_GF_Flag1_holders=protected,
        fourth_native_source_cofactor_records=sources,fourth_native_constant_bit_equalities=2366,
        fourth_left_native_constant_bit_equalities=992,fourth_right_native_constant_bit_equalities=1374,
        actual_fourth_boundary_native_source_bit_enclosure_proved=True,
        all_H2_Info_and_other_unmentioned_source_fields_and_I_free=True,nonconstant_native_output_bits_left_free=True,
        GF_zero_or_canonical_shared_selector_identity_used=False,
        new_twenty_two_phase_Hold_issue_records=issues,new_twenty_two_phase_Hold_ROM_key_checks=keys,
        recovered_native_zero_primary_records=recovered,recovered_native_zero_Info_copies=440,
        actual_two_phase_commit_alias_zeros_and_partial_track_zeros_proved=True,fifth_alias_write_classes=aliases,
        fifth_new_native_capture_gate_routes=224790,fifth_new_complete_true_Flag1_cofactors=result['fifth_true_Flag1_cofactors'],
        fifth_MF509_one_colonies=list(range(104,112)),fifth_MF509_unspecified_colonies=[],
        fifth_MF1021_fixed_one_colonies=ones,fifth_MF1021_unspecified_colonies=optional,
        fifth_partial_MF509_103_and_MF1021_111_zero=True,complete_actual_fifth_signal_thirty_nine_bit_enclosure_proved=True,
        actual_optional_bit_values_or_independence_proved=False,fifth_optional_bit_count=39,fifth_concrete_enclosure_mask_count=549755813888,
        sound_domain_primitive_set_image_checks_reused=1062,sound_domain_GF_selector_checks_reused=36,
        frozen_sound_domain_factor_reused_after_actual_new_rule_identity=True,
        actual_new_private_trajectory_or_unobserved_Info_or_old_late_suffix_transferred=False,
        projected_Info_fields_restricted_to_two_relevant_alias_tracks=True,
        fifth_projected_start_computed_time=4*p.U+p.T_wf,fifth_projected_endpoint_computed_time=4*p.U+p.T_wf+6144,
        fifth_initial_wrong_GF_interval=[105984,114688],fifth_final_wrong_GF_interval=[99840,106496],
        fifth_width_decrease=2048,fifth_endpoint_template_L_R=[98,104],fifth_all_row_GF_support_hull=[98880,114688],
        fifth_GF_site_checks=1610874880,fifth_background_equalities=880394150,fifth_final_protected_interval_on_Z=[52179,220205],
        fifth_all_549755813888_masks_same_singleton_native_endpoint_proved=True,actual_fifth_shrinking_projected_pulse_on_Z_proved=True,
        fifth_native_endpoint_singleton_and_auxiliary_fields_zero=True,fifth_intermediate_noninterval_GF_rows=1,
        fifth_final_MF509_one_colonies=[],fifth_final_MF1021_fixed_one_colonies=list(range(112,126)),
        fifth_final_MF1021_unspecified_colonies=retained_optional,domain_code_sums_or_unevaluated_old_wipe_diagnostics_used_as_proof=False,
        fifth_boundary_computed_time=5*p.U,fifth_boundary_zero_GF_Info_copies=350,fifth_boundary_zero_primary_records=targets,
        fifth_boundary_initially_true_primaries=true,fifth_boundary_old_foreign_primaries=foreign,
        sixth_source_computed_time=5*p.U+p.T_wf,sixth_complete_foreign_MF509_one_colonies=list(range(98,104)),
        sixth_complete_foreign_GF_source_routes=foreign_routes,actual_fifth_bank_and_sixth_complete_foreign_sources_proved=True,
        sixth_complete_signal_or_pulse_or_terminal_repair_or_full_upper_data_proved=False,
        arbitrary_phase_width_clock_defects_or_continuing_E0_eroder_proved=False,
        higher_error_map_or_positive_iid_threshold_or_globally_minimal_change_proved=False,
        additional_rule_programme_layout_or_constant_change=False,active_G17_modified=False,
        numerical_whole_CA_trajectory_used=False,global_reliability_established=False,seconds=time.monotonic()-start)
    (out/'SP30_fifth_signal_certificate.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({key:receipt[key] for key in ('actual_fourth_boundary_native_source_bit_enclosure_proved',
        'complete_actual_fifth_signal_thirty_nine_bit_enclosure_proved','actual_fifth_shrinking_projected_pulse_on_Z_proved',
        'fifth_projected_endpoint_computed_time','fifth_boundary_zero_GF_Info_copies',
        'sixth_complete_foreign_MF509_one_colonies','seconds','global_reliability_established')}),flush=True)


if __name__=='__main__':main()
