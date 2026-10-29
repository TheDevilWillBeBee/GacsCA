"""Aggregate the exact selected receipts; no new CA or inferred histories."""
from pathlib import Path
import hashlib,json,sys
S=Path(__file__).resolve().parent;ROOT=S.parents[3]
D=ROOT/'figs/gray_counterexamples/unregistered_gaw15'
sys.path.insert(0,str(S))
import continue_gaw15_phase_packets as full

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(name):return json.loads((D/name).read_text())

def check():
    expected={
        'phase_3841_0':(1451,5546,16,0,0,[0],3030,901770,17),
        'phase_3841_4':(1451,5546,16,0,0,[0],3030,901770,17),
        'history_capture_3841':(1451,5546,16,0,0,[0],3030,901770,17),
        'source_0_0':(5119,8191,5471,20,5,[],3052,904510,0),
        'source_0_1':(5120,8191,5472,22,5,[0],3052,901770,17),
        'source_8184_0':(5118,8191,5466,14,2,[1],3052,901770,17),
        'source_8184_1':(5119,8191,5468,12,2,[1],3046,901770,17)}
    cases=[];sources={};cofactors=commits=upper=rows=0;deps={}
    for recipe in full.selected():
        tag=recipe['tag'];name=tag+'_complete.json';deps[str((D/name).relative_to(ROOT))]=sha(D/name)
        r=load(name);assert r['recipe']==recipe
        assert (r['Q'],r['U'],r['error_lambda'],r['error_separation'])==(8192,1048576,24,104)
        assert r['actual_intact_H'] and r['actual_chronological_fault_clock']==839681
        assert not r['new_transition_or_selected_future_tape'] and not r['universal_recovery_or_Gray_iid_or_shorter_U']
        c=r['original_c104_classification']
        assert c['points']==16 and c['level0']==0 and c['extent']==[16,1]
        assert c['candidate_level1'] and c['level1'] and c['sep']==104
        payload=r['complete_old_and_replacement_payload']
        assert len(payload)==16 and [v['x'] for v in payload]==list(range(recipe['start'],recipe['start']+16))
        assert all(v['t']==839681 and len(v['old_complete_words'])==496 and
            len(v['replacement_complete_words'])==496 and v['old_complete_words']!=v['replacement_complete_words'] for v in payload)
        trace=r['actual_physical_prefix_rows'];b=r['actual_boundary_continuation'];n=len(trace)
        assert [v['tick'] for v in trace]==list(range(1,n+1))
        assert [v['age'] for v in trace]==list(range(839682,839682+n))
        assert not(trace[-1]['geometry'] or trace[-1]['native_flags'] or trace[-1]['actual_Workspace_sources'])
        closure=r['actual_quiet_coherent_closure'];assert closure['age']==trace[-1]['age']
        assert all(len(set(values))==1 for _,z in closure['changed_SF_groups'] for values in z.values())
        count=sum(len(v['actual_Workspace_sources']) for v in trace)
        wfrows=sum(bool(v['actual_Workspace_sources']) for v in trace)
        observed=(r['first_geometry_quiet'],r['first_native_quiet'],max(v['geometry'] for v in trace),
            count,wfrows,b['actual_U_bad_normal_receivers'],b['actual_U_full_local_R_commit_reset_checks'],
            b['actual_remaining_execution_last_age'],len(b['actual_derived_second_upper_transitions']))
        assert observed==expected[tag],(tag,observed)
        assert n==r['first_native_quiet'] and b['fixed_adjacent_pair_covers']
        assert b['actual_U_native_words_legal'] and b['actual_legal_record_period_theorem_applied']
        assert b['complete2U_shadow'] and b['terminal_before120Q']
        assert all(v['shadow'] for v in b['actual_derived_second_upper_transitions'])
        for g,ws in b['actual_U_normal_full_words'].items():
            words=[int(v,16) for v in ws];assert len(words)==496
            assert all(0<=words[i]<limit for i,limit in enumerate((8192,1048576,2,2,2,2)))
            assert full.k.cell_words(full.k.cell_from_words(words))==words,('unmasked legal record',tag,g)
        nf=sum(len(v['actual_full_local_R_checks']) for v in trace)
        cofactors+=nf;commits+=observed[6];upper+=observed[8];rows+=n
        cases.append(dict(tag=tag,recipe=recipe,original_real1=True,actual_prefix_rows=n,
            first_GF_or_Age_quiet=observed[0],native_and_copy_closure=observed[1],
            max_GF_or_Age_disagreement_sites=observed[2],GF_canonical_proved_when_shift0=recipe['gf_shift']==0,
            actual_nonzero_WF_outputs=count,actual_nonzero_WF_rows=wfrows,
            bad_U_normal_receivers=observed[5],actual_prefix_full_local_R_checks=nf,
            actual_U_full_commit_checks=observed[6],actual_execution_last_age=observed[7],
            actual_next_upper_full_local_R_checks=observed[8],
            actual_legal_Cprime_full_normal_records=b['actual_U_normal_full_words'],
            actual_Aprime_nonzero_unused_Info=b['actual_U_nonzero_unused_Info'],
            actual_F_Cprime_checked_receivers=[v['receiver'] for v in b['actual_derived_second_upper_transitions']],
            actual_F_Cprime_full_next_records_sha256=hashlib.sha256(json.dumps(
                b['actual_derived_second_upper_transitions'],sort_keys=True,separators=(',',':')).encode()).hexdigest(),
            U_legal_broad_encoding=True,F_Cprime_equals_F2_H=True,complete2U_shadow=True))
        if count:sources[tag]=[[v['tick'],v['actual_Workspace_sources']] for v in trace if v['actual_Workspace_sources']]
    phase=load('GAW15_phase_cofactor_certificate.json');witness=load('GAW15_phase_dependency_witnesses.json')
    for name in ('GAW15_phase_cofactor_certificate.json','GAW15_phase_dependency_witnesses.json'):
        deps[str((D/name).relative_to(ROOT))]=sha(D/name)
    assert phase['passed'] and phase['phase_native_SF_cofactors']==123 and phase['actual_full_local_R_checks']==3936
    assert len(phase['all_distinct_capture_dates_checked'])==27 and phase['all_both_direction_capture_lanes_preserved']
    assert phase['real_store_centre_cases']==2 and phase['wipe_centre_cases']==41
    assert phase['actual_six_frame_chronology']['actual_last_chronological_prefix_full_local_R_checks']==3024
    assert phase['actual_six_frame_chronology']['actual17_upper_H_records_to_retained_bank_checks']==2976
    assert witness['passed'] and witness['previous_factor_premise_counterexamples_only']
    assert not witness['automaton_operational_Gray_or_iid_counterexample']
    assert len(witness['false_third_capture_and_reset_birth']['actual_wrong_stage_early_pc_copies'])==2
    assert len(witness['actual_source_forgeries'])==4
    assert (rows,cofactors,commits,upper)==(49402,4064,21292,102)
    period=ROOT/'figs/gray_counterexamples/unregistered_gaw2/GAW2_three_gather_period_certificate.json'
    inherited=json.loads(period.read_text())
    assert inherited['GAW2R_noiseless_physical_period_proved'] and inherited['three_actual_gathers_and_temporal_vote_proved']
    assert inherited['all_upper_raw_patterns_quantified']==49037 and not inherited['upper_SF_or_clock_coherence_assumed']
    proof=ROOT/'Report/proofs/gray_counterexamples/unregistered_gaw2/GAW2_THREE_GATHER_PERIOD.md'
    assert sha(proof)==inherited['proof_sha256']
    for p in (period,proof,
        ROOT/'Report/proofs/gray_counterexamples/unregistered_gaw2/gray_three_gather_gaw2r.py',
        ROOT/'Report/proofs/gray_counterexamples/unregistered_gaw2/check_gaw2_period.py',
        ROOT/'figs/gray_counterexamples/unregistered_gaw2/GAW2R_rom.json',
        ROOT/'figs/gray_counterexamples/unregistered_gaw2/GAW2R_contracts.json',
        ROOT/'figs/gray_counterexamples/unregistered_gaw2/GAW2R_compositional_cost.json'):
        deps[str(p.relative_to(ROOT))]=sha(p)
    return dict(passed=True,Q=8192,U=1048576,error_lambda=24,error_separation=104,
        actual_fault_clock=839681,actual_intact_start_same_shared_error_history=True,
        cases=cases,actual_nonzero_Workspace_traces=sources,actual_total_prefix_rows=rows,
        actual_prefix_full_local_R_checks=cofactors,actual_raw_U_commit_reset_checks=commits,
        actual_next_upper_full_local_R_checks=upper,independent_phase_cofactors=123,
        independent_phase_full_local_R_checks=3936,actual_chronological_last_update_checks=3024,
        actual17_upper_bank_checks=2976,previous_factor_premise_witnesses_only=True,
        all_selected_U_legal_adjacent_pair_and2U_shadow=True,
        inherited_broad_E_period_theorem='GAW2_THREE_GATHER_PERIOD.md',
        actual_upper_Cprime_and_unused_Aprime_pinned=True,F_Cprime_equals_F2_H_and_all_later_identity=True,
        unselected_twelve_64row_prefixes_have_no_boundary_conclusion=True,
        arbitrary_Programme_word_or_universal_mixed_repair=False,new_CA_or_shorter_U=False,
        faithful_Gray_counterexample_or_iid_reliability_or_failure=False,dependencies_sha256=deps)

if __name__=='__main__':
    r=check();(D/'GAW15_phase_packet_certificate.json').write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps({k:v for k,v in r.items() if k not in ('cases','actual_nonzero_Workspace_traces','dependencies_sha256')}),flush=True)
