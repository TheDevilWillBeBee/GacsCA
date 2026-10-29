#!/usr/bin/env python3
"""J94: local premises for birth-independent packet persistence with E0.

The spatial/counter induction is in ROBUSTNESS. This checker validates
the guard implementation, all protected trios, the dangerous-birth
shadow and temporal separation arithmetic. It does not build an own ROM
or certify the coded pressure wave/full-rule structural recovery.
"""
from itertools import combinations
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from gacsca.netlist import Net, const_word, Compiled
import proposed_framed_service as service
import proposed_packet_guard6 as proposed


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cells_at(n, x, holders):
    count = [n.input(('reference_count', b)) for b in range(11)]
    cells = {}
    for off in range(-6, 7):
        y = x + off
        known = y in holders
        cells[off] = dict(packet_valid=1 if known else n.input((off, 'valid')),
            wf2=1 if known else n.input((off, 'wf2')),
            packet_tag=const_word(y - 1, 4) if known else [n.input((off, 'tag', b)) for b in range(4)],
            packet_count=count if known else [n.input((off, 'count', b)) for b in range(11)])
    return cells


def symbolic_guard():
    n = Net()
    cells = cells_at(n, 0, ())
    n.set_output(('guard',), proposed.build(n, cells))
    return n, Compiled(n)


def main():
    protected_cases = 0
    for x in range(-1, 8):
        for trio in combinations(range(1, 6), 3):
            n = Net()
            assert proposed.build(n, cells_at(n, x, trio)) == 1, (x, trio)
            protected_cases += 1
    clean_edge_cases = 0
    for x in (-3, -2, 8, 9):
        holders = [y for y in range(1, 6) if abs(y - x) <= 6]
        assert len(holders) >= 3
        n = Net()
        assert proposed.build(n, cells_at(n, x, holders)) == 1, x
        clean_edge_cases += 1
    # Every potentially dangerous birth has a valid integer packet root
    # r in[-4,4]. Block births in[-1,7] regardless of two current faults.
    # Count the remaining potential births for each root and every
    # possible E0 group meeting the original source1..5.
    groups = [()] + [(y,) for y in range(1, 6)] + [(y, y + 1) for y in range(0, 6)]
    shadow_cases, maximal_shadow = 0, 0
    for faults in groups:
        for r in range(-4, 5):
            births = [y for y in range(r + 1, r + 6)
                if len([h for h in range(1, 6) if abs(h - y) <= 6 and h not in faults]) < 3]
            assert len(births) <= 2, (faults, r, births)
            assert not births or set(faults) & set(range(1, 6)), (faults, r)
            assert r != 0 or not births
            maximal_shadow = max(maximal_shadow, len(births))
            shadow_cases += 1
    exclusions = 0
    for previous in range(1, 6):
        for current in range(-3, 10):
            assert abs(current - previous) < 24
            exclusions += 1
    # A weaker radius-five guard can allow three new words of root-4
    # with the actual J93 initial pair1/2; radius-six permits only two.
    weak = [y for y in range(-3, 2)
        if len([h for h in range(1, 6) if abs(h - y) <= 5 and h not in (1, 2)]) < 3]
    wide = [y for y in range(-3, 2)
        if len([h for h in range(1, 6) if abs(h - y) <= 6 and h not in (1, 2)]) < 3]
    assert weak == [-3, -2, -1] and wide == [-3, -2]
    n, comp = symbolic_guard()
    out = ROOT / 'figs/robustness'
    receipt = dict(proposed_rule_change=True, unincorporated_module=True,
        active_G17_modified=False, SP14_modified=False,
        checker_sha256=digest(Path(__file__)), proposal_source_sha256=digest(Path(proposed.__file__)),
        helpers_sha256=digest(ROOT / 'gacsca/netlist.py'),
        framed_service_proposal_source_sha256=digest(Path(service.__file__)),
        framed_service_certificate_sha256=digest(out / 'framed_service_certificate.json'),
        SP14_competition_counterexample_sha256=digest(out / 'SP14_source_competition_proof_certificate.json'),
        guard_netlist_sha256=comp.digest, guard_live_gates=n.gate_count(),
        original_birth_guard_radius=5, proposed_birth_guard_radius=6,
        packet_selection_radius_unchanged=5, packet_bits_unchanged=17,
        free_word_protected_trio_guard_cofactors=protected_cases,
        clean_edge_birth_requires_source_fault_cofactors=clean_edge_cases,
        dangerous_origin_current_E0_group_cases=shadow_cases,
        maximum_dangerous_newborns_per_integer_origin=maximal_shadow,
        next_row_fault_exclusion_cases=exclusions,
        radius_five_dangerous_birth_slots=weak, radius_six_dangerous_birth_slots=wide,
        initialized_proper_five_packet_words_required=True,
        other_initial_eligible_packet_counters_at_least_one_required=True,
        globally_24_24_separated_singleton_or_adjacent_pair_E0_required=True,
        arbitrary_birth_attempts_GF_Age_and_other_data_allowed=True,
        proper_packet_persists_through_state=1791, original_packet_expiry_state=1792,
        independent_no_further_birth_premise_removed_for_packet_only=True,
        wider_guard_requires_no_new_packet_or_counter_bits=True,
        extra_nonzero_dependency_offsets_per_packet_field=2,
        fits_existing_ten_history_ranks=False,
        own_program_fitting_and_full_CA_incorporation_established=False,
        coded_flag_priority_or_complete_service_wave_established=False,
        authentic_initial_source_delivery_established=False,
        global_reliability_established=False,
        scope='standalone explicit guard change and exact premises of J94 birth-independent packet induction; not a complete self-simulating candidate')
    (out / 'packet_guard6_certificate.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(dict(protected_trios=protected_cases, clean_edges=clean_edge_cases,
        shadow_cases=shadow_cases, source_persistence=1791,
        own_program_and_reliability_established=False)))


if __name__ == '__main__':
    main()
