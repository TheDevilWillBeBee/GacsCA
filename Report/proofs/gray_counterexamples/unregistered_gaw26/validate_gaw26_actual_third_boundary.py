"""Read-only all-new GAW26 replay with exact accepted GAW25 provenance.

Default reuses only frozen, accepted inherited results after checking
all hashes and both terminal replay logs. --full-inherited also runs
that unchanged mathematical dependency. No accepted files are written.
"""
from pathlib import Path
import hashlib,importlib.util,json,subprocess,sys,tempfile,time
import check_gaw26_late_discovery as late
import check_gaw26_physical_late_factor as physical
import check_gaw26_actual_fourth_sources as sources
import check_gaw26_actual_fourth_native as native
S=Path(__file__).resolve().parent;ROOT=S.parents[3]
D=ROOT/'figs/gray_counterexamples/unregistered_gaw26'
S25=S.parent/'unregistered_gaw25';D25=ROOT/'figs/gray_counterexamples/unregistered_gaw25'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text())
def assets(m):
    for p,h in m['assets_sha256'].items():
        assert sha(ROOT/p)==h,(p,'frozen source/receipt or dependency differs')
def run(command):
    p=subprocess.run(list(map(str,command)),cwd=ROOT,capture_output=True,text=True)
    assert p.returncode==0,(command,p.returncode,p.stdout,p.stderr)
    assert p.stderr=='',p.stderr
    return p.stdout
def accepted_dependency(m):
    oldmanifest=ROOT/m['inherited_manifest'];old=load(oldmanifest);assets(old)
    assert len(old['assets_sha256'])==m['inherited_assets']==653
    assert all(m['assets_sha256'][p]==h for p,h in old['assets_sha256'].items())
    for key in ('accepted_child_log','accepted_parent_log'):
        p=ROOT/m[key];result=json.loads([s for s in p.read_text().splitlines() if s.strip()][-1])
        assert result['passed'] and result['assets_verified']==653 and result['inherited_assets_verified']==622
        assert result['manifest_sha256']==sha(oldmanifest)
        assert result['proof_sha256']==sha(S25/'GAW25_ACTUAL_SECOND_BOUNDARY_AND_THIRD_ADDRESS_PULSE.md')
        assert result['second_full_boundary_receipt_sha256']==sha(D25/'GAW25_full_2U_physical_certificate.json')
        assert result['third_source_receipt_sha256']==sha(D25/'GAW25_actual_third_sources_certificate.json')
        assert result['third_native_receipt_sha256']==sha(D25/'GAW25_actual_third_native_pulse_certificate.json')
        assert (result['Q'],result['U'],result['error_lambda'],result['error_separation'])==(8192,1048576,24,104)
        for flag in ('all_new_math_recomputed',
            'inherited_GAW24_provenance_all_hashes_and_both_accepted_terminal_logs_checked',
            'exact_unchanged_GAW2R_own_ROM_dictionary_local_R_and_new_rebuilt_analysis_binaries',
            'same_intact_H_shared_actual_row1_GF_only139264site_original_real2_no_later_errors',
            'actual_second_full_H2_H3_banks_54_complete_emissions_two_interacting_pairs_and_raw2U_commit',
            'actual_third_58_native_early_executions_25_right_couriers_and_no_left_Flag2_commands'):
            assert result[flag] is True
        assert result['actual_native_GF_foreign_intervals_U_2U_3U']==[[61440,163840],[118784,188416],[176128,212992]]
        assert result['canonical_E_relation_at2U_claim'] is False
        assert result['third_full_Out_Info_later_orbit_eventual_repair_operational_counterexample_proved'] is False
        assert result['faithful_Gray_Gacs_iid_higher_error_memory_or_shorterU_claim'] is False
    if '--full-inherited' in sys.argv:
        spec=importlib.util.spec_from_file_location('gaw26_full_accepted_gaw25_replay',S25/'validate_gaw25_actual_second_boundary.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        r=module.main();assert r['passed'] and r['assets_verified']==653
    print(json.dumps(dict(accepted_GAW25_all653_asset_and_child_parent_terminal_hashes_verified=True,
        inherited_math_recomputed='--full-inherited' in sys.argv)),flush=True)
    return old

def main():
    started=time.monotonic();mp=D/'GAW26_standalone_assets.json';m=load(mp);assets(m)
    inherited=accepted_dependency(m);k=late.k
    assert (k.Q,k.U,k.WORD,k.PRIMARY_START,k.FRAME_WORDS)==(8192,1048576,100,3848,496)
    assert k.SLOTS==(0,-2,-1,1,2) and k.STAGE_STARTS==(0,32*k.Q,64*k.Q,96*k.Q,102*k.Q)
    flags=['gcc','-O3','-std=c11','-Wall','-Wextra','-Werror']
    with tempfile.TemporaryDirectory(prefix='gaw26_readonly_') as tmp:
        tmp=Path(tmp);exes={}
        for stem in ('gaw26_retained_bank_masks','gaw26_fourth_native_pulse','gaw26_fourth_native_audit'):
            exe=tmp/stem;run(flags+[S.relative_to(ROOT)/(stem+'.c'),'-o',exe])
            assert sha(exe)==sha(D/stem),(stem,'exact analysis binary identity')
            exes[stem]=exe
        prefix=tmp/'prefix.bin';hist=tmp/'hist.bin';events=tmp/'fourth.bin'
        got=json.loads(run([exes['gaw26_retained_bank_masks'],D25/'GAW25_third_native_pulse_events01.bin',prefix,hist]))
        assert got==load(D/'GAW26_retained_mask_discovery01.json') and got['passed']
        assert got['tag_domain']==[-262144,262144] and got['prefix_Info_zero_tag_intervals']==[]
        assert got['pulse_H2_H3_zero_tag_intervals']==[[118784,176126,0],[188416,212992,0]]
        assert got['mask_updates']==24578 and got['pulse_GF_wipe_holder_locations']==81920
        assert got['all_final_tags_coherent0_or31']
        assert sha(prefix)==sha(D/'GAW26_prefix_Info_masks.bin')
        assert sha(hist)==sha(D/'GAW26_retained_H2_H3_masks.bin')
        got=json.loads(run([exes['gaw26_fourth_native_pulse'],events,D/'GAW26_derived_actual_fourth_F1_sources.txt']))
        assert got==load(D/'GAW26_fourth_native_pulse_discovery01.json') and got['passed']
        assert got['physical_period_index']==4 and got['computed_updates']==20484 and got['event_intervals']==22312255
        assert got['source_Info_at_4U_commit_not_claimed']
        assert sha(events)==sha(D/'GAW26_fourth_native_pulse_events01.bin')
        scalar=json.loads(run([exes['gaw26_fourth_native_audit'],events]))
        assert scalar==load(D/'GAW26_fourth_native_audit_issue01.log')
        assert scalar['passed'] and scalar['independent_event_intervals']==22312255
        assert scalar['scalar_native_WF_cofactors']==44666298 and scalar['source_holder_wipe_cofactors']==2867760
        assert scalar['exact_final_native_segments']==[[204800,208896,2],[208896,233472,1],[233472,237568,3]]
    print(json.dumps(dict(exact_new_retention_and_fourth_native_binary_event_replay_passed=True)),flush=True)
    previous_argv=sys.argv
    try:
        sys.argv=[str(S/'check_gaw26_late_discovery.py')];a=late.main()
        sys.argv=[str(S/'check_gaw26_physical_late_factor.py')];b=physical.main()
        sys.argv=[str(S/'check_gaw26_actual_fourth_sources.py')];c=sources.main()
        sys.argv=[str(S/'check_gaw26_actual_fourth_native.py')];e=native.main()
    finally:sys.argv=previous_argv
    assert a==load(D/'GAW26_actual_late_discovery01.json')
    assert b==load(D/'GAW26_full_3U_physical_certificate.json')
    assert c==load(D/'GAW26_actual_fourth_sources_certificate.json')
    assert e==load(D/'GAW26_actual_fourth_native_pulse_certificate.json')
    assert a['physical_majority_and_full_3U_commit_exterior_lift_not_yet_certified']
    assert b['fourth_native_source_and_pulse_not_yet_certified']
    assert c['actual_fourth_native_pulse_and4U_boundary_not_yet_certified']
    assert b['universal_infinite_line_unchanged_exterior_and_raw_commit_proved_in_companion_text']
    assert b['full_boundary_cell_formula_native_fixed_Info_old_voted_Out_Programme_holder_service_and_workzero']
    independent=a['actual_complete_frame_independent_executions']
    assert len(independent)==70 and all(z['HALT'] and z['ticks']<=141557 and z['exact_literal_local_R_successor_equal'] for z in independent)
    pairs=a['actual_coupled_partial_frame_executions']
    assert [z['ticks_followed'] for z in pairs]==[10871,10869]
    assert [z['head_spatial_hull'] for z in pairs]==[[175880,180471],[212744,217335]]
    assert [[z['collisions'][0]['physical_position']] for z in pairs]==[[180288],[217152]]
    assert all(z['all_heads_stationary_ERROR_by_last_row'] for z in pairs)
    assert all(len(z['actual_chronological_Out_stores'])==171 and len(z['actual_final_all_stored_Out_words'])==158 for z in pairs)
    for z in pairs:
        origins=z['physical_origins'];partial=origins[0];complete=origins[1]
        stored=z['actual_final_all_stored_Out_words']
        a=[p-partial-k.PRIMARY_START for p,v in stored if partial+k.PRIMARY_START<=p<partial+k.PRIMARY_START+k.FRAME_WORDS]
        bidx=[p-complete-k.PRIMARY_START for p,v in stored if complete+k.PRIMARY_START<=p<complete+k.PRIMARY_START+k.FRAME_WORDS]
        assert len(a)==54 and max(a)==241 and len(bidx)==104 and max(bidx)==491
    assert b['actual_full_local_R_3U_commit_checks']==1240
    assert b['physical_late_copy_factor']['actual_full_local_R_raw_holder_reset_reload_stable_ERROR_and_commit_cofactors']==2550
    assert sum(z['actual_full_local_R_five_holder_interpreter_cofactors'] for z in b['physical_coupled_trace_checks'])==2720
    true=b['full_true_native_Info_table_at3U'];foreign=b['full_foreign_native_Info_table_at3U']
    for g in range(-26,47):
        expected=[g%k.Q,3,0,0,0,0] if g<=-1 or g>=26 else [g%k.Q,3,1,0,0,0] if g<=6 else [0,3,1,0,0,0] if g<=9 else [0,2,1,0,0,0] if g<=13 else [0,1,1,0,0,0] if g<=21 else [0]*6
        assert true[str(g)]==expected
    assert foreign['22']==[0,3,1,0,0,0]
    assert all(foreign[str(g)]==[0,1,1,0,0,0] for g in range(23,27))
    assert len(c['complete_actual_fourth_native_early_banks_and_executions'])==74
    assert c['actual_true_positive_Flag1_heads']==[*range(22),26,27,28]
    assert c['actual_foreign_positive_Flag1_heads']==list(range(22,27))
    assert c['actual_positive_Flag2_receivers']==[] and c['actual_all_left_sources_zero']
    expected_sources=sorted([(g+1)*k.Q-3 for g in (*range(21),26,27,28)]+[g*k.Q+k.Q//2-3 for g in range(22,26)])
    assert c['actual_nonzero_right_sources_at3U_plus80Q_minus1']==expected_sources
    assert len(expected_sources)==28 and c['actual_nonzero_left_sources_at3U_plus80Q_minus1']==[]
    assert e['actual_courier_contracts']['maximum_first_arrival_after75Q']==4339
    assert e['actual_frozen_local_R_native_cofactors']['actual_frozen_local_R_native_and_computed_primary_checks']==2948
    assert e['native_GF_shifted_intervals_at4U']==[[208896,233472],[233472,237568]]
    assert e['native_GF_width_at4U']==28672 and e['native_Flag1_intervals_at4U']==[[204800,208896],[233472,237568]]
    assert e['native_common_Age_at4U']==0 and e['native_WF1_WF2_Flag2_zero_at4U']
    assert e['fourth_native_fixed_by_relative_row']==806912
    env=e['actual_finite_Address_allowance_check']
    assert env['all_four_actual_native_event_records']==98334
    assert env['exact_Address_disagreement_union_spatial_hull']==[0,237568]
    assert env['maximum_instantaneous_native_Address_wrong_cell_count']==139264
    assert env['witnessed_rows1_through4U_fit_spatial_0_to2Q_squared_and_time1_to1_plusU_squared_over16']
    assert e['fourth_full_Out_commit_encoding_decoded_damage_or_later_orbit_proved'] is False
    assert e['auxiliary_source_bits_at4U_not_claimed_physical_Info']
    assert e['faithful_Gray_Proposition5_iid_memory_higher_or_shorterU_claim'] is False
    assets(m);assets(inherited)
    result=dict(passed=True,assets_verified=len(m['assets_sha256']),inherited_assets_verified=653,
        inherited_GAW25_provenance_all_hashes_and_both_accepted_terminal_logs_checked=True,
        inherited_math_recomputed='--full-inherited' in sys.argv,all_new_math_recomputed=True,
        Q=k.Q,U=k.U,error_lambda=24,error_separation=104,
        exact_unchanged_GAW2R_own_ROM_dictionary_local_R_and_new_rebuilt_analysis_binaries=True,
        same_intact_H_shared_actual_row1_GF_only139264site_original_real2_no_later_errors=True,
        actual_third_full_H2_H3_banks_70_complete_emissions_two_interacting_pairs_and_raw3U_commit=True,
        canonical_E_relation_at3U_claim=False,
        actual_fourth_74_native_early_executions_28_right_couriers_and_no_left_Flag2_commands=True,
        actual_common_lower_Age_noncommon_upper_Age0_1_2_3_banks_retained=True,
        fourth_native_event_intervals=22312255,native_WF_cofactors=44666298,source_holder_wipe_cofactors=2867760,
        actual_native_GF_foreign_intervals_U_2U_3U_4U=[[61440,163840],[118784,188416],[176128,212992],[208896,237568]],
        native_foreign_widths_U_2U_3U_4U=[102400,69632,36864,28672],
        preceding_4Q_boundary_shrink_extrapolation_false_for_same_actual_rule_history=True,
        exact_Address_disagreement_union_through4U=[0,237568],
        finite_observed_Address_history_fits_real2_P5_sized_allowance=True,
        fourth_full_Out_Info_later_orbit_eventual_repair_operational_counterexample_proved=False,
        faithful_Gray_Gacs_iid_higher_error_memory_or_shorterU_claim=False,
        old_registered_main_G17_rule_ROM_or_constants_changed=False,
        manifest_sha256=sha(mp),proof_sha256=sha(S/'GAW26_ACTUAL_THIRD_BOUNDARY_AND_FOURTH_ADDRESS_PULSE.md'),
        third_full_boundary_receipt_sha256=sha(D/'GAW26_full_3U_physical_certificate.json'),
        fourth_source_receipt_sha256=sha(D/'GAW26_actual_fourth_sources_certificate.json'),
        fourth_native_receipt_sha256=sha(D/'GAW26_actual_fourth_native_pulse_certificate.json'),
        elapsed_seconds=time.monotonic()-started)
    print(json.dumps(result),flush=True);return result

if __name__=='__main__':main()
