#!/usr/bin/env python3
"""J96: ordinary Flag2 preserves RF selection across eligible pressure holes.

Pins local identities for unchanged G17 and SP14 maintenance. The
moving-suffix induction and request-interface application are in
ROBUSTNESS. The force schedule/source/right-boundary premises remain
conditional; no actual damaged-input bootstrap or iid theorem follows.
"""
from itertools import combinations
import hashlib
import inspect
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from gacsca import candidates, maintenance
from gacsca.netlist import Net, const_word, mixed_age_increment
from check_right_barrier import dominant_majority
import proposed_sparse_framed448 as proposed


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def original_build():
    source = inspect.getsource(maintenance.build)
    namespace = dict(maintenance.__dict__, majority_word=dominant_majority)
    exec(compile(source, '<unchanged G17 maintenance; known-three-word majority shortcut>', 'exec'), namespace)
    return namespace['build'], source


def bridge(p, build, address, faults, framed):
    n = Net()
    age = [n.input(('reference_age', b)) for b in range(p.m)]
    cells = {}
    for off in range(-5, 9):
        right_good = 1 <= off <= 5 and off not in faults
        cells[off] = dict(
            addr=const_word((address + off) % p.Q, p.k) if right_good else [n.input((off, 'addr', b)) for b in range(p.k)],
            age=age if right_good else [n.input((off, 'age', b)) for b in range(p.m)],
            f2=1 if -5 <= off <= 0 and off not in faults else n.input((off, 'f2')),
            **{f: n.input((off, f)) for f in ('f1', 'wf1', 'wf2')})
    kwargs = dict(Q=p.Q, nb=p.nb, radix=p.R, pos_bits=p.PB)
    if framed:
        kwargs['service_force'] = n.input(('arbitrary_coded_force',))
    result = build(n, cells, p.k, p.m, **kwargs)
    assert result['f2'] == 1, (address, faults)
    assert result['addr'] == const_word(address, p.k), (address, faults)
    assert result['age_now'] == age, (address, faults)
    assert result['age'] == mixed_age_increment(n, age, p.PB, p.R, p.nb), (address, faults)


def boundary_clear(p, build, framed):
    n = Net()
    age = [n.input(('reference_age', b)) for b in range(p.m)]
    cells = {off: dict(
        addr=const_word(off % p.Q, p.k) if 1 <= off <= 5 else [n.input((off, 'addr', b)) for b in range(p.k)],
        age=age if 1 <= off <= 5 else [n.input((off, 'age', b)) for b in range(p.m)],
        f1=0 if off > 0 else n.input((off, 'f1')),
        f2=1 if -5 <= off <= 0 else n.input((off, 'f2')),
        wf1=0, wf2=0) for off in range(-5, 9)}
    kwargs = dict(Q=p.Q, nb=p.nb, radix=p.R, pos_bits=p.PB)
    if framed:
        kwargs['service_force'] = 0
    result = build(n, cells, p.k, p.m, **kwargs)
    assert result['f1'] == 0 and result['f2'] == 0
    assert result['addr'] == const_word(0, p.k)
    assert result['age_now'] == age


def main():
    active = candidates.load('G17')
    candidate = proposed.load_artifact()
    pairs = list(combinations(range(-5, 6), 2))
    rules = {}
    for name, rule, (build, source), framed in (
        ('G17', active, original_build(), False),
        ('SP14', candidate, proposed.proposed_build(symbolic=True), True)):
        cases = 0
        for address in range(5, rule.p.Q):
            for faults in pairs:
                bridge(rule.p, build, address, faults, framed)
                cases += 1
        boundary_clear(rule.p, build, framed)
        rules[name] = dict(candidate_sha256=rule.digest(), netlist_sha256=rule.comp.digest,
            Q=rule.p.Q, U=rule.p.U, reference_Age_bits_free=rule.p.m,
            maintenance_source_sha256=hashlib.sha256(source.encode()).hexdigest(),
            ordinary_Flag2_RF_bridge_free_word_cases=cases,
            first_five_addresses_excluded_from_persistent_Flag2_claim=True,
            address_zero_quiet_Flag2_erasure_cofactor=True)
        print(json.dumps(dict(rule=name, local_RF_bridge_cases=cases)), flush=True)
    out = ROOT / 'figs/robustness'
    gap = json.loads((out / 'packet_guard6_coded_gap_certificate.json').read_text())
    full_start, deadline = 148, 595
    assert deadline == full_start + candidate.p.Q - 1
    for row in gap['rows']:
        if row['state'] < full_start:
            continue
        current_input_tick = row['state'] - 1
        r = max(0, 447 - (current_input_tick - full_start))
        permitted_hole_start = max(5, r - 1)
        assert all(x >= permitted_hole_start for x in row['coded_force_zero_sites_in_true_colony']), row['state']
    for state in range(401, 1792):
        r = max(0, 447 - (state - 1 - full_start))
        assert 443 >= max(5, r - 1)
    receipt = dict(proposal='SP14', proposed_rule_change=False, active_G17_modified=False,
        proposed_candidate_sha256=candidate.digest(), proposed_netlist_sha256=candidate.comp.digest,
        proposal_source_sha256=digest(Path(proposed.__file__)), checker_sha256=digest(Path(__file__)),
        helpers_sha256=digest(ROOT / 'gacsca/netlist.py'),
        maintenance_sha256=digest(ROOT / 'gacsca/maintenance.py'),
        majority_shortcut_sha256=digest(ROOT / 'Report/proofs/check_right_barrier.py'),
        actual_maintenance_source_sha256=rules['SP14']['maintenance_source_sha256'],
        full_generated_source_sha256=hashlib.sha256(proposed.actual_net(candidate.p)[1].encode()).hexdigest(),
        build_receipt_sha256=digest(out / 'SP14_program_build.json'),
        framed_service_certificate_sha256=digest(out / 'framed_service_certificate.json'),
        coded_gap_receipt_sha256=digest(out / 'packet_guard6_coded_gap_certificate.json'),
        rules=rules, reference_left_GF_Age_and_other_flags_free=True,
        stored_Flag2_self_and_left_five_computed_ones_required=True,
        at_most_two_arbitrary_whole_word_faults_in_each_eleven_site_row_required=True,
        prescribed_right_canonical_GF_and_reference_clock_required=True,
        correct_RF_suffix_before_first_hole_and_force_front_schedule_required=True,
        moving_hole_front_schedule='coded force1 at x<max(5,r_t-1); holes allowed only at x>=max(5,r_t-1)',
        application_complete_force_start_state=full_start,
        application_initial_reference_suffix_start=447,
        application_every_GF_Age_correct_by_state=deadline,
        application_correct_and_stored_Flag2_one_through_state=1791,
        coded_gap_does_not_block_conditional_GF_Age_repair=True,
        application_uses_guard6_request_interface_not_complete_CA=True,
        complete_Flag1_or_simulation_data_repair_established=False,
        actual_full_rule_later_birth_reachability_or_source_bootstrap_established=False,
        general_coded_fault_holes_obey_front_schedule_established=False,
        iid_unreliability_established=False, global_reliability_established=False,
        scope='actual G17/SP14 Flag2 local invariants and SP14 moving-pressure-hole RF suffix proof, ROBUSTNESS J96; exact J95 request-interface application, not full hierarchy reliability')
    (out / 'SP14_pressure_hole_bridge_certificate.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(dict(G17_cases=rules['G17']['ordinary_Flag2_RF_bridge_free_word_cases'],
        SP14_cases=rules['SP14']['ordinary_Flag2_RF_bridge_free_word_cases'],
        conditional_GF_Age_deadline=deadline, global_reliability_established=False)))


if __name__ == '__main__':
    main()
