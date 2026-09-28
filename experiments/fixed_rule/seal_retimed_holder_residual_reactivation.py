"""Seal the actual-endpoint reactivation audit, including rejected predecessors."""
import json
from pathlib import Path
from experiments.fixed_rule.audit_retimed_holder_prefix_embedding import sha


def main():
    root, fig = Path.cwd(), Path('figs/fixed_rule')
    out = fig/'retimed_holder_residual_reactivation_evidence_v1.json'
    if out.exists():
        raise FileExistsError(out)
    prior_path = fig/'retimed_holder_residual_noise_evidence_v1.json'
    prior = json.loads(prior_path.read_text())
    files = dict(prior['files'])
    assert len(files) == 336
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
                 Path('Report/fixed_rule/RESIDUAL_REACTIVATION.md'),
                 Path('Report/fixed_rule/STATUS_BEFORE_RESIDUAL_REACTIVATION_20260927.md'),
                 Path('experiments/fixed_rule/probe_retimed_holder_residual_reactivation.py'),
                 Path('experiments/fixed_rule/audit_retimed_holder_residual_reactivation.py'),
                 Path('tests/fixed_rule/test_retimed_holder_residual_reactivation.py')]
    additions += list(fig.glob('retimed_holder_residual_reactivation_*'))
    for path in additions:
        bind(path)
    name = 'retimed_holder_residual_reactivation_audit_v3'
    path = fig/(name+'.json')
    doc = json.loads(path.read_text())
    assert doc['passed'] and doc['descriptor_sha256'] == prior['descriptor_sha256']
    for source, expected in {**doc['source_sha256'], **doc['input_sha256']}.items():
        bind(source, expected)
    bind(path.with_suffix('.npz'), doc['artifact_sha256'])
    watch = json.loads((fig/(name+'_watch.json')).read_text())
    assert watch['returncode'] == 0 and watch['termination_reason'] is None
    for failed in (1, 2):
        row = json.loads((fig/f'retimed_holder_residual_reactivation_audit_v{failed}_watch.json').read_text())
        assert row['returncode'] == 1 and row['termination_reason'] is None
    tests = json.loads((fig/'retimed_holder_residual_reactivation_tests_v3_watch.json').read_text())
    assert tests['returncode'] == 0 and tests['termination_reason'] is None
    assert 'Ran 5 tests' in (fig/'retimed_holder_residual_reactivation_tests_v3.log').read_text()
    assert doc['observed_residual_value_activated'] and doc['activated_value'] == 2418452793257099264
    assert doc['paired_rejoined'] and not doc['fault_free_rejoined']
    assert doc['scalar_raw_output_words'] == doc['retained_native_output_words'] == 242550
    result = dict(evidence_integrity_verified=True,
                  prior_evidence_files_verified=336, files=dict(sorted(files.items())),
                  external_bank_sha256=external, accepted_receipts=[name],
                  descriptor_sha256=prior['descriptor_sha256'], ROM_sha256=prior['ROM_sha256'],
                  focused_tests_passed=5, actual_observed_residual_controller_read=True,
                  fresh_full_state_marks=9, paired_rejoin_tick=5,
                  fresh_damage_still_present=True, new_fault_free_repair=False,
                  full_ring_initial_relation_conditional=True,
                  pilot_early_snapshot_aliasing_preserved_and_accounted_for=True,
                  independent_scalar_raw_outputs=242550, full_project_goal_complete=False,
                  scope='Complete five-tick scalar/native continuation from the actual repaired '
                        'endpoint. Actual residue enters one controller holder and is then '
                        'physically erased; the paired worlds couple but retain new fault damage '
                        'relative to a fault-free trajectory. No general noise repair claim.')
    with out.open('x') as stream:
        stream.write(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(dict(output=str(out), verified_files=len(files), prior_files_unchanged=336,
                         external_banks_verified=len(external))))


if __name__ == '__main__':
    main()
