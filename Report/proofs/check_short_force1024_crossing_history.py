#!/usr/bin/env python3
"""Actual crossing-history bridge for emerging foreign frame121 only.

The written proof supplies clearing, fixed-frame suffix and commit lifts.
No full third mask/pulse, general eroder or positive iid rate is asserted.
"""
from pathlib import Path
import hashlib,json,sys,time
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
import proposed_sparse_short_force1024 as proposed
from check_short_force1024_protected_scratch import blocked


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    begin=time.monotonic();out=ROOT/'figs/robustness';p=proposed.parameters();candidate=proposed.load_artifact()
    listing_path=out/'SP29_program_listing.json';listing=json.loads(listing_path.read_text())
    probe=json.loads((out/'SP29_crossing_history_probe.json').read_text())
    assert probe['checker_sha256']==digest(ROOT/'Report/proofs/probe_short_force1024_crossing_history.py')
    assert probe['proposed_candidate_sha256']==candidate.digest()
    case=probe['cases'][1]
    assert (case['mode'],case['instructions'],case['terms'],case['target_constant'])==('crossing_histories_zero',41477,37458,0)
    assert case['dependency_variables']==[] and case['physical_premises_proved'] is False
    table=proposed.dependency_table(p);byphase={r['address']:r for r in table}
    old_strip=(121*p.Q,121*p.Q+512);strips=(old_strip,(135*p.Q+512,136*p.Q))
    selected=[r for r in table if r['field']=='h2' and r['bit'] in (141,205,269)]
    assert [(r['bit'],r['address']) for r in selected]==[(141,573),(205,637),(269,701)]
    crossing=[];captured=uncaptured=0
    for row in selected:
        physical_phase=(row['address']+512)%p.Q;y=121*p.Q+physical_phase
        assert physical_phase in (61,125,189)
        assert old_strip[0]<=y-2-37 and y+2+37<old_strip[1]
        old=byphase[physical_phase]
        assert old['field']==('addr' if physical_phase==61 else 'h1')
        assert len(old['offsets'])==(64 if physical_phase==61 else 8)
        assert len(row['offsets'])==8
        captures=[]
        for rank,d in enumerate(old['offsets']):
            ages=[g*p.Q+abs(d)*(p.Q//8)+1 for g in p.gathers_q]
            assert all(age<p.E0 for age in ages)
            captured+=len(ages)
            captures.append(dict(rank=rank,old_offset=d,capture_computed_ages=ages,passing_mail_zero_at_target=True))
        uncaptured+=64-len(old['offsets'])
        crossing.append(dict(bit=row['bit'],virtual_phase=row['address'],physical_true_phase=physical_phase,
            physical_primary=y,holder_radius37_footprint=[y-39,y+40],old_field=old['field'],old_bit=old['bit'],
            actual_old_capture_rank_records=captures,requested_history_ranks_zero=list(range(8)),
            all_64_H1_H2_history_ranks_zero=True,direct_Info_left_free=True))
    assert captured==240 and uncaptured==112
    # Confirm the literal clearing and protected-window equations used.
    source=proposed.generated_source(p)
    assert source.count("        mr = n.AND(mr, n.NOT(f1_new))")==1
    assert source.count("        ml = n.AND(ml, n.OR(n.NOT(f1_new), protected_flag2_courier))")==1
    assert p.E0<p.courier_ticks()[1]
    margin=[]
    for bit in (13,77):
        row=next(r for r in table if r['field']=='h2' and r['bit']==bit)
        phase=(row['address']+512)%p.Q
        assert phase in (957,1021) and phase not in byphase
        margin.append(dict(bit=bit,physical_true_colony=120,physical_phase=phase,
            direct_Info_zero_by_first_unused_commit=True,uncaptured_reset_zero_history_ranks=list(range(8))))
    mail=[];inside=cleared=unused=0
    for row in table:
        if row['field'] not in ('mr','ml'):continue
        phase=row['address']+512;old=byphase[phase]
        assert 614<=phase<=623 and old['field']=='h2' and 182<=old['bit']<=191
        assert old['offsets']==[-4,-3,-2,-1,1,2,3,4]
        assert len(row['offsets'])==10
        ranks=[]
        for rank in range(10):
            if rank>=len(old['offsets']):
                unused+=1;ranks.append(dict(rank=rank,old_offset=None,no_capture_and_initial_reset_zero=True));continue
            d=old['offsets'][rank];erased=blocked(strips,120,d,phase,p.Q)
            assert erased or 120+d<=120
            ages=[g*p.Q+abs(d)*(p.Q//8)+1 for g in p.gathers_q]
            assert max(ages)<p.E0
            inside+=len(ages)*int(not erased);cleared+=len(ages)*int(erased)
            ranks.append(dict(rank=rank,old_offset=d,cleared_by_old_strip=erased,capture_computed_ages=ages))
        mail.append(dict(field=row['field'],bit=row['bit'],physical_true_colony=120,physical_phase=phase,
                         first_left_H2_source_bit=old['bit'],actual_old_rank_records=ranks))
    assert (len(mail),inside,cleared,unused)==(10,120,120,20)
    target=120*p.Q+1021;endpoint=0;asset=out/'SP29_second_pulse_case_final_states.npz'
    with np.load(asset,allow_pickle=False) as arrays:
        for mask in range(8):assert arrays[f'case{mask}_Info'][target]==0;endpoint+=1
    assert 118272<=target-2 and target+2<131072 and (target+512)%p.Q==509
    origin=121*p.Q-512
    assert 118272<=origin+1 and origin+1022<131072
    rows=[r for r in listing if r[4]==509 and r[6]==1];assert len(rows)==1
    row=rows[0];issue=p.E0+row[1]*p.PL+row[2]
    assert issue==357736 and issue+2==357738 and issue>p.E0+280*p.PL
    assert np.flatnonzero(((candidate.rom[509]>>2)&3)==1).tolist()==[row[1]+(row[3]<<p.logNP)]
    deps=('SP29_crossing_history_probe.json','SP29_emerging_foreign_source_certificate.json',
        'SP29_foreign_cache_erasure_certificate.json','SP29_protected_scratch_certificate.json',
        'SP29_first_boundary_signal_data_certificate.json','SP29_second_signal_enclosure_certificate.json',
        'SP29_second_right_boundary_certificate.json','SP29_next_ghost_signal_certificate.json',
        'SP29_refined_wipe_certificate.json','SP29_symbolic_schedule.json','SP29_front_certificate.json',
        'SP29_encoding_family_certificate.json')
    receipt=dict(proposal='SP29',scope='Actual retained MF1021(120) by old Flag1-strip zero histories and arbitrary-work suffix; original clock0 error/no later errors; no full third pulse or iid',
        Q=p.Q,U=p.U,T_wf=p.T_wf,late_suffix_instructions=case['instructions'],late_suffix_terms=case['terms'],
        direct_crossing_Info_values_free=True,shifted_prefix_cache_or_native_readonly_zero_premise_used=False,
        emerging_foreign_frame=121,actual_old_Flag1_strip=list(old_strip),crossing_history_family_records=crossing,
        crossing_actual_capture_rank_count=80,crossing_actual_three_gather_capture_checks=captured,
        crossing_uncaptured_reset_zero_history_rank_count=uncaptured,crossing_total_zero_history_rank_count=192,
        two_unused_margin_family_records=margin,margin_uncaptured_reset_zero_history_rank_count=16,
        mailbox_family_records=mail,mailbox_actual_capture_route_checks=inside+cleared,
        mailbox_zero_source_capture_routes=inside,mailbox_strip_cleared_capture_routes=cleared,
        mailbox_uncaptured_reset_zero_history_rank_count=unused,all_eight_endpoint_selected_Info_zero_checks=endpoint,
        second_pulse_final_state_asset_sha256=digest(asset),Hold509_issue_age=issue,Hold509_materialization_age=issue+2,
        second_U_retained_MF1021_zero_colony=120,third_TF_retained_MF1021_zero_colony=120,
        retained_zero_Info_copy_count=5,third_signal_computed_time=2*p.U+p.T_wf,
        actual_crossing_history_source_and_suffix_bridge_proved=True,
        all_twelve_interior_MF1021_115_through_126_zero_by_composition=True,
        recovered_right_or_partial_retained_data_proved=False,complete_third_signal_or_pulse_proved=False,
        general_eroder_higher_map_or_positive_iid_rate_proved=False,global_reliability_established=False,
        numerical_whole_CA_trajectory_used=False,active_G17_modified=False,rule_programme_or_constant_change=False,
        checker_sha256=digest(__file__),written_proof_sha256=digest(ROOT/'Report/proofs/SP29_CROSSING_HISTORY.md'),
        proposal_source_sha256=digest(proposed.__file__),helper_sha256=digest(ROOT/'Report/proofs/check_short_force1024_protected_scratch.py'),
        listing_sha256=digest(listing_path),proposed_candidate_sha256=candidate.digest(),proposed_netlist_sha256=candidate.comp.digest,
        receipt_dependencies_sha256={name:digest(out/name) for name in deps},seconds=time.monotonic()-begin)
    (out/'SP29_crossing_history_certificate.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({key:receipt[key] for key in ('crossing_actual_three_gather_capture_checks',
        'mailbox_actual_capture_route_checks','third_TF_retained_MF1021_zero_colony','seconds','global_reliability_established')}),flush=True)


if __name__=='__main__':main()
