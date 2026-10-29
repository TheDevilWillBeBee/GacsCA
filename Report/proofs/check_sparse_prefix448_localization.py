#!/usr/bin/env python3
"""SP4 colony-edge closure and simultaneous-capture locality identities.

These are local Boolean and integer identities. The simultaneous noisy
trajectory proof is separate; this checker alone does not establish it.
"""
import hashlib
import json
from itertools import combinations
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from gacsca.netlist import Net, const_word, mixed_age_increment
import proposed_sparse_prefix448 as proposed
import prefix_selection as selection
from check_fast_flag_proposal import invoke


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def closed_colony_case(p, build, address, faults):
    n = Net()
    age = [n.input(('common_clock', bit)) for bit in range(p.m)]
    cells = {}
    for offset in range(-5, 9):
        outside = not 0 <= address+offset < p.Q
        faulty = offset in faults
        if offset >= 6:
            cells[offset] = dict(f1=n.input((offset, 'f1')) if outside or faulty else 0)
            continue
        bad_geometry = address+offset < 0 or faulty
        cells[offset] = dict(
            addr=[n.input((offset, 'addr', bit)) for bit in range(p.k)] if bad_geometry
                 else const_word((address+offset) % p.Q, p.k),
            age=[n.input((offset, 'age', bit)) for bit in range(p.m)] if bad_geometry else age,
            **{field: n.input((offset, field)) if outside or faulty else 0
               for field in ('f1', 'f2', 'wf1', 'wf2')})
    result = invoke(build, n, cells, p)
    assert result['addr'] == const_word(address, p.k)
    assert result['age_now'] == age
    assert result['age'] == mixed_age_increment(n, age, p.PB, p.R, p.nb)
    assert result['f1'] == result['f2'] == 0


def main():
    candidate = proposed.load_artifact()
    p = candidate.p
    out = ROOT / 'figs/robustness'
    coordinates = tuple(range(-5, 9))
    masks = list(combinations(coordinates, 2))
    masks += [faults for count in (3, 4) for faults in combinations(coordinates, count)
              if all(sum(start <= x < start+11 for x in faults) <= 2 for start in range(-5, -1))]
    assert len(masks) == 161
    edges = (*range(5), *range(p.Q-8, p.Q))
    build, source = selection.proposed_build(symbolic=True)
    cases = 0
    for address in edges:
        for faults in masks:
            closed_colony_case(p, build, address, faults)
            cases += 1
    assert cases == 2093
    paths = 0
    maximum_path_span = 0
    smallest_left_margin = p.Q*2
    protected_halos = 0
    table = proposed.dependency_table(p)
    offsets = sorted({offset for row in table for offset in row['offsets']})
    assert min(offsets) == -12 and max(offsets) == 12
    for row in table:
        target = row['address']
        for offset in row['offsets']:
            source_position = target+offset*p.Q
            lo, hi = min(target, source_position)-12, max(target, source_position)+12
            span = hi-lo
            assert span <= 12*p.Q+24 < 22*p.Q+1
            maximum_path_span = max(maximum_path_span, span)
            paths += 1
    for q in range(p.Q):
        anchor = (q+15)//p.Q-1
        C = (anchor+2)*p.Q
        left, right = anchor*p.Q, C-1
        for gap in range(1, 6):
            margin = q-gap-208-left
            assert margin >= 220
            smallest_left_margin = min(smallest_left_margin, margin)
        geometry_radius = 2*p.Q+8*420
        foreign = [(anchor-24)*p.Q, (anchor-22)*p.Q-1,
                   (anchor+24)*p.Q, (anchor+26)*p.Q-1]
        assert q-geometry_radius > foreign[1]
        assert q+geometry_radius < foreign[2]
        # Own recovery colonies and first protected colony. Their capture
        # halos can meet their own pair but cannot meet another recent pair.
        for receiver in (anchor, anchor+1, anchor+2):
            lo = (receiver-12)*p.Q+int(candidate.layout.min())-12
            hi = (receiver+12)*p.Q+int(candidate.layout.max())+12
            assert lo > foreign[1] and hi < foreign[2]
            protected_halos += 1
    assert smallest_left_margin == 220
    assert geometry_radius == 4256
    assert maximum_path_span == 5400
    groups = [(0, 674), (4480, 5154), (8960, 9634)]
    current_overlap = {}
    for tau in range(p.U):
        hit = sum(a <= tau+920 and tau <= b for a,b in groups)
        assert hit <= 1
        current_overlap[hit] = current_overlap.get(hit, 0)+1
    assert sum(a <= 919 and 0 <= b for a,b in groups) == 1
    receipt = dict(
        proposal='SP4', proposed_rule_change=True, active_G17_modified=False,
        proposed_candidate_sha256=candidate.digest(), proposed_netlist_sha256=candidate.comp.digest,
        proposal_source_sha256=digest(Path(proposed.__file__)), checker_sha256=digest(Path(__file__)),
        selection_source_sha256=digest(ROOT / 'Report/proofs/prefix_selection.py'),
        actual_local_source_sha256=hashlib.sha256(source.encode()).hexdigest(),
        build_receipt_sha256=digest(out / 'SP4_program_build.json'),
        maintenance_receipt_sha256=digest(out / 'SP4_maintenance_certificate.json'),
        operational_receipt_sha256=digest(out / 'SP4_operational_certificate.json'),
        autonomy_receipt_sha256=digest(out / 'SP4_autonomy_certificate.json'),
        upper_map_receipt_sha256=digest(out / 'SP4_upper_map_certificate.json'),
        colony_edge_addresses=list(edges), colony_edge_masks=len(masks),
        colony_edge_symbolic_cases=cases, common_clock_bits_free=p.m,
        own_colony_flags_quiet=True, outside_colony_flags_arbitrary=True,
        left_outside_geometry_arbitrary=True, first_right_outside_geometry_canonical=True,
        flags_and_geometry_close_under_eleven_site_density=True,
        sparse_capture_paths_checked=paths, maximum_capture_support_span=maximum_path_span,
        two_recent_pair_regions_minimum_point_gap=22*p.Q+1,
        private_colony_capture_halos_checked=protected_halos,
        geometry_controlled_cone_radius=geometry_radius,
        geometric_damage_margin_at_pair_left=smallest_left_margin,
        current_core_capture_group_overlap=current_overlap,
        previous_core_quiet_deadline_into_period=919,
        all_step_trajectory_proof_established_by_this_checker=False,
        global_reliability_established=False,
        scope='actual quiet-colony edge identities and finite support/deadline arithmetic; simultaneous trajectory validity is a separate obligation')
    (out / 'SP4_localization_certificate.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(dict(edge_cases=cases, capture_paths=paths, max_capture_span=maximum_path_span,
                          private_halos=protected_halos, controlled_geometry_radius=geometry_radius)), flush=True)


if __name__ == '__main__':
    main()
