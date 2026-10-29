#!/usr/bin/env python3
"""Conditional SP4 boundary identities with an old prefix and a far pair.

This is an actual-gate certificate, not a coupled trajectory proof. Healthy
tagged cohorts and quiet geometry are premises; neither their preservation
after repeated physical cores nor an iid threshold is inferred here.
"""
import hashlib
from itertools import combinations
import json
from pathlib import Path
import sys
from types import FunctionType, SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from gacsca import rule_g
from gacsca.netlist import Net, Compiled, const_word, mixed_age_increment, w_in_range
import proposed_sparse_prefix448 as proposed
import prefix_selection as selection
import check_fast_mail_proposal as transport
from check_sparse_prefix448_autonomy import ancestors
from check_shifted_halfline import dominant_bit


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
    masks = []
    for size in range(5):
        for positions in combinations(range(11, 26), size):
            if all(sum(start <= pos < start+11 for pos in positions) <= 2 for start in range(1, 26)):
                masks.append(positions)
    assert len(masks) == 251
    # Two eleven-site intervals cover11..25, so no admissible mask has
    # more than four faults. The enumeration is therefore exhaustive.
    rows = []
    for mask in masks:
        bad = set(mask)
        mask_count = 0
        mask_holders = []
        for address in range(2, 14):
            class BoundNet(Net):
                def input(self, name):
                    if name[0] == 'x':
                        _, offset, field, bit = name
                        position = address+offset
                        healthy = position >= 2 and position not in bad
                        if field == 'addr' and healthy:
                            return ((position % p.Q) >> bit) & 1
                        if field == 'age' and healthy:
                            return super().input(('common_clock', bit))
                        if field in ('f1', 'f2', 'wf1', 'wf2') and healthy and position < p.Q:
                            return 0
                        if field in tagged and healthy:
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
            exec(compile(source, '<same SP4 source, arbitrary prefix and far pair>', 'exec'), build_namespace)
            bounded = build_namespace['build'](p)
            assert [bounded.outputs['y', 'addr', bit] for bit in range(p.k)] == const_word(address, p.k)
            common = [bounded.input(('common_clock', bit)) for bit in range(p.m)]
            assert [bounded.outputs['y', 'age', bit] for bit in range(p.m)] == mixed_age_increment(
                bounded, common, p.PB, p.R, p.nb)
            assert bounded.outputs['y', 'f1', 0] == bounded.outputs['y', 'f2', 0] == 0
            assert bounded.outputs['y', 'wf1', 0] == 0
            window = w_in_range(bounded, common, p.age_code(p.T_wf),
                                p.age_code(p.T_wf+2*p.Q-1)+1)
            signal = bounded.input(('coherent_copy', 3, 'info', 0))
            expected = bounded.AND(window, signal) if address < 5 else 0
            assert bounded.outputs['y', 'wf2', 0] == expected, (mask, address, 'signal voter')
            checked = []
            for slot in proposed.SLOTS:
                logical = address+slot
                if logical < 3:
                    continue
                for field in ('info', 'hold', 'ml'):
                    name = ('y', field, slot+2)
                    support = ancestors(bounded, bounded.outputs[name])
                    assert all(inp[0] != 'I' for inp in support), (mask, address, name)
                    raw = {address+inp[1] for inp in support if inp[0] == 'x'}
                    assert all(pos >= 2 and pos not in bad for pos in raw), (mask, address, name, raw)
                    checked.append(dict(field=field, logical_primary=logical, copy_slot=slot,
                                        raw_input_positions=sorted(raw),
                                        coherent_primaries=sorted({inp[1] for inp in support if inp[0] == 'coherent_copy'})))
            mask_count += len(checked)
            mask_holders.append(dict(holder_address=address, conditional_copy_outputs_checked=len(checked),
                                     raw_input_positions=sorted({pos for row in checked for pos in row['raw_input_positions']}),
                                     coherent_primaries=sorted({pos for row in checked for pos in row['coherent_primaries']})))
        assert mask_count == 162
        rows.append(dict(fault_positions=list(mask), conditional_copy_outputs_checked=mask_count,
                         checked_holders=mask_holders))
    count = sum(row['conditional_copy_outputs_checked'] for row in rows)
    assert count == 251*162 == 40662
    # The actual consumed programme outputs have a tighter input envelope
    # than the whole rule's radius12. This is only a one-update support fact.
    keys = {'laddr', 'psel', 'arrive'}
    fields = {'reg', 'pend', 'pkind', 'pval', 'hold', 'scr'}
    geometric = {'addr', 'age', 'f1', 'f2', 'wf1', 'wf2'}
    data_support = {}
    geometry_support = {}
    consumed = []
    for name, node in actual.outputs.items():
        if name[0] in keys or name[0] == 'y' and name[1] in fields:
            consumed.append(name)
            for inp in ancestors(actual, node):
                if inp[0] == 'x':
                    target = geometry_support if inp[2] in geometric else data_support
                    target.setdefault(inp[2], set()).add(inp[1])
    assert len(consumed) == 134
    assert set(data_support) == {'reg', 'pkind', 'hold', 'pend', 'pval', 'scr', 'h1', 'info'}
    assert data_support['reg'] == set(range(-5, 6))
    assert all(offsets == set(range(-4, 5)) for field, offsets in data_support.items() if field != 'reg')
    assert set(geometry_support) == {'addr', 'age', 'wf1', 'f1'}
    assert geometry_support['f1'] == set(range(9))
    assert all(offsets == set(range(-5, 6)) for field, offsets in geometry_support.items() if field != 'f1')
    dependencies = ('SP4_program_build.json', 'SP4_maintenance_certificate.json',
                    'SP4_autonomy_certificate.json', 'SP4_shifted_halfline_certificate.json',
                    'SP4_boundary_pair_modules_certificate.json', 'SP4_boundary_prefix_pair_certificate.json')
    result = dict(
        proposal='SP4', proposed_rule_change=True, active_G17_modified=False,
        proposed_candidate_sha256=candidate.digest(), proposed_netlist_sha256=candidate.comp.digest,
        proposal_source_sha256=digest(Path(proposed.__file__)), checker_sha256=digest(Path(__file__)),
        full_rule_sha256=digest(ROOT / 'gacsca/rule_g.py'),
        selection_source_sha256=digest(ROOT / 'Report/proofs/prefix_selection.py'),
        transport_checker_sha256=digest(ROOT / 'Report/proofs/check_fast_mail_proposal.py'),
        dominant_bit_helper_sha256=digest(ROOT / 'Report/proofs/check_shifted_halfline.py'),
        actual_generated_source_sha256=hashlib.sha256(source.encode()).hexdigest(),
        majority_truth_assignments_checked=32, common_clock_bits_free=p.m,
        arbitrary_upper_prefix='all upper columns below2', local_fault_position_range=[11, 25],
        exhaustive_local_fault_masks=rows, local_fault_masks_checked=len(masks),
        boundary_addresses_checked=list(range(2, 14)),
        conditional_boundary_copy_outputs_checked=count, literal_Workspace_signal_identity_cases=251*12,
        selected_outputs_independent_of_arbitrary_prefix_and_faults=True,
        consumed_programme_outputs=consumed,
        consumed_simulation_field_offsets={f:sorted(o) for f,o in data_support.items()},
        consumed_geometric_field_offsets={f:sorted(o) for f,o in geometry_support.items()},
        active_register_holder_frame=[36, 411], consumed_simulation_input_frame=[31, 416],
        consumed_all_x_input_frame=[31, 419], support_fact_is_one_update_only=True,
        proof_receipt_sha256={name:digest(out / name) for name in dependencies},
        substitutions='quiet canonical GF outside the current faults on upper indices>=2; arbitrary words below2 and at current faults>=11 with two-per-eleven density; coherent healthy tagged cohorts for logical primaries>=3',
        repeated_physical_core_trajectory_established=False, cohort_preservation_established_by_this_checker=False,
        arbitrary_many_real_cores_covered=False, universal_higher_island_repair_established=False,
        global_reliability_established=False,
        scope='conditional combined-prefix/distant-fault GF/NF, Workspace and copy identities; one-update programme support, no trajectory iteration')
    (out / 'SP4_boundary_prefix_modules_certificate.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(dict(conditional_copy_outputs=count, literal_Workspace_cases=251*12,
                          programme_simulation_input_frame=[31, 416], programme_all_x_input_frame=[31, 419])), flush=True)


if __name__ == '__main__':
    main()
