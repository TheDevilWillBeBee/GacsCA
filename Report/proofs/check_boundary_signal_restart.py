#!/usr/bin/env python3
"""Local witness: a clean far frame does not imply a clean signal restart.

At signal input clock25344, change only the ML copies of logical primary3.
The subsequent Info/Workspace/Flag2 changes are exact Boolean identities.
Reachability after a physical core and iid unreliability are not inferred.
"""
import copy
import hashlib
import json
from pathlib import Path
import sys
from types import FunctionType, SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import numpy as np
from gacsca import rule_g
from gacsca.netlist import Net, Compiled, const_word
import proposed_sparse_prefix448 as proposed
import prefix_selection as selection
import check_fast_mail_proposal as transport
from check_shifted_halfline import dominant_bit


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    candidate = proposed.load_artifact()
    p = candidate.p
    out = ROOT / 'figs/robustness'
    assert transport.maj5_truth() == 32
    namespace = dict(transport.__dict__, proposed_maintenance=selection.proposed_build)
    factory = FunctionType(transport.concrete_sparse_net.__code__, namespace)
    actual, source = factory(p, proposed.dependency_table(p))
    assert Compiled(actual).digest == candidate.comp.digest
    maintenance, _ = selection.proposed_build(symbolic=True)
    tagged = set(proposed.fivefold_fields(p))
    checks = []
    for stage in range(3):
        clock = p.T_sig+stage
        for address in range(2, 8):
            class BoundNet(Net):
                def input(self, name):
                    if name[0] == 'x':
                        _, offset, field, bit = name
                        position = address+offset
                        if position >= 2:
                            if field == 'addr':
                                return ((position % p.Q) >> bit) & 1
                            if field == 'age':
                                return (p.age_code(clock) >> bit) & 1
                            if field in ('f1', 'f2', 'wf1'):
                                return 0
                            if field == 'wf2':
                                return int(stage == 2 and 2 <= position <= 4)
                            if field in tagged:
                                width = proposed.logical_width(field, p)
                                logical = position+bit//width-2
                                if logical >= 3:
                                    if logical == 3 and field == 'info':
                                        return int(stage >= 1)
                                    if logical == 3 and field == 'ml':
                                        return int(stage == 0)
                                    if logical == 3 and field in ('hold', 'pend', 'pkind', 'pval'):
                                        return 0
                                    return super().input(('coherent_copy', logical, field, bit % width))
                    return super().input(name)

            build_namespace = dict(rule_g.__dict__)
            build_namespace.update(Net=BoundNet, maintenance=SimpleNamespace(build=maintenance),
                                   maj5=dominant_bit, OFFSETS=tuple(range(-12, 13)),
                                   sparse_controls=transport.sparse_controls,
                                   sparse_table=proposed.dependency_table(p))
            exec(compile(source, '<same SP4 source, signal restart witness>', 'exec'), build_namespace)
            bounded = build_namespace['build'](p)
            assert [bounded.outputs['y', 'addr', bit] for bit in range(p.k)] == const_word(address, p.k)
            assert [bounded.outputs['y', 'age', bit] for bit in range(p.m)] == const_word(p.age_code(clock+1), p.m)
            assert bounded.outputs['y', 'f1', 0] == 0
            assert bounded.outputs['y', 'f2', 0] == int(stage == 2)
            assert bounded.outputs['y', 'wf1', 0] == 0
            expected_wf2 = int(stage >= 1 and address < 5)
            assert bounded.outputs['y', 'wf2', 0] == expected_wf2
            if address <= 5:
                slot = 3-address
                assert bounded.outputs['y', 'info', slot+2] == 1
            checks.append(dict(input_clock=clock, output_clock=clock+1, holder_address=address,
                               computed_Flag1=0, computed_Flag2=int(stage == 2),
                               computed_Workspace_Flag2=expected_wf2,
                               output_signal3_Info=1 if address <= 5 else None))
    cells = 3*p.Q
    boundary = p.Q
    reference = np.zeros((candidate.W, cells), dtype=bool)
    candidate.set_field(reference, 'addr', np.arange(cells) % p.Q)
    candidate.set_field(reference, 'age', p.age_code(p.T_sig))
    probe = reference.copy()
    changed = []
    for address in range(1, 6):
        slot = 3-address
        row = candidate.row['ml', slot+2]
        probe[row, boundary+address] = True
        changed.append(dict(holder_address=address, raw_row=row, logical_primary=3))
    execution = copy.copy(candidate)
    execution.rom = np.pad(candidate.rom, ((0, (1 << p.k)-p.Q), (0, 0)))
    inputs = np.stack([reference, probe])
    outputs = []
    for stage in range(3):
        reference = execution.step_numpy(reference)
        probe = execution.step_numpy(probe)
        for address in range(2, 8):
            pos = boundary+address
            assert candidate.field(probe, 'addr')[pos] == address
            assert candidate.field(probe, 'age')[pos] == p.age_code(p.T_sig+stage+1)
            assert candidate.field(probe, 'f1')[pos] == 0
            assert candidate.field(probe, 'f2')[pos] == int(stage == 2)
            assert candidate.field(probe, 'wf2')[pos] == int(stage >= 1 and address < 5)
            assert candidate.field(reference, 'f2')[pos] == candidate.field(reference, 'wf2')[pos] == 0
        for address in range(2, 6):
            assert probe[candidate.row['info', 3-address+2], boundary+address]
        outputs.append(np.stack([reference, probe]))
    asset = out / 'SP4_boundary_signal_restart_inputs.npz'
    np.savez_compressed(asset, initial=inputs, computed=np.stack(outputs), boundary=boundary)
    dependencies = ('SP4_program_build.json', 'SP4_maintenance_certificate.json',
                    'SP4_autonomy_certificate.json', 'SP4_shifted_halfline_certificate.json',
                    'SP4_coupled_boundary_core_certificate.json', 'SP4_boundary_prefix_modules_certificate.json')
    result = dict(
        proposal='SP4', proposed_rule_change=True, active_G17_modified=False,
        proposed_candidate_sha256=candidate.digest(), proposed_netlist_sha256=candidate.comp.digest,
        proposal_source_sha256=digest(Path(proposed.__file__)), checker_sha256=digest(Path(__file__)),
        full_rule_sha256=digest(ROOT / 'gacsca/rule_g.py'),
        selection_source_sha256=digest(ROOT / 'Report/proofs/prefix_selection.py'),
        transport_checker_sha256=digest(ROOT / 'Report/proofs/check_fast_mail_proposal.py'),
        dominant_bit_helper_sha256=digest(ROOT / 'Report/proofs/check_shifted_halfline.py'),
        actual_generated_source_sha256=hashlib.sha256(source.encode()).hexdigest(),
        input_asset_sha256=digest(asset), initial_clock=p.T_sig,
        changed_field='ml', changed_logical_primary=3, changed_copy_holders=list(range(1, 6)),
        changed_raw_bits=changed, first_output_signal3_Info=1,
        second_output_Workspace_Flag2_healthy_addresses=[2, 3, 4],
        third_output_Flag2_healthy_addresses=list(range(2, 8)),
        computed_geometry_and_Flag1_remain_pristine=True,
        symbolic_constant_and_free_other_data_cases=len(checks), symbolic_cases=checks,
        full_NumPy_updates=6, initial_NumPy_reference_is_operational_snapshot=False,
        universal_embedding_in_operational_snapshot_is_local_identity=True,
        initial_far_whole_words_can_equal_pristine_snapshot=True,
        initially_unchanged_frozen_programme_frame=True,
        proof_receipt_sha256={name:digest(out / name) for name in dependencies},
        reachable_after_J47_established=False, physical_real_core_reachability_established=False,
        independent_noise_unreliability_established=False, global_reliability_established=False,
        scope='local signal-restart counterexample with free other data; finite NumPy support uses flat legal-clock reference, no physical reachability or iid claim')
    (out / 'SP4_boundary_signal_restart_certificate.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(dict(symbolic_cases=len(checks), changed_raw_ML_bits=5,
                          signal_Info_after_updates=1, Workspace_Flag2_after_updates=2,
                          Flag2_after_updates=3)), flush=True)


if __name__ == '__main__':
    main()
