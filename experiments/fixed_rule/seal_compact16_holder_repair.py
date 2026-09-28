"""Seal timed compact cross-level correction and complete-state rejoin."""
import json
from pathlib import Path
from experiments.fixed_rule.seal_compact16_holder_endpoints import sha


def main():
    fig=Path('figs/fixed_rule');prior_path=fig/'compact16_holder_endpoints_evidence_v1.json';out=fig/'compact16_holder_repair_evidence_v1.json'
    if out.exists():raise FileExistsError(out)
    prior=json.loads(prior_path.read_text());files=dict(prior['files']);external=dict(prior['external_bank_sha256'])
    assert len(files)==831 and len(external)==3
    for path,digest in {**files,**external}.items():assert sha(path)==digest,path
    def bind(path,expected=None,large=False):
        path=Path(path)
        if path.is_absolute():path=path.relative_to(Path.cwd())
        digest=sha(path);assert expected is None or digest==expected,str(path)
        target=external if large else files
        assert str(path) not in target or target[str(path)]==digest,str(path)
        target[str(path)]=digest
    names=('active_faults','timed_depth2_checkpoint','timed_depth2_healthy','timed_depth2_two','timed_depth2_three','timed_prefix','timed_repair_audit','repair_tests')
    docs={}
    for name in names:
        stem='compact16_holder_'+name+'_v1';watch=fig/(stem+'_watch.json');record=json.loads(watch.read_text())
        assert record['returncode']==0 and record['termination_reason'] is None
        bind(watch);bind(fig/(stem+'.log'))
        receipt=fig/(stem+'.json')
        if not receipt.exists():continue
        doc=json.loads(receipt.read_text());assert doc['passed'];docs[name]=doc;bind(receipt)
        if 'descriptor_sha256' in doc:assert doc['descriptor_sha256']==prior['candidate_descriptor_sha256']
        if 'rom_sha256' in doc:assert doc['rom_sha256']==prior['candidate_ROM_sha256']
        for source,digest in doc.get('source_sha256',{}).items():bind(source,digest)
        for path,digest in doc.get('references',{}).items():bind(path,digest)
        for path,digest in doc.get('bank_sha256',{}).items():bind(path,digest,large=True)
        if 'artifact_sha256' in doc:bind(receipt.with_suffix('.npz'),doc['artifact_sha256'])
        if 'small_artifact' in doc:bind(doc['small_artifact'],doc['small_sha256'])
        if 'binary' in doc:bind(doc['binary'],doc['binary_sha256'])
        if 'native_binary' in doc:bind(doc['native_binary'],doc['native_binary_sha256'])
    live=docs['active_faults'];assert live['age']==508479315 and live['rom_instruction']>=live['description_instruction']
    assert live['two_copy_complete_rejoin_after_one_literal_tick'] and live['native_ring_transitions']==6
    assert [row['raw_output_differences'] for row in live['cases']]==[0,15]
    audit=docs['timed_repair_audit'];assert audit['all_bank_words_independently_recomputed']==339345408
    assert audit['all_middle_raw_words_checked']==15138816
    assert [row['differences']['total'] for row in audit['comparisons']]==[56,0]
    assert audit['comparisons'][0]['differences']['history']==42 and audit['comparisons'][0]['differences']['votes']==14
    assert audit['complete_physical_rejoin_by']==545975509301854208
    prefix=docs['timed_prefix'];assert [row['physical_faults'] for row in prefix['cases']]==[4,6,9]
    assert [row['entire_causal_outputs'] for row in prefix['cases']]==[32,38,57]
    assert prefix['checkpoint_receipt_sha256']==sha(fig/'compact16_holder_timed_depth2_checkpoint_v1.json')
    log=(fig/'compact16_holder_repair_tests_v1.log').read_text();assert 'Ran 6 tests' in log and '\nOK\n' in log
    for name in ('active_snapshot','cuda_general_snapshot','checkpoint_pulse'):
        bind(Path('gacsca/fixed_rule')/('compact16_holder_'+name+'.py'))
    for name in ('compact16_holder_active_evaluator_faults','compact16_holder_timed_depth2','audit_compact16_holder_timed_repair','audit_compact16_holder_timed_prefix'):
        bind(Path('experiments/fixed_rule')/(name+'.py'))
    for name in ('checkpoint_pulse','active_checkpoint'):bind(Path('tests/fixed_rule')/('test_compact16_holder_'+name+'.py'))
    for path in (prior_path,Path(__file__),Path('Report/fixed_rule/COMPACT16_TIMED_REPAIR.md'),Path('Report/fixed_rule/STATUS_BEFORE_COMPACT16_REPAIR_20260927.md')):bind(path)
    result=dict(evidence_integrity_verified=True,prior_evidence_files_verified=831,files=dict(sorted(files.items())),external_bank_sha256=external,
                candidate_descriptor_sha256=prior['candidate_descriptor_sha256'],candidate_ROM_sha256=prior['candidate_ROM_sha256'],
                descriptor_sha256=prior['descriptor_sha256'],ROM_sha256=prior['ROM_sha256'],Q=16384,U=1073741824,
                focused_tests_passed=6,actual_live_middle_age=live['age'],timed_lower_bit_fault_cases=[4,6,9,10,15],
                complete_bank_words_independently_recomputed=339345408,
                two_case_retained_difference_words_after_periods=[56,0],three_copy_wrong_middle_raw_words=15,
                literal_U_squared_replay=False,general_noise_theorem=False,full_project_goal_complete=False)
    with out.open('x') as stream:stream.write(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(output=str(out),verified_files=len(files),external_banks=len(external),prior_files_unchanged=831)))


if __name__=='__main__':main()
