"""Verify frozen receipts and seal the selected 73-colony evidence chain.

Read-only except for exclusive creation of the final evidence index. Run from
the project root. This checks recorded evidence, not a new physical trajectory.
"""
import hashlib
import json
from pathlib import Path


ROOT = Path.cwd()
FIG = Path('figs/fixed_rule')


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def main():
    prior_path = FIG / 'retimed_holder_wide_repair_pending_recovery_evidence_v1.json'
    prior = read(prior_path)
    files = dict(prior['files'])
    assert len(files) == 186
    for path, expected in files.items():
        assert digest(path) == expected, path

    additions = [prior_path, Path(__file__).resolve().relative_to(ROOT)]
    additions += list(FIG.glob('retimed_holder_colony_cut*'))
    additions += [FIG / ('retimed_holder_wide_recovery_audit_v2' + suffix)
                  for suffix in ('.json', '.log', '_watch.json')]
    additions += [Path('Report/fixed_rule') / name for name in (
        'WIDE_CONTEXTUAL_REPAIR.md', 'COLONY_CUT.md',
        'STATUS_BEFORE_VERIFIED_WIDE_REPAIR_20260927.md')]
    additions += [Path('experiments/fixed_rule') / name for name in (
        'certify_retimed_holder_colony_cut.py',
        'retimed_holder_symbolic_bits.py',
        'retimed_holder_colony_cut_counterexamples.py')]
    additions += [Path('tests/fixed_rule/test_retimed_holder_colony_cut.py')]
    for path in additions:
        files[str(path)] = digest(path)

    accepted = [
        'wide_burst_audit_v1', 'wide_recovery_audit_v2',
        'wide_macrostep_audit_v1', 'wide_next_periods_audit_v1',
        'wide_reset_entry_v1', 'wide_upper_alignment_v1',
        'colony_cut_v2', 'colony_cut_counterexamples_v1',
    ]
    for suffix in accepted:
        path = FIG / ('retimed_holder_' + suffix + '.json')
        receipt = read(path)
        assert receipt['passed'] is True, path
        watch = read(path.with_name(path.stem + '_watch.json'))
        assert watch['returncode'] == 0 and watch['termination_reason'] is None, path
        for source, expected in receipt.get('source_sha256', {}).items():
            relative = Path(source)
            if relative.is_absolute():
                relative = relative.relative_to(ROOT)
            assert digest(relative) == expected, source
            files[str(relative)] = expected
    recovery = read(FIG / 'retimed_holder_wide_recovery_audit_v2.json')
    for field, suffix in [('source_receipt_sha256', '.json'), ('artifact_sha256', '.npz')]:
        assert recovery[field] == digest(FIG / ('retimed_holder_wide_recovery_v1' + suffix))
    cut = read(FIG / 'retimed_holder_colony_cut_counterexamples_v1.json')
    assert cut['artifact_sha256'] == digest(FIG / 'retimed_holder_colony_cut_counterexamples_v1.npz')
    assert read(FIG / 'retimed_holder_colony_cut_v2.json')['descriptor_sha256'] == prior['descriptor_sha256']
    assert read(FIG / 'retimed_holder_colony_cut_signal_probe_v1.json')['passed'] is True
    assert read(FIG / 'retimed_holder_colony_cut_tests_v1_watch.json')['returncode'] == 0
    assert read(FIG / 'retimed_holder_colony_cut_v1_watch.json')['returncode'] == 1

    result = {key: prior[key] for key in (
        'descriptor_sha256', 'ROM_sha256', 'physical_lower_colonies',
        'central_upper_cells_matching_full_colony',
        'decoded_bad_colonies_by_additional_period',
        'healthy_bank_differences_after_periods_2_3', 'retained_nonMEM_words')}
    result.update(
        evidence_integrity_verified=True,
        selected_trajectory_audit_chain_passed=True,
        prior_evidence_files_verified=len(prior['files']),
        accepted_receipts=accepted,
        final_recovery_ticks_replayed=recovery['all_quiet_ticks_replayed'],
        new_colony_cut_tests_passed=5,
        colony_cut_scope='Conditional one-step descriptor certificate; hypotheses are not proved invariant.',
        full_lower_Q_noisy_embedding_proved=False,
        full_project_goal_complete=False,
        files=dict(sorted(files.items())),
        scope='Selected 73-colony actual physical trajectory with independent burst, '
              'recovery, commit, normalization and endpoint audits. Long later quiet '
              'intervals use conditional endpoint identities, not literal replay of '
              'every tick. Central 17 upper raw states match the complete upper colony. '
              'No full lower-Q noisy boundary, threshold or amplification claim. '
              'Earlier failed/incomplete receipts stay preserved in the prior index.')
    out = FIG / 'retimed_holder_wide_repair_evidence_v1.json'
    with out.open('x') as stream:
        stream.write(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'output': str(out), 'verified_files': len(files),
                      'prior_files_unchanged': len(prior['files'])}))


if __name__ == '__main__':
    main()
