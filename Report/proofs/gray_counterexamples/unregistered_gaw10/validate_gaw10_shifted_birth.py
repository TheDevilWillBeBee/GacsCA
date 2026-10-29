"""Read-only provenance, total-rule identity and actual GAW10 repair replay."""
from pathlib import Path
from dataclasses import asdict
import hashlib,importlib.util,json,subprocess,sys,tempfile,time
ROOT=Path(__file__).resolve().parents[4];S=Path(__file__).resolve().parent
D=ROOT/'figs/gray_counterexamples/unregistered_gaw10'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    start=time.monotonic();manifest_path=D/'GAW10_standalone_assets.json'
    manifest=json.loads(manifest_path.read_text());assets=manifest['assets_sha256']
    for name,h in assets.items():assert sha(ROOT/name)==h,('asset mismatch',name)
    cert=json.loads((D/'GAW10_shifted_birth_certificate.json').read_text())
    assert cert['proof_sha256']==sha(S/'GAW10_SHIFTED_BIRTH_REPAIR.md')
    assert cert['receipt_sha256']==sha(D/'GAW10_shifted_birth_receipt.json')
    assert (cert['Q'],cert['U'],cert['error_lambda'],cert['error_separation'])==(8192,1048576,24,104)
    for key in ('actual_recursively_intact_H','same_chronological_physical_error_history',
        'actual_original_c104_real1','full_actual_local_R_prefix_replayed',
        'extra_Head_disappearance_and_no_write_proved','actual_postbirth_Info_History_Workspace_factor_proved',
        'actual_same_history_bank_derived','actual_reset_birth_commit_composition_proved',
        'one_permitted_upper_Flag1_error_at_U','complete_global_raw_shadow_at2U_and_all_later'):
        assert cert[key],key
    for key in ('arbitrary_birth_near_real1_repair_proved','direct_whole_period_grid_simulation_claimed',
        'Gray_or_G17_refutation','iid_reliability_or_failure','shorter_U_proved',
        'new_rule_created','active_rule_modified','registered_main_modified'):
        assert not cert[key],key
    with tempfile.TemporaryDirectory(prefix='gaw10_readonly_') as td:
        output=Path(td)/'gaw10_postbirth_factor.so'
        subprocess.run(['gcc','-O3','-std=c11','-Wall','-Wextra','-shared','-fPIC',
            str(S/'gaw10_postbirth_factor.c'),'-o',str(output)],check=True)
        assert sha(output)==sha(D/'gaw10_postbirth_factor.so'),'factor simulator binary identity'
    generation=json.loads((D/'GAW10_factor_generation.json').read_text())
    assert not generation['actual_rule_changed']
    assert sha(ROOT/generation['parent_source'])==generation['parent_source_sha256']
    assert sha(S/'gaw10_postbirth_factor.c')==generation['new_source_sha256']
    old=(ROOT/generation['parent_source']).read_text();new=(S/'gaw10_postbirth_factor.c').read_text()
    # Every native scalar equation is literally retained. Extra keeper
    # storage and query-clock changes occur outside this native block.
    def native_block(v):return v[v.index('static Site native('):v.index('static int voteinfo(')]
    assert native_block(old)==native_block(new),'native equation departure'
    previous_path=ROOT/'Report/proofs/gray_counterexamples/unregistered_gaw2/validate_gaw2_period_v2.py'
    sys.path.insert(0,str(previous_path.parent));spec=importlib.util.spec_from_file_location('gaw2_for_gaw10',previous_path)
    previous=importlib.util.module_from_spec(spec);spec.loader.exec_module(previous);previous.main()
    sys.path.insert(0,str(S));import check_gaw10_shifted_birth as checker
    rom=json.loads((ROOT/'figs/gray_counterexamples/unregistered_gaw2/GAW2R_rom.json').read_text())
    rom['dictionary']=[int(v,0) if isinstance(v,str) else v for v in rom['dictionary']]
    assert json.loads(json.dumps(asdict(checker.own.ROM)))==rom,'actual physical own ROM mismatch'
    result=checker.main(write=False)
    assert result['whole_cell_payload']['classification']['level1']
    assert result['whole_cell_payload']['classification']['level0']==0
    factor=result['actual_native_Info_History_continuation'];output=result['actual_bank_and_output_map']
    assert factor['first_geometry_quiet']+3==1450 and factor['first_native_quiet']+3==5545
    assert factor['final_coherent_erased_logical_coordinates']==list(range(3842,8190))
    assert factor['updates']==51493604
    assert output['first_boundary_bad_upper_cells']==[0] and output['sole_upper_difference_Field_Flag1_at_cell0']
    assert output['complete2U_shadow'] and len(output['actual_second_upper_transitions'])==17
    assert output['actual_late_receiver_executions'][0]['actual_execution']['updates']==65117
    for name,h in assets.items():assert sha(ROOT/name)==h,('read-only replay changed asset',name)
    print(json.dumps(dict(passed=True,assets_verified=len(assets),actual_rule_ROM_equal=True,
        exact_intact_start_history_replayed=True,extra_Head_counts=[5,2,0],
        postbirth_actual_factor_updates=51493604,geometry_quiet_by=1450,native_flags_quiet_by=5545,
        actual_full_local_R_cofactors=result['actual_postbirth_local_R_cofactors'],
        actual_literal_reset_birth_commit_contracts=output['actual_literal_reset_birth_commit_contracts'],
        late_execution_updates=65117,one_upper_Flag1_error=True,complete2U_and_all_later_shadow=True,
        operational_Gray_iid_or_shorter_U=False,checkpoint_sha256=sha(manifest_path),
        elapsed_seconds=time.monotonic()-start)),flush=True)

if __name__=='__main__':main()
