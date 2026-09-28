"""Bind audited 63-cell repair and measured costs, preserving prior evidence."""
import json
from pathlib import Path
from experiments.fixed_rule.run_compact16_holder_streamed_depth2 import sha


def main():
    fig=Path('figs/fixed_rule');prior_path=fig/'compact16_holder_all_macrosteps_evidence_v1.json'
    output=fig/'compact16_holder_upper_repair_evidence_v1.json'
    if output.exists():raise FileExistsError(output)
    prior=json.loads(prior_path.read_text());files=dict(prior['files']);external=prior['external_bank_sha256']
    assert len(files)==1050 and len(external)==9
    for path,digest in {**files,**external}.items():assert sha(path)==digest,path
    def bind(path,expected=None):
        path=Path(path)
        if path.is_absolute():path=path.relative_to(Path.cwd())
        digest=sha(path);assert expected is None or digest==expected,str(path)
        assert str(path) not in files or files[str(path)]==digest,str(path)
        files[str(path)]=digest
    docs={}
    for stem in ('coherent_epochs_tests_v1','epoch_signals_v1','encoded_upper_repair_v1','encoded_upper_repair_audit_v1','cost_profile_v1','cost_profile_v2'):
        base='compact16_holder_'+stem
        watch=fig/(base+'_watch.json');record=json.loads(watch.read_text())
        assert record['returncode']==0 and record['termination_reason'] is None
        bind(watch);bind(fig/(base+'.log'));path=fig/(base+'.json')
        if not path.exists():continue
        doc=json.loads(path.read_text());assert doc.get('passed',True);docs[stem]=doc;bind(path)
        assert doc['descriptor_sha256']==prior['candidate_descriptor_sha256']
        for source,digest in doc.get('source_sha256',{}).items():bind(source,digest)
        if 'artifact' in doc:bind(doc['artifact'],doc['artifact_sha256'])
    testlog=(fig/'compact16_holder_coherent_epochs_tests_v1.log').read_text()
    assert 'Ran 5 tests' in testlog and '\nOK\n' in testlog
    audit=docs['encoded_upper_repair_audit_v1'];run=docs['encoded_upper_repair_v1']
    assert audit['reference_sha256']==sha(fig/'compact16_holder_encoded_upper_repair_v1.json')
    assert audit['complete_native_physical_commit_words_checked']==317915136
    assert audit['complete_bank_words_checked']==869904 and audit['independent_SSA_bank_words_checked']==434952
    assert audit['independent_scalar_upper_outputs']==252 and audit['full_Q_reference_repair_cone_matches']
    assert [x['raw_differences_from_healthy'] for x in audit['periods']]==[32,0]
    assert run['actual_continuous_lower_work_periods']==2 and run['no_reencoding_between_periods']
    assert sha(run['fixture'])==run['fixture_sha256']
    proof=docs['epoch_signals_v1'];assert proof['independent_bits']==123 and proof['excluded_old_age']==495999999
    assert proof['complete_procedure_outputs_checked']==90 and proof['complete_procedure_Signal_input_dependencies']==0
    for kind,key in (('independent','unchanged_controller_source_sha256'),('gather','unchanged_gather_source_sha256')):
        bind('gacsca/fixed_rule/compact16_holder_resident_'+kind+'.cu',proof[key])
    assert docs['cost_profile_v2']['controller_path_ticks_per_period']==819159153
    assert docs['cost_profile_v2']['controller_path_ticks_per_period']-docs['cost_profile_v1']['controller_path_ticks_per_period']==5522
    builds=list((fig/'build').glob('compact16_holder_coherent_epochs_*'));assert len(builds)==1
    for directory in builds:
        for path in directory.iterdir():
            if path.is_file():bind(path)
    for path in (prior_path,Path(__file__),Path('tests/fixed_rule/test_compact16_holder_coherent_epochs.py'),
                 Path('Report/fixed_rule/COMPACT16_UPPER_REPAIR_AUDIT_AND_OPTIMIZATION.md'),
                 Path('Report/fixed_rule/STATUS_BEFORE_COMPACT16_UPPER_REPAIR_AUDIT_20260928.md')):bind(path)
    result=dict(evidence_integrity_verified=True,prior_evidence_files_verified=1050,
                files=dict(sorted(files.items())),external_bank_sha256=external,
                candidate_descriptor_sha256=prior['candidate_descriptor_sha256'],candidate_ROM_sha256=prior['candidate_ROM_sha256'],
                descriptor_sha256=prior['descriptor_sha256'],ROM_sha256=prior['ROM_sha256'],Q=16384,U=1073741824,
                focused_tests_passed=5,encoded_upper_sites=63,continuous_lower_periods=2,
                complete_repair_audited=True,all_commit_raw_words=317915136,independent_scalar_upper_outputs=252,
                complete_bank_words_checked=869904,independent_SSA_bank_words_checked=434952,
                cost_profile_v1_omitted_forcing_halt_preserved=True,controller_path_ticks_per_period=819159153,
                no_new_stochastic_runs=True,general_amplification_proved=False,full_project_goal_complete=False)
    with output.open('x') as stream:stream.write(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(output=str(output),verified_files=len(files),prior_files_unchanged=1050,external_banks=len(external))))


if __name__=='__main__':main()
