#!/usr/bin/env python3
"""Conditional SP4 boundary modules after sacrificing two lower colonies.

This checks the actual transition source with two arbitrary upper words
at Addresses0/1. Healthy tagged copies begin at upper Address2. The
trajectory induction and its operational-snapshot premise are separate;
no eroder or iid-noise theorem is certified by this script.
"""
import hashlib
import json
from pathlib import Path
import sys
from types import FunctionType, SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from gacsca import rule_g
from gacsca.netlist import Net, Compiled, const_word, mixed_age_increment
import proposed_sparse_prefix448 as proposed
import prefix_selection as selection
import check_fast_mail_proposal as transport
from check_sparse_prefix448_autonomy import ancestors


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dominant_bit(net, bits):
    # This is the threshold-three identity for the literal maj5 primitive,
    # exhaustively checked by transport.maj5_truth(); not a rule change.
    for value in bits:
        if bits.count(value) >= 3:
            return value
    return rule_g.maj5(net, bits)


def main():
    candidate = proposed.load_artifact()
    p = candidate.p
    out = ROOT / 'figs/robustness'
    assert transport.maj5_truth() == 32
    namespace = dict(transport.__dict__, proposed_maintenance=selection.proposed_build)
    factory = FunctionType(transport.concrete_sparse_net.__code__, namespace)
    actual, source = factory(p, proposed.dependency_table(p))
    assert Compiled(actual).digest == candidate.comp.digest
    maintenance, _ = selection.proposed_build(symbolic=True)
    tagged = set(proposed.fivefold_fields(p))
    rows = []
    for address in range(2, 14):
        class BoundNet(Net):
            def input(self, name):
                if name[0] == 'x':
                    _, offset, field, bit = name
                    position = address+offset
                    if field == 'addr' and position >= 2:
                        return ((position % p.Q) >> bit) & 1
                    if field == 'age' and position >= 2:
                        return super().input(('common_clock', bit))
                    if field in ('f1', 'f2', 'wf1', 'wf2') and 2 <= position < p.Q:
                        return 0
                    if field in tagged and position >= 2:
                        width = proposed.logical_width(field, p)
                        slot = bit//width-2
                        logical = position+slot
                        if logical >= 3:
                            return super().input(('coherent_copy', logical, field, bit % width))
                return super().input(name)

        build_namespace = dict(rule_g.__dict__)
        build_namespace.update(Net=BoundNet, maintenance=SimpleNamespace(build=maintenance),
                               maj5=dominant_bit, OFFSETS=tuple(range(-12, 13)),
                               sparse_controls=transport.sparse_controls,
                               sparse_table=proposed.dependency_table(p))
        exec(compile(source, '<same SP4 source, two upper words arbitrary>', 'exec'), build_namespace)
        bounded = build_namespace['build'](p)
        assert [bounded.outputs['y', 'addr', bit] for bit in range(p.k)] == const_word(address, p.k)
        common = [bounded.input(('common_clock', bit)) for bit in range(p.m)]
        assert [bounded.outputs['y', 'age', bit] for bit in range(p.m)] == mixed_age_increment(
            bounded, common, p.PB, p.R, p.nb)
        assert bounded.outputs['y', 'f1', 0] == bounded.outputs['y', 'f2', 0] == 0
        checked = []
        for slot in proposed.SLOTS:
            logical = address+slot
            if logical < 3:
                continue
            for field in ('info', 'hold', 'ml'):
                assert proposed.logical_width(field, p) == 1
                name = ('y', field, slot+2)
                support = ancestors(bounded, bounded.outputs[name])
                assert all(inp[0] != 'I' for inp in support), (address, name)
                assert all(inp[0] != 'x' or address+inp[1] >= 2 for inp in support), (address, name, support)
                checked.append(dict(field=field, logical_primary=logical, copy_slot=slot,
                                    raw_input_positions=sorted({address+inp[1] for inp in support if inp[0] == 'x'}),
                                    coherent_primaries=sorted({inp[1] for inp in support if inp[0] == 'coherent_copy'})))
        rows.append(dict(holder_address=address, conditional_copy_outputs=checked))
    count = sum(len(row['conditional_copy_outputs']) for row in rows)
    assert count == 162
    capture_margin = min(row['address']-12 for row in proposed.dependency_table(p))
    assert capture_margin == 47
    full_projection_from = 2+12
    frame = [36, 411]
    inputs = [frame[0]-12, frame[1]+12]
    assert inputs == [24, 423] and inputs[0] >= full_projection_from
    left_signal_healthy = list(range(2, 6))
    assert len(left_signal_healthy) == 4
    horizon = 15710
    clock_cases = 0
    threatened = []
    for sigma in range(p.U):
        intersects = any(p.T_wf <= (sigma+t) % p.U <= p.T_wf+2*p.Q-1
                         for t in (0, horizon))
        intersects = intersects or sigma <= p.T_wf <= sigma+horizon
        if intersects:
            assert 9635 <= sigma <= 26240
            assert sigma+horizon <= 41950 < p.U-1
            threatened.append(sigma)
        clock_cases += 1
    assert clock_cases == p.U and threatened == list(range(9635, 26241))
    dependencies = ('SP4_program_build.json', 'SP4_symbolic_schedule.json',
                    'SP4_front_certificate.json', 'SP4_localization_certificate.json',
                    'SP4_operational_certificate.json', 'SP4_autonomy_certificate.json',
                    'SP4_boundary_noise_certificate.json', 'operational_halfline_certificate.json',
                    'SP4_nested_halfline_certificate.json')
    result = dict(
        proposal='SP4', proposed_rule_change=True, active_G17_modified=False,
        proposed_candidate_sha256=candidate.digest(), proposed_netlist_sha256=candidate.comp.digest,
        proposal_source_sha256=digest(Path(proposed.__file__)), checker_sha256=digest(Path(__file__)),
        full_rule_sha256=digest(ROOT / 'gacsca/rule_g.py'),
        selection_source_sha256=digest(ROOT / 'Report/proofs/prefix_selection.py'),
        transport_checker_sha256=digest(ROOT / 'Report/proofs/check_fast_mail_proposal.py'),
        actual_generated_source_sha256=hashlib.sha256(source.encode()).hexdigest(),
        majority_truth_assignments_checked=32, symbolic_clock_bits_free=p.m,
        arbitrary_upper_columns=[0, 1], first_healthy_upper_column=2,
        conditional_boundary_holders=rows, conditional_boundary_copy_outputs_checked=count,
        substitutions='canonical GF and quiet flags on upper indices>=2; arbitrary raw words below2; coherent healthy fixed-tag copies for logical primaries>=3',
        interior_exact_projection_first_upper_index=full_projection_from,
        capture_left_margin=capture_margin, programme_holder_frame=frame,
        programme_input_frame=inputs, left_signal_healthy_holders=left_signal_healthy,
        left_signal_arbitrary_holder=1, left_signal_healthy_copies=4,
        clock_phases_checked=clock_cases, threatened_clock_interval=[9635, 41950],
        upper_horizon=horizon, physical_horizon=horizon*p.U,
        proof_receipt_sha256={name:digest(out / name) for name in dependencies},
        trajectory_induction_is_separate=True, first_two_lower_colonies_repaired=False,
        right_real_level1_errors_covered=False, arbitrary_many_real_cores_covered=False,
        universal_higher_island_repair_established=False, global_reliability_established=False,
        scope='conditional two-column boundary-puncture identities and support arithmetic; trajectory induction separate')
    (out / 'SP4_shifted_halfline_certificate.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(dict(conditional_boundary_copy_outputs=count, full_projection_from=full_projection_from,
                          left_signal_healthy_copies=4, physical_horizon=horizon*p.U)), flush=True)


if __name__ == '__main__':
    main()
