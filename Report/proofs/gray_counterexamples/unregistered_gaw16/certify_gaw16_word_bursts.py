"""Aggregate four actual 16x16 histories and their typed U/2U maps."""
from pathlib import Path
import hashlib,json,sys
S=Path(__file__).resolve().parent;ROOT=S.parents[3]
sys.path.insert(0,str(S))
import continue_gaw16_word_bursts as full
m=full.m;k=m.k;D=m.D

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(name):return json.loads((D/name).read_text())

def check():
    expected={
        'word_program16':(16,16,0,0,0,[0],384,3030,17,901770,0),
        'cycle_commit_capture16':(5561,1466,61,0,0,[0],727,3030,17,901770,0),
        'word_source16':(8206,5133,5480,129,17,[1],898,3042,17,901770,6),
        'interacting_eval16':(6844,2749,61,0,0,[1],799,3030,17,901770,0)}
    cases=[];deps={};sources={};total=prefix=commit=upper=0
    for recipe in m.recipes():
        tag=recipe['tag'];p=D/(tag+'_complete.json');r=load(p.name)
        deps[str(p.relative_to(ROOT))]=sha(p)
        assert r['recipe']==recipe and r['actual_same_intact_H']
        assert (r['Q'],r['U'],r['error_lambda'],r['error_separation'],r['actual_chronological_fault_clock'])==(8192,1048576,24,104,839681)
        assert not r['new_CA_or_chosen_future_controller'] and not r['operational_or_Gray_or_iid_conclusion']
        payload=r['complete_chronological_error_payload']
        support={(v['x'],v['t']) for v in payload}
        assert len(payload)==len(support)==256
        assert support=={(x,t) for x in range(recipe['start'],recipe['start']+16) for t in range(m.T,m.T+16)}
        assert [(v['t'],v['x']) for v in payload]==sorted((v['t'],v['x']) for v in payload)
        for v in payload:
            old=[int(q,16) for q in v['old_complete_words']]
            words=[int(q,16) for q in v['replacement_complete_words']]
            assert len(old)==len(words)==496 and words!=old
            z=k.cell_from_words(words)
            assert k.cell_words(z)==words,('full replacement round trip',tag,v['x'],v['t'])
            assert all(p>1 for p in z.program)
            assert 0<=z.addr<8192 and 0<=z.age<1048576
        c=m.base.gray_errors.classify(support,support,Q=k.Q,U=k.U,sep=104,exact_limit=1)
        assert m.previous.stable(c)==m.previous.stable(r['original_c104_classification'])
        assert c['points']==256 and c['level0']==0 and tuple(c['extent'])==(16,16)
        assert c['candidate_level1'] and c['level1'] and c['sep']==104
        rows=r['actual_rows'];n=len(rows);b=r['actual_U_and2U_boundary']
        assert [v['tick'] for v in rows]==list(range(1,n+1))
        assert [v['age'] for v in rows]==list(range(m.T+1,m.T+1+n))
        assert all(v['actual_old_nonboolean_Programme_sites']==16 for v in rows[:16])
        assert all(v['actual_old_nonboolean_Programme_sites']==0 for v in rows[16:])
        assert not(rows[-1]['geometry'] or rows[-1]['native_flags'] or rows[-1]['actual_Workspace_sources'])
        closure=r['actual_quiet_coherent_closure']
        assert closure['age']==rows[-1]['age'] and not closure['actual_nonboolean_Programme']
        assert all(len(set(values))==1 for _,z in closure['changed_SF_groups'] for values in z.values())
        quiet=next(v['tick'] for v in rows[15:] if not v['geometry'])
        count=sum(len(v['actual_Workspace_sources']) for v in rows)
        wfrows=sum(bool(v['actual_Workspace_sources']) for v in rows)
        nf=sum(len(v['actual_full_local_R_checks']) for v in rows)
        observed=(n,quiet,max(v['geometry'] for v in rows),count,wfrows,b['actual_U_bad_normal_receivers'],
            nf,b['actual_U_full_local_R_commit_reset_checks'],len(b['actual_derived_second_upper_transitions']),
            b['actual_execution_last_age'],len(b['actual_U_nonzero_unused_Info']))
        assert observed==expected[tag],(tag,observed)
        assert b['terminal_by120Q'] and b['fixed_adjacent_pair_covers']
        assert not b['actual_U_illegal_native_words'] and not b['untyped_record_not_decoded_or_given_legal_period_theorem']
        assert b['actual_U_legal_E_encoding'] and b['legal_record_period_theorem_applied'] and b['complete2U_shadow']
        assert not b['general_operational_Gray_or_iid_counterexample']
        assert all(v['shadow'] for v in b['actual_derived_second_upper_transitions'])
        assert sorted(int(g) for g in b['actual_U_normal_full_words'])==list(range(-2,4))
        for g,ws in b['actual_U_normal_full_words'].items():
            words=[int(v,16) for v in ws];assert len(words)==496
            assert all(0<=words[i]<limit for i,limit in enumerate((8192,1048576,2,2,2,2)))
            assert k.cell_words(k.cell_from_words(words))==words,('unmasked legal upper',tag,g)
        assert sorted(v['receiver'] for v in b['actual_derived_second_upper_transitions'])==list(range(observed[5][0]-8,observed[5][0]+9))
        cases.append(dict(tag=tag,recipe=recipe,original_real1_256_point_support=True,actual_prefix_rows=n,
            native_and_copy_closure=n,first_GF_or_Age_quiet_after_final_fault=quiet,
            max_GF_or_Age_disagreement_sites=observed[2],actual_nonzero_WF_outputs=count,actual_nonzero_WF_rows=wfrows,
            actual_prefix_full_local_R_checks=nf,actual_U_commit_reset_checks=observed[7],actual_next_upper_full_local_R_checks=observed[8],
            actual_execution_last_age=observed[9],bad_U_normal_receivers=observed[5],
            actual_legal_Cprime_full_normal_records=b['actual_U_normal_full_words'],
            actual_Aprime_nonzero_unused_Info=b['actual_U_nonzero_unused_Info'],
            actual_F_Cprime_checked_receivers=[v['receiver'] for v in b['actual_derived_second_upper_transitions']],
            actual_F_Cprime_full_next_records_sha256=hashlib.sha256(json.dumps(
                b['actual_derived_second_upper_transitions'],sort_keys=True,separators=(',',':')).encode()).hexdigest(),
            U_legal_broad_encoding=True,F_Cprime_equals_F2_H=True,complete2U_and_all_later_shadow=True))
        if count:sources[tag]=[[v['tick'],v['actual_Workspace_sources']] for v in rows if v['actual_Workspace_sources']]
        total+=n;prefix+=nf;commit+=observed[7];upper+=observed[8]
    assert (total,prefix,commit,upper)==(20627,2808,12132,68)
    cf=load('GAW16_programme_factor_certificate.json');collision=load('GAW16_collision_phase_certificate.json')
    assert cf['passed'] and (cf['phase_full_Programme_cofactors'],cf['phase_full_local_R_checks'],
        cf['actual_nonboolean_Programme_read_holder_checks'])==(54,2646,15)
    assert cf['cofactor_signature_sha256']=='f496a238a6e0c2545e1593a6f142aebea07755cbe3b0b9fc98760293bf2986d3'
    witness=cf['actual_delayed_Programme_to_Out']
    assert witness['actual_H_T_start'] and witness['physical_fault_rows']==16
    assert witness['last_fault_time']==839696 and witness['actual_first_fresh_Programme_time']==839697
    assert len(witness['actual_full_local_R_checks'])==48
    assert witness['actual_Out_two_updates_after_last_computed_fault_row']==[hex(k.MASK)]*5
    assert witness['previous_boolean_byte_factor_inapplicable_to_this_payload'] and not witness['operational_or_Gray_or_iid_counterexample']
    assert collision['passed'] and len(collision['actual_four_timelines'])==4 and collision['full_original_classifier_rechecked']
    assert collision['actual_Workspace129_outputs_and17rows']
    assert k.unpack(int(collision['actual_interacting_incoming_collision']['actual_incoming_collision_packet'],16)).mode==k.ERROR
    for name in ('GAW16_programme_factor_certificate.json','GAW16_collision_phase_certificate.json'):
        deps[str((D/name).relative_to(ROOT))]=sha(D/name)
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
        ROOT/'figs/gray_counterexamples/unregistered_gaw2/GAW2R_compositional_cost.json',
        ROOT/'figs/gray_counterexamples/unregistered_gaw15/GAW15_standalone_assets.json',
        ROOT/'figs/gray_counterexamples/unregistered_gaw15/GAW15_phase_cofactor_certificate.json',
        ROOT/'Report/proofs/gray_counterexamples/unregistered_gaw15/GAW15_PHASE_PACKET_REPAIR.md'):
        deps[str(p.relative_to(ROOT))]=sha(p)
    chrono=json.loads((ROOT/'figs/gray_counterexamples/unregistered_gaw15/GAW15_phase_cofactor_certificate.json').read_text())['actual_six_frame_chronology']
    assert chrono['actual_last_chronological_prefix_full_local_R_checks']==3024
    assert chrono['actual17_upper_H_records_to_retained_bank_checks']==2976
    return dict(passed=True,Q=8192,U=1048576,error_lambda=24,error_separation=104,
        actual_fault_clock=839681,actual_intact_start_same_shared_error_history=True,
        actual_original_real1_16_by16_cases=4,cases=cases,actual_nonzero_Workspace_traces=sources,
        actual_total_prefix_rows=total,actual_prefix_full_local_R_checks=prefix,
        actual_raw_U_commit_reset_checks=commit,actual_next_upper_full_local_R_checks=upper,
        independent_full_Programme_phase_cofactors=54,independent_phase_full_local_R_checks=2646,
        actual_nonboolean_Programme_read_holder_checks=15,actual_delayed_read_following_full_local_R_checks=48,
        inherited_chronological_last_update_checks=3024,inherited_actual17_upper_bank_checks=2976,
        boolean_Programme_refresh_all_raw_local_equation=True,old_boolean_Programme_factor_inapplicable_to_current_errors=True,
        all_selected_U_legal_adjacent_pair_and2U_shadow=True,actual_Cprime_Aprime_and_F_Cprime_pinned=True,
        arbitrary_Programme_or_mixed16by16_repair_unproved=True,
        faithful_Gray_counterexample_or_iid_reliability_or_failure=False,new_CA_or_shorter_U=False,
        beta_fit_Q_or_dictionary512=False,dependencies_sha256=deps)

if __name__=='__main__':
    r=check();(D/'GAW16_word_burst_certificate.json').write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps({key:value for key,value in r.items() if key not in ('cases','actual_nonzero_Workspace_traces','dependencies_sha256')}),flush=True)
