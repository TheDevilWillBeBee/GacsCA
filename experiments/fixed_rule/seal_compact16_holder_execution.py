"""Seal compact physical execution, private binaries, parity tests and audits."""
import json
from pathlib import Path
from experiments.fixed_rule.audit_retimed_holder_prefix_embedding import sha


def main():
    fig = Path('figs/fixed_rule')
    output = fig/'compact16_holder_execution_evidence_v1.json'
    if output.exists():
        raise FileExistsError(output)
    prior_path = fig/'compact16_holder_period_evidence_v1.json'
    prior = json.loads(prior_path.read_text())
    files = dict(prior['files'])
    assert len(files) == 642
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

    docs = {}
    for name in ('backend_distance', 'cpu_periods', 'cpu_period_audit'):
        path = fig/('compact16_holder_'+name+'_v1.json')
        doc = json.loads(path.read_text())
        assert doc['passed']
        if 'descriptor_sha256' in doc:
            assert doc['descriptor_sha256'] == prior['candidate_descriptor_sha256']
        if 'rom_sha256' in doc:
            assert doc['rom_sha256'] == prior['candidate_ROM_sha256']
        for source, digest in doc['source_sha256'].items():
            bind(source, digest)
        bind(path)
        docs[name] = doc
    execution = docs['cpu_periods']
    assert execution['periods'] == 2 and execution['colonies'] == 3
    assert execution['physical_ticks'] == 2147483648
    assert execution['metrics']['full_raw_evaluations'] == 3012954
    assert execution['metrics']['packets_emitted'] == execution['metrics']['packets_delivered'] == 10716
    assert execution['metrics']['packets_dropped'] == 0
    assert all(row['full_entry_relation']['validated_sites'] == 49152 for row in execution['period_results'])
    bind(execution['snapshot'], execution['snapshot_sha256'])
    for binary, digest in execution['binaries'].items():
        bind(binary, digest)
        for path in Path(binary).parent.iterdir():
            if path.is_file():
                bind(path)
    distance = docs['backend_distance']
    assert distance['checked_breakpoint_cases'] == 2557336
    assert set(distance['mutations_rejected']) == {'overshoot', 'wrong_target_register'}
    for directory in (fig/'build').glob('compact16_backend_distance_*'):
        for path in directory.iterdir():
            if path.is_file():
                bind(path)
    audit = docs['cpu_period_audit']['cases'][0]
    assert audit['execution_sha256'] == sha(fig/'compact16_holder_cpu_periods_v1.json')
    assert audit['snapshot_sha256'] == execution['snapshot_sha256']
    assert audit['scalar_and_descriptor_agree'] and audit['saved_complete_Info_matches']
    assert [row['represented_controller_words_changed'] for row in audit['period_results']] == [35, 0]
    for name in (*docs, 'cpu_tests', 'packet_tests', 'execution_audit_tests'):
        stem = 'compact16_holder_'+name+'_v1'
        watch_path = fig/(stem+'_watch.json')
        watch = json.loads(watch_path.read_text())
        assert watch['returncode'] == 0 and watch['termination_reason'] is None
        bind(watch_path)
        bind(fig/(stem+'.log'))
    for name, count in (('cpu_tests', 12), ('packet_tests', 7), ('execution_audit_tests', 2)):
        text = (fig/('compact16_holder_'+name+'_v1.log')).read_text()
        assert f'Ran {count} tests' in text and '\nOK\n' in text
    fixture_path = fig/'compact16_holder_active_fixture_v1.json'
    fixture = json.loads(fixture_path.read_text())
    assert fixture['passed'] and fixture['physical_periods_executed'] == 0
    bind('experiments/fixed_rule/compact16_holder_active_fixture.py', fixture['source_sha256'])
    bind(fixture_path)
    for path in (prior_path, Path(__file__),
                 Path('gacsca/fixed_rule/compact16_holder_quotient.py'),
                 Path('tests/fixed_rule/test_compact16_holder_cpu_events.py'),
                 Path('tests/fixed_rule/test_compact16_holder_cpu_general.py'),
                 Path('tests/fixed_rule/test_compact16_holder_cpu_gather.py'),
                 Path('tests/fixed_rule/test_compact16_holder_execution_audit.py'),
                 Path('Report/fixed_rule/COMPACT16_EXECUTION.md'),
                 Path('Report/fixed_rule/STATUS_BEFORE_COMPACT16_EXECUTION_20260927.md')):
        bind(path)
    result = dict(evidence_integrity_verified=True, prior_evidence_files_verified=642,
                  files=dict(sorted(files.items())), external_bank_sha256=prior['external_bank_sha256'],
                  descriptor_sha256=prior['descriptor_sha256'], ROM_sha256=prior['ROM_sha256'],
                  candidate_descriptor_sha256=prior['candidate_descriptor_sha256'],
                  candidate_ROM_sha256=prior['candidate_ROM_sha256'],
                  frozen_retimed_baseline_unchanged=True, Q=16384, U=1073741824,
                  compact_physical_periods_executed=2, colonies=3, physical_sites=49152,
                  physical_ticks=2147483648, complete_native_evaluations=3012954,
                  physical_evolution_seconds=execution['physical_evolution_seconds'],
                  focused_tests_passed=21, both_Signal_sides_exercised=True,
                  sustained_upper_computation_in_period_run=False,
                  larger_active_fixture_preflight_only=True, GPU_used=False,
                  general_backend_equivalence=False, practical_depth_two_execution=False,
                  general_noise_theorem=False, full_project_goal_complete=False)
    with output.open('x') as stream:
        stream.write(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(dict(output=str(output), verified_files=len(files), prior_files_unchanged=642)))


if __name__ == '__main__':
    main()
