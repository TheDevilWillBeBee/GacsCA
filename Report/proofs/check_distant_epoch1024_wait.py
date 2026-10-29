#!/usr/bin/env python3
"""J140: SP28 common-right-clock seed may start at any legal phase.

Both native vote directions are correct inside a canonical half-line,
apart from a three-site boundary/charged-row retreat. Exact cofactors
and E0 charging remove the initial TF phase premise of J137. A native
half-line seed, confinement on the opposite side and data repair remain
separate: no finite-island eroder or iid theorem is claimed here.
"""
from itertools import combinations,product
from pathlib import Path
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from gacsca.netlist import Net,const_word,mixed_age_increment
import proposed_sparse_distant_epoch1024 as proposed


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def both_votes(p,build,phase,faults):
    n=Net();common=[n.input(('common_Age',b)) for b in range(p.m)]
    cells={}
    for j in range(-5,9):
        good=-5<=j<=5 and j not in faults
        cells[j]=dict(addr=const_word((phase+j)%p.Q,p.k) if good else
            [n.input((j,'addr',b)) for b in range(p.k)],
            age=common if good else [n.input((j,'age',b)) for b in range(p.m)],
            **{f:n.input((j,f)) for f in ('f1','f2','wf1','wf2')})
    result=build(n,cells,p.k,p.m,Q=p.Q,nb=p.nb,radix=p.R,pos_bits=p.PB,
                 service_force=n.input(('arbitrary_service_force',)))
    assert result['addr']==const_word(phase,p.k),(phase,faults)
    assert result['age_now']==common,(phase,faults)
    assert result['age']==mixed_age_increment(n,common,p.PB,p.R,p.nb)


def clean_boundary(p,build,phase,relative,faults):
    n=Net();common=[n.input(('common_Age',b)) for b in range(p.m)]
    cells={}
    for j in range(-5,9):
        good=(j<0 and relative+j>=0) or (1<=j<=5 and j not in faults)
        cells[j]=dict(addr=const_word((phase+j)%p.Q,p.k) if good else
            [n.input((j,'addr',b)) for b in range(p.k)],
            age=common if good else [n.input((j,'age',b)) for b in range(p.m)],
            **{f:n.input((j,f)) for f in ('f1','f2','wf1','wf2')})
    result=build(n,cells,p.k,p.m,Q=p.Q,nb=p.nb,radix=p.R,pos_bits=p.PB,
                 service_force=n.input(('arbitrary_service_force',)))
    assert result['addr']==const_word(phase,p.k),(phase,relative,faults)
    assert result['age_now']==common,(phase,relative,faults)
    assert result['age']==mixed_age_increment(n,common,p.PB,p.R,p.nb)


def charge_arithmetic(p):
    exclusions=0
    for gap in range(1,5):
        for advance in range(3*gap,5*gap+1,2):
            for old_offset,new_offset in product(range(4),repeat=2):
                assert abs(advance+new_offset-old_offset)<24 and gap<24
                exclusions+=1
    assert exclusions==224
    waits={}
    for age in range(p.U):
        wait=(p.T_wf-age)%p.U
        retreat=3*wait+2*((wait+4)//5)
        aligned=(retreat+p.Q-1)//p.Q*p.Q
        waits[wait]=(retreat,aligned)
    assert set(waits)==set(range(p.U))
    maximum=max(x[0] for x in waits.values())
    aligned_max=max(x[1] for x in waits.values())
    assert maximum==1615459 and aligned_max==1615872==1578*p.Q
    assert aligned_max<2*p.Q*p.Q
    periods=aligned_max//(3*p.Q)
    assert periods==526
    return dict(charged_row_exclusion_cases=exclusions,minimum_charged_row_tick_gap=5,
        right_native_boundary_retreat_per_uncharged_update=3,
        right_native_boundary_retreat_per_charged_update=5,
        waiting_native_retreat_bound='3*w+2*ceil(w/5)',
        legal_starting_phase_wait_cases=p.U,maximum_phase_wait=p.U-1,
        maximum_unaligned_wait_retreat=maximum,maximum_aligned_seed_retreat=aligned_max,
        aligned_retreat_upper_bound_colonies=1578,
        epochs_sufficient_to_recapture_initial_aligned_seed_boundary=periods)


def main():
    started=time.monotonic();p=proposed.parameters();out=ROOT/'figs/robustness'
    build,source=proposed.proposed_build(symbolic=True)
    interior=boundary=0
    for phase in range(p.Q):
        for faults in combinations(range(-5,6),2):
            both_votes(p,build,phase,faults);interior+=1
        for relative in (3,4):
            for faults in combinations(range(1,6),2):
                clean_boundary(p,build,phase,relative,faults);boundary+=1
        if phase%256==255:
            print(json.dumps(dict(through_phase=phase,interior=interior,boundary=boundary)),flush=True)
    prior=json.loads((out/'SP28_epoch_halfline_certificate.json').read_text())
    assert prior['all_period_three_colony_native_halfline_expansion_proved']
    assert prior['proposed_netlist_sha256']==proposed.cached(p)[1].digest
    receipt=dict(proposal='SP28',proposed_rule_change=False,active_G17_modified=False,
        checker_sha256=digest(Path(__file__)),proposal_source_sha256=digest(Path(proposed.__file__)),
        helpers_sha256=digest(ROOT/'gacsca/netlist.py'),
        native_halfline_receipt_sha256=digest(out/'SP28_epoch_halfline_certificate.json'),
        canonicalization_receipt_sha256=digest(out/'SP28_canonicalization_certificate.json'),
        majority_proof_helper_sha256=digest(ROOT/'Report/proofs/check_right_barrier.py'),
        proposed_netlist_sha256=prior['proposed_netlist_sha256'],
        actual_maintenance_source_sha256=hashlib.sha256(source.encode()).hexdigest(),
        Q=p.Q,U=p.U,width=proposed.width(p),T_wf=p.T_wf,
        both_vote_directions_two_fault_arbitrary_flags_cofactors=interior,
        clean_three_four_site_boundary_free_exterior_self_flags_cofactors=boundary,
        **charge_arithmetic(p),
        initial_canonical_GF_and_common_legal_Age_halfline_required=True,
        initial_Age_may_be_any_legal_phase=True,initial_all_other_state_and_I_arbitrary=True,
        actual_global_E0_required=True,no_future_boundaries_or_work_command_prescribed=True,
        eventually_expanding_native_halfline_proved=True,
        each_fixed_site_eventually_permanently_computed_GF_Age_correct_proved=True,
        correctly_timed_right_native_seed_from_arbitrary_common_phase_proved=True,
        seed_from_arbitrary_right_GF_or_noncommon_Age_proved=False,
        finite_island_extinction_or_opposite_front_confinement_proved=False,
        original_data_restoration_or_full_noise_map_or_iid_rate_proved=False,
        global_reliability_established=False,seconds=time.monotonic()-started,
        scope='J140 removes TF phase premise given a canonical/common-legal-clock native right halfline and E0; pointwise native repair, not finite-island/data/iid reliability')
    (out/'SP28_phase_wait_certificate.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(interior=interior,boundary=boundary,wait_retreat=receipt['maximum_aligned_seed_retreat'],
        epochs=receipt['epochs_sufficient_to_recapture_initial_aligned_seed_boundary'],seconds=receipt['seconds'],iid=False)),flush=True)


if __name__=='__main__':main()
