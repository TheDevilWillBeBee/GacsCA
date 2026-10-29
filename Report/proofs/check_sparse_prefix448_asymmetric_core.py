#!/usr/bin/env python3
"""Finite boundary-collision probe with a shifted clean left reference.

Explicitly changed driven boundary condition; unchanged interior SP4 rule.
The initial 32-cell upper word is a flat finite context, not a pristine
infinite-hierarchy operational snapshot. No theorem is tested by assertion.
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
from gacsca import codec, machine
import proposed_sparse_prefix448 as proposed
from check_sparse_prefix448_physical import augmented
from check_coherent_phase_physical import replace_bits
import asymmetric_ghost_gpu as ghost


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    started = time.monotonic()
    out = ROOT / 'figs/robustness'
    candidate = proposed.load_artifact()
    p = candidate.p
    columns = 32
    cells = columns*p.Q
    upper_clock = 25344
    upper = np.zeros((candidate.W, columns), dtype=bool)
    candidate.set_field(upper, 'addr', np.arange(columns))
    candidate.set_field(upper, 'age', p.age_code(upper_clock))
    lower = augmented(candidate, upper)
    shifted = np.roll(lower, 1, axis=1)
    cases = [dict(begin=begin, closest_right_point=begin+1, tau=tau)
             for tau in (0, p.U-1) for begin in (0, 417, 879, 880)]
    states = [machine.CKernel.pack(lower), machine.CKernel.pack(shifted)]
    states += [machine.CKernel.pack(lower) for _ in range(len(cases)+1)]
    replacements = np.zeros((len(cases), 17, candidate.W, 16), dtype=bool)
    events = {}
    for case, item in enumerate(cases):
        sites = item['begin']+np.arange(16)
        template = lower[:, (sites-1) % cells]
        for step in range(17):
            tick = item['tau']+(step if step < 16 else 38)
            value = template.copy()
            candidate.set_field(value, 'age', p.age_code(tick % p.U))
            replacements[case, step] = value
            offsets = tuple(range(16)) if step < 16 else (15,)
            events.setdefault(tick, []).append((case+3, case, step, offsets))
    asset = out / 'SP4_asymmetric_core_inputs.npz'
    np.savez_compressed(asset, initial_packed=np.stack(states), upper=upper,
                        cases=np.asarray([(item['begin'], item['tau']) for item in cases]),
                        replacements=replacements)
    execution = copy.copy(candidate)
    execution.rom = np.pad(candidate.rom, ((0, (1 << p.k)-p.Q), (0, 0)))
    sim = ghost.sim(execution, len(states), columns)
    sim.set_state(np.stack(states), t=0)
    del states, lower, shifted
    result = dict(
        proposal='SP4', proposed_rule_change=True, active_G17_modified=False,
        proposed_candidate_sha256=candidate.digest(), proposed_netlist_sha256=candidate.comp.digest,
        proposal_source_sha256=digest(Path(proposed.__file__)), driver_sha256=digest(Path(__file__)),
        asymmetric_ghost_helper_sha256=digest(Path(ghost.__file__)),
        ghost_operator_receipt_sha256=digest(out / 'asymmetric_ghost_certificate.json'),
        augmented_helper_sha256=digest(ROOT / 'Report/proofs/check_sparse_prefix448_physical.py'),
        physical_helper_sha256=digest(ROOT / 'Report/proofs/check_coherent_phase_physical.py'),
        build_receipt_sha256=digest(out / 'SP4_program_build.json'), input_asset_sha256=digest(asset),
        kernel_sha256=sim.source_sha256, completed_rom_sha256=hashlib.sha256(execution.rom.tobytes()).hexdigest(),
        Q=p.Q, U=p.U, physical_cells=cells, upper_cells=columns, upper_clock=upper_clock,
        rings=len(cases)+3, cases=cases, periodic_reference_rings=[0, 1],
        boundary_only_control_ring=2, left_reference_phase_shift=-1,
        noise_classification='each finite 16x16 kernel plus one tail at (begin+15,tau+38) is one real c16/lambda24 level1 set in the driven fundamental domain',
        points_per_case=257, continuing_E0=False, native_C_comparison=False,
        changed_boundary_condition=True, noisy_rings_are_periodic_CA_trajectories=False,
        initial_pristine_infinite_hierarchy=False, infinite_line_equivalence_established=False,
        global_reliability_established=False, checks=[],
        scope='finite flat-upper-context probe; computed checkpoints before fresh replacements; no trajectory theorem or iid counterexample')
    checkpoints = {420, 920, p.U, p.U+419, p.U+919, 2*p.U}
    snapshots, decoded, ticks = [], [], []
    gf_rows = [candidate.row[field, bit] for field, width in (('addr', p.k), ('age', p.m))
               for bit in range(width)]
    flag_rows = [candidate.row[field, 0] for field in ('f1', 'f2', 'wf1', 'wf2')]
    for tick in sorted(set(events) | checkpoints):
        sim.run(tick-sim.t)
        got = sim.state()
        if tick in checkpoints:
            raw = [machine.CKernel.unpack(ring, cells) for ring in got]
            reference = raw[0]
            check = dict(tick=tick, decoder='computed before fresh replacements', rings=[])
            for ring in range(2, len(raw)):
                gf_bad = np.any(raw[ring][gf_rows] != reference[gf_rows], axis=0)
                flags_bad = np.any(raw[ring][flag_rows] != reference[flag_rows], axis=0)
                own_flags = np.any(raw[ring][flag_rows], axis=0)
                check['rings'].append(dict(
                    ring=ring, case=None if ring == 2 else ring-3,
                    geometry_differences_total=int(gf_bad.sum()),
                    geometry_differences_first_four_colonies=[int(part.sum()) for part in np.split(gf_bad[:4*p.Q], 4)],
                    flag_differences_first_four_colonies=[int(part.sum()) for part in np.split(flags_bad[:4*p.Q], 4)],
                    nonzero_flags_first_four_colonies=[int(part.sum()) for part in np.split(own_flags[:4*p.Q], 4)]))
            result['checks'].append(check)
            snapshots.append(got[:, :, :8*(p.Q//64)].copy())
            decoded.append(np.stack([codec.decode(candidate, state) for state in raw]))
            ticks.append(tick)
            print(json.dumps(dict(tick=tick, GF_first_four=[row['geometry_differences_first_four_colonies']
                                                          for row in check['rings']])), flush=True)
        for ring, case, step, offsets in events.get(tick, ()):
            sites = cases[case]['begin']+np.asarray(offsets)
            value = replacements[case, step][:, list(offsets)]
            for row in range(candidate.W):
                replace_bits(got[ring], row, sites, value[row])
        if tick in events:
            sim.set_state(got, t=tick)
    data = out / 'SP4_asymmetric_core_tracking.npz'
    np.savez_compressed(data, ticks=ticks, first_eight_colony_packed=np.stack(snapshots),
                        computed_decoded_upper=np.stack(decoded), final_packed=sim.state())
    result.update(tracking_asset_sha256=digest(data), elapsed_seconds=time.monotonic()-started,
                  result='measured: six computed checkpoints retained for eight real-core driven cases and one boundary-only control')
    (out / 'SP4_asymmetric_core_physical.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(dict(result=result['result'], elapsed_seconds=result['elapsed_seconds'])), flush=True)


if __name__ == '__main__':
    main()
