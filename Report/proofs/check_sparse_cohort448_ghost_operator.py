#!/usr/bin/env python3
"""Finite literal NumPy/CUDA comparison of the asymmetric halo operator."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import numpy as np
from gacsca import machine
import proposed_sparse_cohort448 as proposed
import asymmetric_ghost_gpu as ghost


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    started = time.monotonic()
    candidate = proposed.load_artifact()
    p = candidate.p
    execution = copy.copy(candidate)
    execution.rom = np.pad(candidate.rom, ((0, (1 << p.k)-p.Q), (0, 0)))
    rng = np.random.default_rng(1084470)
    states = rng.random((5, candidate.W, p.Q)) < 0.5
    states[3] = False
    states[4] = True
    out = ROOT / 'figs/robustness'
    asset = out / 'SP12_asymmetric_ghost_inputs.npz'
    np.savez_compressed(asset, initial=states)
    sim = ghost.sim(execution, 5, 1)
    sim.set_state(np.stack([machine.CKernel.pack(state) for state in states]))
    checks = []
    reference_checks = 0
    for tick in range(3):
        expected = [execution.step_numpy(states[0]), execution.step_numpy(states[1])]
        for ring in range(2, 5):
            extended = np.concatenate([states[1, :, -12:], states[ring], states[0, :, :12]], axis=1)
            value = execution.step_numpy(extended)[:, 12:-12]
            checks.append(dict(input_tick=tick, ring=ring, NumPy_CUDA_equal=True,
                               differing_bits_from_periodic=int(np.count_nonzero(value != execution.step_numpy(states[ring])))))
            expected.append(value)
        sim.run(1)
        got = np.stack([machine.CKernel.unpack(state, p.Q) for state in sim.state()])
        assert np.array_equal(got, expected), tick
        reference_checks += 2
        states = got
    assert any(row['differing_bits_from_periodic'] for row in checks)
    result = dict(
        proposal='SP12', proposed_rule_change=True, active_G17_modified=False,
        proposed_candidate_sha256=candidate.digest(), proposed_netlist_sha256=candidate.comp.digest,
        proposal_source_sha256=digest(Path(proposed.__file__)), checker_sha256=digest(Path(__file__)),
        asymmetric_ghost_helper_sha256=digest(Path(ghost.__file__)),
        gpu_backend_sha256=digest(ROOT / 'gacsca/gpu.py'),
        build_receipt_sha256=digest(out / 'SP12_program_build.json'), input_asset_sha256=digest(asset),
        kernel_sha256=sim.source_sha256, rings=5, ticks=3, driven_comparisons=9,
        reference_comparisons=reference_checks, checks=checks,
        periodic_reference_rings=[0, 1], left_reference_ring=1, right_reference_ring=0,
        noisy_rings_are_periodic_CA_trajectories=False, global_reliability_established=False,
        scope='finite execution-only comparison of an explicitly changed boundary condition; no infinite-hierarchy equivalence',
        result='measured: nine driven and six periodic reference updates agree with literal NumPy',
        elapsed_seconds=time.monotonic()-started)
    (out / 'SP12_asymmetric_ghost_certificate.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(dict(driven=9, references=reference_checks, all_equal=True,
                          seconds=result['elapsed_seconds'])), flush=True)


if __name__ == '__main__':
    main()
