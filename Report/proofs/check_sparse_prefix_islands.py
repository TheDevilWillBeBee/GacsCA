#!/usr/bin/env python3
"""Finite full-CA support for SP3's arbitrary-island noise-free eroder.

No continuing noise; first right true colony is quiet. Random global
Flag2/Workspace.Flag2 bits test their proved independence from geometry.
This is separate from the universal local/unbounded-line proof.
"""
import copy
import hashlib
import itertools
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import numpy as np
from gacsca import gpu, machine
import proposed_sparse_prefix as proposed
from check_coherent_phase_physical import replace_bits


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    started = time.monotonic()
    out = ROOT / 'figs/robustness'
    candidate = proposed.load_artifact()
    p = candidate.p
    proof = json.loads((out / 'SP3_prefix_selection_certificate.json').read_text())
    bounds = {row['width']: row for row in proof['bounds']['widths']}
    seed = 1083103
    rng = np.random.default_rng(seed)
    columns = 40
    N = columns*p.Q
    widths = (1, 2, 3, 16, 62, 141, 196)
    positions = (0, 1, 2, 5, 128, 240, 380, 383)
    modes = ('random', 'invert', 'one', 'zero', 'unused', 'staggered')
    flag_modes = ('random', 'zero', 'one')
    cases = list(itertools.product(widths, positions, modes, flag_modes))
    baseline = rng.integers(0, 2, (candidate.W, N), dtype=np.uint8)
    candidate.set_field(baseline, 'addr', np.arange(N) % p.Q)
    candidate.set_field(baseline, 'age', 0)
    for field in ('f1', 'wf1'):
        candidate.set_field(baseline, field, 0)
    base = machine.CKernel.pack(baseline)
    states = np.broadcast_to(base, (len(cases)+1,)+base.shape).copy()
    replacements = np.zeros((len(cases), candidate.W, max(widths)), dtype=np.uint8)
    for i, (width, position, mode, flag_mode) in enumerate(cases):
        sites = N//2+position+np.arange(width)
        replacement = rng.integers(0, 2, (candidate.W, width), dtype=np.uint8)
        if mode == 'invert':
            replacement = baseline[:, sites] ^ 1
        elif mode == 'one':
            replacement[:] = 1
        elif mode == 'zero':
            replacement[:] = 0
        elif mode == 'unused':
            candidate.set_field(replacement, 'addr', 500)
            candidate.set_field(replacement, 'age', (1 << p.m)-1)
        elif mode == 'staggered':
            candidate.set_field(replacement, 'addr', 384+np.arange(width) % 128)
            candidate.set_field(replacement, 'age', np.where(np.arange(width) % 2,
                                (1 << p.m)-1, p.age_code(p.T_wf)+np.arange(width) % 128))
        if flag_mode != 'random':
            for field in ('f1', 'f2', 'wf1', 'wf2'):
                candidate.set_field(replacement, field, int(flag_mode == 'one'))
        replacements[i, :, :width] = replacement
        for row in range(candidate.W):
            replace_bits(states[i+1], row, sites, replacement[row])
    asset = out / 'SP3_island_inputs.npz'
    np.savez_compressed(asset, seed=seed, baseline_packed=base, columns=columns,
                        replacements=replacements,
                        cases=np.asarray([(w, pos, modes.index(mode), flag_modes.index(flags))
                                          for w, pos, mode, flags in cases], dtype=np.int32))
    execution = copy.copy(candidate)
    execution.rom = np.pad(candidate.rom, ((0, (1 << p.k)-p.Q), (0, 0)))
    geometry_bound = max(bounds[w]['geometric_repair_bound'] for w in widths)
    flag_bound = max(bounds[w]['global_flag_clearance_bound'] for w in widths)
    assert N//2-8*flag_bound > 0 and N//2+383+196+8*flag_bound < N
    sim = gpu.GpuSim(execution, len(cases)+1, columns, mode='grid')
    sim.set_state(states, t=0)
    del states, baseline, replacements
    geometry_rows = [candidate.row[field, bit] for field, length in (('addr', p.k), ('age', p.m))
                     for bit in range(length)]
    sim.track(geometry_rows)
    result = dict(proposal='SP3', proposed_rule_change=True, active_G17_modified=False, SP2_modified=False,
                  proposed_candidate_sha256=candidate.digest(), proposed_netlist_sha256=candidate.comp.digest,
                  proposal_source_sha256=digest(Path(proposed.__file__)),
                  selection_source_sha256=digest(ROOT / 'Report/proofs/prefix_selection.py'),
                  driver_sha256=digest(Path(__file__)),
                  physical_helper_sha256=digest(ROOT / 'Report/proofs/check_coherent_phase_physical.py'),
                  proof_receipt_sha256=digest(out / 'SP3_prefix_selection_certificate.json'),
                  build_receipt_sha256=digest(out / 'SP3_program_build.json'),
                  input_asset_sha256=digest(asset), kernel_sha256=sim.source_sha256,
                  Q=p.Q, U=p.U, raw_width=candidate.W, radius=12, seed=seed,
                  physical_cells_per_ring=N, cases=len(cases), widths=widths, positions=positions,
                  replacement_modes=modes, flag_modes=flag_modes, continuing_noise=False,
                  global_initial_Flag2_Workspace_Flag2_random=True,
                  native_C_comparison=False, geometry_bound=geometry_bound, Flag1_Flag2_bound=flag_bound,
                  completion='execution-only zero padding of unused ROM rows; active rules unchanged',
                  periodic_edge_outside_maintenance_cone=True, global_reliability_established=False,
                  scope='finite full-CA arbitrary-island checks; not continuing E0 or iid reliability')
    try:
        sim.run(geometry_bound)
        tracking = sim.tracking()
        got = sim.state()
        assert not np.any(got[:, geometry_rows] ^ got[0, geometry_rows]), 'geometric bound'
        for i, (width, _, _, _) in enumerate(cases, start=1):
            assert tracking['last_rows'][i].max() < bounds[width]['geometric_repair_bound'], (i, width)
        result['last_geometry_difference'] = int(tracking['last_rows'].max())
        del got
        flags = [candidate.row[field, 0] for field in ('f1', 'f2', 'wf1', 'wf2')]
        sim.track(flags)
        sim.run(flag_bound-geometry_bound)
        got = sim.state()
        assert not np.any(got[:, flags]), 'global flag clearance'
        assert not np.any(got[:, geometry_rows] ^ got[0, geometry_rows]), 'permanent geometry'
        data = out / 'SP3_island_tracking.npz'
        np.savez_compressed(data, **{'geometry_'+key: value for key, value in tracking.items()},
                            **{'flags_'+key: value for key, value in sim.tracking().items()})
        result.update(tracking_asset_sha256=digest(data), final_flags_zero=True,
                      final_geometry_equal=True,
                      final_all_field_difference_words=int(np.count_nonzero(got[1:] ^ got[0])),
                      result='measured: all 1008 arbitrary-island cases meet their proved geometry and flag bounds')
    except Exception:
        failure = out / 'SP3_island_failure.npz'
        np.savez_compressed(failure, got=sim.state(), gpu_tick=sim.t)
        result.update(result='failed finite arbitrary-island comparison', failure_asset_sha256=digest(failure))
        raise
    finally:
        result['elapsed_seconds'] = time.monotonic()-started
        (out / 'SP3_island_physical.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({key: result[key] for key in ('result', 'last_geometry_difference', 'elapsed_seconds')}), flush=True)


if __name__ == '__main__':
    main()
