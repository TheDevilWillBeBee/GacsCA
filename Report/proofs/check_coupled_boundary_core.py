#!/usr/bin/env python3
"""Support/timing for SP4's one-core coupled boundary argument J46.

This checks the geometry collars, inside-source paths, group timing and
two-step upper signal cases. The trajectory induction is separate in
ROBUSTNESS.md. Neither a higher-island eroder nor iid reliability follows.
"""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import proposed_sparse_prefix448 as proposed


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    candidate = proposed.load_artifact()
    p = candidate.p
    out = ROOT / 'figs/robustness'
    modules = json.loads((out / 'SP4_boundary_pair_modules_certificate.json').read_text())
    assert modules['conditional_boundary_copy_outputs_checked'] == 3240
    assert modules['literal_Workspace_signal_identity_cases'] == 288
    assert modules['pair_anchors_checked'] == list(range(1, 25))
    table = proposed.dependency_table(p)
    minimum, far = 2*p.Q-15, 25*p.Q-15
    positions = 0
    min_alias = min_forcing = min_front = p.Q**2
    anchors = set()
    for q in range(minimum, far):
        anchor = (q+15)//p.Q-1
        anchors.add(anchor)
        assert 1 <= anchor <= 23
        assert q-61 >= anchor*p.Q+372 > p.Q-1
        assert (q+15)//p.Q+1 == anchor+2
        for gap in range(1, 6):
            left = q-gap
            front = left-208
            assert front >= anchor*p.Q+220
            assert front-14 > 0
            min_alias = min(min_alias, front-anchor*p.Q)
            min_front = min(min_front, front)
            min_forcing = min(min_forcing, q-61-(anchor*p.Q+68))
            positions += 1
    assert anchors == set(range(1, 24))
    assert positions == 23*p.Q*5 == 51520
    assert (min_alias, min_forcing, min_front) == (220, 304, 668)
    # Core/protected/boundary receivers: exterior operands are allowed,
    # but every inside source has a path wholly within the right domain.
    paths = exterior = 0
    min_halo = p.Q**2
    for receiver in range(26):
        for row in table:
            target = receiver*p.Q+row['address']
            for offset in [0]+row['offsets']:
                source_index = receiver+offset
                if source_index < 0:
                    exterior += 1
                    continue
                source = source_index*p.Q+row['address']
                halo = min(source, target)-12
                assert halo >= 47
                min_halo = min(min_halo, halo)
                paths += 1
    assert min_halo == 47
    groups = [(g*p.Q, g*p.Q+674) for g in p.gathers_q]
    assert groups == [(0, 674), (4480, 5154), (8960, 9634)]
    early = late = 0
    for tau in range(p.U):
        if tau <= 9634:
            assert tau+920 <= 10554 < p.E0-1 < p.T_wf
            assert sum(a <= tau+920 and tau <= b for a,b in groups) <= 1
            early += 1
        else:
            assert groups[-1][1] < tau
            late += 1
        g = max(p.U, tau+420)
        assert tau+61 < g
        assert g-p.U <= 419 and g-p.U+500 <= 919 < p.gathers_q[1]*p.Q
    assert (early, late) == (9635, 57949)
    assert 24-12 == 12
    _, left_load, right_load = p.courier_ticks()
    assert (left_load, right_load, p.T_sig, p.T_wf) == (25288, 25287, 25344, 25345)
    assert p.T_sig+1 == p.T_wf
    # An installed signal or the final preceding pulse suffices for two
    # upper transitions. A courier is a one-tick pulse, not an assertion
    # that the whole Mail track stays zero throughout Workspace.
    phase_cases = []
    for sigma in range(p.U):
        hit = any(cycle*p.U+p.T_wf <= sigma+2 and
                  sigma <= cycle*p.U+p.T_wf+2*p.Q-1 for cycle in (0, 1))
        if not hit:
            continue
        assert 25343 <= sigma <= 26240 and sigma+2 < p.U-1
        assert max(left_load, right_load) < sigma
        if sigma == p.T_sig-1:
            assert left_load+1+(p.lo-4) == sigma
            assert right_load+1+((p.Q-4)-(p.hi-1)) == sigma
            provenance = 'preceding pulse: ML4 and MR444 at onset, then ML3/MR445 in first output'
        elif sigma == p.T_sig:
            provenance = 'pulse already at ML3/MR445 at onset'
        else:
            assert sigma > p.T_sig
            provenance = 'zero signal already installed; no later signal/commit in two steps'
        phase_cases.append(dict(onset_clock=sigma, zero_provenance=provenance))
    assert len(phase_cases) == 898
    dependencies = ('SP4_program_build.json', 'SP4_maintenance_certificate.json',
                    'SP4_symbolic_schedule.json', 'SP4_barrier_certificate.json',
                    'SP4_gather_repair_certificate.json', 'SP4_autonomy_certificate.json',
                    'SP4_period_repair_certificate.json', 'SP4_operational_certificate.json',
                    'SP4_localization_certificate.json', 'SP4_nested_halfline_certificate.json',
                    'SP4_boundary_separated_core_certificate.json',
                    'SP4_near_boundary_core_certificate.json',
                    'SP4_boundary_pair_modules_certificate.json')
    result = dict(
        proposal='SP4', proposed_rule_change=True, active_G17_modified=False,
        proposed_candidate_sha256=candidate.digest(), proposed_netlist_sha256=candidate.comp.digest,
        proposal_source_sha256=digest(Path(proposed.__file__)), checker_sha256=digest(Path(__file__)),
        Q=p.Q, U=p.U, core_right_point_minimum_distance=minimum,
        newly_checked_distance_interval=[minimum, far-1], pair_anchors_checked=sorted(anchors),
        closest_pair_positions_checked=positions, minimum_raw_alias_buffer=min_alias,
        minimum_forcing_to_alias_input_margin=min_forcing, minimum_phase_front=min_front,
        inside_source_capture_paths_checked=paths, exterior_operand_paths_permitted=exterior,
        minimum_inside_source_halo=min_halo, capture_receivers_checked=list(range(26)),
        first_boundary_pristine_word_domain_start=12, second_boundary_pristine_word_domain_start=24,
        gather_groups=groups, all_first_period_core_ticks_checked=p.U,
        early_core_phase_count=early, post_gather_core_phase_count=late,
        maximum_second_period_alignment=419, maximum_second_period_quiet=919,
        upper_clock_phases_checked=p.U, threatened_two_step_clock_range=[25343, 26240],
        threatened_two_step_clock_count=len(phase_cases), signal_pulse_cases=phase_cases,
        decoder_convention='computed before fresh boundary replacements',
        proof_receipt_sha256={name:digest(out / name) for name in dependencies},
        trajectory_induction_is_separate=True, first_right_lower_colony_core_repaired=False,
        arbitrary_many_real_cores_covered=False, repeated_core_damaged_input_induction_established=False,
        universal_higher_island_repair_established=False, global_reliability_established=False,
        scope='support/timing for one near-boundary real core at all first-period phases; J46 trajectory proof separate')
    (out / 'SP4_coupled_boundary_core_certificate.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(dict(closest_pair_cases=positions, inside_source_paths=paths,
                          exterior_paths=exterior, signal_pulse_cases=len(phase_cases))), flush=True)


if __name__ == '__main__':
    main()
