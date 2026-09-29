"""Preserve earlier execution evidence and bind the current boundary checks."""
import json
from pathlib import Path
from experiments.fixed_rule.audit_retimed_holder_prefix_embedding import sha


def main():
    fig = Path('figs/fixed_rule')
    output = fig / 'retimed_holder_boundary_data_evidence_v1.json'
    if output.exists():
        raise FileExistsError(output)
    prior_path = fig / 'retimed_holder_fresh_gpu_execution_evidence_v1.json'
    prior = json.loads(prior_path.read_text())
    files = dict(prior['files'])
    assert len(files) == 446
    for path, digest in files.items():
        assert sha(path) == digest, path
    for path, digest in prior['external_bank_sha256'].items():
        assert sha(path) == digest, path

    def bind(path, expected=None):
        path = Path(path)
        if path.is_absolute():
            path = path.relative_to(Path.cwd())
        digest = sha(path)
        assert expected is None or digest == expected, str(path)
        if str(path) in files:
            assert files[str(path)] == digest, str(path)
        files[str(path)] = digest

    proof_path = fig / 'retimed_holder_boundary_orbit_v1.json'
    proof = json.loads(proof_path.read_text())
    assert proof['passed'] and proof['orbit']['passed']
    assert proof['descriptor_sha256'] == prior['descriptor_sha256']
    assert proof['ROM_sha256'] == prior['ROM_sha256']
    assert proof['orbit']['complete_raw_words'] == 154
    assert proof['orbit']['normalized_ages'] == 1 << 31
    assert len(proof['defect_cases']) == 12
    assert all(row['passed'] and row['raw_clocks'] == 1 << 32
               for row in proof['defect_cases'])
    for path, digest in proof['source_sha256'].items():
        bind(path, digest)
    for path in (prior_path, proof_path, Path(__file__),
                 Path('Report/fixed_rule/RETIMED_BOUNDARY_DATA.md'),
                 Path('Report/fixed_rule/STATUS_BEFORE_RETIMED_BOUNDARY_DATA_20260927.md'),
                 Path('tests/fixed_rule/test_retimed_holder_boundary_data.py')):
        bind(path)
    for prefix in ('retimed_holder_boundary_orbit_v1', 'retimed_holder_boundary_tests_v1'):
        watch_path = fig / (prefix + '_watch.json')
        watch = json.loads(watch_path.read_text())
        assert watch['returncode'] == 0 and watch['termination_reason'] is None
        bind(watch_path)
        bind(fig / (prefix + '.log'))
    assert 'Ran 6 tests' in (fig / 'retimed_holder_boundary_tests_v1.log').read_text()
    result = dict(evidence_integrity_verified=True, prior_evidence_files_verified=446,
                  files=dict(sorted(files.items())),
                  external_bank_sha256=prior['external_bank_sha256'],
                  descriptor_sha256=proof['descriptor_sha256'], ROM_sha256=proof['ROM_sha256'],
                  complete_noiseless_boundary_orbit=True,
                  permanent_single_Address_defect=True, focused_tests_passed=6,
                  new_nested_execution=False, robust_cap_proved=False,
                  general_noise_theorem=False, full_project_goal_complete=False)
    with output.open('x') as stream:
        stream.write(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps(dict(output=str(output), verified_files=len(files),
                          prior_files_unchanged=446,
                          external_banks_verified=len(prior['external_bank_sha256']))))


if __name__ == '__main__':
    main()
