"""Seal complete terminal identity, physical comparisons and retained depth two."""
import hashlib
import json
from pathlib import Path


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(8*1024**2),b''):h.update(block)
    return h.hexdigest()


def main():
    fig=Path('figs/fixed_rule');prior_path=fig/'compact16_holder_gpu_evidence_v1.json';out=fig/'compact16_holder_endpoints_evidence_v1.json'
    if out.exists():raise FileExistsError(out)
    prior=json.loads(prior_path.read_text());files=dict(prior['files']);external=dict(prior['external_bank_sha256'])
    assert len(files)==775
    for path,digest in {**files,**external}.items():assert sha(path)==digest,path
    def bind(path,expected=None,large=False):
        path=Path(path)
        if path.is_absolute():path=path.relative_to(Path.cwd())
        digest=sha(path);assert expected is None or digest==expected,str(path)
        target=external if large else files
        assert str(path) not in target or target[str(path)]==digest,str(path)
        target[str(path)]=digest
    names=('terminal_layout','terminal_audit','endpoint','terminal_tests','endpoint_tests','endpoint_tiles_tests','streamed_depth2','streamed_depth2_audit','all_scratch')
    docs={}
    for name in names:
        stem='compact16_holder_'+name+'_v1';watch=fig/(stem+'_watch.json');record=json.loads(watch.read_text())
        assert record['returncode']==0 and record['termination_reason'] is None
        bind(watch);bind(fig/(stem+'.log'))
        receipt=fig/(stem+'.json')
        if receipt.exists():
            doc=json.loads(receipt.read_text());assert doc['passed'];docs[name]=doc;bind(receipt)
            if 'descriptor_sha256' in doc:assert doc['descriptor_sha256']==prior['candidate_descriptor_sha256']
            if 'rom_sha256' in doc:assert doc['rom_sha256']==prior['candidate_ROM_sha256']
            for source,digest in doc.get('source_sha256',{}).items():bind(source,digest)
            for reference,digest in doc.get('references',{}).items():bind(reference,digest)
            if 'artifact' in doc:bind(doc['artifact'],doc['artifact_sha256'])
            if 'binary' in doc:
                bind(doc['binary'],doc['binary_sha256'])
                for path in Path(doc['binary']).parent.iterdir():
                    if path.is_file():bind(path)
    layout=docs['terminal_layout'];assert layout['memory_words']==3447 and layout['metadata_queries']==98
    assert docs['terminal_audit']['distinguishing_witness']['different_retained_bank_words']==28
    assert len(docs['endpoint']['cases'])==4
    nested=docs['streamed_depth2'];assert nested['initial_encoded_depth']==2 and nested['periods']==2
    assert nested['physical_sites']==268435456 and nested['represented_physical_ticks']==2305843009213693952
    assert nested['complete_bottom_banks_retained'] and nested['no_host_simulated_transition']
    bind(nested['initial_info_path'],nested['initial_info_sha256'])
    bind(nested['small_artifact_path'],nested['small_artifact_sha256'])
    for path,digest in nested['bank_sha256'].items():bind(path,digest,large=True)
    assert sum(row['all_bank_words_independently_recomputed'] for row in docs['all_scratch']['cases'])==113115136
    assert docs['all_scratch']['reference_sha256']==sha(fig/'compact16_holder_streamed_depth2_v1.json')
    for name,count in (('terminal_tests',5),('endpoint_tests',2),('endpoint_tiles_tests',6)):
        log=(fig/('compact16_holder_'+name+'_v1.log')).read_text()
        assert f'Ran {count} tests' in log and '\nOK\n' in log
    for name in ('terminal_reference','terminal_dag','terminal_checks','terminal_image','endpoint_gpu','endpoint_tiles','endpoint_image_array'):
        for extension in ('.py','.cu'):
            path=Path('gacsca/fixed_rule')/('compact16_holder_'+name+extension)
            if path.exists():bind(path)
    for name in ('certify_compact16_holder_terminal_layout','audit_compact16_holder_terminal','validate_compact16_holder_endpoint','run_compact16_holder_streamed_depth2','audit_compact16_holder_streamed_depth2','audit_compact16_holder_all_scratch'):
        bind(Path('experiments/fixed_rule')/(name+'.py'))
    for name in ('terminal','endpoint_gpu','endpoint_tiles'):bind(Path('tests/fixed_rule')/('test_compact16_holder_'+name+'.py'))
    for path in (prior_path,Path(__file__),Path('Report/fixed_rule/COMPACT16_ENDPOINTS.md'),Path('Report/fixed_rule/STATUS_BEFORE_COMPACT16_ENDPOINT_20260927.md')):bind(path)
    result=dict(evidence_integrity_verified=True,prior_evidence_files_verified=775,files=dict(sorted(files.items())),external_bank_sha256=external,
                candidate_descriptor_sha256=prior['candidate_descriptor_sha256'],candidate_ROM_sha256=prior['candidate_ROM_sha256'],
                descriptor_sha256=prior['descriptor_sha256'],ROM_sha256=prior['ROM_sha256'],Q=16384,U=1073741824,
                focused_tests_passed=13,physical_boundary_comparisons=4,complete_compact_depth_two_endpoints=2,
                periodic_top_cells=1,complete_depth_two_bank_words_independently_recomputed=113115136,
                literal_U_squared_replay=False,general_backend_equivalence=False,general_noise_theorem=False,full_project_goal_complete=False)
    with out.open('x') as stream:stream.write(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(output=str(out),verified_files=len(files),external_banks=len(external),prior_files_unchanged=775)))


if __name__=='__main__':main()
