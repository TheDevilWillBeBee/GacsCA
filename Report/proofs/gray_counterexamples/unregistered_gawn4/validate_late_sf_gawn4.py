"""Issue once, then read-only replay of the written late-SF burst checkpoint."""
from pathlib import Path
import argparse,hashlib,json,sys,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path.insert(0,str(HERE))
import check_late_sf_gawn4 as checks
OUT=ROOT/'figs/gray_counterexamples/unregistered_gawn4'
CERT=OUT/'GAWN4_late_SF_certificate.json'
PROOF=HERE/'GAWN4_LATE_SF_BURST_REPAIR.md'
PRIOR=ROOT/'figs/gray_counterexamples/unregistered_gawn3/GAWN3_pure_E0_certificate.json'
REDUCTION=ROOT/'figs/gray_counterexamples/unregistered_gawn4_reduction_run01.log'
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    started=time.monotonic();p=argparse.ArgumentParser();p.add_argument('--issue',action='store_true');args=p.parse_args()
    if args.issue:assert not CERT.exists(),'never overwrite frozen certificate'
    else:assert CERT.exists(),'initial issue requires --issue'
    assert sha(PRIOR)=='25adad0a7e33f76273cfc2c74bb3c8cbd8e74f4172a2a12245a9285c2f279f65'
    prior=json.loads(PRIOR.read_text());assert len(prior['assets_sha256'])==517
    for name,value in prior['assets_sha256'].items():assert sha(ROOT/name)==value,name
    oldlog=PRIOR.parent/'readonly_run01.log';old=json.loads(oldlog.read_text().splitlines()[-1])
    assert old['passed'] and old['readonly'] and old['assets_verified']==517 and old['certificate_sha256']==sha(PRIOR)
    assert sha(oldlog)=='41a9c1f930a41567e3fe53f2bb4bd4bc77fed7d79837bd37c8131431b7ad687f'
    result=checks.compute(write=False)
    assert result['maximum_spatial_width']==104
    assert (result['fault_first_row'],result['fault_last_row'])==(409602,524287)
    assert (result['intact']['field_cases'],result['intact']['holder_cases'])==(6448,32240)
    assert result['intact']['all13_upper_C1_holder_cases']==325
    assert result['endpoint_shield']['all4096_SEEK_targets_at_both_endpoints']==8192
    assert result['endpoint_shield']['all4096_immutable_RUN_words_times4_boundary_operand_classes_times2_endpoints']==32768
    assert result['endpoint_shield']['selected_invalid_metadata_endpoint_cases']==960
    assert result['quiet_pair']['exhaustive_two_site_flag_payload_cases_at_selected_Address_classes']==33792
    assert result['quiet_pair']['selected_all496_word_full_kernel_pair_cases']==288
    witness=result['actual_witness']
    assert witness['error_support']==[[x,524287] for x in range(1798,1803)]
    assert (witness['first_full_updates'],witness['second_full_updates'])==(41450,40572)
    assert (witness['first_early_updates'],witness['second_early_updates'])==(158,158)
    assets=dict(prior['assets_sha256'])
    for path in (PRIOR,oldlog,PRIOR.parent/'issue_run01.log',PROOF,Path(__file__),Path(checks.__file__),
        OUT/'GAWN4_late_SF_contracts.json',OUT/'GAWN4_actual_padding_witness.json',REDUCTION):
        assets[str(path.relative_to(ROOT))]=sha(path)
    cert=dict(passed=True,proof_sha256=sha(PROOF),checker_sha256=sha(__file__),
        inherited517_asset_provenance_and_accepted_terminal_replay_checked=True,
        all_NEW_intact_field_endpoint_quorum_and_actual_padding_execution_checks_recomputed=True,
        frozen_GAWN2_rule_ROM_widths_schedule_constants_and_G17_unchanged=True,
        Q=4096,U=524288,physical_state_bits=49035,error_lambda=24,error_separation=104,
        arbitrary_upper_C_and_auxiliary_B_first_boundary_confinement_proved=True,
        recursively_intact_H2_with_actual_own_programme_proved=True,
        all13_SF_only_replacements_arbitrary_adaptive_and_incoherent=True,
        native_fields_must_be_retained=True,maximum_spatial_width=104,
        error_first_permitted_row=409602,error_last_permitted_row=524287,
        duration_bound_required=False,other_or_later_errors_permitted=False,
        native_quiet_closure_and_full_coherent_computed_SF_factor_proved=True,
        arbitrary100bit_packet_endpoint_shield_and_one_first_escape_proved=True,
        fixed_adjacent_pair_logical_confinement_with_physical_two_site_halo_proved=True,
        complete_first_boundary_E2_D_encoding_arbitrary_native_padding_proved=True,
        one_quiet_upper_adjacent_pair_full_cell_correction_proved=True,
        complete_unconditional2U_raw_recovery_from_H2_and_future_noiseless_equality_proved=True,
        legal_native_padding_at_U_required=False,
        actual_five_point_original_c104_real1_malformed_GF_word_and_complete2U_instance_proved=True,
        first_selected_full_updates=41450,second_selected_full_updates=40572,
        first_and_second_selected_early_updates=158,
        exact_finite_checks_are_supplements_not_universal_burst_or_iid_experiments=True,
        general_native_changing_real1_earlier_SF_continuing_mixed_or_higher_clusters_proved=False,
        faithful_Gray_positive_iid_epsilon_memory_or_minimum_proved=False,
        global_reliability_established=False,positive_iid_error_rate=None,
        assets_sha256=dict(sorted(assets.items())))
    if args.issue:CERT.write_text(json.dumps(cert,indent=2)+'\n')
    else:assert cert==json.loads(CERT.read_text()),'certificate changed'
    for name,value in assets.items():assert sha(ROOT/name)==value,name
    print(json.dumps(dict(passed=True,readonly=not args.issue,assets_verified=len(assets),
        certificate_sha256=sha(CERT),Q=4096,U=524288,
        universal_late_SF_first_boundary_and_unconditional2U_H2_repair_proved=True,
        native_changing_or_earlier_or_continuing_mixed_or_higher_or_iid_memory_minimum_proved=False,
        actual_five_point_malformed_padding_real1_recovers_completely=True,
        rule_ROM_constants_or_G17_changed=False,seconds=time.monotonic()-started)),flush=True)

if __name__=='__main__':main()
