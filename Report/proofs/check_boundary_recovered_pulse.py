#!/usr/bin/env python3
"""Exact SP4 unit-courier identities for the two-period recovery output.

The two-upper-transition transfer from physical captures is proved in the
document. This certifies its local gates/timing, not repeated-core recovery
or a positive iid-noise threshold. No active rule is modified.
"""
import hashlib
import json
from pathlib import Path
import sys
from types import FunctionType, SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from gacsca import rule_g
from gacsca.netlist import Net, Compiled, const_word
import proposed_sparse_prefix448 as proposed
import prefix_selection as selection
import check_fast_mail_proposal as transport
from check_shifted_halfline import dominant_bit
from check_sparse_prefix448_autonomy import ancestors


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
    cases = []
    scenarios = [('pair', anchor, 0) for anchor in range(1, 39)]+[('shifted', None, 2)]
    for mode, anchor, boundary in scenarios:
        faults = {anchor, anchor+1} if anchor is not None else set()
        count = 0
        for primary in range(3, 29):
            clock = p.T_sig+2-primary
            assert 25318 <= clock <= 25343
            for address in range(primary-2, primary+3):
                if address < boundary:
                    continue
                class BoundNet(Net):
                    def input(self, name):
                        if name[0] == 'x':
                            _, offset, field, bit = name
                            position = address+offset
                            healthy = position >= boundary and position not in faults
                            if field == 'addr' and healthy:
                                return ((position % p.Q) >> bit) & 1
                            if field == 'age' and healthy:
                                return (p.age_code(clock) >> bit) & 1
                            if field in ('f1', 'f2', 'wf1', 'wf2') and healthy and position < p.Q:
                                return 0
                            if field in tagged and healthy:
                                width = proposed.logical_width(field, p)
                                logical = position+bit//width-2
                                if logical >= 3:
                                    return super().input(('coherent_copy', logical, field, bit % width))
                        return super().input(name)

                build_namespace = dict(rule_g.__dict__)
                build_namespace.update(Net=BoundNet, maintenance=SimpleNamespace(build=maintenance),
                                       maj5=dominant_bit, OFFSETS=tuple(range(-12, 13)),
                                       sparse_controls=transport.sparse_controls,
                                       sparse_table=proposed.dependency_table(p))
                exec(compile(source, '<same SP4 source, recovered unit courier>', 'exec'), build_namespace)
                bounded = build_namespace['build'](p)
                assert [bounded.outputs['y', 'addr', bit] for bit in range(p.k)] == const_word(address, p.k)
                assert [bounded.outputs['y', 'age', bit] for bit in range(p.m)] == const_word(p.age_code(clock+1), p.m)
                assert bounded.outputs['y', 'f1', 0] == bounded.outputs['y', 'f2', 0] == 0
                slot = primary-address
                node = bounded.outputs['y', 'ml', slot+2]
                expected = bounded.input(('coherent_copy', primary+1, 'ml', 0))
                assert node == expected, (mode, anchor, primary, address)
                assert ancestors(bounded, node) == {('coherent_copy', primary+1, 'ml', 0)}
                count += 1
        assert count == (130 if mode == 'pair' else 129)
        cases.append(dict(mode=mode, pair_anchor=anchor, arbitrary_prefix_below=boundary,
                          source_identity_cases=count))
        if anchor in (10, 20, 30, 38) or mode == 'shifted':
            print(json.dumps(dict(mode=mode, through_anchor=anchor,
                                  source_identity_cases=sum(row['source_identity_cases'] for row in cases))), flush=True)
    total = sum(row['source_identity_cases'] for row in cases)
    assert total == 38*130+129 == 5069
    programme = json.loads((out / 'SP4_boundary_prefix_modules_certificate.json').read_text())
    assert programme['consumed_all_x_input_frame'] == [31, 419]
    restart_phases = []
    for phi in range(p.U):
        if 25320 <= phi <= p.T_sig:
            primary = 3+p.T_sig-phi
            assert 3 <= primary <= 27
            assert phi-2 == p.T_sig+2-(primary+1)
            assert phi-1 == p.T_sig+2-primary
            assert primary-2 < 26
            restart_phases.append(dict(recovered_clock=phi, current_pulse_primary=primary,
                                       first_input_clock=phi-2, second_input_clock=phi-1,
                                       first_target_primary=primary+1, second_target_primary=primary))
    assert len(restart_phases) == 25
    # Larger pulse positions have all their backup holders in the whole
    # pristine domain of J47, and need no new near-strip identity.
    assert 28-2 == 26
    dependencies = ('SP4_program_build.json', 'SP4_maintenance_certificate.json',
                    'SP4_localization_certificate.json', 'SP4_autonomy_certificate.json',
                    'SP4_operational_certificate.json', 'SP4_shifted_halfline_certificate.json',
                    'SP4_boundary_pair_modules_certificate.json', 'SP4_coupled_boundary_core_certificate.json',
                    'SP4_boundary_prefix_modules_certificate.json', 'SP4_boundary_signal_restart_certificate.json')
    result = dict(
        proposal='SP4', proposed_rule_change=True, active_G17_modified=False,
        proposed_candidate_sha256=candidate.digest(), proposed_netlist_sha256=candidate.comp.digest,
        proposal_source_sha256=digest(Path(proposed.__file__)), checker_sha256=digest(Path(__file__)),
        full_rule_sha256=digest(ROOT / 'gacsca/rule_g.py'),
        selection_source_sha256=digest(ROOT / 'Report/proofs/prefix_selection.py'),
        transport_checker_sha256=digest(ROOT / 'Report/proofs/check_fast_mail_proposal.py'),
        dominant_bit_helper_sha256=digest(ROOT / 'Report/proofs/check_shifted_halfline.py'),
        actual_generated_source_sha256=hashlib.sha256(source.encode()).hexdigest(),
        majority_truth_assignments_checked=32, source_identity_cases=total,
        pair_anchor_range=[1, 38], pulse_primary_range=[3, 28], case_summaries=cases,
        nonpristine_strip_restart_clock_range=[25320, 25344], restart_clock_cases=restart_phases,
        selected_ML_source_is_only_next_logical_cohort=True,
        trajectory_transfer_is_separate=True, physical_core_reachable_pulse_proof='ROBUSTNESS J52',
        proof_receipt_sha256={name:digest(out / name) for name in dependencies},
        repeated_physical_core_capture_map_established=False,
        private_snapshot_restart_established=False, universal_higher_island_repair_established=False,
        global_reliability_established=False,
        scope='exact unit-ML source identities and two-step phase support; J47 pulse transfer separate, no repeated-core or iid theorem')
    (out / 'SP4_boundary_recovered_pulse_certificate.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(dict(unit_courier_identities=total, restart_clock_cases=len(restart_phases))), flush=True)


if __name__ == '__main__':
    main()
