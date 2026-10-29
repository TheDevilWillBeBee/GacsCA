#!/usr/bin/env python3
"""Finite J32 check of dense real-class forcing before evaluation.

This experiment uses E0 empty and two initial encodings. The proof of
the continuing-E0 and unbounded statements is separate.
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
from check_coherent_phase_physical import replace_bits


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    started = time.monotonic()
    out = ROOT / 'figs/robustness'
    candidate = proposed.load_artifact()
    p = candidate.p
    proof = json.loads((out / 'SP4_gather_repair_certificate.json').read_text())
    assert proof['latest_first_period_danger_tick'] == 10342
    # Exact class proof for this particular257-point set: each candidate
    # level1 subset contains a kernel point, since its complement has
    # only one point. All kernel points are mutually(16,16)-linked.
    # Thus no two candidate level1 subsets are(16,16)-separated. All
    # points are non-E0 (the tail is23-linked to kernel tick15), there
    # are disjoint linked candidate0 singletons, and isolation is vacuous.
    points = {(x, t) for x in range(16) for t in range(16)} | {(15, 38)}
    kernel = points-{(15, 38)}
    assert len(points) == 257 and len(kernel) == 256
    assert max(x for x, _ in kernel)-min(x for x, _ in kernel) < 16
    assert max(t for _, t in kernel)-min(t for _, t in kernel) < 16
    assert 38-15 < 24
    seed = 1084432
    rng = np.random.default_rng(seed)
    top = codec.random_upper(candidate, 1, rng)
    upper = augmented(candidate, top)
    lower = augmented(candidate, upper)
    execution = copy.copy(candidate)
    execution.rom = np.pad(candidate.rom, ((0, (1 << p.k)-p.Q), (0, 0)))
    clean1 = execution.step_numpy(upper)
    clean2 = execution.step_numpy(clean1)
    expected2 = machine.CKernel.pack(augmented(candidate, clean2))
    modes = ('random', 'one', 'unused', 'staggered')
    cases = [(tau, position, modes[index % 4]) for index, (tau, position) in enumerate(
        ( (0, 59), (0, 310), (4000, 59), (4000, 310),
          (9000, 59), (9000, 310), (10342, 59), (10342, 310) ))]
    base = machine.CKernel.pack(lower)
    states = np.broadcast_to(base, (len(cases)+1,)+base.shape).copy()
    replacements = rng.integers(0, 2, (len(cases), 17, candidate.W, 16), dtype=np.uint8)
    for index, (_, _, mode) in enumerate(cases):
        for step in range(17):
            replacement = replacements[index, step]
            if mode == 'one':
                replacement[:] = 1
            elif mode == 'unused':
                candidate.set_field(replacement, 'addr', 500)
                candidate.set_field(replacement, 'age', (1 << p.m)-1)
            elif mode == 'staggered':
                candidate.set_field(replacement, 'addr', 448+(step+np.arange(16)) % 64)
                candidate.set_field(replacement, 'age', np.where(np.arange(16) % 2,
                                    (1 << p.m)-1, p.age_code(p.T_wf)+step))
    asset = out / 'SP4_gather_period_inputs.npz'
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
                  proof_receipt_sha256=digest(out / 'SP4_gather_repair_certificate.json'),
                  build_receipt_sha256=digest(out / 'SP4_program_build.json'),
                  input_asset_sha256=digest(asset), kernel_sha256=sim.source_sha256,
                  completed_rom_sha256=hashlib.sha256(execution.rom.tobytes()).hexdigest(),
                  Q=p.Q, U=p.U, physical_cells=p.Q**2, cases=len(cases), seed=seed,
                  noise_classification=dict(level1=True, level0=0, points=len(points),
                                            method='exact kernel/tail candidate-pair argument in driver'),
                  overwrites_per_case=len(points), continuing_E0=False,
                  native_C_comparison=False, checks=[], global_reliability_established=False,
                  scope='finite J32 checks:16x16 forcing kernel plus original late singleton; E0 empty')
    events = {}
    for index, (tau, _, _) in enumerate(cases):
        for step in range(16):
            events.setdefault(tau+step, []).append((index, step, tuple(range(16))))
        events.setdefault(tau+38, []).append((index, 16, (15,)))
    try:
        for tick in sorted(events):
            sim.run(tick-sim.t)
            got = sim.state()
            for index, step, offsets in events[tick]:
                sites = p.Q**2//2+cases[index][1]+np.array(offsets)
                values = replacements[index, step][:, list(offsets)]
                for row in range(candidate.W):
                    replace_bits(got[index+1], row, sites, values[row])
            sim.set_state(got, t=tick)
        sim.run(p.U-sim.t)
        got = sim.state()
        decoded = []
        for index, (tau, position, mode) in enumerate(cases):
            z1 = codec.decode(candidate, machine.CKernel.unpack(got[index+1], p.Q**2))
            differing = np.any(z1 != clean1, axis=0)
            start = p.Q**2//2+position
            C = ((start+1+15)//p.Q+1)*p.Q
            allowed = list(range((start-208)//p.Q, min(start+1+69, C-1)//p.Q+1))
            outside = differing.copy()
            outside[allowed] = False
            assert len(allowed) <= 2 and not np.any(outside), (index, 'upper support')
            assert np.array_equal(execution.step_numpy(z1), clean2), (index, 'upper Age-one correction')
            boundary = machine.CKernel.pack(augmented(candidate, z1))
            assert np.array_equal(got[index+1], boundary), (index, 'complete boundary encoding')
            decoded.append(z1)
            result['checks'].append(dict(tau=tau, position=position, mode=mode,
                                         allowed_upper_cells=allowed,
                                         changed_upper_cells=np.flatnonzero(differing).tolist(),
                                         upper_next_equals_clean=True, full_boundary_is_encoding=True))
        assert np.array_equal(got[0], machine.CKernel.pack(augmented(candidate, clean1))), 'first clean twin'
        sim.run(p.U)
        got = sim.state()
        assert all(np.array_equal(ring, expected2) for ring in got), 'second full boundaries'
        data = out / 'SP4_gather_period_decoded.npz'
        np.savez_compressed(data, original_upper=upper, first_decodes=np.stack(decoded),
                            clean_first=clean1, clean_second=clean2)
        result.update(decoded_asset_sha256=digest(data), first_boundary_comparisons=len(cases)+1,
                      second_boundary_comparisons=len(cases)+1,
                      result='measured: all eight J32 cases localize to the upper pair and all second boundaries are exactly clean')
    except Exception:
        failure = out / 'SP4_gather_period_failure.npz'
        np.savez_compressed(failure, got=sim.state(), gpu_tick=sim.t, expected_second=expected2)
        result.update(result='failed finite gather-repair comparison', failure_asset_sha256=digest(failure))
        raise
    finally:
        result['elapsed_seconds'] = time.monotonic()-started
        (out / 'SP4_gather_period_physical.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({key: result[key] for key in ('result', 'elapsed_seconds')}), flush=True)


if __name__ == '__main__':
    main()
