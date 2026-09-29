"""Seal residual separation evidence without rewriting previous results."""
import json
from pathlib import Path
from experiments.fixed_rule.audit_retimed_holder_prefix_embedding import sha


def main():
    root, fig = Path.cwd(), Path('figs/fixed_rule')
    out = fig/'retimed_holder_residual_noise_evidence_v1.json'
    if out.exists():
        raise FileExistsError(out)
    prior_path = fig/'retimed_holder_full_ring_repair_evidence_v1.json'
    prior = json.loads(prior_path.read_text())
    files = dict(prior['files'])
    assert len(files) == 320
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
                 Path('Report/fixed_rule/RESIDUAL_NOISE_DOMAIN.md'),
                 Path('Report/fixed_rule/STATUS_BEFORE_RESIDUAL_NOISE_20260927.md'),
                 Path('experiments/fixed_rule/certify_retimed_holder_residual_noise_domain.py'),
                 Path('experiments/fixed_rule/audit_retimed_holder_residual_noise.py'),
                 Path('tests/fixed_rule/test_retimed_holder_residual_noise_domain.py')]
    additions += list(fig.glob('retimed_holder_residual_noise_*'))
    for path in additions:
        bind(path)
    accepted = ('residual_noise_domain_v1', 'residual_noise_audit_v1')
    for name in accepted:
        path = fig/('retimed_holder_'+name+'.json')
        doc = json.loads(path.read_text())
        assert doc['passed'] and doc['descriptor_sha256'] == prior['descriptor_sha256']
        for source, expected in doc['source_sha256'].items():
            bind(source, expected)
        if 'artifact_sha256' in doc:
            bind(path.with_suffix('.npz'), doc['artifact_sha256'])
        watch = json.loads(path.with_name(path.stem+'_watch.json').read_text())
        assert watch['returncode'] == 0 and watch['termination_reason'] is None
    tests = json.loads((fig/'retimed_holder_residual_noise_tests_v1_watch.json').read_text())
    assert tests['returncode'] == 0 and tests['termination_reason'] is None
    assert 'Ran 6 tests' in (fig/'retimed_holder_residual_noise_tests_v1.log').read_text()
    audit = json.loads((fig/'retimed_holder_residual_noise_audit_v1.json').read_text())
    witness = audit['address_counterexample']
    assert witness['actual_output_Signal'] != witness['comparison_output_Signal']
    assert not witness['observed_experiment_residual_value']
    result = dict(evidence_integrity_verified=True,
                  prior_evidence_files_verified=320, files=dict(sorted(files.items())),
                  external_bank_sha256=external, accepted_receipts=list(accepted),
                  descriptor_sha256=prior['descriptor_sha256'], ROM_sha256=prior['ROM_sha256'],
                  focused_tests_passed=6,
                  arbitrary_independent_clock_residual_separation=True,
                  initial_selected_Data_coherence_required=False,
                  canonical_Address_required=True,
                  literal_Address_preserving_fault_replacements=144,
                  scalar_native_Address_counterexample=True,
                  actual_experiment_even_residual_activation_shown=False,
                  general_noise_correction_proved=False, full_project_goal_complete=False,
                  scope='Residual Data separation under canonical Address with arbitrary '
                        'clocks, controllers and incoherent Data copies, plus literal '
                        'fresh-fault tests. A one-bit residue supplies a concrete Address '
                        'counterexample; no general amplification or noise threshold claim.')
    with out.open('x') as stream:
        stream.write(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(dict(output=str(out), verified_files=len(files), prior_files_unchanged=320,
                         external_banks_verified=len(external))))


if __name__ == '__main__':
    main()
