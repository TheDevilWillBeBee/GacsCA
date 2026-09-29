"""Conditional full-lower-ring embedding of the recorded noisy commit.

Combines descriptor identities and existing physical trajectory audits. The NPZ
is a diagnostic witness/patch, never installed into an evolving physical world.
No claim of a new literal full-Q-squared execution is made.
"""
import argparse
import json
from pathlib import Path
import resource
import time
import numpy as np

from gacsca.fixed_rule import retimed_holder_rule as f, retimed_holder_core as c
from gacsca.fixed_rule import retimed_holder_program as p
from gacsca.fixed_rule import retimed_holder_literal_cone as cone
from gacsca.fixed_rule import retimed_holder_contextual_flags as adapter
from experiments.fixed_rule.audit_retimed_holder_contextual_recovery import GlobalProcedures, FIELDS
from experiments.fixed_rule.audit_retimed_holder_burst_recovery import NAMES, MAIL
from experiments.fixed_rule.audit_retimed_holder_prefix_embedding import sha


INPUTS = (
    'late_confinement_v1', 'late_procedure_image_v1', 'empty_tail_interior_v1',
    'prefix_dependence_v2', 'prefix_embedding_v3',
    'wide_burst_v1', 'wide_burst_audit_v1',
    'wide_recovery_v1', 'wide_recovery_audit_v2',
    'wide_macrostep_v1', 'wide_macrostep_audit_v1',
    'mail_schedule_v1', 'signal_schedule_v1')


def guard_empty_tails(words, colonies, allowed_tail_colonies):
    assert words.dtype == np.uint64 and words.shape == (colonies*f.Q, len(NAMES))
    controls = [NAMES.index(name) for name in ('head', *c.CONTROL)]
    found = []
    for col in range(colonies):
        tail = words[col*f.Q+len(p.base_rom()):(col+1)*f.Q, :][:, controls]
        if np.any(tail):
            assert col in allowed_tail_colonies, ('unexpected tail controller', col)
            found.append(col)
    return found


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    out = Path(parser.parse_args().output)
    artifact = out.with_suffix('.npz')
    if out.exists() or artifact.exists():
        raise FileExistsError(out)
    started = time.perf_counter()
    root = Path('figs/fixed_rule')
    paths = {name: root/('retimed_holder_'+name+'.json') for name in INPUTS}
    docs = {name: json.loads(path.read_text()) for name, path in paths.items()}
    for name, doc in docs.items():
        assert doc.get('passed', doc.get('completed')) is True, name
        for source, expected in {**doc.get('source_sha256', {}), **doc.get('input_sha256', {}), **doc.get('external_bank_sha256', {})}.items():
            assert sha(source) == expected, source
    for name in ('wide_burst_v1', 'wide_recovery_v1', 'wide_macrostep_v1'):
        assert sha(paths[name].with_suffix('.npz')) == docs[name]['artifact_sha256']
    for audit, run in (('wide_burst_audit_v1', 'wide_burst_v1'),
                       ('wide_recovery_audit_v2', 'wide_recovery_v1'),
                       ('wide_macrostep_audit_v1', 'wide_macrostep_v1')):
        assert docs[audit]['source_receipt_sha256'] == sha(paths[run])
        assert docs[audit]['artifact_sha256'] == docs[run]['artifact_sha256']
    burst, recovery, macro = (docs[name] for name in ('wide_burst_v1', 'wide_recovery_v1', 'wide_macrostep_v1'))
    assert recovery['source_receipt_sha256'] == sha(paths['wide_burst_v1'])
    assert macro['source_receipt_sha256'] == sha(paths['wide_recovery_v1'])
    assert docs['wide_recovery_audit_v2']['all_mail_outputs_zero']
    assert docs['wide_macrostep_audit_v1']['all_physical_trace_events_checked'] == macro['physical_trace_events']
    assert docs['wide_macrostep_audit_v1']['complete_checkpoints_verified'] == 6
    assert docs['signal_schedule_v1']['no_SEND_during_or_after_forcing']
    assert not next(row for row in docs['mail_schedule_v1']['phases'] if row['name'] == 'final_evaluation')['packets']
    assert docs['late_confinement_v1']['complete_state_join_requires_zero_input_and_output_mail']
    assert docs['late_procedure_image_v1']['passed']
    interior = docs['empty_tail_interior_v1']
    assert interior['complete_zero_controller_copies'] == 45
    assert interior['zero_logical_controller_sites'] == [-1, 0, 1]
    assert interior['zero_first_marker_sites'] == [0]
    assert not np.any(cone.rom()[len(p.base_rom()):, c.STATIC.index('first')])

    center = burst['center_colony']
    assert (center, burst['colonies']) == (36, 73)
    affected = {36, 37}
    raw_procedure = [f.COL['s2_'+name] for name in NAMES]
    with np.load(paths['wide_burst_v1'].with_suffix('.npz'), allow_pickle=False) as z:
        state = {name: z['final_background_'+name] for name in FIELDS}
        actual_view = adapter.View(state, z['final_positions'], z['final_values'])
        healthy_view = adapter.View(state)
        actual = GlobalProcedures(actual_view)  # Full raw geometry/image/zero-mail checks.
        initial_age = int(state['age'])
        assert initial_age == burst['burst_initial_age']+34
        assert f.RESET_AGES[4] < initial_age < f.ACTIVE_ENDS[4]
        assert all(not value for col, value in enumerate(actual.flags) if col not in affected)
        changed_procedure_colonies = []
        for col in range(73):
            sites = np.arange(col*f.Q, (col+1)*f.Q)
            healthy = healthy_view.cells(sites)
            words = actual.words[col*f.Q:(col+1)*f.Q]
            if np.any(words != healthy[:, raw_procedure]):
                changed_procedure_colonies.append(col)
                assert col in affected, ('initial difference outside enclosed group', col)
            np.testing.assert_array_equal(actual_view.cells(sites)[:, f.COL['signal']], healthy[:, f.COL['signal']])
            healthy_controls = healthy[:, [f.COL['s2_'+name] for name in ('head', *c.CONTROL)]]
            assert not np.any(healthy_controls[len(p.base_rom()):])
        ordinary = guard_empty_tails(actual.words, 73, {36})
        assert ordinary == [36] and changed_procedure_colonies == [36]
        upper = z['upper_context'].copy()
        selected = z['selected_upper_positions'].copy()
        schedule = z['schedule']
        assert len(schedule) == 8404 and np.all((1 <= schedule[:, 0]) & (schedule[:, 0] <= 32))
        assert np.all((0 <= schedule[:, 1]) & (schedule[:, 1] < f.Q))
    del actual

    # Every first-34-tick difference lies in this conservative ordinary cone.
    radius = max(map(abs, f.NEIGHBORHOOD))
    patch = (35*f.Q, 39*f.Q)
    early_support = (36*f.Q-34*radius, 37*f.Q+34*radius)
    later_support = (36*f.Q-2, 38*f.Q+2)
    for lo, hi in (early_support, later_support):
        assert patch[0]+radius <= lo < hi <= patch[1]-radius
    safe = set(docs['prefix_embedding_v3']['complete_raw_safe_colonies'])
    assert set(range(34, 40)) <= safe
    assert docs['prefix_dependence_v2']['initial_Signals_zero_required']
    assert docs['prefix_dependence_v2']['late_interval'][1] == f.U-1

    with np.load(paths['wide_macrostep_v1'].with_suffix('.npz'), allow_pickle=False) as z:
        index = next(i for i, row in enumerate(macro['checkpoints']) if row['time'] == f.U)
        committed = z[f'checkpoint{index}_words']
        signals = z[f'checkpoint{index}_signals']
        assert committed.shape == (73*f.Q, len(NAMES)) and not np.any(committed[:, MAIL])
        assert not guard_empty_tails(committed, 73, set())
        decoded = committed[np.arange(73)[:, None]*f.Q+np.array(p.layout().info), NAMES.index('data')]
        np.testing.assert_array_equal(decoded, z['decoded_raw'])
        # Independent represented-step comparison only: no evolving lower state
        # receives this diagnostic full upper array.
        healthy_upper = cone.step(upper)
        np.testing.assert_array_equal(z['expected_decoded_raw'][35:39], healthy_upper[selected[35:39]])
        full_committed_Info = healthy_upper.copy()
        full_committed_Info[selected[35:39]] = decoded[35:39]
        bad = np.flatnonzero(np.any(full_committed_Info != healthy_upper, axis=1))
        assert bad.tolist() == [int(selected[37])] == [9566]
        assert not np.any(full_committed_Info[bad[0]])
        differences = full_committed_Info[bad[0]] != healthy_upper[bad[0]]
        raw_differences = int(np.count_nonzero(differences))
        mutable_differences = int(np.count_nonzero(differences[len(f.STATIC):]))
        assert (raw_differences, mutable_differences) == (26, 12)
        np.savez_compressed(artifact,
                            full_committed_Info=full_committed_Info,
                            healthy_upper_successor=healthy_upper,
                            patch_logical_procedures=committed[patch[0]:patch[1]],
                            patch_raw_Signals=signals[patch[0]:patch[1]],
                            selected_upper_positions=selected)

    result = dict(passed=True, conditional_full_lower_ring_commit_embedding=True,
                  full_physical_ring_sites=f.Q*f.Q, full_lower_colonies=f.Q,
                  selected_unfiltered_fault_marks=8404,
                  physical_patch_interval=list(patch), early_difference_support=list(early_support),
                  late_difference_support=list(later_support),
                  initial_changed_procedure_colonies=changed_procedure_colonies,
                  only_initial_exceptional_controller_tail=36,
                  ordinary_tail_interior_sites_per_colony=f.Q-len(p.base_rom())-2,
                  ordinary_tail_edge_sites_per_colony=2,
                  interior_closure_uses_only_three_empty_logical_records=True,
                  zero_mail_premise='Recovery scalar audit checks every tick. Macro literal '
                                   'Replay asserts zero outputs; guarded transport moves only '
                                   'controller words; inactive intervals retain procedures; '
                                   'commit changes only Data and its complete native output '
                                   'is compared. All existing audit source hashes are checked.',
                  full_committed_bad_upper_positions=bad.tolist(),
                  raw_differences=raw_differences, mutable_differences=mutable_differences,
                  commit_local_time=f.U,
                  commit_absolute_time=burst['entry_physical_time']+f.U,
                  descriptor_sha256=f.self_description().digest(),
                  input_sha256={str(path): sha(path) for path in paths.values()},
                  source_sha256={str(path): sha(path) for path in (
                      Path(__file__), Path(f.__file__), Path(c.__file__), Path(p.__file__),
                      Path(cone.__file__), Path(adapter.__file__),
                      Path('experiments/fixed_rule/audit_retimed_holder_contextual_recovery.py'),
                      Path('experiments/fixed_rule/audit_retimed_holder_contextual_macrostep.py'))},
                  artifact_sha256=sha(artifact), seconds=time.perf_counter()-started,
                  host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  conclusion='Under the checked noiseless physical refinements and existing '
                             'independent trajectory audits, glue the actual 4-colony physical '
                             'patch into the full noiseless lower ring. Equal complete radius-7 '
                             'collars make this a trajectory of the same local rule with the '
                             'same fault marks, through commit. Uniqueness gives the full-ring '
                             'selected noisy commit; exactly upper position9566 commits zero.',
                  limitation='Conditional proof composition and diagnostic patch, not a new '
                             'literal billion-cell GPU execution or a proof-assistant theorem. '
                             'No subsequent full-ring repair, general amplification, fresh '
                             'persistent noise or threshold claim is made here.')
    out.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    main()
