"""Seal actual GPU fresh-fault execution and independent CPU comparisons."""
import json
from pathlib import Path
from experiments.fixed_rule.audit_retimed_holder_prefix_embedding import sha


def main():
    root,fig=Path.cwd(),Path('figs/fixed_rule');out=fig/'retimed_holder_fresh_gpu_execution_evidence_v1.json'
    if out.exists():raise FileExistsError(out)
    prior_path=fig/'retimed_holder_fresh_full_repair_evidence_v1.json'
    prior=json.loads(prior_path.read_text());files=dict(prior['files']);assert len(files)==413
    for path,digest in files.items():assert sha(path)==digest,path
    external=prior['external_bank_sha256']
    for path,digest in external.items():assert sha(path)==digest,path
    def bind(path,expected=None):
        path=Path(path)
        if path.is_absolute():path=path.relative_to(root)
        digest=sha(path);assert expected is None or digest==expected,str(path)
        files[str(path)]=digest
    additions=[prior_path,Path(__file__),Path('Report/fixed_rule/FRESH_GPU_REPLAY.md'),
               Path('Report/fixed_rule/STATUS_BEFORE_FRESH_GPU_REPLAY_20260927.md'),
               Path('gacsca/fixed_rule/retimed_holder_early_flags_gpu.py'),Path('gacsca/fixed_rule/retimed_holder_early_flag_snapshot.py'),
               Path('experiments/fixed_rule/replay_retimed_holder_fresh_repair_gpu.py'),Path('experiments/fixed_rule/audit_retimed_holder_fresh_gpu_replay.py'),
               Path('tests/fixed_rule/test_retimed_holder_early_flag_snapshot.py')]
    for prefix in ('fresh_repair_gpu','fresh_gpu_audit','early_flags_build','early_flag_snapshot_tests'):
        additions+=list(fig.glob('retimed_holder_'+prefix+'*'))
    for path in additions:bind(path)
    accepted=('fresh_repair_gpu_v1','fresh_gpu_audit_v1')
    for name in accepted:
        path=fig/('retimed_holder_'+name+'.json');doc=json.loads(path.read_text())
        assert doc['passed'] and doc['descriptor_sha256']==prior['descriptor_sha256']
        for source,digest in {**doc['source_sha256'],**doc.get('input_sha256',{}),**doc.get('binary_sha256',{})}.items():bind(source,digest)
        if 'artifact_sha256' in doc:bind(path.with_suffix('.npz'),doc['artifact_sha256'])
        watch=json.loads(path.with_name(path.stem+'_watch.json').read_text())
        assert watch['returncode']==0 and watch['termination_reason'] is None
    gpu=json.loads((fig/'retimed_holder_fresh_repair_gpu_v1.json').read_text())
    audit=json.loads((fig/'retimed_holder_fresh_gpu_audit_v1.json').read_text())
    assert audit['source_receipt_sha256']==sha(fig/'retimed_holder_fresh_repair_gpu_v1.json')
    assert gpu['complete_rejoin'] and gpu['same_time_attachment']['physical_transitions']==0
    assert gpu['same_time_attachment']['flag1_bits']==3657
    assert gpu['explicit_GPU_peak_bound_bytes']<64*1024**2
    for path in (fig/'build').glob('retimed_holder_early_flags_*/*'):
        if path.is_file():bind(path)
    for name in ('early_flags_build_v1','early_flag_snapshot_tests_v2'):
        watch=json.loads((fig/('retimed_holder_'+name+'_watch.json')).read_text())
        assert watch['returncode']==0 and watch['termination_reason'] is None
    assert 'Ran 5 tests' in (fig/'retimed_holder_early_flag_snapshot_tests_v2.log').read_text()
    result=dict(evidence_integrity_verified=True,prior_evidence_files_verified=413,
                files=dict(sorted(files.items())),external_bank_sha256=external,
                accepted_receipts=list(accepted),descriptor_sha256=prior['descriptor_sha256'],ROM_sha256=prior['ROM_sha256'],
                focused_tests_passed=5,actual_GPU_selected_fresh_repair_executed=True,
                complete_rejoin_tick=16989,full_rule_exception_ticks=640,
                subsequent_GPU_factored_physical_ticks=16349,
                lossless_attachment_raw_words=85786624,independent_CPU_final_raw_words=5046272,
                explicit_GPU_peak_bound_bytes=gpu['explicit_GPU_peak_bound_bytes'],
                new_dense_full_ring_run=False,general_noise_theorem=False,full_project_goal_complete=False,
                scope='Actual bounded GPU replay through complete selected fresh-fault repair. '
                      'Full raw exceptions precede a checked lossless flag attachment; later '
                      'GPU procedure/flag execution uses the validated canonical domain. '
                      'CPU saved-state comparisons and exact loaded binary hashes are bound.')
    with out.open('x') as stream:stream.write(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(output=str(out),verified_files=len(files),prior_files_unchanged=413,external_banks_verified=len(external))))


if __name__=='__main__':main()
