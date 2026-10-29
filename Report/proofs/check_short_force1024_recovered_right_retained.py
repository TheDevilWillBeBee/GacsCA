#!/usr/bin/env python3
"""Selected first foreign source zeros and recovered second true MF509.

The written proof supplies physical source/capture/suffix/commit bridges.
No third pulse, general eroder, higher map or positive iid theorem.
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
    probe=json.loads((out/'SP29_recovered_right_source_probe.json').read_text())
    assert probe['checker_sha256']==digest(ROOT/'Report/proofs/probe_short_force1024_recovered_right_sources.py')
    assert probe['proposed_candidate_sha256']==candidate.digest()
    assert [r['terms'] for r in probe['cases']]==[37332,36375]
    assert all(r['late_instructions']==41477 for r in probe['cases'])
    assert [len(r['outputs']) for r in probe['cases']]==[5,50]
    table=proposed.dependency_table(p);byphase={r['address']:r for r in table}
    first_inputs=[];first_issues=[];first_capture_checks=first_rom_keys=0
    for case in probe['cases']:
        field='h1' if case['mode'].startswith('first_four') else 'h2'
        for target in case['outputs']:
            assert target['constant']==0 and target['dependency_variables']==[] and target['field']==field
            row=next(r for r in table if r['field']==field and r['bit']==target['bit'])
            assert row['address']==target['phase']
            physical_phase=(row['address']+512)%p.Q;old=byphase.get(physical_phase)
            assert old is None or old['field'] not in ('addr','info')
            assert physical_phase not in (3,515,509,1021)
            if field=='h1':assert physical_phase in (637,701,765,829,893)
            else:assert any(a<=physical_phase<b for a,b in ((998,1008),(38,48),(102,112),(166,176),(230,240)))
            assert row['offsets']==[-4,-3,-2,-1,1,2,3,4]
            for d in row['offsets']:
                assert all(g*p.Q+abs(d)*(p.Q//8)+1<p.E0 for g in p.gathers_q)
                first_capture_checks+=len(p.gathers_q)
            first_inputs.append(dict(field=field,bit=row['bit'],virtual_phase=row['address'],physical_phase=physical_phase,
                initial_physical_field=None if old is None else old['field'],initial_Info_zero_everywhere=True,
                all_ordinary_direct_and_history_readonly_values_zero=True))
            issues=[r for r in listing if r[4]==row['address'] and r[6]==1];assert len(issues)==1
            issue=issues[0];age=p.E0+issue[1]*p.PL+issue[2]
            assert age>p.E0+280*p.PL and age+2<p.U
            assert np.flatnonzero(((candidate.rom[row['address']]>>2)&3)==1).tolist()==[issue[1]+(issue[3]<<p.logNP)]
            first_rom_keys+=candidate.rom.shape[1]
            first_issues.append(dict(field=field,bit=row['bit'],phase=row['address'],issue_age=age,materialization_age=age+2))
    assert len(first_inputs)==55 and first_capture_checks==1320 and first_rom_keys==225280
    source=proposed.generated_source(p)
    assert source.count('        encoded_primary = n.OR(w_in_range(n, xaddr, p.lo, p.lo+sum(w for _,w in sch)+1), w_eq_const(n, xaddr, p.hi-1))')==1
    assert (p.lo,p.lo+sum(width for field,width in candidate.schema),p.hi-1)==(58,900,965)
    strips=((121*p.Q,121*p.Q+512),(135*p.Q+512,136*p.Q))
    selected=[r for r in table if r['field'] in ('mr','ml') or r['field']=='h2' and r['bit'] in (13,77,141,205,269)]
    assert len(selected)==15
    ranks=[];direct=[];inside=clear=uncaptured=local_clearing=0
    for j in range(128,136):
        for row in selected:
            phase=row['address'];oldphase=(phase+512)%p.Q;old=byphase.get(oldphase)
            field,bit=row['field'],row['bit'];y=j*p.Q+phase
            if field in ('mr','ml'):
                assert old['field']=='h2' and old['bit'] in range(182,192)
                known=lambda d:122<=j+d<=135
                source_kind='first_foreign_H2_tail'
            elif bit in (13,77):
                assert old is None and oldphase in (957,1021)
                known=lambda d:False
                source_kind='first_foreign_unused_commit'
            elif bit==141:
                assert old['field']=='addr' and oldphase==61
                known=lambda d:121<=j+d<=135
                source_kind='first_boundary_zero_physical_GF'
            else:
                assert old['field']=='h1' and oldphase in (125,189)
                known=lambda d:122<=j+1+d<=135
                source_kind='first_foreign_H1_rank13'
            local=j==135 and field=='h2' and bit in (141,205,269)
            if local:
                a,b=strips[1];assert a<=y-39 and y+39<b
                local_clearing+=1
            direct.append(dict(true_colony=j,field=field,bit=bit,physical_phase=phase,
                old_virtual_phase=oldphase,source_kind=source_kind,direct_Info_free=field=='h2' and bit in (141,205,269)))
            old_offsets=[] if old is None else old['offsets']
            for rank in range(len(row['offsets'])):
                if rank>=len(old_offsets):
                    uncaptured+=1;ranks.append(dict(true_colony=j,field=field,bit=bit,rank=rank,
                        actual_old_offset=None,no_capture_and_initial_reset_zero=True));continue
                d=old_offsets[rank];erased=blocked(strips,j,d,phase,p.Q)
                assert known(d) or erased or local,(j,field,bit,rank,d)
                ages=[g*p.Q+abs(d)*(p.Q//8)+1 for g in p.gathers_q]
                assert max(ages)<p.E0<p.courier_ticks()[1]
                clear+=len(ages)*int(erased or local);inside+=len(ages)*int(not (erased or local))
                ranks.append(dict(true_colony=j,field=field,bit=bit,rank=rank,actual_old_offset=d,
                    known_zero_source=known(d),cleared_by_old_strip=erased,local_target_mail_clearing=local,
                    capture_computed_ages=ages))
    assert len(direct)==120 and len(ranks)==140*8
    assert (inside+clear,uncaptured,local_clearing)==(2496,288,3)
    asset=out/'SP29_second_pulse_case_final_states.npz';endpoint=0
    primaries=[j*p.Q+509 for j in range(128,136)]
    with np.load(asset,allow_pickle=False) as arrays:
        for mask in range(8):
            assert all(arrays[f'case{mask}_Info'][y]==0 for y in primaries);endpoint+=len(primaries)
    assert endpoint==64 and all(y-2>=128*p.Q for y in primaries)
    assert all((y%p.Q)==509 for y in primaries)
    target_issue=next(r for r in listing if r[4]==509 and r[6]==1)
    assert p.E0+target_issue[1]*p.PL+target_issue[2]==357736
    true_flags=json.loads((out/'SP29_second_right_boundary_certificate.json').read_text())
    assert true_flags['actual_third_complete_true_frame_Flag1_enclosure_proved']
    unknown_true=true_flags['third_true_MF1021_unspecified_colonies']
    assert len(unknown_true)==11
    unknown=[dict(track='MF1021',colony=j,kind='complete_true_flag') for j in unknown_true]
    unknown.extend([dict(track='MF509',colony=115,kind='partial_frame'),dict(track='MF1021',colony=127,kind='partial_frame')])
    assert len({(r['track'],r['colony']) for r in unknown})==13
    deps=('SP29_recovered_right_source_probe.json','SP29_crossing_history_probe.json','SP29_crossing_history_certificate.json',
        'SP29_second_right_boundary_certificate.json','SP29_emerging_foreign_source_certificate.json',
        'SP29_foreign_cache_erasure_certificate.json','SP29_first_boundary_signal_data_certificate.json',
        'SP29_protected_scratch_certificate.json','SP29_second_signal_enclosure_certificate.json',
        'SP29_next_ghost_signal_certificate.json','SP29_refined_wipe_certificate.json','SP29_symbolic_schedule.json',
        'SP29_front_certificate.json','SP29_encoding_family_certificate.json',
        'SP29_recovered_right_initial_rank_count_failure.json')
    receipt=dict(proposal='SP29',scope='Selected first-foreign H1/H2 source theorems and actual recovered-right MF509 zeros; thirteen-bit third mask enclosure only; no pulse/eroder/iid',
        Q=p.Q,U=p.U,T_wf=p.T_wf,first_suffix_H1_rank13_terms=37332,first_suffix_H2_tail_terms=36375,
        first_suffix_instructions=41477,first_foreign_zero_raw_H1_rank13_bits=[13,77,141,205,269],
        first_foreign_zero_raw_H2_tail_bits=probe['raw_H2_tail_copy_bits'],first_foreign_zero_source_frames=list(range(122,136)),
        first_selected_readonly_source_records=first_inputs,first_selected_readonly_capture_checks=first_capture_checks,
        first_selected_unique_Hold_issue_records=first_issues,first_selected_Hold_ROM_key_checks=first_rom_keys,
        recovered_true_frames=list(range(128,136)),recovered_readonly_family_count=15,
        recovered_direct_family_records=direct,recovered_actual_history_rank_records=ranks,
        recovered_actual_capture_route_checks=inside+clear,recovered_zero_source_capture_routes=inside,
        recovered_old_strip_cleared_capture_routes=clear,recovered_uncaptured_reset_zero_requested_ranks=uncaptured,
        recovered_local_right_strip_history_families=local_clearing,all_eight_endpoint_selected_MF509_zero_checks=endpoint,
        second_pulse_final_state_asset_sha256=digest(asset),second_U_and_third_TF_MF509_zero_colonies=list(range(128,136)),
        retained_zero_Info_copy_count=40,third_signal_computed_time=2*p.U+p.T_wf,
        third_MF509_fixed_one_colonies=list(range(116,128)),third_MF509_unspecified_colonies=[115],
        third_retained_MF1021_interior_zero_colonies=list(range(115,127)),third_retained_MF1021_unspecified_colonies=[127],
        third_complete_signal_unspecified_bit_records=unknown,third_complete_signal_unspecified_bit_count=13,
        unspecified_bits_assumed_independent=False,actual_selected_first_foreign_source_theorems_proved=True,
        actual_recovered_right_retained_zero_source_suffix_commit_bridge_proved=True,
        actual_third_complete_signal_thirteen_bit_enclosure_proved=True,complete_third_signal_values_or_pulse_proved=False,
        general_eroder_higher_map_or_positive_iid_rate_proved=False,global_reliability_established=False,
        numerical_whole_CA_trajectory_used=False,active_G17_modified=False,rule_programme_or_constant_change=False,
        checker_sha256=digest(__file__),written_proof_sha256=digest(ROOT/'Report/proofs/SP29_RECOVERED_RIGHT_RETAINED.md'),
        proposal_source_sha256=digest(proposed.__file__),helper_sha256=digest(ROOT/'Report/proofs/check_short_force1024_protected_scratch.py'),
        listing_sha256=digest(listing_path),proposed_candidate_sha256=candidate.digest(),proposed_netlist_sha256=candidate.comp.digest,
        receipt_dependencies_sha256={name:digest(out/name) for name in deps},seconds=time.monotonic()-begin)
    (out/'SP29_recovered_right_retained_certificate.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({key:receipt[key] for key in ('first_selected_readonly_capture_checks','recovered_actual_capture_route_checks',
        'recovered_zero_source_capture_routes','recovered_old_strip_cleared_capture_routes','third_complete_signal_unspecified_bit_count',
        'seconds','global_reliability_established')}),flush=True)


if __name__=='__main__':main()
