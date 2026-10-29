#!/usr/bin/env python3
"""Validate the checkpoint's links, identities, receipts and proof scopes."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys
import numpy as np
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
import gray_scale_rule as proposed
import literal_maintenance
import corrected_native_rule as native
import gray_protocol_spec as specification
import gray_staged_transport as staged
import gray_staged_rule as staged_rule
import gray_raw_gather as raw_gather
import gray_workspace_voted_current as voted_current
import gray_native_bitpacked_program as bitpacked_program
import gray_moving_word_kernel as moving_word
import check_gray_moving_word_v2_audit as full_moving_word_audit
import gray_moving_word_v3 as fast_moving_word
import build_gray_moving_word_v3 as fast_moving_word_builder
import check_gray_moving_word_v3_transport as fast_moving_word_transport
import check_gray_moving_word_v3_deadline as fast_moving_word_deadline
import validate_gray_layout_hardwirer as hardwirer_gather_checkpoint
import validate_gray_affine_word_machine as affine_evaluator_checkpoint
import validate_gray_word_tape_v5 as word_tape_checkpoint
import validate_gray_token_word_v6 as token_word_checkpoint
import validate_gray_token_word_v6_E0 as token_word_E0_checkpoint
import validate_gray_token_gather_v7 as token_gather_checkpoint
import validate_gray_token_gather_v7_clock_island as token_clock_island_checkpoint
import validate_gray_flag_command_contract as flag_command_checkpoint
import validate_gray_clock_gather_bank as clock_gather_bank_checkpoint
import validate_gray_clock_stroboscopic_native as clock_stroboscopic_checkpoint
import validate_gray_clock_erasure_bank as clock_erasure_bank_checkpoint
import validate_gray_early_native_flags as early_native_flags_checkpoint
import validate_gray_global_first_flags as global_first_flags_checkpoint
import validate_ge0_first_workspace_native as first_workspace_native_checkpoint
import validate_gray_native_writeback_ge1 as native_writeback_ge1_checkpoint
import validate_ge2_second_native_prefix as second_native_prefix_ge2_checkpoint
from gacsca import candidates


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def receipt(name):
    return json.loads((ROOT/'figs/gray_counterexamples'/name).read_text())


def validate_native_followup(directory,source):
    """Pin finite numerical evidence and verify its fixed spatial unions."""
    cand=native.candidate(); p=cand.p
    assert (p.Q,p.U,cand.W,cand.comp.digest)==(8192,1048576,37,
        '4812bdc1f84cbc856c95a47b5d0c34c73b63b675b9e5943876c05180b51151cb')
    operator=receipt('corrected_native_operator_certificate.json')
    invariant=receipt('native_geometry_invariant_certificate.json')
    masks=receipt('native_observer_mask_certificate.json')
    real1=receipt('corrected_native_real1_certificate.json')
    mixed=receipt('corrected_native_mixed_certificate.json')
    common=(operator,invariant,masks,real1,mixed)
    checker_names=('check_corrected_native_operator.py','check_native_geometry_invariant.py',
        'check_native_observer_masks.py','check_corrected_native_real1.py','check_corrected_native_mixed.py')
    for row,name in zip(common,checker_names):
        assert row['checker_sha256']==digest(source/name)
        assert row['corrected_native_source_sha256']==digest(native.__file__)
        assert (row['Q'],row['U'])==(p.Q,p.U)
        if 'active_maintenance_sha256' in row:
            assert row['active_maintenance_sha256']==digest(ROOT/'gacsca/maintenance.py')
        if 'candidate_sha256' in row:
            assert row['candidate_sha256']==cand.digest()
            assert row['netlist_sha256']==cand.comp.digest
        if 'global_reliability_established' in row:
            assert not row['global_reliability_established']
    assert invariant['canonical_geometry_noiseless_invariant_proved']
    assert (invariant['phases_checked'],invariant['symbolic_common_clock_bits'],
        invariant['independent_symbolic_flag_bits'])==(8192,20,44)
    assert not invariant['workspace_zero_required']
    assert operator['full_numpy_C_CUDA_updates']==16 and operator['measured_only']
    assert not operator['universal_backend_equivalence_proved']
    assert operator['asset_sha256']==digest(directory/'corrected_native_operator_inputs.npz')
    assert operator['c_backend_source_sha256']==digest(ROOT/'gacsca/machine.py')
    assert operator['gpu_backend_source_sha256']==digest(ROOT/'gacsca/gpu.py')
    assert masks['full_numpy_CUDA_updates']==28 and masks['measured_only']
    assert masks['masks_match_exact_requested_sites']
    assert masks['ever_and_first_last_match_independent_numpy']
    assert masks['asset_sha256']==digest(directory/'native_observer_mask_inputs.npz')
    assert masks['gpu_backend_source_sha256']==digest(ROOT/'gacsca/gpu.py')
    observer=ROOT/'Report/proofs/periodic_ever_gpu.py'
    for row in (masks,real1,mixed):
        assert row['observer_source_sha256']==digest(observer)
        assert row['cuda_kernel_sha256']==masks['cuda_kernel_sha256']
    for stem,row,size,stop in (('corrected_native_real1',real1,32,3072),
                               ('corrected_native_mixed',mixed,20,2924)):
        assert (row['cases'],row['measured_stop_time'])==(size,stop)
        assert row['input_asset_sha256']==digest(directory/(stem+'_inputs.npz'))
        assert row['tracking_asset_sha256']==digest(directory/(stem+'_tracking.npz'))
        assert row['operator_receipt_sha256']==digest(directory/'corrected_native_operator_certificate.json')
        assert row['geometry_invariant_receipt_sha256']==digest(directory/'native_geometry_invariant_certificate.json')
        assert row['measured_only'] and row['geometry_restored']
        assert not row['candidate_counterexample_observed'] and not row['rigorous_counterexample_proved']
        assert not row['full_gray_physical_programme_verified']
        assert (row['maximum_error_age'],row['proposition2_geometry_horizon'],row['age_guard_slack'])==(655360,32769,98303)
        assert (row['error_lambda'],row['error_separation_c'])==(24,104)
        assert row['every_observed_damage_fits_two_adjacent_colonies']
        assert len(row['classifications'])==size
        for classification in row['classifications']:
            assert classification['points']==10818 and classification['level0']==0
            assert classification['extent']==[150,150] and classification['sep']==104
            assert classification['candidate_level1'] and classification['level1']
        with np.load(directory/(stem+'_tracking.npz')) as asset:
            key=('computed_geometry_ever' if stem.endswith('real1')
                 else 'computed_geometry_ever_outside_E0')
            direct=('direct_geometry_ever' if stem.endswith('real1')
                    else 'direct_real1_geometry_ever')
            ever=np.unpackbits(asset[key].view(np.uint8),axis=1,bitorder='little').astype(bool)|asset[direct]
            geometry_rows=[cand.row[f,b] for f,w in (('addr',p.k),('age',p.m)) for b in range(w)]
            assert not np.any(asset['final'][:,geometry_rows]^asset['final'][0,geometry_rows])
            for i,support in enumerate(row['support'],1):
                sites=np.flatnonzero(ever[i]); cols=np.unique(sites//p.Q)
                # This recomputes ONE fixed envelope from the complete
                # per-tick union; it never selects a new pair at each tick.
                assert cols.tolist()==support['colonies']
                assert cols[-1]-cols[0]<=1 and support['fits_two_adjacent_colonies']
                assert int(sites.min())==support['minimum_site']
                assert int(sites.max())==support['maximum_site']
    assert real1['pristine_initial_context_edge_margin']>real1['largest_native_dependency_radius']==5*32769
    assert mixed['original_input_sha256']==digest(directory/'corrected_native_real1_inputs.npz')
    assert mixed['original_receipt_sha256']==digest(directory/'corrected_native_real1_certificate.json')
    assert mixed['choice_asset_sha256']==digest(directory/'corrected_native_mixed_choices.json')
    assert mixed['every_inserted_pair_is_exactly_E0']
    assert (mixed['adaptive_pair_period'],mixed['adaptive_pair_events'])==(25,110)
    assert mixed['E0_points_per_case']==[220]*20
    # Structural location checks independently justify the classification:
    # dense104 core and two linked satellites; E0 pairs separated bytime25.
    with np.load(directory/'corrected_native_real1_inputs.npz') as inp:
        originals=inp['error_points'].copy()
        assert originals.shape==(32,10818,2)
        base=inp['baseline']
        initial=np.unpackbits(base.view(np.uint8),axis=1,bitorder='little').astype(bool)
        expected=np.zeros_like(initial)
        cand.set_field(expected,'addr',np.arange(48*p.Q)%p.Q)
        assert np.array_equal(initial,expected)
        ages=sum(inp['values'][:,:,cand.row['age',b],:].astype(np.uint32)<<b for b in range(p.m))
        assert np.all(ages<=655360)
        for points in originals:
            begin=int(points[:,0].min())+23
            core={(x,t) for x in range(begin,begin+104) for t in range(24,128)}
            expected=core|{(begin-23,1),(begin+126,150)}
            assert set(map(tuple,points.tolist()))==expected
        assert np.array_equal(inp['times'],np.array([1]+list(range(24,128))+[150]))
    with np.load(directory/'corrected_native_mixed_inputs.npz') as inp:
        assert inp['sites'].shape==(110,20,2)
        assert np.array_equal(inp['times'],np.arange(175,2901,25))
        assert np.all(inp['sites'][:,:,1]-inp['sites'][:,:,0]==1)
        assert np.array_equal(inp['real1_error_points'],originals[inp['selected_original_cases']])
        for t,sites in zip(inp['times'],inp['sites']):
            assert np.min(np.minimum(sites,48*p.Q-1-sites))>5*(32769-int(t))
        ages=sum(inp['values'][:,:,cand.row['age',b],:].astype(np.uint32)<<b for b in range(p.m))
        assert np.all(ages<=655360)
    old=receipt('corrected_native_initial_C_api_failure.json')
    assert old['checker_sha256']==digest(directory/old['preserved_checker'])
    assert old['input_sha256']==digest(directory/'corrected_native_initial_C_api_failure_inputs.npz')
    assert not old['backend_counterexample']
    old=receipt('corrected_native_mixed_initial_serialization_failure.json')
    assert not old['backend_counterexample']
    for filename,value in old['retained_files_sha256'].items():
        assert value==digest(directory/filename)


def validate_refinement_checkpoint(directory,source):
    spec=receipt('gray_protocol_refinement_checklist.json')
    generated=specification.arithmetic_certificate()
    assert all(spec[k]==v for k,v in generated.items())
    assert spec['specification_sha256']==digest(specification.__file__)
    assert spec['gray_text_sha256']==digest(ROOT/'papers_txt/gray_readers_guide.txt')
    assert len(spec['obligations'])==16
    assert spec['stage_arithmetic_proved'] and not spec['physical_refinement_proved']
    radius=receipt('computed_simbit_radius_certificate.json')
    assert radius['checker_sha256']==digest(source/'check_computed_simbit_radius.py')
    assert radius['active_maintenance_sha256']==digest(ROOT/'gacsca/maintenance.py')
    assert radius['literal_module_sha256']==digest(literal_maintenance.__file__)
    assert radius['generated_literal_maintenance_sha256']==literal_maintenance.source_sha256()
    assert radius['classifier_sha256']==digest(ROOT/'gacsca/gray_errors.py')
    assert radius['gray_text_sha256']==digest(ROOT/'papers_txt/gray_readers_guide.txt')
    assert radius['gray_pdf_sha256']==digest(next((ROOT/'papers').glob('A Reader*')))
    for filename,value in radius['inspected_page_images_sha256'].items():
        assert value==digest(directory/filename)
    assert radius['exact_native_cofactors']==8 and radius['conditional_radius_lower_bound']==8
    assert radius['conditional_literal_composition_obstruction_proved']
    assert not radius['unconditional_gray_completion_nonexistence_proved']
    assert not radius['full_physical_programme_verified']
    assert not radius['encoded_history_reachability_proved']
    assert not radius['iid_unreliability_proved'] and not radius['gacs_2001_refuted']
    assert radius['raw_state_time']==96*8192 and radius['computed_age']==96*8192+1
    assert radius['radius5_input_neighbourhood_equal']
    assert radius['independent_of_healthy_flag2_repair']
    assert 'no other SimBit write' in radius['proof_premise']
    a,b=radius['witness']
    assert [a['computed_workspace_flag2_at0'],b['computed_workspace_flag2_at0']]==[1,0]
    assert [x for x in a['raw_neighbourhood'] if a['raw_neighbourhood'][x]!=b['raw_neighbourhood'][x]]==['8']
    assert radius['real1_classification']['level1'] and radius['real1_classification']['level0']==0
    assert radius['legal_real1_location_set_for_conditional_one_tick_lift']==[[x,96*8192] for x in range(-5,9)]


def validate_staged_checkpoint(directory,source):
    primitive=receipt('gray_staged_transport_certificate.json')
    assert primitive['primitive_sha256']==digest(staged.__file__)
    assert primitive['checker_sha256']==digest(source/'check_gray_staged_transport.py')
    assert primitive['specification_sha256']==digest(specification.__file__)
    assert primitive['netlist_library_sha256']==digest(ROOT/'gacsca/netlist.py')
    assert primitive['gray_text_sha256']==digest(ROOT/'papers_txt/gray_readers_guide.txt')
    assert (primitive['Q'],primitive['U'],primitive['stored_simulation_bits_per_holder'],
            primitive['input_radius'])==(8192,1048576,260,5)
    assert (primitive['clock_classes'],primitive['address_classes'],
            primitive['symbolic_logical_bits_per_class'],primitive['output_route_equalities'],
            primitive['rest_route_equalities'],primitive['exact_two_fault_majority_cofactors'])==(
            53,24,780,330720,31200,80)
    assert primitive['clock_partition_boundaries']==staged.clock_boundaries()
    assert primitive['address_partition_boundaries']==staged.address_boundaries()
    assert len(primitive['gather_coordinates'])==33
    assert primitive['all_clock_address_route_classes_proved']
    assert primitive['noiseless_rest_stuttering_proved_conditionally']
    assert primitive['two_fault_copy_transparency_proved_conditionally']
    assert 'five identical physical copies' in primitive['copy_transparency_input_premise']
    assert not primitive['interpreter_front_fields_included']
    for key in ('physical_self_simulation_proved','full_physical_E0_lift_proved',
                'computed_SimBit_Workspace_refinement_verified','global_reliability_established'):
        assert not primitive[key]
    build=receipt('GR1_program_build.json'); schedule=receipt('GR1_symbolic_schedule.json')
    fetch=receipt('GR1_fetch_certificate.json'); candidate=staged_rule.load_artifact(); p=candidate.p
    assert (p.Q,p.U,candidate.W,len(candidate.comp.gates))==(8192,1048576,386,20275)
    assert candidate.comp.digest=='54dc5152928eba5d13183a099260aded4643ab2f6aa8daba5fa4c4a66bc8efe4'
    assert build['candidate_sha256']==candidate.digest()==schedule['candidate_sha256']==fetch['candidate_sha256']
    assert build['netlist_sha256']==candidate.comp.digest==fetch['netlist_sha256']
    assert build['asset_sha256']==digest(directory/'GR1_program.npz')
    assert build['listing_sha256']==digest(directory/'GR1_program_listing.json')
    assert build['driver_sha256']==digest(source/'build_gray_staged.py')
    assert build['proposal_sha256']==digest(staged_rule.__file__)
    assert build['transport_primitive_sha256']==digest(staged.__file__)
    for key,path in (('active_rule_sha256','gacsca/rule_g.py'),
        ('active_maintenance_sha256','gacsca/maintenance.py'),('compiler_sha256','gacsca/compiler.py'),
        ('scheduler_sha256','gacsca/jobsched.py'),
        ('isolated_scheduler_sha256','Report/proofs/xor_multiplicity_scheduler.py'),
        ('match_wait_helper_sha256','Report/proofs/gray_counterexamples/build_gray_scale.py')):
        assert build[key]==digest(ROOT/path)
    assert build['build_complete'] and not build['active_rule_modified']
    assert (build['instructions'],build['random_replay_vectors'],build['random_replay_mismatches'])==(27571,64,0)
    assert build['usage']==dict(NPe=11,MP=65,NP=82,MP_min=25)
    attempt=receipt('GR1_attempt01_build.json')
    assert attempt==build
    assert attempt['listing_sha256']==digest(directory/'GR1_attempt01_listing.json')
    assert attempt['preserved_builder_sha256']==digest(directory/attempt['preserved_builder_filename'])
    assert p.Q>=2*candidate.W and len(set(candidate.layout.tolist()))==candidate.W
    assert not set(candidate.layout.tolist())&set(staged_rule.reserved_cells(p))
    assert schedule['checker_sha256']==digest(source/'check_gray_staged_schedule.py')
    assert schedule['inherited_checker_sha256']==digest(ROOT/'Report/proofs/check_g17_schedule.py')
    assert schedule['proposal_sha256']==digest(staged_rule.__file__)
    assert schedule['transport_primitive_sha256']==digest(staged.__file__)
    assert schedule['build_receipt_sha256']==digest(directory/'GR1_program_build.json')
    assert schedule['own_programme_verified'] and schedule['early_prefix_verified']
    assert schedule['final_abstract_replay_requires_no_early_registers_or_scratch']
    assert (schedule['key_equalities'],schedule['final_hold_equalities'],
            schedule['early_flag_equalities'],schedule['counts']['instructions'])==(23,386,2,27571)
    assert fetch['checker_sha256']==digest(source/'check_gray_staged_fetch.py')
    assert fetch['proposal_sha256']==digest(staged_rule.__file__)
    assert fetch['inherited_front_sha256']==digest(ROOT/'gacsca/rule_g.py')
    assert fetch['inherited_timing_sha256']==digest(ROOT/'gacsca/rule.py')
    assert fetch['build_receipt_sha256']==digest(directory/'GR1_program_build.json')
    assert fetch['asset_sha256']==digest(directory/'GR1_program.npz')
    assert (fetch['exact_symbolic_front_cases'],fetch['exact_output_and_lookup_equalities'],
            fetch['work_keys_with_unique_hit'],fetch['zero_row_keys_without_hit'])==(12800,1446400,492,7700)
    assert fetch['match_path']==list(range(p.hi-1,p.lo-p.H-1,-1))
    assert fetch['match_end']==fetch['next_forward_start']==p.lo-p.H
    assert not np.any(candidate.rom[:p.lo]) and not np.any(candidate.rom[p.hi:])
    assert fetch['correct_work_key_fetch_proved_conditionally']
    assert fetch['outside_work_key_instruction_irrelevance_proved'] and not fetch['measured_only']
    initial=receipt('GR1_fetch_initial_checker_failure.json')
    assert initial['checker_sha256']==digest(directory/initial['preserved_checker'])
    assert 'w_eq_const(n,R[:p.k],center)' in (directory/initial['preserved_checker']).read_text()
    for row in (build,schedule,fetch):
        assert not row['gray_verbatim_simulation']
        assert not row['physical_self_simulation_proved'] and not row['full_physical_E0_lift_proved']
        assert not row['global_reliability_established']
    for row in (build,schedule):
        assert row['explicit_healthy_flag2_repair_h']==1
        assert row['explicit_current_corrected_SimBit_Workspace_change']
    frame=receipt('GR1_frame_certificate.json'); quiet=receipt('GR1_flag_quiet_certificate.json')
    clean=receipt('GR1_noiseless_period_certificate.json')
    for row,checker in ((frame,'check_gray_staged_frame.py'),
                        (quiet,'check_gray_staged_flag_quiet.py'),
                        (clean,'check_gray_staged_noiseless_period.py')):
        assert row['checker_sha256']==digest(source/checker)
        assert row['proposal_sha256']==digest(staged_rule.__file__)
        assert (row['Q'],row['U'])==(8192,1048576)
        assert not row['measured_only']
        assert not row['full_physical_E0_lift_proved'] and not row['global_reliability_established']
    assert frame['candidate_sha256']==clean['candidate_sha256']==candidate.digest()
    assert frame['netlist_sha256']==clean['netlist_sha256']==candidate.comp.digest
    assert frame['transport_primitive_sha256']==clean['transport_primitive_sha256']==digest(staged.__file__)
    for key,path in (('inherited_rule_sha256','gacsca/rule_g.py'),
                     ('inherited_timing_sha256','gacsca/rule.py'),
                     ('term_library_sha256','Report/proofs/check_g17_schedule.py')):
        assert frame[key]==digest(ROOT/path)
    assert frame['primitive_receipt_sha256']==digest(directory/'gray_staged_transport_certificate.json')
    assert frame['build_receipt_sha256']==digest(directory/'GR1_program_build.json')
    route=frame['front_route']; coupling=frame['tracked_coupling']
    assert (route['nonmatch_visits_classified'],route['semantic_classes'],
            route['exact_output_and_lookup_equalities'])==(314880,175,19775)
    assert route['nonmatch_front_route_proved_conditionally']
    assert (coupling['address_route_classes'],coupling['exact_tracked_coupling_equalities'])==(24,6240)
    assert coupling['whole_clock_words_symbolic'] and coupling['input_workspace_flags_arbitrary']
    assert coupling['coherent_pending_forwarding_and_selective_reset_coupling_proved']
    assert coupling['native_geometry_receipt_sha256']==digest(directory/'native_geometry_invariant_certificate.json')
    assert quiet['native_source_sha256']==digest(ROOT/'gacsca/maintenance.py')
    assert quiet['native_geometry_receipt_sha256']==digest(directory/'native_geometry_invariant_certificate.json')
    assert quiet['exact_native_boundary_cofactors']==22
    assert quiet['all_flags_quiet_by_age']==clean['native_flags_quiet_by_age']==99*p.Q
    assert quiet['all_colony_flags_noiseless_clearing_proved']
    assert clean['written_proof_sha256']==digest(source/'GR1_NOISELESS_PERIOD.md')
    for name,value in clean['receipt_dependencies_sha256'].items():
        assert value==digest(directory/name)
    assert clean['noiseless_encoded_period_theorem_proved']
    assert clean['continuing_noiseless_boundary_decoding_proved']
    assert not clean['auxiliary_represented_alias_assumed']
    assert (clean['last_gather_computed_age'],clean['last_early_pending_store_application_age'],
            clean['last_final_pending_store_application_age'])==(565245,578540,959464)
    assert (clean['logical_instruction_ROM_bits'],clean['nonzero_instruction_payload_bits'])==(201326592,661704)
    assert not clean['gray_single_ProgramBit_per_Address_compilation_proved']
    assert not clean['full_rest_rule_on_arbitrary_damaged_raw_states_proved']
    assert not clean['gray_verbatim_simulation'] and not clean['real1_recovery_proved']
    assert not clean['iid_reliability_proved'] and not clean['active_rule_modified']
    wake=receipt('GR1_wipe_wake_certificate.json')
    flags=receipt('GR1_E0_flag_recovery_certificate.json')
    lift=receipt('GR1_E0_period_certificate.json')
    for row,checker in ((wake,'check_gray_staged_wipe_wake.py'),
                        (flags,'check_gray_staged_E0_flag_recovery.py'),
                        (lift,'check_gray_staged_E0_period.py')):
        assert row['checker_sha256']==digest(source/checker)
        assert row['proposal_sha256']==digest(staged_rule.__file__)
        assert (row['Q'],row['U'])==(8192,1048576)
        assert not row['measured_only'] and not row['gray_verbatim_simulation']
        assert not row['global_reliability_established']
    assert wake['candidate_sha256']==lift['candidate_sha256']==candidate.digest()
    assert wake['netlist_sha256']==lift['netlist_sha256']==candidate.comp.digest
    assert wake['active_native_source_sha256']==flags['active_native_source_sha256']==digest(ROOT/'gacsca/maintenance.py')
    assert wake['classifier_sha256']==digest(ROOT/'gacsca/gray_errors.py')
    assert wake['term_library_sha256']==digest(ROOT/'Report/proofs/check_g17_schedule.py')
    assert wake['clean_period_receipt_sha256']==digest(directory/'GR1_noiseless_period_certificate.json')
    assert wake['error_set']==[[8189,786433]] and wake['error_classification']['level0']==1
    assert not wake['error_classification']['level1']
    assert wake['raw_self_GF_wipe_wake_proved'] and wake['full_GR1_broad_E_context_reachability_proved']
    assert wake['raw_simulation_difference_at_clean_time']==786434
    assert (wake['all_local_outputs_restored_by_time'],wake['second_tick_exact_restoration_equalities'])==(786435,4510)
    assert len(wake['first_tick_changed_outputs'])==171 and wake['full_compiled_net_cofactors']==64
    assert not wake['gray_intact_all_level_initialization_reachability_proved']
    assert not wake['gray_Proposition2_or4_refuted'] and not wake['iid_unreliability_proved']
    assert flags['exact_native_front_cofactors']==616 and len(flags['records'])==616
    assert flags['charge_tick_gap_lower_bound']==10 and flags['worst_case_rows_per_sweep']==4552
    assert flags['computed_native_flags_quiet_by_age']==lift['native_flags_quiet_by_age']==811920
    assert flags['pure_E0_flag_recovery_proved']
    assert not flags['full_physical_E0_lift_proved']
    assert lift['written_proof_sha256']==digest(source/'GR1_E0_PERIOD.md')
    for name,value in lift['receipt_dependencies_sha256'].items():
        assert value==digest(directory/name)
    assert lift['transport_primitive_sha256']==digest(staged.__file__)
    assert lift['native_source_sha256']==digest(ROOT/'gacsca/maintenance.py')
    assert lift['netlist_source_sha256']==digest(ROOT/'gacsca/netlist.py')
    assert lift['error_classifier_sha256']==digest(ROOT/'gacsca/gray_errors.py')
    assert lift['full_physical_E0_lift_proved'] and lift['pure_E0_physical_encoded_period_lift_proved']
    assert lift['continuing_pure_E0_boundary_decoding_proved']
    assert lift['arbitrary_noisy_clock_words_covered'] and lift['all_Error_replacement_bits_unrestricted']
    assert not lift['unconditional_one_tick_raw_field_transparency_claimed']
    assert not lift['real1_recovery_proved'] and not lift['higher_error_localization_proved']
    assert not lift['iid_reliability_proved'] and lift['explicit_positive_iid_noise_rate'] is None


def validate_real1_clock_commit(directory,source):
    candidate=staged_rule.load_artifact(); p=candidate.p
    row=receipt('GR1_real1_clock_commit_certificate.json')
    assert row['checker_sha256']==digest(source/'check_gray_staged_real1_clock_commit.py')
    assert row['written_proof_sha256']==digest(source/'GR1_REAL1_CLOCK_COMMIT.md')
    assert row['proposal_sha256']==digest(staged_rule.__file__)
    assert row['candidate_sha256']==candidate.digest() and row['netlist_sha256']==candidate.comp.digest
    assert row['input_asset_sha256']==digest(directory/'GR1_real1_clock_commit_inputs_and_cone.npz')
    for key,path in (('active_maintenance_sha256','gacsca/maintenance.py'),
                     ('classifier_sha256','gacsca/gray_errors.py'),
                     ('numpy_backend_sha256','gacsca/machine.py')):
        assert row[key]==digest(ROOT/path)
    for key,name in (('transport_receipt_sha256','gray_staged_transport_certificate.json'),
                    ('forwarding_receipt_sha256','GR1_frame_certificate.json'),
                    ('native_geometry_receipt_sha256','native_geometry_invariant_certificate.json'),
                    ('native_Flag_quiet_receipt_sha256','GR1_flag_quiet_certificate.json'),
                    ('physical_noiseless_receipt_sha256','GR1_noiseless_period_certificate.json')):
        assert row[key]==digest(directory/name)
    assert (row['Q'],row['U'],row['replacement_Age'])==(8192,1048576,1048575)
    assert row['error_points']==[[x,1] for x in range(3865,3870)]
    assert row['classification']['level1'] and row['classification']['level0']==0
    assert row['changed_error_fields']==['age','hold']
    assert row['raw_Info_not_overwritten'] and row['raw_GF_not_overwritten']
    assert (row['computed_Age0_commit_time'],row['geometry_restored_at'],
            row['native_Flag_quiet_by'],row['three_colony_simulation_field_difference_time'])==(2,1444,9636,266470)
    assert row['restored_coherent_primary_Info_one_sites']==[3868,3869]
    assert row['primary_Info_represents_upper_field']==['reg',2]
    assert int(candidate.layout[candidate.row['reg',2]])==3868
    assert row['clock_advection_certificate']['cofactors']==620
    assert row['clock_advection_certificate']['templates']==[[4096,5]]+[[p.Q-d,5] for d in range(5,11)]+[[p.Q-r,r] for r in range(1,5)]
    assert row['fixed_two_colony_pointwise_simulation_field_envelope_refuted_for_GR1']
    assert row['pointwise_mail_witness_uses_exact_route_composition'] and not row['measured_only']
    assert [w['site'] for w in row['three_colony_witness']]==[-457,3868,8193]
    assert [w['colony'] for w in row['three_colony_witness']]==[-1,0,1]
    for key in ('faithful_Gray_Proposition4_refuted','Gray_intact_recursive_initialization_reachability_proved',
                'accepted_GR1_pure_E0_theorem_refuted','GR1_boundary_decoding_or_memory_failure_proved',
                'iid_unreliability_proved','global_reliability_established'):
        assert not row[key]
    with np.load(directory/'GR1_real1_clock_commit_inputs_and_cone.npz') as asset:
        base=asset['initial']; coords=asset['coordinates']; frames=asset['states']
        assert base.shape==(candidate.W,512) and frames.shape==(3,candidate.W,512)
        expected=np.zeros_like(base);candidate.set_field(expected,'addr',coords%p.Q)
        assert np.array_equal(base,expected)
        noisy=candidate.step_numpy(base);sites=np.arange(254,259)
        ages=candidate.field(noisy,'age');ages[sites]=p.U-1;candidate.set_field(noisy,'age',ages)
        for bit in range(5):noisy[candidate.row['hold',bit],sites]=True
        assert np.array_equal(noisy,frames[0])
        assert np.array_equal(candidate.step_numpy(frames[0]),frames[1])
        assert np.array_equal(candidate.step_numpy(frames[1]),frames[2])
    initial=receipt('GR1_real1_clock_commit_initial_checker_failure.json')
    assert initial['checker_source_sha256']==digest(directory/'GR1_real1_clock_commit_initial_checker.py')
    assert not initial['rule_failure'] and not initial['accepted_theorem_failure']
    assert not receipt('GR1_real1_clock_commit_symbolic_checker_failure.json')['rule_failure']
    withdrawn=receipt('GR1_real1_clock_commit_partial_boundary_withdrawal.json')
    assert withdrawn['preserved_checker_sha256']==digest(directory/'GR1_real1_clock_commit_partial_boundary_checker.py')
    assert withdrawn['preserved_receipt_sha256']==digest(directory/'GR1_real1_clock_commit_partial_boundary_certificate.json')
    assert withdrawn['preserved_written_proof_sha256']==digest(directory/'GR1_real1_clock_commit_partial_boundary_proof.md')
    assert not withdrawn['rule_failure']


def validate_intact_clock_commit(directory,source):
    candidate=staged_rule.load_artifact()
    row=receipt('GR1_intact_clock_commit_certificate.json')
    assert row['checker_sha256']==digest(source/'check_gray_staged_intact_clock_commit.py')
    assert row['initializer_sha256']==digest(source/'gray_recursive_initialization.py')
    assert row['written_proof_sha256']==digest(source/'GR1_INTACT_CLOCK_COMMIT.md')
    assert row['proposal_sha256']==digest(staged_rule.__file__)
    assert row['transport_primitive_sha256']==digest(staged.__file__)
    assert row['candidate_sha256']==candidate.digest() and row['netlist_sha256']==candidate.comp.digest
    assert row['active_native_source_sha256']==digest(ROOT/'gacsca/maintenance.py')
    assert row['classifier_sha256']==digest(ROOT/'gacsca/gray_errors.py')
    assert row['term_library_sha256']==digest(ROOT/'Report/proofs/check_g17_schedule.py')
    assert row['cone_asset_sha256']==digest(directory/'GR1_real1_clock_commit_inputs_and_cone.npz')
    for name,value in row['receipt_dependencies_sha256'].items():assert value==digest(directory/name)
    assert row['Info_primary_residues']==[3891,3989,4092,4188,4286]
    assert row['minimum_absolute_Info_recursion_argument']==3891
    assert row['encoding_case_counts']==dict(addr=13,info=5,zero=368)
    assert row['all_represented_fields_and_five_Info_slots_covered']
    assert row['integer_recursion_termination_proved'] and row['stationary_all_level_H_in_E_of_H_proved']
    assert row['all_unused_and_special_Info_primaries_zero'] and row['raw_H_cell0_all386_bits_zero']
    assert row['lower_colony0_all_Info_bits_zero'] and row['exact_old_initial_cone_equalities']==197632
    assert row['samples_are_not_basis_of_universal_recursion_proof']
    assert row['error_points']==[[x,1] for x in range(3865,3870)]
    assert row['error_classification']['level1'] and row['error_classification']['level0']==0
    assert row['no_independent_upper_error_or_earlier_physical_error']
    assert row['full_physical_error_set_is_exactly_one_original_real1']
    assert (row['geometry_restored_at'],row['native_flags_quiet_by'])==(1444,9636)
    assert row['represented_changed_upper_bit']==['reg',2] and row['represented_changed_upper_holder']==0
    assert row['unused_changed_logical_Info_primary']==3869
    assert row['later_history_banks']==[2,3] and row['later_history_all_fields_and11_offsets_encode_q']
    assert not row['first_history_correctness_required']
    assert row['last_later_history_capture_age']==565245
    assert (row['exact_native_zero_flag_cofactors'],row['native_flag_common_clock_free_bits'])==(8192,20)
    assert row['early_flags_zero_at_all_receivers_proved']
    assert row['special_flag_sources_and96Q_Workspace_pulse_zero_proved']
    assert row['intact_recursive_GR1_clock_commit_reachability_proved']
    assert row['intact_recursive_GR1_three_colony_pointwise_SF_witness_proved']
    assert row['simultaneous_three_colony_witness_time']==266470
    assert [w['site'] for w in row['simultaneous_three_colony_witness']]==[-457,3868,8193]
    assert (row['upper_counterfactual_full_net_cofactors'],row['upper_counterfactual_output_equalities'])==(22,4510)
    assert row['all_upper_lookup_instruction_bits_shared_symbolic'] and row['F_of_q_equals_F_of_H_proved']
    assert row['first_noisy_boundary_in_E_of_F_H_proved']
    assert row['no_later_error_continuing_decoded_hierarchy_correct_for_this_witness_proved']
    for key in ('GR1_boundary_decoding_or_memory_failure_proved','faithful_Gray_Proposition4_refuted',
                'Gray_single_ProgramBit_compilation_proved','accepted_pure_E0_theorem_refuted',
                'arbitrary_real1_recovery_proved','iid_unreliability_proved',
                'global_reliability_established','active_rule_modified','measured_only'):
        assert not row[key]


def validate_literal_stage_envelope(directory,source):
    row=receipt('Gray_literal_stage_envelope_certificate.json')
    assert (row['Q'],row['U'],row['error_lambda'],row['error_separation_c'])==(8192,1048576,24,104)
    assert row['checker_sha256']==digest(source/'check_gray_literal_stage_envelope.py')
    assert row['written_proof_sha256']==digest(source/'GRAY_LITERAL_STAGE_ENVELOPE.md')
    assert row['literal_module_sha256']==digest(literal_maintenance.__file__)
    assert row['generated_literal_maintenance_sha256']==literal_maintenance.source_sha256()
    assert row['active_maintenance_sha256']==digest(ROOT/'gacsca/maintenance.py')
    assert row['netlist_library_sha256']==digest(ROOT/'gacsca/netlist.py')
    assert row['classifier_sha256']==digest(ROOT/'gacsca/gray_errors.py')
    assert row['gray_text_sha256']==digest(ROOT/'papers_txt/gray_readers_guide.txt')
    assert row['gray_pdf_sha256']==digest(next((ROOT/'papers').glob('A Reader*')))
    for name,value in row['original_page_images_sha256'].items():assert value==digest(directory/name)
    assert (row['exact_literal_native_phase_cofactors'],row['symbolic_common_clock_bits'])==(8192,20)
    assert row['printed_Flag2_clause_preserved'] and not row['corrected_Flag2_rule_used']
    assert row['canonical_geometry_and_zero_flags_before_pulse_proved_conditionally']
    assert row['error_points']==[[x,1] for x in (4095,4096,4097)]
    assert row['error_classification']['level1'] and row['error_classification']['level0']==0
    assert row['error_classification']['extent']==[3,1]
    assert row['three_copy_majority_one_and_persistence_proved_under_S']
    assert row['arbitrary_programme_recursive_initialization_data_compatibility_proved']
    illustrative=row['initialization_illustrative_frame']
    assert illustrative['arbitrary_correct_ProgramBits_symbolic']
    assert illustrative['unused_marker_bits_symbolic'] and illustrative['upper_cell0_not_all_zero']
    assert illustrative['lifted_ProgramBit_auxiliary_consistent']
    assert illustrative['represented_Workspace_example_zero_independently_of_programme']
    assert illustrative['finite_examples_not_basis_of_universal_initialization_proof']
    assert (row['second_stage_start'],row['second_active_end'],row['third_stage_start'],
            row['conditional_observation_time'])==(262144,393216,524288,458752)
    assert row['conditional_difference_colonies']==[-1,0,1]
    for item in row['fixed_spatial_interval_checks']:
        assert item['covered_colonies']==[c for c in (-1,0,1) if item['j']<=c<item['j']+2]
        assert not {-1,1}<=set(item['covered_colonies'])
    assert row['full_raw_state_gather_G_and_record_retention_R_are_assumed']
    assert row['conditional_pointwise_Proposition4_stage_axiom_incompatibility_proved']
    assert row['no_GR1_rule_ROM_or_transport_dependency']
    for key in ('Age_GF_or_Workspace_overwrite_used','spurious_Age0_Hold_commit_used',
                'actual_Gray_programme_and_final_layout_verified',
                'actual_Q8192_programme_size_and_last_stage_runtime_verified',
                'simultaneous_Mailbox_streams_required','G_R_verified_against_Gray_transition_function',
                'direct_raw_Mailbox_payload_witness_verified','faithful_Gray_full_rule_counterexample_proved',
                'corrected_Gray_decoded_boundary_counterexample_proved','iid_unreliability_proved',
                'gacs_2001_refuted','global_reliability_established','active_rule_modified','measured_only'):
        assert not row[key]
    old=receipt('Gray_literal_stage_envelope_initial_checker_failure.json')
    assert old['retained_checker_sha256']==digest(directory/old['retained_checker'])
    assert old['error_classification_was_correct'] and old['native8192phase_assertions_completed']
    assert not old['rule_failure'] and not old['conditional_theorem_failure']


def validate_real1_split_boundary(directory,source):
    candidate=staged_rule.load_artifact()
    row=receipt('GR1_real1_split_input_certificate.json')
    assert row['checker_sha256']==digest(source/'check_gray_staged_real1_split_input.py')
    assert row['written_proof_sha256']==digest(source/'GR1_REAL1_SPLIT_BOUNDARY.md')
    assert row['proposal_sha256']==digest(staged_rule.__file__)
    assert row['candidate_sha256']==candidate.digest() and row['netlist_sha256']==candidate.comp.digest
    assert row['classifier_sha256']==digest(ROOT/'gacsca/gray_errors.py')
    assert row['term_library_sha256']==digest(ROOT/'Report/proofs/check_g17_schedule.py')
    for name,value in row['receipt_dependencies_sha256'].items():assert value==digest(directory/name)
    assert row['lower_primary_addresses']==[3989,4092]
    assert row['error_points']==[[x,262145] for x in (3988,3989,3990,4091,4092,4093)]
    assert row['error_classification']['level1'] and row['error_classification']['level0']==0
    assert row['error_classification']['extent']==[106,1]
    assert row['error_classification']['method']=='exact'
    assert row['no_Age_or_GF_overwrite']
    assert (row['lower_injection_full_net_cofactors'],row['lower_output_equalities'],
            row['upper_full_net_cofactors'])==(64,13120,6)
    assert row['lower_simulation_copy_coherence_restored_next_tick']
    assert row['original_upper_one_Info_copies']==[[-3,4],[-2,3],[-2,4],[-1,3]]
    assert row['upper_Info_patterns']==[
        dict(logical_Info=0,holders=[-2,-1,0,1,2],output_values=[0,0,1,1,1]),
        dict(logical_Info=-1,holders=[-3,-2,-1,0,1],output_values=[0,0,0,1,1])]
    assert row['full_physical_boundary_composition_proved']
    assert row['GR1_arbitrary_upper_real1_to_adjacent_pair_boundary_map_refuted']
    assert row['lower_boundary_belongs_to_broad_E_of_Y']
    assert row['no_fixed_adjacent_upper_output_exception_pair']
    for key in ('Gray_verbatim_rule_refuted','intact_recursive_hierarchy_reachability_proved',
                'accepted_pure_E0_theorem_refuted','iid_unreliability_proved',
                'global_reliability_established','measured_only'):
        assert not row[key]


def validate_real1_split_E0_context(directory,source):
    candidate=staged_rule.load_artifact(); p=candidate.p
    row=receipt('GR1_real1_split_e0_context_certificate.json')
    assert row['checker_sha256']==digest(source/'check_gray_staged_real1_split_e0_context.py')
    assert row['written_proof_sha256']==digest(source/'GR1_REAL1_SPLIT_E0_CONTEXT.md')
    assert row['proposal_sha256']==digest(staged_rule.__file__)
    assert row['candidate_sha256']==candidate.digest() and row['netlist_sha256']==candidate.comp.digest
    assert row['classifier_sha256']==digest(ROOT/'gacsca/gray_errors.py')
    assert row['term_library_sha256']==digest(ROOT/'Report/proofs/check_g17_schedule.py')
    for name,value in row['receipt_dependencies_sha256'].items():assert value==digest(directory/name)
    assert row['source_Info_upper_bits']==[2,3] and row['lower_primary_addresses']==[4092,4188]
    assert row['error_points']==[[x,262145] for x in (4091,4092,4093,4187,4188,4189)]
    assert row['error_classification']['level1'] and row['error_classification']['level0']==0
    assert row['error_classification']['extent']==[99,1] and row['error_classification']['method']=='window'
    assert row['error_changed_fields']==['info','mr'] and row['own_History2_not_overwritten']
    assert row['no_Age_or_GF_overwrite']
    assert (row['lower_injection_full_net_cofactors'],row['lower_output_equalities'],
            row['upper_full_net_cofactors'],row['operational_Age1_upper_net_cofactors'])==(64,13120,22,22)
    assert row['original_upper_one_Info_copies']==[[1,1],[1,2],[2,0],[2,1]]
    assert row['initial_upper_error_pair']==[[1,0],[2,0]]
    assert row['initial_upper_error_pair_classification']['level0']==2
    assert row['initial_upper_differs_from_coherent_zero_state_only_on_one_E0_pair']
    assert row['independent_upper_F_tick_then_E0_pair_reachability_proved']
    assert row['independent_operational_upper_E0_points']==[[1,1],[2,1]]
    assert (row['independent_operational_upper_initial_native_Age'],
            row['independent_operational_upper_next_computed_Age'])==(1,2)
    assert row['upper_Info_patterns']==[
        dict(logical_Info=0,holders=[-2,-1,0,1,2],output_values=[0,0,0,1,1]),
        dict(logical_Info=1,holders=[-1,0,1,2,3],output_values=[0,0,1,1,1])]
    assert row['upper_Y_difference_from_Fz_sites']==row['operational_Age1_upper_Y_difference_from_Fz_sites']==[1,2,3]
    audit=row['isolation_audit']
    assert audit['shifted_current_core']==[[x,p.U+262145] for x in (4091,4092,4093,4187,4188,4189)]
    assert audit['proposed_previous_core']==[[2*p.Q+d,p.U-1] for d in (-1,0,1)]
    assert audit['previous_core_alone_classification']['level1']
    assert not audit['current_core_classification_in_combined_E']['level1']
    assert (audit['maximum_spatial_difference'],audit['maximum_time_difference'])==(12294,262146)
    assert audit['no_real1_group_in_combined_E'] and audit['full_combined_E_is_original_real2_by_printed_definition']
    assert not audit['proposed_previous_core_generates_initial_upper_fault']
    assert row['illustrative_upper_bad_locations_classification']['level0']==0
    assert row['illustrative_upper_bad_locations_classification']['level1']
    assert row['full_physical_boundary_composition_proved']
    assert row['GR1_arbitrary_upper_real1_to_adjacent_pair_boundary_map_refuted']
    assert row['nearby_earlier_lower_nonE0_source_excluded_by_condition_iv']
    for key in ('earlier_lower_error_realization_proved','all_isolated_lower_histories_reaching_this_context_excluded',
                'admissible_intact_hierarchy_operational_reachability_proved','Gray_verbatim_rule_refuted',
                'intact_recursive_hierarchy_reachability_proved','accepted_pure_E0_theorem_refuted',
                'iid_unreliability_proved','global_reliability_established','measured_only'):
        assert not row[key]


def validate_raw_gather_checkpoint(directory,source):
    row=receipt('GT0_raw_gather_certificate.json');p=raw_gather
    assert (row['Q'],row['U'],row['error_lambda'],row['error_separation_c'],row['input_radius'])==(8192,1048576,24,104,5)
    assert row['primitive_sha256']==digest(p.__file__)
    assert row['checker_sha256']==digest(source/'check_gray_raw_gather.py')
    assert row['written_proof_sha256']==digest(source/'GT0_RAW_GATHER.md')
    assert row['netlist_library_sha256']==digest(ROOT/'gacsca/netlist.py')
    assert row['classifier_sha256']==digest(ROOT/'gacsca/gray_errors.py')
    assert row['term_library_sha256']==digest(ROOT/'Report/proofs/check_g17_schedule.py')
    assert row['gray_text_sha256']==digest(ROOT/'papers_txt/gray_readers_guide.txt')
    assert row['data_fields']==[list(f) for f in p.FIELDS]
    assert (row['data_bits_per_holder'],row['preliminary_frame_bits'])==(240,277)
    comp=p.compiled()
    assert row['netlist_sha256']==comp.digest
    assert (len(comp.inputs),len(comp.gates),len(comp.outputs))==(2687,5035,240)
    assert row['clock_partition_boundaries']==p.clock_boundaries()
    assert row['address_partition_boundaries']==p.address_boundaries()
    assert (row['symbolic_logical_bits_per_class'],row['exact_route_equalities'],
            row['exact_rest_equalities'],row['exact_two_fault_majority_cofactors'])==(720,144000,14400,80)
    for name,value in row['receipt_dependencies_sha256'].items():assert value==digest(directory/name)
    for key,name in (
        ('emitted_transition_graph_sha256','GT0_transitions.json'),
        ('emitted_C_source_sha256','GT0_transitions.c'),
        ('emitted_C_library_sha256','GT0_transitions.so'),
        ('C_comparison_asset_sha256','GT0_C_comparison_inputs_outputs.npz'),
        ('preliminary_layout_sha256','GT0_preliminary_frame_layout.json')):
        assert row[key]==digest(directory/name)
    graph=json.loads((directory/'GT0_transitions.json').read_text())
    assert graph['netlist_sha256']==comp.digest
    assert graph['inputs']==json.loads(json.dumps(comp.inputs))
    assert graph['gates']==json.loads(json.dumps(comp.gates))
    assert graph['outputs']==json.loads(json.dumps(list(comp.outputs.items())))
    assert graph['native_and_programme_integration_ports_unimplemented']
    with np.load(directory/'GT0_C_comparison_inputs_outputs.npz') as asset:
        inputs=asset['inputs'];outputs=asset['outputs']
        assert inputs.shape==(600,2687) and outputs.shape==(600,240)
        values=comp.evaluate({name:inputs[:,i].astype(bool) for i,name in enumerate(comp.inputs)},bool)
        reference=np.stack([values[name] for name in comp.outputs],axis=1).astype(np.uint8)
        assert np.array_equal(reference,outputs)
    assert row['C_compiler_output_comparison_cases']==600
    assert len(row['gather_coordinates'])==33
    for item in row['gather_coordinates']:
        stage=item['stage']-1;off=item['offset']
        assert item['load_age']==p.STAGES[stage][0]+1
        assert item['capture_age']==p.capture_age(stage,p.LANES.index(off))
        assert item['source_displacement']==off*p.Q
        assert item['same_within_colony_address']
    assert row['exact_three_copy_physical_error_set']==[[x,1] for x in (4009,4010,4011)]
    assert row['error_classification']['level1'] and row['error_classification']['level0']==0
    assert row['error_classification']['extent']==[3,1]
    assert (row['exact_first_clean_update_compiled_net_cofactors'],
            row['exact_first_clean_update_output_assertions'])==(30,7200)
    assert row['conditional_witness_time']==56*p.Q
    assert [item['colony'] for item in row['conditional_three_colony_early_prefix_witness']]==[-1,0,1]
    assert [item['site'] for item in row['conditional_three_colony_early_prefix_witness']]==[-4182,4010,12202]
    for key in ('all_clock_address_route_equations_proved',
                'raw_full_state_gather_G_proved_for_component_conditionally',
                'local_receiver_record_storage_and_older_history_independence_proved',
                'record_retention_R_proved_for_component_conditionally',
                'all_data_fields_coherent_rest_stuttering_proved_conditionally',
                'final_programme_ports_unused_before112Q_proved',
                'flag_result_ports_unused_before80Q_minus1_proved',
                'preliminary_all_level_recursive_data_initialization_proved',
                'symbolic_arbitrary_ProgramBits_allowed',
                'all_future_programme_ports_symbolic_in_injection_cofactors',
                'only_SimBit_copies_overwritten',
                'native_controls_need_matching_literal_rule_and_pulse_zero_before96Q',
                'GT0_closed_first56Q_prefix_composition_proved_under_that_native_condition',
                'C_source_gate_mapping_structurally_verified',
                'C_compiler_output_comparison_measured_only',
                'no_GR1_rule_ROM_front_or_transport_dependency',
                'chosen_same_address_gather_layout_and_clock_schedule_explicit'):
        assert row[key]
    for key in ('actual_self_programme_beta_compiled','universal_binary_backend_equivalence_proved',
                'actual_Gray_full_rule_G_R_refinement_proved',
                'integrated_interpreter_ProgramBit_or_computed_SimBit_rule_proved',
                'full_noiseless_or_noisy_period_composition_proved','faster_work_period_variant_used',
                'full_faithful_Gray_counterexample_proved','decoded_memory_or_iid_failure_proved',
                'global_reliability_established','active_rule_modified','mathematical_route_proof_measured_only'):
        assert not row[key]
    old=receipt('GT0_initial_injection_bound_failure.json')
    assert old['retained_checker_sha256']==digest(directory/old['retained_checker'])
    assert old['retained_proof_sha256']==digest(directory/old['retained_proof'])
    assert not old['route_and_rest_certificate_failure'] and not old['rule_failure']
    assert not old['mathematical_witness_failure']
    radius=receipt('GT0_radius_integration_certificate.json')
    assert radius['checker_sha256']==digest(source/'check_gray_raw_gather_radius.py')
    assert radius['written_proof_sha256']==digest(source/'GT0_RADIUS_INTEGRATION.md')
    assert radius['GT0_primitive_sha256']==digest(p.__file__)
    assert radius['GT0_netlist_sha256']==comp.digest
    assert radius['earlier_conditional_checker_sha256']==digest(source/'check_computed_simbit_radius.py')
    assert radius['literal_module_sha256']==digest(literal_maintenance.__file__)
    assert radius['generated_literal_maintenance_sha256']==literal_maintenance.source_sha256()
    assert radius['active_maintenance_sha256']==digest(ROOT/'gacsca/maintenance.py')
    assert radius['netlist_library_sha256']==digest(ROOT/'gacsca/netlist.py')
    assert radius['gray_text_sha256']==digest(ROOT/'papers_txt/gray_readers_guide.txt')
    assert radius['gray_pdf_sha256']==digest(next((ROOT/'papers').glob('A Reader*')))
    for name,value in radius['receipt_dependencies_sha256'].items():assert value==digest(directory/name)
    assert (radius['Q'],radius['U'],radius['raw_state_time'],radius['computed_age'])==(8192,1048576,96*8192,96*8192+1)
    assert (radius['exact_native_cofactors'],radius['exact_GT0_primary_output_cofactors'],
            radius['literal_component_set_required_radius_lower_bound'])==(8,2,8)
    assert radius['sole_different_raw_site']==8 and radius['radius7_neighbourhoods_identical']
    assert radius['workspace_flag2_outputs']==[1,0]
    for key in ('all_future_programme_ports_symbolic','GT0_no_other_SimBit_write_premise_discharged',
                'literal_radius5_completion_of_this_component_set_impossible','independent_of_h1_Flag2_correction'):
        assert radius[key]
    for key in ('any_Gray_completion_nonexistence_proved','actual_self_programme_or_layout_refinement_proved',
                'encoded_hierarchy_reachability_proved','decoded_memory_or_iid_failure_proved',
                'global_reliability_established','active_rule_modified','measured_only'):
        assert not radius[key]


def validate_computed_simbit_order(directory,source):
    row=receipt('Gray_computed_simbit_order_certificate.json')
    assert (row['Q'],row['U'],row['error_lambda'],row['error_separation_c'])==(8192,1048576,24,104)
    assert row['checker_sha256']==digest(source/'check_gray_computed_simbit_order.py')
    assert row['written_proof_sha256']==digest(source/'GRAY_COMPUTED_SIMBIT_ORDER.md')
    assert row['GV0_primitive_sha256']==digest(voted_current.__file__)
    assert row['GT0_primitive_sha256']==digest(raw_gather.__file__)
    assert row['original_conditional_checker_sha256']==digest(source/'check_computed_simbit_radius.py')
    assert row['literal_module_sha256']==digest(literal_maintenance.__file__)
    assert row['generated_literal_maintenance_sha256']==literal_maintenance.source_sha256()
    assert row['native_maintenance_sha256']==digest(ROOT/'gacsca/maintenance.py')
    assert row['netlist_library_sha256']==digest(ROOT/'gacsca/netlist.py')
    assert row['classifier_sha256']==digest(ROOT/'gacsca/gray_errors.py')
    assert row['gray_text_sha256']==digest(ROOT/'papers_txt/gray_readers_guide.txt')
    assert row['gray_pdf_sha256']==digest(next((ROOT/'papers').glob('A Reader*')))
    for name,value in row['original_page_images_sha256'].items():assert value==digest(directory/name)
    for name,value in row['receipt_dependencies_sha256'].items():assert value==digest(directory/name)
    assert (row['exact_native_cofactors'],row['scheduled_prewipe_source_radius_lower_bound'],
            row['exact_vote_at_most_two_fault_cofactors'])==(17,8,102)
    a,b=row['scheduled_prewipe_age_witness']
    assert [x for x in a['raw_native_neighbourhood'] if a['raw_native_neighbourhood'][x]!=
            b['raw_native_neighbourhood'][x]]==['8']
    for item in (a,b):
        assert item['native_wipe3']==0
        assert item['computed_native']['0']==dict(addr=0,age_now=96*8192,age=96*8192+1,f1=0,f2=0)
        assert item['all_GT0_future_programme_ports_symbolic']
        assert item['GV0_voted_current_WF2_reader0']==1
    assert [item['GT0_scheduled_prewipe_primary_SimBit3'] for item in (a,b)]==[1,0]
    assert [item['computed_native']['3']['age'] for item in (a,b)]==[96*8192+1,0]
    assert row['raw_current_primary_singleton_E0_classification']['level0']==1
    assert not row['raw_current_primary_singleton_E0_classification']['level1']
    assert len(row['raw_current_primary_local_E0_false_positive'])==10
    for item in row['raw_current_primary_local_E0_false_positive']:
        assert item['raw_current_primary_WF2']==int(item['primary_copy_overwritten'])
        assert item['GV0_voted_current_WF2']==0
        assert item['unrelated_logical_SimBits_symbolic']
    comp=voted_current.compiled()
    assert row['GV0_netlist_sha256']==comp.digest
    assert row['GV0_maximum_raw_input_distance']==max(abs(name[1]) for name in comp.inputs)==5
    graph=json.loads((directory/'GV0_voted_current_workspace_transitions.json').read_text())
    assert row['emitted_GV0_graph_sha256']==digest(directory/'GV0_voted_current_workspace_transitions.json')
    assert graph['netlist_sha256']==comp.digest and graph['source_interpretation_changed']
    assert graph['inputs']==json.loads(json.dumps(comp.inputs))
    assert graph['gates']==json.loads(json.dumps(comp.gates))
    assert graph['outputs']==json.loads(json.dumps(list(comp.outputs.items())))
    assert row['GV0_complete_clock_partition']==[0,96*8192,98*8192,1048576]
    assert row['GV0_complete_address_partition']==sorted(set(range(6))|set(range(8192-5,8192+1)))
    assert row['GV0_symbolic_raw_copy_and_reader_control_route_equalities']==66
    assert row['final_radius5_source_composition_support_WF1']==list(range(-7,8))
    assert row['final_radius5_source_composition_support_WF2']==list(range(-6,9))
    cone=row['radius8_two_tick_cone_E0_example']
    assert cone['points']==[[0,1],[24,1]] and cone['classification']['level0']==2
    assert not cone['classification']['level1'] and not cone['actual_two_tick_error_survival_proved']
    assert cone['center']==12 and cone['cone']==[-4,28]
    assert row['radius8_gather_offsets']==list(range(-8,9))
    assert (row['radius8_last_capture_delay'],row['radius8_preliminary_frame_bits'],
            row['original_gather_active_duration'])==(8*8192+2,397,16*8192)
    for key in ('age_witness_independent_of_printed_or_h1_Flag2',
                'raw_current_primary_E0_copy_transparency_refuted_locally',
                'GV0_source_expression_changed_to_voted_CURRENT',
                'GV0_native_equation_radius5_composed','GV0_all_raw_state_locality_proved',
                'GV0_local_copy_transparency_with_correct_reader_controls_proved',
                'conditional_final_source_composition_radius8_sufficient_proved',
                'radius8_paper_error_geometry_radius_independent'):
        assert row[key]
    for key in ('deleting_source_wipe_alone_resolves_locality',
                'geometry_or_sufficient_window_is_full_noisy_refinement',
                'actual_programme_runtime_or_final_layout_proved','actual_faithful_Gray_whole_rule_compiled',
                'GV0_whole_rule_E0_or_higher_theorem_proved','encoded_history_reachability_proved',
                'decoded_memory_or_iid_failure_proved','universal_Gray_completion_nonexistence_proved',
                'faster_U_used','active_rule_modified','global_reliability_established','measured_only'):
        assert not row[key]


def validate_native_bitpacked_programme(directory,source):
    row=receipt('GPN0_native_programme_certificate.json');p=bitpacked_program
    assert (row['Q'],row['U'],row['error_lambda'],row['error_separation_c'])==(8192,1048576,24,104)
    assert row['encoder_sha256']==digest(p.__file__)
    assert row['checker_sha256']==digest(source/'check_gray_native_bitpacked_program.py')
    assert row['written_proof_sha256']==digest(source/'GPN0_PROGRAMME_OBSTRUCTION.md')
    assert row['literal_module_sha256']==digest(literal_maintenance.__file__)
    assert row['generated_literal_maintenance_sha256']==literal_maintenance.source_sha256()
    assert row['active_maintenance_sha256']==digest(ROOT/'gacsca/maintenance.py')
    assert row['netlist_library_sha256']==digest(ROOT/'gacsca/netlist.py')
    assert row['gray_text_sha256']==digest(ROOT/'papers_txt/gray_readers_guide.txt')
    assert row['gray_pdf_sha256']==digest(next((ROOT/'papers').glob('A Reader*')))
    assert row['gacs_text_sha256']==digest(ROOT/'papers_txt/gacs_2001.txt')
    assert row['gacs_pdf_sha256']==digest(ROOT/'papers/Reliable Cellular Automata with Self-Organization.pdf')
    for name,value in row['receipt_dependencies_sha256'].items():assert value==digest(directory/name)
    for key,name in (('beta_asset_sha256','GPN0_literal_native_beta.bin'),
                     ('programme_description_sha256','GPN0_literal_native_programme.json'),
                     ('replay_asset_sha256','GPN0_native_programme_replays.npz')):
        assert row[key]==digest(directory/name)
    comp=p.native_compiled();bits=p.encode(comp);parsed=p.decode(bits)
    assert row['native_netlist_sha256']==comp.digest
    assert len(bits)==row['encoded_literal_native_beta_actual_bits']==76389
    assert parsed['gates']==list(comp.gates) and parsed['outputs']==list(comp.outputs.values())
    assert (len(comp.inputs),len(comp.gates),len(comp.outputs),comp.n_nodes)==(407,2919,35,3328)
    baseline=row['baseline']
    assert (baseline['header_bits'],baseline['gate_bits'],baseline['output_map_bits'],
            baseline['index_width'],baseline['programme_bits'])==(75,75894,420,12,76389)
    assert not baseline['programme_fits_Q'] and not baseline['serial_fetch_fits_fifth_active']
    binary=(directory/'GPN0_literal_native_beta.bin').read_bytes()
    assert np.unpackbits(np.frombuffer(binary,np.uint8),bitorder='little')[:len(bits)].tolist()==bits
    graph=json.loads((directory/'GPN0_literal_native_programme.json').read_text())
    assert graph['native_only_not_self_beta'] and graph['bit_length']==76389
    assert graph['netlist_sha256']==comp.digest
    assert graph['inputs']==json.loads(json.dumps(comp.inputs))
    assert graph['gates']==json.loads(json.dumps(comp.gates))
    assert graph['outputs']==json.loads(json.dumps(list(comp.outputs.items())))
    with np.load(directory/'GPN0_native_programme_replays.npz') as asset:
        inputs=asset['inputs'];actual=asset['decoded_outputs'];stored=asset['compiled_outputs']
        assert inputs.shape==(128,407) and actual.shape==stored.shape==(128,35)
        assert np.array_equal(actual,stored)
        values=comp.evaluate({name:inputs[:,i].astype(bool) for i,name in enumerate(comp.inputs)},bool)
        expected=np.stack([values[name] for name in comp.outputs],axis=1).astype(np.uint8)
        assert np.array_equal(actual,expected)
    assert (row['exact_decoded_gate_equalities'],row['exact_decoded_output_map_equalities'],
            row['retained_random_replay_vectors'])==(2919,35,128)
    assert len(row['malformed_case_receipts'])==8
    assert all(item['invalid'] and item['output_zero'] for item in row['malformed_case_receipts'])
    assert not row['native_only_h1_change']['programme_fits_Q']
    assert not row['native_only_h1_change']['serial_fetch_fits_fifth_active']
    assert row['native_only_h1_change']['programme_bits']==76207
    assert [(item['Q'],item['programme_bits']) for item in row['power_of_two_native_prefix_counts']]==[
        (8192,76389),(16384,80911),(32768,85433),(65536,89955),(131072,101742)]
    assert row['first_tested_power_of_two_native_prefix_fit_Q']==131072
    assert (row['native_prefix_header_free_bits'],row['fifth_active_ticks'],
            row['native_prefix_fetch_ticks_lower_bound'],row['fetch_excess_ticks'])==(76314,65536,76389,10853)
    assert row['modern_sufficient_bound_transplant_optimistic_C1_K277_maximum_P_bits']==11
    assert 3*8192+(11+1)**2*277<=8*8192<3*8192+(12+1)**2*277
    text=(ROOT/'papers_txt/gacs_2001.txt').read_text().split('\n')
    assert 'January 24, 2024 (last printing)' in text[row['gacs_title_page_version_newline']-1]
    for key in ('original_printed_native_preserved',
                'all_raw_native_input_programme_equivalence_by_structural_induction',
                'total_abstract_invalid_programme_input_response_defined','random_replays_measured_only',
                'independent_native_module_no_cross_module_optimization_premise',
                'one_fresh_programme_bit_per_tick_serial_fetch_premise',
                'no_programme_prefetch_before_fifth_stage_premise',
                'prefix_storage_obstruction_for_this_encoder_proved','serial_fetch_fifth_stage_obstruction_proved'):
        assert row[key]
    for key in ('universal_proof_based_on_random_replays','increasing_U_alone_repairs_storage_failure',
                'existing_paper_asymptotic_bound_is_Q8192_certificate',
                'source_version_difference_refutes_Gray_citation',
                'modern_bound_guarantee_failure_is_actual_runtime_lower_bound',
                'supplied_three_input_interpreter_verbatim_covers_Gray_eleven_inputs',
                'programme_is_whole_self_beta','physical_interpreter_service_or_final_layout_emitted',
                'physical_whole_rule_defined_on_all_raw_states',
                'arbitrary_word_loop_or_parallel_evaluator_obstruction_proved',
                'native_prefix_Q131072_is_full_rule_sufficient_constant',
                'faithful_Gray_counterexample_or_iid_memory_failure_proved',
                'faster_U_used','active_rule_modified','global_reliability_established'):
        assert not row[key]


def validate_moving_word_kernel(directory,source):
    row=receipt('GMW0_native_programme_certificate.json');p=moving_word
    assert (row['Q'],row['U'],row['error_lambda'],row['error_separation_c'])==(8192,1048576,24,104)
    assert row['kernel_sha256']==digest(p.__file__)
    assert row['checker_sha256']==digest(source/'check_gray_moving_word_kernel.py')
    assert row['written_proof_sha256']==digest(source/'GMW0_PHYSICAL_NATIVE_PROGRAMME.md')
    assert row['literal_module_sha256']==digest(literal_maintenance.__file__)
    assert row['gray_text_sha256']==digest(ROOT/'papers_txt/gray_readers_guide.txt')
    assert row['gray_pdf_sha256']==digest(next((ROOT/'papers').glob('A Reader*')))
    for name,value in row['receipt_dependencies_sha256'].items():assert value==digest(directory/name)
    for key,name in (('beta_sha256','GMW0_native_beta.bin'),
                     ('listing_sha256','GMW0_native_listing.json'),
                     ('replays_sha256','GMW0_native_physical_replays.npz')):
        assert row[key]==digest(directory/name)
    old=receipt('GMW0_initial_listing_failure.json')
    assert old['exit_code']==1
    for name,value in old['sources_sha256'].items():
        assert value==digest(directory/(Path(name).name+'.initial_listing_failure.txt'))
    beta,listing,labels=p.native_word_programme()
    restored=np.unpackbits(np.frombuffer((directory/'GMW0_native_beta.bin').read_bytes(),np.uint8),bitorder='little')
    assert restored.tolist()==list(beta)
    stored=json.loads((directory/'GMW0_native_listing.json').read_text())
    assert stored['entry']==p.ENTRY and stored['programme']==listing and stored['labels']==labels
    assert stored['code_bits']==row['programme_bits']==2346
    assert row['programme_instructions']==len(listing)==107
    assert (row['head_logical_bits'],row['physical_frame_bits'],row['primary_start'],
            row['native_programme_entry'],row['native_programme_end'])==(434,2272,2960,3024,5370)
    assert row['head_holder_dependency_offsets']==list(range(-5,6))
    assert row['tape_dependency_offsets']==list(range(-4,5))
    assert row['native_prefix_runtime_ticks']==row['actual_local_transition_replays']==34396
    assert row['runtime_code_ticks']+sum(r['extra_ticks'] for r in row['runtime_excursions'])==34396
    assert len(row['runtime_excursions'])==14 and len(row['branches'])==3
    assert sum(row['rotating_holder_replay_counts'])==34396
    assert (row['head_initial_row_age'],row['halt_row_age'],row['fifth_active_end_age'],row['active_end_slack'])==(
            917505,951901,983040,31139)
    with np.load(directory/'GMW0_native_physical_replays.npz') as a:
        assert a['inputs'].shape==(98,11,6) and a['outputs'].shape==(98,4)
        assert np.all(a['ticks']==34396)
        for data,result in zip(a['inputs'],a['outputs']):
            cells={j:dict(zip(('addr','age','f1','f2','wf1','wf2'),map(int,data[j+5]))) for j in range(-5,6)}
            expected=literal_maintenance.scalar(cells)
            assert result.tolist()==[expected[n] for n in ('addr','age','f1','f2')]
        assert a['trace_addresses'].shape==(34396,)
        assert a['trace_before'].shape==a['trace_after'].shape==(34396,55)
        assert np.array_equal(a['trace_before'][1:],a['trace_after'][:-1])
        cells={j:dict(zip(('addr','age','f1','f2','wf1','wf2'),map(int,a['inputs'][18,j+5]))) for j in range(-5,6)}
        tape=p.tape_from_native(cells);out={};position=p.ENTRY
        for address,before,after,write in zip(a['trace_addresses'],a['trace_before'],a['trace_after'],a['trace_writes']):
            packet=p.unpack(int.from_bytes(before.tobytes(),'little'))
            assert int(address)==position+(1 if packet.move==1 else -1 if packet.move==2 else 0)
            produced,written=p.step_packet(packet,int(address),tape.get(int(address),0),beta)
            assert p.pack(produced)==int.from_bytes(after.tobytes(),'little')
            assert int(write)==(-1 if written is None else written)
            if written is not None:out[int(address)]=written
            position=int(address)
        assert p.native_output(out)==dict(zip(('addr','age','f1','f2'),map(int,a['outputs'][18])))
        assert produced.mode==p.HALT
    for key in ('Q_ge_twice_frame','programme_storage_fits','runtime_bound_input_independent',
                'opcode_semantics_defined','instruction_fetch_one_immutable_bit_per_tick',
                'all_raw_physical_component_transition_defined','all_raw_radius_at_most5_proved',
                'native_programme_equivalence_by_register_invariants',
                'noiseless_physical_native_prefix_by_copy_induction','quiet_head_uniqueness_by_induction',
                'immutable_programme_lookup_by_raw_address','mutable_input_tape_noise_exposed',
                'workspace_flag_outputs_forced_zero_explicit_change','preloaded_native_input_tape_premise',
                'instruction_and_physical_replays_measured_only','Info_commit_reads_old_Out_before_Out_reset'):
        assert row[key]
    for key in ('physical_input_gather_refinement_proved','full_SimBit_WF_order_completed',
                'own_full_beta_emitted','full_self_simulation_proved','physical_native_prefix_programme_is_own_beta',
                'h1_GV0_radius8_silently_used','faster_U_used','faithful_Gray_whole_rule_completed',
                'faithful_Gray_counterexample_proved','iid_memory_failure_proved','global_reliability_established',
                'active_rule_modified'):
        assert not row[key]


def validate_full_moving_word_checkpoint(directory,source):
    row=receipt('GMW2_full_programme_audit_certificate.json')
    audit=full_moving_word_audit
    assert row['checker_sha256']==digest(audit.__file__)
    assert row['written_proof_sha256']==digest(source/'GMW2_FULL_PROGRAMME_AUDIT.md')
    for name,path in (('kernel_sha256',audit.k.__file__),('builder_sha256',audit.builder.__file__),
                      ('GMW1_kernel_sha256',audit.k1.__file__),('GMW1_builder_sha256',audit.b1.__file__)):
        assert row[name]==digest(path)
    for name,value in row['receipt_dependencies_sha256'].items():assert value==digest(directory/name)
    for name,value in row['asset_dependencies_sha256'].items():assert value==digest(directory/name)
    for name,value in row['retained_failure_and_first56_sources_assets_sha256'].items():
        assert value==digest(directory/name)
    beta,execution=audit.validate_assets(directory)
    assert audit.validate_prefix(directory,beta)==row['prepared_input_exact_active_recurrence_updates']==65535
    flagcounts,votecounts=audit.flag_capacity()
    assert audit.validate_runtime_costs(directory,beta)==row['uninterrupted_runtime_cost_breakdown']
    assert row['instruction_and_CODE_fetch_use_one_update']
    assert not row['serial_programme_fetch_cost_inferred_from_beta_length']
    assert (flagcounts,votecounts)==(row['E0_native_flag_cofactors'],row['E0_SF_bit_vote_cofactors'])==(156827,102)
    assert (row['Q'],row['U'],row['lambda_original'],row['c_original'])==(8192,1048576,24,104)
    assert (row['GMW2_frame_bits'],row['GMW2_immutable_ROM_capacity'],row['GMW2_programme_bits'],
            row['GMW2_instructions'])==(2007,65536,44730,1863)
    assert (row['dense_raw_head_wrong_bit_at_actual_last_precommit_tick'],
            row['dense_raw_head_actual_last_precommit_usable_ticks'])==(66,131070)
    for key in ('GMW1_specific_Q_code_overflow_proved','GMW2_total_local_component_and_radius5_proved',
                'GMW2_actual_beta_listing_identity_verified','generic_ROM_self_reference_defined_without_whole_Apply',
                'quiet_copy_closure_by_equations_proved','E0_only_component_transparency_by_capacity_and_counts_proved',
                'all_native_word_replacements_covered_by_three_correct_words',
                'prepared_no_error_fifth_stage_ProgramBit_copy4_mismatch_proved',
                'dense_raw_head_16Q_output_obstruction_proved','finite_comparisons_measured_only'):
        assert row[key]
    for key in ('prepared_input_intact_recursive_initialization','universal_full_beta_equivalence_proved',
                'faithful_Gray_programme_gather_pulse_or_period_completed','real1_or_higher_theorem_proved',
                'positive_iid_noise_rate_proved','corrected_Gray_or_iid_failure_proved','faster_U_used',
                'active_rule_modified','global_reliability_established'):
        assert not row[key]
    assert row['finite_whole_beta_comparisons']==execution['uninterrupted_word_evaluator_replays']==70


def validate_fast_moving_word_checkpoint(directory,source):
    k=fast_moving_word;b=fast_moving_word_builder
    transport=receipt('GMW3_fast_transport_certificate.json')
    emission=receipt('GMW3_full_proposed_certificate.json')
    deadline=receipt('GMW3_deadline_certificate.json')
    proof=source/'GMW3_FAST_TRANSPORT.md'
    for row in (transport,emission,deadline):
        assert (row['Q'],row['U'],row['lambda_original'],row['c_original'],row['frame_bits'])==(8192,1048576,24,104,2007)
        assert row['kernel_sha256']==digest(k.__file__)
        assert row['base_GMW2_kernel_sha256']==digest(k.base.__file__)
        assert not row['global_reliability_established']
    assert transport['checker_sha256']==digest(fast_moving_word_transport.__file__)
    assert deadline['checker_sha256']==digest(fast_moving_word_deadline.__file__)
    assert transport['proof_sha256']==deadline['proof_sha256']==digest(proof)
    assert emission['builder_sha256']==digest(b.__file__)
    assert emission['base_GMW2_builder_sha256']==digest(b.previous.__file__)
    assert emission['checker_sha256']==digest(source/'check_gray_moving_word_v3.py')
    code,listing,labels,errors=b.programme().assemble()
    assert (len(code),len(listing),len(errors))==(58129,2410,0)
    beta=tuple(code+[0]*(65536-len(code)))
    stored=json.loads((directory/'GMW3_full_proposed_listing.json').read_text())
    assert stored==dict(code_capacity=65536,programme_bits=len(code),instructions=listing,labels=labels,errors=errors)
    assert np.unpackbits(np.fromfile(directory/'GMW3_full_proposed_beta.bin',np.uint8),bitorder='little').tolist()==list(beta)
    for row in listing:
        word=k.beta_word(beta,row['address'],29)
        assert k.decode(word)==(row['opcode'],tuple(v&((1<<w)-1) for v,w in zip(row['operands'],k.ARGS[row['opcode']])))
        assert k.instruction_length(word)==row['bits']
    for row,asset in ((transport,'GMW3_unpaused_E0_transport_witness.npz'),
                      (emission,'GMW3_full_proposed_replays.npz'),
                      (deadline,'GMW3_prepared_deadline_traces.npz')):
        assert row['asset_sha256']==digest(directory/asset)
    for row in (emission,deadline):
        assert row['beta_sha256']==digest(directory/'GMW3_full_proposed_beta.bin')
        assert row['listing_sha256']==digest(directory/'GMW3_full_proposed_listing.json')
    assert transport['beta_sha256']==digest(directory/'GMW3_transport_zero_beta.bin')
    assert transport['classifier_sha256']==digest(ROOT/'gacsca/gray_errors.py')
    masks,bits,controls,supports=fast_moving_word_transport.transport_identities()
    assert masks==transport['visible_masks']
    assert (bits,controls,supports)==(transport['transport_bit_cofactors'],transport['opaque_head_control_cofactors'],
        transport['arbitrary_source_fault_supports'])==(204,5670,67)
    witness,classification=fast_moving_word_transport.physical_witness((0,)*65536,0)
    restored,_=fast_moving_word_transport.physical_witness((0,)*65536,2)
    assert classification==transport['original_error_classification']
    assert transport['actual_error_points']==[[3092,0],[3093,0],[3117,8]]
    assert transport['absolute_error_points']==[[3092,917505],[3093,917505],[3117,917513]]
    with np.load(directory/'GMW3_unpaused_E0_transport_witness.npz') as a:
        for name,value in witness.items():assert np.array_equal(value,a[name])
        assert np.array_equal(restored['actual'],a['restored_actual'])
        assert np.array_equal(restored['reference'],a['restored_reference'])
    with np.load(directory/'GMW3_full_proposed_replays.npz') as a:
        assert a['input_bits'].shape==(86,11,2007)
        assert a['names'].tolist()==emission['replay_names']
        assert a['ticks'].tolist()==emission['measured_ticks']
        for data,result in zip(a['input_bits'],a['outputs']):
            cells={j:k.cell_from_bits(data[j+5].tolist()) for j in range(-5,6)}
            assert result.tolist()==k.cell_bits(k.local_transition(cells,beta))
    failure=receipt('GMW3_emission_failure_01.json')
    assert failure['asset_sha256']==digest(directory/'GMW3_emission_failure_01.npz')
    for name,value in failure['source_snapshots_sha256'].items():assert value==digest(directory/name)
    assert not failure['universal_beta_equivalence_proved'] and not failure['Gray_or_iid_failure_proved']
    with np.load(directory/'GMW3_emission_failure_01.npz') as a:
        assert np.flatnonzero(a['actual']!=a['expected']).tolist()==failure['different_field_bits']
    for name,value in deadline['receipt_dependencies_sha256'].items():assert value==digest(directory/name)
    prepared=fast_moving_word_deadline.fixtures(stored)
    with np.load(directory/'GMW3_prepared_deadline_traces.npz') as a:
        for result in deadline['fixtures']:
            name=result['fixture'];cells=prepared[name]
            assert a[name+'_input_bits'].tolist()==[k.cell_bits(cells[j]) for j in range(-5,6)]
            expected=k.cell_bits(k.local_transition(cells,beta))
            assert a[name+'_expected'].tolist()==expected
            different=np.flatnonzero(a[name+'_truncated']!=a[name+'_expected']).tolist()
            assert different==result['different_field_bits']
            if name=='canonical':assert different==[] and result['uninterrupted_halt_ticks']==71354
            else:assert 66 in different and result['uninterrupted_halt_ticks']==98633
            assert result['all_decoded_outputs_correct_at_deadline']==(name=='canonical')
            assert not result['halted_at_deadline']
        tape=k.input_tape(prepared['normalized_dense_HLT']);out={};scratch={}
        position=k.HEAD_ADDRESS;p=k.initial_packet();age=112*k.Q+1
        assert a['physical_before'].shape==a['physical_after'].shape==(65535,48)
        # Cache NPZ members once; repeated indexing otherwise decompresses
        # the same retained member on every tick. The recurrence is unchanged.
        trace={name:a[name] for name in ('physical_address','physical_old_age','physical_new_age',
            'physical_before','physical_after','physical_stride','physical_out_writes','physical_scratch_writes')}
        for i in range(65535):
            address=int(trace['physical_address'][i]);oldage=int(trace['physical_old_age'][i]);newage=int(trace['physical_new_age'][i])
            assert oldage==age and newage==age+1
            assert k.pack(p)==int.from_bytes(trace['physical_before'][i].tobytes(),'little')
            stride=k.travel_stride(p,position,bool(newage%2)) if p.move in (1,2) else 0
            assert stride==int(trace['physical_stride'][i])
            assert address==position+(stride if p.move==1 else -stride if p.move==2 else 0)
            p,ow,sw=k.base.step_packet(p,address,tape.get(address,0),out.get(address,0),
                scratch.get(address,0),beta[address],beta)
            assert k.pack(p)==int.from_bytes(trace['physical_after'][i].tobytes(),'little')
            assert int(trace['physical_out_writes'][i])==(-1 if ow is None else ow)
            assert int(trace['physical_scratch_writes'][i])==(-1 if sw is None else sw)
            if ow is not None:out[address]=ow
            if sw is not None:scratch[address]=sw
            position=address;age=newage
        assert p.mode==k.SEEK and p.pc==56529 and age==120*k.Q
        output=[out.get(k.PRIMARY_START+i,0) for i in range(k.FRAME_BITS)]
        assert output==a['physical_output'].tolist()==a['normalized_dense_HLT_truncated'].tolist()
        assert a['physical_expected'].tolist()==a['normalized_dense_HLT_expected'].tolist()
        assert output[66]==0 and a['physical_expected'][66]==1
        for q,s in enumerate(k.SLOTS):
            x=3159-s
            cells={j:k.Cell(addr=(x+j)%k.Q,age=k.U-1,
                heads=tuple(k.pack(p) if x+j+t==position else 0 for t in k.SLOTS),
                mem=tuple(tape.get(x+j+t,0) for t in k.SLOTS),
                out=tuple(out.get(x+j+t,0) for t in k.SLOTS),
                scratch=tuple(scratch.get(x+j+t,0) for t in k.SLOTS),
                program=tuple(beta[(x+j+t)%k.Q] for t in k.SLOTS)) for j in range(-5,6)}
            committed=k.local_transition(cells,beta)
            assert committed.info[q]==0 and committed.out[q]==0
    physical=deadline['physical_prefix']
    assert (physical['actual_physical_updates'],physical['all_five_holder_equations_checked'],physical['wrong_represented_primary'])==(65535,327675,3159)
    assert transport['unpaused_original_E0_history_head_loss_proved']
    assert transport['paired_fast_then_one_site_restore_proof_uses_diameter20_less_than_lambda24']
    assert transport['arbitrary_packet_replacement_universal_transport_proof_in_written_argument']
    assert deadline['canonical_unfinished_halt_does_not_imply_wrong_decoded_output']
    assert deadline['dense_prepared_output_deadline_failure_proved']
    for row in (emission,deadline):
        assert not row['universal_full_beta_identity_proved'] and not row['Gray_faithful']
    assert not deadline['initial_context_is_intact_recursive_hierarchy']
    assert not deadline['iid_failure_proved']


def main():
    directory = ROOT/'figs/gray_counterexamples'
    source = ROOT/'Report/proofs/gray_counterexamples'
    doc = ROOT/'Report/GRAY_COUNTEREXAMPLES.md'
    links = re.findall(r'\[[^\]]*\]\(([^)]+)\)',doc.read_text())
    for link in links:
        path = doc.parent/link.split('#',1)[0]
        assert path.exists(),link
    printed = receipt('printed_flag2_certificate.json')
    assert printed['checker_sha256'] == digest(source/'check_printed_flag2.py')
    assert printed['literal_module_sha256'] == digest(source/'literal_maintenance.py')
    assert printed['base_maintenance_sha256'] == digest(ROOT/'gacsca/maintenance.py')
    assert printed['literal_generated_maintenance_sha256'] == literal_maintenance.source_sha256()
    assert printed['gray_text_sha256'] == digest(ROOT/'papers_txt/gray_readers_guide.txt')
    assert printed['gray_pdf_sha256'] == digest(next((ROOT/'papers').glob('A Reader*')))
    assert printed['page21_image_sha256'] == digest(directory/'Gray_page21.png')
    assert printed['scalar_inputs_asset_sha256'] == digest(directory/'printed_flag2_scalar_inputs.npz')
    assert len(printed['symbolic_cases']) == 22
    assert len(printed['adjacent_pair_symbolic_cases']) == 36
    assert printed['published_initialization_two_tick_flag_counterexample_proved']
    assert not printed['full_all_time_simulation_context_certified']
    assert not printed['iid_unreliability_proved'] and not printed['gacs_2001_refuted']
    build = receipt('GR0_program_build.json')
    schedule = receipt('GR0_symbolic_schedule.json')
    cofactor = receipt('GR0_flag2_cofactor_certificate.json')
    p = proposed.parameters()
    candidate = proposed.load_artifact()
    assert (p.Q,p.U,proposed.width(p)) == (8192,1048576,266)
    assert build['build_complete'] and build['random_replay_mismatches'] == 0
    assert build['driver_sha256'] == digest(source/'build_gray_scale.py')
    assert build['proposal_sha256'] == digest(proposed.__file__)
    assert build['literal_module_sha256'] == digest(source/'literal_maintenance.py')
    assert build['literal_maintenance_sha256'] == literal_maintenance.source_sha256()
    assert build['generated_rule_source_sha256'] == hashlib.sha256(proposed.generated_source().encode()).hexdigest()
    assert build['base_rule_sha256'] == digest(ROOT/'gacsca/rule_g.py')
    assert build['compiler_sha256'] == digest(ROOT/'gacsca/compiler.py')
    assert build['scheduler_sha256'] == digest(ROOT/'gacsca/jobsched.py')
    assert build['asset_sha256'] == digest(directory/'GR0_program.npz')
    assert build['listing_sha256'] == digest(directory/'GR0_program_listing.json')
    assert build['candidate_sha256'] == candidate.digest() == schedule['candidate_sha256']
    assert schedule['checker_sha256'] == digest(source/'check_gray_scale_schedule.py')
    assert schedule['inherited_checker_sha256'] == digest(ROOT/'Report/proofs/check_g17_schedule.py')
    assert schedule['own_programme_verified'] and not schedule['gray_verbatim_simulation']
    assert schedule['key_equalities'] == 23 and schedule['final_hold_equalities'] == 266
    assert schedule['counts']['instructions'] == 24014
    assert cofactor['checker_sha256'] == digest(source/'check_gray_scale_flag2_cofactor.py')
    assert cofactor['proposal_sha256'] == digest(proposed.__file__)
    assert cofactor['netlist_sha256'] == candidate.comp.digest
    assert cofactor['full_output_and_lookup_equalities'] == 3189
    assert not cofactor['full_pristine_hierarchy_lift_proved']
    for stem in ('GR0_initial_stall','GR0_wait_boundary_stall'):
        old = receipt(stem+'_program_build.json')
        assert not old['build_complete']
        assert old['listing_sha256'] == digest(directory/(stem+'_program_listing.json'))
        assert old['preserved_builder_sha256'] == digest(directory/old['preserved_builder_filename'])
        assert old['driver_sha256'] == old['preserved_builder_sha256']
        assert old['proposal_sha256'] == digest(proposed.__file__)
    for row in (build,schedule):
        assert not row['global_reliability_established']
    validate_native_followup(directory,source)
    validate_refinement_checkpoint(directory,source)
    validate_staged_checkpoint(directory,source)
    validate_real1_clock_commit(directory,source)
    validate_intact_clock_commit(directory,source)
    validate_literal_stage_envelope(directory,source)
    validate_real1_split_boundary(directory,source)
    validate_real1_split_E0_context(directory,source)
    validate_raw_gather_checkpoint(directory,source)
    validate_computed_simbit_order(directory,source)
    validate_native_bitpacked_programme(directory,source)
    validate_moving_word_kernel(directory,source)
    validate_full_moving_word_checkpoint(directory,source)
    validate_fast_moving_word_checkpoint(directory,source)
    hardwirer_gather_checkpoint.validate(directory)
    affine_evaluator_checkpoint.validate(directory)
    word_tape_checkpoint.validate(directory)
    token_word_checkpoint.validate(directory)
    token_word_E0_checkpoint.validate(directory)
    token_gather_checkpoint.validate(directory)
    token_clock_island_checkpoint.validate(directory)
    flag_command_checkpoint.validate()
    clock_gather_bank_checkpoint.validate()
    clock_stroboscopic_checkpoint.validate()
    clock_erasure_bank_checkpoint.validate()
    early_native_flags_checkpoint.validate()
    global_first_flags_checkpoint.validate()
    first_workspace_native_checkpoint.validate()
    native_writeback_ge1_checkpoint.validate()
    ge1_replay_names=('GE1_native_writeback_replay.log','GE1_native_writeback_root_replay.log')
    for name in ge1_replay_names:
        replay=json.loads((directory/name).read_text())
        assert replay['receipt_sha256']==digest(directory/'GE1_native_writeback_second_bank_certificate.json')
        assert replay['conditional_GE1_native_commit_and_actual_next_bank_validated']
        assert not replay['faithful_Gray_or_iid_result']
    second_native_prefix_ge2_checkpoint.validate()
    ge2_replay_names=('GE2_second_native_prefix_replay.log','GE2_second_native_prefix_root_replay.log')
    for name in ge2_replay_names:
        replay=json.loads((directory/name).read_text())
        assert replay['receipt_sha256']==digest(directory/'GE2_second_native_prefix_certificate.json')
        assert replay['conditional_actual_second_prefix_validated']
        assert not replay['faithful_Gray_or_iid_or_common_clock_repair']
    failure_manifest=json.loads((directory/'GMW56_retained_failure_manifest.json').read_text())
    for name,value in failure_manifest['assets_sha256'].items():assert digest(directory/name)==value
    assert failure_manifest['changed_implementation_or_checker_failures_only']
    assert not failure_manifest['Gray_or_iid_refutation_proved']
    # Direct first-rest corollary of the unchanged new component equations.
    assert hardwirer_gather_checkpoint.gather.capture_age(0,4)==28560
    assert hardwirer_gather_checkpoint.gather.capture_age(0,6)==28560<16*8192<24*8192<32*8192
    assert candidates.CURRENT == 'G17'
    subprocess.run(['git','diff','--quiet','--','gacsca'],cwd=ROOT,check=True)
    active_sources = {name:digest(ROOT/'gacsca'/name) for name in
        ('rule_g.py','rule.py','netlist.py','maintenance.py','compiler.py','jobsched.py','candidates.py','manifest.json',
         'gray_errors.py','machine.py','gpu.py')}
    receipt_names = ('printed_flag2_certificate.json','GR0_program_build.json',
        'GR0_symbolic_schedule.json','GR0_flag2_cofactor_certificate.json',
        'GR0_initial_stall_program_build.json','GR0_wait_boundary_stall_program_build.json',
        'corrected_native_operator_certificate.json','native_geometry_invariant_certificate.json',
        'native_observer_mask_certificate.json','corrected_native_real1_certificate.json',
        'corrected_native_mixed_certificate.json','corrected_native_initial_C_api_failure.json',
        'corrected_native_mixed_initial_serialization_failure.json',
        'gray_protocol_refinement_checklist.json','computed_simbit_radius_certificate.json',
        'gray_staged_transport_certificate.json','GR1_program_build.json','GR1_attempt01_build.json',
        'GR1_symbolic_schedule.json','GR1_fetch_certificate.json','GR1_fetch_initial_checker_failure.json',
        'GR1_frame_certificate.json','GR1_flag_quiet_certificate.json','GR1_noiseless_period_certificate.json',
        'GR1_wipe_wake_certificate.json','GR1_E0_flag_recovery_certificate.json','GR1_E0_period_certificate.json',
        'GR1_real1_clock_commit_certificate.json','GR1_real1_clock_commit_initial_checker_failure.json',
        'GR1_real1_clock_commit_symbolic_checker_failure.json',
        'GR1_real1_clock_commit_partial_boundary_certificate.json',
        'GR1_real1_clock_commit_partial_boundary_withdrawal.json',
        'GR1_real1_split_input_certificate.json','GR1_real1_split_e0_context_certificate.json',
        'GR1_intact_clock_commit_certificate.json',
        'Gray_literal_stage_envelope_certificate.json',
        'Gray_literal_stage_envelope_initial_checker_failure.json',
        'GT0_raw_gather_certificate.json','GT0_initial_injection_bound_failure.json',
        'GT0_radius_integration_certificate.json','Gray_computed_simbit_order_certificate.json',
        'GPN0_native_programme_certificate.json','GMW0_native_programme_certificate.json',
        'GMW0_initial_listing_failure.json',
        'GMW1_full_own_overflow.json','GMW2_full_own_certificate.json','GMW2_full_programme_audit_certificate.json',
        'GMW2_first56_full_own_certificate.json','GMW2_semantic_failure_01.json',
        'GMW2_semantic_failure_02.json','GMW2_semantic_failure_03.json',
        'GMW2_initial_audit_api_failure.json','GMW2_second_audit_receipt_key_failure.json',
        'GMW3_fast_transport_certificate.json','GMW3_full_proposed_certificate.json',
        'GMW3_deadline_certificate.json','GMW3_emission_failure_01.json',
        'GH0_hardwirer_gather_certificate.json','GH0_initial_validator_serialization_failure.json',
        'GMW4_affine_full_attempt_certificate.json','GMW4_initial_validator_receipt_race.json',
        'GMW5_word_tape_execution_certificate.json','GMW5_first_Q_full_attempt.json',
        'GMW5_initial_generator_assertion_failure.json','GMW5_execution_failure_01.json',
        'GMW5_execution_failure_02.json','GMW5_execution_failure_03.json',
        'GMW6_token_word_certificate.json','GMW6_execution_bound.json','GMW6_first_token_overflow.json',
        'GMW6_slot_alias_failure.json','GMW6_slot_shift_failure.json','GMW6_initial_bound_import_failure.json',
        'GMW6_bound_singleton_failure.json','GMW6_wipe_fixture_failure.json',
        'GMW6_bound_predicate_hardening.json','GMW6_initial_validator_minimum_failure.json',
        'GMW56_retained_failure_manifest.json','GMW6_E0_component_certificate.json',
        'GMW7_prepared_execution_certificate.json','GMW7_execution_bound.json',
        'GMW7_single_gather_period_certificate.json',
        'GMW7_WF0_clock_island_certificate.json','GMW7_WF0_clock_island_initial_certificate.json',
        'Gray_flag_command_contract_certificate.json','GMW7_clock_gather_bank_certificate.json',
        'GMW7_clock_stroboscopic_native_certificate.json',
        'GT0_clock_erasure_bank_certificate.json','GE0_early_native_flags_certificate.json',
        'GE0_workspace_endpoint_initial_certificate.json','GE0_global_first_flags_certificate.json',
        'GE0_first_workspace_native_certificate.json','GE1_native_writeback_second_bank_certificate.json',
        'GE2_second_native_prefix_certificate.json','GE2_second_prefix_initial_certificate.json')
    result = dict(document_sha256=digest(doc),document_links=len(links),
        checker_sha256=digest(__file__), candidate_sha256=candidate.digest(),
        active_sources_sha256=active_sources,
        receipt_dependencies_sha256={name:digest(directory/name) for name in receipt_names},
        GE1_registered_replay_logs_sha256={name:digest(directory/name) for name in ge1_replay_names},
        GE2_registered_replay_logs_sha256={name:digest(directory/name) for name in ge2_replay_names},
        GE2_retained_proof_only_revision_assets_sha256=receipt(
            'GE2_second_native_prefix_certificate.json')['retained_initial_assets_sha256'],
        proof_sources_sha256={path.name:digest(path) for path in source.glob('*.py')},
        proof_documents_sha256={path.name:digest(path) for path in source.glob('*.md')},
        gray_text_sha256=digest(ROOT/'papers_txt/gray_readers_guide.txt'),
        gray_pdf_sha256=digest(next((ROOT/'papers').glob('A Reader*'))),
        checkpoint_validated=True, active_rule_modified=False,
        printed_flags_counterexample_proved=True, corrected_gray_refuted=False,
        corrected_native_campaigns_validated=True,
        corrected_native_fixed_two_colony_envelopes_verified_from_tracking_assets=True,
        corrected_native_universal_recovery_proved=False,
        gray_stage_checklist_validated=True,
        conditional_computed_simbit_radius_witness_validated=True,
        gray_staged_tracked_transport_validated=True,
        GR1_own_abstract_programme_validated=True,
        GR1_conditional_noiseless_match_courier_validated=True,
        GR1_outside_work_key_instruction_irrelevance_validated=True,
        GR1_nonmatch_frame_and_pending_coupling_validated=True,
        GR1_healthy_geometry_clean_Flag_clearing_validated=True,
        GR1_noiseless_encoded_period_and_boundary_decoding_validated=True,
        GR1_raw_GF_wipe_wake_and_next_tick_healing_validated=True,
        GR1_pure_E0_native_Flag_recovery_validated=True,
        GR1_pure_E0_physical_period_and_boundary_decoding_validated=True,
        GR1_real1_full_legal_clock_early_commit_validated=True,
        GR1_real1_clock_advection_and_native_recovery_validated=True,
        GR1_real1_pointwise_all_SF_fixed_two_colony_envelope_refuted=True,
        GR1_explicit_stationary_intact_recursive_initialization_validated=True,
        GR1_real1_intact_context_pointwise_three_colony_witness_validated=True,
        GR1_clock_witness_later_native_histories_and_early_flags_validated=True,
        GR1_clock_witness_correct_first_and_continuing_decoded_boundaries_validated=True,
        Gray_literal_stage_axiom_conditional_Proposition4_incompatibility_validated=True,
        Gray_stage_witness_original_native_and_three_copy_majority_constituents_validated=True,
        Gray_stage_witness_actual_gather_retention_programme_or_layout_verified=False,
        Gray_full_rule_Proposition4_counterexample_proved=False,
        GT0_emitted_raw_gather_retention_and_tracked_rest_component_validated=True,
        GT0_preliminary_recursive_data_frame_and_conditional56Q_footprint_validated=True,
        GT0_measured_C_backend_comparisons_retained=True,
        GT0_literal_native_p41_component_set_radius_at_least8_validated=True,
        GT0_faithful_Gray_whole_rule_or_self_programme_refinement_proved=False,
        computed_SimBit_order_and_source_interpretations_audited=True,
        GT0_scheduled_prewipe_Age8_locality_obstruction_validated=True,
        changed_current_primary_source_local_E0_transparency_failure_validated=True,
        GV0_changed_voted_current_source_radius5_and_local_copy_correction_validated=True,
        conditional_radius8_source_composition_and_noise_obligations_audited=True,
        GV0_or_radius8_faithful_Gray_whole_rule_or_noisy_lift_proved=False,
        Gacs_supplied_printing_programme_section_and_finite_bound_audit_validated=True,
        GPN0_actual_bitpacked_native_programme_and_all_input_code_equivalence_validated=True,
        GPN0_Q8192_native_prefix_storage_and_fresh_serial_fetch_obstructions_validated=True,
        GMW0_compact_native_word_programme_all_input_register_proof_validated=True,
        GMW0_total_radius5_physical_kernel_and_quiet_native_prefix_execution_validated=True,
        GMW0_actual_all_tick_local_transition_and_retained_native_replays_validated=True,
        GMW0_preloaded_input_and_fixed_zero_workspace_departures_explicit=True,
        GMW0_own_full_beta_or_faithful_Gray_integration_proved=False,
        GMW1_specific_full_Q_code_emission_overflow_validated=True,
        GMW2_total_radius5_component_and_defined_generic_immutable_ROM_self_reference_validated=True,
        GMW2_proposed_full_beta_emission_and_separate64K_ROM_identity_validated=True,
        GMW2_quiet_copy_closure_and_original_E0_only_component_transparency_validated=True,
        GMW2_measured70_whole_field_comparisons_and_retained_implementation_failures_validated=True,
        GMW2_prepared_no_error_actual_fifth_stage_wrong_ProgramBit_commit_validated=True,
        GMW2_dense_raw_head_actual_remaining16Q_output_obstruction_validated=True,
        GMW2_universal_full_beta_or_faithful_Gray_period_proved=False,
        GMW2_faster_schedule_or_intact_iid_counterexample_proved=False,
        GMW3_changed_three_site_raw_locality_and_exact_E0_head_loss_validated=True,
        GMW3_arbitrary_payload_67_support_capacity_and_paired_E0_component_coupling_validated=True,
        GMW3_proposed64K_beta_identity_and86_finite_field_checks_validated=True,
        GMW3_canonical_correct_output_despite_unfinished_halt_validated=True,
        GMW3_prepared_dense_HLT_actual65K_prefix_and_wrong_Info_commit_validated=True,
        GMW3_universal_beta_or_full_encoded_Gray_period_proved=False,
        GMW3_shorter_U_or_intact_iid_counterexample_proved=False,
        GH0_projected_actual_raw_holder_programme_access_and_total_courier_validated=True,
        GH0_quiet_completion_and_source_identity_before_changed_GH1_snapshot_validated=True,
        GH0_h1_native_complete_cell_E0_component_transparency_validated_conditionally=True,
        GH1_exact_raw_gather_rest_retention_and367_bit_recursive_H_validated_conditionally=True,
        GH1_single_real1_three_colony_first24Q_and_second56Q_footprints_validated_conditionally=True,
        GH0_GH1_own_beta_final_K_or_faithful_Gray_completion_proved=False,
        GH0_GH1_shorter_U_decoded_failure_or_iid_refutation_proved=False,
        GMW4_changed_affine_IO_total_local_radius5_validated=True,
        GMW4_specified_Q_code_full_emission_and_invalid_reference_obstruction_validated=True,
        GMW4_separate64K_static_beta_identity_and51_finite_field_checks_validated=True,
        GMW4_exact_prepared65535_update_wrong_output_rest_and_Info_commit_validated=True,
        GMW4_universal_beta_Q_fit_or_sufficient_schedule_proved=False,
        GMW4_full_Gray_intact_hierarchy_or_iid_refutation_proved=False,
        GMW5_changed_word_tape_total_raw_radius5_and_real_IO_validated=True,
        GMW5_specific_Q_full_code_emission_and_reference_obstruction_validated=True,
        GMW5_separate64K_128_native_and62_full_measured_comparisons_validated=True,
        GMW5_prepared65535_update_two_wrong_words_rest_and_actual_Info_commits_validated=True,
        GMW5_universal_beta_or_Gray_full_period_proved=False,
        GMW6_changed_token_dictionary_total_raw_radius5_rule_and_full_code_identity_validated=True,
        GMW6_used_beta8091_and_total_immutable_capacity59392_explicit=True,
        GMW6_all_legal_upper_raw_prepared_beta_contracts_validated=True,
        GMW6_universal47913_preloaded_execution_bound_validated=True,
        GMW6_no_error_prepared_physical_self_evaluation_and_Info_commit_validated=True,
        GMW6_91_finite_comparisons_measured_only=True,
        GMW6_Gray_Q_bit_programme_or_simulated_flag_repair_proved=False,
        GMW6_quiet_coherent_current_row_whole_cell_E0_coupling_validated=True,
        GMW6_all_native_payloads_and_all_head_metadata_controller_source_footprints_audited=True,
        GMW6_prepared_fifth_stage_continuing_pure_E0_decoder_extension_validated=True,
        GMW6_E0_native_reduced_cofactors_and_additional_full_cell_temporal_checks_validated=True,
        GMW6_complete_period_real1_higher_or_iid_theorem_proved=False,
        GMW7_changed_total_radius5_rule_full_own_programme_and7902_token_bits_validated=True,
        GMW7_universal49068_execution_bound_and_extra51200_dictionary_bits_explicit=True,
        GMW7_actual_single32Q_gather_all191_by11_capture_routes_by37Q_validated=True,
        GMW7_broad_Info_noiseless_encoded_period_validated_for_changed_rule=True,
        GMW7_continuing_pure_E0_majority_decoder_encoded_period_validated_for_changed_rule=True,
        GMW7_97_execution_and14807_full_cell_comparisons_measured_only=True,
        GMW7_Gray_three_gathers_early_flags_or_simulated_flag_pulses_proved=False,
        GMW7_real1_higher_or_iid_theorem_proved=False,
        GMW7_intact_recursive_context_single_original_real2_clock_only_history_validated=True,
        GMW7_actual_native_two_clock_factor_and_all_transient_Flag1_saturation_validated=True,
        GMW7_fixed_WF0_stationary_139264_site_clock_island_for_all_time_proved=True,
        GMW7_no_finite_spacetime_native_clock_erasure_envelope_proved=True,
        GMW7_fixed_spatial_hull_and_unchanged_Address_explicit=True,
        GMW7_private_programme_dictionary_SF_only_fix_under_unchanged_native_WF0_ruled_out=True,
        GMW7_Gray_Address_decoded_memory_or_iid_refuted=False,
        Gray_four_null_right_raw_Address_bank_to_native_Flag2_conditional_lemma_validated=True,
        Gray_final_computed_source_to_Workspace2_and_next_native_seed_conditional_lemma_validated=True,
        Gray_seed_arbitrary_single_row_local_two_fault_payload_extension_validated=True,
        GMW7_actual_intact_first_window_Info_hold_and_zero_end_sources_validated=True,
        GMW7_existing_late_only_evaluator_first_command_timing_gap_validated=True,
        Gray_actual_damaged_input_bank_Age_progression_early_evaluator_source_retention_refinement_proved=False,
        Gray_flag_command_new_candidate_or_schedule_emitted=False,
        GMW7_actual_first_voted_Mem_centre_clock_factor_without_boundary_copy_coherence_validated=True,
        GMW7_actual_capture_sources_on_shared_intact_real2_and_four_five_null_banks_validated=True,
        GMW7_first_bank_col15_quiet_col16_fully_Flag1_set_and_both_upperAge1_validated=True,
        GMW7_later_distorted_bank_periods_and_sixteen_upperAge_progression_proved=False,
        GMW7_all_SF_centre_clock_factor_and16_actual_distorted_bank_periods_validated=True,
        GMW7_actual_padding_beta_flag_normalization_and_asynchronous_commit_lift_validated=True,
        GMW7_actual_fifth_evaluation_Age2_at_colony2_instead_of5_proved=True,
        GMW7_inside_Flag2_zero_for_first16_actual_evaluations_proved=True,
        GMW7_sixteen_common_upper_Age_continuation_premise_refuted_for_changed_rule=True,
        GMW7_all_time_distorted_map_recovery_proved=False,
        GT0_printed_Mailbox_erasure_raw_boundary_logical_factors_validated_for_conditional_prefix=True,
        GT0_actual_second_third_native_banks_on_original_clock_real2_prefix_validated=True,
        GT0_arbitrary_first_bank_temporal_majority_available_by70Q_proved=True,
        GT0_intact_final_layout_and_native_Workspace_window_completion_premises_explicit=True,
        GT0_actual_early_evaluator_own_beta_final_layout_or_late_repair_proved=False,
        GE0_actual_three_history_LOAD_and_compact_literal_native_beta_validated_for_conditional_prefix=True,
        GE0_total_radius5_component_with_explicit_late_ports_and_new_early_schedule_validated=True,
        GE0_34396_tick_native_execution_and_before80Q_flag_delivery_validated_conditionally=True,
        GE0_actual_derived_banks_have_Flag1_one_Flag2_zero_validated=True,
        GE0_prepared_positive_Flag2_reachability_proved=False,
        GE0_initial_closed_Workspace_endpoint_defect_retained_and_halfopen_correction_validated=True,
        GE0_own_full_beta_final_self_layout_or_late_Gray_composition_proved=False,
        GE0_general_E0_birth_or_higher_iid_or_shorter_U_theorem_proved=False,
        GE0_all_receiver_actual_first_native_banks_from_shared_real2_validated_conditionally=True,
        GE0_no_surviving_first_bank_route_crosses_clock_jump_or_displaces_source_word=True,
        GE0_all_receiver_literal_native_beta_Gf_correct_Age_one_and_exact_Flag1_support_validated=True,
        GE0_all_receiver_actual_first_Flag2_commands_zero_and_source_delivery_validated_conditionally=True,
        GE0_global_first_bank_own_completion_late_Workspace_or_later_repair_proved=False,
        GE0_global_first_bank_Gray_refutation_iid_or_shorter_U_proved=False,
        GE0_first_literal_Workspace_native_prefix_from_derived_source_bits_validated_conditionally=True,
        GE0_first_Workspace_computed_Age_and_old_new_source_lag_validated=True,
        GE0_infinite_line_event_partition_and_finite_native_prefix_to100Q_validated=True,
        GE0_first_pulse_exact_20Q_clock_and_quiet_native_rows_validated=True,
        GE0_first_Workspace_whole_own_rule_or_future_native_writeback_or_later_Flag2_recovery_proved=False,
        GE0_first_Workspace_Gray_refutation_iid_or_shorter_U_proved=False,
        GE1_explicit_native_only_fifth_store_raw_holder_votes_and_radius5_validated=True,
        GE1_actual_first_native_commit_old_Nextbit_order_and_clock_phases_validated_conditionally=True,
        GE1_same_real2_actual_next_History2_History3_bank_barriers_minus1_19_validated=True,
        GE1_actual_raw_History_reset_capture_and_payload_cases_validated=True,
        GE1_next_native_bank_common_Age_extrapolation_absent_on_this_history=True,
        GE1_parent_read_only_replay_and_failure_provenance_registered=True,
        GE1_remaining_ports_own_beta_final_layout_and_computed_source_completion_premises_explicit=True,
        GE1_literal_full_fifth_own_programme_or_all_raw_Gray_refinement_proved=False,
        GE1_second_late_repair_full_period_noisy_Gray_iid_or_shorter_U_result_proved=False,
        GE2_actual_second_stage0_and_later_History_native_banks_from_GE1_shared_history_validated=True,
        GE2_actual_second_34396_tick_head_and_five_holder_courier_delivery_validated_conditionally=True,
        GE2_actual_derived_D2_zero_Flag2_and_noncommon_upper_Ages_validated=True,
        GE2_second_literal_Workspace_infinite_line_native_prefix_20Q_to23Q_validated_conditionally=True,
        GE2_unchanged_native_only_GE1_mirror_and_own_beta_layout_final_computed_source_premises_explicit=True,
        GE2_parent_read_only_replay_and_proof_only_boundary_clarification_registered=True,
        GE2_full_own_beta_literal_Gray_completion_or_later_Flag2_recovery_proved=False,
        GE2_full_period_noisy_Gray_iid_or_shorter_U_theorem_proved=False,
        GMW7_clock_bank_literal_Gray_Mailbox_clear_or_three_gather_refinement_proved=False,
        compact_word_loop_prepared_self_evaluator_with_extra_dictionary_proved=True,
        faithful_Gray_compact_self_evaluator_or_complete_encoded_period_proved=False,
        faithful_Gray_Proposition4_or_GR1_boundary_memory_refuted=False,
        GR1_arbitrary_upper_real1_adjacent_pair_boundary_map_refuted=True,
        GR1_real1_split_boundary_physical_composition_validated=True,
        intact_recursive_hierarchy_reliability_or_iid_failure_proved=False,
        GR1_width99_initial_upper_E0_pair_split_boundary_validated=True,
        GR1_split_independent_upper_operational_E0_reachability_validated=True,
        GR1_split_nearby_lower_source_failure_of_isolation_validated=True,
        split_context_global_physical_history_reachability_or_exclusion_proved=False,
        GR1_real1_or_higher_noisy_lift_proved=False,
        unconditional_gray_completion_nonexistence_proved=False,
        gacs_2001_refuted=False, global_reliability_established=False)
    (directory/'checkpoint_validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
