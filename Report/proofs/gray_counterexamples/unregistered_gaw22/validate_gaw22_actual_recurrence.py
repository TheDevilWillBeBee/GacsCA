"""Read-only replay of the same actual real2's exact GAW22 recurrence.

Frozen GAW21 is replayed rather than silently inheriting a later outcome.
All new fixed-control/full-word receipts are recomputed without writes.
The written all-row recurrence supplies the universal induction, not a
sampled trillion-row experiment or a generic malformed-input theorem.
"""
from pathlib import Path
import hashlib,importlib.util,json,sys,time
import check_gaw22_actual_recurrence as recurrence
S=Path(__file__).resolve().parent;ROOT=S.parents[3]
D=ROOT/'figs/gray_counterexamples/unregistered_gaw22'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text())
def assets(m):
    for p,h in m['assets_sha256'].items():
        assert sha(ROOT/p)==h,(p,'frozen source, receipt or dependency differs')

def main():
    started=time.monotonic();mp=D/'GAW22_standalone_assets.json';m=load(mp);assets(m)
    oldm=load(ROOT/m['inherited_manifest']);assets(oldm)
    assert len(oldm['assets_sha256'])==m['inherited_assets']==555
    assert all(m['assets_sha256'][p]==h for p,h in oldm['assets_sha256'].items())
    spec=importlib.util.spec_from_file_location('gaw22_accepted_gaw21_replay',
        S.parent/'unregistered_gaw21/validate_gaw21_two_and_three.py')
    prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
    previous=prior.main()
    assert previous['passed'] and previous['assets_verified']==555
    assert previous['exact_unchanged_GAW2R_ROM_dictionary_listing_and_local_R']
    assert previous['actual_intact_H15_Info_bit_faults_atU_genuine_shared_original_c104_real2']
    assert previous['actual_derived_banks_seven_full_beta65062_runs_and_legal2U_boundary_proved']
    assert not previous['operational_real2_recovery_eventual_memory_failure_or_Gray_iid_counterexample']

    k=recurrence.k
    assert (k.Q,k.U,k.WORD,k.PRIMARY_START,k.FRAME_WORDS)==(8192,1048576,100,3848,496)
    assert k.STAGE_STARTS==(0,32*k.Q,64*k.Q,96*k.Q,102*k.Q)
    r=recurrence.main();assert r==load(D/'GAW22_actual_recurrence_certificate.json')
    original=ROOT/'figs/gray_counterexamples/unregistered_gaw21/GAW21_three_record_witness_certificate.json'
    assert r['exact_same_GAW21_actual_intact_start15_point_shared_real2_receipt_sha256']==sha(original)
    assert r['no_later_errors_or_prescribed_future_commands']
    assert r['event_contracts']['actual_full_local_R_event_checks']==9559
    assert r['event_contracts']['native_GF_clock_flags_and_Workspace_checks']==9559
    assert r['event_contracts']['all_rows_covered_by_written_exact_track_recurrence_and_frozen_phase_contract']
    assert r['native_geometry_and_all_native_flags_Workspace_match_shadow_throughout']
    assert r['every_normal_frame_History_Mem_and_Head_Output_input_matches_shadow']
    assert r['raw_Mail_can_cross_normal_frames_between_safe_capture_times']
    states=r['whole_relevant_unmasked_Word100_records'];assert len(states)==17
    for snapshot in states:
        assert snapshot['actual_lower_boundary']==snapshot['upper_row']*k.U
        for record in snapshot['all_changed_raw_upper_records']:
            a=record['actual_full496_words'];c=record['clean_full496_words']
            assert len(a)==len(c)==496 and a!=c
            assert a[:6]==c[:6]
            assert all(0<=int(v,16)<1<<100 for v in a+c)
    final=states[-1];assert final['upper_row']==k.U
    assert final['exact_logical_track_XOR_words']=={}
    assert final['all_changed_raw_upper_records']==[]
    executions=r['normal_interpreter_executions']
    assert [(e['receiver'],e['early'],e['ticks']) for e in executions]==[
        (-9,True,150),(0,False,66185),(0,True,150),(8,True,150)]
    for e in executions:
        assert e['HALT'] and len(e['actual_derived_full496x17_normal_bank'])==496
        assert len(e['final_full_output_words'])==(6 if e['early'] else 496)
        assert e['final_full_output_words'][2:4]==['0x0','0x0']
        assert e['ticks']<=213 if e['early'] else e['ticks']<=141557
        assert all(0<=int(v,16)<1<<1700 for v in e['actual_derived_full496x17_normal_bank'])
    assert r['full_upper_raw_equality_first_at_rowU']
    assert r['full_lower_boundary_equality_at_physicalU_squared']==k.U*k.U==1099511627776
    assert r['lower_primary4054_persistent_Info_bit1_interval']==[k.U,k.U*k.U]
    assert r['interval_half_open_and_shadow_bit0'] and r['thereafter_full_shadow_by_autonomous_determinism']
    upper_class=r['rescaled_original_c104_real1_classification']
    assert upper_class['level1'] and upper_class['level0']==0 and upper_class['points']==3
    assert upper_class['sep']==104
    p4=r['transplanted_literal_all_SF_Proposition4_R_failure']
    assert p4['upper_row']==34*k.Q+1==278529
    assert p4['disagreement_sites']==[-2*k.Q,2*k.Q]
    assert p4['simultaneous_spatial_span']==4*k.Q>p4['printed_two_colony_box_width']==2*k.Q
    for field in ('printed_Address_Proposition5_failure_claim',
        'operational_real2_recovery_eventual_memory_or_iid_failure_claim',
        'faithful_Gray_or_Gacs_construction_counterexample',
        'rule_ROM_G17_accepted_assets_or_shorter_U_changed'):
        assert r[field] is False
    assert m['earlier_GAW21_eventual_recovery_status_remains_historical_unproved']
    assets(m);assets(oldm)
    result=dict(passed=True,assets_verified=len(m['assets_sha256']),inherited_assets_verified=555,
        Q=k.Q,U=k.U,error_lambda=24,error_separation=104,
        exact_unchanged_GAW2R_ROM_dictionary_listing_actual_local_R=True,
        same_actual_intact_H15_point_shared_real2_no_later_errors=True,
        written_all_row_upper_recurrence_and_actual_normal_bank_head_source_native_coupling_proved=True,
        actual_full496word_local_R_event_checks=9559,
        full_unmasked_changed_upper_record_snapshots=17,
        legal_native_physical_period_applied_to_actual_Dt_not_malformed_projection=True,
        whole_lower_raw_repair_first_at_U_squared=1099511627776,
        continuous_lower_Info4054_bit_persistence_interval_half_open=[k.U,k.U*k.U],
        all_later_full_raw_shadow_equality_by_determinism=True,
        exact_derived_rescaled_real1_transplanted_all_SF_P4_R_envelope_failure=True,
        Address_P5_Gray_Gacs_operational_eventual_repair_iid_or_memory_failure_claim=False,
        arbitrary_real2_higher_noise_theorem_or_shorter_U=False,
        rule_ROM_G17_frozen_ancestors_or_registered_main_changed=False,
        manifest_sha256=sha(mp),receipt_sha256=sha(D/'GAW22_actual_recurrence_certificate.json'),
        proof_sha256=sha(S/'GAW22_REAL2_EXACT_RECURRENCE.md'),elapsed_seconds=time.monotonic()-started)
    print(json.dumps(result),flush=True);return result

if __name__=='__main__':main()
