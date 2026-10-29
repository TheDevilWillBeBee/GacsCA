"""Read-only actual-rule identity, provenance and complete GAW9 replay."""
from pathlib import Path
from dataclasses import asdict
import hashlib,importlib.util,json,subprocess,sys,tempfile,time
ROOT=Path(__file__).resolve().parents[4];S=Path(__file__).resolve().parent
D=ROOT/'figs/gray_counterexamples/unregistered_gaw9'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    start=time.monotonic();manifest_path=D/'GAW9_standalone_assets.json'
    manifest=json.loads(manifest_path.read_text());assets=manifest['assets_sha256']
    for name,h in assets.items():assert sha(ROOT/name)==h,('asset mismatch',name)
    certificate=json.loads((D/'GAW9_native_factor_certificate.json').read_text())
    assert certificate['proof_sha256']==sha(S/'GAW9_ACTUAL_NATIVE_FACTOR.md')
    assert certificate['receipt_sha256']==sha(D/'GAW9_native_factor_receipt.json')
    assert (certificate['Q'],certificate['U'],certificate['error_lambda'],certificate['error_separation'])==(8192,1048576,24,104)
    for key in ('actual_recursively_intact_H','same_chronological_physical_error_history',
        'birth_clock_restriction_explicit','actual_Info_Workspace_factor_proved',
        'actual_Head_Out_courier_zero_contract_proved','infinite_exterior_and_geometry_absorption_proved',
        'exact140_case_geometry_envelope_replay','actual_changed_support_original_c104_real1',
        'actual_nonzero_WF_source_reachable','actual_shifted_five_copy_late_birth_reachable',
        'initial_checker_summary_failure_provenance_preserved'):
        assert certificate[key],key
    for key in ('all_admitted_payloads_geometry_repair_proved','all_legal_Age_control_repair_proved',
        'Flags_U_recovery_proved','History_decoder_or_whole_period_map_proved','all_real1_repair_proved',
        'Gray_or_G17_refutation','iid_reliability_or_failure','shorter_U_proved','new_rule_created',
        'active_rule_modified','registered_main_modified'):
        assert not certificate[key],key
    assert certificate['admitted_legal_Age_count']==983040
    # Retained source/binary equality; temporary outputs never replace assets.
    with tempfile.TemporaryDirectory(prefix='gaw9_readonly_') as td:
        flags=['gcc','-O3','-std=c11','-Wall','-Wextra','-shared','-fPIC']
        for source,binary in (('gaw9_native_info.c','gaw9_native_info.so'),
                              ('gaw9_geometry_query.c','gaw9_geometry_query.so')):
            output=Path(td)/binary
            subprocess.run(flags+[str(S/source),'-o',str(output)],check=True)
            assert sha(output)==sha(D/binary),('projection binary identity',source)
    original=(S/'gaw9_native_info.c').read_text()
    query=(S/'gaw9_geometry_query.c').read_text()
    generated=original.replace('if(!gc&&!fc){','if(!gc){')
    generation=json.loads((D/'GAW9_geometry_query_generation.json').read_text())
    assert generation['physical_factor_changed'] is False
    assert generation['original_source_sha256']==sha(S/'gaw9_native_info.c')
    assert generation['geometry_query_source_sha256']==sha(S/'gaw9_geometry_query.c')
    prefix='/* Same exact factor; geometry-only query stop. Native canonical/common\n * geometry is absorbing for arbitrary subsequent flags/workspace. */\n'
    assert query==prefix+generated
    failure=json.loads((D/'GAW9_recovery_bound_failure_provenance.json').read_text())
    assert not failure['simulation_or_rule_affected'] and not failure['original_campaigns_changed']
    for name,h in failure['files'].items():assert sha(ROOT/name)==h,('retained receipt assertion failure',name)
    previous_path=ROOT/'Report/proofs/gray_counterexamples/unregistered_gaw2/validate_gaw2_period_v2.py'
    sys.path.insert(0,str(previous_path.parent));spec=importlib.util.spec_from_file_location('gaw2_for_gaw9',previous_path)
    previous=importlib.util.module_from_spec(spec);spec.loader.exec_module(previous);previous.main()
    sys.path.insert(0,str(S));import check_gaw9_native_factor as checker
    rom=json.loads((ROOT/'figs/gray_counterexamples/unregistered_gaw2/GAW2R_rom.json').read_text())
    rom['dictionary']=[int(v,0) if isinstance(v,str) else v for v in rom['dictionary']]
    assert json.loads(json.dumps(asdict(checker.own.ROM)))==rom,'actual physical own ROM mismatch'
    result=checker.main(write=False)
    assert len(result['cases'])==140
    assert result['maximum_mixed_geometry_quiet']==5115 and result['maximum_uniform_geometry_quiet']==2736
    for case in result['cases']:
        assert case['classification']['level1'] and case['classification']['level0']==0
        assert case['geometry_quiet_absorbing_proved'] and case['original_4Q_geometry_envelope_instance']
    for name,h in assets.items():assert sha(ROOT/name)==h,('read-only replay changed asset',name)
    print(json.dumps(dict(passed=True,assets_verified=len(assets),actual_rule_ROM_equal=True,
        exact140_histories_replayed=True,full_local_R_cofactors=result['actual_full_local_R_cofactors'],
        exact_updated_sites=result['exact_updated_sites'],geometry_quiet_by=5115,
        actual_nonzero_Workspace_source=True,actual_shifted_five_copy_birth=True,
        History_decoder_or_Gray_iid_or_shorter_U=False,
        checkpoint_sha256=sha(manifest_path),elapsed_seconds=time.monotonic()-start)),flush=True)

if __name__=='__main__':main()
