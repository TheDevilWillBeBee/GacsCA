#!/usr/bin/env python3
"""Independent finite geometry review of GMW3; no Gray/iid theorem."""
from itertools import combinations, product
from pathlib import Path
import hashlib
import json
import sys
import time
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'Report/proofs/gray_counterexamples'
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(SOURCE))
import gray_moving_word_v3 as kernel


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    start = time.monotonic()
    folder = ROOT / 'figs/gray_counterexamples'
    names = ('GMW3_fast_transport_certificate.json',
             'GMW3_full_proposed_certificate.json',
             'GMW3_deadline_certificate.json')
    transport, emission, deadline = [json.loads((folder / name).read_text()) for name in names]
    for row in (transport, emission, deadline):
        assert (row['Q'], row['U'], row['lambda_original'], row['c_original']) == (8192, 1048576, 24, 104)
        assert row['kernel_sha256'] == digest(kernel.__file__)
        assert not row['global_reliability_established']
    assert transport['proof_sha256'] == deadline['proof_sha256'] == digest(SOURCE / 'GMW3_FAST_TRANSPORT.md')
    assert transport['asset_sha256'] == digest(folder / 'GMW3_unpaused_E0_transport_witness.npz')

    # Absolute logical output is y=0, physical holder is x=-s.  This
    # enumeration does not call the child's transport-mask function.
    slots = (0, -2, -1, 1, 2)
    assert tuple(kernel.SLOTS) == slots
    records = []
    bit_assignments = 0
    for count in range(3):
        for faulty in combinations(range(-5, 6), count):
            exact_slots = []
            for s in slots:
                all_sources_exact = True
                for delta in range(-3, 4):
                    consulted = [delta - t for t in slots if abs(s + delta - t) <= 5]
                    assert len(consulted) >= 3
                    for actual_bit in (0, 1):
                        relevant = sorted(set(consulted).intersection(faulty))
                        universally_exact = True
                        for replacement in product((0, 1), repeat=len(relevant)):
                            errors = dict(zip(relevant, replacement))
                            positives = sum(errors.get(x, actual_bit) for x in consulted)
                            vote = int(positives >= 3)  # five nominal values, zero padding
                            universally_exact &= vote == actual_bit
                            if actual_bit == 0:
                                assert vote == 0
                            bit_assignments += 1
                        if actual_bit == 1:
                            assert universally_exact == (len(set(consulted).difference(faulty)) >= 3)
                        all_sources_exact &= universally_exact
                if all_sources_exact:
                    exact_slots.append(s)
            assert len(exact_slots) >= 3, (faulty, exact_slots)
            records.append(dict(faulty_sites=list(faulty), simultaneously_exact_slots=exact_slots))
    assert len(records) == 67 and min(len(row['simultaneously_exact_slots']) for row in records) == 3

    restoration_cases = 0
    for actual_bit in (0, 1):
        for count in range(3):
            for faulty in combinations(range(5), count):
                for replacement in product((0, 1), repeat=count):
                    values = [actual_bit] * 5
                    for index, value in zip(faulty, replacement):
                        values[index] = value
                    assert int(sum(values) >= 3) == actual_bit
                    restoration_cases += 1
    assert restoration_cases == 102
    assert all(abs(s + delta - t) <= 5 for s, delta, t in product(slots, (-1, 0, 1), slots))

    cone_point_pairs = 0
    for (x, t), (y, u) in product(product(range(-10, 11), (0, 1)), repeat=2):
        assert abs(x - y) < 24 and abs(t - u) < 24
        cone_point_pairs += 1
    assert cone_point_pairs == 1764
    points = [[3092, 0], [3093, 0], [3117, 8]]
    assert transport['actual_error_points'] == points
    assert min(abs(p[0] - points[2][0]) for p in points[:2]) == 24
    assert transport['original_error_classification']['level0'] == 3
    assert not transport['original_error_classification']['candidate_level1']
    with np.load(folder / 'GMW3_unpaused_E0_transport_witness.npz') as asset:
        sites = asset['sites'].tolist()
        actual, reference = asset['actual'], asset['reference']
        assert asset['errors'].tolist() == points
        for tick in range(1, 9):
            y = 3093 + 3 * tick
            heads = [kernel.cell_from_bits(actual[tick, sites.index(y - s)].tolist()).heads[q]
                     for q, s in enumerate(slots)]
            assert [int(bool(h)) for h in heads] == ([1, 0, 0, 1, 1] if tick < 8 else [0, 0, 0, 1, 1])
        assert all(not any(kernel.cell_from_bits(bits.tolist()).heads) for bits in actual[9])
        assert any(any(kernel.cell_from_bits(bits.tolist()).heads) for bits in reference[9])
        assert np.array_equal(asset['restored_actual'][9], asset['restored_reference'][9])

    assert emission['programme_bits'] == 58129 and emission['instructions'] == 2410
    assert emission['finite_whole_field_replays'] == 86 and emission['replays_measured_only']
    canonical, dense = deadline['fixtures']
    assert canonical['all_decoded_outputs_correct_at_deadline'] and not canonical['halted_at_deadline']
    assert canonical['uninterrupted_halt_ticks'] == 71354
    assert not dense['all_decoded_outputs_correct_at_deadline'] and 66 in dense['different_field_bits']
    physical = deadline['physical_prefix']
    assert (physical['actual_physical_updates'], physical['all_five_holder_equations_checked']) == (65535, 327675)
    assert (physical['wrong_represented_primary'], physical['expected_Info'], physical['committed_Info']) == (3159, 1, 0)
    assert len(physical['five_boundary_commits']) == 5
    for row in (emission, deadline):
        assert not row['universal_full_beta_identity_proved']
        assert not row['universal_runtime_bound_proved'] and not row['shorter_U_used']
        assert not row['Gray_faithful']
    result = dict(scope='ROBUSTNESS J168; independent all-payload transport geometry, source/witness review and exact limits; inherited native lemma and full deadline trace remain separately certified',
        checker_sha256=digest(__file__), kernel_sha256=digest(kernel.__file__),
        written_component_proof_sha256=digest(SOURCE / 'GMW3_FAST_TRANSPORT.md'),
        child_receipts_sha256={name:digest(folder/name) for name in names},
        Q=8192, U=1048576, error_lambda=24, error_separation_c=104,
        arbitrary_fault_supports=len(records), support_records=records,
        independent_transport_bit_assignments=bit_assignments,
        minimum_simultaneously_exact_output_slots=3,
        complete_vote_restoration_bit_cases=restoration_cases,
        two_update_cone_radius=10, two_update_cone_spatial_diameter=20,
        isolation_cone_point_pairs=cone_point_pairs,
        all_payload_simultaneous_transport_capacity_proved=True,
        unpaused_witness_copy_presence_and_final_loss_checked=True,
        universal_beta_equivalence_or_runtime_bound_proved=False,
        own_complete_encoded_period_proved=False, shorter_U_proved=False,
        faithful_Gray_or_iid_counterexample_proved=False,
        active_rule_modified=False, global_reliability_established=False,
        wall_seconds=time.monotonic()-start)
    output=ROOT/'figs/robustness/GMW3_root_review_certificate.json'
    output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({key:result[key] for key in ('arbitrary_fault_supports',
        'independent_transport_bit_assignments','complete_vote_restoration_bit_cases',
        'isolation_cone_point_pairs','wall_seconds','global_reliability_established')}))


if __name__ == '__main__':
    main()
