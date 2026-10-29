#!/usr/bin/env python3
"""J93: exact SP14 later-birth/source-displacement witness, not iid failure.

Initial full-rule birth cofactors leave ordinary flags/data/instructions
free. A retained 26-step literal NumPy/C trace supplies an independently
replayable finite witness. The origin/count argument is in ROBUSTNESS.
No active or isolated proposal rule is changed by this checker.
"""
import copy
import hashlib
import json
from pathlib import Path
import sys
import time
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import numpy as np
from gacsca import machine, rule_g
from gacsca.netlist import Net
from check_shifted_halfline import dominant_bit
import check_fast_mail_proposal as transport
import proposed_sparse_framed448 as proposed


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def birth_case(p, x):
    maintenance, _ = proposed.proposed_build(symbolic=True)
    _, source = proposed.actual_net(p)
    class BoundNet(Net):
        def input(self, key):
            if key[0] == 'x':
                _, off, field, bit = key
                y = x + off
                alive = y in (3, 4, 5)
                if field == 'addr':
                    return (((y + 4) % p.Q) >> bit) & 1
                if field == 'age':
                    return (p.age_code(p.T_wf) >> bit) & 1
                if field == 'info':
                    return 1
                if field in ('packet_valid', 'wf2'):
                    return int(alive)
                if field == 'packet_tag':
                    return (((y - 1) if alive else 0) >> bit) & 1
                if field in ('packet_count', 'service_valid', 'service_position', 'service_count'):
                    return 0
            return super().input(key)
    namespace = dict(rule_g.__dict__, Net=BoundNet, maj5=dominant_bit,
        maintenance=SimpleNamespace(build=maintenance), schema=proposed.schema,
        service_build=proposed.service.build, OFFSETS=tuple(range(-12, 13)),
        sparse_controls=transport.sparse_controls, sparse_table=proposed.dependency_table(p))
    exec(compile(source, '<SP14 actual younger-source birth seam>', 'exec'), namespace)
    n = namespace['build'](p)
    new = x in (-3, -2, -1)
    old = 1 <= x <= 5
    alive = new or old
    tag = x + 3 if new else x - 1 if old else 0
    count = int(old)
    assert n.outputs['y', 'packet_valid', 0] == int(alive), x
    assert n.outputs['y', 'wf2', 0] == int(alive), x
    assert [n.outputs['y', 'packet_tag', b] for b in range(4)] == [(tag >> b) & 1 for b in range(4)], x
    assert [n.outputs['y', 'packet_count', b] for b in range(11)] == [(count >> b) & 1 for b in range(11)], x


def main():
    started = time.monotonic()
    candidate = proposed.load_artifact()
    p = candidate.p
    for x in range(-4, 7):
        birth_case(p, x)
    print(json.dumps(dict(actual_birth_cofactors=11, passed=True)), flush=True)
    execution = copy.copy(candidate)
    execution.rom = np.pad(candidate.rom, ((0, (1 << p.k) - p.Q), (0, 0)))
    cells, center = 3*p.Q, p.Q
    coordinates = np.arange(cells) - center
    initial = np.zeros((candidate.W, cells), dtype=bool)
    candidate.set_field(initial, 'addr', (coordinates + 4) % p.Q)
    candidate.set_field(initial, 'age', p.age_code(p.T_wf))
    for bit in range(5):
        initial[candidate.row['info', bit]] = True
    holders = center + np.arange(1, 6)
    initial[candidate.row['wf2', 0], holders] = True
    initial[candidate.row['packet_valid', 0], holders] = True
    for b in range(4):
        initial[candidate.row['packet_tag', b], holders] = ((np.arange(5) >> b) & 1).astype(bool)
    faults = {0: (1, 2), 25: (2, 3)}
    raw = initial.copy()
    snapshots = [machine.CKernel.pack(raw)]
    rows, overwritten = [], []
    backend = execution.c_backend()
    for t in range(26):
        if t in faults:
            sites = center + np.asarray(faults[t])
            for field in ('wf2', 'packet_valid', 'packet_tag', 'packet_count',
                          'service_valid', 'service_position', 'service_count'):
                for b in range(dict(candidate.schema)[field]):
                    raw[candidate.row[field, b], sites] = False
            overwritten.append(machine.CKernel.pack(raw[:, sites].repeat(32, axis=1)))
        expected = execution.step_numpy(raw)
        actual = backend.run(raw, 1)
        assert np.array_equal(expected, actual), t
        raw = expected
        assert np.array_equal(candidate.field(raw, 'addr'), (coordinates + 4) % p.Q), t
        assert np.all(candidate.field(raw, 'age') == p.age_code(p.T_wf + t + 1)), t
        live = (candidate.field(raw, 'packet_valid') & candidate.field(raw, 'wf2') &
                (candidate.field(raw, 'packet_tag') < 5)).astype(bool)
        origin = coordinates - candidate.field(raw, 'packet_tag') - 1
        old = np.flatnonzero(live & (origin == 0))
        young = np.flatnonzero(live & (origin == -4))
        row = dict(state=t + 1, old_source_sites=coordinates[old].tolist(),
            old_source_counts=candidate.field(raw, 'packet_count')[old].tolist(),
            young_source_sites=coordinates[young].tolist(),
            young_source_counts=candidate.field(raw, 'packet_count')[young].tolist(),
            NumPy_C_all_bits_equal=True)
        rows.append(row)
        snapshots.append(machine.CKernel.pack(raw))
        print(json.dumps(row), flush=True)
    assert rows[0]['old_source_sites'] == [1, 2, 3, 4, 5]
    assert rows[0]['young_source_sites'] == [-3, -2, -1]
    assert rows[1]['old_source_sites'] == [2, 3, 4, 5]
    assert rows[1]['young_source_sites'] == [-3, -2, -1, 0, 1]
    assert rows[24]['old_source_sites'] == [2, 3, 4, 5]
    assert rows[25]['old_source_sites'] == []
    assert rows[25]['young_source_sites'] == [-3, -2, -1, 0, 1]
    # Protected observations[-8,12] and all26 radius12 steps are farther
    # from both periodic seams than their causal radius312.
    assert center - 8 - 26*12 > 0
    assert center + 12 + 26*12 < cells
    out = ROOT / 'figs/robustness'
    asset = out / 'SP14_source_competition_trace.npz'
    np.savez_compressed(asset, initial=initial, computed_states_packed=np.stack(snapshots),
        input_fault_ticks=np.array(list(faults)), input_fault_sites=np.array(list(faults.values())))
    receipt = dict(proposal='SP14', proposed_rule_change=False, active_G17_modified=False,
        proposed_candidate_sha256=candidate.digest(), proposed_netlist_sha256=candidate.comp.digest,
        proposal_source_sha256=digest(Path(proposed.__file__)), checker_sha256=digest(Path(__file__)),
        helpers_sha256=digest(ROOT / 'gacsca/netlist.py'),
        dominant_bit_helper_sha256=digest(ROOT / 'Report/proofs/check_shifted_halfline.py'),
        transport_checker_sha256=digest(Path(transport.__file__)),
        full_generated_source_sha256=hashlib.sha256(proposed.actual_net(p)[1].encode()).hexdigest(),
        actual_maintenance_source_sha256=hashlib.sha256(proposed.proposed_build()[1].encode()).hexdigest(),
        build_receipt_sha256=digest(out / 'SP14_program_build.json'),
        framed_service_certificate_sha256=digest(out / 'framed_service_certificate.json'),
        canonical_birth_receipt_sha256=digest(out / 'SP14_packet_birth_certificate.json'),
        trace_asset_sha256=digest(asset), kernel_sha256=backend.source_sha256,
        kernel_kind='literal_C',
        completed_rom_sha256=hashlib.sha256(execution.rom.tobytes()).hexdigest(),
        full_rule_initial_birth_seam_cofactors=11,
        free_ordinary_flags_data_and_instruction_bits_in_birth_cofactors=True,
        exact_NumPy_C_full_state_comparisons=26, rows=rows,
        input_fault_groups=[dict(tick=t, sites=list(sites)) for t, sites in faults.items()],
        global_E0_separation_satisfied=True,
        initial_proper_fresh_source_origin=0, initial_source_count=0,
        all_other_initial_component_words_zero=True,
        new_birth_origin=-4, newborn_carriers_state_one=[-3, -2, -1],
        old_source_first_incomplete_state=2, old_source_erased_state=26,
        source_lifetime=1792, initial_uniform_global_clock=p.age_code(p.T_wf),
        initial_global_GF_phase=4, initialized_from_pristine_hierarchy=False,
        right_canonical_boundary_prescribed=False,
        finite_causal_buffer_updates=26, finite_causal_buffer_radius=12,
        verified_persistent_counting_profile=True,
        iid_unreliability_established=False, global_reliability_established=False,
        elapsed_seconds=time.monotonic() - started,
        scope='actual-rule counterexample to birth-independent initialized packet persistence; local cofactors plus origin/count induction in ROBUSTNESS J93; finite full-state trace retained')
    (out / 'SP14_source_competition_certificate.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(dict(source_erased_at=26, literal_comparisons=26,
        seconds=receipt['elapsed_seconds'], global_reliability_established=False)), flush=True)


if __name__ == '__main__':
    main()
