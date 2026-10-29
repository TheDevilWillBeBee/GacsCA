"""Read-only exact actual late-SF replay, legal-padding audit and provenance."""
from pathlib import Path
from dataclasses import asdict
import hashlib,importlib.util,json,re,sys,time
ROOT=Path(__file__).resolve().parents[4];S=Path(__file__).resolve().parent
D=ROOT/'figs/gray_counterexamples/unregistered_gaw12'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    start=time.monotonic();mp=D/'GAW12_standalone_assets.json'
    assets=json.loads(mp.read_text())['assets_sha256']
    for name,h in assets.items():assert sha(ROOT/name)==h,('asset mismatch',name)
    certificate=json.loads((D/'GAW12_active_sf_certificate.json').read_text())
    assert certificate['proof_sha256']==sha(S/'GAW12_ACTIVE_SF_CONFINEMENT.md')
    assert certificate['checker_sha256']==sha(S/'check_gaw12_active_sf.py')
    assert certificate['validator_sha256']==sha(Path(__file__))
    assert certificate['receipt_sha256']==sha(D/'GAW12_active_sf_discovery.json')
    assert (certificate['Q'],certificate['U'],certificate['error_lambda'],certificate['error_separation'])==(8192,1048576,24,104)
    for name in ('actual_recursively_intact_H','actual_chronological4096_update_prefix',
        'same_original_c104_real1_physical_history','full_raw_holder_local_R_factor',
        'general_late_SF_only_fixed_adjacent_pair_confinement',
        'conditional_legal_record_complete2U_corollary',
        'all_six_selected_histories_complete2U_shadow',
        'selected_high_padding_boundary_outside_legal_E',
        'selected_high_padding_18_actual_second_bank_executions'):
        assert certificate[name],name
    for name in ('arbitrary_SF_fault_legal_E_at_U','general_malformed_record_repair',
        'earlier_gather_SF_faults_covered','mixed_native_faults_covered',
        'general_real1_or_higher_repair','Gray_G17_or_operational_counterexample',
        'iid_reliability_or_failure','shorter_U','new_rule_created',
        'active_rule_modified','registered_main_modified'):
        assert not certificate[name],name
    assert certificate['general_theorem_error_rows']==[102*8192+2,120*8192]
    assert certificate['general_theorem_native_replacements']=='retain all six actual native fields'
    for rel in re.findall(r'\]\(([^)]+)\)',(S/'GAW12_ACTIVE_SF_CONFINEMENT.md').read_text()):
        assert (S/rel).exists(),('broken proof link',rel)
    prior=ROOT/'Report/proofs/gray_counterexamples/unregistered_gaw2/validate_gaw2_period_v2.py'
    sys.path.insert(0,str(prior.parent));spec=importlib.util.spec_from_file_location('gaw2_for_gaw12',prior)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);module.main()
    sys.path.insert(0,str(S));import check_gaw12_active_sf as checker
    rom=json.loads((ROOT/'figs/gray_counterexamples/unregistered_gaw2/GAW2R_rom.json').read_text())
    rom['dictionary']=[int(v,0) if isinstance(v,str) else v for v in rom['dictionary']]
    assert json.loads(json.dumps(asdict(checker.own.ROM)))==rom,'actual own ROM identity'
    result=checker.campaign(write=False,all_cases=True,certify=True)
    assert result['chronological_fault_time']==839681
    assert len(result['cases'])==6
    assert result['actual_intact_H_and_chronological_prefix']
    assert not result['future_tapes_Workspace_or_commands_selected']
    stats=result['source_factor_and_chronological_certificates']
    assert stats['actual_prefix']['actual_last_chronological_prefix_full_local_R_checks']==1008
    assert stats['actual_prefix']['actual17_upper_H_records_to_retained_bank_checks']==992
    assert stats['arbitrary_SF_factor']['actual_full_local_R_arbitrary_SF_cofactors']==96
    assert stats['endpoint_motion']['all_legal_SEEK_targets_at_both_colony_endpoints']==16384
    expected=[[0,1],[0],[1],[],[0],[]]
    for n,c in enumerate(result['cases']):
        initial=c['initial'];boundary=c['actual_U_and_recovery']
        payload=initial['whole_cell_payloads'];assert len(payload)==16
        assert [p['x'] for p in payload]==list(range(c['actual_fault_start'],c['actual_fault_start']+16))
        for p in payload:
            old=[int(v,16) for v in p['old_complete_words']]
            new=[int(v,16) for v in p['replacement_complete_words']]
            assert p['t']==839681 and len(old)==len(new)==496
            assert old!=new and old[:6]==new[:6]
            assert old[:6]==[p['x']%8192,839681,0,0,0,0]
        classification=initial['original_c104_classification']
        assert classification['level0']==0 and classification['level1']
        assert tuple(classification['extent'])==(16,1)
        assert boundary['actual_U_bad_normal_record_receivers']==expected[n]
        assert boundary['complete2U_shadow_proved']
        assert boundary['actual_U_full_local_R_commit_checks']==1057
        assert boundary['first_native_padding_legal']==(n!=4)
        if n!=4:
            assert boundary['actual_U_is_E_Cprime_Aprime']
            assert boundary['noiseless_next_period_applies_to_derived_boundary']
            assert len(boundary['actual_next_upper_full_local_R_checks'])==18
        else:
            assert 'actual_U_is_E_Cprime_Aprime' not in boundary
            words=[int(v,16) for v in boundary['actual_U_normal_raw_words']['0']]
            assert words[:6]==[1<<99]*6
            executions=boundary['selected_unpadded_actual_next_bank_executions']
            assert [e['receiver'] for e in executions]==list(range(-8,10))
            for e in executions:
                assert len(e['actual_derived_input_raw_records'])==17
                assert [int(v,16) for v in e['early']['out_words']][2:4]==[0,0]
                assert e['early']['updates']==150 and e['late']['updates']==65062
                assert [int(v,16) for v in e['late']['out_words']]==checker.k.cell_words(checker.base.next2H(e['receiver']))
                assert checker.P<=e['late']['head_min']<=e['late']['head_max']<checker.P+496
    crossing=result['cases'][0]
    first=crossing['initial']['first_actual_head_positions_and_packets']
    assert [y for y,p in first]==[4035,8191,8192,12227]
    run=crossing['actual_postfault_interpreter']
    assert run['total_collisions']==2 and run['last_executed_physical_age']==846560
    retained=json.loads((D/'GAW12_active_sf_discovery01.json').read_text())
    assert not retained['cases'][4]['actual_U_and_recovery']['complete2U_shadow_proved']
    failure=json.loads((D/'GAW12_launch_failure.json').read_text())
    assert failure['exit_code']==1 and not failure['rule_failure']
    assert failure['source_sha256']==sha(S/'check_gaw12_active_sf.discovery01.py')
    for name,h in assets.items():assert sha(ROOT/name)==h,('read-only replay changed asset',name)
    print(json.dumps(dict(passed=True,assets_verified=len(assets),actual_frozen_own_ROM_equal=True,
        exact_selected_intact_start_real1_histories=6,chronological_fault_clock=839681,
        actual_prefix_full_local_R_checks=1008,actual_bank_record_checks=992,
        arbitrary_SF_cofactors=96,all_endpoint_SEEK_target_checks=16384,
        actual_first_noisy_full_local_R_checks=sum(c['initial']['actual_first_computed_row_full_local_R_checks'] for c in result['cases']),
        actual_U_full_local_R_checks=6342,selected_malformed_next_banks=18,
        selected_all_complete2U_shadow=True,general_late_only_SF_fixed_pair_theorem=True,
        general_malformed_or_mixed_native_repair=False,Gray_or_iid_or_shorter_U=False,
        manifest_sha256=sha(mp),elapsed_seconds=time.monotonic()-start)),flush=True)

if __name__=='__main__':main()
