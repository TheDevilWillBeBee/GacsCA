#!/usr/bin/env python3
"""SP28: epoch-seeded autonomous native half-line expansion, not reliability.

Exact local cofactors and source-free quiet-suffix charging arithmetic.
The induction with these interfaces is ROBUSTNESS J137. No trajectories
are sampled; arbitrary data/packet fields and I are left unconstrained.
Initial aligned native half-line/common TF clock and actual global E0
remain hypotheses. No finite-island confinement or data repair theorem.
"""
from itertools import combinations,product
from pathlib import Path
import hashlib,json,sys,time
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from gacsca.netlist import Net,Compiled,const_word,mixed_age_increment
from check_right_barrier import dominant_majority,check_dominance_primitive
from check_buffered448_period_barrier import suffix_case,PAIRS
import proposed_sparse_distant_epoch1024 as proposed


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def two_good_blocks():
    # The general-width proof is word equality: a wrong accepted word
    # cannot equal either of the two valid good blocks, leaving only two
    # votes, below the literal three-vote threshold. A width2 truth table
    # additionally pins the implementation with independent valid bits.
    checks=0
    for good in combinations(range(4),2):
        other=[i for i in range(4) if i not in good]
        for common,default,bad0,bad1,valid in product(range(4),repeat=5):
            n=Net();values=[None]*4
            for i in good:values[i]=(const_word(common,2),1)
            for k,i in enumerate(other):
                values[i]=(const_word((bad0,bad1)[k],2),(valid>>k)&1)
            result,exists=proposed.local.block_quorum(n,values,const_word(default,2))
            value=sum(bit<<b for b,bit in enumerate(result))
            assert exists in (0,1) and value==(common if exists else default)
            checks+=1
    assert checks==6144
    return checks


def forced_right(p,build,phase,faults):
    n=Net();common=[n.input(('common_Age',b)) for b in range(p.m)]
    cells={}
    for j in range(-5,9):
        good=1<=j<=5 and j not in faults
        cells[j]=dict(addr=const_word((phase+j)%p.Q,p.k) if good else
            [n.input((j,'addr',b)) for b in range(p.k)],
            age=common if good else [n.input((j,'age',b)) for b in range(p.m)],
            **{f:n.input((j,f)) for f in ('f1','f2','wf1','wf2')})
    result=build(n,cells,p.k,p.m,Q=p.Q,nb=p.nb,radix=p.R,pos_bits=p.PB,service_force=1)
    assert result['addr']==const_word(phase,p.k),(phase,faults)
    assert result['age_now']==common,(phase,faults)
    assert result['age']==mixed_age_increment(n,common,p.PB,p.R,p.nb)


def epoch_clocks(p):
    clocks=np.arange(p.U,dtype=np.uint32)
    codes=np.array([p.age_code(int(t)) for t in clocks],dtype=np.uint32)
    expected_force=(p.T_wf<=clocks)&(clocks<p.T_wf+proposed.EPOCH_LENGTH)
    counts=0
    for phase in (0,1,5,6,p.Q-1):
        n=Net();age=[n.input(('common_Age',b)) for b in range(p.m)]
        cells={j:dict(addr=const_word((phase+j)%p.Q,p.k),age=age) for j in range(6)}
        result=proposed.epoch(n,cells,p,dominant_majority)
        assert result['addr']==const_word(phase,p.k) and result['age']==age
        assert result['tag']==const_word((phase-1)%16,4)
        n.set_output(('force',),result['force']);n.set_output(('birth',),result['birth'])
        got=Compiled(n).evaluate({('common_Age',b):((codes>>b)&1).astype(bool)
                                 for b in range(p.m)},bool)
        assert np.array_equal(got['force',],expected_force)
        assert np.array_equal(got['birth',],(clocks==p.T_wf)&(1<=phase<=5))
        counts+=p.U
    return counts


def charging(p):
    cases=0
    for gap in range(1,9):
        for advance in range(0,2*gap+1,2):
            for old_offset,new_offset in product(range(7),repeat=2):
                assert abs(-advance+new_offset-old_offset)<24 and gap<24
                cases+=1
    assert cases==2156
    updates=next(t for t in range(p.Q+1) if 2*t-2*((t+8)//9)>=p.Q-2)
    assert updates==575
    capture=3*p.Q
    WF_quiet=capture+1
    last_two=WF_quiet+1
    all_quiet=last_two+updates
    assert (capture,WF_quiet,last_two,all_quiet)==(3072,3073,3074,3649)
    assert all_quiet<proposed.EPOCH_LENGTH==4096
    assert 4*p.Q+2+updates>proposed.EPOCH_LENGTH
    assert p.T_wf+proposed.EPOCH_LENGTH<p.U
    assert p.T_wf+capture>p.T_wf+2*p.Q
    return dict(minimum_charged_row_tick_gap=9,charged_row_exclusion_cases=cases,
        quiet_suffix_growth_lower_bound='2*t-2*ceil(t/9)',
        source_free_Flag1_contraction_updates=updates,
        three_colonies_native_capture_state=capture,
        three_colonies_WF1_quiet_state=WF_quiet,
        three_colonies_last_two_Flag1_quiet_state=last_two,
        three_colonies_all_Flag1_quiet_state=all_quiet,
        epoch_force_window_ticks=proposed.EPOCH_LENGTH,
        permanent_aligned_native_halfline_expansion_per_period=3*p.Q,
        four_colony_quieting_not_supplied_by_this_bound=True)


def main():
    started=time.monotonic();p=proposed.parameters()
    build,source=proposed.proposed_build(symbolic=True)
    assert source.count('    f2 = n.OR(f2, service_force)\n')==1
    assert source.count('    vote_right = n.AND(exists, n.OR(n.NOT(f1), f2))\n')==1
    primitive=check_dominance_primitive();quorum=two_good_blocks()
    forced=0
    for phase in range(p.Q):
        for faults in combinations(range(1,6),2):
            forced_right(p,build,phase,faults);forced+=1
    legal=epoch_clocks(p)
    seed=stable=growth=0
    for phase in (p.Q-2,p.Q-1):
        for faults in PAIRS:
            suffix_case(p,build,phase,faults);seed+=1
    for phase in range(p.Q):
        for faults in PAIRS:
            suffix_case(p,build,phase,faults,front=phase);stable+=1
        for delta in (1,2):
            front=phase+delta
            if front>p.Q-2:continue
            for faults in PAIRS:
                if any(front<=phase+off<=front+6 for off in faults):continue
                suffix_case(p,build,phase,faults,front=front);growth+=1
        if phase%128==127:
            print(json.dumps(dict(through_phase=phase,forced=forced,seed=seed,stable=stable,growth=growth)),flush=True)
    native_path=ROOT/'figs/robustness/SP28_native_certificate.json'
    native=json.loads(native_path.read_text())
    assert native['proposed_netlist_sha256']==proposed.cached(p)[1].digest
    assert native['full_output_native_wiring_identities']==29
    generated=proposed.generated_source(p)
    assert generated.count("    in_wf = w_in_range(n, age_now, p.age_code(p.T_wf), p.age_code(p.T_wf + 2 * Q - 1) + 1)")==1
    receipt=dict(proposal='SP28',proposed_rule_change=True,active_G17_modified=False,
        checker_sha256=digest(Path(__file__)),proposal_source_sha256=digest(Path(proposed.__file__)),
        helpers_sha256=digest(ROOT/'gacsca/netlist.py'),
        majority_proof_helper_sha256=digest(ROOT/'Report/proofs/check_right_barrier.py'),
        quiet_suffix_helper_sha256=digest(ROOT/'Report/proofs/check_buffered448_period_barrier.py'),
        raw_cells_helper_sha256=digest(ROOT/'Report/proofs/check_buffered448_arbitrary_age.py'),
        local_proposal_source_sha256=digest(Path(proposed.local.__file__)),
        native_receipt_sha256=digest(native_path),proposed_netlist_sha256=native['proposed_netlist_sha256'],
        actual_maintenance_source_sha256=hashlib.sha256(source.encode()).hexdigest(),
        full_generated_source_sha256=hashlib.sha256(generated.encode()).hexdigest(),
        Q=p.Q,U=p.U,width=proposed.width(p),radius=37,NPe=p.NPe,MP=p.MP,T_wf=p.T_wf,
        five_word_dominance_truth_assignments=primitive,
        two_good_block_quorum_width_two_truth_assignments=quorum,
        two_good_block_no_invented_wrong_word_general_width_proof='ROBUSTNESS J137',
        forced_RF_two_fault_free_LF_self_flags_cofactors=forced,
        actual_epoch_force_and_birth_legal_clock_cases=legal,
        last_two_Flag1_seed_cofactors=seed,stable_quiet_Flag1_suffix_cofactors=stable,
        two_cell_quiet_suffix_growth_outside_charge_zone_cofactors=growth,
        **charging(p),
        initial_aligned_GF_Age_halfline_at_T_wf_required=True,
        initial_native_flags_and_all_other_fields_and_I_arbitrary=True,
        error_set_restricted_to_actual_global_E0=True,higher_errors_allowed=False,
        no_future_left_or_right_boundary_or_work_command_prescribed=True,
        force_window_native_halfline_boundary_advances_one_cell_per_tick_proved=True,
        captured_three_colonies_autonomously_native_correct_after_force_expiry_proved=True,
        all_period_three_colony_native_halfline_expansion_proved=True,
        arbitrary_phase_seed_bootstrap_proved=False,
        opposite_damage_front_confinement_or_finite_island_eroder_proved=False,
        simulation_data_restoration_or_complete_seeded_boundary_encoding_proved=False,
        full_upper_error_map_or_iid_threshold_established=False,global_reliability_established=False,
        seconds=time.monotonic()-started,
        scope='J137 exact epoch-seeded native halfline expansion under actual E0; initial TF native seed remains, no finite-island/data/iid reliability theorem')
    (ROOT/'figs/robustness/SP28_epoch_halfline_certificate.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(forced=forced,seed=seed,stable=stable,growth=growth,
        quiet_state=receipt['three_colonies_all_Flag1_quiet_state'],seconds=receipt['seconds'],iid=False)),flush=True)


if __name__=='__main__':main()
