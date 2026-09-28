"""Bind all eight actual noisy outcomes, including timeout and domain boundary."""
import json
from pathlib import Path
from experiments.fixed_rule.run_compact16_holder_streamed_depth2 import sha


def main():
    fig=Path('figs/fixed_rule');prior_path=fig/'compact16_holder_canonical_noise_evidence_v1.json';out=fig/'compact16_holder_all_macrosteps_evidence_v1.json'
    if out.exists():raise FileExistsError(out)
    prior=json.loads(prior_path.read_text());files=dict(prior['files']);external=prior['external_bank_sha256']
    assert len(files)==984 and len(external)==9
    for path,digest in {**files,**external}.items():assert sha(path)==digest,path
    def bind(path,expected=None):
        path=Path(path)
        if path.is_absolute():path=path.relative_to(Path.cwd())
        digest=sha(path);assert expected is None or digest==expected,str(path)
        assert str(path) not in files or files[str(path)]==digest,str(path)
        files[str(path)]=digest
    docs={}
    for name,version in (('late_events_tests',1),('stationary_signals',1),('late_multi_tests',1),('all_noise_macrosteps',2),('late_mail_tests',1),('mail_macrostep',1),('all_noise_macrosteps_audit',1)):
        stem=f'compact16_holder_{name}_v{version}';watch=fig/(stem+'_watch.json');record=json.loads(watch.read_text())
        assert record['returncode']==0 and record['termination_reason'] is None
        bind(watch);bind(fig/(stem+'.log'));path=fig/(stem+'.json')
        if not path.exists():continue
        doc=json.loads(path.read_text());assert doc['passed'] or name=='all_noise_macrosteps';docs[name]=doc;bind(path)
        if 'descriptor_sha256' in doc:assert doc['descriptor_sha256']==prior['candidate_descriptor_sha256']
        for source,digest in doc.get('source_sha256',{}).items():bind(source,digest)
        if 'artifact' in doc:bind(doc['artifact'],doc['artifact_sha256'])
    for name,count in (('late_events_tests',5),('late_multi_tests',3),('late_mail_tests',3)):
        log=(fig/f'compact16_holder_{name}_v1.log').read_text();assert f'Ran {count} tests' in log and '\nOK\n' in log
    timeout=fig/'compact16_holder_all_noise_macrosteps_v1_watch.json';record=json.loads(timeout.read_text())
    assert record['returncode']==-9 and record['termination_reason']=='wall-time limit exceeded'
    bind(timeout);bind(fig/'compact16_holder_all_noise_macrosteps_v1.log');bind('experiments/fixed_rule/compact16_holder_all_noise_macrosteps.py')
    proof=docs['stationary_signals'];assert proof['independent_bits']==123 and proof['complete_procedure_outputs_checked']==90 and proof['complete_procedure_Signal_input_dependencies']==0
    batch=docs['all_noise_macrosteps'];assert not batch['passed'] and batch['completed_macrosteps']==7 and batch['correct_macrosteps']==1
    assert [row['case'] for row in batch['trials'] if not row['completed']]==[4]
    assert batch['trials'][4]['stopped_age']==514889820 and batch['trials'][4]['error']=="RuntimeError('resident prefix step rejected: -4')"
    for row in batch['trials']:bind(row['checkpoint_artifact'],row['checkpoint_artifact_sha256'])
    bind(fig/'compact16_holder_all_noise_macrosteps_v2.jsonl')
    mail=docs['mail_macrostep'];assert mail['passed'] and mail['resumed_case']==4 and mail['starting_age']==514889820 and not mail['decoded_matches_intended_rule']
    assert mail['reference_sha256']==sha(fig/'compact16_holder_all_noise_macrosteps_v2.json')
    audit=docs['all_noise_macrosteps_audit'];assert audit['all_eight_histories_resolved'] and audit['correct_cases']==[1] and audit['incorrect_cases']==[0,2,3,4,5,6,7]
    assert audit['complete_raw_words_checked']==68124672 and audit['independent_scalar_outputs']==1232 and audit['headless_paths_agree']
    assert audit['cases'][6]['invalid_projected_words']==[dict(field='signal',value=32212254792,width=5)]
    negative=[]
    for kind,count in (('late_events',1),('late_multi',2),('late_mail',1)):
        builds=list((fig/'build').glob('compact16_holder_'+kind+'_*'));assert len(builds)==count
        for directory in builds:
            if kind=='late_multi' and 'During this jump every head has a constant velocity' not in (directory/'compact16_holder_resident_period.cu').read_text():negative.append(str(directory))
            for path in directory.iterdir():
                if path.is_file():bind(path)
    assert len(negative)==1
    for name in ('late_events','late_multi_events','late_mail_events'):
        bind(Path('gacsca/fixed_rule')/('compact16_holder_'+name+'.py'))
        bind(Path('tests/fixed_rule')/('test_compact16_holder_'+name+'.py'))
    for path in (prior_path,Path(__file__),Path('Report/fixed_rule/COMPACT16_ALL_NOISE_MACROSTEPS.md'),Path('Report/fixed_rule/STATUS_BEFORE_COMPACT16_ALL_MACROSTEPS_20260928.md')):bind(path)
    result=dict(evidence_integrity_verified=True,prior_evidence_files_verified=984,files=dict(sorted(files.items())),external_bank_sha256=external,
                candidate_descriptor_sha256=prior['candidate_descriptor_sha256'],candidate_ROM_sha256=prior['candidate_ROM_sha256'],
                descriptor_sha256=prior['descriptor_sha256'],ROM_sha256=prior['ROM_sha256'],Q=16384,U=1073741824,
                focused_tests_passed=11,stationary_Signal_BDD_bits=123,all_eight_noisy_macrosteps_resolved=True,
                correct_cases=[1],incorrect_cases=[0,2,3,4,5,6,7],malformed_projected_output_case=6,
                complete_native_audit_words=68124672,independent_scalar_outputs=1232,negative_control_builds=negative,
                preserved_timeout_attempt=True,preserved_seven_case_partial_receipt=True,
                general_noise_threshold=False,full_project_goal_complete=False)
    with out.open('x') as stream:stream.write(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(output=str(out),verified_files=len(files),external_banks=len(external),prior_files_unchanged=984)))


if __name__=='__main__':main()
