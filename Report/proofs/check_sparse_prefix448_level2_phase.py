#!/usr/bin/env python3
"""Finite SP4 coherent phase islands with an exact real-level2 forcing set.

A dense16Q-by1 initial set, no E0, four placements/phases. This is a
mechanism experiment, not a higher-island induction or iid threshold.
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
    seed = 1084462
    rng = np.random.default_rng(seed)
    top = codec.random_upper(candidate, 1, rng)
    lower = augmented(candidate, augmented(candidate, top))
    cases = [(1, 1), (1, 97), (p.Q**2//2+1, 1), (p.Q**2//2+1, 97)]
    width = 16*p.Q
    assert width < p.Q**2 and width-1 < 16*p.Q
    # A connected dense interval has neither isolated E0 groups nor an
    # isolated candidate level1 subset (such a subset fits in a Q-box).
    # The entire set is a candidate2 and its diameter is <16Q, so (iii)
    # holds. Isolation from any other higher error is vacuous.
    states, replacements = [], []
    for begin, shift in cases:
        replacement = lower[:, (np.arange(begin, begin+width)-shift) % lower.shape[1]].copy()
        modified = lower.copy()
        modified[:, begin:begin+width] = replacement
        states.append(machine.CKernel.pack(modified))
        replacements.append(replacement)
    states.append(machine.CKernel.pack(lower))
    asset = out / 'SP4_level2_phase_inputs.npz'
    np.savez_compressed(asset, seed=seed, top=top, initial_packed_base=states[-1],
                        cases=np.array(cases, dtype=np.int32), width=width,
                        replacements=np.stack(replacements))
    del lower
    execution = copy.copy(candidate)
    execution.rom = np.pad(candidate.rom, ((0, (1 << p.k)-p.Q), (0, 0)))
    sim = gpu.GpuSim(execution, len(states), p.Q, mode='grid')
    sim.set_state(np.stack(states), t=0)
    del states
    checks = []
    periods = 32
    result = dict(
        proposal='SP4', proposed_rule_change=True, active_G17_modified=False,
        proposed_candidate_sha256=candidate.digest(), proposed_netlist_sha256=candidate.comp.digest,
        proposal_source_sha256=digest(Path(proposed.__file__)), driver_sha256=digest(Path(__file__)),
        augmented_helper_sha256=digest(ROOT / 'Report/proofs/check_sparse_prefix448_physical.py'),
        build_receipt_sha256=digest(out / 'SP4_program_build.json'),
        input_asset_sha256=digest(asset), kernel_sha256=sim.source_sha256,
        completed_rom_sha256=hashlib.sha256(execution.rom.tobytes()).hexdigest(),
        Q=p.Q, U=p.U, physical_cells=p.Q**2, cases=len(cases), seed=seed,
        noise_classification=dict(level=2, level0=0, level1=0, points=width,
                                  method='connected dense interval, no isolated lower candidate; full diameter strictly less than16Q'),
        overwrite_tick=0, overwrite_interval_width=width, continuing_E0=False,
        requested_periods=periods, native_C_comparison=False, checks=checks,
        global_reliability_established=False,
        scope='finite two-encoding coherent phase level2 mechanism checks; no universal higher-island or iid result')
    snapshots, snapshot_periods = [], []
    try:
        for period in range(1, periods+1):
            sim.run(p.U)
            got = sim.state()
            for index, (begin, shift) in enumerate(cases):
                raw = machine.CKernel.unpack(got[index], p.Q**2)
                address = candidate.field(raw, 'addr')
                age = candidate.field(raw, 'age')
                bad = np.flatnonzero((address != np.arange(p.Q**2) % p.Q) |
                                      (age != p.age_code(0)))
                full_difference = int(np.count_nonzero(got[index] ^ got[-1]))
                decoded = codec.decode(candidate, raw)
                reference_raw = machine.CKernel.unpack(got[-1], p.Q**2)
                clean_decoded = codec.decode(candidate, reference_raw)
                decoded_bad = np.flatnonzero(np.any(decoded != clean_decoded, axis=0))
                check = dict(case=index, begin=begin, phase_shift=shift,
                             period=period, tick=sim.t, bad_geometry_sites=len(bad),
                             geometry_min=int(bad.min()) if len(bad) else None,
                             geometry_max=int(bad.max()) if len(bad) else None,
                             Flag1_sites=int(np.count_nonzero(candidate.field(raw, 'f1'))),
                             Flag2_sites=int(np.count_nonzero(candidate.field(raw, 'f2'))),
                             upper_decoder_changed_sites=decoded_bad.tolist(),
                             whole_state_differing_packed_words=full_difference)
                checks.append(check)
            if period in (1, 2, 4, 8, 16, periods):
                snapshots.append(got.copy())
                snapshot_periods.append(period)
            print(json.dumps(dict(period=period, tick=sim.t,
                                  geometry_counts=[c['bad_geometry_sites'] for c in checks[-len(cases):]],
                                  decoded_counts=[len(c['upper_decoder_changed_sites']) for c in checks[-len(cases):]],
                                  exact_full_states=[c['whole_state_differing_packed_words'] == 0 for c in checks[-len(cases):]])), flush=True)
        tracking = out / 'SP4_level2_phase_tracking.npz'
        np.savez_compressed(tracking, periods=np.array(snapshot_periods), states=np.stack(snapshots))
        result.update(tracking_asset_sha256=digest(tracking), completed_periods=periods,
                      result='measured: thirty-two period checkpoints of four dense real-level2 coherent phase seeds')
    finally:
        result['elapsed_seconds'] = time.monotonic()-started
        (out / 'SP4_level2_phase_physical.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(dict(result=result['result'], elapsed_seconds=result['elapsed_seconds'])), flush=True)


if __name__ == '__main__':
    main()
