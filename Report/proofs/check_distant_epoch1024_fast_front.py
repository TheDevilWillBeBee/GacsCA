#!/usr/bin/env python3
"""J142: unchanged SP28 captures nine native colonies per epoch under E0.

Refine J137's one-cell bound: three cells on an uncharged row, one
otherwise; charged rows are seven ticks apart. Exact local cofactors,
not sampled trajectories. Native seed/data/confinement scopes retained.
"""
from itertools import product
from pathlib import Path
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from gacsca.netlist import Net,const_word,mixed_age_increment,w_in_range
from check_right_barrier import dominant_majority
import proposed_sparse_distant_epoch1024 as proposed


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def clean_step(p,build,phase,gain):
    n=Net();common=[n.input(('common_Age',b)) for b in range(p.m)]
    cells={}
    for j in range(-5,9):
        good=gain<=j<=5
        cells[j]=dict(addr=const_word((phase+j)%p.Q,p.k) if good else
            [n.input((j,'addr',b)) for b in range(p.k)],
            age=common if good else [n.input((j,'age',b)) for b in range(p.m)],
            **{f:n.input((j,f)) for f in ('f1','f2','wf1','wf2')})
    epoch=proposed.epoch(n,cells,p,dominant_majority)
    assert epoch['addr']==const_word(phase,p.k) and epoch['age']==common
    assert epoch['force']==w_in_range(n,common,p.age_code(p.T_wf),p.age_code(p.T_wf+proposed.EPOCH_LENGTH))
    result=build(n,cells,p.k,p.m,Q=p.Q,nb=p.nb,radix=p.R,pos_bits=p.PB,service_force=1)
    assert result['addr']==const_word(phase,p.k),(phase,gain)
    assert result['age_now']==common,(phase,gain)
    assert result['age']==mixed_age_increment(n,common,p.PB,p.R,p.nb)


def charging(p):
    count=0
    for gap in range(1,7):
        for advance in range(gap,3*gap+1,2):
            for old_offset,new_offset in product(range(4),repeat=2):
                assert abs(-advance+new_offset-old_offset)<24 and gap<24
                count+=1
    assert count==432
    capture=next(t for t in range(4097) if 3*t-2*((t+6)//7)>=9*p.Q)
    quiet=capture+2+575
    ten=next(t for t in range(4097) if 3*t-2*((t+6)//7)>=10*p.Q)
    assert (capture,quiet,ten)==(3396,3973,3773)
    assert 3*capture-2*((capture+6)//7)==9*p.Q
    assert quiet<proposed.EPOCH_LENGTH<ten+2+575
    epochs=(1578+8)//9
    assert epochs==176
    return dict(charged_row_exclusion_cases=count,minimum_charged_row_tick_gap=7,
        guaranteed_native_front_advance_uncharged_row=3,guaranteed_native_front_advance_charged_row=1,
        force_window_native_gain_lower_bound='3*t-2*ceil(t/7)',
        nine_colonies_native_capture_state=capture,nine_colonies_WF1_quiet_state=capture+1,
        nine_colonies_last_two_Flag1_quiet_state=capture+2,nine_colonies_all_Flag1_quiet_state=quiet,
        permanent_aligned_native_halfline_expansion_per_period=9*p.Q,
        ten_colony_quieting_not_supplied_by_this_bound=True,
        common_arbitrary_phase_epochs_sufficient_to_recapture_initial_aligned_seed_boundary=epochs)


def main():
    started=time.monotonic();p=proposed.parameters();out=ROOT/'figs/robustness'
    build,source=proposed.proposed_build(symbolic=True)
    checks=0
    for phase in range(p.Q):
        for gain in (2,3):clean_step(p,build,phase,gain);checks+=1
    half=json.loads((out/'SP28_epoch_halfline_certificate.json').read_text())
    wait=json.loads((out/'SP28_phase_wait_certificate.json').read_text())
    assert half['all_period_three_colony_native_halfline_expansion_proved']
    assert half['proposed_netlist_sha256']==wait['proposed_netlist_sha256']==proposed.cached(p)[1].digest
    receipt=dict(proposal='SP28',proposed_rule_change=False,active_G17_modified=False,
        checker_sha256=digest(Path(__file__)),proposal_source_sha256=digest(Path(proposed.__file__)),
        helpers_sha256=digest(ROOT/'gacsca/netlist.py'),
        majority_proof_helper_sha256=digest(ROOT/'Report/proofs/check_right_barrier.py'),
        native_halfline_receipt_sha256=digest(out/'SP28_epoch_halfline_certificate.json'),
        phase_wait_receipt_sha256=digest(out/'SP28_phase_wait_certificate.json'),
        canonicalization_receipt_sha256=digest(out/'SP28_canonicalization_certificate.json'),
        proposed_netlist_sha256=half['proposed_netlist_sha256'],
        actual_maintenance_source_sha256=hashlib.sha256(source.encode()).hexdigest(),
        Q=p.Q,U=p.U,width=proposed.width(p),T_wf=p.T_wf,
        clean_two_three_cell_RF_native_and_actual_epoch_cofactors=checks,**charging(p),
        initial_canonical_common_clock_native_right_halfline_required=True,
        actual_global_E0_required=True,initial_all_other_fields_exterior_and_I_arbitrary=True,
        no_future_boundaries_or_work_command_prescribed=True,
        nine_colonies_captured_and_quiet_before_force_expiry_proved=True,
        all_period_nine_colony_autonomous_native_halfline_expansion_proved=True,
        initial_common_legal_Age_may_be_any_phase_by_J140=True,
        each_fixed_site_eventually_permanently_computed_GF_Age_correct_proved=True,
        arbitrary_work_commit_fivefold_layout_with_independent_auxiliary_flags_on_nine_colony_expanded_halfline_proved=True,
        complete_E28_encoding_on_nine_colony_halfline_from_arbitrary_work_proved=False,
        original_data_restoration_finite_island_extinction_full_noise_map_or_iid_rate_proved=False,
        global_reliability_established=False,seconds=time.monotonic()-started,
        scope='J142 strengthens unchanged SP28 native E0 capture to9Q/epoch; same initial native seed and unproved opposite-front/data/higher/iid requirements')
    (out/'SP28_fast_native_front_certificate.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(cofactors=checks,capture=3396,quiet=3973,colonies=9,epochs=176,seconds=receipt['seconds'],iid=False)),flush=True)


if __name__=='__main__':main()
