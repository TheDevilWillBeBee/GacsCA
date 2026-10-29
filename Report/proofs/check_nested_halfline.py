#!/usr/bin/env python3
"""Conditional boundary modules and support arithmetic for SP4's J42.

The two-level trajectory induction is separate in ROBUSTNESS.md. This
checker proves neither a higher-island eroder nor a positive noise rate.
Its symbolic substitutions use J38a's quiet geometry/flag premise, not
the conclusion of the proposed trajectory induction.
"""
import hashlib
import json
from pathlib import Path
import sys
from types import FunctionType, SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from gacsca import rule_g
from gacsca.netlist import Net, Compiled, const_word, mixed_age_increment
import proposed_sparse_prefix448 as proposed
import prefix_selection as selection
import check_fast_mail_proposal as transport
from check_sparse_prefix448_autonomy import ancestors


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    candidate = proposed.load_artifact()
    p = candidate.p
    out = ROOT / 'figs/robustness'
    namespace = dict(transport.__dict__, proposed_maintenance=selection.proposed_build)
    factory = FunctionType(transport.concrete_sparse_net.__code__, namespace)
    actual, source = factory(p, proposed.dependency_table(p))
    assert Compiled(actual).digest == candidate.comp.digest
    # This changes only input substitutions and the already-proved symbolic
    # majority simplification. The generated transition source is identical.
    maintenance, _ = selection.proposed_build(symbolic=True)
    rows = []
    for address in range(12):
        class BoundNet(Net):
            def input(self, name):
                if name[0] == 'x':
                    _, offset, field, bit = name
                    position = address+offset
                    if field == 'addr' and position >= 0:
                        return ((position % p.Q) >> bit) & 1
                    if field == 'age' and position >= 0:
                        return super().input(('common_clock', bit))
                    if field in ('f1', 'f2', 'wf1', 'wf2') and 0 <= position < p.Q:
                        return 0
                return super().input(name)

        build_namespace = dict(rule_g.__dict__)
        build_namespace.update(Net=BoundNet, maintenance=SimpleNamespace(build=maintenance),
                               OFFSETS=tuple(range(-12, 13)),
                               sparse_controls=transport.sparse_controls,
                               sparse_table=proposed.dependency_table(p))
        exec(compile(source, '<same SP4 source, quiet right input substitutions>', 'exec'), build_namespace)
        bounded = build_namespace['build'](p)
        assert [bounded.outputs['y', 'addr', bit] for bit in range(p.k)] == const_word(address, p.k)
        common = [bounded.input(('common_clock', bit)) for bit in range(p.m)]
        assert [bounded.outputs['y', 'age', bit] for bit in range(p.m)] == mixed_age_increment(
            bounded, common, p.PB, p.R, p.nb)
        assert bounded.outputs['y', 'f1', 0] == bounded.outputs['y', 'f2', 0] == 0
        checked = []
        for slot in proposed.SLOTS:
            logical = address+slot
            if logical < 3:
                continue
            for field in ('info', 'hold', 'ml'):
                width = proposed.logical_width(field, p)
                assert width == 1
                name = ('y', field, slot+2)
                support = ancestors(bounded, bounded.outputs[name])
                assert all(inp[0] != 'I' for inp in support), (address, name)
                assert all(inp[0] != 'x' or address+inp[1] >= 0 for inp in support), (address, name)
                checked.append(dict(field=field, logical_primary=logical, copy_slot=slot,
                                    input_positions=sorted({address+inp[1] for inp in support if inp[0] == 'x'})))
        rows.append(dict(holder_address=address, conditional_copy_outputs=checked))
    count = sum(len(row['conditional_copy_outputs']) for row in rows)
    assert count == 135

    deps = proposed.dependency_table(p)
    assert min(off for row in deps for off in row['offsets']) == -12
    assert max(off for row in deps for off in row['offsets']) == 12
    # Once a source colony index is nonnegative, every part of its capture
    # path stays on the physical right: layout/control footprint >=47.
    capture_margin = min(row['address']-12 for row in deps)
    assert capture_margin == 47
    frame = [p.lo-p.H-2, p.hi-1+(p.fronts-1)*p.delta+2]
    frame_inputs = [frame[0]-12, frame[1]+12]
    assert frame == [36, 411] and frame_inputs == [24, 423]
    assert frame_inputs[0] >= 12 and frame_inputs[1] < p.Q
    horizon = 15710
    frozen = 9635
    active_start_max = p.T_wf+2*p.Q-1
    active_horizon_end = active_start_max+horizon
    assert active_horizon_end == 41950 < p.U-1
    # All relevant upper courier updates occur after the final fast-mail
    # stage/capture and before commit. The literal rule is unit speed here.
    gather_windows = [[g*p.Q+1, g*p.Q+12*(p.Q//8)] for g in p.gathers_q]
    assert max(b for a,b in gather_windows) < frozen
    _, left_load, right_load = p.courier_ticks()
    paths = []
    for field, origin, target, tick in (('ml', p.lo, 3, left_load),
                                       ('mr', p.hi-1, p.Q-3, right_load)):
        assert tick+1+abs(target-origin) == p.T_sig
        holders = [min(origin, target)-2, max(origin, target)+2]
        assert 0 <= holders[0] <= holders[1] < p.Q
        paths.append(dict(field=field, origin=origin, target=target,
                          load_input_clock=tick, holder_span=holders))

    dependencies = ('SP4_program_build.json', 'SP4_symbolic_schedule.json',
                    'SP4_front_certificate.json', 'SP4_localization_certificate.json',
                    'SP4_operational_certificate.json', 'SP4_autonomy_certificate.json',
                    'operational_halfline_certificate.json')
    result = dict(
        proposal='SP4', proposed_rule_change=True, active_G17_modified=False,
        proposed_candidate_sha256=candidate.digest(), proposed_netlist_sha256=candidate.comp.digest,
        proposal_source_sha256=digest(Path(proposed.__file__)), checker_sha256=digest(Path(__file__)),
        full_rule_sha256=digest(ROOT / 'gacsca/rule_g.py'),
        selection_source_sha256=digest(ROOT / 'Report/proofs/prefix_selection.py'),
        transport_checker_sha256=digest(ROOT / 'Report/proofs/check_fast_mail_proposal.py'),
        actual_generated_source_sha256=hashlib.sha256(source.encode()).hexdigest(),
        symbolic_clock_bits_free=p.m, conditional_boundary_holders=rows,
        conditional_boundary_copy_outputs_checked=count,
        substitutions='right canonical geometry, common clock; own upper colony four flags zero; outside-left raw states free',
        interior_exact_projection_first_upper_index=12,
        capture_left_margin=capture_margin, programme_holder_frame=frame,
        programme_input_frame=frame_inputs, threatened_clock_interval=[frozen, active_horizon_end],
        final_fast_mail_input_clock=max(b for a,b in gather_windows), signal_courier_paths=paths,
        upper_horizon=horizon, physical_horizon=horizon*p.U,
        proof_receipt_sha256={name:digest(out / name) for name in dependencies},
        trajectory_induction_is_separate=True, right_real_level1_errors_covered=False,
        all_level_projection_established=False, universal_higher_island_repair_established=False,
        global_reliability_established=False,
        scope='conditional boundary-copy identities and private programme/capture supports for the finite two-level J42 barrier')
    (out / 'SP4_nested_halfline_certificate.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(dict(conditional_boundary_copy_outputs=count, capture_margin=capture_margin,
                          upper_horizon=horizon, physical_horizon=horizon*p.U)), flush=True)


if __name__ == '__main__':
    main()
