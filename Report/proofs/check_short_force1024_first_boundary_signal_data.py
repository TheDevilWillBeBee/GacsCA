#!/usr/bin/env python3
"""Exact late-suffix and source certificates for retained first-boundary data.

Physical lift is proved in SP29_FIRST_BOUNDARY_SIGNAL_DATA.md. This neither
samples prior work for the zero identity nor claims a complete second pulse.
"""
from pathlib import Path
import hashlib
import json
import sys
import time
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import proposed_sparse_short_force1024 as proposed
import probe_short_force1024_late_suffix as suffix


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    begin=time.monotonic();out=ROOT/'figs/robustness'
    p=proposed.parameters();candidate=proposed.load_artifact()
    listing_path=out/'SP29_program_listing.json';listing=json.loads(listing_path.read_text())
    start_age=p.E0+280*p.PL
    assert start_age==285824 and p.T_wf+6144==284545
    assert start_age-(p.T_wf+6144)==1279
    result=suffix.run(p,candidate,listing,'four_h2_copies_and_mail_zero',start_age)
    assert result['h2_77_suffix_proved_constant_zero']
    assert result['explicit_arbitrary_seed_h2_77_one_assignment'] is None
    assert result['late_instructions']==41477
    selected=result['selected_Hold_outputs']['h2:77']
    assert selected['cell']==509 and selected['term']==selected['proved_constant']==0
    assert selected['issue']==dict(sequence=129986,page=357,tick=456,age=357736)
    output=out/'SP29_first_boundary_signal_suffix.json'
    output.write_text(json.dumps(result,indent=2)+'\n')

    table=proposed.dependency_table(p);byphase={row['address']:(row['field'],row['bit']) for row in table}
    zero_rows=[row for row in table if row['field'] in ('mr','ml') or
               row['field']=='h2' and row['bit'] in (13,77,205,269)]
    assert len(zero_rows)==14
    geometry=[];gather_routes=0
    special={3,509,515,1021}
    for shift in (0,512):
        for row in zero_rows:
            phase=(row['address']+shift)%p.Q
            field=byphase.get(phase)
            assert field is None or field[0] in ('h1','h2','mr','ml')
            track_exception=phase in (509,1021)
            assert track_exception or phase not in special
            source_ages=[]
            for off in row['offsets']:
                for gather in p.gathers_q:
                    age=gather*p.Q+abs(off)*(p.Q//8)+1
                    assert age<p.E0<p.T_wf and abs(off)<=37
                    source_ages.append(age);gather_routes+=1
            geometry.append(dict(frame_shift=shift,virtual_field=row['field'],virtual_bit=row['bit'],
                virtual_phase=row['address'],physical_phase=phase,
                original_true_field=field,initial_logical_Info_zero=True,
                direct_Info_requires_corrected_first_pulse_track=track_exception,
                readonly_history_rank_count=len(row['offsets']),latest_capture_age=max(source_ages,default=None)))
    assert sorted(row['address'] for row in zero_rows if row['field']=='h2')==[445,509,637,701]
    assert [((row['address']+512)%p.Q) for row in zero_rows if row['field']=='h2']==[957,1021,125,189]
    hold_rows=[row for row in listing if row[4]==509 and row[6]==1]
    assert len(hold_rows)==1 and hold_rows[0][0]==129986
    assert not [row for row in listing if row[4]==1021 and row[6]==1]
    key_checks=0
    for phase,expected in ((509,[357+(hold_rows[0][3]<<p.logNP)]),(1021,[])):
        found=np.flatnonzero(((candidate.rom[phase]>>2)&3)==1).tolist()
        assert found==expected,(phase,found,expected)
        key_checks+=candidate.rom.shape[1]
    corrected=json.loads((out/'SP29_refined_wipe_certificate.json').read_text())
    assert corrected['all_three_corrected_pulse_histories_certified']
    assert corrected['historical_J169_first_endpoint_premise_restored']
    first=json.loads((out/'SP29_first_signal_certificate.json').read_text())
    next_signal=json.loads((out/'SP29_next_ghost_signal_certificate.json').read_text())
    assert first['exact_first_signal_physical_history_proved']
    assert next_signal['actual_next_complete_foreign_GF_zero_and_Flag1_signal_proved']
    assert candidate.digest()==first['proposed_candidate_sha256']==next_signal['proposed_candidate_sha256']
    with np.load(out/'SP29_refined_wipe_final_states.npz',allow_pickle=False) as stored:
        info=stored['duration2048_mode1_Info']
        assert (np.flatnonzero(info[509::p.Q])).tolist()==list(range(128,136))
        assert (np.flatnonzero(info[1021::p.Q])).tolist()==[144,145,146]
        assert np.all(info[509::p.Q][:121]==0) and np.all(info[509::p.Q][136:]==0)
        assert np.all(info[1021::p.Q][121:135]==0)
    # Complete-frame relative front footprints and endpoint arithmetic.
    assert (p.lo-p.H,p.hi-1+p.H)==(38,985)
    assert (38-37,985+37)==(1,1022)
    a,b=124416,139264
    assert (a,b)==(122*p.Q-512,136*p.Q)
    targets=[]
    for h in range(122,136):
        origin=h*p.Q-512;y=origin+509
        assert a<=origin and origin+p.Q<=b-512
        assert a<=y-2 and y+2<b
        assert y==(h-1)*p.Q+1021 and (y+512)%p.Q==509
        targets.append(dict(foreign_frame=h,origin=origin,primary=y,true_colony=h-1))
    for j in (120,136):
        origin=j*p.Q;y=origin+509
        assert origin+p.Q<=a-512 or origin>=b
        assert y%p.Q==509
    dependencies=('SP29_refined_wipe_certificate.json','SP29_first_signal_certificate.json',
        'SP29_next_ghost_signal_certificate.json','SP29_symbolic_schedule.json','SP29_front_certificate.json',
        'SP29_encoded_certificate.json','SP29_encoding_family_certificate.json','SP29_program_build.json',
        'SP29_late_suffix_probe.json','SP29_late_h2_suffix_page280_probe.json')
    receipt=dict(proposal='SP29',scope='J171 retained first-boundary signal data and second MF509 track except one partial-frame bit; no complete second signal or pulse',
        Q=p.Q,U=p.U,T_wf=p.T_wf,first_pulse_endpoint=284545,suffix_start_age=start_age,suffix_start_page=280,
        suffix_late_instructions=41477,suffix_symbolic_terms=result['terms'],
        suffix_initial_register_and_scratch_seeds_arbitrary=True,Match_I_word_arbitrary=True,
        suffix_all_other_readonly_inputs_free=True,suffix_h2_77_constant_zero_proved=True,
        zero_source_families=[dict(field=row['field'],bit=row['bit'],phase=row['address']) for row in zero_rows],
        zero_source_geometry=geometry,zero_source_gather_coordinate_checks=gather_routes,
        raw_two_phase_Hold_key_checks=key_checks,unique_h2_77_Hold_issue=selected['issue'],Hold_materialization_age=357738,
        complete_frame_front_center_interval=[38,985],complete_frame_radius37_footprint=[1,1022],
        first_boundary_MF509_zero_true_colony_ranges=[dict(upper=120),dict(lower=136)],
        first_boundary_MF1021_zero_colonies=list(range(121,135)),
        first_boundary_MF1021_zero_primary_records=targets,
        next_MF509_one_colonies=list(range(122,136)),next_MF509_unspecified_colonies=[121],
        next_MF509_zero_true_colony_ranges=[dict(upper=120),dict(lower=136)],
        next_MF1021_interior_zero_colonies=list(range(121,135)),
        next_MF1021_partial_right_colony_unspecified=135,next_true_MF1021_track_proved=False,
        every_stated_boundary_Info_copy_zero_proved=True,
        original_initial_upper_Info_payloads_arbitrary=True,physical_suffix_lift_proved_for_complete_quiet_frames=True,
        earlier_register_scratch_computation_correctness_required=False,
        complete_first_boundary_upper_Age_or_other_data_restoration_proved=False,
        full_second_signal_or_second_shrinking_pulse_proved=False,
        general_eroder_higher_map_or_iid_rate_proved=False,global_reliability_established=False,
        numerical_whole_CA_trajectory_used=False,rule_programme_or_constant_change=False,active_G17_modified=False,
        checker_sha256=digest(__file__),written_proof_sha256=digest(Path(__file__).with_name('SP29_FIRST_BOUNDARY_SIGNAL_DATA.md')),
        suffix_source_sha256=digest(suffix.__file__),algebra_source_sha256=digest(ROOT/'Report/proofs/check_g17_schedule.py'),
        proposal_source_sha256=digest(proposed.__file__),proposed_candidate_sha256=candidate.digest(),
        proposed_netlist_sha256=candidate.comp.digest,listing_sha256=digest(listing_path),
        suffix_asset_sha256=digest(output),corrected_pulse_state_asset_sha256=digest(out/'SP29_refined_wipe_final_states.npz'),
        receipt_dependencies_sha256={name:digest(out/name) for name in dependencies},seconds=time.monotonic()-begin)
    (out/'SP29_first_boundary_signal_data_certificate.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({key:receipt[key] for key in ('suffix_late_instructions','zero_source_gather_coordinate_checks',
        'first_boundary_MF1021_zero_colonies','next_MF509_one_colonies','next_MF509_unspecified_colonies','seconds',
        'global_reliability_established')}),flush=True)


if __name__=='__main__':main()
