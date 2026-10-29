#!/usr/bin/env python3
"""J207 conditional prepared SP30 translation class; finite force variants.

Full-rule and Z theorem only for unchanged2Q. 3Q/4Q modify a projection,
with no compiled own rule. No infinite glider, eroder or iid conclusion.
"""
from pathlib import Path
import hashlib,json,sys,time
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
import proposed_sparse_signal_reservation1024 as proposed
sys.path.insert(0,str(Path(__file__).resolve().parent/'unregistered_terminal'))
import probe_sp30_translation_class_force as driver


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def check_run(parent,force):
    out=parent/f'unregistered_translation_force{force}'
    probe=json.loads((out/'receipt.json').read_text());updates=force+4096
    assert (probe['Q'],probe['U'],probe['T_wf'],probe['force_duration'],probe['updates'])==(1024,475136,278401,force,updates)
    assert probe['checker_sha256']==digest(driver.__file__)
    assert probe['inherited_wrapper_sha256']==digest(parent/'unregistered_terminal_controlled/half_colony_controlled_signal_generated.c')
    assert probe['frozen_factor_sha256']==digest(parent/'SP29_third_pulse_domains_factor_generated.c')
    assert probe['new_rule_projection_receipt_sha256']==digest(parent/'SP30_native_pulse_certificate.json')
    for key,name in (('wrapper_sha256','generated.c'),('run_log_sha256','trace.jsonl'),('endpoint_asset_sha256','endpoint.npz')):
        assert probe[key]==digest(out/name)
    assert (out/'generated.c').read_text()==driver.expected_wrapper(force)
    assert probe['initial_template_L_R']==[128,134] and probe['initial_wrong_GF_interval']==[130560,137216]
    assert probe['initial_MF509_fixed_ones']==list(range(128,134))
    zero=[*range(72,123),127,*range(128,134)]
    one=[124,125,126,*range(134,152)];free=[*range(72),123,*range(152,256)]
    assert probe['initial_MF1021_fixed_ones']==one
    assert probe['initial_MF1021_fixed_zero_colonies']==zero
    assert probe['initial_MF1021_free_quotient_colonies']==free and len(free)==177
    assert len(set(zero+one+free))==len(zero+one+free)==256
    final_interval=[72*1024-8*(updates+1)-37,152*1024+8*(updates+1)+37]
    assert probe['seed_interval']==[73728,155648] and probe['final_protected_interval']==final_interval
    assert probe['finite_domain_recurrence_complete'] and probe['exit_code']==0 and probe['first_unresolved_GF'] is None
    assert probe['hypothetical_RF_force_projection_constant_change']==(force!=2048)
    for key in ('new_fixed_own_rule_compiled','actual_period_signal_supply_or_original_history_proved',
        'infinite_line_translation_class_or_eroder_proved','noise_or_iid_or_full_rule_counterexample_or_reliability_proved',
        'active_G17_or_frozen_SP30_modified','global_reliability_established'):assert probe[key] is False,key
    assert probe['periodic_exterior_is_a_domain_box_not_one_physical_background']
    rows=[json.loads(line) for line in (out/'trace.jsonl').read_text().splitlines()]
    summary=rows.pop();assert summary==probe['summary'] and summary['certificate_complete']
    assert summary['duration']==force and summary['rows_checked']==len(rows)==updates+1
    assert [r['row'] for r in rows]==list(range(updates+1))
    assert summary['GF_support_sites_checked']==len(rows)*262144
    assert summary['background_site_equalities']==sum(262144-r['background_hi']+r['background_lo'] for r in rows)
    assert summary['refined_wipe_copy_mask_disagreements']==summary['refined_wipe_active_majority_disagreements']==0
    for row in rows:
        assert row['duration']==force
        assert row['background_lo']==72*1024-8*(row['row']+1)-37
        assert row['background_hi']==152*1024+8*(row['row']+1)+37
        assert 1024+37<row['background_lo'] and row['background_hi']<262144-37
        assert row['wrong_Addresses']>0
    shift=3*force;L=128-shift//1024;R=L+6
    a=L*1024-512;b=R*1024
    hull=[min(r['left'] for r in rows),max(r['right_exclusive'] for r in rows)]
    assert hull==[a-960,137216]
    assert sum(r['holes_in_support_hull']>0 for r in rows)==1
    assert probe['endpoint']==dict(wrong_GF_sites=6656,GF_support=[a,b],
        native_nonzero_sites_by_plane=[6656,1024,0,0,0,0,0,0],code_nonzero_sites=0,
        Info_fixed_ones=18,Info_free_bits=176)
    with np.load(out/'endpoint.npz',allow_pickle=False) as arrays:
        assert set(arrays.files)=={'native','code','Info'}
        assert arrays['native'].shape==(8,262144) and arrays['code'].shape==arrays['Info'].shape==(262144,)
        xx=np.arange(262144)
        assert np.array_equal(arrays['native'][0],(a<=xx)&(xx<b))
        assert np.array_equal(arrays['native'][1],((a-512<=xx)&(xx<a))|((b-512<=xx)&(xx<b)))
        assert not arrays['native'][2:].any() and not arrays['code'].any()
        assert not arrays['Info'][509::1024].any()
        assert np.flatnonzero(arrays['Info']==1).tolist()==[j*1024+1021 for j in range(134,152)]
        assert np.flatnonzero(arrays['Info']==2).tolist()==[j*1024+1021 for j in free if j!=123]
    return dict(force_duration=force,updates=updates,rows=updates+1,
        endpoint_template_L_R=[L,R],endpoint_wrong_GF_interval=[a,b],endpoint_wrong_GF_width=6656,
        all_row_GF_support_hull=hull,hole_rows=1,GF_site_checks=summary['GF_support_sites_checked'],
        background_domain_equalities=summary['background_site_equalities'],final_protected_interval=final_interval,
        hypothetical_projection_force_change=force!=2048,
        full_rule_and_infinite_line_translation_theorem_proved=force==2048,
        new_fixed_own_rule_compiled=False,permanent_defect_or_general_eroder_or_iid_proved=False,
        assets_sha256={str((out/name).relative_to(parent)):digest(out/name) for name in (
            'receipt.json','generated.c','trace.jsonl','endpoint.npz','compile.log','stderr.log')})


def main():
    start=time.monotonic();p=proposed.parameters();c=proposed.load_artifact();parent=ROOT/'figs/robustness'
    projection=json.loads((parent/'SP30_native_pulse_certificate.json').read_text())
    factor=json.loads((parent/'SP29_third_domain_pulse_certificate.json').read_text())
    terminal=json.loads((parent/'SP30_controlled_terminal_certificate.json').read_text())
    assert (p.Q,p.U,p.T_wf)==(1024,475136,278401)
    assert c.digest()==projection['proposed_candidate_sha256']
    assert projection['unrestricted_native_header_output_node_equalities']==73
    assert projection['exhaustive_copy_keep_majority_cases']==1024
    assert projection['legal_no_write_clock_cases']==6144
    for key in ('corrected_keep_compares_to_refined_old_GF',
        'arbitrary_other_private_fields_and_instructions_irrelevant_to_restricted_factor',
        'arbitrary_binary_labels_and_raw_Flag1_Flag2_allowed_for_factor',
        'common_legal_clock_and_initial_empty_headers_and_no_later_errors_required'):assert projection[key] is True,key
    cofactors=projection['conditional_copy_WF1_cofactors']
    assert [row['clock'] for row in cofactors]==[278401,280448,280449,284544]
    for row in cofactors:
        assert (row['conditional_Info_identities'],row['conditional_WF1_identity'])==(5,1)
        assert row['refined_old_GF_word_preserved_symbolically'] and row['all_raw_Info_and_other_private_and_instruction_inputs_free']
    assert factor['actual_domain_inclusion_proved_by_induction']
    assert (factor['domain_primitive_set_image_checks'],factor['domain_GF_selector_set_image_checks'])==(1062,36)
    assert factor['domain_factor_C_source_sha256']==digest(parent/'SP29_third_pulse_domains_factor_generated.c')
    assert terminal['primitive_domain_and_infinite_line_inclusion_proved']
    assert terminal['periodic_exterior_is_an_abstract_domain_box_only']
    assert terminal['no_concrete_periodic_background_or_quotient_assignment_assumed']
    results=[check_run(parent,force) for force in (2048,3072,4096)]
    # The actual seventh signal fits the theorem after translating by36Q.
    seventh=json.loads((parent/'SP30_seventh_signal_certificate.json').read_text())
    assert seventh['seventh_MF509_fixed_one_colonies']==list(range(92,98))
    assert seventh['seventh_MF1021_fixed_one_colonies']==[88,89,90,*range(98,116)]
    assert seventh['seventh_MF1021_unspecified_colonies']==[87,*range(116,192)]
    assert seventh['seventh_endpoint_template_L_R']==[86,92]
    assert [j+36 for j in seventh['seventh_MF1021_fixed_one_colonies']]==[124,125,126,*range(134,152)]
    sources=('Report/proofs/unregistered_terminal/probe_sp30_translation_class_force.py',
        'Report/proofs/SP30_NATIVE_PULSE.md','Report/proofs/SP29_THIRD_DOMAIN_PULSE.md',
        'Report/proofs/SP30_CONTROLLED_TERMINAL.md','Report/proofs/check_signal_reservation1024_controlled_terminal.py',
        'Report/proofs/check_signal_reservation1024_native_pulse.py',
        'Report/proofs/check_short_force1024_third_domain_pulse.py','gacsca/rule_g.py','gacsca/netlist.py')
    deps=('SP30_native_pulse_certificate.json','SP29_third_domain_pulse_certificate.json',
        'SP30_controlled_terminal_certificate.json','SP30_seventh_signal_certificate.json')
    certificate=dict(proposal='SP30',scope='J207 conditional width6.5Q translating pulse on Z with infinite arbitrary exterior; longer-force finite hypothetical equations only; iteration/eroder/higher/iid unproved',
        Q=p.Q,U=p.U,T_wf=p.T_wf,force_duration=2048,updates=6144,
        checker_sha256=digest(__file__),written_proof_sha256=digest(ROOT/'Report/proofs/SP30_TRANSLATION_CLASS.md'),
        proposal_source_sha256=digest(proposed.__file__),proposed_candidate_sha256=c.digest(),proposed_netlist_sha256=c.comp.digest,
        source_dependencies_sha256={name:digest(ROOT/name) for name in sources},
        receipt_dependencies_sha256={name:digest(parent/name) for name in deps},
        frozen_domain_factor_sha256=digest(parent/'SP29_third_pulse_domains_factor_generated.c'),
        finite_runs=results,finite_controlled_signal_window_colonies=80,
        initial_native_template_L_R=[128,134],final_native_template_L_R=[122,128],
        initial_wrong_GF_width=6656,final_wrong_GF_width=6656,
        MF509_fixed_one_offsets_from_K=list(range(6)),
        MF1021_fixed_one_offsets_from_K=[-4,-3,-2,*range(6,24)],
        MF1021_fixed_zero_offset_ranges_from_K=[[-56,-6],[-1,5]],
        MF1021_all_other_integer_colonies_free=True,
        domain_primitive_set_image_checks_reused=1062,domain_GF_selector_set_image_checks_reused=36,
        arbitrary_infinite_signal_assignments_correlations_and_raw_Info_copies_covered=True,
        periodic_exterior_is_an_abstract_domain_box_only=True,no_concrete_periodic_assignment_assumed=True,
        unchanged_full_rule_restricted_projection_and_infinite_line_lift_proved=True,
        conditional_width_preserving_translation_class_on_Z_proved=True,
        all_integer_Q_translations_and_all_legal_period_indices_covered=True,
        all_row_baseline_GF_singletons_and_native_endpoint_singletons=True,
        actual_seventh_history_satisfies_stronger_window_after_translation=True,
        retained_signal_does_not_satisfy_next_invocation_premise_without_programme=True,
        hypothetical_RF_force_projection_constants_explicit=[3072,4096],
        hypothetical_variants_new_full_rule_own_programme_or_Z_theorem_proved=False,
        finite_hypothetical_longer_force_does_not_remove_prepared_defect=True,
        eighth_actual_complete_signal_or_all_period_iteration_or_permanent_defect_or_terminal_history_proved=False,
        all_data_or_arbitrary_fault_or_continuing_E0_eroder_proved=False,
        higher_error_map_or_positive_iid_threshold_or_minimum_globally_sufficient_change_proved=False,
        additional_baseline_rule_programme_layout_or_constant_change=False,
        frozen_SP30_or_active_G17_modified=False,numerical_whole_CA_trajectory_used=False,
        domain_code_sums_used_as_concrete_counts=False,global_reliability_established=False,seconds=time.monotonic()-start)
    (parent/'SP30_translation_class_certificate.json').write_text(json.dumps(certificate,indent=2)+'\n')
    print(json.dumps({key:certificate[key] for key in (
        'conditional_width_preserving_translation_class_on_Z_proved','finite_controlled_signal_window_colonies',
        'finite_hypothetical_longer_force_does_not_remove_prepared_defect',
        'hypothetical_variants_new_full_rule_own_programme_or_Z_theorem_proved',
        'eighth_actual_complete_signal_or_all_period_iteration_or_permanent_defect_or_terminal_history_proved',
        'global_reliability_established','seconds')}),flush=True)


if __name__=='__main__':main()
