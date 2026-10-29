#!/usr/bin/env python3
"""Exact local counterexample to naive discarded-prefix + pair closure.

Two permanent arbitrary upper columns plus a new pair exceed the proved
row-density hypothesis. This is not a reachable-physical-core or iid
counterexample. The maintenance identities cover arbitrary simulation data.
"""
import copy
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import numpy as np
from gacsca.netlist import Net, const_word
import proposed_sparse_prefix448 as proposed
import prefix_selection as selection
from check_fast_flag_proposal import invoke


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    candidate = proposed.load_artifact()
    p = candidate.p
    out = ROOT / 'figs/robustness'
    clock = 2000
    assert clock < p.T_wf
    build, source = selection.proposed_build(symbolic=True)
    rows = []
    for address in range(2, 8):
        n = Net()
        cells = {}
        for off in range(-5, 9):
            position = address+off
            if off >= 6:
                cells[off] = dict(f1=0)
                continue
            phase = -1 if position < 4 else 0
            cells[off] = dict(addr=const_word((position+phase) % p.Q, p.k),
                              age=const_word(p.age_code(clock), p.m),
                              f1=0, f2=0, wf1=0, wf2=0)
        result = invoke(build, n, cells, p)
        wanted = address-1 if 3 <= address <= 6 else address
        assert result['addr'] == const_word(wanted, p.k)
        assert result['age_now'] == const_word(p.age_code(clock), p.m)
        assert result['age'] == const_word(p.age_code(clock+1), p.m)
        assert result['f1'] == int(3 <= address <= 6) and result['f2'] == 0
        rows.append(dict(healthy_before_pair=address >= 4, upper_address=address,
                         computed_address=wanted, computed_Flag1=int(3 <= address <= 6),
                         computed_Flag2=0, computed_clock=clock+1))
    cells = 3*p.Q
    boundary = p.Q
    pristine = np.zeros((candidate.W, cells), dtype=bool)
    candidate.set_field(pristine, 'addr', np.arange(cells) % p.Q)
    candidate.set_field(pristine, 'age', p.age_code(clock))
    prefix = pristine.copy()
    positions = np.arange(boundary+2)
    # Advanced indexing returns a copy; assign the modified block explicitly.
    block = prefix[:, positions].copy()
    candidate.set_field(block, 'addr', (positions-1) % p.Q)
    prefix[:, positions] = block
    combined = prefix.copy()
    pair_sites = boundary+np.arange(2, 4)
    block = combined[:, pair_sites].copy()
    candidate.set_field(block, 'addr', (np.arange(2, 4)-1) % p.Q)
    combined[:, pair_sites] = block
    pair_only = pristine.copy()
    pair_only[:, pair_sites] = block
    execution = copy.copy(candidate)
    execution.rom = np.pad(candidate.rom, ((0, (1 << p.k)-p.Q), (0, 0)))
    got = [execution.step_numpy(state) for state in (pristine, prefix, pair_only, combined)]
    window = boundary+np.arange(2, 8)
    for address in range(2, 8):
        pos = boundary+address
        assert candidate.field(got[3], 'addr')[pos] == rows[address-2]['computed_address']
        assert candidate.field(got[3], 'f1')[pos] == rows[address-2]['computed_Flag1']
    gf_rows = [candidate.row[field, bit] for field, width in (('addr', p.k), ('age', p.m))
               for bit in range(width)]
    assert np.array_equal(got[1][gf_rows][:, window], got[0][gf_rows][:, window])
    assert np.array_equal(got[2][gf_rows][:, window], got[0][gf_rows][:, window])
    assert candidate.field(got[3], 'addr')[boundary+4:boundary+7].tolist() == [3, 4, 5]
    packing = []
    for anchor in range(1, 26):
        damaged = {0, 1, anchor, anchor+1}
        worst = max(sum(start <= pos < start+11 for pos in damaged)
                    for start in range(-10, 37))
        assert (worst <= 2) == (anchor >= 11)
        packing.append(dict(new_pair_anchor=anchor, maximum_faults_per_eleven=worst,
                            quiet_colony_density_hypothesis=worst <= 2))
    asset = out / 'SP4_boundary_prefix_pair_inputs.npz'
    np.savez_compressed(asset, initial=np.stack([pristine, prefix, pair_only, combined]),
                        computed=np.stack(got), boundary=boundary, pair_sites=pair_sites)
    dependencies = ('SP4_program_build.json', 'SP4_maintenance_certificate.json',
                    'SP4_localization_certificate.json', 'SP4_shifted_halfline_certificate.json',
                    'SP4_coupled_boundary_core_certificate.json')
    result = dict(
        proposal='SP4', proposed_rule_change=True, active_G17_modified=False,
        proposed_candidate_sha256=candidate.digest(), proposed_netlist_sha256=candidate.comp.digest,
        proposal_source_sha256=digest(Path(proposed.__file__)), checker_sha256=digest(Path(__file__)),
        selection_source_sha256=digest(ROOT / 'Report/proofs/prefix_selection.py'),
        actual_maintenance_source_sha256=hashlib.sha256(source.encode()).hexdigest(),
        input_asset_sha256=digest(asset), symbolic_constant_cases=6, NumPy_comparisons=4,
        upper_clock=clock, discarded_upper_columns=[0, 1], new_upper_pair=[2, 3],
        initial_flags_and_Workspace_zero=True, wrong_left_geometry_phase=-1,
        newly_wrong_healthy_upper_columns=[4, 5, 6], symbolic_rows=rows,
        prefix_pair_density_cases=packing, minimum_new_pair_anchor_for_two_per_eleven_density=11,
        corresponding_physical_core_right_point=12*p.Q-15,
        prefix_alone_right_window_correct=True, pair_alone_right_window_correct=True,
        all_other_simulation_fields_irrelevant_to_maintenance=True,
        proof_receipt_sha256={name:digest(out / name) for name in dependencies},
        reachable_after_J47_established=False, reachable_from_real_physical_level1_core_established=False,
        independent_noise_unreliability_established=False, global_reliability_established=False,
        scope='proved local counterexample to arbitrary discarded-prefix plus arbitrary pair preserving right GF; no mapped-pair reachability or iid claim')
    (out / 'SP4_boundary_prefix_pair_certificate.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(dict(newly_wrong_healthy_columns=[4, 5, 6], constant_cases=6,
                          prefix_alone_and_pair_alone_correct=True)), flush=True)


if __name__ == '__main__':
    main()
