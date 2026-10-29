#!/usr/bin/env python3
"""Analyze saved SP4 repeated-near snapshots; measured finite scope only."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import numpy as np
from gacsca import codec, machine
import proposed_sparse_prefix448 as proposed


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out = ROOT / 'figs/robustness'
    receipt_path = out / 'SP4_repeated_near_core_physical.json'
    receipt = json.loads(receipt_path.read_text())
    assert receipt['completed_periods'] == len(receipt['checks']) == 80
    candidate = proposed.load_artifact()
    p = candidate.p
    assert receipt['proposed_candidate_sha256'] == candidate.digest()
    assert receipt['recorded_overwrite_batches'] == 68
    gf_rows = [candidate.row[field, bit] for field, width in (('addr', p.k), ('age', p.m))
               for bit in range(width)]
    records = {row['period']:row for row in receipt['checks']}
    for period, row in records.items():
        control, driven = row['rings']
        assert control['geometry_sites'] == 0
        if period <= 25:
            assert driven['geometry_first_eight_colonies'] == [448]+[0]*7
        elif period <= 50:
            assert driven['geometry_first_eight_colonies'] == [448,448]+[0]*6
        if period >= 51:
            assert driven['upper_GF_changed_cells'] == list(range(3*(period-49)))
            assert driven['geometry_sites'] == p.Q*3*(period-49)
            assert driven['geometry_min'] == 0 and driven['geometry_max'] == driven['geometry_sites']-1
    tracking_path = out / 'SP4_repeated_near_core_tracking.npz'
    with np.load(tracking_path, allow_pickle=False) as saved:
        ticks = saved['snapshot_ticks']
        snapshots = saved['first_eight_colonies_packed']
        assert len(ticks) == len(snapshots) == 15
        assert len(saved['overwrite_ticks']) == len(saved['overwrite_sites']) == len(saved['overwrite_values']) == 68
        assert sum(np.count_nonzero(sites >= 0) for sites in saved['overwrite_sites']) == 1028
        for index, item in enumerate(receipt['cases']):
            for step in range(17):
                batch = index*17+step
                assert saved['overwrite_ticks'][batch] == item['tau']+(step if step < 16 else 38)
                selected = saved['overwrite_sites'][batch]
                expected = np.arange(item['begin'],item['begin']+16) if step < 16 else np.asarray([item['begin']+15])
                assert np.array_equal(selected[selected >= 0], expected)
        summary = []
        for tick, packed in zip(ticks, snapshots):
            period = int(tick)//p.U
            reference = machine.CKernel.unpack(packed[0], 8*p.Q)
            raw = machine.CKernel.unpack(packed[3], 8*p.Q)
            gf_bad = np.any(raw[gf_rows] != reference[gf_rows], axis=0)
            assert [int(part.sum()) for part in np.split(gf_bad,8)] == records[period]['rings'][1]['geometry_first_eight_colonies']
            expected_shifted_addr = (np.arange(8*p.Q)-1) % p.Q
            shifted_correct = candidate.field(raw, 'addr') == expected_shifted_addr
            age_zero = candidate.field(raw, 'age') == 0
            aligned = codec.decode(candidate, np.roll(raw,-1,axis=1))
            blank_clock_words = np.zeros((candidate.W,7), dtype=bool)
            candidate.set_field(blank_clock_words, 'addr', np.arange(7))
            candidate.set_field(blank_clock_words, 'age', 1)
            candidate.set_field(blank_clock_words, 'f1', 1)
            # Exclude cell7: circularizing the cropped eight-colony snapshot
            # would give its last Info copy an invented wrap neighbor.
            equals_P = np.all(aligned[:,:7] == blank_clock_words,axis=0)
            candidate.set_field(blank_clock_words, 'addr', candidate.field(aligned,'addr')[:7])
            equals_P_own_address = np.all(aligned[:,:7] == blank_clock_words,axis=0)
            summary.append(dict(period=period, phase_minus_one_Address_counts_first_eight=[int(part.sum()) for part in np.split(shifted_correct,8)],
                                Age_zero_counts_first_eight=[int(part.sum()) for part in np.split(age_zero,8)],
                                phase_aligned_upper_Address_first_seven=candidate.field(aligned,'addr')[:7].tolist(),
                                phase_aligned_upper_Age_first_seven=candidate.field(aligned,'age')[:7].tolist(),
                                phase_aligned_upper_Flag1_first_seven=candidate.field(aligned,'f1')[:7].tolist(),
                                phase_aligned_upper_Flag2_first_seven=candidate.field(aligned,'f2')[:7].tolist(),
                                phase_aligned_upper_whole_word_equals_P_first_seven=equals_P.tolist(),
                                phase_aligned_upper_whole_word_equals_P_of_own_Address_first_seven=equals_P_own_address.tolist()))
        final_raw = machine.CKernel.unpack(saved['final_packed'][3], p.Q*p.Q)
        final_aligned = codec.decode(candidate, np.roll(final_raw,-1,axis=1))
        final_P = np.zeros_like(final_aligned)
        candidate.set_field(final_P, 'addr', candidate.field(final_aligned,'addr'))
        candidate.set_field(final_P, 'age', 1)
        candidate.set_field(final_P, 'f1', 1)
        final_P_indices = np.flatnonzero(np.all(final_aligned == final_P,axis=0)).tolist()
        final_blank_indices = np.flatnonzero(~final_aligned.any(axis=0)).tolist()
        final_Flag2_indices = np.flatnonzero(candidate.field(final_aligned,'f2')[:93]).tolist()
        assert final_P_indices == [89] and final_blank_indices == [90,91,92]
        assert candidate.field(final_aligned,'addr')[89] == 0
    result = dict(proposal='SP4', proposed_rule_change=True, active_G17_modified=False,
                  proposed_candidate_sha256=candidate.digest(), proposed_netlist_sha256=candidate.comp.digest,
                  proposal_source_sha256=digest(Path(proposed.__file__)), checker_sha256=digest(Path(__file__)),
                  physical_receipt_sha256=digest(receipt_path), tracking_asset_sha256=digest(tracking_path),
                  blank_clock_receipt_sha256=digest(out/'blank_neighbor_clock_certificate.json'),
                  completed_periods=80, first_extra_physical_damaged_colonies=[3,4,5],
                  first_extra_damage_period=51, no_noise_in_extra_colonies_at_first_extra_damage=True,
                  measured_decoded_GF_bad_count_formula='3*(period-49), periods51..80 only',
                  final_decoded_GF_bad_cells=records[80]['rings'][1]['upper_GF_changed_cells'],
                  final_phase_aligned_whole_P_indices=final_P_indices,
                  final_phase_aligned_P_Address=0, final_phase_aligned_blank_word_indices=final_blank_indices,
                  final_phase_aligned_Flag2_set_indices_in_damaged_prefix=final_Flag2_indices,
                  snapshots=summary, changed_boundary_condition=True,
                  measured_whole_word_identity_is_not_a_capture_proof=True,
                  autonomous_infinite_hierarchy_equivalence_established=False,
                  propagation_rate_for_arbitrary_time_established=False,
                  iid_unreliability_established=False, global_reliability_established=False,
                  scope='finite retained snapshot analysis; aligned decoder is a diagnostic, not a proved effective upper map')
    (out/'SP4_repeated_near_analysis.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(periods=80, snapshots=len(summary), final_decoded_GF_bad_count=len(result['final_decoded_GF_bad_cells']),
                          phase_aligned_P_matches={row['period']:row['phase_aligned_upper_whole_word_equals_P_first_seven'] for row in summary})), flush=True)


if __name__ == '__main__':
    main()
