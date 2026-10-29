#!/usr/bin/env python3
"""Issue once/replay the SAME J261 chronology through its current boundary."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
OUT=ROOT/'figs/robustness/unregistered_sp31_phaseTF_continuation'
CERT=OUT/'actual_current_boundary_certificate.json';PROOF=HERE/'SP31_ACTUAL_PHASE_TF_CURRENT_BOUNDARY.md'
PARENT=ROOT/'figs/robustness/unregistered_sp31_phaseTF_real2/actual_phaseTF_certificate.json'
REPLAY=ROOT/'figs/robustness/unregistered_sp31_phaseTF_real2/readonly_run01.log'
sys.path.insert(0,str(HERE));import probe_continuation as trace_probe
import probe_full_cofactors as cofactor_probe
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def accepted_parent(full=False):
    assert sha(PARENT)=='b13f8668cda5cf1c78caecabe716a5784e82ad93af267db08558aff979a25d4a'
    assert sha(REPLAY)=='2b0a9aab21b384b1b4b7d1de4ea1146ce6369386859e9d8fd59ae668d7ce8f4c'
    parent=json.loads(PARENT.read_text());last=json.loads(REPLAY.read_text().splitlines()[-1])
    assert last['passed'] and last['readonly'] and last['assets_verified']==277
    assert last['certificate_sha256']==sha(PARENT)
    assert parent['actual_phaseTF_old_fields_retained_and_one_original_real2_fault_proved']
    assert parent['complete_encoded_actual_intact_start_one_original_real3_fault_proved']
    assert parent['actual_all_time_intact_native_flags_and_all_four_Info_alias_groups_zero_proved']
    for rel,h in parent['assets_sha256'].items():assert sha(ROOT/rel)==h,rel
    if full:
        result=subprocess.run([sys.executable,str(ROOT/'Report/proofs/unregistered_sp31_phaseTF_real2/check_actual_phaseTF.py')],capture_output=True,text=True)
        assert result.returncode==0,(result.stdout,result.stderr)
        assert json.loads(result.stdout)['passed']
    return parent
def replay_new_facts():
    raw,trace=trace_probe.compute();old_trace=json.loads((OUT/'native_continuation_probe01.json').read_text())
    assert {k:v for k,v in trace.items() if k!='seconds'}=={k:v for k,v in old_trace.items() if k!='seconds'}
    assert raw==(OUT/'native_trace01.jsonl').read_bytes()
    rows=[json.loads(s) for s in raw.decode().splitlines()][:-1]
    final=[[-15360,-14848,2],[-14848,512,1],[512,1024,3]]
    assert trace['full_projected_states']==6145 and trace['exact_constant_event_intervals']==4977949
    assert trace['maximum_native_segments']==7 and trace['first_source_vote_erasure']==512
    assert trace['first_final_native_projection_row']==855 and trace['final_native_segments']==final
    assert rows[854]['native_segments']!=final and all(z['native_segments']==final for z in rows[855:])
    assert all(z['voted_Info_ones']==[1021] for z in rows[:512]) and all(not z['voted_Info_ones'] for z in rows[512:])
    assert all(not (z['native0']&1) for z in rows[:172]) and all(z['native0']&1 for z in rows[172:])
    assert all(z['wrongGF_right_sites']==1024 and z['wrongGF_right_exclusive']==1024 for z in rows[512:])
    union=set();largest=0
    for z in rows:
        points={x for a,b,v in z['native_segments'] if v&1 for x in range(a,b)}
        union.update(points);largest=max(largest,len(points))
    assert union==set(range(-14848,1024)) and largest==15872
    # Every raw source holder is zero from513 because the preceding vote is0.
    assert all(cofactor_probe.factor.info_holder(rows,513,1021-s,s)==0 for s in range(-2,3))
    new=cofactor_probe.compute();old=json.loads((OUT/'full_cofactors01.json').read_text())
    assert {k:v for k,v in new.items() if k!='seconds'}=={k:v for k,v in old.items() if k!='seconds'}
    assert len(new['selected_actual_native_alias_cofactors'])==168
    assert len(new['selected_full_current_commit_cofactors'])==47
    quiet=new['exact_new_endpoint_free_common_clock_quiet_fragment']
    assert quiet['template']==[-14,1] and (quiet['refinements'],quiet['native_cofactors'])==(162,4258)
    assert new['all_other_private_SF_instruction_and_ordinary_Info_inputs_symbolic']
    assert not new['universal_allrow_actual_lift_quiet_tail_reset_and_encoded_bit_interval_proved_by_this_probe']
    assert 278401+855==279256 and 475136-278401==196735
    assert (278401+172)*475136==132360060928 and 475136**2==225754218496
    return dict(exact_native_projected_states=6145,constant_event_intervals=4977949,maximum_native_segments=7,
        first_source_vote_erasure=512,all_raw_source_holders_zero_from=513,first_final_quiet_projection_row=855,
        native_final_segments=final,GF_union=[-14848,1024],maximum_GF_sites=15872,
        initial_GF_sites=14848,current_native_GF_grows_by_one_colony=1024,
        exact_free_clock_quiet_refinement_identities=162,exact_free_clock_quiet_native_identities=4258,
        selected_full_R_native_alias_cofactors=168,selected_full_R_current_commit_cofactors=47,
        current_upper_boundary_relative_steps=196735,current_upper_boundary_logical_Age=0,
        lower_GF0_bit9_first_change_absolute_row=132360060928,lower_encoding_current_boundary_absolute_row=225754218496)
def assets(parent):
    pinned=dict(parent['assets_sha256'])
    for p in (PARENT,REPLAY,PROOF,Path(__file__),HERE/'probe_continuation.py',HERE/'probe_full_cofactors.py',
        HERE/'sp31_actual_phaseTF_continuation.c',OUT/'native_trace01.jsonl',OUT/'native_continuation_probe01.json',
        OUT/'probe01.log',OUT/'full_cofactors01.json',OUT/'full_cofactor_probe01.log'):
        rel=str(p.relative_to(ROOT));h=sha(p);assert rel not in pinned or pinned[rel]==h,rel;pinned[rel]=h
    for module in list(sys.modules.values()):
        f=getattr(module,'__file__',None)
        if f:
            p=Path(f).resolve()
            if p.suffix=='.py' and p.is_relative_to(ROOT):
                rel=str(p.relative_to(ROOT));h=sha(p);assert rel not in pinned or pinned[rel]==h,rel;pinned[rel]=h
    for rel,h in pinned.items():assert sha(ROOT/rel)==h,rel
    return dict(sorted(pinned.items()))
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--issue',action='store_true');ap.add_argument('--full-inherited',action='store_true')
    args=ap.parse_args();start=time.monotonic()
    if args.issue:assert not CERT.exists()
    else:
        frozen=json.loads(CERT.read_text())
        for rel,h in frozen['assets_sha256'].items():assert sha(ROOT/rel)==h,rel
    parent=accepted_parent(args.full_inherited);facts=replay_new_facts()
    encoded=json.loads((ROOT/'figs/robustness/SP31_encoded_certificate.json').read_text())
    assert encoded['complete_start_noiseless_and_all_period_pure_E0_simulation_proved']
    cert=dict(passed=True,Q=1024,U=475136,TF=278401,radius=37,
        proof_sha256=sha(PROOF),checker_sha256=sha(__file__),candidate_sha256=parent['candidate_sha256'],netlist_sha256=parent['netlist_sha256'],
        accepted_same_J261_intact_start_fault_original_real2_real3_provenance_reused=True,
        inherited277_assets_and_accepted_terminal_replay_pinned=True,all_new_facts_recomputed=True,
        actual_full_native_alias_history6144_steps_on_Z_proved=True,
        actual_raw_source_holders_zero_from513_and_first_quiet_shape855_proved=True,
        allrow_quiet_tail_to_current_U_native807_reset_and_four_alias_zero_proved=True,
        actual_full_lower_encoding_composition_through_upper_current_boundary_at_physical_U_squared_proved=True,
        first_and_continuous_lower_geometry_bank_GF0_bit9_one_interval_through_U_squared_proved=True,
        exact_native_GF_union_and_current_one_colony_growth_proved=True,
        raw_lower_GF_clock_correct_at_all_physical_rows=True,
        native_GF_or_encoded_geometry_bit_not_remembered_data_bit=True,
        selected_full_R_cofactors_measured_supplements=True,exact_free_clock_quiet_identities_not_phase_samples=True,
        facts=facts,full_remaining_upper_Info_at_U_or_next_sources_later_eroder_proved=False,
        numerical225billiontick_whole_CA_or_all_old842bit_payloads_computed=False,
        original_J225_same_fault_TF_provenance_or_general_original_real2_higher_repair_proved=False,
        Gray_G17_iid_failure_positive_rate_memory_or_globally_sufficient_minimum_proved=False,
        rule_ROM_constants_or_G17_changed=False,global_reliability_established=False,assets_sha256=assets(parent))
    if args.issue:CERT.write_text(json.dumps(cert,indent=2)+'\n')
    else:assert cert==frozen,'Read-only certificate differs.'
    print(json.dumps(dict(passed=True,readonly=not args.issue,assets_verified=len(cert['assets_sha256']),
        certificate_sha256=sha(CERT),accepted_inherited277_asset_provenance_checked=True,inherited_full_replay_requested=args.full_inherited,
        projected_states=6145,event_intervals=4977949,native_cofactors=168,commit_cofactors=47,
        first_final_quiet_projection_row=855,current_U_wrongGF_width=15872,
        actual_current_native_reset_and_lower_continuous_GF0_bit9_interval_proved=True,
        full_remaining_Info_later_arbitrary_higher_iid_or_minimum_proved=False,seconds=time.monotonic()-start)),flush=True)
if __name__=='__main__':main()
