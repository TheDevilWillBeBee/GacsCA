"""Seal first optimized-ROM candidate, failed trials, and prior immutable evidence."""
import json
from pathlib import Path
from experiments.fixed_rule.run_compact16_holder_streamed_depth2 import sha


def main():
    fig=Path('figs/fixed_rule');prior_path=fig/'compact16_holder_upper_repair_evidence_v1.json';out=fig/'compact16_compiler_optimization_evidence_v2.json'
    if out.exists():raise FileExistsError(out)
    prior=json.loads(prior_path.read_text());files=dict(prior['files']);external=prior['external_bank_sha256']
    assert len(files)==1086 and len(external)==9
    for path,digest in {**files,**external}.items():assert sha(path)==digest,path
    def bind(path,expected=None):
        path=Path(path)
        if path.is_absolute():path=path.relative_to(Path.cwd())
        digest=sha(path);assert expected is None or digest==expected,str(path)
        assert str(path) not in files or files[str(path)]==digest,str(path)
        files[str(path)]=digest
    for path in fig.glob('compact16_compiler_*'):
        if path.is_file() and not path.name.startswith('compact16_compiler_optimization_evidence_v2'):bind(path)
    for path in fig.glob('word_boolean_cuts_*'):
        if path.is_file():bind(path)
    bind(fig/'boolean_cuts_initial_rejected.json')
    for path in (Path('gacsca/fixed_rule')/'word_boolean_cuts.py',Path('gacsca/fixed_rule')/'word_dag_order.py',
                 Path('gacsca/fixed_rule')/'word_lowbit_optimization.py',Path('gacsca/fixed_rule')/'compact16_compiler_candidate.py',
                 Path('gacsca/fixed_rule')/'compact16_holder_compiler_program.py'):
        bind(path)
    for path in Path('experiments/fixed_rule').glob('*compact16*compiler*.py'):
        if path.name!='bounded_cuda_probe.py':bind(path)
    for path in Path('experiments/fixed_rule').glob('probe_compact16_compiler_*.py'):bind(path)
    for path in Path('tests/fixed_rule').glob('test_compact16_compiler_candidate*.py'):bind(path)
    for path in (prior_path,Path(__file__),Path('Report/fixed_rule/COMPACT16_COMPILER_OPTIMIZATION.md'),
                 Path('Report/fixed_rule/STATUS_BEFORE_COMPACT16_COMPILER_OPTIMIZATION_20260928.md'),
                 Path('Report/fixed_rule/COMPACT16_COMPILER_SEAL_CORRECTION.md')):bind(path)
    search=json.loads((fig/'compact16_compiler_search_v2.json').read_text());rom=json.loads((fig/'compact16_compiler_rom_v3.json').read_text())
    paths=json.loads((fig/'compact16_compiler_paths_v3.json').read_text());hits=json.loads((fig/'compact16_compiler_meta_hit_v3.json').read_text())
    assert search['passed'] and rom['passed'] and paths['passed'] and hits['passed']
    assert search['best']['description_sha256']==rom['cost']['description_sha256']
    assert search['best']['controller_path_ticks']==811855585 and rom['controller_ticks_saved']==7303568
    assert rom['core_cells_saved']==73 and rom['ROM_sha256']==paths['ROM']['rom_sha256']
    assert rom['physical_descriptor_sha256']==prior['candidate_descriptor_sha256']
    assert hits['query_addresses']==[1,3396,3397]
    assert rom['search_receipt_sha256']==sha(fig/'compact16_compiler_search_v2.json')
    for receipt in (search,rom,paths,hits):
        for path,digest in receipt.get('source_sha256',{}).items():bind(path,digest)
    baseline_search=json.loads((fig/'compact16_compiler_search_v1.json').read_text())
    assert baseline_search['source_sha256']['/scratch/Ehsan/Projects/GacsCA/gacsca/fixed_rule/word_boolean_cuts.py']==sha(fig/'word_boolean_cuts_before_label_check.py')
    for stem in ('compact16_compiler_search_v2','compact16_compiler_rom_v3','compact16_compiler_tests_v2','compact16_compiler_paths_v3','compact16_compiler_meta_hit_v3'):
        watch=json.loads((fig/(stem+'_watch.json')).read_text());assert watch['returncode']==0 and watch['termination_reason'] is None
    log=(fig/'compact16_compiler_tests_v2.log').read_text();assert 'Ran 3 tests' in log and '\nOK\n' in log
    for stem in ('compact16_compiler_rom_v1','compact16_compiler_paths_v1','compact16_compiler_paths_v2',
                 'compact16_compiler_meta_hit_v1','compact16_compiler_meta_hit_v2','compact16_compiler_tests_v1'):
        watch=json.loads((fig/(stem+'_watch.json')).read_text());assert watch['returncode']==1 and watch['termination_reason'] is None
    result=dict(first_seal_self_log_hash_invalid=True,evidence_integrity_verified=True,prior_evidence_files_verified=1086,
                files=dict(sorted(files.items())),external_bank_sha256=external,
                physical_descriptor_sha256=prior['candidate_descriptor_sha256'],
                baseline_ROM_sha256=prior['candidate_ROM_sha256'],optimized_ROM_sha256=rom['ROM_sha256'],
                Q=16384,U=1073741824,core_cells_saved=73,controller_ticks_saved=7303568,
                complete_symbolic_own_ROM=True,representative_physical_paths=True,
                complete_new_ROM_physical_period_executed=False,new_Q_or_U_proved=False,
                failed_experiments_preserved=True)
    with out.open('x') as stream:stream.write(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(output=str(out),files=len(files),prior_unchanged=1086,external_banks=len(external))))


if __name__=='__main__':main()
