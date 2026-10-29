#!/usr/bin/env python3
"""Finite NumPy/CUDA checks of the explicit driven ghost input operator."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import numpy as np
from gacsca import gpu, machine
import proposed_sparse_prefix448 as proposed
import reference_ghost_gpu as ghost


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    started = time.monotonic()
    candidate = proposed.load_artifact()
    execution = copy.copy(candidate)
    p = candidate.p
    execution.rom = np.pad(candidate.rom, ((0, (1 << p.k)-p.Q), (0, 0)))
    rng = np.random.default_rng(1084464)
    states = rng.random((5, candidate.W, p.Q)) < 0.5
    states[2] = False
    states[3] = True
    states[4] = np.roll(states[0], 13, axis=1)
    sim = ghost.sim(execution, len(states), 1)
    assert sim.mode == 'grid'
    sim.set_state(np.stack([machine.CKernel.pack(state) for state in states]))
    out = ROOT / 'figs/robustness'
    inputs = out / 'reference_ghost_inputs.npz'
    np.savez_compressed(inputs, initial=states)
    rows = []
    for tick in range(3):
        expected = [execution.step_numpy(states[0])]
        for ring in range(1, len(states)):
            extended = np.concatenate([states[0, :, -12:], states[ring], states[0, :, :12]], axis=1)
            value = execution.step_numpy(extended)[:, 12:-12]
            periodic = execution.step_numpy(states[ring])
            rows.append(dict(ring=ring, input_tick=tick,
                             ghost_vs_periodic_differing_bits=int(np.count_nonzero(value != periodic)),
                             NumPy_CUDA_equal=True))
            expected.append(value)
        sim.run(1)
        got = np.stack([machine.CKernel.unpack(state, p.Q) for state in sim.state()])
        assert np.array_equal(got, expected), tick
        states = got
    assert any(row['ghost_vs_periodic_differing_bits'] for row in rows)
    receipt = dict(
        proposal='SP4', proposed_rule_change=True, active_G17_modified=False,
        proposed_candidate_sha256=candidate.digest(), proposed_netlist_sha256=candidate.comp.digest,
        proposal_source_sha256=digest(Path(proposed.__file__)), checker_sha256=digest(Path(__file__)),
        ghost_helper_sha256=digest(Path(ghost.__file__)), gpu_backend_sha256=digest(ROOT / 'gacsca/gpu.py'),
        build_receipt_sha256=digest(out / 'SP4_program_build.json'), input_asset_sha256=digest(inputs),
        kernel_sha256=sim.source_sha256, rings=5, ticks=3, finite_comparisons=len(rows), checks=rows,
        noisy_rings_are_periodic_CA_trajectories=False,
        boundary_condition='input coordinates outside a noisy finite domain come from periodic clean ring0 at the same tick',
        global_reliability_established=False,
        result='measured: all twelve driven NumPy/CUDA updates and all three clean-twin updates agree',
        elapsed_seconds=time.monotonic()-started,
        scope='finite execution-operator checks only, not an infinite-Z or reliability theorem')
    (out / 'reference_ghost_certificate.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(dict(comparisons=len(rows), all_equal=True, seconds=receipt['elapsed_seconds'])), flush=True)


if __name__ == '__main__':
    main()
