"""Read-only all-new GAW27 math, with hash-checked accepted GAW26 reuse."""
from pathlib import Path
import hashlib,importlib.util,json,subprocess,sys,tempfile,time
import check_gaw27_late_discovery as late
import check_gaw27_physical_late_factor as physical
import check_gaw27_actual_fifth_sources as sources
import check_gaw27_actual_fifth_native as native
import check_gaw27_rf_translation as renewal
S=Path(__file__).resolve().parent;ROOT=S.parents[3]
D=ROOT/'figs/gray_counterexamples/unregistered_gaw27'
S26=S.parent/'unregistered_gaw26';D26=ROOT/'figs/gray_counterexamples/unregistered_gaw26'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text())
def assets(m):
    for p,h in m['assets_sha256'].items():assert sha(ROOT/p)==h,(p,'frozen dependency or new asset differs')
def run(cmd):
    p=subprocess.run(list(map(str,cmd)),cwd=ROOT,capture_output=True,text=True)
    assert p.returncode==0,(cmd,p.returncode,p.stdout,p.stderr)
    assert p.stderr=='',p.stderr
    return p.stdout
def inherited(m):
    path=ROOT/m['inherited_manifest'];old=load(path);assets(old)
    assert len(old['assets_sha256'])==m['inherited_assets']==690
    assert all(m['assets_sha256'][p]==h for p,h in old['assets_sha256'].items())
    for key in ('accepted_child_log','accepted_parent_log'):
        result=json.loads((ROOT/m[key]).read_text().splitlines()[-1])
        assert result['passed'] and result['assets_verified']==690 and result['inherited_assets_verified']==653
        assert result['manifest_sha256']==sha(path)
        for key2,p in [('proof_sha256',S26/'GAW26_ACTUAL_THIRD_BOUNDARY_AND_FOURTH_ADDRESS_PULSE.md'),
            ('third_full_boundary_receipt_sha256',D26/'GAW26_full_3U_physical_certificate.json'),
            ('fourth_source_receipt_sha256',D26/'GAW26_actual_fourth_sources_certificate.json'),
            ('fourth_native_receipt_sha256',D26/'GAW26_actual_fourth_native_pulse_certificate.json')]:assert result[key2]==sha(p)
        assert (result['Q'],result['U'],result['error_lambda'],result['error_separation'])==(8192,1048576,24,104)
        for f in ('all_new_math_recomputed','inherited_GAW25_provenance_all_hashes_and_both_accepted_terminal_logs_checked',
            'exact_unchanged_GAW2R_own_ROM_dictionary_local_R_and_new_rebuilt_analysis_binaries',
            'same_intact_H_shared_actual_row1_GF_only139264site_original_real2_no_later_errors',
            'actual_third_full_H2_H3_banks_70_complete_emissions_two_interacting_pairs_and_raw3U_commit',
            'actual_fourth_74_native_early_executions_28_right_couriers_and_no_left_Flag2_commands',
            'actual_common_lower_Age_noncommon_upper_Age0_1_2_3_banks_retained',
            'finite_observed_Address_history_fits_real2_P5_sized_allowance'):assert result[f] is True
        assert result['native_foreign_widths_U_2U_3U_4U']==[102400,69632,36864,28672]
        for f in ('canonical_E_relation_at3U_claim','fourth_full_Out_Info_later_orbit_eventual_repair_operational_counterexample_proved',
            'faithful_Gray_Gacs_iid_higher_error_memory_or_shorterU_claim','old_registered_main_G17_rule_ROM_or_constants_changed'):assert result[f] is False
    if '--full-inherited' in sys.argv:
        spec=importlib.util.spec_from_file_location('gaw27_accepted_gaw26_full',S26/'validate_gaw26_actual_third_boundary.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        assert module.main()['passed']
    print(json.dumps(dict(all690_inherited_hashes_and_both_accepted_GAW26_terminal_logs_verified=True,
        inherited_math_recomputed='--full-inherited' in sys.argv)),flush=True)
    return old
def main():
    start=time.monotonic();mp=D/'GAW27_standalone_assets.json';m=load(mp);assets(m);old=inherited(m);k=late.k
    assert (k.Q,k.U,k.WORD,k.PRIMARY_START,k.FRAME_WORDS)==(8192,1048576,100,3848,496)
    assert k.SLOTS==(0,-2,-1,1,2) and k.STAGE_STARTS==(0,32*k.Q,64*k.Q,96*k.Q,102*k.Q)
    flags=['gcc','-O3','-std=c11','-Wall','-Wextra','-Werror']
    with tempfile.TemporaryDirectory(prefix='gaw27_readonly_') as tmp:
        tmp=Path(tmp);exes={}
        for stem in ('gaw27_retained_bank_masks','gaw27_fifth_native_pulse','gaw27_fifth_native_audit','gaw27_rf_template_native'):
            exe=tmp/stem;run(flags+[S.relative_to(ROOT)/(stem+'.c'),'-o',exe])
            assert sha(exe)==sha(D/stem),(stem,'rebuilt binary mismatch');exes[stem]=exe
        prefix=tmp/'prefix.bin';hist=tmp/'hist.bin';events=tmp/'fifth.bin';template=tmp/'template.bin'
        a=json.loads(run([exes['gaw27_retained_bank_masks'],D26/'GAW26_fourth_native_pulse_events01.bin',prefix,hist]))
        assert a==load(D/'GAW27_retained_mask_discovery01.json') and a['passed']
        assert a['tag_domain']==[-327680,327680] and a['prefix_Info_zero_tag_intervals']==[]
        assert a['pulse_H2_H3_zero_tag_intervals']==[[176128,208894,0],[212992,237568,0]]
        assert a['mask_updates']==20483 and a['pulse_GF_wipe_holder_locations']==57344
        assert sha(prefix)==sha(D/'GAW27_prefix_Info_masks.bin') and sha(hist)==sha(D/'GAW27_retained_H2_H3_masks.bin')
        a=json.loads(run([exes['gaw27_fifth_native_pulse'],events,D/'GAW27_derived_actual_fifth_F1_sources.txt']))
        assert a==load(D/'GAW27_fifth_native_pulse_issue01.log') and a['passed']
        assert a['physical_period_index']==5 and a['computed_updates']==20484 and a['event_intervals']==24625426
        assert sha(events)==sha(D/'GAW27_fifth_native_pulse_events01.bin')
        a=json.loads(run([exes['gaw27_fifth_native_audit'],events]))
        assert a==load(D/'GAW27_fifth_native_audit_issue01.log') and a['passed']
        assert a['scalar_native_WF_cofactors']==49292552 and a['source_holder_wipe_cofactors']==3175020
        a=json.loads(run([exes['gaw27_rf_template_native'],template]))
        assert a==load(D/'GAW27_RF_template_native_issue01.log') and a['passed']
        assert a['computed_updates']==16387 and a['event_intervals']==4231776
        assert sha(template)==sha(D/'GAW27_RF_template_native_events01.bin')
        a=json.loads(run([exes['gaw27_fifth_native_audit'],template]))
        assert a==load(D/'GAW27_RF_template_native_audit_issue01.log') and a['passed']
    print(json.dumps(dict(all_new_binaries_masks_actual_fifth_and_conditional_template_events_rebuilt_exactly=True)),flush=True)
    argv=sys.argv
    try:
        sys.argv=[str(S/'check_gaw27_late_discovery.py')];a=late.main()
        sys.argv=[str(S/'check_gaw27_physical_late_factor.py')];b=physical.main()
        sys.argv=[str(S/'check_gaw27_actual_fifth_sources.py')];c=sources.main()
        sys.argv=[str(S/'check_gaw27_actual_fifth_native.py')];e=native.main()
        sys.argv=[str(S/'check_gaw27_rf_translation.py')];f=renewal.main()
    finally:sys.argv=argv
    complete=a['actual_complete_frame_independent_executions'];assert len(complete)==86
    assert all(z['HALT'] and z['ticks']<=141557 and z['exact_literal_local_R_successor_equal'] for z in complete)
    pairs=a['actual_coupled_partial_frame_executions']
    assert [z['ticks_followed'] for z in pairs]==[10871,10869]
    assert [z['head_spatial_hull'] for z in pairs]==[[208648,213239],[237320,241911]]
    assert [z['collisions'][0]['physical_position'] for z in pairs]==[213056,241728]
    assert all(z['all_heads_stationary_ERROR_by_last_row'] for z in pairs)
    assert all(len(z['actual_chronological_Out_stores'])==171 and len(z['actual_final_all_stored_Out_words'])==158 for z in pairs)
    for z in pairs:
        partial,complete=z['physical_origins'];stored=z['actual_final_all_stored_Out_words']
        partialidx=[p-partial-k.PRIMARY_START for p,v in stored if partial+k.PRIMARY_START<=p<partial+k.PRIMARY_START+k.FRAME_WORDS]
        completeidx=[p-complete-k.PRIMARY_START for p,v in stored if complete+k.PRIMARY_START<=p<complete+k.PRIMARY_START+k.FRAME_WORDS]
        assert len(partialidx)==54 and max(partialidx)==241 and len(completeidx)==104 and max(completeidx)==491
    assert b['actual_full_local_R_4U_commit_checks']==1221
    assert b['physical_late_copy_factor']['actual_full_local_R_raw_holder_reset_reload_stable_ERROR_and_commit_cofactors']==2550
    assert sum(z['actual_full_local_R_five_holder_interpreter_cofactors'] for z in b['physical_coupled_trace_checks'])==2720
    assert b['universal_infinite_line_unchanged_exterior_and_raw_commit_proved_in_companion_text']
    assert b['full_boundary_cell_formula_native_fixed_Info_old_voted_Out_Programme_holder_service_and_workzero']
    assert b['all_potential_true_and_foreign_special_Info_sources_zero_at4U']
    true=b['full_true_native_Info_table_at4U'];foreign=b['full_foreign_native_Info_table_at4U']
    for g in range(-34,55):
        wanted=[g%k.Q,4,0,0,0,0] if g<=-1 or g>=29 else [g%k.Q,4,1,0,0,0] if g<=9 else [0,4,1,0,0,0] if g<=12 else [0,3,1,0,0,0] if g<=16 else [0,2,1,0,0,0] if g<=20 else [0,1,1,0,0,0] if g<=25 else [0]*6
        assert true[str(g)]==wanted
    assert all(foreign[str(g)]==([0,1,1,0,0,0] if 26<=g<=29 else [0]*6) for g in range(44))
    assert len(c['complete_actual_fifth_native_early_banks_and_executions'])==90
    assert c['actual_true_positive_Flag1_heads']==[*range(26),29,30,31]
    assert c['actual_foreign_positive_Flag1_heads']==list(range(26,30))
    assert c['actual_positive_Flag2_receivers']==[] and c['actual_all_left_sources_zero']
    wanted=sorted([(g+1)*k.Q-3 for g in (*range(25),29,30,31)]+[g*k.Q+k.Q//2-3 for g in range(26,29)])
    assert c['actual_nonzero_right_sources_at4U_plus80Q_minus1']==wanted and len(wanted)==31
    assert e['native_GF_shifted_intervals_at5U']==[[233472,258048],[258048,262144]]
    assert e['native_GF_width_at5U']==28672 and e['native_Flag1_intervals_at5U']==[[229376,233472],[258048,262144]]
    assert e['fifth_native_fixed_by_relative_row']==806912
    assert e['actual_frozen_local_R_native_cofactors']['actual_frozen_local_R_native_and_computed_primary_checks']==2948
    assert e['fifth_full_Out_commit_encoding_decoded_damage_or_later_orbit_proved'] is False
    assert f['RF_only_template_to_same_template_translated_plus3Q'] and f['actual_fifth_pulse_instantiates_template_at_A25']
    assert f['same_actual_fifth_pulse_core_all_event_rows_checked']==20488 and f['normalized_template_event_rows']==16391
    assert f['left_barrier_actual_scalar_cofactors']==20480
    assert f['actual_future_native_bank_and_six_command_renewal_not_proved']
    assert f['nonzero_future_left_Flag2_commands_not_covered']
    assert f['prepared_source3_Flag2_birth_diagnostic']['actual_reachability_in_the_row1_fault_history_not_claimed']
    assert f['future_persistence_erosion_P5_Gray_iid_shorterU_claim'] is False
    assets(m);assets(old)
    result=dict(passed=True,assets_verified=len(m['assets_sha256']),inherited_assets_verified=690,
        inherited_GAW26_all_hashes_and_both_terminal_logs_checked=True,all_new_math_recomputed=True,
        inherited_math_recomputed='--full-inherited' in sys.argv,Q=k.Q,U=k.U,error_lambda=24,error_separation=104,
        exact_frozen_GAW2R_own_ROM_dictionary_local_R_and_new_analysis_binary_identity=True,
        same_intact_H_actual_original_c104_row1_GF_only139264site_real2_no_later_errors=True,
        actual_fourth_full_late_banks_86_complete_emissions_two_coupled_pairs_and_all_raw4U=True,
        actual_fifth_90_native_early_heads_31_right_sources_no_left_and_native_through5U=True,
        actual_common_lower_Age_noncommon_upper_Age0_to4_retained=True,
        native_GF_interval_at5U=[233472,262144],native_wrongGF_width_at4U_and5U=28672,
        exact_Address_union_through5U=[0,262144],printed_real2_P5_sized_allowance_still_fits=True,
        conditional_RF_template_integer_Q_equivariance_left_barrier_and_plus3Q_translation_proved=True,
        actual_fifth_core_all20488_event_rows_instantiates_conditional_template=True,
        prepared_source3_Flag2_birth_is_warning_not_an_actual_future_history=True,
        full_5U_Out_Info_future_actual_command_renewal_erosion_or_persistence_proved=False,
        canonical_E_relation_at4U_faithful_Gray_iid_higher_error_reliability_or_shorterU_claim=False,
        old_registered_main_rules_ROM_or_constants_modified=False,
        manifest_sha256=sha(mp),proof_sha256=sha(S/'GAW27_FOURTH_BOUNDARY_AND_RF_RENEWAL_REDUCTION.md'),
        fourth_full_boundary_receipt_sha256=sha(D/'GAW27_full_4U_physical_certificate.json'),
        fifth_source_receipt_sha256=sha(D/'GAW27_actual_fifth_sources_certificate.json'),
        fifth_native_receipt_sha256=sha(D/'GAW27_actual_fifth_native_pulse_certificate.json'),
        conditional_RF_translation_receipt_sha256=sha(D/'GAW27_conditional_RF_translation_certificate.json'),
        elapsed_seconds=time.monotonic()-start)
    print(json.dumps(result),flush=True);return result
if __name__=='__main__':main()
