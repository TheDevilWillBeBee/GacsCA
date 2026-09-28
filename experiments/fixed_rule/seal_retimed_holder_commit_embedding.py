"""Seal the conditional full-ring selected noisy-commit evidence."""
import json
from pathlib import Path
from experiments.fixed_rule.audit_retimed_holder_prefix_embedding import sha


def main():
    root, fig = Path.cwd(), Path('figs/fixed_rule')
    out = fig/'retimed_holder_commit_embedding_evidence_v1.json'
    if out.exists():
        raise FileExistsError(out)
    prior_path = fig/'retimed_holder_prefix_embedding_evidence_v1.json'
    prior = json.loads(prior_path.read_text())
    files = dict(prior['files'])
    assert len(files) == 260
    for path, expected in files.items():
        assert sha(path) == expected, path
    external = prior['external_bank_sha256']
    for path, expected in external.items():
        assert sha(path) == expected, path

    def bind(path, expected=None):
        path = Path(path)
        if path.is_absolute():
            path = path.relative_to(root)
        actual = sha(path)
        assert expected is None or actual == expected, str(path)
        files[str(path)] = actual

    additions = [prior_path, Path(__file__),
                 Path('Report/fixed_rule/NOISY_COMMIT_EMBEDDING.md'),
                 Path('Report/fixed_rule/STATUS_BEFORE_NOISY_COMMIT_EMBEDDING_20260927.md')]
    additions += [Path('experiments/fixed_rule')/name for name in (
        'certify_retimed_holder_late_confinement.py',
        'certify_retimed_holder_late_procedure_image.py',
        'certify_retimed_holder_empty_tail_interior.py',
        'join_retimed_holder_noisy_commit_embedding.py')]
    additions += [Path('tests/fixed_rule')/name for name in (
        'test_retimed_holder_late_confinement.py',
        'test_retimed_holder_late_procedure_image.py',
        'test_retimed_holder_empty_tail_interior.py',
        'test_retimed_holder_gluing.py')]
    for prefix in ('late_confinement', 'late_procedure_image', 'empty_tail_interior',
                   'noisy_commit_embedding', 'gluing_tests', 'commit_gluing_tests'):
        additions += list(fig.glob('retimed_holder_'+prefix+'*'))
    for path in additions:
        bind(path)
    accepted = ('late_confinement_v1', 'late_procedure_image_v1',
                'empty_tail_interior_v1', 'noisy_commit_embedding_v2')
    for name in accepted:
        path = fig/('retimed_holder_'+name+'.json')
        doc = json.loads(path.read_text())
        assert doc['passed'] and doc['descriptor_sha256'] == prior['descriptor_sha256']
        for source, expected in {**doc['source_sha256'], **doc.get('input_sha256', {})}.items():
            bind(source, expected)
        if 'artifact_sha256' in doc:
            bind(path.with_suffix('.npz'), doc['artifact_sha256'])
        watch = json.loads(path.with_name(path.stem+'_watch.json').read_text())
        assert watch['returncode'] == 0 and watch['termination_reason'] is None
    tests = json.loads((fig/'retimed_holder_commit_gluing_tests_v1_watch.json').read_text())
    assert tests['returncode'] == 0 and tests['termination_reason'] is None
    assert 'Ran 13 tests' in (fig/'retimed_holder_commit_gluing_tests_v1.log').read_text()
    first = json.loads((fig/'retimed_holder_noisy_commit_embedding_v1.json').read_text())
    final = json.loads((fig/'retimed_holder_noisy_commit_embedding_v2.json').read_text())
    assert first['artifact_sha256'] == final['artifact_sha256']
    source = str(root/'experiments/fixed_rule/join_retimed_holder_noisy_commit_embedding.py')
    assert sha(fig/'retimed_holder_noisy_commit_embedding_v1_source.py') == first['source_sha256'][source]
    result = dict(evidence_integrity_verified=True, conditional_commit_embedding_checks_passed=True,
                  prior_evidence_files_verified=260, files=dict(sorted(files.items())),
                  external_bank_sha256=external, accepted_receipts=list(accepted),
                  descriptor_sha256=prior['descriptor_sha256'], ROM_sha256=prior['ROM_sha256'],
                  focused_tests_passed=13, full_lower_ring_physical_sites=1073741824,
                  selected_fault_marks=8404, full_committed_bad_upper_positions=[9566],
                  wrong_Info_raw_words=26, wrong_Info_mutable_words=12,
                  full_ring_selected_noisy_commit_embedded_under_refinements=True,
                  zero_mail_on_recorded_trajectory_is_an_explicit_premise=True,
                  new_literal_full_ring_GPU_execution=False,
                  full_ring_subsequent_repair_embedded=False,
                  full_project_goal_complete=False,
                  scope='Conditional descriptor-semantics gluing of the audited selected '
                        'noisy physical window into the complete lower ring through commit. '
                        'Complete-controller images, empty-tail invariance and shared Signals '
                        'are checked symbolically; no-mail trajectory and noiseless prefix '
                        'refinements are explicit audited premises. No subsequent full-ring '
                        'repair, general amplification, persistent-noise or threshold claim.')
    with out.open('x') as stream:
        stream.write(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(dict(output=str(out), verified_files=len(files), prior_files_unchanged=260,
                          external_banks_verified=len(external))))


if __name__ == '__main__':
    main()
