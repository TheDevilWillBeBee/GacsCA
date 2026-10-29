#!/usr/bin/env python3
"""J99: packet-supported pressure survives arbitrary coded competitors.

This is an explicit proposed change, not SP14/G17. The unchanged packet
outputs and guard6 theorem give conditional fresh-source pressure. No
authentic source, full-frame pressure or iid theorem is claimed.
"""
from itertools import combinations
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from gacsca.netlist import Net, Compiled, const_word
import proposed_framed_service as old
import proposed_packet_pressure as proposed

WIDTHS = dict(wf2=1, packet_valid=1, packet_tag=4, packet_count=11,
    flag_valid=1, flag_position=9, flag_count=11)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cells_at(n, x, root, proper):
    count = [n.input(('proper_count', b)) for b in range(11)]
    cells = {}
    for off in range(-5, 6):
        cells[off] = {f: n.input((off, f, 0)) if width == 1 else
            [n.input((off, f, b)) for b in range(width)] for f, width in WIDTHS.items()}
        y = x + off
        if y in proper:
            cells[off].update(wf2=1, packet_valid=1,
                packet_tag=const_word(y-root-1, 4), packet_count=count)
    return cells


def module_net():
    n = Net()
    cells = cells_at(n, 0, 0, ())
    original = old.build(n, cells)
    result = proposed.build(n, cells)
    equalities = 0
    for field in WIDTHS:
        before = original[field] if isinstance(original[field], list) else [original[field]]
        after = result[field] if isinstance(result[field], list) else [result[field]]
        assert before == after, field
        equalities += len(after)
        for b, node in enumerate(after):
            n.set_output((field, b), node)
    assert result['service_force'] == n.OR(original['service_force'], original['packet_any_cohort'])
    n.set_output(('service_force',), result['service_force'])
    return n, Compiled(n), equalities


def main():
    n, comp, equalities = module_net()
    leading = 0
    for center in range(7):
        for trio in combinations(range(1, 6), 3):
            n = Net()
            assert proposed.build(n, cells_at(n, center, 0, trio))['service_force'] == 1
            leading += 1
    # J95's younger right source is at445..449, root444. At its
    # gap443, four of those words lie within the radius-five window.
    gap = 0
    for trio in combinations(range(445, 449), 3):
        n = Net()
        assert proposed.build(n, cells_at(n, 443, 444, trio))['service_force'] == 1
        gap += 1
    assert (equalities, leading, gap) == (38, 70, 4)
    out = ROOT/'figs/robustness'
    receipt = dict(proposed_rule_change=True, standalone_module_certificate=True,
        active_G17_modified=False, SP14_modified=False,
        checker_sha256=digest(Path(__file__)), proposal_source_sha256=digest(Path(proposed.__file__)),
        framed_service_proposal_source_sha256=digest(Path(old.__file__)),
        helpers_sha256=digest(ROOT/'gacsca/netlist.py'),
        framed_service_certificate_sha256=digest(out/'framed_service_certificate.json'),
        guard6_certificate_sha256=digest(out/'packet_guard6_certificate.json'),
        J95_coded_gap_receipt_sha256=digest(out/'packet_guard6_coded_gap_certificate.json'),
        module_netlist_sha256=comp.digest, module_live_gates=comp.n_nodes-len(comp.inputs)-2,
        unchanged_component_output_node_equalities=equalities,
        proposed_pressure_equation='old coded flag force OR unrestricted packet_any_cohort',
        leading_center_trio_free_input_cases=leading, J95_gap_right_packet_trio_free_input_cases=gap,
        other_packet_and_all_coded_words_free=True, proper_count_bits_free=11,
        initialized_origin_zero_proper_packet_and_older_initial_packets_required=True,
        radius_six_birth_guard_and_global_E0_required_for_later_birth_persistence=True,
        arbitrary_later_birth_attempts_and_coded_competitors_allowed=True,
        computed_pressure_one_on_zero_through_six_for_input_states_zero_through_1791=True,
        original_guard6_packet_clears_at_state=1792,
        added_pressure_has_no_inside_GF_or_Code_position_filter=True,
        J95_exact_gap_filled_while_young_root444_packet_alive=True,
        clears_with_original_components_after_no_birth_timer_bound=True,
        no_rule_or_registered_candidate_modified=True,
        whole_colony_pressure_or_GF_Age_repair_under_arbitrary_births_established=False,
        authentic_initial_source_or_autonomous_boundary_established=False,
        own_program_or_full_CA_incorporation_certified_by_this_checker=False,
        global_reliability_established=False,
        scope='explicit packet-supported pressure module and guard6 conditional initialized-source consequence, ROBUSTNESS J99; full self-simulation separately checked')
    (out/'packet_pressure_certificate.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(dict(component_equalities=equalities, leading_pressure_cases=leading,
        J95_gap_cases=gap, global_reliability_established=False)))


if __name__ == '__main__':
    main()
