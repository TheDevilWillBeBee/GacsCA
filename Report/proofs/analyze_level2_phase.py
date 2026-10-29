#!/usr/bin/env python3
"""Recheck retained level2 phase measurements; no infinite-time inference."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import numpy as np
from gacsca import codec, machine
import proposed_sparse_prefix448 as sp4
import proposed_sparse_quiet as sp2


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out = ROOT / 'figs/robustness'
    results = []
    for prefix, module in (('SP4', sp4), ('SP2', sp2)):
        candidate = module.load_artifact()
        p = candidate.p
        receipt_path = out / (prefix+'_level2_phase_physical.json')
        receipt = json.loads(receipt_path.read_text())
        inputs = out / (prefix+'_level2_phase_inputs.npz')
        tracking = out / (prefix+'_level2_phase_tracking.npz')
        assert receipt['proposed_candidate_sha256'] == candidate.digest()
        assert receipt['input_asset_sha256'] == digest(inputs)
        assert receipt['tracking_asset_sha256'] == digest(tracking)
        rows = []
        comparisons = 0
        for case in range(4):
            checks = [c for c in receipt['checks'] if c['case'] == case]
            steady = [c for c in checks if c['period'] >= 8]
            assert len(steady) == 25
            expected_width = 4*p.Q-checks[0]['phase_shift']
            for a, b in zip(steady, steady[1:]):
                assert b['geometry_min']-a['geometry_min'] == 3*p.Q
                assert b['geometry_max']-a['geometry_max'] == 3*p.Q
                assert a['bad_geometry_sites'] == b['bad_geometry_sites'] == expected_width
                assert a['whole_state_differing_packed_words'] > 0
                comparisons += 1
            rows.append(dict(case=case, initial_phase=checks[0]['phase_shift'],
                             initial_geometry_counts=[c['bad_geometry_sites'] for c in checks[:7]],
                             final_geometry_min=checks[-1]['geometry_min'],
                             final_geometry_max=checks[-1]['geometry_max'],
                             final_geometry_sites=checks[-1]['bad_geometry_sites'],
                             final_upper_decoder_changed_sites=len(checks[-1]['upper_decoder_changed_sites']),
                             final_whole_state_differing_words=checks[-1]['whole_state_differing_packed_words']))
        snapshots = []
        with np.load(tracking, allow_pickle=False) as saved:
            periods, states = saved['periods'], saved['states']
        for period in (8, 16, 32):
            index = int(np.flatnonzero(periods == period)[0])
            for case in range(4):
                check = next(c for c in receipt['checks'] if c['case'] == case and c['period'] == period)
                raw = machine.CKernel.unpack(states[index, case], p.Q**2)
                begin, end, shift = check['geometry_min'], check['geometry_max'], check['phase_shift']
                xs = np.arange(begin, end+1)
                assert np.all(candidate.field(raw, 'addr')[xs] == (xs-shift) % p.Q)
                assert np.all(candidate.field(raw, 'age')[xs] == p.age_code(0))
                # A translated fixed-layout read is a diagnostic only. It
                # is not a decoder/intertwining theorem for these colonies.
                apparent = codec.decode(candidate, np.roll(raw, -shift, axis=1))
                js = np.arange(begin//p.Q, begin//p.Q+4) % p.Q
                addresses = candidate.field(apparent, 'addr')[js].tolist()
                ages = candidate.field(apparent, 'age')[js].tolist()
                assert addresses == [0, 0, 0, 0]
                assert ages == [1, 0, 0, 0]
                snapshots.append(dict(case=case, period=period, apparent_column_indices=js.tolist(),
                                      apparent_Address=addresses, apparent_raw_Age=ages,
                                      apparent_Flag1=candidate.field(apparent, 'f1')[js].tolist(),
                                      apparent_Flag2=candidate.field(apparent, 'f2')[js].tolist(),
                                      lower_boundary_Flag2_sites=int(np.count_nonzero(candidate.field(raw, 'f2')))))
        results.append(dict(proposal=prefix, Q=p.Q, U=p.U,
                            proposed_candidate_sha256=candidate.digest(),
                            proposed_netlist_sha256=candidate.comp.digest,
                            physical_receipt_sha256=digest(receipt_path),
                            input_asset_sha256=digest(inputs), tracking_asset_sha256=digest(tracking),
                            steady_boundary_step_comparisons=comparisons,
                            steady_period_range=[8, 32], measured_right_shift_per_period=3*p.Q,
                            cases=rows, apparent_snapshot_reads=snapshots,
                            native_C_comparison=False))
    receipt = dict(checker_sha256=digest(Path(__file__)), active_G17_modified=False,
                   results=results, geometry_translation_observed=True,
                   apparent_snapshot_clock_pattern=[1, 0, 0, 0],
                   higher_island_eroder_established=False,
                   eternal_travelling_pattern_established=False,
                   iid_unreliability_established=False, global_reliability_established=False,
                   scope='reproducible finite boundary and apparent-row observations, not a valid upper trajectory or all-stage source-clock proof')
    (out / 'level2_phase_analysis.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(dict(proposals=[r['proposal'] for r in results],
                          boundary_step_comparisons=sum(r['steady_boundary_step_comparisons'] for r in results),
                          apparent_snapshot_reads=sum(len(r['apparent_snapshot_reads']) for r in results),
                          eternal_pattern=False)), flush=True)


if __name__ == '__main__':
    main()
