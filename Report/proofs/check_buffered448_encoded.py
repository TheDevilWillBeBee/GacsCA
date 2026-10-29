#!/usr/bin/env python3
"""J105: pin SP16 complete-encoding proof premises and clearing reserves.

The universal induction is written in ROBUSTNESS. These provenance and
arithmetic checks do not simulate all damaged trajectories or certify
an iid theorem. Literal maintenance identities transfer from SP14.
"""
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import proposed_sparse_framed448 as previous
import proposed_sparse_buffered448 as proposed


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out = ROOT/'figs/robustness'
    candidate = proposed.load_artifact()
    p, oldp = candidate.p, previous.parameters()
    for field in ('Q','U','k','m','nb','R','PB'):
        assert getattr(p, field) == getattr(oldp, field)
    assert proposed.proposed_build()[1] == previous.proposed_build()[1]
    schedule = json.loads((out/'SP16_symbolic_schedule.json').read_text())
    birth = json.loads((out/'SP16_buffered_incorporation_certificate.json').read_text())
    assert schedule['final_hold_equalities'] == 316 and schedule['history_ranks_checked'] == 12
    assert birth['canonical_thirteen_site_two_fault_birth_cofactors'] == 390
    assert max(schedule['early_flag_store_ages'].values()) < min(p.courier_ticks()[1:])
    assert all(row['address'] not in proposed.reserved_cells(p) for row in proposed.dependency_table(p))
    assert len(set(candidate.layout.tolist())) == candidate.W == 316
    assert p.T_wf == 27457
    source1_free = p.T_wf+2*p.Q+1
    source2_free = p.T_wf+1793
    clean_F1 = source1_free+224
    clean_flags = max(clean_F1,source2_free)+224
    E0_F1 = source1_free+252
    E0_flags = max(E0_F1,source2_free)+247
    assert (source1_free,source2_free,clean_flags,E0_flags) == (28354,29250,29474,29497)
    assert 2*251-2*((251+8)//9) >= p.Q-2
    assert 1+2*246-2*((246+10)//11) >= p.Q-1
    assert E0_flags < p.E0+p.NP*p.PL < p.U-1
    dependencies = {key:digest(out/name) for key,name in (
        ('build_receipt_sha256','SP16_program_build.json'),
        ('schedule_receipt_sha256','SP16_symbolic_schedule.json'),
        ('front_receipt_sha256','SP16_front_certificate.json'),
        ('incorporation_receipt_sha256','SP16_buffered_incorporation_certificate.json'),
        ('packet_pressure_certificate_sha256','packet_pressure_certificate.json'),
        ('guard6_certificate_sha256','packet_guard6_certificate.json'),
        ('SP14_encoding_transfer_receipt_sha256','SP14_encoding_transfer_certificate.json'),
        ('SP14_clean_closure_receipt_sha256','SP14_encoded_closure_certificate.json'),
        ('SP14_E0_closure_receipt_sha256','SP14_encoded_e0_certificate.json'),
        ('framed_service_certificate_sha256','framed_service_certificate.json'),
        ('buffered_service_certificate_sha256','buffered_framed_service_certificate.json'),
        ('SP15_encoding_receipt_sha256','SP15_encoded_certificate.json'))}
    receipt = dict(proposal='SP16',proposed_rule_change=True,active_G17_modified=False,SP14_modified=False,
        proposed_candidate_sha256=candidate.digest(),proposed_netlist_sha256=candidate.comp.digest,
        checker_sha256=digest(Path(__file__)),proposal_source_sha256=digest(Path(proposed.__file__)),
        guard_source_sha256=digest(Path(proposed.guard.__file__)),buffered_service_source_sha256=digest(Path(proposed.service.__file__)),
        SP15_proposal_source_sha256=digest(ROOT/'Report/proofs/proposed_sparse_guarded_pressure448.py'),SP15_modified=False,
        base_rule_source_sha256=digest(ROOT/'gacsca/rule_g.py'),
        actual_maintenance_source_sha256=hashlib.sha256(proposed.proposed_build()[1].encode()).hexdigest(),
        full_generated_source_sha256=hashlib.sha256(proposed.actual_net(p)[1].encode()).hexdigest(),
        Q=p.Q,U=p.U,width=candidate.W,history_ranks=12,**dependencies,
        canonical_GF_Age_with_free_pressure_identities_transfer_literally=True,
        empty_components_and_empty_packet_pressure_invariant_under_two_current_faults=True,
        packet_component_equations_unchanged_and_buffered_code_ancestry_proved_J103=True,
        canonical_adjacent_code_frames_overlap_five_cells=True,
        simultaneous_fresh_sources_count_lower_bound_does_not_require_disjoint_code_frames=True,
        coded_origin_winner_not_required_for_complete_encoding_induction=True,
        independent_per_rank_copy_gather_induction_now_uses_all_twelve_checked_ranks=True,
        extra_packet_pressure_may_extend_across_true_colony_edges_but_does_not_change_canonical_GF_Age=True,
        no_birth_clock_closed_except_T_wf_in_each_complete_period=True,
        all_components_computed_empty_by_clock=source2_free,
        pressure_zero_on_all_updates_from_empty_component_state_except_two_faults=True,
        Workspace1_source_free_clock=source1_free,Workspace2_source_free_clock=source2_free,
        all_computed_structural_flags_quiet_clean_clock=clean_flags,
        all_computed_structural_flags_quiet_E0_clock=E0_flags,
        computed_GF_Age_Flag1_only_control_physical_data=True,
        all_316_upper_outputs_use_changed_own_program=True,
        complete_initial_encoding_required=True,globally_24_24_separated_singleton_or_adjacent_pair_E0_required=True,
        boundary_full_word_identity_outside_current_overwrites=True,
        decoded_boundary_identity_for_every_period_and_every_upper_configuration=True,
        noiseless_intact_infinite_hierarchy_closure=True,
        arbitrary_damaged_colony_source_or_boundary_bootstrap_established=False,
        general_force_envelope_or_full_upper_error_map_established=False,
        iid_threshold_established=False,global_reliability_established=False,
        proof='ROBUSTNESS J105; literal maintenance/copy transfers, common-count erasure allowing overlapping buffered frames, and changed own-ROM certificate',
        scope='complete boundary encodings, noiseless and E0-only, all upper configurations; no general damaged trajectory or positive Bernoulli threshold')
    (out/'SP16_encoded_certificate.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(Q=p.Q,U=p.U,width=candidate.W,clean_flags=clean_flags,E0_flags=E0_flags,
        global_reliability_established=False)))


if __name__=='__main__':
    main()
