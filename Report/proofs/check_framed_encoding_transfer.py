#!/usr/bin/env python3
"""Exact canonical-clock and empty-component premises for SP14 J89.

Force is free in the GF/clock identities. This does not assert a full
maintenance equality on damaged inputs or prove authentic noisy birth.
"""
from itertools import combinations
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from gacsca.netlist import Net, const_word, mixed_age_increment
import proposed_sparse_framed448 as proposed


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def clock_case(p, build, address, faults):
    n = Net()
    age = [n.input(('reference_age', bit)) for bit in range(p.m)]
    cells = {}
    for off in range(-5, 9):
        good = off not in faults
        cells[off] = dict(
            addr=const_word((address + off) % p.Q, p.k) if good else [n.input((off, 'addr', bit)) for bit in range(p.k)],
            age=age if good else [n.input((off, 'age', bit)) for bit in range(p.m)],
            **{key: n.input((off, key)) for key in ('f1', 'f2', 'wf1', 'wf2')})
    result = build(n, cells, p.k, p.m, Q=p.Q, nb=p.nb, radix=p.R,
                   pos_bits=p.PB, service_force=n.input(('arbitrary_computed_service_force',)))
    assert result['addr'] == const_word(address, p.k)
    assert result['age_now'] == age
    assert result['age'] == mixed_age_increment(n, age, p.PB, p.R, p.nb)


def empty_component_case(faults):
    n = Net()
    widths = dict(packet_valid=1, wf2=1, packet_tag=4, packet_count=11,
                  flag_valid=1, flag_position=9, flag_count=11)
    cells = {}
    for off in range(-5, 6):
        cells[off] = {}
        for field, width in widths.items():
            values = [n.input((off, field, bit)) for bit in range(width)] if off in faults else [0] * width
            cells[off][field] = values[0] if width == 1 else values
    result = proposed.service.build(n, cells)
    for field, value in result.items():
        values = value if isinstance(value, list) else [value]
        assert all(node == 0 for node in values), (faults, field)


def main():
    candidate = proposed.load_artifact()
    p = candidate.p
    build, source = proposed.proposed_build(symbolic=True)
    pairs = list(combinations(range(-5, 6), 2))
    clock_cases = 0
    for address in range(p.Q):
        for faults in pairs:
            clock_case(p, build, address, faults)
            clock_cases += 1
    for faults in pairs:
        empty_component_case(faults)
    assert clock_cases == 24640
    out = ROOT / 'figs/robustness'
    receipt = dict(proposal='SP14', proposed_rule_change=True, active_G17_modified=False,
        proposed_candidate_sha256=candidate.digest(), proposed_netlist_sha256=candidate.comp.digest,
        proposal_source_sha256=digest(Path(proposed.__file__)), checker_sha256=digest(Path(__file__)),
        build_receipt_sha256=digest(out / 'SP14_program_build.json'),
        framed_service_certificate_sha256=digest(out / 'framed_service_certificate.json'),
        framed_service_proposal_source_sha256=digest(ROOT / 'Report/proofs/proposed_framed_service.py'),
        actual_maintenance_source_sha256=hashlib.sha256(source.encode()).hexdigest(),
        full_generated_source_sha256=hashlib.sha256(proposed.actual_net(p)[1].encode()).hexdigest(),
        canonical_GF_clock_two_fault_free_pressure_identities=clock_cases,
        every_other_GF_Age_flag_bit_free=True, reference_Age_bits_free=p.m,
        empty_component_two_arbitrary_word_identities=len(pairs),
        empty_component_cannot_be_created_under_local_two_fault_bound=True,
        full_maintenance_equality_on_general_damaged_inputs_established=False,
        source_authenticity_or_higher_error_projection_established=False,
        global_reliability_established=False,
        scope='canonical GF/clock with arbitrary coded pressure and two free words; empty-component invariance; complete encoding proof ROBUSTNESS J89')
    (out / 'SP14_encoding_transfer_certificate.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(dict(canonical_GF_clock_cases=clock_cases, empty_component_cases=len(pairs))))


if __name__ == '__main__':
    main()
