#!/usr/bin/env python3
"""Measured one-core repair-command probe for the explicit SP7 proposal.

The driven domain uses the explicitly changed asymmetric reference boundary.
Its interior is the unchanged isolated SP7 rule. The full upper colony is
encoded, but the top context is finite and not an infinite hierarchy. No
bounded-repair, iid unreliability or asymptotic speed theorem is inferred.
"""
import copy
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import numpy as np
from gacsca import codec, machine
import proposed_sparse_latched448 as proposed
from check_sparse_prefix448_physical import augmented
from check_coherent_phase_physical import replace_bits
import asymmetric_ghost_gpu as ghost


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    started = time.monotonic()
    out = ROOT / 'figs/robustness'
    candidate = proposed.load_artifact()
    p = candidate.p
    columns = p.Q
    cells = columns*p.Q
    top = np.zeros((candidate.W, 1), dtype=bool)
    upper = augmented(candidate, top)
    lower = augmented(candidate, upper)
    shifted = np.roll(lower, 1, axis=1)
    initial = np.stack([machine.CKernel.pack(state) for state in (lower, shifted, lower, lower)])
    cases = [dict(set_index=index, begin=index*p.Q+p.Q-31,
                  closest_right_point=index*p.Q+p.Q-30, tau=index*25*p.U)
             for index in range(1)]
    assert 25*p.U-38 >= 24*p.U
    events = {}
    for item in cases:
        for step in range(17):
            tick = item['tau']+(step if step < 16 else 38)
            offsets = list(range(16)) if step < 16 else [15]
            events.setdefault(tick, []).append(dict(set_index=item['set_index'], step=step,
                                                     sites=[item['begin']+offset for offset in offsets]))
    input_asset = out / 'SP7_latched_one_core_inputs.npz'
    np.savez_compressed(input_asset, top=top, upper=upper, initial_packed=initial,
                        cases=np.asarray([(item['begin'], item['tau']) for item in cases]))
    del lower, shifted, upper
    execution = copy.copy(candidate)
    execution.rom = np.pad(candidate.rom, ((0, (1 << p.k)-p.Q), (0, 0)))
    sim = ghost.sim(execution, 4, columns)
    sim.set_state(initial, t=0)
    del initial
    checks, snapshots, snapshot_ticks, overwrite_values, overwrite_ticks, overwrite_sites = [], [], [], [], [], []
    periods = 20
    snapshot_periods = {1, 2, 14, 15, 16, 17, 18, 19, 20}
    result = dict(
        proposal='SP7', proposed_rule_change=True, active_G17_modified=False,
        proposed_candidate_sha256=candidate.digest(), proposed_netlist_sha256=candidate.comp.digest,
        proposal_source_sha256=digest(Path(proposed.__file__)), driver_sha256=digest(Path(__file__)),
        asymmetric_ghost_helper_sha256=digest(Path(ghost.__file__)),
        SP6_comparison_receipt_sha256=digest(out / "SP6_relay_one_core_physical.json"),
        ghost_operator_receipt_sha256=digest(out / 'SP7_asymmetric_ghost_certificate.json'),
        augmented_helper_sha256=digest(ROOT / 'Report/proofs/check_sparse_prefix448_physical.py'),
        physical_helper_sha256=digest(ROOT / 'Report/proofs/check_coherent_phase_physical.py'),
        build_receipt_sha256=digest(out / 'SP7_program_build.json'), input_asset_sha256=digest(input_asset),
        kernel_sha256=sim.source_sha256, completed_rom_sha256=hashlib.sha256(execution.rom.tobytes()).hexdigest(),
        Q=p.Q, U=p.U, physical_cells=cells, upper_cells=columns, initial_upper_clock=0,
        requested_periods=periods, completed_periods=0, rings=4, cases=cases,
        periodic_reference_rings=[0, 1], boundary_only_control_ring=2, one_core_ring=3,
        left_reference_phase_shift=-1, real_level1_sets=1, points_per_set=257, total_overwrites=257,
        minimum_cross_set_tick_gap=25*p.U-38, real_level1_isolation_ticks=24*p.U,
        classification_proof='each16x16 kernel plus singleton at its right end/tick38 has every minimal linked candidate meeting the kernel; kernel points differ<16 in both coordinates; all cross-set tick gaps>=24U',
        continuing_E0=False, native_C_comparison=False,
        changed_boundary_condition=True, noisy_rings_are_periodic_CA_trajectories=False,
        initial_pristine_infinite_hierarchy=False, infinite_line_equivalence_established=False,
        universal_repeated_core_repair_established=False, independent_noise_unreliability_established=False,
        global_reliability_established=False, checks=checks,
        scope='finite full-upper-colony driven one-core SP7 probe; computed checkpoints before fresh errors, measured only')
    gf_rows = [candidate.row[field, bit] for field, width in (('addr', p.k), ('age', p.m))
               for bit in range(width)]
    flag_rows = [candidate.row[field, 0] for field in ('f1', 'f2', 'wf1', 'wf2')]
    checkpoints = {period*p.U for period in range(1, periods+1)}
    try:
        for tick in sorted(set(events) | checkpoints):
            sim.run(tick-sim.t)
            packed = sim.state()
            if tick in checkpoints:
                reference = machine.CKernel.unpack(packed[0], cells)
                expected_addr = np.arange(cells) % p.Q
                assert np.array_equal(candidate.field(reference, 'addr'), expected_addr)
                assert np.all(candidate.field(reference, 'age') == p.age_code(0))
                assert all(not candidate.field(reference, field).any() for field in ('f1', 'f2', 'wf1', 'wf2'))
                reference_upper = codec.decode(candidate, reference)
                row = dict(period=tick//p.U, tick=tick, rings=[])
                for ring in (2, 3):
                    raw = machine.CKernel.unpack(packed[ring], cells)
                    gf_bad = np.any(raw[gf_rows] != reference[gf_rows], axis=0)
                    flags_bad = np.any(raw[flag_rows] != reference[flag_rows], axis=0)
                    decoded = codec.decode(candidate, raw)
                    upper_gf_bad = np.any(decoded[gf_rows] != reference_upper[gf_rows], axis=0)
                    upper_flags_bad = np.any(decoded[flag_rows] != reference_upper[flag_rows], axis=0)
                    bad = np.flatnonzero(gf_bad)
                    row['rings'].append(dict(
                        ring=ring, geometry_sites=int(gf_bad.sum()),
                        geometry_min=int(bad[0]) if len(bad) else None,
                        geometry_max=int(bad[-1]) if len(bad) else None,
                        geometry_first_eight_colonies=[int(part.sum()) for part in np.split(gf_bad[:8*p.Q], 8)],
                        flags_first_eight_colonies=[int(part.sum()) for part in np.split(flags_bad[:8*p.Q], 8)],
                        upper_GF_changed_cells=np.flatnonzero(upper_gf_bad).tolist(),
                        upper_flags_changed_cells=np.flatnonzero(upper_flags_bad).tolist(),
                        upper_Address_first_sixteen=candidate.field(decoded, 'addr')[:16].tolist(),
                        upper_Age_first_sixteen=candidate.field(decoded, 'age')[:16].tolist(),
                        upper_Flag1_first_sixteen=candidate.field(decoded, 'f1')[:16].tolist()))
                checks.append(row)
                result['completed_periods'] = row['period']
                if row['period'] in snapshot_periods:
                    snapshots.append(packed[:, :, :8*(p.Q//64)].copy())
                    snapshot_ticks.append(tick)
                print(json.dumps(dict(period=row['period'], GF_first_eight=row['rings'][1]['geometry_first_eight_colonies'],
                                      control_GF=row['rings'][0]['geometry_sites'],
                                      upper_GF_changed=row['rings'][1]['upper_GF_changed_cells'],
                                      elapsed_seconds=round(time.monotonic()-started, 3))), flush=True)
            for event in events.get(tick, ()):
                sites = np.asarray(event['sites'], dtype=np.int64)
                shifted_reference = machine.CKernel.unpack(packed[1], cells)
                values = shifted_reference[:, sites].copy()
                for bit in range(candidate.W):
                    replace_bits(packed[3], bit, sites, values[bit])
                padded = np.zeros((candidate.W, 16), dtype=bool)
                padded[:, :len(sites)] = values
                overwrite_values.append(padded)
                overwrite_ticks.append(tick)
                padded_sites = np.full(16, -1, dtype=np.int64)
                padded_sites[:len(sites)] = sites
                overwrite_sites.append(padded_sites)
            if tick in events:
                sim.set_state(packed, t=tick)
        result['result'] = 'measured:20 computed period boundaries retained after one real core'
    finally:
        tracking_asset = out / 'SP7_latched_one_core_tracking.npz'
        np.savez_compressed(tracking_asset, snapshot_ticks=snapshot_ticks,
                            first_eight_colonies_packed=np.stack(snapshots) if snapshots else np.empty((0,)),
                            final_packed=sim.state(), overwrite_ticks=overwrite_ticks,
                            overwrite_sites=np.stack(overwrite_sites) if overwrite_sites else np.empty((0,)),
                            overwrite_values=np.stack(overwrite_values) if overwrite_values else np.empty((0,)))
        result.update(tracking_asset_sha256=digest(tracking_asset), elapsed_seconds=time.monotonic()-started,
                      recorded_overwrite_batches=len(overwrite_ticks))
        (out / 'SP7_latched_one_core_physical.json').write_text(json.dumps(result, indent=2)+'\n')
        print(json.dumps(dict(result=result.get('result', 'incomplete'), completed_periods=result['completed_periods'],
                              elapsed_seconds=result['elapsed_seconds'])), flush=True)


if __name__ == '__main__':
    main()
