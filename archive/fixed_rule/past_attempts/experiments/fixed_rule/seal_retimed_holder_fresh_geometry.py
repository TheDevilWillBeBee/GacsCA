"""Seal the bounded literal and projected fresh-geometry evidence."""
import json
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import retimed_holder_rule as f
from experiments.fixed_rule.audit_retimed_holder_prefix_embedding import sha


def main():
    root,fig=Path.cwd(),Path('figs/fixed_rule')
    out=fig/'retimed_holder_fresh_geometry_evidence_v1.json'
    if out.exists():raise FileExistsError(out)
    prior_path=fig/'retimed_holder_residual_reactivation_evidence_v1.json'
    prior=json.loads(prior_path.read_text());files=dict(prior['files']);assert len(files)==363
    for path,digest in files.items():assert sha(path)==digest,path
    external=prior['external_bank_sha256']
    for path,digest in external.items():assert sha(path)==digest,path
    def bind(path,expected=None):
        path=Path(path)
        if path.is_absolute():path=path.relative_to(root)
        digest=sha(path);assert expected is None or digest==expected,str(path)
        files[str(path)]=digest
    additions=[prior_path,Path(__file__),Path('Report/fixed_rule/FRESH_GEOMETRY_RECOVERY.md'),
               Path('Report/fixed_rule/STATUS_BEFORE_FRESH_GEOMETRY_20260927.md'),
               Path('gacsca/fixed_rule/retimed_holder_geometry_projection.py')]
    additions += [Path('experiments/fixed_rule')/x for x in (
        'probe_retimed_holder_fresh_geometry_recovery.py','certify_retimed_holder_early_geometry_projection.py',
        'audit_retimed_holder_fresh_geometry_projection.py','finish_retimed_holder_geometry_flags.py')]
    additions += [Path('tests/fixed_rule')/x for x in ('test_retimed_holder_early_geometry_projection.py','test_retimed_holder_geometry_flags.py')]
    for prefix in ('fresh_geometry','early_geometry','geometry_flags','geometry_final_tests'):
        additions+=list(fig.glob('retimed_holder_'+prefix+'*'))
    for path in additions:bind(path)
    accepted=('fresh_geometry_recovery_128_v1','early_geometry_projection_v1','fresh_geometry_projection_v1','geometry_flags_v1')
    for name in accepted:
        path=fig/('retimed_holder_'+name+'.json');doc=json.loads(path.read_text())
        assert doc['passed'] and doc['descriptor_sha256']==prior['descriptor_sha256']
        for source,digest in {**doc['source_sha256'],**doc.get('input_sha256',{})}.items():bind(source,digest)
        if 'artifact_sha256' in doc:bind(path.with_suffix('.npz'),doc['artifact_sha256'])
        watch=json.loads(path.with_name(path.stem+'_watch.json').read_text())
        assert watch['returncode']==0 and watch['termination_reason'] is None
    # The diagnostic projection ignores Wf and replaces the clock by a common
    # scalar. Bind those hypotheses to every actual saved replacement record.
    marks_path=fig/'retimed_holder_residual_reactivation_audit_v3.npz'
    with np.load(marks_path,allow_pickle=False) as z:
        fields=[f.COL[f'w{k}_{name}'] for k in range(5) for name in ('wf1','wf2')]
        assert not np.any(z['fault_replacements'][:,fields])
        np.testing.assert_array_equal(z['fault_replacements'][:,f.COL['age']],z['fault_times'])
        assert not np.any(z['initial_actual'][:,fields])
        assert not np.any(z['initial_actual'][:,f.COL['age']])
    tests=json.loads((fig/'retimed_holder_geometry_final_tests_v1_watch.json').read_text())
    assert tests['returncode']==0 and tests['termination_reason'] is None
    assert 'Ran 9 tests' in (fig/'retimed_holder_geometry_final_tests_v1.log').read_text()
    result=dict(evidence_integrity_verified=True,prior_evidence_files_verified=363,
                files=dict(sorted(files.items())),external_bank_sha256=external,
                accepted_receipts=list(accepted),descriptor_sha256=prior['descriptor_sha256'],ROM_sha256=prior['ROM_sha256'],
                focused_tests_passed=9,literal_complete_state_ticks=128,diagnostic_geometry_ticks=1024,
                exact_final_Flag1_recurrence_ticks=15965,geometry_restored_at_tick=16989,
                fresh_marks_preserve_uniform_clock_and_zero_Wf=True,
                all_projected_outputs_scalar_audited=False,complete_fresh_fault_repair_proved=False,
                full_project_goal_complete=False,
                scope='Literal complete-state continuation through128, checked geometry '
                      'projection through1024 and exact canonical Flag1 recurrence to16989. '
                      'Computation state after128 remains unverified; no full repair claim.')
    with out.open('x') as stream:stream.write(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(output=str(out),verified_files=len(files),prior_files_unchanged=363,external_banks_verified=len(external))))


if __name__=='__main__':main()
