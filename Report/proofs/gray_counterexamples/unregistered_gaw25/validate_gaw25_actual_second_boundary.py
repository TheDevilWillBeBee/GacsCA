"""Read-only new-work replay with exact accepted GAW24 provenance reuse.

Every inherited asset and both accepted terminal logs are checked. All
NEW GAW25 calculations are recomputed. --full-inherited additionally
reruns the complete unchanged GAW24 dependency, without modifying it.
"""
from pathlib import Path
import hashlib,importlib.util,json,subprocess,sys,tempfile,time
import check_gaw25_late_discovery as late
import check_gaw25_physical_late_factor as physical
import check_gaw25_actual_third_sources as sources
import check_gaw25_actual_third_native as native
S=Path(__file__).resolve().parent;ROOT=S.parents[3]
D=ROOT/'figs/gray_counterexamples/unregistered_gaw25'
S24=S.parent/'unregistered_gaw24';D24=ROOT/'figs/gray_counterexamples/unregistered_gaw24'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text())
def assets(m):
    for p,h in m['assets_sha256'].items():
        assert sha(ROOT/p)==h,(p,'frozen source/receipt or inherited dependency differs')
def run(command):
    p=subprocess.run(list(map(str,command)),cwd=ROOT,capture_output=True,text=True)
    assert p.returncode==0,(command,p.returncode,p.stdout,p.stderr)
    assert p.stderr=='',p.stderr
    return p.stdout
def accepted_dependency(m):
    oldmanifest=ROOT/m['inherited_manifest'];old=load(oldmanifest);assets(old)
    assert len(old['assets_sha256'])==m['inherited_assets']==622
    assert all(m['assets_sha256'][p]==h for p,h in old['assets_sha256'].items())
    for key in ('accepted_child_log','accepted_parent_log'):
        p=ROOT/m[key];result=json.loads([s for s in p.read_text().splitlines() if s.strip()][-1])
        assert result['passed'] and result['assets_verified']==622 and result['inherited_assets_verified']==591
        assert result['manifest_sha256']==sha(oldmanifest)
        assert result['proof_sha256']==sha(S24/'GAW24_ACTUAL_FULL_FIRST_PERIOD_AND_SECOND_NATIVE_PULSE.md')
        assert result['full_U_receipt_sha256']==sha(D24/'GAW24_full_U_physical_certificate.json')
        assert result['second_source_receipt_sha256']==sha(D24/'GAW24_actual_second_sources_certificate.json')
        assert result['second_native_receipt_sha256']==sha(D24/'GAW24_actual_second_native_pulse_certificate.json')
        assert (result['Q'],result['U'],result['error_lambda'],result['error_separation'])==(8192,1048576,24,104)
        for flag in ('exact_frozen_GAW2R_own_ROM_dictionary_local_R_analysis_binary_and_event_identity',
            'actual_intact_H_same_shared_original_real2_row1_GF_only_fault139264sites',
            'actual_complete_unmasked_raw_U_cell_formula_with_unused_Info_and_workreset',
            'actual_second_42_native_early_executions_and24_right_couriers_no_common_upper_Age_assumption'):
            assert result[flag] is True
        assert result['actual_native_GF_foreign_interval_at2U']==[118784,188416]
        assert result['canonical_E_relation_atU_claim'] is False
        assert result['second_full_late_Out_Info_commit_decoded_map_later_orbit_or_operational_counterexample_proved'] is False
        assert result['faithful_Gray_Gacs_iid_higher_error_memory_or_shorterU_claim'] is False
    if '--full-inherited' in sys.argv:
        spec=importlib.util.spec_from_file_location('gaw25_full_accepted_gaw24_replay',S24/'validate_gaw24_actual_full_boundary.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        r=module.main();assert r['passed'] and r['assets_verified']==622
    print(json.dumps(dict(accepted_GAW24_all622_asset_and_child_parent_terminal_hashes_verified=True,
        inherited_math_recomputed='--full-inherited' in sys.argv)),flush=True)
    return old

def main():
    started=time.monotonic();mp=D/'GAW25_standalone_assets.json';m=load(mp);assets(m)
    inherited=accepted_dependency(m);k=late.k
    assert (k.Q,k.U,k.WORD,k.PRIMARY_START,k.FRAME_WORDS)==(8192,1048576,100,3848,496)
    assert k.SLOTS==(0,-2,-1,1,2) and k.STAGE_STARTS==(0,32*k.Q,64*k.Q,96*k.Q,102*k.Q)
    flags=['gcc','-O3','-std=c11','-Wall','-Wextra','-Werror']
    with tempfile.TemporaryDirectory(prefix='gaw25_readonly_') as tmp:
        tmp=Path(tmp);exes={}
        for stem in ('gaw25_retained_bank_masks','gaw25_third_native_pulse','gaw25_third_native_audit'):
            exe=tmp/stem;run(flags+[S.relative_to(ROOT)/(stem+'.c'),'-o',exe])
            assert sha(exe)==sha(D/stem),(stem,'exact analysis binary identity')
            exes[stem]=exe
        prefix=tmp/'prefix.bin';hist=tmp/'hist.bin';events=tmp/'third.bin'
        got=json.loads(run([exes['gaw25_retained_bank_masks'],D24/'GAW24_second_native_pulse_events01.bin',prefix,hist]))
        assert got==load(D/'GAW25_retained_mask_discovery01.json') and got['passed']
        assert got['prefix_Info_zero_tag_intervals']==[]
        assert got['pulse_H2_H3_zero_tag_intervals']==[[61440,118782,0],[163840,188416,0]]
        assert got['mask_updates']==24578 and got['all_final_tags_coherent0_or31']
        assert sha(prefix)==sha(D/'GAW25_prefix_Info_masks.bin')
        assert sha(hist)==sha(D/'GAW25_retained_H2_H3_masks.bin')
        got=json.loads(run([exes['gaw25_third_native_pulse'],events,D/'GAW25_derived_actual_third_F1_sources.txt']))
        assert got==load(D/'GAW25_third_native_pulse_discovery01.json') and got['passed']
        assert got['physical_period_index']==3 and got['computed_updates']==24579 and got['event_intervals']==20898440
        assert got['source_Info_at_3U_commit_not_claimed']
        assert sha(events)==sha(D/'GAW25_third_native_pulse_events01.bin')
        scalar=json.loads(run([exes['gaw25_third_native_audit'],events]))
        assert scalar==load(D/'GAW25_third_native_audit_issue01.log')
        assert scalar['passed'] and scalar['independent_event_intervals']==20898440
    print(json.dumps(dict(exact_new_retention_and_third_native_binary_event_replay_passed=True)),flush=True)
    previous_argv=sys.argv
    try:
        sys.argv=[str(S/'check_gaw25_late_discovery.py')];a=late.main()
        sys.argv=[str(S/'check_gaw25_physical_late_factor.py')];b=physical.main()
        sys.argv=[str(S/'check_gaw25_actual_third_sources.py')];c=sources.main()
        sys.argv=[str(S/'check_gaw25_actual_third_native.py')];e=native.main()
    finally:sys.argv=previous_argv
    assert a==load(D/'GAW25_actual_late_discovery01.json')
    assert b==load(D/'GAW25_full_2U_physical_certificate.json')
    assert c==load(D/'GAW25_actual_third_sources_certificate.json')
    assert e==load(D/'GAW25_actual_third_native_pulse_certificate.json')
    assert a['physical_majority_and_full_2U_commit_exterior_lift_not_yet_certified']
    assert b['third_native_source_and_pulse_not_yet_certified']
    assert c['actual_third_native_pulse_and3U_boundary_not_yet_certified']
    assert b['universal_infinite_line_unchanged_exterior_and_raw_commit_proved_in_companion_text']
    assert b['full_boundary_cell_formula_native_fixed_Info_old_voted_Out_Programme_holder_service_and_workzero']
    independent=a['actual_complete_frame_independent_executions']
    assert len(independent)==54 and all(z['HALT'] and z['ticks']<=141557 and z['exact_literal_local_R_successor_equal'] for z in independent)
    pairs=a['actual_coupled_partial_frame_executions']
    assert [z['ticks_followed'] for z in pairs]==[10871,10869]
    assert [z['head_spatial_hull'] for z in pairs]==[[118536,123127],[188168,192759]]
    assert all(z['all_heads_stationary_ERROR_by_last_row'] for z in pairs)
    assert all(len(z['actual_chronological_Out_stores'])==171 and len(z['actual_final_all_stored_Out_words'])==158 for z in pairs)
    assert b['actual_full_local_R_2U_commit_checks']==1215
    assert b['physical_late_copy_factor']['actual_full_local_R_raw_holder_reset_reload_stable_ERROR_and_commit_cofactors']==2550
    assert sum(z['actual_full_local_R_five_holder_interpreter_cofactors'] for z in b['physical_coupled_trace_checks'])==2720
    true=b['full_true_native_Info_table_at2U'];foreign=b['full_foreign_native_Info_table_at2U']
    for g in range(-18,39):
        expected=[g%k.Q,2,0,0,0,0] if g<=-3 or g>=23 else [g%k.Q,2,1,0,0,0] if g<=3 else [0,2,1,0,0,0] if g<=6 else [0,1,1,0,0,0] if g<=14 else [0]*6
        assert true[str(g)]==expected
    assert all(foreign[str(g)]==[0,2,1,0,0,0] for g in range(15,20))
    assert all(foreign[str(g)]==[0,1,1,0,0,0] for g in range(20,24))
    assert len(c['complete_actual_third_native_early_banks_and_executions'])==58
    assert c['actual_true_positive_Flag1_heads']==[*range(15),23,24,25]
    assert c['actual_foreign_positive_Flag1_heads']==list(range(15,24))
    assert c['actual_positive_Flag2_receivers']==[] and c['actual_all_left_sources_zero']
    assert len(c['actual_nonzero_right_sources_at2U_plus80Q_minus1'])==25
    assert e['actual_courier_contracts']['maximum_first_arrival_after75Q']==4339
    assert e['actual_frozen_local_R_native_cofactors']['actual_frozen_local_R_native_and_computed_primary_checks']==2948
    assert e['native_GF_interval_at3U']==[176128,212992] and e['native_GF_width_at3U']==36864
    assert e['native_Flag1_intervals_at3U']==[[172032,176128],[208896,212992]]
    assert e['native_common_Age_at3U']==0 and e['native_WF1_WF2_Flag2_zero_at3U']
    env=e['actual_finite_Address_allowance_check']
    assert env['all_three_actual_native_event_records']==77846
    assert env['exact_Address_disagreement_union_spatial_hull']==[0,212992]
    assert env['maximum_instantaneous_native_Address_wrong_cell_count']==139264
    assert env['witnessed_rows1_through3U_fit_spatial_0_to2Q_squared_and_time1_to1_plusU_squared_over16']
    assert e['third_full_Out_commit_encoding_decoded_damage_or_later_orbit_proved'] is False
    assert e['auxiliary_source_bits_at3U_not_claimed_physical_Info']
    assert e['faithful_Gray_Proposition5_iid_memory_higher_or_shorterU_claim'] is False
    assets(m);assets(inherited)
    r=dict(passed=True,assets_verified=len(m['assets_sha256']),inherited_assets_verified=622,
        inherited_GAW24_provenance_all_hashes_and_both_accepted_terminal_logs_checked=True,
        inherited_math_recomputed='--full-inherited' in sys.argv,all_new_math_recomputed=True,
        Q=k.Q,U=k.U,error_lambda=24,error_separation=104,
        exact_unchanged_GAW2R_own_ROM_dictionary_local_R_and_new_rebuilt_analysis_binaries=True,
        same_intact_H_shared_actual_row1_GF_only139264site_original_real2_no_later_errors=True,
        actual_second_full_H2_H3_banks_54_complete_emissions_two_interacting_pairs_and_raw2U_commit=True,
        canonical_E_relation_at2U_claim=False,
        actual_third_58_native_early_executions_25_right_couriers_and_no_left_Flag2_commands=True,
        actual_common_lower_Age_noncommon_upper_Age0_1_2_banks_retained=True,
        third_native_event_intervals=20898440,native_WF_cofactors=41847254,source_holder_wipe_cofactors=3072375,
        actual_native_GF_foreign_intervals_U_2U_3U=[[61440,163840],[118784,188416],[176128,212992]],
        native_foreign_widths_U_2U_3U=[102400,69632,36864],
        exact_Address_disagreement_union_through3U=[0,212992],
        finite_observed_Address_history_fits_real2_P5_sized_allowance=True,
        third_full_Out_Info_later_orbit_eventual_repair_operational_counterexample_proved=False,
        faithful_Gray_Gacs_iid_higher_error_memory_or_shorterU_claim=False,
        old_registered_main_G17_rule_ROM_or_constants_changed=False,
        manifest_sha256=sha(mp),proof_sha256=sha(S/'GAW25_ACTUAL_SECOND_BOUNDARY_AND_THIRD_ADDRESS_PULSE.md'),
        second_full_boundary_receipt_sha256=sha(D/'GAW25_full_2U_physical_certificate.json'),
        third_source_receipt_sha256=sha(D/'GAW25_actual_third_sources_certificate.json'),
        third_native_receipt_sha256=sha(D/'GAW25_actual_third_native_pulse_certificate.json'),
        elapsed_seconds=time.monotonic()-started)
    print(json.dumps(r),flush=True);return r

if __name__=='__main__':main()
