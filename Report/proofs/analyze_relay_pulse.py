#!/usr/bin/env python3
"""Exact retained SP6 one-core/pulse analysis; measured scope only.

The initial trace queried the next update's ML target. This re-reads the
saved state at the correct current-state primary, without rerunning it.
"""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import numpy as np
from gacsca import machine,codec
import proposed_sparse_relay448 as proposed


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cohort(candidate,raw,field,primary):
    width = proposed.logical_width(field,candidate.p)
    holders = list(range(primary-2,primary+3))
    bits = [int(raw[candidate.row[field,(primary-holder+2)*width],holder]) for holder in holders]
    return dict(primary=primary,holders=holders,copies=bits,majority=int(sum(bits)>=3))


def main():
    out = ROOT/'figs/robustness'
    candidate = proposed.load_artifact()
    p = candidate.p
    physical_path = out/'SP6_relay_one_core_physical.json'
    trace_path = out/'SP6_relay_pulse_trace.json'
    physical = json.loads(physical_path.read_text())
    trace = json.loads(trace_path.read_text())
    assert physical['completed_periods'] == 20 and trace['completed_tick'] == 32*p.U
    assert trace['driver_sha256'] == digest(out/'SP6_relay_pulse_trace_driver_v1.py')
    assert all(row['rings'][0]['geometry_sites'] == 0 and row['rings'][1]['geometry_sites'] == p.Q
               for row in physical['checks'])
    snapshots = []
    asset = out/'SP6_relay_one_core_tracking.npz'
    with np.load(asset,allow_pickle=False) as saved:
        for tick,packed in zip(saved['snapshot_ticks'],saved['first_eight_colonies_packed']):
            raw = machine.CKernel.unpack(packed[3],8*p.Q)
            decoded = codec.decode(candidate,np.roll(raw,-1,axis=1))
            assert np.array_equal(candidate.field(raw,'addr')[:p.Q],(np.arange(p.Q)-1)%p.Q)
            assert not candidate.field(raw,'age')[:p.Q].any()
            snapshots.append(dict(period=int(tick)//p.U,
                                  aligned_parent_GF_flags={field:candidate.field(decoded,field)[:3].tolist()
                                                           for field in ('addr','age','f1','f2')}))
    corrected = []
    tracking = out/'SP6_relay_pulse_trace.npz'
    with np.load(tracking,allow_pickle=False) as saved:
        assert len(saved['ticks']) == len(trace['rows']) == len(saved['first_eight_colonies_packed'])
        for tick,packed,old in zip(saved['ticks'],saved['first_eight_colonies_packed'],trace['rows']):
            assert int(tick) == old['tick']
            raw = machine.CKernel.unpack(packed[3],8*p.Q)
            clock = int(tick)%p.U
            primary = 60-(clock-25288) if 25289 <= clock <= 25344 else (59 if clock == 25288 else 4)
            row = dict(old,moving_ML=cohort(candidate,raw,'ml',primary))
            assert row['source_Hold'] == cohort(candidate,raw,'hold',59)
            assert row['special_Info'] == cohort(candidate,raw,'info',4)
            address = candidate.field(raw,'addr')[:p.Q]
            assert row['canonical_Address_sites_first_colony'] == int((address==np.arange(p.Q)).sum())
            assert row['first_colony_Flag_counts'] == {field:int(candidate.field(raw,field)[:p.Q].sum()) for field in ('f1','f2','wf1','wf2')}
            corrected.append(row)
    active = {row['clock']:row for row in corrected if row['period'] == 31 and row['clock']}
    assert active[22529]['source_Hold']['copies'] == [1]*5
    assert active[25289]['moving_ML']['copies'] == active[25344]['moving_ML']['copies'] == [1]*5
    assert active[25345]['special_Info']['copies'] == [1]*5
    assert active[25346]['first_colony_Flag_counts']['wf2'] == 5
    assert active[25700]['canonical_Address_sites_first_colony'] == 404
    assert active[25800]['special_Info']['majority'] == active[25800]['first_colony_Flag_counts']['wf2'] == 0
    assert active[26200]['canonical_Address_sites_first_colony'] == 0
    assert corrected[-1]['period'] == 32 and corrected[-1]['canonical_Address_sites_first_colony'] == 0
    result = dict(proposal='SP6',proposed_rule_change=True,active_G17_modified=False,
                  proposed_candidate_sha256=candidate.digest(),proposed_netlist_sha256=candidate.comp.digest,
                  proposal_source_sha256=digest(Path(proposed.__file__)),checker_sha256=digest(Path(__file__)),
                  physical_receipt_sha256=digest(physical_path),pulse_trace_receipt_sha256=digest(trace_path),
                  input_asset_sha256=digest(asset),tracking_asset_sha256=digest(tracking),
                  original_driver_archive_sha256=digest(out/'SP6_relay_pulse_trace_driver_v1.py'),
                  original_moving_ML_query_off_by_one_corrected_from_saved_state=True,
                  saved_one_core_snapshots=snapshots,corrected_trace_rows=corrected,
                  pulse_correctly_loaded_and_reached_special_Info=True,
                  maximum_observed_canonical_Address_sites_in_pulse=404,
                  Workspace_source_off_while_scheduled_window_still_active=True,
                  geometry_shift_returns_by_clock26200=True,
                  changed_boundary_condition=True,infinite_hierarchy_equivalence_established=False,
                  autonomous_island_repair_established=False,causal_capture_map_proved=False,
                  positive_iid_threshold_established=False,global_reliability_established=False,
                  scope='exact analysis of retained finite driven measurements, not a universal repair or failure theorem')
    (out/'SP6_relay_pulse_analysis.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(corrected_ML_copies=True,observed_canonical_maximum=404,source_lost_at_observed_clock=25800)))


if __name__ == '__main__':
    main()
