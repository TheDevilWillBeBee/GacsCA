#!/usr/bin/env python3
"""Physical first-left H1/unused zeros and five second foreign suffixes.

The written proof supplies the physical phase/pending/capture/commit lifts.
No complete third mask/pulse, general eroder or iid theorem is claimed.
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
    probe=json.loads((out/'SP29_emerging_foreign_source_probe.json').read_text())
    assert probe['checker_sha256']==digest(ROOT/'Report/proofs/probe_short_force1024_emerging_foreign_sources.py')
    assert probe['proposed_candidate_sha256']==candidate.digest()
    case=probe['cases'][0];assert case['mode']=='true_history_and_mail_zero'
    assert case['late_instructions']==41477
    assert case['outputs']['h1']['constant_bits']=={str(bit):0 for bit in range(320)}
    assert case['outputs']['h2']['constant_bits']=={str(bit):0 for bit in range(320)}
    table=proposed.dependency_table(p);phases={(r['field'],r['bit']):r['address'] for r in table}
    h1_issues=[]
    for bit in range(320):
        phase=phases['h1',bit];rows=[row for row in listing if row[4]==phase and row[6]==1]
        assert len(rows)==1
        row=rows[0];age=p.E0+row[1]*p.PL+row[2]
        assert age>p.E0+280*p.PL
        assert np.flatnonzero(((candidate.rom[phase]>>2)&3)==1).tolist()==[row[1]+(row[3]<<p.logNP)]
        h1_issues.append(dict(bit=bit,phase=phase,input_issue_age=age,materialization_age=age+2))
    source=proposed.generated_source(p)
    mask_line='        encoded_primary = n.OR(w_in_range(n, xaddr, p.lo, p.lo+sum(w for _,w in sch)+1), w_eq_const(n, xaddr, p.hi-1))'
    assert source.count(mask_line)==1
    mask_ranges=[p.lo,p.lo+sum(width for field,width in candidate.schema)+1]
    assert mask_ranges==[58,901] and p.hi-1==965
    assert all(not (mask_ranges[0]<=phase<mask_ranges[1] or phase==p.hi-1) for phase in (957,1021))
    unused_issues=[];romkeys=0
    for phase in (445,509,957,1021):
        rows=[row for row in listing if row[4]==phase and row[6]==1]
        assert len(rows)==int(phase<512)
        columns=np.flatnonzero(((candidate.rom[phase]>>2)&3)==1).tolist()
        assert columns==[row[1]+(row[3]<<p.logNP) for row in rows]
        for row in rows:assert p.E0+row[1]*p.PL+row[2]>284545
        unused_issues.append(dict(phase=phase,Hold_issue_ages=[p.E0+r[1]*p.PL+r[2] for r in rows]))
        romkeys+=candidate.rom.shape[1]
    assert romkeys==16384
    old_strips=((121*p.Q,121*p.Q+512),(135*p.Q+512,136*p.Q))
    selected=[r for r in table if r['field'] in ('mr','ml') or r['field']=='h2' and r['bit'] in (13,77,205,269)]
    assert len(selected)==14
    records=[];actual_records=[];direct=clear=inside=actual_clear=actual_inside=unused_ranks=0
    byphase={r['address']:r for r in table}
    for h in range(116,121):
        for row in selected:
            phase=(row['address']+512)%p.Q
            # Physical source primaries are indexed relative to a true
            # colony; the added carry is needed at wrapped virtual phases.
            j=h-1+int(row['address']>=512)
            field,bit=row['field'],row['bit']
            if field=='h2':assert phase in (957,1021,125,189)
            else:assert 614<=phase<=623
            assert j<=120
            direct+=1
            for d in row['offsets']:
                erased=blocked(old_strips,j,d,phase,p.Q)
                assert erased or j+d<=120,(h,field,bit,d,phase,j+d)
                for gather in p.gathers_q:
                    assert gather*p.Q+abs(d)*(p.Q//8)+1<p.E0
                    clear+=int(erased);inside+=int(not erased)
                records.append(dict(foreign_frame=h,field=field,bit=bit,physical_true_colony=j,
                                    physical_phase=phase,offset=d,cleared_by_old_strip=erased))
            old_offsets=byphase.get(phase,{}).get('offsets',[])
            for rank in range(len(row['offsets'])):
                if rank>=len(old_offsets):
                    unused_ranks+=1
                    actual_records.append(dict(foreign_frame=h,field=field,bit=bit,rank=rank,
                        physical_true_colony=j,physical_phase=phase,actual_pre_pulse_offset=None,
                        no_capture_and_initial_reset_zero=True))
                    continue
                d=old_offsets[rank];erased=blocked(old_strips,j,d,phase,p.Q)
                assert erased or j+d<=120,(h,field,bit,rank,d,phase,j+d)
                for gather in p.gathers_q:
                    assert gather*p.Q+abs(d)*(p.Q//8)+1<p.E0
                    actual_clear+=int(erased);actual_inside+=int(not erased)
                actual_records.append(dict(foreign_frame=h,field=field,bit=bit,rank=rank,
                    physical_true_colony=j,physical_phase=phase,actual_pre_pulse_offset=d,
                    cleared_by_old_strip=erased))
    assert direct==70 and inside+clear==1980
    assert actual_inside+actual_clear==1440 and unused_ranks==180
    suffix=json.loads((out/'SP29_second_right_boundary_certificate.json').read_text())
    assert suffix['actual_first_five_H2_raw_copy_zeros_proved']
    assert suffix['first_suffix_instructions']==41477
    assert suffix['first_boundary_zero_raw_H2_bits']==[13,77,141,205,269]
    zero_primaries=[j*p.Q+1021 for j in range(115,120)]
    assert all(118272<=y-2 and y+2<131072 for y in zero_primaries)
    assert all((y+512)%p.Q==509 for y in zero_primaries)
    pulse_asset=out/'SP29_second_pulse_case_final_states.npz';endpoint_checks=0
    with np.load(pulse_asset,allow_pickle=False) as arrays:
        for mask in range(8):
            assert all(arrays[f'case{mask}_Info'][y]==0 for y in zero_primaries)
            endpoint_checks+=len(zero_primaries)
    dependencies=('SP29_emerging_foreign_source_probe.json','SP29_second_right_boundary_certificate.json',
        'SP29_protected_scratch_certificate.json','SP29_first_boundary_signal_data_certificate.json',
        'SP29_second_signal_enclosure_certificate.json','SP29_next_ghost_signal_certificate.json',
        'SP29_refined_wipe_certificate.json','SP29_symbolic_schedule.json','SP29_front_certificate.json',
        'SP29_encoding_family_certificate.json','SP29_emerging_foreign_source_initial_failure.json')
    receipt=dict(proposal='SP29',scope='Actual first-left full H1/unused-primary zeros and five emerging-foreign second-U retained zeros; original clock0 error/no later errors; no complete third mask or iid',
        Q=p.Q,U=p.U,T_wf=p.T_wf,first_left_zero_raw_H1_bits=320,first_left_zero_encoded_Info_copies_per_frame=1600,
        first_left_H1_zero_colonies_upper_bound=120,first_suffix_instructions=case['late_instructions'],
        first_suffix_terms=case['terms'],first_H1_actual_Hold_issue_records=h1_issues,
        first_unused_zero_true_phases=[957,1021],first_unused_zero_true_colonies_upper_bound=120,
        actual_Info_commit_mask_range=mask_ranges,actual_Info_commit_mask_additional_phase=p.hi-1,
        first_unused_zero_Info_commit_mask_copy_checks=10,
        two_phase_unused_Hold_issue_records=unused_issues,two_phase_unused_Hold_ROM_key_checks=romkeys,
        second_new_foreign_frame_colonies=list(range(116,121)),second_new_foreign_source_families=14,
        second_new_foreign_direct_primary_checks=direct,second_new_foreign_capture_route_checks=inside+clear,
        second_new_foreign_zero_source_capture_routes=inside,second_new_foreign_strip_cleared_capture_routes=clear,
        second_new_foreign_source_route_records=records,second_boundary_retained_MF1021_zero_colonies=list(range(115,120)),
        second_new_foreign_actual_pre_pulse_capture_route_checks=actual_inside+actual_clear,
        second_new_foreign_actual_zero_source_capture_routes=actual_inside,
        second_new_foreign_actual_strip_cleared_capture_routes=actual_clear,
        second_new_foreign_actual_pre_pulse_uncaptured_zero_history_ranks=unused_ranks,
        second_new_foreign_actual_pre_pulse_rank_records=actual_records,
        second_pulse_all_eight_final_selected_MF1021_zero_checks=endpoint_checks,
        second_pulse_final_state_asset_sha256=digest(pulse_asset),
        second_boundary_retained_zero_primaries=zero_primaries,second_boundary_retained_zero_Info_copy_count=25,
        third_retained_MF1021_zero_colonies=list(range(115,120)),third_signal_computed_time=2*p.U+p.T_wf,
        actual_first_left_H1_and_unused_source_zero_proved=True,
        actual_five_emerging_foreign_second_U_and_third_TF_retained_zeros_proved=True,
        first_old_foreign_mailbox_outputs_or_remaining_interior_retained_zeros_proved=False,
        complete_third_signal_or_pulse_proved=False,recovered_right_retained_data_all_proved=False,
        entire_second_boundary_upper_successor_restored=False,general_eroder_higher_map_or_positive_iid_rate_proved=False,
        global_reliability_established=False,numerical_whole_CA_trajectory_used=False,active_G17_modified=False,
        rule_programme_or_constant_change=False,checker_sha256=digest(__file__),
        written_proof_sha256=digest(ROOT/'Report/proofs/SP29_EMERGING_FOREIGN_SOURCES.md'),
        proposal_source_sha256=digest(proposed.__file__),helper_sha256=digest(ROOT/'Report/proofs/check_short_force1024_protected_scratch.py'),
        listing_sha256=digest(listing_path),proposed_candidate_sha256=candidate.digest(),proposed_netlist_sha256=candidate.comp.digest,
        receipt_dependencies_sha256={name:digest(out/name) for name in dependencies},seconds=time.monotonic()-begin)
    (out/'SP29_emerging_foreign_source_certificate.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({key:receipt[key] for key in ('first_suffix_terms','second_new_foreign_capture_route_checks',
        'second_new_foreign_zero_source_capture_routes','second_new_foreign_strip_cleared_capture_routes',
        'third_retained_MF1021_zero_colonies','seconds','global_reliability_established')}),flush=True)


if __name__=='__main__':main()
