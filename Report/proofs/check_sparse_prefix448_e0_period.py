#!/usr/bin/env python3
"""Finite support for SP4 SP4 initial-burst corollary: arbitrary initial burst plus continuing E0.

This checks one period with lattice E0, not iid-noise reliability.
Uses NumPy/CUDA and static pack/unpack helpers; no native C backend.
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
    proof = json.loads((out / 'SP4_maintenance_certificate.json').read_text())
    bound = proof['mixed_E0_bounds'][1]
    assert bound['Q'] == p.Q and bound['seed_width'] == 160 and bound['closes']
    seed = 1084304
    rng = np.random.default_rng(seed)
    top = codec.random_upper(candidate, 1, rng)
    upper = augmented(candidate, top)
    lower = augmented(candidate, upper)
    execution = copy.copy(candidate)
    execution.rom = np.pad(candidate.rom, ((0, (1 << p.k)-p.Q), (0, 0)))
    expected_upper = execution.step_numpy(upper)
    expected = machine.CKernel.pack(augmented(candidate, expected_upper))
    cases = [(141, 0, 'random'), (141, 1, 'one'),
             (141, 320, 'zero'), (141, 447, 'invert'),
             (160, 0, 'unused'), (160, 1, 'staggered'),
             (160, 320, 'random'), (160, 447, 'one')]
    base = machine.CKernel.pack(lower)
    states = np.broadcast_to(base, (len(cases)+1,)+base.shape).copy()
    replacements = np.zeros((len(cases), candidate.W, 160), dtype=np.uint8)
    for i, (width, position, mode) in enumerate(cases):
        sites = p.Q**2//2+position+np.arange(width)
        replacement = rng.integers(0, 2, (candidate.W, width), dtype=np.uint8)
        if mode == 'invert':
            replacement = lower[:, sites] ^ 1
        elif mode in ('zero', 'one'):
            replacement[:] = int(mode == 'one')
        elif mode == 'unused':
            candidate.set_field(replacement, 'addr', 500)
            candidate.set_field(replacement, 'age', (1 << p.m)-1)
        elif mode == 'staggered':
            candidate.set_field(replacement, 'addr', 448+np.arange(width) % 64)
            candidate.set_field(replacement, 'age', np.where(np.arange(width) % 2,
                                (1 << p.m)-1, p.age_code(p.T_wf)+np.arange(width) % 128))
        replacements[i, :, :width] = replacement
        for row in range(candidate.W):
            replace_bits(states[i+1], row, sites, replacement[row])
    asset = out / 'SP4_E0_period_inputs.npz'
    np.savez_compressed(asset, seed=seed, top=top, initial_packed_base=base,
                        cases=np.asarray([(w, pos) for w, pos, _ in cases], dtype=np.int32),
                        replacement_modes=np.asarray([mode for _, _, mode in cases]),
                        replacements=replacements)
    geometry_bound = bound['raw_geometry_repair_bound']
    result = dict(proposal='SP4', proposed_rule_change=True, active_G17_modified=False,
                  proposed_candidate_sha256=candidate.digest(), proposed_netlist_sha256=candidate.comp.digest,
                  proposal_source_sha256=digest(Path(proposed.__file__)),
                  selection_source_sha256=digest(ROOT / 'Report/proofs/prefix_selection.py'),
                  driver_sha256=digest(Path(__file__)),
                  augmented_helper_sha256=digest(ROOT / 'Report/proofs/check_sparse_prefix448_physical.py'),
                  physical_helper_sha256=digest(ROOT / 'Report/proofs/check_coherent_phase_physical.py'),
                  proof_receipt_sha256=digest(out / 'SP4_maintenance_certificate.json'),
                  build_receipt_sha256=digest(out / 'SP4_program_build.json'),
                  input_asset_sha256=digest(asset), seed=seed, Q=p.Q, U=p.U,
                  physical_cells=p.Q**2, cases=len(cases), geometry_bound=geometry_bound,
                  continuing_noise=True, E0_grid=26, E0_pair_integer_threshold=65536, native_C_comparison=False,
                  completion='execution-only zero padding of unused ROM rows',
                  global_reliability_established=False, checks=[],
                  scope='finite SP4 initial-burst corollary first-period recovery; arbitrary width141/160 initial seed with two encodings and continuing lattice E0')
    sim = gpu.GpuSim(execution, len(cases)+1, p.Q, mode='grid')
    initial_tick = (1-p.U) % 26
    cfgs = [gpu.noise()]
    for index in range(len(cases)):
        cfg = gpu.noise(seed=seed+index, e0_grid=26, e0_pair=1,
                        mode=('random', 'one', 'invert', 'copy')[index % 4],
                        shift_sites=p.Q if index % 4 == 3 else 0)
        cfg.e0_pair16 = 65536
        cfgs.append(cfg)
    sim.set_state(states, t=initial_tick)
    sim.set_noise(cfgs)
    result['initial_gpu_tick'] = initial_tick
    del states, lower, replacements
    result['kernel_sha256'] = sim.source_sha256
    result['completed_rom_sha256'] = hashlib.sha256(execution.rom.tobytes()).hexdigest()
    try:
        sim.run(geometry_bound)
        got = sim.state()
        repaired_upper = []
        for ring, (width, position, mode) in enumerate(cases, start=1):
            repaired = codec.decode(candidate, machine.CKernel.unpack(got[ring], p.Q**2))
            differing = np.any(repaired != upper, axis=0)
            start = p.Q**2//2+position
            left_padding = bound['maximum_left_phase_expansion']
            allowed = list(range((start-left_padding)//p.Q, (start+width-1)//p.Q+1))
            assert len(allowed) <= 2
            outside = differing.copy()
            outside[allowed] = False
            assert not np.any(outside), 'upper support escapes the proved two colonies'
            assert np.array_equal(execution.step_numpy(repaired), expected_upper), 'upper pair failed to correct'
            repaired_upper.append(repaired)
            result['checks'].append(dict(width=width, position=position, mode=mode,
                                         changed_upper_cells=np.flatnonzero(differing).tolist(),
                                         allowed_upper_cells=allowed, upper_next_equals_clean=True))
        del got
        sim.run(p.U-geometry_bound)
        got = sim.state()
        for ring in range(len(cases)+1):
            current = sim.error_masks(cfgs[ring], ring, sim.t-1, 1)[0]
            error_words = np.packbits(current, bitorder='little').view(np.uint64)
            indirect = (got[ring] ^ expected) & ~error_words[None, :]
            assert not np.any(indirect), (ring, 'boundary differs outside current overwrites')
            decoded = codec.decode(candidate, machine.CKernel.unpack(got[ring], p.Q**2))
            assert np.array_equal(decoded, expected_upper), (ring, 'boundary decode differs')
            if ring:
                result['checks'][ring-1].update(E0_mode=('random', 'one', 'invert', 'copy')[(ring-1) % 4],
                    current_boundary_overwrite_sites=int(current.sum()),
                    whole_boundary_correct_outside_current_errors=True, boundary_decode_correct=True)
        data = out / 'SP4_E0_period_decoded.npz'
        np.savez_compressed(data, original_upper=upper, repaired_upper=np.stack(repaired_upper),
                            expected_upper=expected_upper)
        result.update(decoded_asset_sha256=digest(data), full_boundary_comparisons=len(cases)+1,
                      result='measured: all eight arbitrary seeds with continuing E0 recover the first-period boundary outside current errors; all decoded boundaries clean')
    except Exception:
        failure = out / 'SP4_E0_period_failure.npz'
        np.savez_compressed(failure, got=sim.state(), gpu_tick=sim.t, expected=expected)
        result.update(result='failed finite mixed-E0 period-recovery comparison', failure_asset_sha256=digest(failure))
        raise
    finally:
        result['elapsed_seconds'] = time.monotonic()-started
        (out / 'SP4_E0_period_physical.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({key: result[key] for key in ('result', 'elapsed_seconds')}), flush=True)


if __name__ == '__main__':
    main()
