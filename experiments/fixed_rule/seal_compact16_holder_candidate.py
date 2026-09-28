"""Seal the smaller fixed-rule candidate without promoting its execution status."""
import json
from pathlib import Path
from experiments.fixed_rule.audit_retimed_holder_prefix_embedding import sha
from gacsca.fixed_rule import compact16_holder_rule as f, compact16_holder_program as p
from gacsca.fixed_rule import retimed_holder_rule as reference


def main():
    fig = Path('figs/fixed_rule')
    out = fig / 'compact16_holder_candidate_evidence_v1.json'
    if out.exists():
        raise FileExistsError(out)
    prior_path = fig / 'sparse_holder_compiler_evidence_v1.json'
    prior = json.loads(prior_path.read_text())
    files = dict(prior['files'])
    assert len(files) == 533
    for path, digest in files.items():
        assert sha(path) == digest, path
    for path, digest in prior['external_bank_sha256'].items():
        assert sha(path) == digest, path

    def bind(path, digest=None):
        path = Path(path)
        if path.is_absolute():
            path = path.relative_to(Path.cwd())
        actual = sha(path)
        assert digest is None or actual == digest, str(path)
        assert str(path) not in files or files[str(path)] == actual, str(path)
        files[str(path)] = actual

    receipts = {}
    for kind in ('rom', 'clock_events', 'boundary'):
        path = fig / ('compact16_holder_'+kind+'_v1.json')
        doc = json.loads(path.read_text())
        assert doc['passed']
        assert doc.get('physical_descriptor_sha256', doc.get('descriptor_sha256')) == f.self_description().digest()
        if isinstance(doc['source_sha256'], dict):
            for source, digest in doc['source_sha256'].items():
                bind(source, digest)
        else:
            bind('experiments/fixed_rule/certify_compact16_holder_clock_events.py', doc['source_sha256'])
        bind(path)
        receipts[kind] = doc
    for kind in ('rom', 'clock_events', 'tests', 'boundary'):
        prefix = 'compact16_holder_'+kind+'_v1'
        watch_path = fig / (prefix+'_watch.json')
        watch = json.loads(watch_path.read_text())
        assert watch['returncode'] == 0 and watch['termination_reason'] is None
        bind(watch_path)
        bind(fig / (prefix+'.log'))
    assert 'Ran 6 tests' in (fig / 'compact16_holder_tests_v1.log').read_text()
    for path in Path('gacsca/fixed_rule').glob('compact16_holder*.py'):
        bind(path)
    for path in Path('experiments/fixed_rule').glob('*compact16_holder*.py'):
        bind(path)
    for directory in (fig/'build').glob('compact16_holder_native_*'):
        for path in directory.iterdir():
            if path.is_file():
                bind(path)
    for path in (prior_path, Path(__file__),
                 Path('tests/fixed_rule/test_compact16_holder.py'),
                 Path('Report/fixed_rule/COMPACT16_CANDIDATE.md'),
                 Path('Report/fixed_rule/STATUS_BEFORE_COMPACT16_20260927.md')):
        bind(path)
    rom, events, boundary = (receipts[name] for name in ('rom', 'clock_events', 'boundary'))
    assert f.SCHEMA == reference.SCHEMA and f.NEIGHBORHOOD == reference.NEIGHBORHOOD
    assert (f.Q, f.U, f.WIDTH) == (16384, 1073741824, 4090)
    assert boundary['ROM_sha256'] == rom['ROM_sha256']
    assert boundary['orbit']['normalized_ages'] == f.U
    assert all(row['replacement_addresses'] == 32768 for row in boundary['defect_cases'])
    assert events['case_count'] == 812 and events['event_families'] == 116
    g = p.layout()
    result = dict(evidence_integrity_verified=True, prior_evidence_files_verified=533,
                  files=dict(sorted(files.items())), external_bank_sha256=prior['external_bank_sha256'],
                  descriptor_sha256=prior['descriptor_sha256'], ROM_sha256=prior['ROM_sha256'],
                  candidate_descriptor_sha256=f.self_description().digest(),
                  candidate_ROM_sha256=rom['ROM_sha256'], candidate_promoted_to_baseline=False,
                  Q=f.Q, U=f.U, unchanged_raw_schema=True, unchanged_raw_bits=f.WIDTH,
                  core_cells=g.computation_cells, controller_path_ticks=rom['controller_path_ticks'],
                  complete_conditional_self_reference=True, direct_clock_event_cases=events['case_count'],
                  complete_noiseless_cap_orbit=True, permanent_Address_defect=True,
                  focused_tests_passed=6, new_physical_period_executed=False,
                  depth_two_costs=dict(physical_sites=f.Q**2, physical_ticks=f.U**2,
                      dense_projected_buffer_bytes=f.Q**2*2704//8,
                      canonical_MEM_bank_bytes=f.Q*(g.memory_count+5)*8,
                      allocation_measured=False, runtime_speedup_measured=False),
                  general_noise_theorem=False, full_project_goal_complete=False)
    with out.open('x') as stream:
        stream.write(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps(dict(output=str(out), verified_files=len(files), prior_files_unchanged=533,
                          actual_Q=f.Q, actual_U=f.U, unchanged_raw_bits=f.WIDTH)))


if __name__ == '__main__':
    main()
