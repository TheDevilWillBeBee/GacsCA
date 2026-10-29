#!/usr/bin/env python3
"""Actual SP4 voters and local-density support for the pristine-orbit proof.

The all-time copy/clock induction is in ROBUSTNESS.md, not an exhaustive
trajectory experiment. No multiple-core, higher-island or iid theorem.
"""
import hashlib
import json
from itertools import combinations
from pathlib import Path
import sys
from types import FunctionType, SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from gacsca import rule_g
from gacsca.netlist import Compiled
import proposed_sparse_prefix448 as proposed
import prefix_selection as selection
import check_fast_mail_proposal as transport
from check_fast_flag_proposal import pristine_symbolic


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    candidate = proposed.load_artifact()
    p = candidate.p
    out = ROOT / 'figs/robustness'
    namespace = dict(transport.__dict__, proposed_maintenance=selection.proposed_build)
    factory = FunctionType(transport.concrete_sparse_net.__code__, namespace)
    actual, source = factory(p, proposed.dependency_table(p))
    assert Compiled(actual).digest == candidate.comp.digest
    votes = []

    def record_vote(net, bits):
        names = {node: name for name, node in net.input_node.items()}
        inputs = [names[node] for node in bits]
        assert len(inputs) == 5 and all(name[0] == 'x' for name in inputs)
        fields = {name[2] for name in inputs}
        assert len(fields) == 1
        field = next(iter(fields))
        holders = sorted(name[1] for name in inputs)
        assert holders == list(range(holders[0], holders[0]+5))
        if field == 'reg':
            assert p.compact_front and len({name[3] for name in inputs}) == 1
            # Only a selected source window has five agreeing registers.
            # Do not impose impossible global agreement on overlapping windows.
            primary, logical_bit = None, inputs[0][3]
        else:
            width = proposed.logical_width(field, p)
            primaries = {name[1]+name[3]//width-2 for name in inputs}
            bits_in_word = {name[3] % width for name in inputs}
            assert len(primaries) == len(bits_in_word) == 1
            primary, logical_bit = next(iter(primaries)), next(iter(bits_in_word))
        node = rule_g.maj5(net, bits)
        votes.append(dict(field=field, primary=primary, bit=logical_bit,
                          holders=holders, output_node=node))
        return node

    maintenance_build, _ = selection.proposed_build()
    instrumented = dict(rule_g.__dict__, maj5=record_vote,
                        maintenance=SimpleNamespace(build=maintenance_build),
                        OFFSETS=tuple(range(-12, 13)),
                        sparse_controls=transport.sparse_controls,
                        sparse_table=proposed.dependency_table(p))
    exec(compile(source, '<SP4 actual-voter audit; no rule modification>', 'exec'), instrumented)
    recorded_net = instrumented['build'](p)
    assert Compiled(recorded_net).digest == candidate.comp.digest
    assert votes and set(v['field'] for v in votes) == set(proposed.fivefold_fields(p)) | {'reg'}
    assert min(min(v['holders']) for v in votes) == -12
    assert max(max(v['holders']) for v in votes) == 12
    assert p.mux_front and not p.sel_front and p.five_front and p.computed_front
    # The one/two-fault cases are already certified for all448 Addresses.
    # Complete the local-density cases that have more than two faults in
    # the14-site envelope, but at most two in each11-site subinterval.
    coordinates = tuple(range(-5, 9))
    extra_masks = []
    for count in range(3, len(coordinates)+1):
        for faults in combinations(coordinates, count):
            if all(sum(start <= x < start+11 for x in faults) <= 2
                   for start in range(-5, -1)):
                extra_masks.append(faults)
    assert len(extra_masks) == 70
    assert sum(len(f) == 3 for f in extra_masks) == 64
    assert sum(len(f) == 4 for f in extra_masks) == 6
    symbolic_build, _ = selection.proposed_build(symbolic=True)
    cases = 0
    for address in range(p.Q):
        for faults in extra_masks:
            pristine_symbolic(p, symbolic_build, address, faults)
            cases += 1
        if address % 112 == 111:
            print(f'SP4 local-density correction through Address {address}: {cases}', flush=True)
    assert cases == 31360
    receipt = dict(
        proposal='SP4', proposed_rule_change=True, active_G17_modified=False,
        proposed_candidate_sha256=candidate.digest(), proposed_netlist_sha256=candidate.comp.digest,
        proposal_source_sha256=digest(Path(proposed.__file__)), checker_sha256=digest(Path(__file__)),
        build_receipt_sha256=digest(out / 'SP4_program_build.json'),
        maintenance_receipt_sha256=digest(out / 'SP4_maintenance_certificate.json'),
        autonomy_receipt_sha256=digest(out / 'SP4_autonomy_certificate.json'),
        transport_checker_sha256=digest(ROOT / 'Report/proofs/check_fast_mail_proposal.py'),
        selection_source_sha256=digest(ROOT / 'Report/proofs/prefix_selection.py'),
        front_source_sha256=digest(ROOT / 'gacsca/rule_g.py'),
        actual_generated_source_sha256=hashlib.sha256(source.encode()).hexdigest(),
        actual_copy_voters=len(votes), copy_voters=votes,
        copy_vote_maximum_span=4, copy_vote_holder_range=[-12, 12],
        compact_register_agreement_required_only_for_consumed_front_source=True,
        additional_local_density_masks=[list(f) for f in extra_masks],
        additional_symbolic_maintenance_cases=cases, symbolic_Age_bits=p.m,
        fault_density_condition='at most two overwritten sites in each interval of eleven sites at each input tick',
        arbitrary_legal_pristine_clock=True,
        all_time_orbit_induction='proved separately in ROBUSTNESS J35',
        multiple_real_set_error_process_established=False,
        global_reliability_established=False,
        scope='actual-voter and free-clock local identities supporting pristine operational correction; no noisy higher-island induction')
    (out / 'SP4_operational_certificate.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(dict(actual_copy_voters=len(votes), additional_symbolic_cases=cases,
                          arbitrary_legal_pristine_clock=True)), flush=True)


if __name__ == '__main__':
    main()
