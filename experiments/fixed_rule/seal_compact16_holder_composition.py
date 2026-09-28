"""Seal new-rule physical paths, regular mail identities and literal packet tests."""
import json
from pathlib import Path
from experiments.fixed_rule.audit_retimed_holder_prefix_embedding import sha


def main():
    fig = Path('figs/fixed_rule')
    output = fig / 'compact16_holder_composition_evidence_v1.json'
    if output.exists():
        raise FileExistsError(output)
    prior_path = fig / 'compact16_holder_candidate_evidence_v1.json'
    prior = json.loads(prior_path.read_text())
    files = dict(prior['files'])
    assert len(files) == 568
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
        assert str(path) not in files or files[str(path)] == digest, str(path)
        files[str(path)] = digest

    docs = {}
    for name in ('paths', 'mail'):
        path = fig / ('compact16_holder_'+name+'_v1.json')
        doc = json.loads(path.read_text())
        assert doc['passed'] and doc['descriptor_sha256'] == prior['candidate_descriptor_sha256']
        assert doc['ROM_sha256'] == prior['candidate_ROM_sha256']
        for source, digest in {**doc['source_sha256'], **doc.get('input_sha256', {})}.items():
            bind(source, digest)
        bind(path)
        docs[name] = doc
    for name in ('paths', 'mail', 'composition_tests'):
        stem = 'compact16_holder_'+name+'_v1'
        watch_path = fig / (stem+'_watch.json')
        watch = json.loads(watch_path.read_text())
        assert watch['returncode'] == 0 and watch['termination_reason'] is None
        bind(watch_path)
        bind(fig / (stem+'.log'))
    assert 'Ran 6 tests' in (fig / 'compact16_holder_composition_tests_v1.log').read_text()
    for path in (prior_path, Path(__file__),
                 Path('tests/fixed_rule/test_compact16_holder_composition.py'),
                 Path('Report/fixed_rule/COMPACT16_PATHS_AND_MAIL.md'),
                 Path('Report/fixed_rule/STATUS_BEFORE_COMPACT16_COMPOSITION_20260927.md')):
        bind(path)
    paths, mail = docs['paths'], docs['mail']
    assert len(paths['additional_leaves']) == 84
    assert paths['ordinary_path_count'] == 12809 and paths['metadata_path_count'] == 392
    assert paths['dispatch_path_count'] == 12907 and paths['packet_schedule']['passed']
    assert paths['packet_schedule']['actual_SEND_sites_checked'] == 1786
    assert mail['case_count'] == 63 and len(mail['packet_flight_cases']) == 8
    assert all(row['passed'] for row in mail['mail_cases'])
    result = dict(evidence_integrity_verified=True, prior_evidence_files_verified=568,
                  files=dict(sorted(files.items())), external_bank_sha256=prior['external_bank_sha256'],
                  descriptor_sha256=prior['descriptor_sha256'], ROM_sha256=prior['ROM_sha256'],
                  candidate_descriptor_sha256=prior['candidate_descriptor_sha256'],
                  candidate_ROM_sha256=prior['candidate_ROM_sha256'],
                  candidate_promoted_to_baseline=False, Q=16384, U=1073741824,
                  additional_local_leaves=84, ordinary_paths=12809, metadata_paths=392,
                  dispatch_paths=12907, regular_mail_cases=63, flight_hop_cases=8,
                  literal_packet_trajectories=3, ticks_per_literal_trajectory=8,
                  focused_tests_passed=6, whole_period_composition_complete=False,
                  new_physical_period_executed=False, general_noise_theorem=False,
                  full_project_goal_complete=False)
    with output.open('x') as stream:
        stream.write(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps(dict(output=str(output), verified_files=len(files), prior_files_unchanged=568)))


if __name__ == '__main__':
    main()
