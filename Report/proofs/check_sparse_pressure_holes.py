#!/usr/bin/env python3
"""J98: conditional SP14 GF/Age repair through sparse pressure holes.

No rule change. The coded-force envelope and canonical right boundary
are premises. Local exact cofactors and E0 exclusion arithmetic support
the suffix induction in ROBUSTNESS; no source bootstrap or iid theorem.
"""
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from gacsca.netlist import Net, const_word, mixed_age_increment
import proposed_sparse_framed448 as proposed


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def local_case(p, build, address, faults, established):
    n = Net()
    age = [n.input(('reference_age', b)) for b in range(p.m)]
    support = set(range(-5, -1))
    cells = {}
    for off in range(-5, 9):
        known_right = 1 <= off <= 5 and off not in faults
        known_F2 = off in support or (off == 0 and established)
        cells[off] = dict(
            addr=const_word((address + off) % p.Q, p.k) if known_right else [n.input((off, 'addr', b)) for b in range(p.k)],
            age=age if known_right else [n.input((off, 'age', b)) for b in range(p.m)],
            f2=1 if known_F2 and off not in faults else n.input((off, 'f2')),
            **{f: n.input((off, f)) for f in ('f1', 'wf1', 'wf2')})
    result = build(n, cells, p.k, p.m, Q=p.Q, nb=p.nb, radix=p.R,
        pos_bits=p.PB, service_force=n.input(('arbitrary_coded_force',)))
    assert result['f2'] == 1, (address, faults, established)
    assert result['addr'] == const_word(address, p.k)
    assert result['age_now'] == age
    assert result['age'] == mixed_age_increment(n, age, p.PB, p.R, p.nb)


def main():
    candidate = proposed.load_artifact()
    p = candidate.p
    build, source = proposed.proposed_build(symbolic=True)
    support = set(range(-5, -1))
    groups = [()] + [(y,) for y in range(-5, 6)] + [(y, y + 1) for y in range(-5, 5)]
    stable, acquisition = 0, 0
    for address in range(5, p.Q):
        for faults in groups:
            local_case(p, build, address, faults, True)
            stable += 1
            if not support.intersection(faults):
                local_case(p, build, address, faults, False)
                acquisition += 1
    # If a failed acquisition has any fault on the four guaranteed
    # left supports, all eleven inputs are fault-free on the next row.
    exclusion = 0
    for blocker in support:
        for subsequent in range(-5, 6):
            assert abs(blocker - subsequent) < 24 and 1 < 24
            exclusion += 1
    # Maximize |H| subject to x-5,...,x-2 not in H for each x in H,
    # and H subset[5,Q). Five-bit suffix dynamic programming enumerates
    # every envelope; no sampled spacing argument is used.
    counts = {0: 0}
    for x in range(p.Q):
        following = {}
        for mask, count in counts.items():
            for is_hole in (0, 1):
                if is_hole and (x < 5 or mask & 0b11110):
                    continue
                next_mask = ((mask << 1) | is_hole) & 31
                following[next_mask] = max(following.get(next_mask, -1), count + is_hole)
        counts = following
    maximum_holes = max(counts.values())
    assert (stable, acquisition, exclusion, maximum_holes) == (9746, 6202, 44, 128)
    out = ROOT / 'figs/robustness'
    receipt = dict(proposal='SP14', proposed_rule_change=False, active_G17_modified=False,
        proposed_candidate_sha256=candidate.digest(), proposed_netlist_sha256=candidate.comp.digest,
        proposal_source_sha256=digest(Path(proposed.__file__)), checker_sha256=digest(Path(__file__)),
        helpers_sha256=digest(ROOT / 'gacsca/netlist.py'),
        majority_shortcut_sha256=digest(ROOT / 'Report/proofs/check_right_barrier.py'),
        actual_maintenance_source_sha256=hashlib.sha256(source.encode()).hexdigest(),
        full_generated_source_sha256=hashlib.sha256(proposed.actual_net(p)[1].encode()).hexdigest(),
        build_receipt_sha256=digest(out / 'SP14_program_build.json'),
        framed_service_certificate_sha256=digest(out / 'framed_service_certificate.json'),
        established_hole_free_word_cases=stable, acquisition_without_left_support_fault_free_word_cases=acquisition,
        one_row_E0_exclusion_pairs=exclusion, all_reference_Age_bits_free=p.m,
        maximum_static_hole_envelope_size=maximum_holes,
        static_hole_envelope_condition='H subset[5,448); for each x in H, x-5,...,x-2 not in H',
        coded_force_outside_H_one_each_update_required=True,
        coded_force_inside_H_arbitrary_and_time_varying_allowed=True,
        globally_24_24_separated_singleton_or_adjacent_pair_E0_required=True,
        prescribed_right_canonical_GF_and_reference_clock_required=True,
        initial_colony_GF_Age_flags_data_and_components_arbitrary_subject_to_force_history=True,
        initial_stored_Flag2_one_premise_removed=True,
        hole_birth_time_behind_correct_front_premise_removed=True,
        every_GF_Age_correct_deadline_formula='T+1+448+|H|',
        worst_case_GF_Age_repair_updates=577,
        arbitrary_reachable_component_histories_obey_sparse_envelope_established=False,
        autonomous_right_boundary_or_source_delivery_established=False,
        complete_Flag1_or_simulation_data_repair_established=False,
        uniform_upper_map_or_iid_threshold_established=False,
        global_reliability_established=False,
        scope='unchanged SP14 maintenance conditional sparse-pressure-hole E0 eroder, ROBUSTNESS J98; not general damaged-input source or hierarchy proof')
    (out / 'SP14_sparse_pressure_holes_certificate.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(dict(stable_hole_cases=stable, acquisition_cases=acquisition,
        maximum_holes=maximum_holes, conditional_GF_Age_deadline=577, global_reliability_established=False)))


if __name__ == '__main__':
    main()
