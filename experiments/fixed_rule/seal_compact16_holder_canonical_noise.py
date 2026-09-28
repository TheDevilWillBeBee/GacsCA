"""Preserve prior evidence and bind the exact factored/idle macrostep findings."""
import json
from pathlib import Path
from experiments.fixed_rule.run_compact16_holder_streamed_depth2 import sha


def main():
    fig=Path('figs/fixed_rule');prior_path=fig/'compact16_holder_dense_noise_evidence_v1.json';output=fig/'compact16_holder_canonical_noise_evidence_v1.json'
    if output.exists():raise FileExistsError(output)
    prior=json.loads(prior_path.read_text());files=dict(prior['files']);external=prior['external_bank_sha256']
    assert len(files)==935 and len(external)==9
    for path,digest in {**files,**external}.items():assert sha(path)==digest,path
    def bind(path,expected=None):
        path=Path(path)
        if path.is_absolute():path=path.relative_to(Path.cwd())
        digest=sha(path);assert expected is None or digest==expected,str(path)
        assert str(path) not in files or files[str(path)]==digest,str(path)
        files[str(path)]=digest
    docs={}
    for name,version in (('canonical_gpu_tests',1),('canonical_geometry',1),('canonical_noise',1),('late_idle_tests',1),('late_idle_proof',3),('headless_macrostep',1),('canonical_noise_audit',1)):
        stem=f'compact16_holder_{name}_v{version}';watch=fig/(stem+'_watch.json');record=json.loads(watch.read_text())
        assert record['returncode']==0 and record['termination_reason'] is None
        bind(watch);bind(fig/(stem+'.log'));path=fig/(stem+'.json')
        if not path.exists():continue
        doc=json.loads(path.read_text());assert doc['passed'];docs[name]=doc;bind(path)
        if 'descriptor_sha256' in doc:assert doc['descriptor_sha256']==prior['candidate_descriptor_sha256']
        for source,digest in doc.get('source_sha256',{}).items():bind(source,digest)
        if 'artifact' in doc:bind(doc['artifact'],doc['artifact_sha256'])
    for version in (1,2):
        name=f'compact16_holder_late_idle_proof_v{version}';watch=fig/(name+'_watch.json');record=json.loads(watch.read_text())
        assert record['returncode']==1 and record['termination_reason'] is None
        log=fig/(name+'.log');assert 'MemoryError: diagnostic BDD node budget exhausted' in log.read_text()
        bind(watch);bind(log)
        bind(Path('experiments/fixed_rule')/('prove_compact16_holder_late_idle'+('' if version==1 else '_v2')+'.py'))
    for name,count in (('canonical_gpu_tests',4),('late_idle_tests',3)):
        log=(fig/f'compact16_holder_{name}_v1.log').read_text();assert f'Ran {count} tests' in log and '\nOK\n' in log
    geo=docs['canonical_geometry'];assert geo['independent_bits']==88 and geo['independently_arbitrary_primary_flags_and_Wf']==44
    proof=docs['late_idle_proof'];assert proof['independent_bits']==958 and len(proof['complete_procedure_fields_checked'])==18
    assert proof['legal_idle_ages']==[502000001,1073741822] and proof['mutation_Data_bit']==0
    noise=docs['canonical_noise'];assert noise['complete_site_transitions']==2415919104 and noise['every_physical_tick_executed']
    assert noise['explicit_peak_device_bytes']==47411200 and len(noise['trials'])==8
    macro=docs['headless_macrostep'];assert [row['case'] for row in macro['cases']]==[3,7]
    assert all(row['skipped_idle_ticks']==565245588 and row['final_age']==0 and not row['decoded_matches_intended_rule'] for row in macro['cases'])
    audit=docs['canonical_noise_audit'];assert audit['complete_raw_words_checked']==30277632 and audit['scalar_outputs_checked']==340
    assert audit['all_eight_final_flag_planes_zero'] and audit['independently_verified_idle_premises']
    assert all(row['projected_decoded_differences']==33 and row['all_five_Info_copies_agree'] for row in audit['failed_projected_macrosteps'])
    assert audit['reference_sha256']==sha(fig/'compact16_holder_canonical_noise_v1.json')
    assert audit['macrostep_reference_sha256']==sha(fig/'compact16_holder_headless_macrostep_v1.json')
    for kind in ('canonical','late_idle'):
        builds=list((fig/'build').glob('compact16_holder_'+kind+'_*'));assert len(builds)==1
        for path in builds[0].iterdir():
            if path.is_file():bind(path)
    for name in ('canonical_gpu','late_idle_gpu'):
        for suffix in ('.py','.cu'):bind(Path('gacsca/fixed_rule')/('compact16_holder_'+name+suffix))
        bind(Path('tests/fixed_rule')/('test_compact16_holder_'+name+'.py'))
    for path in (prior_path,Path(__file__),Path('Report/fixed_rule/COMPACT16_CANONICAL_NOISE.md'),Path('Report/fixed_rule/STATUS_BEFORE_COMPACT16_CANONICAL_NOISE_20260928.md')):bind(path)
    result=dict(evidence_integrity_verified=True,prior_evidence_files_verified=935,files=dict(sorted(files.items())),external_bank_sha256=external,
                candidate_descriptor_sha256=prior['candidate_descriptor_sha256'],candidate_ROM_sha256=prior['candidate_ROM_sha256'],
                descriptor_sha256=prior['descriptor_sha256'],ROM_sha256=prior['ROM_sha256'],Q=16384,U=1073741824,
                focused_tests_passed=7,canonical_geometry_BDD_bits=88,idle_procedure_BDD_bits=958,
                factored_GPU_site_transitions=2415919104,complete_audit_words=30277632,scalar_audit_outputs=340,
                all_eight_failures_retained=True,actual_failed_projected_macrosteps=[3,7],other_six_macrostep_outcomes_unresolved=True,
                general_noise_threshold=False,full_project_goal_complete=False)
    with output.open('x') as out:out.write(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(output=str(output),verified_files=len(files),external_banks=len(external),prior_files_unchanged=935)))


if __name__=='__main__':main()
