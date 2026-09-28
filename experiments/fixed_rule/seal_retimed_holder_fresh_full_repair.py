"""Seal the conditional complete selected fresh-fault recovery join."""
import json
from pathlib import Path
from experiments.fixed_rule.audit_retimed_holder_prefix_embedding import sha


def main():
    root,fig=Path.cwd(),Path('figs/fixed_rule')
    out=fig/'retimed_holder_fresh_full_repair_evidence_v1.json'
    if out.exists():raise FileExistsError(out)
    prior_path=fig/'retimed_holder_fresh_geometry_evidence_v1.json'
    prior=json.loads(prior_path.read_text());files=dict(prior['files']);assert len(files)==392
    for path,digest in files.items():assert sha(path)==digest,path
    external=prior['external_bank_sha256']
    for path,digest in external.items():assert sha(path)==digest,path
    def bind(path,expected=None):
        path=Path(path)
        if path.is_absolute():path=path.relative_to(root)
        digest=sha(path);assert expected is None or digest==expected,str(path)
        files[str(path)]=digest
    additions=[prior_path,Path(__file__),Path('Report/fixed_rule/FRESH_FULL_REPAIR.md'),
               Path('Report/fixed_rule/STATUS_BEFORE_FRESH_FULL_REPAIR_20260927.md'),
               Path('experiments/fixed_rule/certify_retimed_holder_geometry_procedure_effects.py'),
               Path('experiments/fixed_rule/join_retimed_holder_fresh_full_repair.py'),
               Path('tests/fixed_rule/test_retimed_holder_fresh_full_repair.py')]
    for prefix in ('geometry_procedure_effects','fresh_full_repair'):
        additions+=list(fig.glob('retimed_holder_'+prefix+'*'))
    for path in additions:bind(path)
    accepted=('geometry_procedure_effects_v1','fresh_full_repair_v2')
    for name in accepted:
        path=fig/('retimed_holder_'+name+'.json');doc=json.loads(path.read_text())
        assert doc['passed'] and doc['descriptor_sha256']==prior['descriptor_sha256']
        for source,digest in {**doc['source_sha256'],**doc.get('input_sha256',{})}.items():bind(source,digest)
        if 'artifact_sha256' in doc:bind(path.with_suffix('.npz'),doc['artifact_sha256'])
        watch=json.loads(path.with_name(path.stem+'_watch.json').read_text())
        assert watch['returncode']==0 and watch['termination_reason'] is None
    first=json.loads((fig/'retimed_holder_fresh_full_repair_v1.json').read_text())
    final=json.loads((fig/'retimed_holder_fresh_full_repair_v2.json').read_text())
    source=str(root/'experiments/fixed_rule/join_retimed_holder_fresh_full_repair.py')
    assert sha(fig/'retimed_holder_fresh_full_repair_v1_source.py')==first['source_sha256'][source]
    assert first['artifact_sha256']==final['artifact_sha256']
    assert final['conditional_complete_selected_fresh_fault_repair'] and final['full_state_rejoin_age']==16989
    tests=json.loads((fig/'retimed_holder_fresh_full_repair_tests_v1_watch.json').read_text())
    assert tests['returncode']==0 and tests['termination_reason'] is None
    assert 'Ran 7 tests' in (fig/'retimed_holder_fresh_full_repair_tests_v1.log').read_text()
    result=dict(evidence_integrity_verified=True,prior_evidence_files_verified=392,
                files=dict(sorted(files.items())),external_bank_sha256=external,
                accepted_receipts=list(accepted),descriptor_sha256=prior['descriptor_sha256'],ROM_sha256=prior['ROM_sha256'],
                focused_tests_passed=7,conditional_complete_selected_fresh_repair=True,
                complete_rejoin_age=16989,old_residual_words_included_and_erased=True,
                inherited_full_ring_and_geometry_refinement_premises=True,
                new_literal_noisy_suffix=False,new_literal_full_ring_GPU_run=False,
                general_repeated_noise_theorem=False,full_project_goal_complete=False,
                scope='Conditional full-state induction for the selected nine fresh marks '
                      'after the earlier audited burst repair. Complete descriptor clearing '
                      'and zero-domain identities plus healthy execution and checked dangerous '
                      'neighborhoods establish equality at16989 under prior refinements.')
    with out.open('x') as stream:stream.write(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(output=str(out),verified_files=len(files),prior_files_unchanged=392,external_banks_verified=len(external))))


if __name__=='__main__':main()
