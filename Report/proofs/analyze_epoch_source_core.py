#!/usr/bin/env python3
"""Independently read SP18's retained finite source-core observations.

Snapshots and overwrite geometry are verified; the experiment is measured
only and has driven boundaries. No universal recovery inference is made.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import numpy as np
from gacsca import machine,codec
import proposed_sparse_epoch448 as proposed


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--stem',default='SP18_epoch_source_core')
    args=parser.parse_args()
    assert args.stem in ('SP18_epoch_source_core','SP18_epoch_GF_Age_source_core','SP18_epoch_frozen_source_core')
    out=ROOT/'figs/robustness'
    candidate=proposed.load_artifact()
    p=candidate.p
    physical_path=out/(args.stem+'_physical.json')
    physical=json.loads(physical_path.read_text())
    periods=physical['requested_periods']
    assert physical['completed_periods']==len(physical['checks'])==periods
    assert physical['proposed_candidate_sha256']==candidate.digest()
    assert physical['proposed_netlist_sha256']==candidate.comp.digest
    asset=out/(args.stem+'_tracking.npz')
    assert physical['tracking_asset_sha256']==digest(asset)
    input_asset=out/(args.stem+'_inputs.npz')
    assert physical['input_asset_sha256']==digest(input_asset)
    gf_rows=[candidate.row[f,b] for f,w in (('addr',p.k),('age',p.m)) for b in range(w)]
    flags=[candidate.row[f,0] for f in ('f1','f2','wf1','wf2')]
    pulse_map={r['tick']:r for r in physical['pulses']}
    checkpoint_map={r['tick']:r for r in physical['checks']}
    verified_pulses=verified_checkpoints=verified_overwrites=0
    with np.load(asset,allow_pickle=False) as saved:
        ticks=saved['overwrite_ticks']
        sites=saved['overwrite_sites']
        values=saved['overwrite_values']
        assert len(ticks)==len(sites)==len(values)==17
        assert ticks.tolist()==[physical['core_tau']+s for s in list(range(16))+[38]]
        assert sum(np.count_nonzero(s>=0) for s in sites)==257
        for index,s in enumerate(sites):
            wanted=np.arange(1,17) if index<16 else np.array([16])
            assert np.array_equal(s[s>=0],wanted)
            assert not values[index,:,len(wanted):].any()
            if args.stem=='SP18_epoch_frozen_source_core':
                expected=np.zeros((candidate.W,len(wanted)),dtype=bool)
                candidate.set_field(expected,'addr',(wanted-6)%p.Q)
                candidate.set_field(expected,'age',p.age_code(p.T_wf))
                candidate.set_field(expected,'f1',1)
                candidate.set_field(expected,'wf1',1)
                planted=(wanted>=7)&(wanted<=11)
                candidate.set_field(expected,'wf2',planted.astype(np.int64))
                candidate.set_field(expected,'packet_valid',planted.astype(np.int64))
                candidate.set_field(expected,'packet_tag',np.where(planted,wanted-7,0))
                assert np.array_equal(values[index,:,:len(wanted)],expected)
        boundaries=[]
        control_comparisons=[]
        for tick,packed in zip(saved['snapshot_ticks'],saved['first_eight_colonies_packed']):
            tick=int(tick)
            raw=machine.CKernel.unpack(packed[3],8*p.Q)
            reference=machine.CKernel.unpack(packed[0],8*p.Q)
            control=machine.CKernel.unpack(packed[2],8*p.Q)
            control_comparisons.append(dict(tick=tick,period=tick//p.U,clock=tick%p.U,
                first_colony_full_word_differing_bits=int(np.count_nonzero(raw[:,:p.Q]!=control[:,:p.Q])),
                first_eight_full_word_differing_bits=int(np.count_nonzero(raw!=control)),
                first_eight_GF_Age_differing_bits=int(np.count_nonzero(raw[gf_rows]!=control[gf_rows]))))
            if tick in pulse_map:
                observed=pulse_map[tick]
                fields={f:candidate.field(raw,f) for f in ('addr','age','f1','f2','wf2',
                    'packet_valid','packet_tag','packet_count','service_valid','service_position','service_count')}
                live=np.flatnonzero(fields['packet_valid'] & fields['wf2'] & (fields['packet_tag']<5))
                coded=np.flatnonzero(fields['service_valid'])
                row=dict(tick=tick,period=tick//p.U,clock=tick%p.U,
                    canonical_GF_first_eight=[int(np.count_nonzero(a==np.arange(p.Q))) for a in np.split(fields['addr'],8)],
                    reference_Age_first_eight=[int(np.count_nonzero(a==b)) for a,b in zip(np.split(fields['age'],8),np.split(candidate.field(reference,'age'),8))],
                    F1_first_eight=[int(a.sum()) for a in np.split(fields['f1'],8)],
                    F2_first_eight=[int(a.sum()) for a in np.split(fields['f2'],8)],
                    packet_sites=live.tolist(),packet_tags=fields['packet_tag'][live].tolist(),packet_counts=fields['packet_count'][live].tolist(),
                    packet_origins=(live-fields['packet_tag'][live].astype(np.int64)-1).tolist(),
                    code_count=len(coded),code_origins=np.unique(coded-fields['service_position'][coded].astype(np.int64)).tolist(),
                    code_counter_range=[int(fields['service_count'][coded].min()),int(fields['service_count'][coded].max())] if len(coded) else None)
                assert row==observed,(tick,'pulse mismatch')
                verified_pulses+=1
            if tick in checkpoint_map:
                observed=checkpoint_map[tick]['rings'][1]
                gf_bad=np.any(raw[gf_rows]!=reference[gf_rows],axis=0)
                full_bad=np.any(raw!=reference,axis=0)
                assert observed['geometry_first_eight_colonies']==[int(a.sum()) for a in np.split(gf_bad,8)]
                assert observed['full_word_first_eight_colonies']==[int(a.sum()) for a in np.split(full_bad,8)]
                boundaries.append(dict(period=tick//p.U,first_eight_GF_sites=int(gf_bad.sum()),
                    first_eight_full_word_sites=int(full_bad.sum())))
                verified_checkpoints+=1
            matches=np.flatnonzero(ticks==tick)
            if len(matches) and args.stem!='SP18_epoch_frozen_source_core':
                index=int(matches[0])
                reference_shifted=machine.CKernel.unpack(packed[1],8*p.Q)
                present=sites[index][sites[index]>=0]
                assert np.array_equal(values[index,:,:len(present)],reference_shifted[:,present])
                verified_overwrites+=1
        assert verified_pulses==len(pulse_map)==13*periods
        assert verified_checkpoints==periods
        final=saved['final_packed']
        final_equal=bool(np.array_equal(final[3],final[0]))
        final_control_equal=bool(np.array_equal(final[2],final[0]))
        final_core_equals_control=bool(np.array_equal(final[3],final[2]))
        last_gf=saved['every_tick_last_rows'][3].tolist()
        last_whole=saved['every_tick_last_any'][3].tolist()
        assert last_gf[:8]==physical['final_GF_last_difference_first_eight']
        assert last_whole[:8]==physical['final_full_word_last_difference_first_eight']
    first_pulses=[r for r in physical['pulses'] if r['period']==0]
    def recovered(key):
        return next((r['period'] for r in physical['checks'] if not r['rings'][1][key]),None)
    last_force=int(ticks[-1])
    result=dict(proposal='SP18',proposed_rule_change=False,active_G17_modified=False,
        checker_sha256=digest(Path(__file__)),proposal_source_sha256=digest(Path(proposed.__file__)),
        proposed_candidate_sha256=candidate.digest(),proposed_netlist_sha256=candidate.comp.digest,
        physical_receipt_sha256=digest(physical_path),tracking_asset_sha256=digest(asset),
        input_asset_sha256=digest(input_asset),experiment_stem=args.stem,
        computed_period_checkpoints=periods,verified_first_eight_checkpoint_snapshots=verified_checkpoints,
        verified_first_eight_pulse_snapshots=verified_pulses,
        overwritten_batches_with_direct_retained_reference_comparison=verified_overwrites,
        overwrite_batches=17,overwritten_space_time_points=257,
        first_epoch_pulses=first_pulses,boundary_first_eight_observations=boundaries,
        source_core_vs_boundary_control_retained_snapshots=control_comparisons,
        physical_GF_first_observed_recovered_period=recovered('geometry_sites'),
        full_physical_word_first_observed_recovered_period=recovered('full_word_sites'),
        GF_last_differing_computed_tick_by_colony=last_gf,
        full_word_last_differing_computed_tick_by_colony=last_whole,
        first_colony_GF_matches_every_retained_computed_tick_from=last_gf[0]+1,
        first_colony_full_word_matches_every_retained_computed_tick_from=last_whole[0]+1,
        first_colony_GF_clock_of_last_difference=last_gf[0]%p.U if last_gf[0]>=0 else None,
        first_colony_GF_updates_to_match_after_last_overwrite=last_gf[0]+1-last_force,
        final_full_physical_state_matches_reference=final_equal,
        final_boundary_control_matches_reference=final_control_equal,
        final_source_core_matches_boundary_control=final_core_equals_control,
        boundary_control_exact_at_every_checkpoint=all(not r['rings'][0]['full_word_sites'] for r in physical['checks']),
        changed_boundary_condition=True,continuing_E0=False,
        initial_pristine_infinite_hierarchy=False,infinite_line_equivalence_established=False,
        general_GF_Age_error_values_or_uniform_recovery_bound_established=False,
        upper_error_map_established=False,iid_threshold_established=False,global_reliability_established=False,
        scope='finite own-programme driven SP18 source-core observations, measured only; no universal repair or infinite-hierarchy theorem')
    (out/(args.stem+'_analysis.json')).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('computed_period_checkpoints',
        'physical_GF_first_observed_recovered_period','full_physical_word_first_observed_recovered_period',
        'first_colony_GF_clock_of_last_difference','first_colony_GF_updates_to_match_after_last_overwrite',
        'final_full_physical_state_matches_reference')}),flush=True)


if __name__=='__main__':
    main()
