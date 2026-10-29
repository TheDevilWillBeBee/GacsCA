#!/usr/bin/env python3
"""Read SP14's retained finite experiment; no universal repair claim."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import numpy as np
from gacsca import machine, codec
import proposed_sparse_framed448 as proposed


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out = ROOT / 'figs/robustness'
    candidate = proposed.load_artifact()
    p = candidate.p
    physical_path = out / 'SP14_framed_one_core_physical.json'
    physical = json.loads(physical_path.read_text())
    assert physical['completed_periods'] == len(physical['checks']) == 20
    asset = out / 'SP14_framed_one_core_tracking.npz'
    snapshots, pulses = [], []
    with np.load(asset, allow_pickle=False) as saved:
        assert len(saved['overwrite_ticks']) == 17
        assert sum(np.count_nonzero(sites >= 0) for sites in saved['overwrite_sites']) == 257
        for tick, packed in zip(saved['snapshot_ticks'], saved['first_eight_colonies_packed']):
            raw = machine.CKernel.unpack(packed[3], 8*p.Q)
            reference = machine.CKernel.unpack(packed[0], 8*p.Q)
            decoded, expected = codec.decode(candidate, raw), codec.decode(candidate, reference)
            snapshots.append(dict(period=int(tick)//p.U,
                physical_differing_bits_in_first_eight_colonies=int(np.count_nonzero(raw != reference)),
                fixed_decoded_whole_words_different_first_seven=np.flatnonzero(
                    np.any(decoded[:, :7] != expected[:, :7], axis=0)).tolist()))
        assert len(saved['pulse_ticks']) == len(physical['pulse_rows']) == 39
        for tick, packed, observed in zip(saved['pulse_ticks'], saved['pulse_first_eight_colonies_packed'], physical['pulse_rows']):
            raw = machine.CKernel.unpack(packed[3], 8*p.Q)
            reference = machine.CKernel.unpack(packed[0], 8*p.Q)
            fields = {f: candidate.field(raw, f) for f in
                ('addr', 'age', 'f1', 'wf2', 'packet_valid', 'packet_tag', 'packet_count',
                 'service_valid', 'service_position', 'service_count')}
            sites = np.flatnonzero(fields['packet_valid'] & fields['wf2'] & (fields['packet_tag'] < 5))
            coded = np.flatnonzero(fields['service_valid'])
            row = dict(tick=int(tick), period=int(tick)//p.U, clock=int(tick)%p.U,
                first_colony_canonical_GF=int(np.count_nonzero(fields['addr'][:p.Q] == np.arange(p.Q))),
                first_colony_reference_Age=int(np.count_nonzero(fields['age'][:p.Q] == candidate.field(reference, 'age')[:p.Q])),
                first_colony_Flag1=int(fields['f1'][:p.Q].sum()),
                packet_sites=sites.tolist(), packet_tags=fields['packet_tag'][sites].tolist(),
                packet_counts=fields['packet_count'][sites].tolist(),
                packet_origins=(sites - fields['packet_tag'][sites].astype(np.int64) - 1).tolist(),
                code_count=len(coded), code_origins=np.unique(coded - fields['service_position'][coded].astype(np.int64)).tolist(),
                code_counter_range=[int(fields['service_count'][coded].min()), int(fields['service_count'][coded].max())] if len(coded) else None)
            for key, value in row.items():
                assert observed[key] == value, (tick, key)
            pulses.append(row)
        final_equal = bool(np.array_equal(saved['final_packed'][3], saved['final_packed'][0]))
        last_gf = saved['every_tick_last_rows'][3].tolist()
        last_whole = saved['every_tick_last_any'][3].tolist()
        assert last_gf[:8] == physical['final_driven_GF_last_difference_first_eight']
    def first_zero(key):
        return next((row['period'] for row in physical['checks'] if not row['rings'][1][key]), None)
    birth = next((row for row in pulses if row['packet_counts'] and 0 in row['packet_counts']), None)
    pulse15 = [row for row in pulses if row['period'] == 15]
    source_clock = birth['clock'] if birth else None
    result = dict(proposal='SP14', proposed_rule_change=False, active_G17_modified=False,
        proposed_candidate_sha256=candidate.digest(), proposed_netlist_sha256=candidate.comp.digest,
        proposal_source_sha256=digest(Path(proposed.__file__)), checker_sha256=digest(Path(__file__)),
        physical_receipt_sha256=digest(physical_path), tracking_asset_sha256=digest(asset),
        computed_period_checkpoints=20, snapshots=snapshots, verified_pulse_snapshots=len(pulses),
        first_retained_fresh_packet=birth, period15_pulses=pulse15,
        physical_GF_first_observed_recovered_period=first_zero('geometry_sites'),
        fixed_decoded_upper_GF_first_observed_recovered_period=first_zero('upper_GF_changed_cells'),
        GF_last_differing_computed_tick_by_colony=last_gf,
        whole_word_last_differing_computed_tick_by_colony=last_whole,
        first_colony_GF_matches_every_computed_tick_from=last_gf[0] + 1,
        first_colony_GF_recovery_clock=(last_gf[0] + 1) % p.U,
        first_colony_GF_recovery_updates_after_retained_birth=(last_gf[0] + 1) - birth['tick'] if birth else None,
        packet_expiry_retained_clock=next((row['clock'] for row in pulse15
            if row['clock'] > source_clock and not row['packet_sites'] and not row['code_count']), None),
        boundary_control_GF_zero_at_every_checkpoint=all(not row['rings'][0]['geometry_sites'] for row in physical['checks']),
        final_period=20, final_whole_physical_state_matches_reference=final_equal,
        noisy_domain_physical_cells=p.Q*p.Q, changed_boundary_condition=True,
        continuing_E0=False, actual_full_infinite_hierarchy_equivalence_established=False,
        shifted_source_proof_premises_established_globally_by_experiment=False,
        universal_one_core_repair_deadline_established=False,
        repeated_core_or_general_island_repair_established=False,
        positive_iid_threshold_established=False, global_reliability_established=False,
        scope='retained finite driven one-core experiment with own SP14 program; exact artifact observations, measured only')
    (out / 'SP14_framed_one_core_analysis.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({key: result[key] for key in
        ('physical_GF_first_observed_recovered_period', 'fixed_decoded_upper_GF_first_observed_recovered_period',
         'first_colony_GF_recovery_clock', 'first_colony_GF_recovery_updates_after_retained_birth',
         'packet_expiry_retained_clock', 'final_whole_physical_state_matches_reference')}))


if __name__ == '__main__':
    main()
