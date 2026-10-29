#!/usr/bin/env python3
"""Finite four-real-set SP4 composition checks, with fresh-noise convention.

Four sets at the minimum spatial isolation, four timing families, E0 empty.
Computed and raw boundary decoders are measured separately. No iid theorem.
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
    seed = 1084463
    rng = np.random.default_rng(seed)
    top = codec.random_upper(candidate, 1, rng)
    initial_upper = augmented(candidate, top)
    base = machine.CKernel.pack(augmented(candidate, initial_upper))
    times = [(0, 0, 0, 0), (0, 4000, 9000, 10342),
             (9635, 22165, 25344, p.U-1),
             (p.U, p.U+4000, p.U+9000, 2*p.U-1)]
    initial_positions = (57, 57, 437, 57)
    starts = [[96*p.Q+position+i*(24*p.Q+15) for i in range(4)]
              for position in initial_positions]
    for sites in starts:
        assert all(b-a-15 == 24*p.Q for a,b in zip(sites, sites[1:]))
        assert 0 <= sites[0] and sites[-1]+16 < p.Q**2
    points = {(x,t) for x in range(16) for t in range(16)} | {(15,38)}
    replacements = rng.integers(0, 2, (4, 4, 17, candidate.W, 16), dtype=np.uint8)
    for case in range(4):
        for core in range(4):
            mode = (case+core) % 4
            for step in range(17):
                replacement = replacements[case, core, step]
                if mode == 0:
                    replacement[:] = 1
                elif mode == 2:
                    candidate.set_field(replacement, 'addr', 500)
                    candidate.set_field(replacement, 'age', (1 << p.m)-1)
                elif mode == 3:
                    candidate.set_field(replacement, 'addr', 448+(step+np.arange(16)) % 64)
                    candidate.set_field(replacement, 'age', np.where(np.arange(16) % 2,
                                       (1 << p.m)-1, p.age_code(p.T_wf)+step))
    asset = out / 'SP4_multiple_period_inputs.npz'
    np.savez_compressed(asset, seed=seed, top=top, initial_packed_base=base,
                        core_ticks=np.array(times, dtype=np.int32), core_starts=np.array(starts),
                        relative_error_points=np.array(sorted(points)), replacements=replacements)
    execution = copy.copy(candidate)
    execution.rom = np.pad(candidate.rom, ((0, (1 << p.k)-p.Q), (0, 0)))
    sim = gpu.GpuSim(execution, 5, p.Q, mode='grid')
    sim.set_state(np.broadcast_to(base, (5,)+base.shape).copy(), t=0)
    clean_upper = [initial_upper]
    for _ in range(4):
        clean_upper.append(execution.step_numpy(clean_upper[-1]))
    expected = [machine.CKernel.pack(augmented(candidate, upper)) for upper in clean_upper]
    events = {}
    for case in range(4):
        for core, tau in enumerate(times[case]):
            for step in range(16):
                events.setdefault(tau+step, []).append((case, core, step, tuple(range(16))))
            events.setdefault(tau+38, []).append((case, core, 16, (15,)))
    boundaries = {p.U, 2*p.U, 3*p.U}
    checks = []
    computed_decodes, raw_decodes = [], []
    result = dict(
        proposal='SP4', proposed_rule_change=True, active_G17_modified=False,
        proposed_candidate_sha256=candidate.digest(), proposed_netlist_sha256=candidate.comp.digest,
        proposal_source_sha256=digest(Path(proposed.__file__)), driver_sha256=digest(Path(__file__)),
        augmented_helper_sha256=digest(ROOT / 'Report/proofs/check_sparse_prefix448_physical.py'),
        physical_helper_sha256=digest(ROOT / 'Report/proofs/check_coherent_phase_physical.py'),
        build_receipt_sha256=digest(out / 'SP4_program_build.json'), input_asset_sha256=digest(asset),
        localization_receipt_sha256=digest(out / 'SP4_localization_certificate.json'),
        kernel_sha256=sim.source_sha256,
        completed_rom_sha256=hashlib.sha256(execution.rom.tobytes()).hexdigest(),
        Q=p.Q, U=p.U, physical_cells=p.Q**2, cases=4, sets_per_case=4,
        points_per_set=257, overwrites_per_case=1028, minimum_cross_set_spatial_gap=24*p.Q,
        noise_classification=dict(real_level1_sets=4, level0=0,
                                  method='kernel/tail candidate-pair argument, exact cross-set spatial isolation'),
        continuing_E0=False, native_C_comparison=False, periods=3, checks=checks,
        computed_decoder_convention='before fresh overwrites at that boundary',
        simultaneous_trajectory_theorem_established_by_experiment=False,
        global_reliability_established=False,
        scope='finite four-real-set composition checks; no iid or all-level theorem')

    def pairs(case, period):
        return [((start+16)//p.Q-1, (start+16)//p.Q)
                for start,tau in zip(starts[case], times[case]) if tau//p.U+1 == period]

    try:
        for tick in sorted(set(events) | boundaries):
            sim.run(tick-sim.t)
            computed = sim.state()
            if tick in boundaries:
                period = tick//p.U
                assert np.array_equal(computed[0], expected[period]), 'clean twin'
                for case in range(4):
                    allowed = sorted({j for pair in pairs(case, period) for j in pair})
                    decoded = codec.decode(candidate, machine.CKernel.unpack(computed[case+1], p.Q**2))
                    bad = np.flatnonzero(np.any(decoded != clean_upper[period], axis=0)).tolist()
                    assert set(bad) <= set(allowed), (case, period, 'computed decoder support', bad, allowed)
                    assert np.array_equal(execution.step_numpy(decoded), clean_upper[period+1]), (case, period, 'upper correction')
                    difference = computed[case+1] ^ expected[period]
                    for j in allowed:
                        difference[:, j*(p.Q//64):(j+1)*(p.Q//64)] = 0
                    assert not np.any(difference), (case, period, 'complete state outside current pair columns')
                    computed_decodes.append(decoded)
                    checks.append(dict(case=case, period=period, tick=tick, allowed_upper_cells=allowed,
                                       computed_changed_upper_cells=bad, upper_next_equals_clean=True,
                                       full_state_outside_current_pairs_exact=True))
            raw = computed.copy()
            for case, core, step, offsets in events.get(tick, ()):
                sites = starts[case][core]+np.array(offsets)
                values = replacements[case, core, step][:, list(offsets)]
                for row in range(candidate.W):
                    replace_bits(raw[case+1], row, sites, values[row])
            if tick in events:
                sim.set_state(raw, t=tick)
            if tick in boundaries:
                period = tick//p.U
                for case in range(4):
                    decoded = codec.decode(candidate, machine.CKernel.unpack(raw[case+1], p.Q**2))
                    bad = np.flatnonzero(np.any(decoded != clean_upper[period], axis=0)).tolist()
                    fresh = {j for start,tau in zip(starts[case], times[case]) if tau == tick
                             for j in ((start+16)//p.Q-1, (start+16)//p.Q)}
                    check = next(c for c in checks if c['case'] == case and c['period'] == period)
                    assert set(bad) <= set(check['allowed_upper_cells']) | fresh
                    check.update(raw_changed_upper_cells=bad, fresh_boundary_upper_cells=sorted(fresh))
                    raw_decodes.append(decoded)
                print(json.dumps(dict(period=period,
                                      computed_changes=[c['computed_changed_upper_cells'] for c in checks[-4:]],
                                      raw_changes=[c['raw_changed_upper_cells'] for c in checks[-4:]])), flush=True)
        assert all(np.array_equal(ring, expected[3]) for ring in sim.state()), 'full final boundaries'
        data = out / 'SP4_multiple_period_decoded.npz'
        np.savez_compressed(data, computed_decodes=np.stack(computed_decodes),
                            raw_decodes=np.stack(raw_decodes), clean_upper=np.stack(clean_upper))
        result.update(decoded_asset_sha256=digest(data), full_final_boundary_comparisons=5,
                      result='measured: twelve computed/raw boundary comparisons and all five full final boundaries pass')
    except Exception:
        failure = out / 'SP4_multiple_period_failure.npz'
        np.savez_compressed(failure, got=sim.state(), gpu_tick=sim.t)
        result.update(result='failed finite simultaneous-map comparison', failure_asset_sha256=digest(failure))
        raise
    finally:
        result['elapsed_seconds'] = time.monotonic()-started
        (out / 'SP4_multiple_period_physical.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(dict(result=result['result'], elapsed_seconds=result['elapsed_seconds'])), flush=True)


if __name__ == '__main__':
    main()
