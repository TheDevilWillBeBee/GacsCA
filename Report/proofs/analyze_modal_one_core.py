#!/usr/bin/env python3
"""Read SP11's retained finite probe without imposing recovery outcomes."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import numpy as np
from gacsca import machine,codec
import proposed_sparse_modal_clock448 as proposed


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out = ROOT/'figs/robustness'
    candidate = proposed.load_artifact()
    p = candidate.p
    physical_path = out/'SP11_modal_one_core_physical.json'
    physical = json.loads(physical_path.read_text())
    assert physical['completed_periods'] == len(physical['checks']) == 20
    snapshots = []
    asset = out/'SP11_modal_one_core_tracking.npz'
    with np.load(asset,allow_pickle=False) as saved:
        assert len(saved['overwrite_ticks']) == 17
        assert sum(np.count_nonzero(sites>=0) for sites in saved['overwrite_sites']) == 257
        for tick,packed in zip(saved['snapshot_ticks'],saved['first_eight_colonies_packed']):
            raw = machine.CKernel.unpack(packed[3],8*p.Q)
            reference = machine.CKernel.unpack(packed[0],8*p.Q)
            decoded = codec.decode(candidate,raw)
            expected = codec.decode(candidate,reference)
            changed = np.flatnonzero(np.any(decoded[:,:7]!=expected[:,:7],axis=0)).tolist()
            snapshots.append(dict(period=int(tick)//p.U,
                physical_differing_bits_in_first_eight_colonies=int(np.count_nonzero(raw!=reference)),
                fixed_decoded_whole_words_different_first_seven=changed,
                fixed_decoded_parent_GF_flags={field:candidate.field(decoded,field)[:3].tolist()
                                               for field in ('addr','age','f1','f2')}))
        final_equal = bool(np.array_equal(saved['final_packed'][3],saved['final_packed'][0]))
    def first_zero(key):
        return next((row['period'] for row in physical['checks'] if not row['rings'][1][key]),None)
    result = dict(proposal='SP11',proposed_rule_change=True,active_G17_modified=False,
        proposed_candidate_sha256=candidate.digest(),proposed_netlist_sha256=candidate.comp.digest,
        proposal_source_sha256=digest(Path(proposed.__file__)),checker_sha256=digest(Path(__file__)),
        physical_receipt_sha256=digest(physical_path),tracking_asset_sha256=digest(asset),
        computed_period_checkpoints=20,snapshots=snapshots,
        physical_GF_first_observed_recovered_period=first_zero('geometry_sites'),
        fixed_decoded_upper_GF_first_observed_recovered_period=first_zero('upper_GF_changed_cells'),
        boundary_control_GF_zero_at_every_checkpoint=all(not row['rings'][0]['geometry_sites'] for row in physical['checks']),
        final_period=20,final_whole_physical_state_matches_reference=final_equal,
        noisy_domain_physical_cells=p.Q*p.Q,changed_boundary_condition=True,
        actual_full_infinite_hierarchy_equivalence_established=False,
        universal_one_core_repair_deadline_established=False,
        repeated_core_or_general_island_repair_established=False,
        positive_iid_threshold_established=False,global_reliability_established=False,
        scope='retained finite driven one-core experiment; exact artifact observations, measured only')
    (out/'SP11_modal_one_core_analysis.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({key:result[key] for key in ('physical_GF_first_observed_recovered_period',
        'fixed_decoded_upper_GF_first_observed_recovered_period','final_whole_physical_state_matches_reference')}))


if __name__=='__main__':
    main()
