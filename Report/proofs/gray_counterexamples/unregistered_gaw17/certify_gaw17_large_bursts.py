"""Pin complete large-burst histories without decoding invalid U records."""
from pathlib import Path
import hashlib,json,sys
S=Path(__file__).resolve().parent;ROOT=S.parents[3]
sys.path.insert(0,str(S))
import continue_gaw17_large_bursts as full
m=full.m;k=m.k;D=m.D

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(name):return json.loads((D/name).read_text())

def check():
    expected={
      'native_program104':(104,104,0,0,0,[0],896,3031,0,0,5),
      'cycle_control104':(2324,131,105,0,0,[0],1344,3030,17,0,0),
      'source_flags104':(4227,130,104,312,104,[],1792,3045,0,9,0),
      'interacting104':(6946,2851,413,0,0,[0,1],2782,3030,18,0,0),
      'sparse_span150':(6946,2851,413,593,119,[1],2425,3030,17,0,0)}
    cases=[];deps={};sources={};total=prefix=commit=upper=points=0
    def pin(p):deps[str(p.relative_to(ROOT))]=sha(p)
    planned=load('GAW17_support_classification.json')
    assert m.previous.stable(m.support_audit())==m.previous.stable(planned)
    pin(D/'GAW17_support_classification.json')
    for recipe in m.recipes():
        tag=recipe['tag'];p=D/(tag+'_complete.json');r=load(p.name);pin(p)
        assert r['recipe']==recipe and r['actual_same_intact_H'] and r['full_planned_error_burst_executed']
        assert (r['Q'],r['U'],r['error_lambda'],r['error_separation'],r['actual_chronological_fault_clock'])==(8192,1048576,24,104,839681)
        assert not r['new_CA_or_chosen_future_controller'] and not r['operational_or_Gray_or_iid_conclusion']
        payload=r['complete_chronological_error_payload'];support={(v['x'],v['t']) for v in payload}
        desired={(x,m.T+t) for t in range(104) for x in m.sites(recipe,t)}
        assert len(payload)==len(support)==len(desired)==10816+(2 if recipe['sparse_ends'] else 0)
        assert support==desired and [(v['t'],v['x']) for v in payload]==sorted((v['t'],v['x']) for v in payload)
        for v in payload:
            old=[int(w,16) for w in v['old_complete_words']];words=[int(w,16) for w in v['replacement_complete_words']]
            assert len(old)==len(words)==496 and old!=words
            z=k.cell_from_words(words);assert k.cell_words(z)==words
            assert all(q>1 for q in z.program)
            assert all(q in (0,1) for q in k.cell_from_words(old).program)
            assert 0<=z.addr<8192 and 0<=z.age<1048576
        c=m.classify(support);assert c==r['original_c104_classification']
        assert c['level1'] and c['level0']==0 and c['sep']==104
        rows=r['actual_rows'];n=len(rows);b=r['actual_U_and2U_boundary'];closure=r['actual_quiet_coherent_closure']
        assert [v['tick'] for v in rows]==list(range(1,n+1))
        assert [v['age'] for v in rows]==list(range(m.T+1,m.T+1+n))
        assert [v['actual_old_nonboolean_Programme_sites'] for v in rows[:104]]==[106 if recipe['sparse_ends'] else 104]+[104]*103
        assert all(v['actual_old_nonboolean_Programme_sites']==0 for v in rows[104:])
        assert not(rows[-1]['geometry'] or rows[-1]['native_flags'] or rows[-1]['actual_Workspace_sources'])
        assert closure['age']==rows[-1]['age'] and not closure['actual_nonboolean_Programme']
        assert all(len(set(v))==1 for _,z in closure['changed_SF_groups'] for v in z.values())
        quiet=next(v['tick'] for v in rows[103:] if not v['geometry'])
        wf=sum(len(v['actual_Workspace_sources']) for v in rows);wfrows=sum(bool(v['actual_Workspace_sources']) for v in rows)
        checks=sum(len(v['actual_full_local_R_checks']) for v in rows)
        observed=(n,quiet,max(v['geometry'] for v in rows),wf,wfrows,b['actual_U_bad_normal_receivers'],checks,
            b['actual_U_full_local_R_commit_reset_checks'],len(b['actual_derived_second_upper_transitions']),
            len(b['actual_U_nonzero_unused_Info']),len(b['actual_U_illegal_native_words']))
        assert observed==expected[tag],(tag,observed)
        assert b['terminal_by120Q'] and b['actual_execution_last_age']==901770 and b['fixed_adjacent_pair_covers']
        assert not b['general_operational_Gray_or_iid_counterexample']
        if tag=='native_program104':
            assert b['actual_U_normal_full_words']['0'][:6]==['0x0']+[hex(k.MASK)]*5
            assert b['actual_U_illegal_native_words']==[[0,i,hex(k.MASK),1048576 if i==1 else 2] for i in range(1,6)]
            assert not b['actual_U_legal_E_encoding'] and not b['legal_record_period_theorem_applied']
            assert b['untyped_record_not_decoded_or_given_legal_period_theorem']
            assert not b['actual_derived_second_upper_transitions'] and not b['complete2U_shadow']
            outcome='unproved: illegal native padding; not an observed 2U disagreement'
        else:
            assert not b['actual_U_illegal_native_words'] and b['actual_U_legal_E_encoding']
            assert b['legal_record_period_theorem_applied'] and b['complete2U_shadow']
            assert not b['untyped_record_not_decoded_or_given_legal_period_theorem']
            for g,ws in b['actual_U_normal_full_words'].items():
                words=[int(v,16) for v in ws]
                assert len(words)==496 and k.cell_words(k.cell_from_words(words))==words
                assert all(0<=words[i]<limit for i,limit in enumerate((8192,1048576,2,2,2,2)))
            assert all(v['shadow'] for v in b['actual_derived_second_upper_transitions'])
            assert sorted(v['receiver'] for v in b['actual_derived_second_upper_transitions'])==sorted({g+d for g in observed[5] for d in range(-8,9)})
            outcome='proved full raw 2U and all later shadow via legal broad-E composition'
        cases.append(dict(tag=tag,recipe=recipe,original_real1_classification=c,actual_points=len(support),
            actual_prefix_rows=n,first_GF_or_Age_quiet_after_final_fault=quiet,max_GF_or_Age_disagreement_sites=observed[2],
            actual_WF_outputs=wf,actual_WF_rows=wfrows,actual_prefix_full_local_R_checks=checks,
            actual_U_commit_reset_checks=observed[7],actual_next_upper_full_local_R_checks=observed[8],
            actual_U_bad_normal_receivers=observed[5],actual_U_normal_full_words=b['actual_U_normal_full_words'],
            actual_U_Aprime_nonzero_unused_Info=b['actual_U_nonzero_unused_Info'],
            actual_U_illegal_native_words=b['actual_U_illegal_native_words'],
            actual_U_legal_E_encoding=b['actual_U_legal_E_encoding'],
            literal_narrow_E_of_any_legal_upper_C_excluded=tag=='native_program104',
            actual_next_upper_full_records_sha256=sha_bytes(b['actual_derived_second_upper_transitions']),
            second_boundary_outcome=outcome,second_boundary_equality=True if tag!='native_program104' else None))
        if wf:sources[tag]=[[v['tick'],v['actual_Workspace_sources']] for v in rows if v['actual_Workspace_sources']]
        total+=n;prefix+=checks;commit+=observed[7];upper+=observed[8];points+=len(support)
    assert (total,prefix,commit,upper,points)==(20547,9239,15166,52,54082)
    inherited=ROOT/'figs/gray_counterexamples/unregistered_gaw16/GAW16_standalone_assets.json';pin(inherited)
    for p in (ROOT/'Report/proofs/gray_counterexamples/unregistered_gaw16/search_gaw16_word_bursts.py',
        ROOT/'Report/proofs/gray_counterexamples/unregistered_gaw16/continue_gaw16_word_bursts.py',
        ROOT/'Report/proofs/gray_counterexamples/unregistered_gaw16/GAW16_WORD_PROGRAMME_BURSTS.md',
        ROOT/'figs/gray_counterexamples/unregistered_gaw2/GAW2_three_gather_period_certificate.json',
        ROOT/'Report/proofs/gray_counterexamples/unregistered_gaw2/GAW2_THREE_GATHER_PERIOD.md'):
        pin(p)
    period=json.loads((ROOT/'figs/gray_counterexamples/unregistered_gaw2/GAW2_three_gather_period_certificate.json').read_text())
    assert period['GAW2R_noiseless_physical_period_proved'] and period['all_upper_raw_patterns_quantified']==49037
    assert not period['upper_SF_or_clock_coherence_assumed']
    assert sha(ROOT/'Report/proofs/gray_counterexamples/unregistered_gaw2/GAW2_THREE_GATHER_PERIOD.md')==period['proof_sha256']
    return dict(passed=True,Q=8192,U=1048576,error_lambda=24,error_separation=104,actual_fault_clock=m.T,
        actual_recursive_intact_H_same_history=True,actual_complete_original_real1_histories=5,
        actual_genuine_whole_cell_replacements=points,cases=cases,actual_nonzero_Workspace_traces=sources,
        actual_total_prefix_rows=total,actual_prefix_full_local_R_checks=prefix,
        actual_U_commit_reset_checks=commit,actual_next_upper_full_local_R_checks=upper,
        four_selected_legal_U_adjacent_pair_and_full2U_shadow=True,
        actual_illegal_U_normal_record_native_Age_Flags_WF_pinned=True,
        illegal_U_record_not_decoded_or_given_legal_upper_theorem=True,
        one_actual_boundary_outside_literal_narrow_E=True,
        illegal_case_eventual_repair_or_memory_failure_unproved=True,
        sparse_span150_valid_original_real1_and_dense150_rejected=True,
        classifier_serialization_failure_retained_no_trajectory_rule_change=True,
        universal_mixed_repair_or_Gray_iid_counterexample=False,new_CA_shorter_U_or_beta_fit_Q=False,
        dependencies_sha256=deps)

def sha_bytes(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()

if __name__=='__main__':
    r=check();(D/'GAW17_large_burst_certificate.json').write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps({key:value for key,value in r.items() if key not in ('cases','actual_nonzero_Workspace_traces','dependencies_sha256')}),flush=True)
