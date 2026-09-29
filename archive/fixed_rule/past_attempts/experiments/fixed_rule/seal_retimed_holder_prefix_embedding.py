"""Seal the conditional prefix/cone evidence without changing prior artifacts."""
import json
from pathlib import Path
from experiments.fixed_rule.audit_retimed_holder_prefix_embedding import sha


def main():
    root = Path.cwd()
    fig = Path('figs/fixed_rule')
    out = fig/'retimed_holder_prefix_embedding_evidence_v1.json'
    if out.exists():
        raise FileExistsError(out)
    prior_path = fig/'retimed_holder_wide_repair_evidence_v1.json'
    prior = json.loads(prior_path.read_text())
    files = dict(prior['files'])
    for path, expected in files.items():
        assert sha(path) == expected, path
    assert len(files) == 211

    def bind(path, expected=None):
        path = Path(path)
        if path.is_absolute():
            path = path.relative_to(root)
        actual = sha(path)
        assert expected is None or actual == expected, str(path)
        files[str(path)] = actual

    bind(prior_path)
    additions = [Path(__file__), Path('Report/fixed_rule/PREFIX_EMBEDDING.md'),
                 Path('Report/fixed_rule/STATUS_BEFORE_PREFIX_EMBEDDING_20260927.md')]
    additions += [Path('experiments/fixed_rule')/name for name in (
        'certify_retimed_holder_prefix_dependence.py',
        'audit_retimed_holder_prefix_embedding.py',
        'certify_retimed_holder_embedding_cones.py')]
    additions += [Path('tests/fixed_rule')/name for name in (
        'test_retimed_holder_prefix_dependence.py', 'test_retimed_holder_embedding_cones.py')]
    for pattern in ('retimed_holder_prefix_dependence*', 'retimed_holder_prefix_embedding*',
                    'retimed_holder_embedding_cones*'):
        additions += list(fig.glob(pattern))
    for path in additions:
        bind(path)
    accepted = ('prefix_dependence_v2', 'prefix_embedding_v3', 'embedding_cones_v2')
    external_banks = {}
    for name in accepted:
        path = fig/('retimed_holder_'+name+'.json')
        doc = json.loads(path.read_text())
        assert doc['passed'] is True and doc['descriptor_sha256'] == prior['descriptor_sha256']
        for source, expected in {**doc['source_sha256'], **doc.get('input_sha256', {})}.items():
            bind(source, expected)
        for bank, expected in doc.get('external_bank_sha256', {}).items():
            assert sha(bank) == expected
            external_banks[bank] = expected
        watch = json.loads(path.with_name(path.stem+'_watch.json').read_text())
        assert watch['returncode'] == 0 and watch['termination_reason'] is None
    tests = json.loads((fig/'retimed_holder_prefix_embedding_tests_v3_watch.json').read_text())
    assert tests['returncode'] == 0 and tests['termination_reason'] is None
    for name in ('prefix_embedding_v1', 'prefix_embedding_v2'):
        watch = json.loads((fig/('retimed_holder_'+name+'_watch.json')).read_text())
        assert watch['returncode'] == -9 and watch['termination_reason'] == 'RSS threshold exceeded'
    assert json.loads((fig/'retimed_holder_embedding_cones_v1_watch.json').read_text())['returncode'] == 1
    first = json.loads((fig/'retimed_holder_prefix_dependence_v1.json').read_text())
    expected = first['source_sha256'][str(root/'experiments/fixed_rule/certify_retimed_holder_prefix_dependence.py')]
    assert sha(fig/'retimed_holder_prefix_dependence_v1_source.py') == expected
    result = dict(evidence_integrity_verified=True, accepted_conditional_checks_passed=True,
                  prior_evidence_files_verified=211, files=dict(sorted(files.items())),
                  external_bank_sha256=external_banks,
                  descriptor_sha256=prior['descriptor_sha256'], ROM_sha256=prior['ROM_sha256'],
                  accepted_receipts=list(accepted), focused_tests_passed=8,
                  initial_matching_raw_colonies=57,
                  matching_raw_colonies_after_116418_ticks=list(range(33, 40)),
                  initial_Signals_zero_required=True,
                  later_nonzero_window_Signal_colonies=[0, 1, 2, 70, 71, 72],
                  superseded_passing_receipt='prefix_dependence_v1: omitted initial-Signal restriction',
                  preserved_RSS_terminations=2, preserved_rejected_global_Signal_check=1,
                  full_lower_Q_noisy_commit_embedded=False,
                  persistent_cut_proved=False, full_project_goal_complete=False,
                  scope='Conditional descriptor-semantics noiseless prefix embedding, '
                        'complete inherited entry matching and a finite radius-seven noisy '
                        'cone. Relies on existing physical refinements; no new literal '
                        'GPU-prefix replay. Local cut premises checked only at a saved '
                        'time. No final noisy commit, unaffected full-ring exterior, '
                        'amplification or threshold proof.')
    with out.open('x') as stream:
        stream.write(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(dict(output=str(out), verified_files=len(files), prior_files_unchanged=211,
                          external_banks_verified=len(external_banks))))


if __name__ == '__main__':
    main()
