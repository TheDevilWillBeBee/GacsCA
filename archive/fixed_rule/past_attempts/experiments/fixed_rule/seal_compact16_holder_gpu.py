"""Preserve the prior702 files and bind compact CUDA proofs, executions and failures."""
import json
from pathlib import Path
from experiments.fixed_rule.audit_small_holder_position_events import sha


def main():
    fig = Path('figs/fixed_rule'); prior_path = fig/'compact16_holder_execution_evidence_v1.json'
    out = fig/'compact16_holder_gpu_evidence_v1.json'
    if out.exists(): raise FileExistsError(out)
    prior = json.loads(prior_path.read_text()); files = dict(prior['files'])
    assert len(files) == 702
    for path, digest in {**files, **prior['external_bank_sha256']}.items(): assert sha(path) == digest, path

    def bind(path, expected=None):
        path = Path(path)
        if path.is_absolute(): path = path.relative_to(Path.cwd())
        digest = sha(path)
        assert expected is None or digest == expected, str(path)
        assert str(path) not in files or files[str(path)] == digest, str(path)
        files[str(path)] = digest

    stems = ('build_v1','reduction_v1','reduction_v2','tests_v1','periods_v1','periods_v2','active_v1','audit_v1','audit_tests_v1')
    for stem in stems:
        base = 'compact16_holder_gpu_'+stem
        watch = fig/(base+'_watch.json'); record = json.loads(watch.read_text())
        expected = 1 if stem in ('reduction_v1','periods_v1') else 0
        assert record['returncode'] == expected and record['termination_reason'] is None
        bind(watch); bind(fig/(base+'.log'))
        path = fig/(base+'.json')
        if path.exists():
            doc = json.loads(path.read_text()); assert doc['passed']; bind(path)
            for source, digest in doc.get('source_sha256', {}).items(): bind(source, digest)
            if 'artifact' in doc: bind(doc['artifact'], doc['artifact_sha256'])
    for name in ('periods_v2','active_v1'):
        doc = json.loads((fig/('compact16_holder_gpu_'+name+'.json')).read_text())
        assert doc['descriptor_sha256'] == prior['candidate_descriptor_sha256']
        assert doc['rom_sha256'] == prior['candidate_ROM_sha256']
        assert doc['physical_ticks'] == 2147483648 and doc['periods'] == 2
        assert doc['sustained_upper_arithmetic'] == (name == 'active_v1')
    reduction = json.loads((fig/'compact16_holder_gpu_reduction_v2.json').read_text())
    assert len(reduction['cases']) == 9
    assert all(case['exact_expression_fields'] == 28 for case in reduction['cases'])
    build = json.loads((fig/'compact16_holder_gpu_build_v1.json').read_text())
    for row in build['libraries']:
        bind(row['binary'], row['sha256'])
        for path in Path(row['binary']).parent.iterdir():
            if path.is_file(): bind(path)
    for name in ('records','packed','prefix_description','flag_profile','resident_period','resident_independent','resident_mixed','resident_gather','resident_general','flags_gpu'):
        for extension in ('.py','.cu'):
            path = Path('gacsca/fixed_rule')/('compact16_holder_'+name+extension)
            if path.exists(): bind(path)
    for name in ('build_compact16_holder_gpu','certify_compact16_holder_gpu_reduction','certify_compact16_holder_gpu_reduction_v2','run_compact16_holder_gpu_periods','run_compact16_holder_gpu_periods_v2','audit_compact16_holder_gpu_periods'):
        bind(Path('experiments/fixed_rule')/(name+'.py'))
    for name in ('gpu','gpu_audit'): bind(Path('tests/fixed_rule')/('test_compact16_holder_'+name+'.py'))
    for name, number in (('tests_v1',5), ('audit_tests_v1',2)):
        log = (fig/('compact16_holder_gpu_'+name+'.log')).read_text()
        assert f'Ran {number} tests' in log and '\nOK\n' in log
    for path in (prior_path, Path(__file__), Path('Report/fixed_rule/COMPACT16_GPU_BACKEND.md'), Path('Report/fixed_rule/STATUS_BEFORE_COMPACT16_GPU_20260927.md')): bind(path)
    result = dict(evidence_integrity_verified=True, prior_evidence_files_verified=702,
                  files=dict(sorted(files.items())), external_bank_sha256=prior['external_bank_sha256'],
                  candidate_descriptor_sha256=prior['candidate_descriptor_sha256'], candidate_ROM_sha256=prior['candidate_ROM_sha256'],
                  descriptor_sha256=prior['descriptor_sha256'], ROM_sha256=prior['ROM_sha256'],
                  Q=16384, U=1073741824, focused_tests_passed=7,
                  actual_GPU_periods_per_fixture=2, colonies=[3,31], sustained_upper_arithmetic=True,
                  general_backend_equivalence=False, compact_complete_depth_two_execution=False,
                  general_noise_theorem=False, full_project_goal_complete=False)
    with out.open('x') as stream: stream.write(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(dict(output=str(out), verified_files=len(files), prior_files_unchanged=702)))


if __name__ == '__main__': main()
