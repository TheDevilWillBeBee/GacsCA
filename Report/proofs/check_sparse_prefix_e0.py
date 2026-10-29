#!/usr/bin/env python3
"""Finite combinatorial certificates for SP3 mixed-E0 maintenance proofs.

These are necessary-support masks and telescoping inequalities, not CA
trajectory samples. ROBUSTNESS J24--J27 give the unbounded inductions.
Q400/Q448 rows describe changed maintenance constants, not built ROMs.
"""
import hashlib
from itertools import product
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import proposed_sparse_prefix as proposed


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def possible_second(n0, n1, x):
    """Necessary conditions only; prefix endpoint is zero."""
    def bad0(y):
        return y > 0 or y in n0

    def bad1(y):
        return y in n1 or any(sum(bad0(y+s*j) for j in range(1, 6)) >= 3
                              for s in (-1, 1))

    def quiet1(y, address):
        if y in n1:
            return True
        right_support = sum(bad0(y+j) for j in range(1, 6)) >= 3
        good_inside_left = sum(not bad0(y-j) for j in range(1, min(address, 5)+1))
        return right_support and good_inside_left <= 2

    if sum(bad1(x-j) for j in range(1, 6)) >= 3:
        return True
    return any(sum(not bad1(x-j) for j in range(1, address+1)) <= 2 and
               sum(quiet1(x+j, address+j) for j in range(1, 6)) >= 3
               for address in range(5))


def local_masks():
    assert not any(possible_second(set(), set(), x) for x in range(-9, -1))
    rows, templates = [], []
    for layer, width, start in product((0, 1), (1, 2), range(-15, 5)):
        group = set(range(start, start+width))
        n0, n1 = (group, set()) if layer == 0 else (set(), group)
        possible = [x for x in range(-9, -1) if possible_second(n0, n1, x)]
        prefix = min(possible)-1 if possible else -2
        charge = -2-prefix
        assert 0 <= charge <= 4
        rows.append(dict(input_layer=layer, group_width=width, group_start=start,
                         earliest_possible_wrong_output=min(possible) if possible else None,
                         guaranteed_prefix=prefix, extra_retreat_charge=charge))
        if charge:
            templates.append((layer, width, start, charge))
    assert len(templates) == 18
    return dict(relevant_point_zone=[-14, 4], consecutive_input_ticks=2,
                mutually_separated_groups_in_zone_at_most=1,
                no_group_prefix_loss=2, maximum_loss_with_one_group=6,
                cases=rows, charged_templates=templates,
                all_outputs_at_or_left_of_minus_ten_good_by_two_generic_growth_updates=True,
                statement='computed residue/exact-Age prefix p becomes p-2-charge after two updates; stored direct faults kept separate')


def minimum_gap(a, b):
    layer, width, offset, charge = a
    next_layer, next_width, next_offset, _ = b
    for blocks in range(1, 20):
        time_distance = 2*blocks+next_layer-layer
        spatial_distance = 2*blocks+charge+offset-next_offset-(next_width-1)
        if time_distance >= 24 or spatial_distance >= 24:
            return blocks
    raise AssertionError('missing gap')


def retreat_packing(templates):
    # Potential in half-units; verify every ordered template transition.
    potential = [-4 if row in ((0, 1, -3, 2), (0, 2, -4, 3)) else 0
                 for row in templates]
    gaps = []
    for i, a in enumerate(templates):
        for j, b in enumerate(templates):
            gap = minimum_gap(a, b)
            assert 4*gap-11*a[3] >= potential[j]-potential[i]
            gaps.append(gap)
    # Last event costs at most four; endpoint potential range is four.
    return dict(transition_cases=len(gaps), minimum_event_gap_in_blocks=min(gaps),
                half_unit_potential=potential, potential_range=4,
                verified_inequality='4 gap - 11 previous_charge >= next_potential-previous_potential',
                accumulated_charge_upper_bound='4 + floor(4N/11) in N two-update blocks',
                even_time_prefix_loss_upper_bound='t+4+floor(2t/11)',
                even_time_retreat_rate_upper_bound='13/11')


def advance_packing():
    rows = []
    for width in (1, 2):
        for start in range(-5, 1):
            count = len(set(range(start, start+width)).intersection(range(-4, 1)))
            if not count:
                continue
            assert 27*count <= 2*(count+width-1+24)
            rows.append((width, start, count))
    return dict(event_templates=rows, input_zone=[-4, 0],
                conditional_one_step_advance='3-current_fault_count_in_zone',
                sum_of_nonlast_event_costs_upper_bound='3(T-1)+5',
                accumulated_fault_count_upper_bound='2+floor((6T+4)/27)',
                advance_lower_bound='3T-2-floor((6T+4)/27) for T>=1',
                hypothesis='quiet wrong outputs with Address 0,...,4 excluded at and beyond prefix minus four')


def retreat_loss(tick):
    assert tick % 2 == 0
    return tick+4+2*tick//11


def advance(ticks):
    return 0 if ticks == 0 else 3*ticks-2-(6*ticks+4)//27


def ancestry_displacement(ticks):
    return 3*ticks-2*((ticks+5)//6)


def normalization_updates(Q):
    strip_width = 512-Q
    return next(t for t in range(1, 100) if ancestry_displacement(t) >= strip_width)


def flag_clearance_reserve(Q):
    flag1 = 1+next(t for t in range(1000) if 2*t-2*((t+8)//9) >= Q-2)
    flag2 = 1+next(t for t in range(1000) if 1+2*t-2*((t+10)//11) >= Q-1)
    return dict(Workspace_reset_updates=1, Flag1_updates=flag1,
                Flag2_updates=flag2, total=1+flag1+flag2)


def sustained_window(Q, width, startup):
    prefix = -1-retreat_loss(startup)
    Cminus1 = width+Q-2
    duration = next(t for t in range(1000) if prefix+advance(t) >= Cminus1)
    minimum_initial_slack = 10**9
    minimum_near_end_slack = 10**9
    first_failure = None
    for elapsed in range(duration):
        T = startup+elapsed+1
        x = prefix+advance(elapsed)-4
        initial_slack = x+ancestry_displacement(T)-(width-1)
        minimum_initial_slack = min(minimum_initial_slack, initial_slack)
        if initial_slack <= 0 and first_failure is None:
            first_failure = dict(stop='initial', elapsed=elapsed, slack=initial_slack)
        for address in range(5):
            D = Q-5-address
            s = T-(D+4)//5
            if s < 0:
                continue
            right_edge = min(Cminus1, width-1+3*s+2*(1+3*s//23))
            slack = x+D-right_edge
            minimum_near_end_slack = min(minimum_near_end_slack, slack)
            if slack <= 0 and first_failure is None:
                first_failure = dict(stop='near-end', elapsed=elapsed,
                                     Address=address, slack=slack)
    padding = max(retreat_loss(startup), retreat_loss(startup-2)+5)
    norm = normalization_updates(Q)
    return dict(Q=Q, seed_width=width, even_startup=startup, advance_duration=duration,
                phase_and_Age_repair_bound=startup+duration,
                raw_geometry_repair_bound=startup+duration+norm,
                all_flags_clearance_bound=startup+duration+norm+flag_clearance_reserve(Q)['total'],
                maximum_left_phase_expansion=padding,
                two_true_colonies=width+padding < Q,
                minimum_initial_ancestor_slack=minimum_initial_slack,
                minimum_near_end_ancestor_slack=minimum_near_end_slack,
                closes=first_failure is None, first_failure=first_failure,
                proposed_constants=Q != 384, full_self_simulation_ROM_built=Q == 384)


def main():
    local = local_masks()
    certificates = [sustained_window(Q, width, startup) for Q, width, startup in
                    ((384, 133, 94), (400, 141, 100), (448, 141, 100), (448, 160, 112))]
    assert all(row['closes'] and row['two_true_colonies'] for row in certificates)
    assert [(r['phase_and_Age_repair_bound'], r['raw_geometry_repair_bound']) for r in certificates] == [
        (322, 370), (339, 381), (357, 381), (380, 404)]
    for Q, width, startup in ((384, 133, 94), (400, 141, 100), (448, 160, 112)):
        for smaller in range(1, width+1):
            row = sustained_window(Q, smaller, startup)
            assert row['closes'] and row['two_true_colonies']
    failed = sustained_window(384, 141, 100)
    assert failed['closes'] is False
    candidate = proposed.load_artifact()
    out = ROOT / 'figs/robustness'
    result = dict(proposal='SP3', proposed_rule_change=True, active_G17_modified=False,
                  proposed_candidate_sha256=candidate.digest(), proposed_netlist_sha256=candidate.comp.digest,
                  checker_sha256=digest(Path(__file__)),
                  proposal_source_sha256=digest(Path(proposed.__file__)),
                  selection_source_sha256=digest(ROOT / 'Report/proofs/prefix_selection.py'),
                  prefix_proof_receipt_sha256=digest(out / 'SP3_prefix_selection_certificate.json'),
                  ancestry_proof_receipt_sha256=digest(out / 'quiet_majority_proposal_certificate.json'),
                  growth_proof_receipt_sha256=digest(out / 'geometry_growth_certificate.json'),
                  local_masks=local, retreat_packing=retreat_packing(local['charged_templates']),
                  advance_packing=advance_packing(), sustained_windows=certificates,
                  failed_width_141_Q384_sufficient_estimate=failed,
                  noisy_alias_normalization_updates={str(q): normalization_updates(q) for q in (384, 400, 448)},
                  flag_clearance_reserves={str(q): flag_clearance_reserve(q) for q in (384, 400, 448)},
                  Q400_not_supported_by_current_q_multiple_of_64_check=True,
                  Q448_not_a_built_or_verified_self_simulating_candidate=True,
                  global_reliability_established=False,
                  scope='finite support-mask and packing arithmetic for the unbounded mixed-E0 maintenance induction; not experiments or an iid theorem')
    (out / 'SP3_E0_prefix_certificate.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(dict(sustained_windows=certificates,
                          Q384_width141_estimate=failed), indent=2))


if __name__ == '__main__':
    main()
