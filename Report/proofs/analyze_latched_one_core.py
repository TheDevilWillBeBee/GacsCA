#!/usr/bin/env python3
"""Validate retained SP7 finite driven one-core recovery observations."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import numpy as np
from gacsca import machine,codec
import proposed_sparse_latched448 as proposed


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out = ROOT/'figs/robustness'
    candidate = proposed.load_artifact()
    p = candidate.p
    physical_path = out/'SP7_latched_one_core_physical.json'
    physical = json.loads(physical_path.read_text())
    assert physical['completed_periods'] == len(physical['checks']) == 20
    for row in physical['checks']:
        control,driven = row['rings']
        assert control['geometry_sites'] == 0
        assert driven['geometry_sites'] == (p.Q if row['period']<16 else 0)
        assert driven['upper_GF_changed_cells'] == ([0] if row['period']<17 else [])
    snapshots = []
    asset = out/'SP7_latched_one_core_tracking.npz'
    with np.load(asset,allow_pickle=False) as saved:
        assert len(saved['overwrite_ticks']) == 17
        assert sum(np.count_nonzero(sites>=0) for sites in saved['overwrite_sites']) == 257
        for tick,packed in zip(saved['snapshot_ticks'],saved['first_eight_colonies_packed']):
            raw = machine.CKernel.unpack(packed[3],8*p.Q)
            reference = machine.CKernel.unpack(packed[0],8*p.Q)
            period = int(tick)//p.U
            physical_bits = int(np.count_nonzero(raw!=reference))
            if period == 16:
                assert physical_bits == 5
            if period >= 17:
                assert physical_bits == 0
            decoded = codec.decode(candidate,raw)
            expected = codec.decode(candidate,reference)
            changed = np.flatnonzero(np.any(decoded[:,:7]!=expected[:,:7],axis=0)).tolist()
            assert changed == ([0] if period<17 else [])
            snapshots.append(dict(period=period,physical_differing_bits_in_first_eight_colonies=physical_bits,
                                  fixed_decoded_whole_words_different_first_seven=changed,
                                  fixed_decoded_parent_GF_flags={field:candidate.field(decoded,field)[:3].tolist() for field in ('addr','age','f1','f2')}))
        final = saved['final_packed']
        assert np.array_equal(final[3],final[0])
    result = dict(proposal='SP7',proposed_rule_change=True,active_G17_modified=False,
                  proposed_candidate_sha256=candidate.digest(),proposed_netlist_sha256=candidate.comp.digest,
                  proposal_source_sha256=digest(Path(proposed.__file__)),checker_sha256=digest(Path(__file__)),
                  physical_receipt_sha256=digest(physical_path),tracking_asset_sha256=digest(asset),
                  SP6_comparison_receipt_sha256=digest(out/'SP6_relay_one_core_physical.json'),
                  computed_period_checkpoints=20,snapshots=snapshots,
                  physical_GF_first_observed_recovered_period=16,
                  fixed_decoded_upper_GF_first_observed_recovered_period=17,
                  final_period=20,final_whole_physical_state_matches_reference=True,
                  noisy_domain_physical_cells=p.Q*p.Q,changed_boundary_condition=True,
                  actual_full_infinite_hierarchy_equivalence_established=False,
                  universal_one_core_repair_deadline_established=False,
                  repeated_core_or_general_island_repair_established=False,
                  positive_iid_threshold_established=False,global_reliability_established=False,
                  scope='retained finite driven one-core experiment; exact artifact observations, measured only')
    (out/'SP7_latched_one_core_analysis.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(physical_GF_period=16,upper_GF_period=17,full_final_physical_equal=True)))


if __name__ == '__main__':
    main()
