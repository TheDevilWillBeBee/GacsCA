#!/usr/bin/env python3
"""Read actual barrier premises in the retained finite periodic experiment."""
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
    physical = out / 'SP4_level2_boundary_physical.json'
    tracking = out / 'SP4_level2_boundary_tracking.npz'
    recorded = json.loads(physical.read_text())
    assert recorded['tracking_asset_sha256'] == digest(tracking)
    candidate = proposed.load_artifact()
    p = candidate.p
    assert recorded['proposed_candidate_sha256'] == candidate.digest()
    with np.load(tracking, allow_pickle=False) as saved:
        periods, states = saved['periods'], saved['states']
    rows = []
    for index, period in enumerate(periods.tolist()):
        noisy, clean = [codec.decode(candidate, machine.CKernel.unpack(state, 2*p.Q**2))
                        for state in states[index]]
        a, age = candidate.field(noisy, 'addr'), candidate.field(noisy, 'age')
        ar, ager = candidate.field(clean, 'addr'), candidate.field(clean, 'age')
        assert np.array_equal(ar, np.arange(2*p.Q) % p.Q)
        assert np.all(ager == p.age_code(period))
        assert all(not np.any(candidate.field(clean, field)) for field in ('f1', 'f2', 'wf1', 'wf2'))
        right = slice(p.Q, 2*p.Q)
        flags = {field: int(np.count_nonzero(candidate.field(noisy, field)[right]))
                 for field in ('f1', 'f2', 'wf1', 'wf2')}
        rows.append(dict(
            period=period,
            protected_upper_colony_geometry_changed=int(np.count_nonzero(
                (a[right] != ar[right]) | (age[right] != ager[right]))),
            protected_upper_colony_flag_counts=flags,
            first_five_upper_right_neighbors_geometry_changed=int(np.count_nonzero(
                (a[:5] != ar[:5]) | (age[:5] != ager[:5]))),
            first_five_upper_right_neighbors_Address=a[:5].tolist(),
            first_five_upper_right_neighbors_Age=age[:5].tolist(),
            first_protected_upper_cell_Address=int(a[p.Q]),
            first_protected_upper_cell_Age=int(age[p.Q]),
            first_protected_upper_cell_Flag1=int(candidate.field(noisy, 'f1')[p.Q])))
    first_crossing = next(row['period'] for row in recorded['checks']
                          if row['geometry_at_or_beyond_next_true_level2_boundary'])
    spoiled_before_crossing = [row for row in rows if row['period'] < first_crossing and (
        row['first_five_upper_right_neighbors_geometry_changed'] or
        any(row['protected_upper_colony_flag_counts'].values()) or
        row['protected_upper_colony_geometry_changed'])]
    assert spoiled_before_crossing
    result = dict(
        checker_sha256=digest(Path(__file__)), proposal='SP4',
        proposed_candidate_sha256=candidate.digest(), proposed_netlist_sha256=candidate.comp.digest,
        proposal_source_sha256=digest(Path(proposed.__file__)), active_G17_modified=False,
        physical_receipt_sha256=digest(physical), tracking_asset_sha256=digest(tracking),
        first_geometric_crossing_period=first_crossing, snapshot_reads=rows,
        barrier_premises_spoiled_before_crossing=True,
        earliest_retained_spoiled_snapshot=spoiled_before_crossing[0]['period'],
        J40_infinite_halfline_counterexample_established=False,
        universal_higher_island_repair_established=False,
        global_reliability_established=False,
        scope='finite periodic decoded-state diagnosis; wrap inputs and quiet-colony premises differ from J40')
    (out / 'level2_boundary_analysis.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    main()
