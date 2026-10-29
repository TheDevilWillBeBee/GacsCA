#!/usr/bin/env python3
"""Distance/timing certificates for J43's boundary-separated real core.

This verifies support arithmetic, not a CA experiment or the trajectory
induction. Near-boundary cores and general higher-island repair remain
outside the statement in ROBUSTNESS.md.
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
    table = proposed.dependency_table(p)
    threshold = 25*p.Q-15
    first_clean, second_clean = 12, 24
    radius = 2*p.Q+8*420
    positions = 0
    min_left_buffer = p.Q
    min_controlled_margin = threshold-radius
    for q in range(threshold, threshold+p.Q):
        anchor = (q+15)//p.Q-1
        assert anchor == second_clean
        assert q-61+1 > 24*p.Q  # distance from S to an arbitrary x<=-1
        assert q-radius > 0
        for gap in range(1, 6):
            left = q-gap
            assert left-208 >= anchor*p.Q
            min_left_buffer = min(min_left_buffer, left-208-anchor*p.Q)
            positions += 1
    assert positions == 2240 and min_left_buffer == 220
    assert min_controlled_margin == 6929
    paths = 0
    min_halo = p.Q**2
    for receiver in (24, 25, 26):
        for row in table:
            target = receiver*p.Q+row['address']
            for offset in [0]+row['offsets']:
                source = (receiver+offset)*p.Q+row['address']
                lower = min(target, source)-12
                assert receiver+offset >= first_clean
                assert lower >= first_clean*p.Q+47
                min_halo = min(min_halo, lower)
                paths += 1
    assert min_halo == 5467 >= first_clean*p.Q+47
    assert second_clean-12 == first_clean
    latest_align = latest_quiet = 0
    for tau in range(p.U):
        g = max(p.U, tau+420)
        assert tau+61 < g
        align = g-p.U
        quiet = align+500
        assert align <= 419 and quiet <= 919 < p.gathers_q[1]*p.Q
        latest_align = max(latest_align, align)
        latest_quiet = max(latest_quiet, quiet)
    assert (latest_align, latest_quiet) == (419, 919)
    _, left_load, right_load = p.courier_ticks()
    phases = []
    for clock in range(p.U):
        hit = False
        for cycle in (0, 1):
            start, stop = cycle*p.U+p.T_wf, cycle*p.U+p.T_wf+2*p.Q-1
            if start <= clock+2 and clock <= stop:
                hit = True
                assert cycle == 0
                assert max(left_load, right_load) < clock
                assert clock+2 < p.U-1
                assert clock > 9633
        if hit:
            phases.append(clock)
    assert [min(phases), max(phases)] == [25343, 26240]
    assert len(phases) == 898
    dependencies = ('SP4_program_build.json', 'SP4_maintenance_certificate.json',
                    'SP4_symbolic_schedule.json', 'SP4_gather_repair_certificate.json',
                    'SP4_autonomy_certificate.json', 'SP4_period_repair_certificate.json',
                    'SP4_operational_certificate.json', 'SP4_localization_certificate.json',
                    'SP4_nested_halfline_certificate.json')
    result = dict(
        proposal='SP4', proposed_rule_change=True, active_G17_modified=False,
        proposed_candidate_sha256=candidate.digest(), proposed_netlist_sha256=candidate.comp.digest,
        proposal_source_sha256=digest(Path(proposed.__file__)), checker_sha256=digest(Path(__file__)),
        Q=p.Q, U=p.U, core_right_point_minimum_distance=threshold,
        minimum_upper_pair_anchor=second_clean,
        first_boundary_pristine_word_domain_start=first_clean,
        second_boundary_pristine_word_domain_start=second_clean,
        closest_pair_positions_checked=positions, private_capture_paths_checked=paths,
        minimum_lower_capture_halo_position=min_halo,
        minimum_raw_left_alias_buffer=min_left_buffer,
        controlled_geometry_cone_radius=radius, minimum_controlled_left_margin=min_controlled_margin,
        all_core_ticks_checked=p.U, latest_alignment_into_second_period=latest_align,
        latest_quiet_into_second_period=latest_quiet,
        upper_clock_phases_checked=p.U, conservative_active_two_tick_phase_count=len(phases),
        active_two_tick_phase_range=[min(phases), max(phases)],
        fresh_upper_courier_loads_precede_every_such_phase=True,
        decoder_convention='computed boundary before fresh noise',
        proof_receipt_sha256={name:digest(out / name) for name in dependencies},
        trajectory_induction_is_separate=True, near_boundary_real_cores_covered=False,
        arbitrary_many_real_cores_covered=False, universal_higher_island_repair_established=False,
        global_reliability_established=False,
        scope='support/timing for one real level1 core separated from an arbitrary left half-line; J43 trajectory proof separate')
    (out / 'SP4_boundary_separated_core_certificate.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(dict(core_distance=threshold, closest_pair_cases=positions,
                          private_paths=paths, first_pristine_domain=first_clean,
                          second_pristine_domain=second_clean, upper_clock_phases=p.U)), flush=True)


if __name__ == '__main__':
    main()
