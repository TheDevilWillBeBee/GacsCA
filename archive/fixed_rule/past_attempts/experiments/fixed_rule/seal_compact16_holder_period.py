"""Seal compact descriptor-period argument and its finite executable evidence."""
import json
from pathlib import Path
from experiments.fixed_rule.audit_retimed_holder_prefix_embedding import sha


def main():
    fig = Path('figs/fixed_rule')
    output = fig/'compact16_holder_period_evidence_v1.json'
    if output.exists():
        raise FileExistsError(output)
    prior_path = fig/'compact16_holder_barrier_evidence_v1.json'
    prior = json.loads(prior_path.read_text())
    files = dict(prior['files'])
    assert len(files) == 610
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
    for name in ('structural', 'semantic', 'period_entry', 'noiseless_period'):
        path = fig/('compact16_holder_'+name+'_v1.json')
        doc = json.loads(path.read_text())
        assert doc['passed'] and doc['descriptor_sha256'] == prior['candidate_descriptor_sha256']
        if 'ROM_sha256' in doc:
            assert doc['ROM_sha256'] == prior['candidate_ROM_sha256']
        for source, digest in {**doc['source_sha256'], **doc.get('input_sha256', {})}.items():
            bind(source, digest)
        bind(path)
        docs[name] = doc
    for name in (*docs, 'period_tests'):
        stem = 'compact16_holder_'+name+'_v1'
        watch_path = fig/(stem+'_watch.json')
        watch = json.loads(watch_path.read_text())
        assert watch['returncode'] == 0 and watch['termination_reason'] is None
        bind(watch_path)
        bind(fig/(stem+'.log'))
    tests = (fig/'compact16_holder_period_tests_v1.log').read_text()
    assert 'Ran 8 tests' in tests and '\nOK\n' in tests
    structural, semantic = docs['structural'], docs['semantic']
    assert len(structural['cases']) == 9 and structural['canonical_structural_domain_preserved']
    assert structural['geometry']['minimum_gap_to_next_colony_core'] == 30
    assert semantic['timed']['commit_matches_normalized_complete_rule']
    assert semantic['open']['center_commit_equals_normalized_full_descriptor']
    assert not semantic['open']['periodic_destination_used']
    assert semantic['queries']['maximum_possible_query_mask'] == 16383
    assert semantic['typing']['raw_outputs_checked'] == 154
    assert docs['period_entry']['full_ring']['validated_sites'] == 16384
    assert docs['period_entry']['first_reset_complete_scalar_native_outputs'] == 317
    assert len(docs['noiseless_period']['phase_interfaces']) == 6
    assert docs['noiseless_period']['complete_entry_restored_at_commit']
    assert not docs['noiseless_period']['new_physical_period_executed']
    for path in (prior_path, Path(__file__),
                 Path('tests/fixed_rule/test_compact16_holder_noiseless_period.py'),
                 Path('Report/fixed_rule/COMPACT16_NOISELESS_MACROSTEP.md'),
                 Path('Report/fixed_rule/STATUS_BEFORE_COMPACT16_PERIOD_20260927.md')):
        bind(path)
    result = dict(evidence_integrity_verified=True, prior_evidence_files_verified=610,
                  files=dict(sorted(files.items())), external_bank_sha256=prior['external_bank_sha256'],
                  descriptor_sha256=prior['descriptor_sha256'], ROM_sha256=prior['ROM_sha256'],
                  candidate_descriptor_sha256=prior['candidate_descriptor_sha256'],
                  candidate_ROM_sha256=prior['candidate_ROM_sha256'],
                  candidate_promoted_to_execution_baseline=False, Q=16384, U=1073741824,
                  descriptor_period_induction='Companion mathematical induction with executable '
                                              'finite checks; not a proof-assistant formalization.',
                  candidate_whole_period_composition_complete=True,
                  independent_raw_mail_head_image_cases=9, complete_raw_output_words=154,
                  timed_instruction_reads=671760, timed_instruction_writes=326070,
                  timed_packet_deliveries=26790, bounded_metadata_queries=7350,
                  entry_ring_sites=16384, first_reset_scalar_native_outputs=317,
                  focused_tests_passed=8, successive_periods_by_relation_composition=True,
                  new_physical_period_executed=False, general_backend_equivalence=False,
                  practical_depth_two_execution=False, general_noise_theorem=False,
                  full_project_goal_complete=False)
    with output.open('x') as stream:
        stream.write(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(dict(output=str(output), verified_files=len(files), prior_files_unchanged=610)))


if __name__ == '__main__':
    main()
