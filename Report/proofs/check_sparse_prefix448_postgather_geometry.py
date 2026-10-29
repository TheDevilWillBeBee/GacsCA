#!/usr/bin/env python3
"""Finite J33 geometry checks at post-gather, command and commit stages.

One257-point real level1 set per case; E0 empty. No all-field boundary
or iid reliability result is claimed. The analytic proof is separate.
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
    proof = json.loads((out / 'SP4_autonomy_certificate.json').read_text())
    assert proof['post_gather_core_begin'] == 9635
    points = {(x, t) for x in range(16) for t in range(16)} | {(15, 38)}
    kernel = points-{(15, 38)}
    assert len(points) == 257 and len(kernel) == 256
    assert max(x for x, _ in kernel)-min(x for x, _ in kernel) < 16
    assert max(t for _, t in kernel)-min(t for _, t in kernel) < 16
    assert 38-15 < 24
    seed = 1084433
    rng = np.random.default_rng(seed)
    top = codec.random_upper(candidate, 1, rng)
    lower = augmented(candidate, augmented(candidate, top))
    base = machine.CKernel.pack(lower)
    modes = ('random', 'one', 'unused', 'staggered')
    ticks = (9635, 11264, 22165, 25287, 25344, 26240, 56319, 67583)
    cases = [(tau, pos, modes[(2*index+j) % 4]) for index, tau in enumerate(ticks)
             for j, pos in enumerate((59, 437))]
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
    asset = out / 'SP4_postgather_geometry_inputs.npz'
    np.savez_compressed(asset, seed=seed, top=top, initial_packed_base=base,
                        cases=np.array([(tau, pos) for tau, pos, _ in cases], dtype=np.int32),
                        replacement_modes=np.array([mode for _, _, mode in cases]),
                        relative_error_points=np.array(sorted(points), dtype=np.int32), replacements=replacements)
    execution = copy.copy(candidate)
    execution.rom = np.pad(candidate.rom, ((0, (1 << p.k)-p.Q), (0, 0)))
    sim = gpu.GpuSim(execution, len(cases)+1, p.Q, mode='grid')
    sim.set_state(np.broadcast_to(base, (len(cases)+1,)+base.shape).copy(), t=0)
    del lower
    centers = [p.Q**2//2+pos for _, pos, _ in cases]
    boundaries = [((start+16)//p.Q+1)*p.Q for start in centers]
    result = dict(proposal='SP4', proposed_rule_change=True, active_G17_modified=False,
                  proposed_candidate_sha256=candidate.digest(), proposed_netlist_sha256=candidate.comp.digest,
                  proposal_source_sha256=digest(Path(proposed.__file__)), driver_sha256=digest(Path(__file__)),
                  augmented_helper_sha256=digest(ROOT / 'Report/proofs/check_sparse_prefix448_physical.py'),
                  physical_helper_sha256=digest(ROOT / 'Report/proofs/check_coherent_phase_physical.py'),
                  proof_receipt_sha256=digest(out / 'SP4_autonomy_certificate.json'),
                  build_receipt_sha256=digest(out / 'SP4_program_build.json'),
                  input_asset_sha256=digest(asset), kernel_sha256=sim.source_sha256,
                  completed_rom_sha256=hashlib.sha256(execution.rom.tobytes()).hexdigest(),
                  Q=p.Q, U=p.U, physical_cells=p.Q**2, cases=len(cases), seed=seed,
                  noise_classification=dict(level1=True, level0=0, points=257,
                                            method='exact kernel/tail candidate-pair argument'),
                  overwrites_per_case=257, continuing_E0=False, native_C_comparison=False,
                  protected_colony_checks=0, geometry_checks=[], global_reliability_established=False,
                  scope='finite first-period post-gather J33 geometry/quiet-colony checks; no all-field boundary claim')
    events, checkpoints = {}, {}
    for index, (tau, _, _) in enumerate(cases):
        for step in range(16):
            events.setdefault(tau+step, []).append((index, step, tuple(range(16))))
        events.setdefault(tau+38, []).append((index, 16, (15,)))
        for offset in (396, 420):
            checkpoints.setdefault(tau+offset, []).append((index, offset))
    saved_colonies = []
    saved_ids = []
    reference_address = np.arange(p.Q**2) % p.Q

    def protected(got, index, tick):
        C = boundaries[index]
        local = machine.CKernel.unpack(np.ascontiguousarray(
                    got[index+1, :, C//64:(C+p.Q)//64]), p.Q)
        assert np.array_equal(candidate.field(local, 'addr'), np.arange(p.Q)), (index, tick, 'barrier Address')
        assert np.all(candidate.field(local, 'age') == p.age_code(tick % p.U)), (index, tick, 'barrier Age')
        assert not np.any(candidate.field(local, 'f1')), (index, tick, 'barrier Flag1')
        assert not np.any(candidate.field(local, 'wf1')), (index, tick, 'barrier Workspace.Flag1')
        result['protected_colony_checks'] += 1
        return local

    try:
        for tick in sorted(set(events) | set(checkpoints)):
            sim.run(tick-sim.t)
            got = sim.state()
            for index, _, _ in events.get(tick, ()):
                protected(got, index, tick)
            for index, offset in checkpoints.get(tick, ()):
                local = protected(got, index, tick)
                rows = [candidate.row['addr', bit] for bit in range(p.k)]
                rows += [candidate.row['age', bit] for bit in range(p.m)]
                geometry = machine.CKernel.unpack(got[index+1, rows], p.Q**2)
                address = sum(geometry[bit].astype(np.int64) << bit for bit in range(p.k))
                age = sum(geometry[p.k+bit].astype(np.int64) << bit for bit in range(p.m))
                assert np.all(address % p.Q == reference_address), (index, tick, 'phase')
                assert np.all(age == p.age_code(tick % p.U)), (index, tick, 'global Age')
                aliases = int(np.count_nonzero(address != reference_address))
                if offset == 420:
                    assert aliases == 0, (index, tick, 'raw geometry')
                    saved_colonies.append(local)
                    saved_ids.append((index, tick))
                result['geometry_checks'].append(dict(case=index, tau=cases[index][0], position=cases[index][1],
                                                     mode=cases[index][2], checkpoint=tick, offset=offset,
                                                     phase_exact=True, Age_exact=True, raw_Address_aliases=aliases))
            for index, step, offsets in events.get(tick, ()):
                sites = centers[index]+np.array(offsets)
                values = replacements[index, step][:, list(offsets)]
                for row in range(candidate.W):
                    replace_bits(got[index+1], row, sites, values[row])
            if tick in events:
                sim.set_state(got, t=tick)
        tracking = out / 'SP4_postgather_geometry_tracking.npz'
        np.savez_compressed(tracking, ids=np.array(saved_ids, dtype=np.int32),
                            protected_colony_states=np.stack(saved_colonies),
                            boundaries=np.array(boundaries, dtype=np.int32))
        result.update(tracking_asset_sha256=digest(tracking),
                      result='measured: all sixteen post-gather/command/commit cases satisfy the global geometry deadlines and protected-colony checks')
    except Exception:
        failure = out / 'SP4_postgather_geometry_failure.npz'
        np.savez_compressed(failure, got=sim.state(), gpu_tick=sim.t)
        result.update(result='failed finite post-gather geometry comparison', failure_asset_sha256=digest(failure))
        raise
    finally:
        result['elapsed_seconds'] = time.monotonic()-started
        (out / 'SP4_postgather_geometry_physical.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({key: result[key] for key in ('result', 'elapsed_seconds', 'protected_colony_checks')}), flush=True)


if __name__ == '__main__':
    main()
