"""Preserve prior evidence; bind quantified compact repair and all noise outcomes."""
import itertools
import json
from pathlib import Path
from experiments.fixed_rule.seal_compact16_holder_endpoints import sha


def main():
    fig=Path('figs/fixed_rule');prior_path=fig/'compact16_holder_repair_evidence_v1.json';out=fig/'compact16_holder_repair_theorem_evidence_v1.json'
    if out.exists():raise FileExistsError(out)
    prior=json.loads(prior_path.read_text());files=dict(prior['files']);external=dict(prior['external_bank_sha256'])
    assert len(files)==873 and len(external)==9
    for path,digest in {**files,**external}.items():assert sha(path)==digest,path
    def bind(path,expected=None):
        path=Path(path)
        if path.is_absolute():path=path.relative_to(Path.cwd())
        digest=sha(path);assert expected is None or digest==expected,str(path)
        assert str(path) not in files or files[str(path)]==digest,str(path)
        files[str(path)]=digest
    names=('two_site_geometry','two_tick_repair','sparse_repair_theorem','repair_certificate_tests','high_bit_tests','literal_noise','literal_noise_audit');docs={}
    for name in names:
        stem='compact16_holder_'+name+'_v1';watch=fig/(stem+'_watch.json');record=json.loads(watch.read_text())
        assert record['returncode']==0 and record['termination_reason'] is None
        bind(watch);bind(fig/(stem+'.log'))
        path=fig/(stem+'.json')
        if not path.exists():continue
        doc=json.loads(path.read_text());assert doc['passed'];docs[name]=doc;bind(path)
        if 'descriptor_sha256' in doc:assert doc['descriptor_sha256']==prior['candidate_descriptor_sha256']
        for source,digest in doc.get('source_sha256',{}).items():bind(source,digest)
        for source,digest in doc.get('proof_inputs',{}).items():bind(source,digest)
        if 'artifact' in doc:bind(doc['artifact'],doc['artifact_sha256'])
    geo=docs['two_site_geometry'];assert geo['all_healthy_addresses']==16384 and geo['all_faulty_addresses']==32768
    assert geo['all_healthy_ages']==1073741824 and geo['all_faulty_ages']==4294967296
    assert geo['complete_position_cover'] and len(geo['cases'])==55
    assert {tuple(row['defect_positions']) for row in geo['cases']}==set(itertools.combinations(range(-5,6),2))
    assert all(row['passed'] and row['independent_bits']==146 for row in geo['cases'])
    structure=docs['two_tick_repair'];assert structure['geometry_certificate_sha256']==sha(fig/'compact16_holder_two_site_geometry_v1.json')
    assert structure['cut_groups']==dict(geometry=20,procedure=119,signal=10)
    assert structure['unrestricted_logical_procedure_words'] and structure['no_head_count_assumption']
    theorem=docs['sparse_repair_theorem'];assert theorem['second_tick_all_physical_fields_equal'] and theorem['total_fault_site_count_unrestricted']
    noise=docs['literal_noise'];assert noise['all_samples_retained'] and noise['no_sparsity_filter'] and noise['all_transitions_literal']
    assert len(noise['trial_results'])==24 and [row['recovered'] for row in noise['summaries']]==[8,8,0]
    assert [row['fault_events'] for row in noise['summaries']]==[38,155,831]
    audit=docs['literal_noise_audit'];assert audit['reference_sha256']==sha(fig/'compact16_holder_literal_noise_v1.json')
    assert audit['all_sampled_replacements_checked']==1024 and audit['additional_scalar_outputs']==576
    assert audit['final_complete_raw_words_checked']==1482096
    for name,count in (('repair_certificate_tests',11),('high_bit_tests',1)):
        log=(fig/('compact16_holder_'+name+'_v1.log')).read_text()
        assert (f'Ran {count} '+('test' if count==1 else 'tests')) in log and '\nOK\n' in log
    for name in ('literal_cone','pulse_domain'):bind(Path('gacsca/fixed_rule')/('compact16_holder_'+name+'.py'))
    for name in ('prove_compact16_holder_two_site_geometry','certify_compact16_holder_replica_repair','certify_compact16_holder_two_tick_repair','compose_compact16_holder_sparse_repair','compact16_holder_literal_noise','audit_compact16_holder_literal_noise'):
        bind(Path('experiments/fixed_rule')/(name+'.py'))
    for name in ('two_tick_certificate','sparse_pulse','high_bit_repair'):bind(Path('tests/fixed_rule')/('test_compact16_holder_'+name+'.py'))
    for path in (prior_path,Path(__file__),Path('Report/fixed_rule/COMPACT16_REPAIR_THEOREM_AND_NOISE.md'),Path('Report/fixed_rule/STATUS_BEFORE_COMPACT16_REPAIR_THEOREM_20260927.md')):bind(path)
    bind(Path('experiments/fixed_rule/seal_compact16_holder_repair_theorem.py'))
    failed=fig/'compact16_holder_repair_theorem_seal_v1_watch.json'
    assert json.loads(failed.read_text())['returncode']==1
    bind(failed);bind(fig/'compact16_holder_repair_theorem_seal_v1.log')
    result=dict(evidence_integrity_verified=True,prior_evidence_files_verified=873,files=dict(sorted(files.items())),external_bank_sha256=external,
                candidate_descriptor_sha256=prior['candidate_descriptor_sha256'],candidate_ROM_sha256=prior['candidate_ROM_sha256'],
                descriptor_sha256=prior['descriptor_sha256'],ROM_sha256=prior['ROM_sha256'],Q=16384,U=1073741824,
                focused_tests_passed=12,quantified_geometry_position_pairs=55,arbitrary_full_width_faults=True,
                conditional_distributed_two_tick_repair=True,literal_unfiltered_noise_trials=24,
                noise_recovered_by_deadline=[8,8,0],all_noise_failures_retained=True,GPU_used=False,
                general_noise_threshold=False,full_project_goal_complete=False)
    with out.open('x') as stream:stream.write(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(output=str(out),verified_files=len(files),external_banks=len(external),prior_files_unchanged=873)))


if __name__=='__main__':main()
