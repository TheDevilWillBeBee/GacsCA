#!/usr/bin/env python3
"""Finite J34 full reset for the saved post-gather/command/commit cases.

Replays the exact forcing inputs of the separate geometry experiment,
with E0 empty. First boundaries need not be complete encodings.
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
    proof_path = out / 'SP4_period_repair_certificate.json'
    proof = json.loads(proof_path.read_text())
    assert proof['maximum_alignment_tick_into_second_period'] == 419
    parent_path = out / 'SP4_postgather_geometry_physical.json'
    parent = json.loads(parent_path.read_text())
    assert parent['proposed_candidate_sha256'] == candidate.digest()
    asset = out / 'SP4_postgather_geometry_inputs.npz'
    assert digest(asset) == parent['input_asset_sha256']
    with np.load(asset, allow_pickle=False) as saved:
        top = saved['top']
        base = saved['initial_packed_base']
        replacements = saved['replacements']
        cases = [(int(tau), int(pos), str(mode))
                 for (tau, pos), mode in zip(saved['cases'], saved['replacement_modes'])]
    assert len(cases) == 16
    execution = copy.copy(candidate)
    execution.rom = np.pad(candidate.rom, ((0, (1 << p.k)-p.Q), (0, 0)))
    upper = augmented(candidate, top)
    clean1 = execution.step_numpy(upper)
    clean2 = execution.step_numpy(clean1)
    expected2 = machine.CKernel.pack(augmented(candidate, clean2))
    sim = gpu.GpuSim(execution, len(cases)+1, p.Q, mode='grid')
    sim.set_state(np.broadcast_to(base, (len(cases)+1,)+base.shape).copy(), t=0)
    result = dict(proposal='SP4', proposed_rule_change=True, active_G17_modified=False,
                  proposed_candidate_sha256=candidate.digest(), proposed_netlist_sha256=candidate.comp.digest,
                  proposal_source_sha256=digest(Path(proposed.__file__)), driver_sha256=digest(Path(__file__)),
                  augmented_helper_sha256=digest(ROOT / 'Report/proofs/check_sparse_prefix448_physical.py'),
                  physical_helper_sha256=digest(ROOT / 'Report/proofs/check_coherent_phase_physical.py'),
                  proof_receipt_sha256=digest(proof_path), parent_geometry_receipt_sha256=digest(parent_path),
                  build_receipt_sha256=digest(out / 'SP4_program_build.json'),
                  input_asset_sha256=digest(asset), input_asset=str(asset.relative_to(ROOT)),
                  kernel_sha256=sim.source_sha256,
                  completed_rom_sha256=hashlib.sha256(execution.rom.tobytes()).hexdigest(),
                  Q=p.Q, U=p.U, physical_cells=p.Q**2, cases=len(cases),
                  noise_classification=parent['noise_classification'], overwrites_per_case=257,
                  continuing_E0=False, native_C_comparison=False,
                  first_boundary_checks=[], aligned_decode_checks=[], global_reliability_established=False,
                  scope='finite J34 post-gather first-decoder and full second-boundary checks; E0 empty')
    events, checkpoints = {}, {}
    for index, (tau, _, _) in enumerate(cases):
        for step in range(16):
            events.setdefault(tau+step, []).append((index, step, tuple(range(16))))
        events.setdefault(tau+38, []).append((index, 16, (15,)))
        checkpoints.setdefault(max(p.U, tau+420), []).append(index)
    first_decodes = [None]*len(cases)
    aligned_decodes = [None]*len(cases)

    def decode_check(packed, index):
        decoded = codec.decode(candidate, machine.CKernel.unpack(packed, p.Q**2))
        different = np.any(decoded != clean1, axis=0)
        start = p.Q**2//2+cases[index][1]
        C = ((start+16)//p.Q+1)*p.Q
        allowed = list(range((start-208)//p.Q, min(start+1+69, C-1)//p.Q+1))
        outside = different.copy()
        outside[allowed] = False
        assert len(allowed) <= 2 and not np.any(outside), (index, sim.t, 'upper pair support')
        return decoded, dict(case=index, tau=cases[index][0], position=cases[index][1], mode=cases[index][2],
                             tick=sim.t, allowed_upper_cells=allowed,
                             changed_upper_cells=np.flatnonzero(different).tolist())

    try:
        for tick in sorted(set(events) | set(checkpoints) | {p.U, 2*p.U}):
            sim.run(tick-sim.t)
            got = sim.state()
            for index, step, offsets in events.get(tick, ()):
                sites = p.Q**2//2+cases[index][1]+np.array(offsets)
                values = replacements[index, step][:, list(offsets)]
                for row in range(candidate.W):
                    replace_bits(got[index+1], row, sites, values[row])
            if tick in events:
                sim.set_state(got, t=tick)
            if tick == p.U:
                for index in range(len(cases)):
                    decoded, check = decode_check(got[index+1], index)
                    encoded = machine.CKernel.pack(augmented(candidate, decoded))
                    check['full_boundary_is_encoding'] = bool(np.array_equal(got[index+1], encoded))
                    first_decodes[index] = decoded
                    result['first_boundary_checks'].append(check)
                assert np.array_equal(got[0], machine.CKernel.pack(augmented(candidate, clean1))), 'first clean twin'
            for index in checkpoints.get(tick, ()):
                decoded, check = decode_check(got[index+1], index)
                assert np.array_equal(execution.step_numpy(decoded), clean2), (index, 'upper Age-one correction')
                aligned_decodes[index] = decoded
                check['upper_next_equals_clean'] = True
                result['aligned_decode_checks'].append(check)
            if tick == 2*p.U:
                assert all(np.array_equal(ring, expected2) for ring in got), 'full second boundaries'
        data = out / 'SP4_postgather_period_decoded.npz'
        np.savez_compressed(data, original_upper=upper, first_decodes=np.stack(first_decodes),
                            aligned_decodes=np.stack(aligned_decodes), clean_first=clean1, clean_second=clean2)
        result.update(decoded_asset_sha256=digest(data), second_boundary_comparisons=len(cases)+1,
                      incomplete_first_encodings=sum(not c['full_boundary_is_encoding'] for c in result['first_boundary_checks']),
                      result='measured: all sixteen late-core decoders stay in the upper pair and all full second boundaries are exactly clean')
    except Exception:
        failure = out / 'SP4_postgather_period_failure.npz'
        np.savez_compressed(failure, got=sim.state(), gpu_tick=sim.t, expected_second=expected2)
        result.update(result='failed finite post-gather period comparison', failure_asset_sha256=digest(failure))
        raise
    finally:
        result['elapsed_seconds'] = time.monotonic()-started
        (out / 'SP4_postgather_period_physical.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({key: result[key] for key in ('result', 'elapsed_seconds', 'incomplete_first_encodings')}), flush=True)


if __name__ == '__main__':
    main()
