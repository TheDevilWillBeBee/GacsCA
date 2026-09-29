"""Bind literal GPU continuation, independent audit and all prior evidence."""
import json
from pathlib import Path
from experiments.fixed_rule.run_compact16_holder_streamed_depth2 import sha


def main():
    fig=Path('figs/fixed_rule');prior_path=fig/'compact16_holder_repair_theorem_evidence_v1.json'
    output=fig/'compact16_holder_dense_noise_evidence_v1.json'
    if output.exists():raise FileExistsError(output)
    prior=json.loads(prior_path.read_text());files=dict(prior['files']);external=prior['external_bank_sha256']
    assert len(files)==911 and len(external)==9
    for path,digest in {**files,**external}.items():assert sha(path)==digest,path
    def bind(path,expected=None):
        path=Path(path)
        if path.is_absolute():path=path.relative_to(Path.cwd())
        digest=sha(path);assert expected is None or expected==digest,str(path)
        assert str(path) not in files or files[str(path)]==digest,str(path)
        files[str(path)]=digest
    docs={}
    for stem in ('dense_gpu_tests','dense_noise','dense_noise_audit'):
        name='compact16_holder_'+stem+'_v1';watch=fig/(name+'_watch.json');record=json.loads(watch.read_text())
        assert record['returncode']==0 and record['termination_reason'] is None
        bind(watch);bind(fig/(name+'.log'));path=fig/(name+'.json')
        if path.exists():
            doc=json.loads(path.read_text());assert doc['passed'];docs[stem]=doc;bind(path)
            for source,digest in doc.get('source_sha256',{}).items():bind(source,digest)
            if 'artifact' in doc:bind(doc['artifact'],doc['artifact_sha256'])
    doc=docs['dense_noise'];audit=docs['dense_noise_audit']
    assert doc['descriptor_sha256']==prior['candidate_descriptor_sha256']
    assert doc['sites']==16384 and doc['fields']==154 and doc['literal_GPU_site_transitions']==75890688
    assert doc['all_eight_failures_retained'] and doc['all_transitions_literal_complete_GPU']
    assert doc['explicit_peak_device_bytes']==52363264
    assert len(doc['trials'])==8 and all(x['first_checked_rejoin'] is None for x in doc['trials'])
    assert audit['reference_sha256']==sha(fig/'compact16_holder_dense_noise_v1.json')
    assert audit['complete_raw_words_checked']==100925440 and audit['scalar_outputs_checked']==64
    log=(fig/'compact16_holder_dense_gpu_tests_v1.log').read_text();assert 'Ran 4 tests' in log and '\nOK\n' in log
    diagnosis=fig/'compact16_holder_dense_noise_diagnosis_v1.json';diag=json.loads(diagnosis.read_text());assert diag['passed']
    assert diag['reference_sha256']==audit['reference_sha256'];bind(diagnosis);bind(diagnosis.with_suffix('.log'))
    for source,digest in diag['source_sha256'].items():bind(source,digest)
    builds=list((fig/'build').glob('compact16_holder_dense_*'));assert len(builds)==1
    for name in ('dense.so','build.log','compact16_holder_dense_generated.h'):bind(builds[0]/name)
    for path in (prior_path,Path(__file__),Path('tests/fixed_rule/test_compact16_holder_dense_gpu.py'),
                 Path('Report/fixed_rule/COMPACT16_LITERAL_GPU_NOISE.md'),Path('Report/fixed_rule/STATUS_BEFORE_COMPACT16_DENSE_NOISE_20260927.md')):bind(path)
    result=dict(evidence_integrity_verified=True,prior_evidence_files_verified=911,files=dict(sorted(files.items())),external_bank_sha256=external,
                candidate_descriptor_sha256=prior['candidate_descriptor_sha256'],candidate_ROM_sha256=prior['candidate_ROM_sha256'],
                descriptor_sha256=prior['descriptor_sha256'],ROM_sha256=prior['ROM_sha256'],Q=16384,U=1073741824,
                focused_tests_passed=4,literal_GPU_site_transitions=75890688,complete_native_comparison_words=100925440,
                scalar_outputs_checked=64,all_eight_high_rate_failures_retained=True,rejoined_after_520_quiet_ticks=0,
                general_noise_threshold=False,full_project_goal_complete=False)
    with output.open('x') as out:out.write(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(output=str(output),verified_files=len(files),external_banks=len(external),prior_files_unchanged=911)))


if __name__=='__main__':main()
