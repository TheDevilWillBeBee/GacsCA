#!/usr/bin/env python3
"""SP4 protected-suffix/clock certificate and early real-level-1 bridge.

Universal gates, class examples and arithmetic support the unbounded proof.
No arbitrary-stage or iid-noise theorem is claimed.
"""
import hashlib
from itertools import combinations
import json
from pathlib import Path
import sys
from types import FunctionType

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from gacsca import gray_errors, rule_g
from gacsca.netlist import Net, Compiled, const_word, mixed_age_increment
import numpy as np
import proposed_sparse_prefix448 as proposed
import prefix_selection as selection
import check_fast_mail_proposal as transport
from check_fast_flag_proposal import invoke
from check_right_barrier import workspace_output_gate


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def barrier_case(p, build, address, faults):
    net = Net()
    common = [net.input(('common_Age', bit)) for bit in range(p.m)]
    cells = {}
    for j in range(-5, 9):
        outside_suffix = address+j < 0
        outside_colony = outside_suffix or address+j >= p.Q
        faulty = j in faults
        if j >= 6:
            cells[j] = dict(f1=net.input((j, 'f1')) if outside_colony or faulty else 0)
            continue
        cells[j] = dict(
            addr=[net.input((j, 'addr', bit)) for bit in range(p.k)] if outside_suffix or faulty
                 else const_word((address+j) % p.Q, p.k),
            age=[net.input((j, 'age', bit)) for bit in range(p.m)] if outside_suffix or faulty else common,
            f1=net.input((j, 'f1')) if outside_colony or faulty else 0,
            wf1=net.input((j, 'wf1')) if outside_colony or faulty else 0,
            f2=net.input((j, 'f2')), wf2=net.input((j, 'wf2')))
    actual = invoke(build, net, cells, p)
    assert actual['f1'] == 0
    assert actual['addr'] == const_word(address, p.k)
    assert actual['age_now'] == common
    assert actual['age'] == mixed_age_increment(net, common, p.PB, p.R, p.nb)


def main():
    candidate = proposed.load_artifact()
    p = candidate.p
    build, _ = selection.proposed_build(symbolic=True)
    pairs = tuple(combinations(range(-5, 9), 2))
    cases = 0
    for address in range(p.Q):
        for faults in pairs:
            barrier_case(p, build, address, faults)
            cases += 1
        if address % 112 == 111:
            print(f'SP4 protected suffix through Address {address}: {cases}', flush=True)
    # Reconstruct exactly the actual generated rule, not a source analogy.
    namespace = dict(transport.__dict__, proposed_maintenance=selection.proposed_build)
    factory = FunctionType(transport.concrete_sparse_net.__code__, namespace)
    net, source = factory(p, proposed.dependency_table(p))
    assert Compiled(net).digest == candidate.comp.digest
    for exact_line in ('    wf1 = n.all([right_end, in_wf, sim_r])',
                       '    wf2 = n.all([left_end, in_wf, sim_l, n.NOT(f1_new)])'):
        assert source.count(exact_line) == 1
    gate = workspace_output_gate(p)
    # Entire legal clock cycle, with its actual increment gates.
    clock = Net()
    bits = [clock.input(('age', i)) for i in range(p.m)]
    nxt = mixed_age_increment(clock, bits, p.PB, p.R, p.nb)
    for i, node in enumerate(nxt):
        clock.set_output(('age', i), node)
    words = np.array([p.age_code(t) for t in range(p.U)], dtype=np.uint32)
    got = Compiled(clock).evaluate({('age', i): ((words >> i) & 1).astype(bool)
                                   for i in range(p.m)}, bool)
    actual = sum(got['age', i].astype(np.uint32) << i for i in range(p.m))
    assert np.array_equal(actual, np.roll(words, -1))
    rows = []
    for width, phase, raw, flags in ((141, 357, 381, 881), (160, 380, 404, 904)):
        rows.append(dict(width=width, phase_repair=phase, raw_repair=raw, flag_clearance=flags,
                         latest_early_good_clock_for_phase=p.T_wf-phase,
                         latest_early_good_clock_for_flag_clearance=p.T_wf-flags,
                         late_inactive_good_clocks_begin=p.T_wf+2*p.Q))
    examples = []
    for points in ({(0, 0), (5, 0), (10, 0)},
                   {(x, t) for x in range(3) for t in (0, 15)} | {(2, 38)}):
        result = gray_errors.classify(points, Q=p.Q, U=p.U, sep=16)
        assert result['level1'] and not result['level0']
        examples.append(dict(points=sorted(points), classification=result))
    first_pair_max_gap = max(min(b-a for a, b in combinations(triple, 2))
                             for triple in combinations(range(11), 3))
    assert first_pair_max_gap == 5
    forcing = 31+first_pair_max_gap
    seed = forcing+2*(3*16+2*(1+3*16//23))
    assert (forcing, seed) == (36, 144)
    phase_from_danger = 16+380
    raw_from_danger = 16+404
    flags_from_danger = 16+904
    latest_early_danger = p.gathers_q[1]*p.Q-flags_from_danger-1
    assert latest_early_danger == 3559
    out = ROOT / 'figs/robustness'
    receipt = dict(proposal='SP4', proposed_rule_change=True, active_G17_modified=False,
                   proposed_candidate_sha256=candidate.digest(), proposed_netlist_sha256=candidate.comp.digest,
                   checker_sha256=digest(Path(__file__)), proposal_source_sha256=digest(Path(proposed.__file__)),
                   selection_source_sha256=digest(ROOT / 'Report/proofs/prefix_selection.py'),
                   transport_checker_sha256=digest(ROOT / 'Report/proofs/check_fast_mail_proposal.py'),
                   right_barrier_checker_sha256=digest(ROOT / 'Report/proofs/check_right_barrier.py'),
                   classifier_sha256=digest(ROOT / 'gacsca/gray_errors.py'),
                   helpers_sha256=digest(ROOT / 'gacsca/netlist.py'),
                   timing_sha256=digest(ROOT / 'gacsca/rule.py'),
                   full_generated_source_sha256=hashlib.sha256(source.encode()).hexdigest(),
                   protected_suffix_symbolic_cases=cases, common_Age_bits_free=p.m,
                   arbitrary_outside_colony_inputs=True, arbitrary_Flag2_Workspace_Flag2=True,
                   current_arbitrary_faults_per_case=2, Workspace_output_gate=gate,
                   legal_clock_transitions=p.U, inactive_clock_rows=rows,
                   closest_pair_triplet_cases=165, first_danger_pair_maximum_gap=first_pair_max_gap,
                   fixed_forcing_interval_width_at_most=forcing, geometric_seed_width_at_most=seed,
                   phase_repair_updates_after_first_danger=phase_from_danger,
                   raw_repair_updates_after_first_danger=raw_from_danger,
                   flags_clear_updates_after_first_danger=flags_from_danger,
                   latest_first_period_danger_tick_for_two_later_gathers=latest_early_danger,
                   real_level1_examples=examples,
                   maintenance_receipt_sha256=digest(out / 'SP4_maintenance_certificate.json'),
                   build_receipt_sha256=digest(out / 'SP4_program_build.json'),
                   global_reliability_established=False,
                   scope='universal barrier/clock gates and finite class/arithmetic support for early real-level-1 recovery; arbitrary stages and higher islands unproved')
    (out / 'SP4_barrier_certificate.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(dict(inactive_clock_rows=rows, seed_width=seed,
                          latest_early_danger_tick=latest_early_danger), indent=2))


if __name__ == '__main__':
    main()
