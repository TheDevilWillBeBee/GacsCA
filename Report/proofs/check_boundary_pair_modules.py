#!/usr/bin/env python3
"""Conditional private SP4 boundary copies with a two-word upper defect.

This certifies local Boolean identities only. It does not establish the
coupled alias-strip/quiet-boundary trajectory or iid reliability.
"""
import hashlib
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
    rows = []
    for anchor in range(1, 25):
        for address in range(12):
            bad = {anchor, anchor+1}
            class BoundNet(Net):
                def input(self, name):
                    if name[0] == 'x':
                        _, offset, field, bit = name
                        position = address+offset
                        healthy = position >= 0 and position not in bad
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
            exec(compile(source, '<same SP4 source, upper pair and exterior arbitrary>', 'exec'), build_namespace)
            bounded = build_namespace['build'](p)
            assert [bounded.outputs['y', 'addr', bit] for bit in range(p.k)] == const_word(address, p.k)
            common = [bounded.input(('common_clock', bit)) for bit in range(p.m)]
            assert [bounded.outputs['y', 'age', bit] for bit in range(p.m)] == mixed_age_increment(
                bounded, common, p.PB, p.R, p.nb)
            assert bounded.outputs['y', 'f1', 0] == bounded.outputs['y', 'f2', 0] == 0
            # The literal Workspace voter at the near-left boundary reads
            # exactly the common signal3 bit, even with the arbitrary pair
            # and exterior. Setting that preceding cohort to zero therefore
            # forces WF2 zero at every clock, including a faulty center.
            assert bounded.outputs['y', 'wf1', 0] == 0
            window = w_in_range(bounded, common, p.age_code(p.T_wf),
                                p.age_code(p.T_wf+2*p.Q-1)+1)
            signal = bounded.input(('coherent_copy', 3, 'info', 0))
            expected_wf2 = bounded.AND(window, signal) if address < 5 else 0
            assert bounded.outputs['y', 'wf2', 0] == expected_wf2, (anchor, address, 'literal signal3 voter')
            checked = []
            for slot in proposed.SLOTS:
                logical = address+slot
                if logical < 3:
                    continue
                for field in ('info', 'hold', 'ml'):
                    assert proposed.logical_width(field, p) == 1
                    name = ('y', field, slot+2)
                    support = ancestors(bounded, bounded.outputs[name])
                    assert all(inp[0] != 'I' for inp in support), (anchor, address, name)
                    raw = {address+inp[1] for inp in support if inp[0] == 'x'}
                    assert all(pos >= 0 and pos not in bad for pos in raw), (anchor, address, name, raw)
                    checked.append(dict(field=field, logical_primary=logical, copy_slot=slot,
                                        raw_input_positions=sorted(raw),
                                        coherent_primaries=sorted({inp[1] for inp in support if inp[0] == 'coherent_copy'})))
            rows.append(dict(pair_anchor=anchor, holder_address=address,
                             conditional_copy_outputs=checked))
    count = sum(len(row['conditional_copy_outputs']) for row in rows)
    assert count == 24*135 == 3240
    dependencies = ('SP4_program_build.json', 'SP4_localization_certificate.json',
                    'SP4_autonomy_certificate.json', 'SP4_nested_halfline_certificate.json',
                    'SP4_near_boundary_core_certificate.json', 'SP4_shifted_halfline_certificate.json')
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
        pair_anchors_checked=list(range(1, 25)), boundary_addresses_checked=list(range(12)),
        conditional_boundary_copy_outputs_checked=count, conditional_boundary_holders=rows,
        literal_Workspace_signal_identity_cases=24*12,
        zero_signal3_forces_zero_boundary_Workspace_at_all_raw_clocks=True,
        substitutions='canonical quiet GF outside the pair on upper indices>=0; arbitrary exterior and pair words; healthy tagged cohorts for logical primaries>=3',
        proof_receipt_sha256={name:digest(out / name) for name in dependencies},
        trajectory_induction_is_separate=True, coupled_boundary_trajectory_established_by_this_checker=False,
        first_right_lower_colony_core_covered=False, arbitrary_many_real_cores_covered=False,
        global_reliability_established=False,
        scope='conditional boundary copy support, GF/NF and literal Workspace voter identities; trajectory proof separate')
    (out / 'SP4_boundary_pair_modules_certificate.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(dict(conditional_boundary_copy_outputs=count, upper_pair_anchors=24,
                          holder_addresses=12)), flush=True)


if __name__ == '__main__':
    main()
