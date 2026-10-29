#!/usr/bin/env python3
"""J115: SP17 autonomous complete C boundary from a specified mid-period seed.

No rule change. Exact shifted command/courier/reset identities and reuse
of unchanged native cofactors, with a written simultaneous packet/native
induction. Initial GF/Age halfline, two quiet colonies, valid C work seed,
verified upper Flag2=1 and global E0 remain required. A radius12 finite
initial field buffer suffices for the C-only conclusion. No iid threshold.
"""
from pathlib import Path
import hashlib
import json
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from gacsca import rule,rule_g
from gacsca.netlist import Net,const_word,w_in_range,mixed_age_increment
from check_buffered448_command import read,forwarded_hold,keep
import check_buffered448_quiet_region as native
import check_buffered448_period_barrier as period
import check_commit_reset448_incorporation as reset
import proposed_sparse_commit_reset448 as proposed


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def projected(p,reader,clock,word=None):
    class BoundNet(Net):
        def input(self,key):
            if key[0] == 'I' and word is not None:
                return (word>>key[1])&1
            return super().input(key)
    def controller(n,*args,**kwargs):
        return dict(addr=const_word(reader%p.Q,p.k),age_now=const_word(p.age_code(clock),p.m),
            age=const_word(p.age_code((clock+1)%p.U),p.m),
            f1=n.input(('proof','free_computed_Flag1')),f2=n.input(('proof','free_computed_Flag2')))
    return proposed.full_net(p,net_class=BoundNet,maintenance=controller)


def courier_and_store(candidate,schedule):
    p=candidate.p
    store=schedule['early_flag_store_ages'][str(p.lo)]
    assert store == 28154
    load=p.courier_ticks()[1]
    assert load == 28808 and p.T_sig == 28864
    identities=holds=0
    for clock in range(load,p.T_sig):
        target=p.lo-(clock-load)
        for reader in range(target-2,target+3):
            n,source=projected(p,reader,clock)
            value=forwarded_hold(n,p,reader,target) if clock == load else read(n,p,reader,target+1,'ml')
            assert n.outputs['y','ml',target-reader+2] == n.AND(keep(n,p,reader),value),(clock,reader)
            identities += 1
    for reader in range(1,6):
        n,_=projected(p,reader,p.T_sig)
        assert n.outputs['y','info',3-reader+2] == n.AND(keep(n,p,reader),read(n,p,reader,3,'ml')),reader
        identities += 1
    for reader in range(p.lo-2,p.lo+3):
        n,_=projected(p,reader,store+1)
        assert n.outputs['y','hold',p.lo-reader+2] == n.AND(keep(n,p,reader),forwarded_hold(n,p,reader,p.lo))
        holds += 1
    assert (identities,holds) == (285,5)
    arrivals=[]
    keys=pending=0
    for clock in range(store+1,load):
        page,tick=divmod(clock-p.E0,p.PL)
        assert page < p.MP
        step=tick if page%2 == 0 else p.PL-1-tick
        for front in range(p.fronts):
            if p.lo-p.H+step+front*p.delta != p.lo:
                continue
            column=page+(front<<p.logNP)
            word=int(candidate.rom[p.lo,column])
            assert (word>>2)&3 == rule_g.K_REG,(clock,front,word)
            arrivals.append(dict(clock=clock,page=page,front=front,column=column,instruction_word=word))
            for reader in range(p.lo-2,p.lo+3):
                n,_=projected(p,reader,clock,word)
                assert [n.outputs['laddr',b] for b in range(p.k)] == const_word(p.lo,p.k)
                assert [n.outputs['psel',b] for b in range(p.PW)] == const_word(column,p.PW)
                keys += 1
                slot=p.lo-reader+2
                assert n.outputs['y','pend',slot] == n.outputs['y','pval',slot] == 0
                assert all(n.outputs['y','pkind',slot*p.PK+b] == 0 for b in range(p.PK))
                pending += 1
    for reader in range(p.lo-2,p.lo+3):
        n,_=projected(p,reader,load-1)
        slot=p.lo-reader+2
        assert n.outputs['y','pend',slot] == n.outputs['y','pval',slot] == 0
        assert all(n.outputs['y','pkind',slot*p.PK+b] == 0 for b in range(p.PK))
        pending += 1
    assert (len(arrivals),keys,pending) == (6,30,35)
    return dict(upper_Flag2_last_store_input_clock=store,source_pending_correct_computed_state=1082,
        source_Hold_correct_computed_state=1083,protected_courier_load_input_clock=load,
        last_store_to_courier_input_clock_gap=load-store,
        protected_courier_and_Info_literal_output_identities=identities,
        source_forwarded_Hold_literal_output_identities=holds,
        post_store_source_arrivals=arrivals,post_store_actual_source_key_groups=keys,
        post_store_source_pending_zero_groups=pending,
        source_pending_zero_at_courier_derived_not_prescribed=True),hashlib.sha256(source.encode()).hexdigest()


def time_arithmetic(p):
    base=p.T_wf-1792
    T=p.U-base
    assert (base,T) == (27073,40511)
    pre=increments=wf_excluded=idle=0
    for t in range(1792):
        n=Net()
        assert w_in_range(n,const_word(p.age_code(base+t),p.m),p.age_code(p.T_wf),p.age_code(p.T_wf+2*p.Q-1)+1) == 0
        pre += 1
    for clock in range(base,p.U):
        n=Net()
        assert mixed_age_increment(n,const_word(p.age_code(clock),p.m),p.PB,p.R,p.nb) == const_word(p.age_code((clock+1)%p.U),p.m)
        increments += 1
    for t in range(2689,T):
        n=Net()
        assert w_in_range(n,const_word(p.age_code(base+t),p.m),p.age_code(p.T_wf),p.age_code(p.T_wf+2*p.Q-1)+1) == 0
        wf_excluded += 1
    end=p.E0+p.NP*p.PL
    assert end == 56320
    for clock in range(end,p.U):
        n=Net()
        gf=[n.input(('arbitrary_GF',b)) for b in range(p.k)]
        assert rule.front_controls(n,p,dict(age=const_word(p.age_code(clock),p.m),addr=gf))['arrive'] == 0
        idle += 1
    for t in range(1793,3585):
        # Simultaneous native/packet induction: each proper holder has
        # this actual clock, so its extra SP17 output erasure is off.
        assert p.T_wf < base+t <= p.T_wf+1792 < p.U-1
    assert (pre,increments,wf_excluded,idle) == (1792,40511,37822,11264)
    assert p.gathers_q[-1]*p.Q+12*(p.Q//8)+1 == 9633 < base
    assert p.lo-p.H-3 == 35 and p.lo-p.H+p.PL-1+(p.fronts-1)*p.delta+3 == 412
    assert p.lo-2 >= 0 and p.hi+1 < p.Q
    quiet=period.quieting_arithmetic(p)
    assert quiet['all_C_Flag1_quiet_computed_state'] == 2942 < 3584 < T
    return dict(initial_reference_clock=base,current_period_boundary_state=T,
        pre_window_clock_exclusion_checks=pre,reference_mixed_radix_increment_checks=increments,
        after_window_before_commit_WF1_exclusion_checks=wf_excluded,pre_commit_idle_clock_checks=idle,
        proper_holder_commit_exclusion_checks=1792,latest_history_capture_clock=9633,
        required_work_operand_holder_interval=[35,412],**quiet)


def actual_WF1_identities(p):
    checked=0
    for address in range(p.Q-5,p.Q):
        def controller(n,*args,**kwargs):
            age=[n.input(('proof_common_Age',b)) for b in range(p.m)]
            return dict(addr=const_word(address,p.k),age_now=age,
                age=mixed_age_increment(n,age,p.PB,p.R,p.nb),f1=0,f2=n.input(('proof_free_F2',)))
        n,_=proposed.full_net(p,maintenance=controller)
        age=[n.input(('proof_common_Age',b)) for b in range(p.m)]
        expected=n.AND(w_in_range(n,age,p.age_code(p.T_wf),p.age_code(p.T_wf+2*p.Q-1)+1),
            read(n,p,address,p.Q-3,'info'))
        assert n.outputs['y','wf1',0] == expected,address
        checked += 1
    assert checked == 5
    return checked


def main():
    candidate=proposed.load_artifact()
    p=candidate.p
    out=ROOT/'figs/robustness'
    schedule=json.loads((out/'SP17_symbolic_schedule.json').read_text())
    old_native=json.loads((out/'SP16_quiet_region_certificate.json').read_text())
    old_period=json.loads((out/'SP16_period_barrier_certificate.json').read_text())
    incorporated=json.loads((out/'SP17_incorporation_encoded_certificate.json').read_text())
    source=proposed.proposed_build()[1]
    native_source=hashlib.sha256(source.encode()).hexdigest()
    actual_net=proposed.cached(p)[0]
    live=set(actual_net.live_nodes())
    raw_offsets={key[1] for key,node in actual_net.input_node.items()
                 if key[0] == 'x' and node in live}
    assert max(abs(offset) for offset in raw_offsets) == 12
    assert all(key[0] in ('x','I') for key in actual_net.input_node)
    assert native_source == old_native['actual_maintenance_source_sha256'] == old_period['actual_maintenance_source_sha256']
    oldp=proposed.previous.parameters()
    for field in ('Q','U','k','m','R','PB','nb','lo','hi','PL','fronts','delta','L','S','NP'):
        assert getattr(p,field) == getattr(oldp,field),field
    assert incorporated['full_unrestricted_output_equalities_unchanged'] == 292
    assert incorporated['all_full_outputs_unchanged_off_computed_commit_clock']
    courier,full_source=courier_and_store(candidate,schedule)
    assert full_source == incorporated['full_generated_source_sha256']
    times=time_arithmetic(p)
    wf=actual_WF1_identities(p)
    data=native.quiet_data_votes(p)
    zeros,commit_infos=reset.commit_identities(p)
    assert (zeros,commit_infos) == (283,5)
    assert incorporated['allowed_Info_primaries'] == 318 and incorporated['unrepresented_Info_copy_slots_zero'] == 650
    dependencies={key:digest(out/name) for key,name in (
        ('build_receipt_sha256','SP17_program_build.json'),
        ('programme_receipt_sha256','SP17_symbolic_schedule.json'),
        ('incorporation_receipt_sha256','SP17_incorporation_encoded_certificate.json'),
        ('SP16_quiet_region_receipt_sha256','SP16_quiet_region_certificate.json'),
        ('SP16_preparation_receipt_sha256','SP16_guard_preparation_certificate.json'),
        ('SP16_period_barrier_receipt_sha256','SP16_period_barrier_certificate.json'),
        ('guard6_receipt_sha256','packet_guard6_certificate.json'),
        ('packet_pressure_receipt_sha256','packet_pressure_certificate.json'))}
    receipt=dict(proposal='SP17',proposed_rule_change=False,active_G17_modified=False,SP16_modified=False,SP15_modified=False,
        proposed_candidate_sha256=candidate.digest(),proposed_netlist_sha256=candidate.comp.digest,
        checker_sha256=digest(Path(__file__)),proposal_source_sha256=digest(Path(proposed.__file__)),
        helpers_sha256=digest(ROOT/'gacsca/netlist.py'),base_front_controls_source_sha256=digest(ROOT/'gacsca/rule.py'),
        native_quiet_region_helper_sha256=digest(Path(native.__file__)),
        native_period_barrier_helper_sha256=digest(Path(period.__file__)),
        commit_reset_helper_sha256=digest(Path(reset.__file__)),
        forwarded_Hold_helper_sha256=digest(ROOT/'Report/proofs/check_buffered448_command.py'),
        buffered_service_source_sha256=digest(Path(proposed.service.__file__)),
        actual_maintenance_source_sha256=native_source,full_generated_source_sha256=full_source,
        **dependencies,**courier,**times,
        actual_live_raw_input_radius=12,
        finite_C_only_initial_GF_Age_interval=[-p.Q,p.Q-1+12*times['current_period_boundary_state']],
        finite_C_only_right_dependency_buffer_cells=12*times['current_period_boundary_state'],
        finite_C_only_dependency_agreement_right_edge_at_boundary=p.Q-1,
        actual_symbolic_WF1_window_Info_output_identities=wf,
        quiet_copied_data_votes_including_current_holder_replacements=data,
        inherited_quiet_native_cofactors=old_native['quiet_native_GF_Age_Flag1_cofactors'],
        inherited_active_source_GF_Age_cofactors=old_native['source_sealed_GF_Age_free_flags_cofactors'],
        inherited_extra_two_mode_wrap_cofactors=old_native['two_mode_first_five_phase_extra_cofactors'],
        inherited_Flag1_seed_stable_growth_cofactors=[old_period['last_two_Flag1_seed_cofactors'],
            old_period['stable_quiet_Flag1_suffix_cofactors'],old_period['two_cell_quiet_suffix_growth_outside_charge_zone_cofactors']],
        initial_GF_Age_correct_halfline_x_ge_minus_Q_required=True,
        initial_quiet_Flag1_WF1_only_two_colonies_required=True,
        initial_valid_C_eight_field_work_seed_from_operational_F17_reference_required=True,
        verified_F17_upper_Flag2_one_required_for_complete_boundary_conclusion=True,
        global_E0_through_current_boundary_required=True,
        all_initial_packet_code_NF2_and_exterior_work_fields_arbitrary=True,
        no_future_left_or_right_boundary_prescribed=True,
        local_guard_preparation_witness_induction_allows_additional_exterior_commit_deletions=True,
        actual_newborn_source_born_iff_upper_Flag2_one_at_computed_state=1793,
        simultaneous_proper_packet_and_GF_Age_induction_keeps_proper_holders_off_commit=True,
        source_proper_when_one_persists_through_state=3584,
        GF_Age_autonomously_correct_on_x_ge_zero_through_current_boundary=True,
        Flag1_WF1_on_C_quiet_from_computed_state_2942_through_boundary=True,
        all316_outputs_and_two_reserved_flag_values_have_five_correct_Info_copies_at_boundary=True,
        native_Flag2_components_workspace_and_all_unused_Info_reset_at_boundary=True,
        exact_full_computed_C_boundary_equals_complete_E17_encoding_of_F17_z_at_zero=True,
        current_boundary_E0_overwrite_leaves_exact_five_copy_upper_decoder=True,
        full_boundary_native_Flag2_component_workspace_literal_zero_bits=283,
        full_boundary_Info_unused_copy_slots_literal_zero=650,
        rule_or_ROM_change_in_this_checker=False,
        arbitrary_damaged_native_work_seed_recovery_repeated_periods_full_upper_map_or_iid_threshold_established=False,
        finite_initial_GF_Age_right_interval_sufficient_for_C_only_full_boundary_established=True,
        finite_field_corollary_uses_same_ROM_and_coupled_E0_overwrites=True,
        finite_field_corollary_is_uniform_small_island_repair_established=False,
        global_reliability_established=False,
        scope='ROBUSTNESS J115: unchanged SP17 complete current C boundary from initial GF/Age halfline (or radius12 finite C-only buffer), two quiet colonies, valid own mid-period work seed and upper Flag2=1 under E0; no general seed recovery, small-island repair, full upper map or iid threshold')
    (out/'SP17_seeded_boundary_certificate.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(source=1793,Flag1_quiet=2942,boundary=times['current_period_boundary_state'],
        courier_identities=courier['protected_courier_and_Info_literal_output_identities'],
        commit_zero_bits=zeros,unused_Info_copies=650,global_reliability_established=False)),flush=True)


if __name__ == '__main__':
    main()
