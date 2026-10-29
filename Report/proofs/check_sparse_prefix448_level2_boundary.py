#!/usr/bin/env python3
"""Finite coherent level2 island approaching a fresh true higher boundary.

The top two cells are a static pristine fragment (Addresses0/1), rather
than a random top word. The periodic top fragment is not an infinite
hierarchy; no infinite isolated-error or reliability claim is made.
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
from gacsca import codec, gpu, machine
import proposed_sparse_prefix448 as proposed
from check_sparse_prefix448_physical import augmented


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    started = time.monotonic()
    out = ROOT / 'figs/robustness'
    candidate = proposed.load_artifact()
    p = candidate.p
    top = np.zeros((candidate.W, 2), dtype=bool)
    candidate.set_field(top, 'addr', np.arange(2))
    # These are the first two raw cells of an augmented encoding of any
    # zero-flag static higher cell: no represented primary is this close
    # to the boundary, and signal/auxiliary primaries are zero there.
    lower = augmented(candidate, augmented(candidate, top))
    width, begin, shift = 16*p.Q, 1, 1
    cells = lower.shape[1]
    assert cells == 2*p.Q**2 and width-1 < 16*p.Q
    replacement = lower[:, (np.arange(begin, begin+width)-shift) % cells].copy()
    modified = lower.copy()
    modified[:, begin:begin+width] = replacement
    states = np.stack([machine.CKernel.pack(modified), machine.CKernel.pack(lower)])
    asset = out / 'SP4_level2_boundary_inputs.npz'
    np.savez_compressed(asset, top=top, initial_packed=states, begin=begin,
                        width=width, shift=shift, replacements=replacement)
    del lower, modified, replacement
    execution = copy.copy(candidate)
    execution.rom = np.pad(candidate.rom, ((0, (1 << p.k)-p.Q), (0, 0)))
    sim = gpu.GpuSim(execution, 2, 2*p.Q, mode='grid')
    sim.set_state(states, t=0)
    del states
    checks, snapshots, snapshot_periods = [], [], []
    periods = 160
    snapshot_targets = (1, 8, 32, 128, 140, 144, 145, 146, 148, 152, 160)
    result = dict(
        proposal='SP4', proposed_rule_change=True, active_G17_modified=False,
        proposed_candidate_sha256=candidate.digest(), proposed_netlist_sha256=candidate.comp.digest,
        proposal_source_sha256=digest(Path(proposed.__file__)), driver_sha256=digest(Path(__file__)),
        augmented_helper_sha256=digest(ROOT / 'Report/proofs/check_sparse_prefix448_physical.py'),
        build_receipt_sha256=digest(out / 'SP4_program_build.json'),
        input_asset_sha256=digest(asset), kernel_sha256=sim.source_sha256,
        completed_rom_sha256=hashlib.sha256(execution.rom.tobytes()).hexdigest(),
        Q=p.Q, U=p.U, physical_cells=cells, cases=1, requested_periods=periods,
        top_fragment_addresses=[0, 1], top_fragment_other_fields_zero=True,
        initial_static_infinite_hierarchy=False, periodic_copies_satisfy_level2_isolation=False,
        next_true_level2_boundary=p.Q**2,
        noise_classification=dict(level=2, level0=0, level1=0, points=width,
                                  scope='one finite forcing set in the fundamental ring domain',
                                  method='connected dense interval, full diameter strictly below16Q'),
        overwrite_tick=0, overwrite_interval_width=width, continuing_E0=False,
        native_C_comparison=False, checks=checks,
        universal_higher_island_repair_established=False,
        global_reliability_established=False,
        scope='finite two-top-cell higher-boundary mechanism run; no isolated infinite-Z, all-stage or iid theorem')
    try:
        for period in range(1, periods+1):
            sim.run(p.U)
            got = sim.state()
            raw = machine.CKernel.unpack(got[0], cells)
            reference = machine.CKernel.unpack(got[1], cells)
            address, age = candidate.field(raw, 'addr'), candidate.field(raw, 'age')
            expected_address = np.arange(cells) % p.Q
            assert np.array_equal(candidate.field(reference, 'addr'), expected_address)
            assert np.all(candidate.field(reference, 'age') == p.age_code(0))
            assert all(not np.any(candidate.field(reference, field)) for field in ('f1', 'f2', 'wf1', 'wf2'))
            bad = np.flatnonzero((address != expected_address) | (age != p.age_code(0)))
            decoded, clean_decoded = codec.decode(candidate, raw), codec.decode(candidate, reference)
            decoded_bad = np.flatnonzero(np.any(decoded != clean_decoded, axis=0))
            check = dict(
                period=period, tick=sim.t, bad_geometry_sites=len(bad),
                geometry_min=int(bad.min()) if len(bad) else None,
                geometry_max=int(bad.max()) if len(bad) else None,
                geometry_at_or_beyond_next_true_level2_boundary=int(np.count_nonzero(bad >= p.Q**2)),
                Flag1_sites=int(np.count_nonzero(candidate.field(raw, 'f1'))),
                Flag2_sites=int(np.count_nonzero(candidate.field(raw, 'f2'))),
                upper_decoder_changed_sites=decoded_bad.tolist(),
                upper_geometry_changed_sites=np.flatnonzero(
                    (candidate.field(decoded, 'addr') != candidate.field(clean_decoded, 'addr')) |
                    (candidate.field(decoded, 'age') != candidate.field(clean_decoded, 'age'))).tolist(),
                whole_state_differing_packed_words=int(np.count_nonzero(got[0] ^ got[1])))
            checks.append(check)
            if period in snapshot_targets:
                snapshots.append(got.copy())
                snapshot_periods.append(period)
            if period % 8 == 0 or period in snapshot_targets:
                print(json.dumps(dict(period=period, geometry_sites=len(bad),
                                      geometry_min=check['geometry_min'], geometry_max=check['geometry_max'],
                                      beyond_higher_boundary=check['geometry_at_or_beyond_next_true_level2_boundary'],
                                      decoder_changed_sites=len(decoded_bad),
                                      full_exact=check['whole_state_differing_packed_words'] == 0)), flush=True)
        tracking = out / 'SP4_level2_boundary_tracking.npz'
        np.savez_compressed(tracking, periods=np.array(snapshot_periods), states=np.stack(snapshots))
        result.update(tracking_asset_sha256=digest(tracking), completed_periods=periods,
                      result='measured: 160 boundary checkpoints approaching the first fresh true level2 boundary')
    finally:
        result['elapsed_seconds'] = time.monotonic()-started
        (out / 'SP4_level2_boundary_physical.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(dict(result=result['result'], elapsed_seconds=result['elapsed_seconds'])), flush=True)


if __name__ == '__main__':
    main()
