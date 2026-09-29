"""Seal the selected conditional full-ring repair and unchanged prior evidence."""
import json
from pathlib import Path
from experiments.fixed_rule.audit_retimed_holder_prefix_embedding import sha


def main():
    root, fig = Path.cwd(), Path('figs/fixed_rule')
    out = fig/'retimed_holder_full_ring_repair_evidence_v1.json'
    if out.exists():
        raise FileExistsError(out)
    prior_path = fig/'retimed_holder_commit_embedding_evidence_v1.json'
    prior = json.loads(prior_path.read_text())
    files = dict(prior['files'])
    assert len(files) == 298
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
                 Path('Report/fixed_rule/FULL_RING_REPAIR.md'),
                 Path('Report/fixed_rule/STATUS_BEFORE_FULL_RING_REPAIR_20260927.md')]
    additions += [Path('experiments/fixed_rule')/name for name in (
        'certify_retimed_holder_normalization_prefix.py',
        'join_retimed_holder_full_ring_repair.py')]
    additions += [Path('tests/fixed_rule')/name for name in (
        'test_retimed_holder_normalization_prefix.py',
        'test_retimed_holder_full_ring_repair_join.py')]
    for prefix in ('normalization_prefix', 'full_ring_repair'):
        additions += list(fig.glob('retimed_holder_'+prefix+'*'))
    for path in additions:
        bind(path)
    accepted = ('normalization_prefix_v1', 'full_ring_repair_v1')
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
    tests = json.loads((fig/'retimed_holder_full_ring_repair_tests_v1_watch.json').read_text())
    assert tests['returncode'] == 0 and tests['termination_reason'] is None
    assert 'Ran 7 tests' in (fig/'retimed_holder_full_ring_repair_tests_v1.log').read_text()
    join = json.loads((fig/'retimed_holder_full_ring_repair_v1.json').read_text())
    assert join['conditional_full_ring_physical_repair_join']
    assert join['full_upper_rejoined_after_additional_periods'] == 2
    assert join['full_banks_Signals_controllers_and_flags_rejoin_after_additional_periods'] == 3
    assert join['retained_nonMEM_words'] == 3 and not join['complete_physical_erasure']
    result = dict(evidence_integrity_verified=True, conditional_full_ring_repair_checks_passed=True,
                  prior_evidence_files_verified=298, files=dict(sorted(files.items())),
                  external_bank_sha256=external, accepted_receipts=list(accepted),
                  descriptor_sha256=prior['descriptor_sha256'], ROM_sha256=prior['ROM_sha256'],
                  focused_tests_passed=7, full_lower_ring_physical_sites=1073741824,
                  selected_fault_marks=8404, decoded_repair_after_additional_periods=2,
                  bank_history_repair_after_additional_periods=3,
                  retained_nonMEM_words=3, complete_physical_erasure=False,
                  physical_normalization_before_communication_checked=True,
                  new_literal_full_ring_GPU_execution=False,
                  full_project_goal_complete=False,
                  scope='Conditional descriptor-semantics join from the selected physically '
                        'faulted full-ring commit through reset, physical metadata normalization '
                        'and three further periods. Existing noiseless refinements and audited '
                        'window execution remain premises. Three nonMEM Data words persist; '
                        'no fresh-noise, general amplification or threshold claim.')
    with out.open('x') as stream:
        stream.write(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(dict(output=str(out), verified_files=len(files), prior_files_unchanged=298,
                         external_banks_verified=len(external))))


if __name__ == '__main__':
    main()
