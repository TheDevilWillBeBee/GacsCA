#!/usr/bin/env python3
"""Exact coordinate/deadline checks for SP4's one-core upper map.

The map's dynamical validity is proved for one real set on a pristine
orbit in ROBUSTNESS J36. Packing prospective maps for many sets does not
prove their simultaneous dynamical validity or an iid threshold.
"""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import proposed_sparse_prefix448 as proposed


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    candidate = proposed.load_artifact()
    p = candidate.p
    out = ROOT / 'figs/robustness'
    positions = 0
    for left in range(p.Q):
        for gap in range(1, 6):
            right = left+gap
            C = ((right+15)//p.Q+1)*p.Q
            anchor = C//p.Q-2
            assert C-2*p.Q <= left-208
            assert min(right+69, C-1) < C
            assert anchor == (right+15)//p.Q-1
            assert right//p.Q-1 <= anchor <= right//p.Q
            positions += 1
    # Integer-floor packing at the smallest permitted spatial separation.
    # A larger separation only increases the difference of anchors.
    spatial = 0
    for a in range(p.Q):
        for b in range(p.Q):
            first = a
            second = b+(24+(b < a))*p.Q
            assert second-first >= 24*p.Q
            ja, jb = (first+15)//p.Q-1, (second+15)//p.Q-1
            assert jb-ja >= 24
            assert jb-(ja+1) >= 23
            spatial += 1
    temporal = 0
    for tau in range(p.U):
        repair = max(p.U, tau+420)
        relative = repair-p.U
        assert 0 <= relative <= 419
        assert tau+61 < repair
        assert relative+500 <= 919 < 4480
        assert tau//p.U+1 == 1
        # At temporal distance24U, the output-time map differs by24.
        assert (tau+24*p.U)//p.U+1 == tau//p.U+1+24
        temporal += 1
    receipt = dict(
        proposal='SP4', proposed_rule_change=True, active_G17_modified=False,
        proposed_candidate_sha256=candidate.digest(), proposed_netlist_sha256=candidate.comp.digest,
        proposal_source_sha256=digest(Path(proposed.__file__)), checker_sha256=digest(Path(__file__)),
        barrier_receipt_sha256=digest(out / 'SP4_barrier_certificate.json'),
        operational_receipt_sha256=digest(out / 'SP4_operational_certificate.json'),
        period_repair_receipt_sha256=digest(out / 'SP4_period_repair_certificate.json'),
        Q=p.Q, U=p.U, closest_pair_positions_checked=positions,
        spatial_residue_pairs_checked=spatial, core_tick_deadlines_checked=temporal,
        fixed_upper_pair_anchor='floor((q+15)/Q)-1',
        upper_input_error_tick='floor(tau/U)+1',
        decoder_convention='computed boundary before fresh noise: Y_t=F_4(X_(t-1))',
        pair_width_upper_cells=2, upper_error_duration_ticks=1,
        prospective_distinct_pair_anchor_separation=24,
        prospective_upper_error_point_spatial_separation=23,
        prospective_upper_error_tick_temporal_separation=24,
        correction_at_any_pristine_upper_clock=True,
        single_real_set_map_established='proof in ROBUSTNESS J36',
        raw_boundary_exact_one_tick_map_established=False,
        simultaneous_multiple_real_set_map_established=False,
        prospective_map_is_original_lambda24_E0=False,
        global_reliability_established=False,
        scope='one-core coordinate/deadline arithmetic and conditional prospective-map packing; no simultaneous-map or higher-island theorem')
    (out / 'SP4_upper_map_certificate.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(dict(position_cases=positions, spatial_residue_pairs=spatial,
                          core_tick_deadlines=temporal,
                          prospective_separation=[23, 24], multiple_map_established=False)), flush=True)


if __name__ == '__main__':
    main()
