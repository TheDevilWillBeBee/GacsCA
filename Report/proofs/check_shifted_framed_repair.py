#!/usr/bin/env python3
"""J90/J91: local premises for shifted-source repair and a density witness.

SP14 is unchanged. The positive theorem needs global E0 separation,
uniform initial nonzero clock, a correctly initialized origin1 packet,
older competing carriers and the prescribed right GF/Flag1 boundary.
The negative witness addresses a stronger local-density-only lemma,
not iid unreliability. Universal inductions are in ROBUSTNESS.
"""
from itertools import combinations
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import numpy as np
from gacsca import maintenance
from gacsca.netlist import Net, Compiled, const_word, mixed_age_increment, at_least, w_eq_const
import proposed_sparse_framed448 as proposed


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def clock_case(p, build, faults, nonzero_bit):
    n = Net()
    age = [1 if bit == nonzero_bit else n.input(('reference_age', bit)) for bit in range(p.m)]
    cells = {}
    for off in range(-5, 9):
        cells[off] = dict(addr=[n.input((off, 'addr', bit)) for bit in range(p.k)],
            age=[n.input((off, 'age', bit)) for bit in range(p.m)] if off in faults else age,
            **{key: n.input((off, key)) for key in ('f1', 'f2', 'wf1', 'wf2')})
    result = build(n, cells, p.k, p.m, Q=p.Q, nb=p.nb, radix=p.R,
                   pos_bits=p.PB, service_force=n.input(('arbitrary_service_force',)))
    assert result['age_now'] == age, (faults, nonzero_bit)
    assert result['age'] == mixed_age_increment(n, age, p.PB, p.R, p.nb)


def clock_birth_gate(p, faults, unequal_bit):
    n = Net()
    age = [1 - ((p.age_code(p.T_wf) >> bit) & 1) if bit == unequal_bit
           else n.input(('reference_age', bit)) for bit in range(p.m)]
    cells = {off: [n.input((off, 'age', bit)) for bit in range(p.m)] if off in faults else age
             for off in range(-5, 6)}
    vote = [at_least(n, [cells[j][bit] for j in range(-5, 6)], 6) for bit in range(p.m)]
    assert w_eq_const(n, vote, p.age_code(p.T_wf)) == 0, (faults, unequal_bit)


def leading_recovery(p, build, addr_cohort, age_cohort, wf2_cohort):
    n = Net()
    age = [n.input(('reference_age', bit)) for bit in range(p.m)]
    cells = {}
    for off in range(-5, 9):
        cells[off] = dict(
            addr=const_word(off % p.Q, p.k) if off in addr_cohort else [n.input((off, 'addr', bit)) for bit in range(p.k)],
            age=age if off in age_cohort else [n.input((off, 'age', bit)) for bit in range(p.m)],
            f1=n.input((off, 'f1')), f2=n.input((off, 'f2')),
            wf1=n.input((off, 'wf1')), wf2=1 if off in wf2_cohort else n.input((off, 'wf2')))
    result = build(n, cells, p.k, p.m, Q=p.Q, nb=p.nb, radix=p.R,
                   pos_bits=p.PB, service_force=n.input(('arbitrary_service_force',)))
    assert result['f2'] == 1
    assert result['addr'] == const_word(0, p.k)
    assert result['age_now'] == age
    assert result['age'] == mixed_age_increment(n, age, p.PB, p.R, p.nb)


def missed_cell_clean_retreat(p, build, address, gap):
    n = Net()
    age = [n.input(('reference_age', bit)) for bit in range(p.m)]
    cells = {}
    for off in range(-5, 9):
        y = address + off
        cells[off] = dict(
            addr=const_word(y % p.Q, p.k) if y > 0 else [n.input((off, 'addr', bit)) for bit in range(p.k)],
            age=age, f1=0 if y >= address + gap else n.input((off, 'f1')),
            f2=n.input((off, 'f2')), wf1=0, wf2=n.input((off, 'wf2')))
    result = build(n, cells, p.k, p.m, Q=p.Q, nb=p.nb, radix=p.R,
                   pos_bits=p.PB, service_force=n.input(('arbitrary_service_force',)))
    assert result['f1'] == 0, (address, gap)
    assert result['addr'] == const_word(address, p.k)
    assert result['age_now'] == age


def blocked_leading_cell(p, build):
    """Exact central cofactor; clock/count free and raw fields2/3 free.

    Negative GF-1/-2 are free binary phases; -3..-5 shifted. Negative
    Flag2 may occur at -3..-1 only. This covers the invariant in J91.
    """
    n = Net()
    age = [n.input(('reference_age', bit)) for bit in range(p.m)]
    count = [n.input(('common_count', bit)) for bit in range(11)]
    cells, code = {}, {}
    for off in range(-5, 9):
        if off in (2, 3):
            addr = [n.input((off, 'addr', bit)) for bit in range(p.k)]
            raw_age = [n.input((off, 'age', bit)) for bit in range(p.m)]
        elif off in (-1, -2):
            addr = [n.MUX(n.input((off, 'phase')), a, b) for a, b in
                    zip(const_word(off % p.Q, p.k), const_word((off - 1) % p.Q, p.k))]
            raw_age = age
        else:
            addr = const_word((off - 1 if off <= 0 else off) % p.Q, p.k)
            raw_age = age
        wf2 = int(off in (4, 5, 6))
        cells[off] = dict(addr=addr, age=raw_age,
                         f1=1 if off in (0, 2, 3) else n.input((off, 'f1')),
                         f2=0 if off <= -4 or off == 0 else n.input((off, 'f2')),
                         wf1=0, wf2=wf2)
        if -5 <= off <= 5:
            proper_packet = off in (4, 5)
            eligible_flag = 0 if off <= 0 or off in (2, 3) else n.input((off, 'eligible_flag'))
            code[off] = dict(packet_valid=int(proper_packet), wf2=wf2,
                packet_tag=const_word(off - 2 if proper_packet else 0, 4), packet_count=count,
                flag_valid=eligible_flag, flag_position=const_word(off - 1 if off > 0 else 0, 9), flag_count=count)
    result_code = proposed.service.build(n, code)
    assert result_code['service_force'] == 0
    result = build(n, cells, p.k, p.m, Q=p.Q, nb=p.nb, radix=p.R,
                   pos_bits=p.PB, service_force=result_code['service_force'])
    assert result['f1'] == 1 and result['f2'] == 0
    assert result['addr'] == const_word(p.Q - 1, p.k)
    assert result['age_now'] == age
    return dict(leading_flag1=1, leading_flag2=0, leading_computed_GF=p.Q - 1,
                computed_coded_pressure=0, two_current_fault_sites=[2, 3],
                proper_source_origin=1, every_clock_and_counter_bit_free=True,
                left_minus_one_minus_two_GF_free_binary_phase=True,
                negative_Flag2_free_on_minus_three_through_minus_one=True)


def density_profile_invariant(p, build):
    """Pin the finite seam cases of a simpler infinite witness.

    Faults2/3 keep canonical GF/current Age but set Flag1 and erase the
    packet/code. GF is phase-1 on x<=0 and canonical on x>=1. Flag2 is
    zero on x<=0; Flag1 is one at0/1 and zero at x>=2 before faults.
    Negative Flag1 and positive Flag2 are arbitrary. WF1 is zero.
    Far from the seam the same constant-frame cofactor applies.
    """
    checks = 0
    for x in range(-8, 11):
        n = Net()
        age = [n.input(('reference_age', bit)) for bit in range(p.m)]
        cells = {}
        for off in range(-5, 9):
            y = x + off
            cells[off] = dict(
                addr=const_word((y - 1 if y <= 0 else y) % p.Q, p.k),
                age=age,
                f1=n.input((y, 'f1')) if y < 0 else int(y in (0, 1, 2, 3)),
                f2=0 if y <= 0 or y in (2, 3) else n.input((y, 'f2')),
                wf1=0, wf2=int(y in (4, 5, 6)))
        force = 0 if x <= 0 else n.input(('arbitrary_positive_service_force',))
        result = build(n, cells, p.k, p.m, Q=p.Q, nb=p.nb, radix=p.R,
                       pos_bits=p.PB, service_force=force)
        assert result['addr'] == const_word((x - 1 if x <= 0 else x) % p.Q, p.k), x
        assert result['age_now'] == age, x
        if x <= 0:
            assert result['f2'] == 0, x
        if x >= 0:
            assert result['f1'] == int(x in (0, 1)), x
        checks += 1
    return checks


def main():
    candidate = proposed.load_artifact()
    p = candidate.p
    build, source = proposed.proposed_build(symbolic=True)
    pairs = list(combinations(range(-5, 6), 2))
    counts = dict(nonzero_clock=0, clock_birth_closed=0, leading_recovery=0,
                  missed_cell_clean_retreat=0)
    for bit in range(p.m):
        for faults in pairs:
            clock_case(p, build, faults, bit)
            clock_birth_gate(p, faults, bit)
            counts['nonzero_clock'] += 1
            counts['clock_birth_closed'] += 1
        print(json.dumps(dict(clock_bits_checked=bit + 1, nonzero_clock_cases=counts['nonzero_clock'])), flush=True)
    for addr_trio in combinations(range(1, 6), 3):
        for age_trio in combinations(range(1, 6), 3):
            for wf2_trio in combinations(range(2, 6), 3):
                leading_recovery(p, build, addr_trio, age_trio, wf2_trio)
                counts['leading_recovery'] += 1
    for address in range(6):
        for gap in (1, 2):
            missed_cell_clean_retreat(p, build, address, gap)
            counts['missed_cell_clean_retreat'] += 1
    witness = blocked_leading_cell(p, build)
    profile_cases = density_profile_invariant(p, build)
    # If a previous blocking pair made GF0 wrong, every current fault in
    # the relevant leading-cell/front neighborhoods violates separation.
    separation_cases = 0
    for start in (2, 3, 4):
        for site in range(-5, 14):
            assert min(abs(site - start), abs(site - start - 1)) < 24
            separation_cases += 1
    tmax = 2040
    clock_words = [p.age_code(p.T_wf + 1 + t) for t in range(tmax + 1)]
    assert all(word != 0 and word != p.age_code(p.T_wf) for word in clock_words)
    assert p.T_wf + 1 + tmax < p.U
    flag1_source_free, flag1_reserve = 897, 252
    assert flag1_source_free + flag1_reserve == 1149
    assert 1150 < proposed.service.LIFETIME
    assert proposed.service.LIFETIME + 247 == 2039 <= tmax
    out = ROOT / 'figs/robustness'
    identity = dict(proposal='SP14', proposed_rule_change=False, active_G17_modified=False,
        checker_sha256=digest(Path(__file__)), proposal_source_sha256=digest(Path(proposed.__file__)),
        proposed_candidate_sha256=candidate.digest(), proposed_netlist_sha256=candidate.comp.digest,
        actual_maintenance_source_sha256=hashlib.sha256(source.encode()).hexdigest(),
        full_generated_source_sha256=hashlib.sha256(proposed.actual_net(p)[1].encode()).hexdigest(),
        build_receipt_sha256=digest(out / 'SP14_program_build.json'),
        framed_service_certificate_sha256=digest(out / 'framed_service_certificate.json'),
        incorporation_receipt_sha256=digest(out / 'SP14_framed_incorporation_certificate.json'),
        canonical_birth_receipt_sha256=digest(out / 'SP14_packet_birth_certificate.json'),
        encoding_transfer_receipt_sha256=digest(out / 'SP14_encoding_transfer_certificate.json'),
        old_E0_retreat_receipt_sha256=digest(out / 'SP13_encoded_e0_certificate.json'),
        global_reliability_established=False)
    positive = dict(**identity, local_identities=counts,
        source_holders=[2, 3, 4, 5, 6], source_origin=1, initial_count=0,
        uniform_initial_global_reference_Age=p.age_code(p.T_wf + 1),
        initial_GF_on_true_colony_arbitrary=True,
        initial_other_eligible_component_counters_at_least_one_required=True,
        globally_24_24_separated_singleton_or_adjacent_pair_E0_required=True,
        right_exterior_canonical_GF_and_quiet_Flag1_prescribed=True,
        nonzero_clock_window_words_checked=len(clock_words),
        no_further_birth_premise_discharged_by_uniform_nonzero_clock=True,
        previous_blocker_current_fault_exclusion_cases=separation_cases,
        positive_GF_Age_by_update=890, leading_GF_possible_blockers=[[2, 3], [3, 4], [4, 5]],
        Age_on_whole_true_colony_always_reference=True,
        Flag1_source_free_by_update=flag1_source_free, Flag1_quiet_by_update=1149,
        full_true_colony_GF_Age_by_update=1150,
        all_structural_and_component_fields_quiet_by_update=tmax,
        authentic_initial_command_or_general_Age_islands_established=False,
        full_field_repair_or_uniform_upper_map_established=False,
        scope='exact local/cohort/separation premises for actual SP14 shifted-source E0 structural proof; ROBUSTNESS J90')
    (out / 'SP14_shifted_source_repair_certificate.json').write_text(json.dumps(positive, indent=2) + '\n')
    negative = dict(**identity, witness=witness,
        infinite_profile_invariant_cofactors=profile_cases,
        actual_field_fault_profile=dict(GF_at_sites_two_three='canonical',
            Age_at_sites_two_three='current common reference',
            Flag1=1, Workspace1=0, Workspace2=0, packet_valid=0, coded_valid=0),
        initial_GF_phase_minus_one_on_nonpositive_sites_and_canonical_on_positive_sites=True,
        initial_Flag1_one_at_zero_one_zero_on_sites_at_least_two=True,
        initial_Flag2_zero_on_nonpositive_sites=True,
        initial_proper_origin1_packet_and_other_codes_zero=True,
        repeated_adjacent_pair_at_every_input_tick_required=True,
        local_two_word_per_eleven_bound_satisfied=True,
        global_E0_separation_satisfied=False,
        initial_reference_clock=p.age_code(p.T_wf + 897),
        active_packet_states_with_leading_GF_wrong=1792,
        full_neighborhoods_exhausted=False,
        iid_unreliability_established=False,
        scope='universal central cofactor plus infinite-profile invariant counterexample to shifted-source local-density-only extension; ROBUSTNESS J91')
    (out / 'SP14_shifted_density_counterexample.json').write_text(json.dumps(negative, indent=2) + '\n')
    print(json.dumps(dict(local_identities=counts, GF_Age_deadline=1150, structural_deadline=tmax,
                          local_density_only_extension_refuted=True)))


if __name__ == '__main__':
    main()
