#!/usr/bin/env python3
"""Physical erasure-only cache lift for six old second foreign frames.

No complete third mask/pulse or iid result. The written proof specifies
why a potentially damaged cache is a prefix value times a survival bit.
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
    listing_path=out/'SP29_program_listing.json';listing=json.loads(listing_path.read_text());start=p.E0+280*p.PL
    probe=json.loads((out/'SP29_foreign_scratch_alias_probe.json').read_text())
    assert probe['checker_sha256']==digest(ROOT/'Report/proofs/probe_short_force1024_foreign_scratch_aliases.py')
    assert probe['proposed_candidate_sha256']==candidate.digest()
    assert probe['seed_count']==47
    assert probe['fresh_GF0_rank13_H2zero_output_copies']=={str(bit):0 for bit in (13,77,141,205,269)}
    assert probe['seed_slots_with_opposite_pulse_issues']==probe['opposite_pulse_issue_count']==0
    assert probe['seed_slots_with_ordinary_post_TF_issues']==0
    assert all(row['output_constant']==0 for row in probe['cases'])
    assert all(not row['dependency_variables'] for row in probe['cases'])
    records=[];keys=0
    for seed in probe['scratch_alias_records']:
        cell,index=seed['cell'],seed['index'];pair=[]
        for phase in (cell,(cell+512)%p.Q):
            words=candidate.rom[phase]
            actual=np.flatnonzero((((words>>2)&3)==2)&(((words>>(4+2*p.SB))&((1<<p.DB)-1))==index)).tolist()
            expected=sorted(row[1]+(row[3]<<p.logNP) for row in listing if row[4]==phase and row[6]==2 and row[9]==index)
            assert actual==expected
            relevant=[row for row in listing if row[4]==phase and row[6]==2 and row[9]==index]
            deadline=start if phase==cell else p.T_wf+6144
            assert all(not (p.T_wf-2<=p.E0+r[1]*p.PL+r[2]<deadline) for r in relevant)
            pair.append(dict(phase=phase,raw_ROM_key_checks=len(words),no_scratch_issue_before_age=deadline,
                             all_scratch_issue_ages=[p.E0+r[1]*p.PL+r[2] for r in relevant]))
            keys+=len(words)
        prior=[row for row in listing if row[4]==cell and row[6]==2 and row[9]==index and p.E0+row[1]*p.PL+row[2]<p.T_wf]
        assert prior
        last=max(p.E0+r[1]*p.PL+r[2] for r in prior)
        assert last+2<p.T_wf
        records.append(dict(cell=cell,index=index,last_correct_prefix_materialization_age=last+2,two_phase_issue_records=pair))
    assert keys==385024
    table=proposed.dependency_table(p);strips=((121*p.Q,121*p.Q+512),(135*p.Q+512,136*p.Q))
    copies=(13,77,141,205,269);source_records=[];gf_direct=h2_direct=gf_paths=h2_paths=0;cleared=0
    for h in range(122,128):
        for row in table:
            if row['field']!='addr' and not (row['field']=='h2' and row['bit'] in copies):continue
            phase=(row['address']+512)%p.Q;j=h-1+int(row['address']>=512)
            if row['field']=='addr':assert j in range(121,136);gf_direct+=1
            else:assert h in range(122,136);h2_direct+=1
            for d in row['offsets']:
                erased=blocked(strips,j,d,phase,p.Q)
                known=121<=j+d<=135 if row['field']=='addr' else 122<=h+d<=135
                assert known or erased,(h,row['field'],row['bit'],d,j,phase)
                for gather in p.gathers_q:
                    assert gather*p.Q+abs(d)*(p.Q//8)+1<p.E0
                    if row['field']=='addr':gf_paths+=1
                    else:h2_paths+=1
                    cleared+=int(erased)
                source_records.append(dict(foreign_frame=h,field=row['field'],bit=row['bit'],offset=d,
                    physical_true_colony=j,physical_true_phase=phase,known_zero_source=known,cleared_by_old_strip=erased))
    assert (gf_direct,h2_direct,gf_paths,h2_paths)==(60,30,11520,720)
    zero_primaries=[j*p.Q+1021 for j in range(121,127)]
    asset=out/'SP29_second_pulse_case_final_states.npz';endpoint_checks=0
    with np.load(asset,allow_pickle=False) as arrays:
        for mask in range(8):
            assert all(arrays[f'case{mask}_Info'][y]==0 for y in zero_primaries)
            endpoint_checks+=len(zero_primaries)
    assert all(118272<=y-2 and y+2<131072 for y in zero_primaries)
    dependencies=('SP29_foreign_scratch_alias_probe.json','SP29_second_right_boundary_certificate.json',
        'SP29_protected_scratch_certificate.json','SP29_first_boundary_signal_data_certificate.json',
        'SP29_second_signal_enclosure_certificate.json','SP29_next_ghost_signal_certificate.json',
        'SP29_refined_wipe_certificate.json','SP29_symbolic_schedule.json','SP29_front_certificate.json',
        'SP29_encoding_family_certificate.json')
    receipt=dict(proposal='SP29',scope='Actual six old second-foreign retained zeros by universal prefix-cache erasure composition; original clock0 error/no later errors; no full third pulse or iid',
        Q=p.Q,U=p.U,T_wf=p.T_wf,second_old_foreign_frame_colonies=list(range(122,128)),protected_prefix_scratch_seed_count=47,
        two_phase_scratch_issue_ROM_key_checks=keys,two_phase_scratch_issue_records=records,
        actual_cache_can_change_only_by_vote_or_erase_proved=True,arbitrary_independent_seed_survival_bit_suffix_identity_proved=True,
        native_GF_zero_direct_source_checks=gf_direct,native_GF_zero_capture_route_checks=gf_paths,
        rank13_H2_zero_direct_source_checks=h2_direct,rank13_H2_zero_capture_route_checks=h2_paths,
        capture_routes_meeting_old_Flag1_strip=cleared,actual_GF_and_H2_zero_source_route_records=source_records,
        all_eight_second_pulse_final_selected_MF1021_zero_checks=endpoint_checks,second_pulse_final_state_asset_sha256=digest(asset),
        second_U_retained_MF1021_zero_colonies=list(range(121,127)),third_TF_retained_MF1021_zero_colonies=list(range(121,127)),
        retained_zero_primary_count=6,retained_zero_Info_copy_count=30,third_signal_computed_time=2*p.U+p.T_wf,
        actual_six_old_foreign_second_U_and_third_TF_retained_zeros_proved=True,
        partial_emerging_frame121_or_recovered_right_retained_data_proved=False,complete_third_signal_or_pulse_proved=False,
        entire_second_boundary_upper_successor_restored=False,general_eroder_higher_map_or_positive_iid_rate_proved=False,
        global_reliability_established=False,numerical_whole_CA_trajectory_used=False,active_G17_modified=False,
        rule_programme_or_constant_change=False,checker_sha256=digest(__file__),
        written_proof_sha256=digest(ROOT/'Report/proofs/SP29_FOREIGN_CACHE_ERASURES.md'),proposal_source_sha256=digest(proposed.__file__),
        helper_sha256=digest(ROOT/'Report/proofs/check_short_force1024_protected_scratch.py'),listing_sha256=digest(listing_path),
        proposed_candidate_sha256=candidate.digest(),proposed_netlist_sha256=candidate.comp.digest,
        receipt_dependencies_sha256={name:digest(out/name) for name in dependencies},seconds=time.monotonic()-begin)
    (out/'SP29_foreign_cache_erasure_certificate.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({key:receipt[key] for key in ('two_phase_scratch_issue_ROM_key_checks','native_GF_zero_capture_route_checks',
        'rank13_H2_zero_capture_route_checks','third_TF_retained_MF1021_zero_colonies','seconds','global_reliability_established')}),flush=True)


if __name__=='__main__':main()
