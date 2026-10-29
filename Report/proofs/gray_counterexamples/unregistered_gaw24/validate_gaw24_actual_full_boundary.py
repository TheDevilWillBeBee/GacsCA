"""Read-only exact full-U and second native-prefix lineage replay.

No main report/checkpoint or frozen source changes. All generated outputs
are temporary; their bytes and complete receipts must match the manifest.
The full inherited actual-error proof is replayed before the new lift.
"""
from pathlib import Path
import hashlib,importlib.util,json,subprocess,sys,tempfile,time
import check_gaw24_late_discovery as late
import check_gaw24_physical_late_factor as physical
import check_gaw24_actual_second_sources as sources
import check_gaw24_actual_second_native as native
S=Path(__file__).resolve().parent;ROOT=S.parents[3]
D=ROOT/'figs/gray_counterexamples/unregistered_gaw24'
S23=S.parent/'unregistered_gaw23';D23=ROOT/'figs/gray_counterexamples/unregistered_gaw23'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text())
def assets(m):
    for p,h in m['assets_sha256'].items():
        assert sha(ROOT/p)==h,(p,'immutable isolated source/receipt or inherited dependency differs')
def run(command):
    p=subprocess.run(list(map(str,command)),cwd=ROOT,capture_output=True,text=True)
    assert p.returncode==0,(command,p.returncode,p.stdout,p.stderr)
    assert p.stderr=='',p.stderr
    return p.stdout

def main():
    started=time.monotonic();mp=D/'GAW24_standalone_assets.json';m=load(mp);assets(m)
    inherited=load(ROOT/m['inherited_manifest']);assets(inherited)
    assert len(inherited['assets_sha256'])==m['inherited_assets']==591
    assert all(m['assets_sha256'][p]==h for p,h in inherited['assets_sha256'].items())
    spec=importlib.util.spec_from_file_location('gaw24_accepted_gaw23_replay',S23/'validate_gaw23_actual_first_pulse.py')
    old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
    inherited_result=old.main()
    assert inherited_result['passed'] and inherited_result['assets_verified']==591
    assert inherited_result['actual_intact_H_chronological_row1_GF_only139264_complete_shared_real2_payloads']
    assert inherited_result['exact_frozen_GAW2R_ROM_dictionary_local_R_and_rebuilt_analysis_binaries']
    print(json.dumps(dict(inherited_GAW23_full_replay_passed=True,assets=591)),flush=True)
    k=late.k
    assert (k.Q,k.U,k.WORD,k.PRIMARY_START,k.FRAME_WORDS)==(8192,1048576,100,3848,496)
    assert k.SLOTS==(0,-2,-1,1,2) and k.STAGE_STARTS==(0,32*k.Q,64*k.Q,96*k.Q,102*k.Q)
    flags=['gcc','-O3','-std=c11','-Wall','-Wextra','-Werror']
    with tempfile.TemporaryDirectory(prefix='gaw24_readonly_') as tmp:
        tmp=Path(tmp);exes={}
        for stem in ('gaw24_retained_bank_masks','gaw24_second_native_pulse','gaw24_second_native_audit'):
            exe=tmp/stem
            run(flags+[S.relative_to(ROOT)/(stem+'.c'),'-o',exe])
            assert sha(exe)==sha(D/stem),(stem,'analysis binary identity')
            exes[stem]=exe
        prefix=tmp/'prefix.bin';hist=tmp/'hist.bin';events=tmp/'second.bin'
        mask=load(D/'GAW24_retained_mask_discovery01.json')
        got=json.loads(run([exes['gaw24_retained_bank_masks'],D23/'GAW23_first_pulse_events02.bin',prefix,hist]))
        assert got==mask and got['passed']
        assert got['prefix_Info_zero_tag_intervals']==[[0,4095,0]]
        assert got['pulse_H2_H3_zero_tag_intervals']==[[4096,61438,0],[139264,163840,0]]
        assert got['mask_updates']==28675 and got['all_final_tags_coherent0_or31']
        assert sha(prefix)==sha(D/'GAW24_prefix_Info_masks.bin')
        assert sha(hist)==sha(D/'GAW24_retained_H2_H3_masks.bin')
        got=json.loads(run([exes['gaw24_second_native_pulse'],events,D/'GAW24_derived_actual_second_F1_sources.txt']))
        assert got==load(D/'GAW24_second_native_pulse_discovery01.json') and got['passed']
        assert got['event_intervals']==20488060 and got['computed_updates']==24579
        assert got['source_Info_at_2U_commit_not_claimed']
        assert sha(events)==sha(D/'GAW24_second_native_pulse_events01.bin')
        scalar=json.loads(run([exes['gaw24_second_native_audit'],events]))
        assert scalar==load(D/'GAW24_second_native_audit_issue01.log')
        assert scalar['passed'] and scalar['independent_event_intervals']==20488060
    print(json.dumps(dict(exact_new_mask_and_native_analysis_binary_event_replays_passed=True)),flush=True)
    previous_argv=sys.argv
    try:
        sys.argv=[str(S/'check_gaw24_late_discovery.py')];a=late.main()
        sys.argv=[str(S/'check_gaw24_physical_late_factor.py')];b=physical.main()
        sys.argv=[str(S/'check_gaw24_actual_second_sources.py')];c=sources.main()
        sys.argv=[str(S/'check_gaw24_actual_second_native.py')];e=native.main()
    finally:sys.argv=previous_argv
    assert a==load(D/'GAW24_actual_late_discovery01.json')
    assert b==load(D/'GAW24_full_U_physical_certificate.json')
    assert c==load(D/'GAW24_actual_second_sources_certificate.json')
    assert e==load(D/'GAW24_actual_second_native_pulse_certificate.json')
    # Historical discovery scope is retained unchanged; the later proof
    # closes exactly these ports rather than rewriting older receipts.
    assert a['physical_majority_and_full_U_commit_exterior_lift_not_yet_certified']
    assert a['actual_coupled_partial_frame_executions'][0]['logical_majority_to_raw_physical_factor_not_yet_certified']
    assert b['second_native_source_and_pulse_not_yet_certified']
    assert c['actual_second_native_pulse_and2U_boundary_not_yet_certified']
    assert b['universal_infinite_line_unchanged_exterior_and_raw_commit_proved_in_companion_text']
    assert b['full_boundary_cell_formula_native_fixed_Info_old_voted_Out_Programme_holder_service_and_workzero']
    assert b['literal_canonical_E_upper_relation_not_claimed_GF_remains_foreign']
    independent=a['actual_complete_frame_independent_executions']
    assert len(independent)==38 and all(z['HALT'] and z['ticks']<=141557 and z['exact_literal_local_R_successor_equal'] for z in independent)
    pairs=a['actual_coupled_partial_frame_executions']
    assert [z['ticks_followed'] for z in pairs]==[10871,10869]
    assert [z['head_spatial_hull'] for z in pairs]==[[61192,65783],[163592,168183]]
    assert all(z['all_heads_stationary_ERROR_by_last_row'] for z in pairs)
    assert all(len(z['actual_chronological_Out_stores'])==171 and len(z['actual_final_all_stored_Out_words'])==158 for z in pairs)
    assert b['actual_full_local_R_U_commit_checks']==1247
    assert b['physical_late_copy_factor']['actual_full_local_R_raw_holder_reset_reload_stable_ERROR_and_commit_cofactors']==2550
    assert sum(z['actual_full_local_R_five_holder_interpreter_cofactors'] for z in b['physical_coupled_trace_checks'])==2720
    assert len(c['complete_actual_second_native_early_banks_and_executions'])==42
    assert c['no_common_upper_Age_assumed_actual_zero_one_native_lanes_retained']
    assert len(c['actual_nonzero_right_sources_atU_plus80Q_minus1'])==24
    assert e['actual_courier_contracts']['maximum_first_arrival_after75Q']==4339
    assert e['actual_frozen_local_R_native_cofactors']['actual_frozen_local_R_native_and_computed_primary_checks']==2948
    assert e['native_GF_interval_at2U']==[118784,188416] and e['native_GF_width_at2U']==69632
    assert e['native_Flag1_intervals_at2U']==[[114688,118784],[184320,188416]]
    assert e['native_common_Age_at2U']==0 and e['native_WF1_WF2_Flag2_zero_at2U']
    assert e['second_full_Out_commit_encoding_decoded_damage_or_later_orbit_proved'] is False
    assert e['auxiliary_source_bits_at2U_not_claimed_physical_Info']
    assert e['faithful_Gray_Proposition5_iid_memory_higher_or_shorterU_claim'] is False
    assets(m);assets(inherited)
    r=dict(passed=True,assets_verified=len(m['assets_sha256']),inherited_assets_verified=591,
        Q=k.Q,U=k.U,error_lambda=24,error_separation=104,
        exact_frozen_GAW2R_own_ROM_dictionary_local_R_analysis_binary_and_event_identity=True,
        actual_intact_H_same_shared_original_real2_row1_GF_only_fault139264sites=True,
        actual_H2_H3_retention_masks_and102Q_plus1_full496x17_late_banks=True,
        actual_38_complete_independent_own_evaluations_and_two_interacting_partial_pairs=True,
        actual_complete_unmasked_raw_U_cell_formula_with_unused_Info_and_workreset=True,
        canonical_E_relation_atU_claim=False,
        actual_second_42_native_early_executions_and24_right_couriers_no_common_upper_Age_assumption=True,
        second_native_event_intervals=20488060,second_native_WF_cofactors=41027022,
        second_source_holder_wipe_cofactors=2949480,second_full_local_R_native_cofactors=2948,
        actual_native_GF_foreign_interval_atU=[61440,163840],
        actual_native_GF_foreign_interval_at2U=[118784,188416],
        native_foreign_widths_U_2U=[102400,69632],
        second_full_late_Out_Info_commit_decoded_map_later_orbit_or_operational_counterexample_proved=False,
        faithful_Gray_Gacs_iid_higher_error_memory_or_shorterU_claim=False,
        frozen_main_reports_G17_rule_ROM_or_constants_changed=False,
        manifest_sha256=sha(mp),proof_sha256=sha(S/'GAW24_ACTUAL_FULL_FIRST_PERIOD_AND_SECOND_NATIVE_PULSE.md'),
        full_U_receipt_sha256=sha(D/'GAW24_full_U_physical_certificate.json'),
        second_source_receipt_sha256=sha(D/'GAW24_actual_second_sources_certificate.json'),
        second_native_receipt_sha256=sha(D/'GAW24_actual_second_native_pulse_certificate.json'),
        elapsed_seconds=time.monotonic()-started)
    print(json.dumps(r),flush=True);return r

if __name__=='__main__':main()
