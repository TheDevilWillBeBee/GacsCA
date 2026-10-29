#!/usr/bin/env python3
"""Conditional SP30 terminal native eroder; physical terminal history open.

Checks the frozen domain run and the written infinite-line domain lift.
No actual late-signal supply, all-data repair, general eroder or iid proof.
"""
from pathlib import Path
import hashlib,json,sys,time
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
import proposed_sparse_signal_reservation1024 as proposed
sys.path.insert(0,str(Path(__file__).resolve().parent/'unregistered_terminal'))
import probe_sp30_half_colony_controlled_left_signal as driver


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    start=time.monotonic();p=proposed.parameters();c=proposed.load_artifact()
    parent=ROOT/'figs/robustness';out=parent/'unregistered_terminal_controlled'
    probe=json.loads((out/'receipt.json').read_text())
    factor=json.loads((parent/'SP29_third_domain_pulse_certificate.json').read_text())
    projection=json.loads((parent/'SP30_native_pulse_certificate.json').read_text())
    native=json.loads((parent/'SP30_native_certificate.json').read_text())
    encoded=json.loads((parent/'SP30_encoded_certificate.json').read_text())
    assert (p.Q,p.U,p.T_wf)==(1024,475136,278401)
    assert c.digest()==projection['proposed_candidate_sha256']==encoded['proposed_candidate_sha256']
    assert projection['unrestricted_native_header_output_node_equalities']==73
    assert projection['exhaustive_copy_keep_majority_cases']==1024
    assert projection['legal_no_write_clock_cases']==6144
    assert projection['corrected_keep_compares_to_refined_old_GF']
    assert projection['arbitrary_other_private_fields_and_instructions_irrelevant_to_restricted_factor']
    assert projection['arbitrary_binary_labels_and_raw_Flag1_Flag2_allowed_for_factor']
    assert projection['common_legal_clock_and_initial_empty_headers_and_no_later_errors_required']
    cofactors=projection['conditional_copy_WF1_cofactors']
    assert [row['clock'] for row in cofactors]==[278401,280448,280449,284544]
    for row in cofactors:
        assert (row['conditional_Info_identities'],row['conditional_WF1_identity'])==(5,1)
        assert row['refined_old_GF_word_preserved_symbolically']
        assert row['all_raw_Info_and_other_private_and_instruction_inputs_free']
    assert native['all_time_computed_GF_Age_under_E0_plus_real1_proved']
    assert encoded['complete_encoded_noiseless_and_all_period_E0_simulation_proved']
    assert factor['actual_domain_inclusion_proved_by_induction']
    assert (factor['domain_primitive_set_image_checks'],factor['domain_GF_selector_set_image_checks'])==(1062,36)
    assert probe['checker_sha256']==digest(driver.__file__)
    assert probe['inherited_wrapper_sha256']==digest(parent/'unregistered_terminal/half_colony_zero_signal_generated.c')
    assert probe['frozen_factor_sha256']==digest(parent/'SP29_third_pulse_domains_factor_generated.c')
    assert probe['frozen_factor_sha256']==factor['domain_factor_C_source_sha256']
    assert probe['new_rule_projection_receipt_sha256']==digest(parent/'SP30_native_pulse_certificate.json')
    for key,name in (('wrapper_sha256','half_colony_controlled_signal_generated.c'),
        ('run_log_sha256','half_colony_controlled_signal.jsonl'),('endpoint_asset_sha256','endpoint.npz')):
        assert probe[key]==digest(out/name)
    assert (out/'half_colony_controlled_signal_generated.c').read_text()==driver.expected_wrapper()
    assert probe['initial_template_L_R']==[128,128] and probe['initial_wrong_GF_interval']==[130560,131072]
    assert probe['initial_MF509_zero_everywhere']
    zero=[*range(72,123),127];one=[124,125,126];free=[*range(72),123,*range(128,256)]
    assert probe['initial_MF1021_fixed_ones']==one
    assert probe['initial_MF1021_fixed_zero_colonies']==zero
    assert probe['initial_MF1021_free_quotient_colonies']==free and len(free)==201
    assert len(set(zero+one+free))==len(zero+one+free)==256
    assert probe['seed_interval']==[73728,132096] and probe['final_protected_interval']==[24531,181293]
    assert probe['finite_domain_recurrence_complete'] and probe['exit_code']==0 and probe['first_unresolved_GF'] is None
    assert not probe['infinite_line_controlled_signal_terminal_theorem_or_general_eroder_proved']
    assert not probe['actual_terminal_signal_or_intact_start_history_proved']
    rows=[json.loads(line) for line in (out/'half_colony_controlled_signal.jsonl').read_text().splitlines()]
    summary=rows.pop();assert summary==probe['summary'] and summary['certificate_complete']
    assert summary['rows_checked']==len(rows)==6145 and [r['row'] for r in rows]==list(range(6145))
    assert summary['GF_support_sites_checked']==len(rows)*262144==1610874880
    assert summary['background_site_equalities']==sum(262144-r['background_hi']+r['background_lo'] for r in rows)==949611430
    for row in rows:
        assert row['background_lo']==72*p.Q-8*(row['row']+1)-37
        assert row['background_hi']==129*p.Q+8*(row['row']+1)+37
        assert 17*p.Q<row['background_lo'] and row['background_hi']<262144-37
    nonempty=[r for r in rows if r['wrong_Addresses']]
    assert [min(r['left'] for r in nonempty),max(r['right_exclusive'] for r in nonempty)]==[123456,131072]
    assert nonempty[-1]['row']==2489 and len(nonempty)==2490
    assert sum(r['holes_in_support_hull']>0 for r in nonempty)==1
    for row in rows[2490:]:
        assert row['wrong_Addresses']==0 and (row['left'],row['right_exclusive'])==(262144,0)
    visible_quiet=lambda r:all(r[field]==0 for field in (
        'wrong_Addresses','Flag1','Flag2','WF1','packets','codes','pressure'))
    assert next(r['row'] for r in rows if visible_quiet(r))==3186
    assert all(visible_quiet(r) for r in rows[3186:])
    assert probe['endpoint']==dict(wrong_GF_sites=0,GF_support=[262144,0],
        native_nonzero_sites_by_plane=[0]*8,code_nonzero_sites=0,Info_fixed_ones=0,Info_free_bits=200)
    with np.load(out/'endpoint.npz',allow_pickle=False) as arrays:
        assert set(arrays.files)=={'native','code','Info'}
        assert arrays['native'].shape==(8,262144) and arrays['code'].shape==arrays['Info'].shape==(262144,)
        assert not arrays['native'].any() and not arrays['code'].any()
        assert not arrays['Info'][509::1024].any() and not (arrays['Info']==1).any()
        assert np.flatnonzero(arrays['Info']==2).tolist()==[j*p.Q+1021 for j in free if j!=123]
        assert not arrays['Info'][123*p.Q+1021]
    sources=('Report/proofs/unregistered_terminal/probe_sp30_half_colony_controlled_left_signal.py',
        'Report/proofs/SP30_NATIVE_PULSE.md','Report/proofs/SP29_THIRD_DOMAIN_PULSE.md',
        'Report/proofs/check_short_force1024_third_domain_pulse.py',
        'Report/proofs/check_signal_reservation1024_native_pulse.py',
        'Report/proofs/check_signal_reservation1024_native.py','Report/proofs/check_distant960_native.py',
        'Report/proofs/SP30_OWN_RULE.md','gacsca/rule_g.py','gacsca/netlist.py')
    deps=('SP29_third_domain_pulse_certificate.json','SP30_native_pulse_certificate.json',
        'SP30_native_certificate.json','SP30_encoded_certificate.json','SP30_front_certificate.json')
    failure=json.loads((out/'initial_checker_failure.json').read_text())
    assert failure['failure']=='Requested nonexistent new_corrected_Info_native_factor_proved receipt field'
    assert not failure['domain_equations_or_results_or_rule_changed']
    assert not failure['global_reliability_established']
    for name,expected in failure['assets_sha256'].items():assert digest(out/name)==expected
    assets=('receipt.json','half_colony_controlled_signal_generated.c','half_colony_controlled_signal.jsonl',
        'endpoint.npz','compile.log','stderr.log','initial_checker_failure.json',
        'initial_checker.py.txt','initial_checker_failure.log')
    certificate=dict(proposal='SP30',scope='J204 conditional terminal native eroder on Z, finite left-signal window, infinitely many arbitrary other signals; original-history window/full data/general eroder/higher/iid unproved',
        Q=p.Q,U=p.U,T_wf=p.T_wf,force_duration=2048,updates=6144,
        checker_sha256=digest(__file__),written_proof_sha256=digest(ROOT/'Report/proofs/SP30_CONTROLLED_TERMINAL.md'),
        proposal_source_sha256=digest(proposed.__file__),proposed_candidate_sha256=c.digest(),proposed_netlist_sha256=c.comp.digest,
        source_dependencies_sha256={name:digest(ROOT/name) for name in sources},
        receipt_dependencies_sha256={name:digest(parent/name) for name in deps},
        domain_assets_sha256={str((out/name).relative_to(parent)):digest(out/name) for name in assets},
        frozen_domain_factor_sha256=probe['frozen_factor_sha256'],
        prepared_domain_receipt_sha256=digest(out/'receipt.json'),
        domain_primitive_set_image_checks_reused=1062,domain_GF_selector_set_image_checks_reused=36,
        native_template_L_R=[128,128],initial_wrong_GF_interval=[130560,131072],
        MF509_zero_everywhere=True,MF1021_fixed_one_offsets_from_K=[-4,-3,-2],
        MF1021_fixed_zero_offset_ranges_from_K=[[-56,-6],[-1,-1]],
        MF1021_all_other_integer_colonies_free=True,finite_controlled_left_window_colonies=56,
        finite_quotient_initial_free_signal_entries=201,
        arbitrary_infinite_signal_assignments_correlations_and_raw_Info_copies_covered=True,
        periodic_exterior_is_an_abstract_domain_box_only=True,
        no_concrete_periodic_background_or_quotient_assignment_assumed=True,
        full_rule_restricted_projection_premises_explicit=True,
        original_J191_error_history_reaches_terminal_template_and_signal_window=False,
        primitive_domain_and_infinite_line_inclusion_proved=True,
        conditional_terminal_native_eroder_on_Z_proved=True,
        all_integer_Q_translations_and_all_legal_period_indices_covered=True,
        future_noiseless_native_GF_and_common_Age_invariant_proved=True,
        future_all_flags_private_or_Info_quiet_or_restored=False,
        all_row_nonempty_GF_support_hull=[123456,131072],
        first_GF_empty_relative_row=2490,last_nonempty_GF_relative_row=2489,
        first_printed_native_validity_quiet_relative_row=3186,
        all6144_GF_selections_determined=True,intermediate_nonempty_hull_hole_rows=1,
        GF_site_checks=1610874880,background_domain_equalities=949611430,
        seed_interval=[73728,132096],final_protected_interval_on_Z=[24531,181293],
        final_GF_empty_and_all_native_header_code_domains_zero=True,
        final_Info_quotient_free_domains=200,
        empty_support_sentinel_not_a_geometric_interval=True,
        initial_checker_receipt_metadata_failure_retained=True,
        domain_code_counts_or_negative_empty_hull_diagnostic_used_as_concrete_evidence=False,
        actual_terminal_signal_supply_or_original_error_repair_or_all_data_proved=False,
        arbitrary_phase_width_clock_private_faults_or_continuing_E0_eroder_proved=False,
        higher_error_map_or_positive_iid_threshold_or_globally_minimal_change_proved=False,
        numerical_whole_CA_trajectory_used=False,additional_rule_programme_layout_or_constant_change=False,
        active_G17_modified=False,global_reliability_established=False,seconds=time.monotonic()-start)
    (parent/'SP30_controlled_terminal_certificate.json').write_text(json.dumps(certificate,indent=2)+'\n')
    print(json.dumps({key:certificate[key] for key in ('conditional_terminal_native_eroder_on_Z_proved',
        'arbitrary_infinite_signal_assignments_correlations_and_raw_Info_copies_covered',
        'future_noiseless_native_GF_and_common_Age_invariant_proved',
        'first_GF_empty_relative_row','finite_controlled_left_window_colonies',
        'actual_terminal_signal_supply_or_original_error_repair_or_all_data_proved',
        'seconds','global_reliability_established')}),flush=True)


if __name__=='__main__':main()
