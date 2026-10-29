"""Read-only provenance, actual-ROM identity and complete GAW8 replay."""
from pathlib import Path
from dataclasses import asdict
import hashlib,importlib.util,json,subprocess,sys,tempfile,time
ROOT=Path(__file__).resolve().parents[4];S=Path(__file__).resolve().parent
D=ROOT/'figs/gray_counterexamples/unregistered_gaw8'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    start=time.monotonic();manifest_path=D/'GAW8_standalone_assets.json'
    manifest=json.loads(manifest_path.read_text());assets=manifest['assets_sha256']
    for name,h in assets.items():assert sha(ROOT/name)==h,('asset mismatch',name)
    certificate=json.loads((D/'GAW8_mixed_clock_certificate.json').read_text())
    assert certificate['proof_sha256']==sha(S/'GAW8_MIXED_CLOCK_REPAIR.md')
    assert certificate['receipt_sha256']==sha(D/'GAW8_mixed_clock_repair_receipt.json')
    assert (certificate['Q'],certificate['U'],certificate['error_lambda'],certificate['error_separation'])==(8192,1048576,24,104)
    for key in ('actual_recursively_intact_H','same_chronological_physical_error_history',
        'actual_source_phase_interval_proved','actual_new_Workspace_zero_derived',
        'canonical_GF_native_factor_proved','exact795_case_event_replay',
        'actual_changed_support_original_c104_real1','complete_global_shadow_before97Q',
        'first_U_and_all_later_physical_decoded_shadow','integer_Q_translates_proved',
        'initial_query_stop_provenance_preserved'):
        assert certificate[key],key
    for key in ('arbitrary_full_range_Age_control_repair_proved','mixed_GF_SF_repair_proved',
        'all_real1_repair_proved','Gray_or_G17_refutation','iid_reliability_or_failure',
        'shorter_U_proved','new_rule_created','active_rule_modified','registered_main_modified'):
        assert not certificate[key],key
    # Exact initial and extended projection identity. Compiler outputs are
    # temporary and do not replace any retained simulator or receipt.
    with tempfile.TemporaryDirectory(prefix='gaw8_readonly_') as td:
        flags=['gcc','-O3','-std=c11','-Wall','-Wextra','-shared','-fPIC']
        for source,binary in (('gaw8_categorical_native.c','gaw8_categorical_native.so'),
                              ('gaw8_categorical_native_initial.c','gaw8_categorical_native_initial.so')):
            output=Path(td)/binary
            compile_source=S/source
            if source.endswith('_initial.c'):
                # The retained initial binary was compiled before the
                # archive copy was given its _initial filename. GCC emits
                # the source basename in ELF's local FILE symbol. Restore
                # that basename in a temporary copy, preserving every byte
                # of the retained source; do not strip/change the binary.
                initial_dir=Path(td)/'initial_original_basename';initial_dir.mkdir()
                compile_source=initial_dir/'gaw8_categorical_native.c'
                compile_source.write_bytes((S/source).read_bytes())
            subprocess.run(flags+[str(compile_source),'-o',str(output)],check=True)
            assert sha(output)==sha(D/binary),('projection binary identity',source)
    failure=json.loads((D/'GAW8_basename_failure_provenance.json').read_text())
    assert not failure['mathematical_result_affected']
    for name,h in failure['files'].items():assert sha(ROOT/name)==h,('retained initial replay failure',name)
    previous_path=ROOT/'Report/proofs/gray_counterexamples/unregistered_gaw2/validate_gaw2_period_v2.py'
    sys.path.insert(0,str(previous_path.parent));spec=importlib.util.spec_from_file_location('gaw2_for_gaw8',previous_path)
    previous=importlib.util.module_from_spec(spec);spec.loader.exec_module(previous);previous.main()
    sys.path.insert(0,str(S));import check_gaw8_mixed_clock_repair as checker
    rom=json.loads((ROOT/'figs/gray_counterexamples/unregistered_gaw2/GAW2R_rom.json').read_text())
    rom['dictionary']=[int(v,0) if isinstance(v,str) else v for v in rom['dictionary']]
    assert json.loads(json.dumps(asdict(checker.own.ROM)))==rom,'actual physical own ROM mismatch'
    result=checker.main(write=False)
    assert len(result['cases'])==795 and result['maximum_whole_raw_shadow_recovery']==8182
    assert result['maximum_clock_recovery']==5111
    for case in result['cases']:
        assert case['actual_classification']['level1'] and case['actual_classification']['level0']==0
        assert case['complete_global_shadow_at_native_quiet'] and case['first_U_and_all_later_decodes_shadow']
    for name,h in assets.items():assert sha(ROOT/name)==h,('read-only replay changed asset',name)
    print(json.dumps(dict(passed=True,assets_verified=len(assets),actual_rule_ROM_equal=True,
        exact795_histories_replayed=True,full_local_R_checks=result['actual_phase_interval_cofactors']['actual_full_local_R_checks'],
        scalar_checks=result['actual_native_cofactors']['actual_scalar_checks'],
        event_intervals=result['exact_event_intervals'],complete_whole_raw_shadow_by=8182,
        complete_U_and_all_later_decoded_shadow=True,Gray_iid_or_shorter_U=False,
        checkpoint_sha256=sha(manifest_path),elapsed_seconds=time.monotonic()-start)),flush=True)

if __name__=='__main__':main()
