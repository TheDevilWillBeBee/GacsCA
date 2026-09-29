"""Bind phase proofs, entry relation, literal tests and preserved fixture failure."""
import json
from pathlib import Path
from experiments.fixed_rule.audit_retimed_holder_prefix_embedding import sha


def main():
    fig = Path('figs/fixed_rule')
    output = fig/'compact16_holder_barrier_evidence_v1.json'
    if output.exists():
        raise FileExistsError(output)
    prior_path = fig/'compact16_holder_composition_evidence_v1.json'
    prior = json.loads(prior_path.read_text())
    files = dict(prior['files'])
    assert len(files) == 588
    for path, digest in {**files, **prior['external_bank_sha256']}.items():
        assert sha(path) == digest, path

    def bind(path, expected=None):
        path = Path(path)
        if path.is_absolute():
            path = path.relative_to(Path.cwd())
        digest = sha(path)
        assert expected is None or digest == expected, str(path)
        assert str(path) not in files or files[str(path)] == digest, str(path)
        files[str(path)] = digest

    path = fig/'compact16_holder_barriers_v1.json'
    doc = json.loads(path.read_text())
    assert doc['passed'] and doc['descriptor_sha256'] == prior['candidate_descriptor_sha256']
    assert doc['ROM_sha256'] == prior['candidate_ROM_sha256']
    assert len(doc['all_clock_mail_cases']) == 9
    assert doc['all_clock_mail_raw_output_words'] == 11242
    assert all(row['passed'] for row in doc['all_clock_mail_cases'])
    assert doc['quiet_barriers']['passed'] and doc['full_raw_reset']['complete_raw_outputs'] == 154
    assert doc['signal_schedule_join']['passed']
    assert doc['signal_schedule_join']['packet_occurrences_checked'] == 1786
    assert not doc['whole_period_composition_complete'] and not doc['new_physical_period_executed']
    for source, digest in {**doc['source_sha256'], **doc['input_sha256']}.items():
        bind(source, digest)
    bind(path)
    for stem, code in (('compact16_holder_barriers_v1', 0),
                       ('compact16_holder_barrier_tests_v1', 1),
                       ('compact16_holder_barrier_tests_v2', 0)):
        watch_path = fig/(stem+'_watch.json')
        watch = json.loads(watch_path.read_text())
        assert watch['returncode'] == code and watch['termination_reason'] is None
        bind(watch_path)
        bind(fig/(stem+'.log'))
    test_log = (fig/'compact16_holder_barrier_tests_v2.log').read_text()
    assert 'Ran 6 tests' in test_log and '\nOK\n' in test_log
    assert 'FAILED (failures=1)' in (fig/'compact16_holder_barrier_tests_v1.log').read_text()
    for path in (prior_path, Path(__file__),
                 Path('gacsca/fixed_rule/compact16_holder_period_relation.py'),
                 Path('tests/fixed_rule/test_compact16_holder_barriers.py'),
                 Path('Report/fixed_rule/COMPACT16_BARRIERS.md'),
                 Path('Report/fixed_rule/COMPACT16_BARRIER_TEST_FIXTURE_FAILED_V1.txt'),
                 Path('Report/fixed_rule/STATUS_BEFORE_COMPACT16_BARRIERS_20260927.md')):
        bind(path)
    result = dict(evidence_integrity_verified=True, prior_evidence_files_verified=588,
                  files=dict(sorted(files.items())), external_bank_sha256=prior['external_bank_sha256'],
                  descriptor_sha256=prior['descriptor_sha256'], ROM_sha256=prior['ROM_sha256'],
                  candidate_descriptor_sha256=prior['candidate_descriptor_sha256'],
                  candidate_ROM_sha256=prior['candidate_ROM_sha256'],
                  candidate_promoted_to_baseline=False, Q=16384, U=1073741824,
                  all_clock_mail_cases=9, complete_reset_outputs=154,
                  focused_tests_passed=6, literal_native_phase_steps=13,
                  complete_entry_ring_sites_validated=16384, preserved_failed_fixture_runs=1,
                  whole_period_composition_complete=False, new_physical_period_executed=False,
                  general_noise_theorem=False, full_project_goal_complete=False)
    with output.open('x') as stream:
        stream.write(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(dict(output=str(output), verified_files=len(files), prior_files_unchanged=588)))


if __name__ == '__main__':
    main()
