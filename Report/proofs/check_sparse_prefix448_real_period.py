#!/usr/bin/env python3
"""Finite J31 check: one real level-1 forcing set in the first period.

Dense three-site overwrites at16 ticks plus the permitted late singleton
are checked at first-danger ticks0/3559. E0 is empty in this experiment.
The general E0 interaction is proved separately, not sampled here.
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
from gacsca import codec, gpu, gray_errors, machine
import proposed_sparse_prefix448 as proposed
from check_sparse_prefix448_physical import augmented
from check_coherent_phase_physical import replace_bits


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    started = time.monotonic()
    out = ROOT / 'figs/robustness'
    candidate = proposed.load_artifact()
    p = candidate.p
    proof = json.loads((out / 'SP4_barrier_certificate.json').read_text())
    assert proof['latest_first_period_danger_tick_for_two_later_gathers'] == 3559
    points = {(x, t) for x in range(3) for t in range(16)} | {(2, 38)}
    classification = gray_errors.classify(points, Q=p.Q, U=p.U, sep=16)
    assert classification['level1'] and classification['level0'] == 0
    seed = 1084404
    rng = np.random.default_rng(seed)
    top = codec.random_upper(candidate, 1, rng)
    upper = augmented(candidate, top)
    lower = augmented(candidate, upper)
    execution = copy.copy(candidate)
    execution.rom = np.pad(candidate.rom, ((0, (1 << p.k)-p.Q), (0, 0)))
    expected_upper = execution.step_numpy(upper)
    expected = machine.CKernel.pack(augmented(candidate, expected_upper))
    modes = ('random', 'one', 'unused', 'staggered')
    cases = [(tau, position, modes[index]) for tau in (0, 3559)
             for index, position in enumerate((0, 1, 320, 447))]
    base = machine.CKernel.pack(lower)
    states = np.broadcast_to(base, (len(cases)+1,)+base.shape).copy()
    replacements = rng.integers(0, 2, (len(cases), 17, candidate.W, 3), dtype=np.uint8)
    for index, (_, _, mode) in enumerate(cases):
        for step in range(17):
            replacement = replacements[index, step]
            if mode == 'one':
                replacement[:] = 1
            elif mode == 'unused':
                candidate.set_field(replacement, 'addr', 500)
                candidate.set_field(replacement, 'age', (1 << p.m)-1)
            elif mode == 'staggered':
                candidate.set_field(replacement, 'addr', 448+(step+np.arange(3)) % 64)
                candidate.set_field(replacement, 'age', np.where(np.arange(3) % 2,
                                    (1 << p.m)-1, p.age_code(p.T_wf)+step))
    asset = out / 'SP4_real_period_inputs.npz'
    np.savez_compressed(asset, seed=seed, top=top, initial_packed_base=base,
                        cases=np.array([(tau, pos) for tau, pos, _ in cases], dtype=np.int32),
                        replacement_modes=np.array([mode for _, _, mode in cases]),
                        relative_error_points=np.array(sorted(points), dtype=np.int32), replacements=replacements)
    sim = gpu.GpuSim(execution, len(cases)+1, p.Q, mode='grid')
    sim.set_state(states, t=0)
    del states, lower
    result = dict(proposal='SP4', proposed_rule_change=True, active_G17_modified=False,
                  proposed_candidate_sha256=candidate.digest(), proposed_netlist_sha256=candidate.comp.digest,
                  proposal_source_sha256=digest(Path(proposed.__file__)), driver_sha256=digest(Path(__file__)),
                  augmented_helper_sha256=digest(ROOT / 'Report/proofs/check_sparse_prefix448_physical.py'),
                  physical_helper_sha256=digest(ROOT / 'Report/proofs/check_coherent_phase_physical.py'),
                  classifier_sha256=digest(ROOT / 'gacsca/gray_errors.py'),
                  proof_receipt_sha256=digest(out / 'SP4_barrier_certificate.json'),
                  build_receipt_sha256=digest(out / 'SP4_program_build.json'),
                  input_asset_sha256=digest(asset), kernel_sha256=sim.source_sha256,
                  completed_rom_sha256=hashlib.sha256(execution.rom.tobytes()).hexdigest(),
                  Q=p.Q, U=p.U, physical_cells=p.Q**2, cases=len(cases), seed=seed,
                  noise_classification=classification, overwrites_per_case=len(points),
                  continuing_E0=False, native_C_comparison=False, checks=[],
                  global_reliability_established=False,
                  scope='finite first-period J31 real-class checks,16 forcing ticks and late original singleton; E0 empty')
    events = {}
    for index, (tau, _, _) in enumerate(cases):
        for step in range(16):
            events.setdefault(tau+step, []).append((index, step, (0, 1, 2)))
        events.setdefault(tau+38, []).append((index, 16, (2,)))
    checkpoints = {tau+proof['raw_repair_updates_after_first_danger']: tau for tau in (0, 3559)}
    all_times = sorted(set(events) | set(checkpoints))
    repaired_upper = [None]*len(cases)
    try:
        for tick in all_times:
            assert tick >= sim.t
            sim.run(tick-sim.t)
            if tick in checkpoints:
                got = sim.state()
                for index, (tau, position, mode) in enumerate(cases):
                    if tau != checkpoints[tick]:
                        continue
                    repaired = codec.decode(candidate, machine.CKernel.unpack(got[index+1], p.Q**2))
                    differing = np.any(repaired != upper, axis=0)
                    start = p.Q**2//2+position
                    C = ((start+1+15)//p.Q+1)*p.Q
                    allowed = list(range((start-208)//p.Q, min(start+1+69, C-1)//p.Q+1))
                    assert len(allowed) <= 2
                    outside = differing.copy()
                    outside[allowed] = False
                    assert not np.any(outside), (index, 'upper support')
                    assert np.array_equal(execution.step_numpy(repaired), expected_upper), (index, 'upper update')
                    repaired_upper[index] = repaired
                    result['checks'].append(dict(tau=tau, position=position, mode=mode,
                                                 checkpoint=tick, allowed_upper_cells=allowed,
                                                 changed_upper_cells=np.flatnonzero(differing).tolist(),
                                                 upper_next_equals_clean=True))
            if tick in events:
                got = sim.state()
                for index, step, offsets in events[tick]:
                    sites = p.Q**2//2+cases[index][1]+np.array(offsets)
                    values = replacements[index, step][:, list(offsets)]
                    for row in range(candidate.W):
                        replace_bits(got[index+1], row, sites, values[row])
                sim.set_state(got, t=tick)
        sim.run(p.U-sim.t)
        got = sim.state()
        for ring in range(len(cases)+1):
            assert np.array_equal(got[ring], expected), (ring, 'full boundary')
        data = out / 'SP4_real_period_decoded.npz'
        np.savez_compressed(data, original_upper=upper, repaired_upper=np.stack(repaired_upper),
                            expected_upper=expected_upper)
        result.update(decoded_asset_sha256=digest(data), full_boundary_comparisons=len(cases)+1,
                      result='measured: all eight real-class forcing cases and clean twin exactly recover the full first-period boundary')
    except Exception:
        failure = out / 'SP4_real_period_failure.npz'
        np.savez_compressed(failure, got=sim.state(), gpu_tick=sim.t, expected=expected)
        result.update(result='failed finite real-class period comparison', failure_asset_sha256=digest(failure))
        raise
    finally:
        result['elapsed_seconds'] = time.monotonic()-started
        (out / 'SP4_real_period_physical.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({key: result[key] for key in ('result', 'elapsed_seconds')}), flush=True)


if __name__ == '__main__':
    main()
