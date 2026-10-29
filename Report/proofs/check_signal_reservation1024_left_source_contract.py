#!/usr/bin/env python3
"""J210 local left-source identities; actual-history premises stay explicit."""
from collections import defaultdict
from pathlib import Path
import hashlib
import json
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'Report/proofs/unregistered_terminal'))
from gacsca.netlist import Compiled, mixed_age_increment
import proposed_sparse_signal_reservation1024 as proposed
import proposed_distant_native448 as distant
from check_signal_reservation1024_second_signal import blocked
from probe_sp30_symbolic_left_absorption import AbsorptionNet


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def native_case(p, K, r, pinned_A_bit=None, zero_A_X=False):
    n = AbsorptionNet()
    A = [0 if zero_A_X else 1 if b == pinned_A_bit else n.input(('A', b))
         for b in range(p.m)]
    X = [0 if zero_A_X else n.input(('X', b)) for b in range(p.m)]
    cells = {}
    j = K-r
    for d in range(-5, 9):
        col = j+d
        cells[d] = dict(
            addr=[((col % p.Q) >> b) & 1 for b in range(p.k)]
                 if col <= K-2 else [0]*p.k,
            age=A if col <= K-3 else X if col == K-2 else [0]*p.m,
            f1=0, wf1=n.input(('edgeWF', 0)) if col == K-2 else 0,
            f2=n.input(('f2', d)), wf2=n.input(('wf2', d)))
    function, _ = proposed.proposed_build()
    value = function(n, cells, p.k, p.m, Q=p.Q, nb=p.nb,
                     radix=p.R, pos_bits=p.PB,
                     service_force=n.input(('service_force', 0)))
    assert value['addr'] == [((j % p.Q) >> b) & 1 for b in range(p.k)]
    expected_F1 = (0 if r >= 6 else 1 if r in (2, 3) else
                   1 if r == 4 and (K % p.Q not in (0, 1, p.Q-1)
                                    or pinned_A_bit is not None) else
                   0 if r == 4 and zero_A_X else None)
    if expected_F1 is not None:
        assert value['f1'] == expected_F1, (K, r, pinned_A_bit, value['f1'])
    if r in (2, 3) or r >= 6:
        assert value['age_now'] == A, (K, r)
        assert value['age'] == mixed_age_increment(n, A, p.PB, p.R, p.nb)
    return dict(K_mod_Q=K % p.Q, r=r, fixed_F1=expected_F1,
                pinned_A_one_bit=pinned_A_bit, zero_A_and_X=zero_A_X)


def main():
    start = time.monotonic()
    p = proposed.parameters()
    c = proposed.load_artifact()
    assert (p.Q, p.U, p.T_wf, p.R, p.PB, p.nb, p.m) == (
        1024, 475136, 278401, 928, 10, 512, 19)
    assert distant.CENTERS == (-30, -10, 10, 30)
    assert distant.REFINED == tuple(range(-5, 6))
    assert distant.OFFSETS == tuple(range(-37, 38))
    for a in (0, 1):
        for b in (0, 1):
            assert (a | (a & b)) == a and (a & (a | b)) == a

    # GF cohort exhaustion. Age values are never chosen. A noncanonical
    # GF occurs once at most. Any canonical triple contains a strict-left
    # member, so a quorum pair's Age must be the arbitrary shared A.
    blocks = corners = raw_retained = 0
    for K in range(p.Q):
        for r in range(2, 44):
            j = K-r
            for u in distant.REFINED:
                canonical = (j+u) % p.Q
                for center in distant.CENTERS:
                    cohorts = defaultdict(list)
                    for v in range(-2, 3):
                        col = j+u+center+v
                        gf = col % p.Q if col <= K-2 else 0
                        kind = 'A' if col <= K-3 else 'X' if col == K-2 else 'zero'
                        adjusted = (gf-center-v) % p.Q
                        cohorts[adjusted].append(kind)
                    assert all(len(kinds) <= 1 for gf, kinds in cohorts.items()
                               if gf != canonical)
                    canon = cohorts.get(canonical, [])
                    assert canon.count('X') <= 1 and canon.count('zero') <= 1
                    if len(canon) >= 3:
                        assert 'A' in canon
                        corners += 1
                    if j+u >= K-2 and center > 0:
                        assert all(len(kinds) < 3 for kinds in cohorts.values())
                        raw_retained += 1
                    blocks += 1
    assert blocks == 1024*42*11*4
    # Beyond r43, the rightmost radius37 source is strict-left.
    assert -43+37 <= -6 < -3

    native = []
    for K in range(p.Q):
        for r in range(2, 9):
            native.append(native_case(p, K, r))
    nonzero = [native_case(p, K, 4, pinned_A_bit=b)
               for K in (0, 1, p.Q-1) for b in range(p.m)]
    exceptions = [native_case(p, K, 4, zero_A_X=True)
                  for K in (0, 1, p.Q-1)]
    assert len(native) == 7168 and len(nonzero) == 57 and len(exceptions) == 3

    # Exact actual gather predicate, including every dependency offset
    # and every holder. Its translation/distant-source lift is in the proof.
    fields = ('addr', 'age', 'f1', 'wf1')
    table = [row for row in proposed.dependency_table(p) if row['field'] in fields]
    assert len(table) == 31
    assert all(59 <= row['address'] <= 90 for row in table)
    routes = 0
    for r in range(2, 39):
        for row in table:
            for d in sorted(set((0, *row['offsets']))):
                for slot in proposed.SLOTS:
                    assert blocked(((-p.Q, -p.Q//2),), -r, d,
                                   row['address']+slot, p.Q) == (-r+d >= -1)
                    routes += 1
    for K in range(p.Q):
        for r in range(2, 7):
            j = K-r
            adjusted = [(((j+d) % p.Q if j+d <= K-2 else 0)-d) % p.Q
                        for d in range(1, 6)]
            if r == 4:
                quorum = any(adjusted.count(gf) >= 3 for gf in adjusted)
                assert quorum == (K in (0, 1, p.Q-1))
    assert [p0 for p0 in range(512) if (128-6*p0) % p.Q == 0] == [192]
    assert p.U % 512 == 0
    assert all(p.age_code(t) > 0 for t in range(1, p.T_wf))
    assert all(p.age_code(t) < p.age_code(p.T_wf) for t in range(p.T_wf))
    assert all(p.age_code(t) < p.age_code(t+1) for t in range(p.U-1))

    # Complete function probes use symbolic A/X and every unmentioned
    # raw bit; algebra above covers all K and distances. They are retained
    # as exact universal cofactor checks, never as all-history evidence.
    complete = []
    for K, r, pinned, zeroed in (
        (0, 2, None, False), (0, 3, None, False), (0, 4, 0, False),
        (0, 4, None, True), (0, 5, None, False), (0, 6, None, False),
        (1, 4, 7, False), (1023, 4, 18, False),
        (92, 2, None, False), (92, 4, None, False),
        (92, 6, None, False), (92, 8, None, False),
        (92, 43, None, False)):
        j = K-r
        class Captured(AbsorptionNet):
            def input(self, key):
                if isinstance(key, tuple) and len(key) == 4 and key[0] == 'x':
                    _, d, field, bit = key
                    col = j+d
                    if field in fields:
                        if col >= K-1:
                            return 0
                        if field == 'addr':
                            return ((col % p.Q) >> bit) & 1
                        if field == 'f1':
                            return 0
                        if field == 'wf1':
                            return super().input(('edgeWF', bit)) if col == K-2 else 0
                        assert field == 'age'
                        if zeroed:
                            return 0
                        if col == K-2:
                            return super().input(('X', bit))
                        return 1 if bit == pinned else super().input(('A', bit))
                return super().input(key)
        n, _ = proposed.full_net(p, Captured)
        gf = [n.outputs['y', 'addr', bit] for bit in range(p.k)]
        assert gf == [((j % p.Q) >> bit) & 1 for bit in range(p.k)]
        f1 = n.outputs['y', 'f1', 0]
        expected = (0 if r >= 6 or zeroed else 1 if r in (2, 3, 4) else None)
        if expected is not None:
            assert f1 == expected, (K, r, pinned, f1)
        if r in (2, 3) or r >= 6:
            A = [n.input(('A', bit)) for bit in range(p.m)]
            assert [n.outputs['y', 'age', bit] for bit in range(p.m)] == \
                   mixed_age_increment(n, A, p.PB, p.R, p.nb)
        if zeroed:
            assert n.outputs['y', 'wf1', 0] == 0
        complete.append(dict(K_mod_Q=K % p.Q, r=r, pinned_A_one_bit=pinned,
                             zero_A_and_X=zeroed, fixed_F1=expected,
                             cofactored_complete_netlist_sha256=Compiled(n).digest))

    generated = proposed.generated_source(p)
    assert 'in_wf = w_in_range(n, age_now, p.age_code(p.T_wf),' in generated
    assert 'wf1 = n.all([right_end, in_wf, sim_r])' in generated
    receipts = ('SP30_encoded_certificate.json', 'SP30_zero_GF_prefix_certificate.json',
                'SP30_translation_class_certificate.json', 'SP30_seventh_signal_certificate.json')
    parent = ROOT/'figs/robustness'
    own = json.loads((parent/receipts[0]).read_text())
    assert own['complete_encoded_noiseless_and_all_period_E0_simulation_proved']
    assert c.digest() == own['proposed_candidate_sha256']
    certificate = dict(
        proposal='SP30', scope='J210 complete local arbitrary-shared-Age left-source theorem and conditional gather/store bridge; all-period source supply/general eroder/higher/iid open',
        Q=p.Q, U=p.U, T_wf=p.T_wf, Age_radix=p.R, Age_position_bits=p.PB, Age_blocks=p.nb,
        checker_sha256=digest(__file__),
        written_proof_sha256=digest(ROOT/'Report/proofs/SP30_LEFT_SOURCE_CONTRACT.md'),
        proposal_source_sha256=digest(proposed.__file__),
        proposed_candidate_sha256=c.digest(), proposed_netlist_sha256=c.comp.digest,
        full_generated_source_sha256=hashlib.sha256(generated.encode()).hexdigest(),
        actual_maintenance_source_sha256=hashlib.sha256(proposed.proposed_build()[1].encode()).hexdigest(),
        source_dependencies_sha256={name:digest(ROOT/name) for name in (
            'gacsca/netlist.py', 'gacsca/rule_g.py', 'gacsca/maintenance.py',
            'Report/proofs/proposed_distant_native448.py',
            'Report/proofs/check_signal_reservation1024_second_signal.py',
            'Report/proofs/unregistered_terminal/probe_sp30_symbolic_left_absorption.py',
            'Report/proofs/SP30_OWN_RULE.md', 'Report/proofs/SP30_ZERO_GF_PREFIX.md',
            'Report/proofs/SP30_TRANSLATION_CLASS.md')},
        receipt_dependencies_sha256={name:digest(parent/name) for name in receipts},
        preliminary_probe_assets_sha256={name:digest(parent/name) for name in (
            'unregistered_symbolic_left_clock/receipt.json',
            'unregistered_symbolic_left_absorption/receipt.json',
            'SP30_symbolic_left_clock_unregistered_run.log',
            'SP30_symbolic_left_absorption_unregistered_run.log')},
        initial_successful_format_only_revision_assets_sha256={name:digest(parent/name)
            for name in ('unregistered_left_source_initial_format/proof.md',
                         'unregistered_left_source_initial_format/checker.py.txt',
                         'unregistered_left_source_initial_format/certificate.json',
                         'unregistered_left_source_initial_format/run.log')},
        initial_successful_revision_changed_equations_or_computed_results=False,
        Boolean_absorption_truth_cases=8,
        refinement_GF_cohort_checks=blocks, potential_canonical_GF_quorums=corners,
        erased_right_block_checks=raw_retained, checked_K_residues=1024,
        checked_refinement_receiver_distances=list(range(2, 44)),
        native_symbolic_boundary_cofactors=len(native),
        nonzero_Age_corner_symbolic_cofactors=nonzero,
        zero_Age_corner_exact_exceptions=exceptions,
        complete_symbolic_netlist_cofactors=complete,
        actual_normal_phase_dependency_rows=len(table), actual_five_holder_stride8_route_checks=routes,
        all_integer_K_translations_and_all_receiver_distances_covered=True,
        refinement_raw_pair_identity_proved=True,
        universal_complete_local_GF_Flag1_and_claimed_Age_contract_proved=True,
        arbitrary_shared_raw_Age_free_edge_Age_and_unmentioned_raw_inputs_covered=True,
        Workspace1_zero_under_explicit_Age_below_TF_contract_proved=True,
        correct_mixed_Age_radix928_block512_increment_used=True,
        zero_Age_coordinate_exception_retained=True,
        conditional_actual_gather_and_store_contract_proved=True,
        coordinate_corner_for_proposed_K128_minus6p_is_p192_mod512=True,
        actual_all_period_source_strip_controls_alias_Hold_commit_premises_supplied=False,
        actual_eighth_complete_signal_or_long_history_or_permanent_defect_proved=False,
        all_data_general_noisy_repair_higher_map_positive_iid_or_minimum_global_change_proved=False,
        additional_rule_programme_layout_or_constant_change=False,
        active_G17_or_frozen_SP30_modified=False, numerical_whole_CA_trajectory_used=False,
        numerical_Age_private_or_Info_payload_samples_used=False,
        global_reliability_established=False, seconds=time.monotonic()-start)
    (parent/'SP30_left_source_contract_certificate.json').write_text(json.dumps(certificate, indent=2)+'\n')
    print(json.dumps({key:certificate[key] for key in (
        'refinement_GF_cohort_checks', 'native_symbolic_boundary_cofactors',
        'actual_five_holder_stride8_route_checks',
        'universal_complete_local_GF_Flag1_and_claimed_Age_contract_proved',
        'conditional_actual_gather_and_store_contract_proved',
        'actual_all_period_source_strip_controls_alias_Hold_commit_premises_supplied',
        'seconds', 'global_reliability_established')}), flush=True)


if __name__ == '__main__':
    main()
