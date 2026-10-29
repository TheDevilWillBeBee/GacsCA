"""Read-only GAW21 two-record proof contracts and actual three-record replay."""
from pathlib import Path
import hashlib,importlib.util,json,sys,time
import check_gaw21_two_raw_records as two
import check_gaw21_three_record_witness as three
S=Path(__file__).resolve().parent;ROOT=S.parents[3]
D=ROOT/'figs/gray_counterexamples/unregistered_gaw21'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text())
def assets(m):
    for p,h in m['assets_sha256'].items():assert sha(ROOT/p)==h,(p,'frozen asset differs')

def main():
    started=time.monotonic();mp=D/'GAW21_standalone_assets.json';m=load(mp);assets(m)
    inherited=load(ROOT/m['inherited_manifest']);assets(inherited)
    assert len(inherited['assets_sha256'])==m['inherited_assets']==544
    assert all(m['assets_sha256'][p]==h for p,h in inherited['assets_sha256'].items())
    spec=importlib.util.spec_from_file_location('gaw21_accepted_gaw20_replay',
        S.parent/'unregistered_gaw20/validate_gaw20_all_phase02.py')
    old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
    prior=old.main()
    assert prior['passed'] and prior['assets_verified']==544
    assert prior['exact_unchanged_GAW2R_ROM_dictionary_listing_scalar_local_R']
    # Replayed native/body/cost assumptions keep their frozen original
    # meaning; the new theorem separately discharges a3-clean premise.
    r2=two.main();r3=three.main()
    assert r2==load(D/'GAW21_two_raw_record_certificate.json')
    assert r3==load(D/'GAW21_three_record_witness_certificate.json')
    assert r2['arbitrary_replacement_bits']==99200
    assert r2['actual_scalar_flag_support_checks']==313654
    assert r2['universal_two_unknown_word_quorum_cube_checks']==80
    assert r2['three_clean_adjusted_GF_cube_checks']==120
    assert r2['GAW20_receipt_four_clean_premise_not_silently_assumed']
    fault=r3['fault'];assert fault['points']==len(fault['full_whole_cell_payloads'])==15
    assert fault['shared_E0_points']==fault['shared_actual_E1_points']==0
    assert fault['exact_original_c104_class']=='one actual real2; no actual E0/E1 points'
    assert r3['changed_decoded_normal_record_indices']==[-2,-1,0,1,2]
    assert not r3['three_record_one_period_contraction_identity']
    assert not r3['general_operational_real2_repair_or_eventual_memory_failure_claim']
    assert len(r3['actual_bank_emitted_executions'])==7
    for run in r3['actual_bank_emitted_executions']:
        early,late=run['executions']
        assert early['early'] and not late['early']
        assert early['HALT'] and late['HALT'] and late['updates']==65062
        assert len(late['output_words'])==496 and len(early['output_words'])==6
        assert early['output_words'][2:4]==['0x0','0x0']
        assert 3848<=late['head_range'][0]<=late['head_range'][1]<=4343
    assets(m);assets(inherited)
    r=dict(passed=True,assets_verified=len(m['assets_sha256']),inherited_assets_verified=544,
        Q=8192,U=1048576,error_lambda=24,error_separation=104,
        exact_unchanged_GAW2R_ROM_dictionary_listing_and_local_R=True,
        two_arbitrary_raw_records_99200bit_prepared_contraction_proved=True,
        two_record_family='canonicalGF/commonlegalAge/zero_old_native_flags_and_WF/coherent_SF; lower reset E_raw; any two record locations',
        exact_three_clean_conditional_quorums_padding_congruence_native_helper_and_full_body_replayed=True,
        physical_three_gather_early_zero_flags_and_late_commit_period_lift_proved=True,
        alln_alllocations_intact_shadow_two_record_corollary_proved=True,
        actual_intact_H15_Info_bit_faults_atU_genuine_shared_original_c104_real2=True,
        actual_derived_banks_seven_full_beta65062_runs_and_legal2U_boundary_proved=True,
        three_record_one_period_contraction_counterexample_proved=True,
        five_changed_decoded_normal_records_not_inside_any_fixed_adjacent_pair=True,
        operational_real2_recovery_eventual_memory_failure_or_Gray_iid_counterexample=False,
        uniform_original_class_for_two_record_prepared_family=False,
        generic_malformed_projection_or_arbitrary_lower_geometry_work_repair=False,
        rule_ROM_G17_registered_main_or_accepted_assets_changed=False,
        shorter_U_theorem=False,
        manifest_sha256=sha(mp),two_record_receipt_sha256=sha(D/'GAW21_two_raw_record_certificate.json'),
        three_record_receipt_sha256=sha(D/'GAW21_three_record_witness_certificate.json'),
        proof_sha256=sha(S/'GAW21_TWO_RECORD_REPAIR_THREE_RECORD_WITNESS.md'),
        elapsed_seconds=time.monotonic()-started)
    print(json.dumps(r),flush=True);return r

if __name__=='__main__':main()
