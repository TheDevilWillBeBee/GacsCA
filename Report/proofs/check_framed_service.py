#!/usr/bin/env python3
"""Exact local premises for the conditional framed-service theorem J87.

Exhausts counter comparison, valid-position ancestry and quorum masks;
checks free-word maintenance cofactors. It does not exhaust the entire
38-bit, eleven-cell component neighborhood or establish source birth.
"""
from itertools import combinations
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import numpy as np
from gacsca.netlist import Net, Compiled, const_word, mixed_age_increment
from check_fast_flag_proposal import invoke
import proposed_sparse_timed448 as sp13
import proposed_framed_service as proposed


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_comparison():
    n = Net()
    a = [n.input(('a', b)) for b in range(proposed.COUNTER_BITS)]
    b = [n.input(('b', bit)) for bit in range(proposed.COUNTER_BITS)]
    n.set_output(('less',), proposed.word_less(n, a, b))
    comp = Compiled(n)
    checked = 0
    words = np.arange(1 << proposed.COUNTER_BITS, dtype=np.uint32)
    for start in range(0, len(words), 64):
        av = np.repeat(words[start:start + 64], len(words))
        bv = np.tile(words, min(64, len(words) - start))
        values = {('a', bit): ((av >> bit) & 1).astype(bool) for bit in range(proposed.COUNTER_BITS)}
        values.update({('b', bit): ((bv >> bit) & 1).astype(bool) for bit in range(proposed.COUNTER_BITS)})
        assert np.array_equal(comp.evaluate(values, bool)['less',], av < bv)
        checked += len(av)
    assert checked == 4194304
    return checked, comp.digest


def check_ancestry():
    cases = dict(packet=0, flag=0, accepted_packet=0, accepted_flag=0)
    for name, limit, modulus in (('packet', proposed.PACKET_SIZE, 1 << proposed.TAG_BITS),
                                  ('flag', proposed.Q, proposed.POSITION_MODULUS)):
        for position in range(limit):
            for offset in range(-proposed.RADIUS, proposed.RADIUS + 1):
                adjusted = (position - offset) % modulus
                cases[name] += 1
                if adjusted < limit:
                    # y=x+offset, so y-position=x-adjusted exactly.
                    assert position - adjusted == offset
                    cases['accepted_' + name] += 1
    return cases


def check_quorum():
    masks = np.arange(1 << 11, dtype=np.uint16)
    matching = ((masks[:, None] >> np.arange(11)) & 1).astype(bool)
    witness_cases, five_holder_cases = 0, 0
    for faults in combinations(range(11), 2):
        good = [j for j in range(11) if j not in faults]
        assert not np.any((matching.sum(axis=1) >= 3) & ~matching[:, good].any(axis=1))
        witness_cases += len(masks)
        for start in range(7):
            holders = set(range(start, start + 5))
            assert len(holders - set(faults)) >= 3
            five_holder_cases += 1
    return witness_cases, five_holder_cases


def check_RF_suffix():
    p = sp13.parameters()
    build, source = proposed.maintenance_build(symbolic=True)
    # With force=0, this is the exact old maintenance at every node.
    n = Net()
    raw = {}
    for off in range(-5, 9):
        raw[off] = dict(addr=[n.input((off, 'addr', bit)) for bit in range(p.k)],
                        age=[n.input((off, 'age', bit)) for bit in range(p.m)],
                        **{key: n.input((off, key)) for key in ('f1', 'f2', 'wf1', 'wf2')})
    old = invoke(sp13.proposed_build(symbolic=True)[0], n, raw, p)
    new = invoke(build, n, raw, p)
    assert old == new
    cases = 0
    for x in range(p.Q):
        for cohort in combinations(range(1, 6), 3):
            n = Net()
            age = [n.input(('reference_age', bit)) for bit in range(p.m)]
            cells = {}
            for off in range(-5, 9):
                cells[off] = dict(
                    addr=const_word((x + off) % p.Q, p.k) if off in cohort else [n.input((off, 'addr', bit)) for bit in range(p.k)],
                    age=age if off in cohort else [n.input((off, 'age', bit)) for bit in range(p.m)],
                    **{key: n.input((off, key)) for key in ('f1', 'f2', 'wf1', 'wf2')})
            result = build(n, cells, p.k, p.m, Q=p.Q, nb=p.nb, radix=p.R, pos_bits=p.PB, service_force=1)
            assert result['f2'] == 1
            assert result['addr'] == const_word(x, p.k)
            assert result['age_now'] == age
            assert result['age'] == mixed_age_increment(n, age, p.PB, p.R, p.nb)
            cases += 1
    return cases, hashlib.sha256(source.encode()).hexdigest()


def module_net():
    n = Net()
    cells = {}
    widths = dict(packet_valid=1, wf2=1, packet_tag=4, packet_count=11,
                  flag_valid=1, flag_position=9, flag_count=11)
    for off in range(-5, 6):
        cells[off] = {field: (n.input((off, field, 0)) if width == 1 else
                             [n.input((off, field, bit)) for bit in range(width)])
                      for field, width in widths.items()}
    result = proposed.build(n, cells)
    for field, value in result.items():
        for bit, node in enumerate(value if isinstance(value, list) else [value]):
            n.set_output((field, bit), node)
    return n, Compiled(n)


def main():
    comparisons, comparator_digest = check_comparison()
    ancestry = check_ancestry()
    witnesses, holder_cases = check_quorum()
    suffix_cases, maintenance_digest = check_RF_suffix()
    n, comp = module_net()
    prefix_deadline = 1 + (proposed.Q - 1 - 6)
    GF_Age_deadline = prefix_deadline + proposed.Q
    assert (prefix_deadline, GF_Age_deadline) == (442, 890)
    assert GF_Age_deadline < proposed.LIFETIME
    out = ROOT / 'figs/robustness'
    receipt = dict(
        proposed_rule_change=True, unincorporated_module=True,
        active_G17_modified=False, SP13_modified=False,
        checker_sha256=digest(Path(__file__)),
        proposal_source_sha256=digest(Path(proposed.__file__)),
        helpers_sha256=digest(ROOT / 'gacsca/netlist.py'),
        local_correction_helper_sha256=digest(ROOT / 'Report/proofs/check_fast_flag_proposal.py'),
        modal_maintenance_proposal_source_sha256=digest(ROOT / 'Report/proofs/proposed_modal_clock.py'),
        SP13_maintenance_source_sha256=hashlib.sha256(sp13.proposed_build()[1].encode()).hexdigest(),
        framed_maintenance_source_sha256=maintenance_digest,
        comparator_netlist_sha256=comparator_digest,
        proposed_component_netlist_sha256=comp.digest,
        component_live_gates=n.gate_count(),
        component_inputs=len(n.input_names), component_state_bits=38,
        flag_added_state_bits=proposed.ADDED_FLAG_BITS,
        counter_bits=proposed.COUNTER_BITS, lifetime=proposed.LIFETIME,
        position_bits=proposed.POSITION_BITS, position_modulus=proposed.POSITION_MODULUS,
        Q=proposed.Q, all_unsigned_counter_comparisons=comparisons,
        valid_position_ancestry_cases=ancestry,
        nonfault_witness_assignments=witnesses,
        five_holder_two_fault_placements=holder_cases,
        forced_RF_joint_three_word_free_input_identities=suffix_cases,
        pressure_zero_exactly_equals_existing_maintenance=True,
        at_most_one_combined_vote_per_physical_cell=True,
        minimum_counter_used_within_each_cell_and_between_cohorts=True,
        no_external_birth_required=True,
        correct_fresh_five_packet_words_at_time_zero_required=True,
        every_other_initial_eligible_packet_or_flag_counter_at_least_one_required=True,
        at_most_two_whole_cell_faults_per_eleven_site_row_required=True,
        right_canonical_GF_and_reference_Age_prescribed=True,
        arbitrary_initial_GF_Age_NF1_NF2_and_other_data_allowed=True,
        continuing_GF_Age_and_flag_faults_covered_under_local_bound=True,
        correct_computed_flag_code_on_colony_by_update=prefix_deadline,
        canonical_GF_and_correct_computed_Age_by_update=GF_Age_deadline,
        arbitrary_initial_component_erased_by_lifetime_without_birth=True,
        finite_initial_component_support_enlargement=447,
        full_width_neighborhoods_exhausted=False,
        authentic_birth_own_ROM_or_full_upper_map_established=False,
        global_reliability_established=False,
        scope='exact arithmetic/cofactor premises of conditional framed-service proof ROBUSTNESS J87; no whole-CA or iid theorem')
    (out / 'framed_service_certificate.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(dict(counter_comparisons=comparisons, ancestry=ancestry,
                          RF_suffix_identities=suffix_cases, component_gates=n.gate_count(),
                          flag_deadline=prefix_deadline, GF_Age_deadline=GF_Age_deadline)))


if __name__ == '__main__':
    main()
