#!/usr/bin/env python3
"""Local identities/timing for the separate coupled right-boundary proof.

Both geometry votes agree in the canonical alias strip, independently
of every flag/Workspace value. The trajectory induction is separate;
this does not certify the first-boundary-colony or repeated-core cases.
"""
import hashlib
from itertools import combinations
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from gacsca.netlist import Net, const_word, mixed_age_increment
from check_fast_flag_proposal import invoke
import proposed_sparse_prefix448 as proposed
import prefix_selection as selection


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    candidate = proposed.load_artifact()
    p = candidate.p
    out = ROOT / 'figs/robustness'
    build, source = selection.proposed_build(symbolic=True)
    cases = 0
    for address in range((1 << p.k)-p.Q):
        for faults in combinations(range(-5, 6), 2):
            net = Net()
            clock = [net.input(('common_clock', bit)) for bit in range(p.m)]
            cells = {}
            for offset in range(-5, 9):
                if offset >= 6:
                    cells[offset] = dict(f1=net.input((offset, 'f1')))
                    continue
                bad = offset in faults
                cells[offset] = dict(
                    addr=[net.input((offset, 'addr', bit)) for bit in range(p.k)] if bad
                         else const_word((address+offset) % p.Q, p.k),
                    age=[net.input((offset, 'age', bit)) for bit in range(p.m)] if bad else clock,
                    **{field:net.input((offset, field)) for field in ('f1', 'f2', 'wf1', 'wf2')})
            result = invoke(build, net, cells, p)
            assert result['addr'] == const_word(address, p.k)
            assert result['age_now'] == clock
            assert result['age'] == mixed_age_increment(net, clock, p.PB, p.R, p.nb)
            cases += 1
    assert cases == 3520

    threshold = 2*p.Q-15
    positions = 0
    min_buffer = min_phase_front = min_forcing_gap = p.Q**2
    for q in range(threshold, threshold+p.Q):
        anchor = (q+15)//p.Q-1
        assert anchor == 1
        assert q-61 > p.Q+68
        for gap in range(1, 6):
            left = q-gap
            phase_front = left-208
            assert phase_front >= anchor*p.Q+220
            assert phase_front > anchor*p.Q+68
            min_phase_front = min(min_phase_front, phase_front)
            min_buffer = min(min_buffer, phase_front-anchor*p.Q)
            min_forcing_gap = min(min_forcing_gap, q-61-(anchor*p.Q+68))
            positions += 1
    assert threshold == 881 and positions == 2240
    assert (min_phase_front, min_buffer, min_forcing_gap) == (668, 220, 304)
    assert p.Q-5 > 0
    alias_halo = [p.Q-5, p.Q+68]
    early = late = 0
    last_early_align = last_early_quiet = 0
    for tau in range(p.U):
        if tau <= 9634:
            align, quiet = tau+420, tau+920
            assert quiet <= 10554 < p.E0-1 < p.T_wf
            last_early_align = max(last_early_align, align)
            last_early_quiet = max(last_early_quiet, quiet)
            early += 1
        else:
            assert 9633+1 < tau
            late += 1
        g = max(p.U, tau+420)
        assert tau+61 < g
        assert g-p.U <= 419 and g-p.U+500 <= 919 < p.gathers_q[1]*p.Q
    assert (early, late) == (9635, 57949)
    assert (last_early_align, last_early_quiet) == (10054, 10554)
    assert min(row['address']-12 for row in proposed.dependency_table(p)) == 47
    deps = ('SP4_program_build.json', 'SP4_maintenance_certificate.json',
            'SP4_symbolic_schedule.json', 'SP4_barrier_certificate.json',
            'SP4_gather_repair_certificate.json', 'SP4_autonomy_certificate.json',
            'SP4_period_repair_certificate.json', 'SP4_operational_certificate.json',
            'SP4_localization_certificate.json', 'SP4_nested_halfline_certificate.json',
            'SP4_boundary_separated_core_certificate.json')
    result = dict(
        proposal='SP4', proposed_rule_change=True, active_G17_modified=False,
        proposed_candidate_sha256=candidate.digest(), proposed_netlist_sha256=candidate.comp.digest,
        proposal_source_sha256=digest(Path(proposed.__file__)), checker_sha256=digest(Path(__file__)),
        selection_source_sha256=digest(ROOT / 'Report/proofs/prefix_selection.py'),
        majority_shortcut_sha256=digest(ROOT / 'Report/proofs/check_right_barrier.py'),
        actual_maintenance_source_sha256=hashlib.sha256(source.encode()).hexdigest(),
        alias_strip_addresses_checked=64, alias_strip_two_fault_symbolic_cases=cases,
        alias_strip_flag_and_Workspace_inputs_arbitrary=True, common_clock_bits_free=p.m,
        core_right_point_minimum_distance=threshold, minimum_upper_pair_anchor=1,
        closest_pair_positions_checked=positions, minimum_phase_front_position=min_phase_front,
        minimum_raw_alias_buffer=min_buffer, minimum_S_distance_beyond_alias_input_halo=min_forcing_gap,
        first_alias_strip_input_halo=alias_halo, inside_source_capture_margin=47,
        first_period_core_ticks_checked=p.U, early_core_phase_count=early,
        post_gather_core_phase_count=late, latest_early_alignment=last_early_align,
        latest_early_quiet=last_early_quiet, early_alignment_before_first_Workspace=True,
        maximum_alignment_into_second_period=419, maximum_quiet_into_second_period=919,
        decoder_convention='computed boundary before fresh noise',
        classification_scope='right restricted forcing; arbitrary left forcing need not be globally E0',
        proof_receipt_sha256={name:digest(out / name) for name in deps},
        trajectory_induction_is_separate=True, first_right_lower_colony_core_covered=False,
        arbitrary_many_real_cores_covered=False, universal_higher_island_repair_established=False,
        global_reliability_established=False,
        scope='canonical alias-strip identity with arbitrary flags, and support/stage arithmetic; J45/J46 trajectory inductions separate')
    (out / 'SP4_near_boundary_core_certificate.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(dict(alias_strip_cases=cases, core_distance=threshold,
                          first_phase_front=min_phase_front, early=early, post_gather=late)), flush=True)


if __name__ == '__main__':
    main()
