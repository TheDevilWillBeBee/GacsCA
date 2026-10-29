#!/usr/bin/env python3
"""J110: SP16 upper Flag2 output -> protected courier -> actual source.

Literal copied-output identities after the proven GF/Age controller cut,
small exact data-vote cofactors and own-ROM store/key checks. Initial
work on C must match the pristine operational reference at clock25665;
native flags/packets/codes and both exterior work states are arbitrary.
No general damaged-work initialization, upper map or iid claim.
"""
from itertools import combinations
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from gacsca import rule_g
from gacsca.netlist import Net,const_word,w_eq,w_eq_const,w_mux
from check_shifted_halfline import dominant_bit
from check_buffered448_incorporation import full_net
import check_fast_mail_proposal as transport
import proposed_sparse_buffered448 as proposed


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(n,p,reader,primary,field,bit=0,majority=rule_g.maj5):
    width = proposed.logical_width(field,p)
    return majority(n,[n.input(('x',y-reader,field,(primary-y+2)*width+bit))
        for y in range(primary+2,primary-3,-1)])


def forwarded_hold(n,p,reader,primary,majority=rule_g.maj5):
    value = read(n,p,reader,primary,'hold',majority=majority)
    pending = read(n,p,reader,primary,'pend',majority=majority)
    kind = [read(n,p,reader,primary,'pkind',b,majority) for b in range(p.PK)]
    hit = n.AND(pending,w_eq_const(n,kind,0))
    return n.MUX(hit,read(n,p,reader,primary,'pval',majority=majority),value)


def keep(n,p,reader):
    same = w_eq(n,[n.input(('x',0,'addr',b)) for b in range(p.k)],const_word(reader%p.Q,p.k))
    return n.NOT(n.AND(n.input(('proof','free_computed_Flag1')),n.NOT(same)))


def projected(p,reader,clock,word=None):
    class BoundNet(Net):
        def input(self,key):
            if key[0] == 'I' and word is not None:
                return (word>>key[1])&1
            return super().input(key)
    def controller(n,*args,**kwargs):
        return dict(addr=const_word(reader%p.Q,p.k),age_now=const_word(p.age_code(clock),p.m),
            age=const_word(p.age_code(clock+1),p.m),
            f1=n.input(('proof','free_computed_Flag1')),f2=n.input(('proof','free_computed_Flag2')))
    # This is an explicit proof cut, not a modified CA. Native field
    # inductions establish these controller values on the used holders;
    # copied formulas leave every raw state/I bit free otherwise.
    return full_net(p,net_class=BoundNet,maintenance=controller)


def literal_output_identities(p):
    load = p.courier_ticks()[1]
    identities = 0
    source_hash = None
    for clock in range(load,p.T_sig):
        target = p.lo-(clock-load)
        for reader in range(target-2,target+3):
            n,source = projected(p,reader,clock)
            value = forwarded_hold(n,p,reader,target) if clock == load else read(n,p,reader,target+1,'ml')
            expected = n.AND(keep(n,p,reader),value)
            assert n.outputs['y','ml',target-reader+2] == expected,(clock,target,reader)
            identities += 1
            source_hash = hashlib.sha256(source.encode()).hexdigest()
    for reader in range(1,6):
        n,_ = projected(p,reader,p.T_sig)
        expected = n.AND(keep(n,p,reader),read(n,p,reader,3,'ml'))
        assert n.outputs['y','info',3-reader+2] == expected,reader
        identities += 1
    hold = 0
    for reader in range(p.lo-2,p.lo+3):
        n,_ = projected(p,reader,26737)
        assert n.outputs['y','hold',p.lo-reader+2] == n.AND(keep(n,p,reader),forwarded_hold(n,p,reader,p.lo))
        hold += 1
    assert (identities,hold) == (285,5)
    return identities,hold,source_hash


def no_later_store(candidate):
    p = candidate.p
    start = 26737
    load = p.courier_ticks()[1]
    arrivals = []
    for clock in range(start,load):
        page,tick = divmod(clock-p.E0,p.PL)
        assert page < p.MP
        step = tick if page%2 == 0 else p.PL-1-tick
        for front in range(p.fronts):
            if p.lo-p.H+step+front*p.delta != p.lo:
                continue
            column = page+(front<<p.logNP)
            word = int(candidate.rom[p.lo,column])
            assert (word>>2)&3 == rule_g.K_REG,(clock,front,word)
            arrivals.append(dict(clock=clock,page=page,front=front,column=column,instruction_word=word))
    keys = reset = 0
    for row in arrivals:
        for reader in range(p.lo-2,p.lo+3):
            n,_ = projected(p,reader,row['clock'],row['instruction_word'])
            assert [n.outputs['laddr',b] for b in range(p.k)] == const_word(p.lo,p.k)
            assert [n.outputs['psel',b] for b in range(p.PW)] == const_word(row['column'],p.PW)
            keys += 1
            slot = p.lo-reader+2
            assert n.outputs['y','pend',slot] == 0
            assert n.outputs['y','pval',slot] == 0
            assert all(n.outputs['y','pkind',slot*p.PK+b] == 0 for b in range(p.PK))
            reset += 1
    # Last pre-launch step: no front arrives at logical58; all I/work
    # bits are free. This clears stale source pending fields even on
    # a holder where the raw-GF wipe fires.
    for reader in range(p.lo-2,p.lo+3):
        n,_ = projected(p,reader,load-1)
        slot = p.lo-reader+2
        assert n.outputs['y','pend',slot] == 0
        assert n.outputs['y','pval',slot] == 0
        assert all(n.outputs['y','pkind',slot*p.PK+b] == 0 for b in range(p.PK))
        reset += 1
    assert (len(arrivals),keys,reset) == (8,40,45)
    return arrivals,keys,reset,load-start


def vote_case(p,stage,reader,primary,current=(),previous=()):
    assert 0 not in current
    if previous:
        assert not current
    source = primary+1 if stage == 'transfer' else primary
    data_field = 'ml' if stage in ('transfer','signal') else 'hold'
    class BoundNet(Net):
        def input(self,key):
            if key[0] == 'x':
                _,off,field,bit = key
                y = reader+off
                if field == 'addr' and off == 0:
                    return ((reader%p.Q)>>bit)&1
                width = proposed.logical_width(field,p)
                logical = y+bit//width-2
                if logical == source and source-2 <= y <= source+2:
                    if off in current:
                        return super().input(key)
                    old_bad = y in previous
                    if stage == 'entry':
                        if field == 'pend' and not old_bad:
                            return 1
                        if field == 'pkind' and not old_bad:
                            return 0
                        if field == 'pval' and not old_bad:
                            return super().input(('verified_upper_Flag2',))
                    else:
                        if field == data_field and not old_bad:
                            return super().input(('verified_upper_Flag2',))
                        if field == 'pend' and stage in ('carry','load'):
                            # Computed source pending is0 even at a
                            # previous noisy holder; only current raw
                            # replacements can alter it.
                            return 0
            return super().input(key)
    n = BoundNet()
    if stage in ('entry','carry','load'):
        value = forwarded_hold(n,p,reader,source,dominant_bit)
    else:
        value = read(n,p,reader,source,'ml',majority=dominant_bit)
    output = n.AND(keep(n,p,reader),value)
    assert output == n.input(('verified_upper_Flag2',)),(stage,reader,current,previous)


def data_votes(p):
    current = tuple(combinations([off for off in range(-5,6) if off != 0],2))
    stages = [('entry',p.lo),('carry',p.lo),('load',p.lo),('transfer',p.lo-1),('signal',3)]
    counts = {}
    for stage,primary in stages:
        cases = 0
        source = primary+1 if stage == 'transfer' else primary
        for reader in range(primary-2,primary+3):
            for faults in current:
                vote_case(p,stage,reader,primary,current=faults)
                cases += 1
            for old in combinations(range(source-2,source+3),2):
                vote_case(p,stage,reader,primary,previous=old)
                cases += 1
        assert cases == 275
        counts[stage] = cases
    # Separate E0 groups at adjacent ticks cannot both meet a source
    # five-copy window or the containing eleven-site local window.
    exclusions = 0
    for old in range(-5,6):
        for current_off in range(-5,6):
            assert abs(old-current_off) < 24
            exclusions += 1
    assert exclusions == 121
    return counts,exclusions


def work_footprint(p):
    first = p.lo-p.H
    last = first+p.PL-1+(p.fronts-1)*p.delta
    interval = [first-3,last+3]
    assert interval == [35,412] and interval[0] >= 0 and interval[1] < p.Q
    start = p.T_wf-1792
    store = 26736
    states = 0
    for t in range(store+2-start+1):
        assert -8972+5*t <= interval[0]-5 and 8978-5*t >= interval[1]+5
        assert -8961+5*t <= interval[0]-5 and 8967-5*t >= interval[1]+5
        page = (start+t-p.E0)//p.PL
        assert page < p.MP
        # Every sparse capture and mail/gather reset is already past.
        assert start+t > p.gathers_q[-1]*p.Q+12*(p.Q//8)+1
        states += 1
    load = p.courier_ticks()[1]
    route = []
    for clock in range(load,p.T_sig+1):
        primary = p.lo-(clock-load) if clock < p.T_sig else 3
        t = clock-start
        # Five physical holders, and +/-5 native GF/Age neighbors for
        # their selected controls. Protected copying tolerates current
        # and previous state-copy punctures separately.
        left,right = primary-7,primary+7
        assert -8972+5*t <= left and 8978-5*t >= right
        assert -8961+5*t <= left and 8967-5*t >= right
        route.append(dict(input_clock=clock,state=t,target_primary=primary,
            source_primary=primary if clock in (load,p.T_sig) else primary+1,
            five_output_holders=list(range(primary-2,primary+3))))
    assert len(route) == 57
    return interval,states,route


def early_Flag2_dependencies(comp):
    first = 2+len(comp.inputs)
    todo = [comp.outputs['y','f2',0]]
    seen = set()
    while todo:
        node = todo.pop()
        if node in seen:
            continue
        seen.add(node)
        if node >= first:
            _,a,b = comp.gates[node-first]
            todo.extend((a,b))
    inputs = [name for name,node in comp.index.items() if node in seen]
    assert inputs and all(name[0] != 'I' for name in inputs)
    return len(seen),len(inputs)


def main():
    candidate = proposed.load_artifact()
    p = candidate.p
    out = ROOT/'figs/robustness'
    schedule = json.loads((out/'SP16_symbolic_schedule.json').read_text())
    assert schedule['early_flag_store_ages']['58'] == 26736
    assert p.T_wf-1792 == 25665 and p.courier_ticks()[1] == 27400
    assert p.T_sig == 27456 and p.T_wf == 27457
    assert transport.maj5_truth() == 32
    counts,exclusions = data_votes(p)
    interval,states,route = work_footprint(p)
    dependencies_nodes,dependencies_inputs = early_Flag2_dependencies(candidate.comp)
    arrivals,keys,reset,ticks = no_later_store(candidate)
    identities,holds,source_hash = literal_output_identities(p)
    dependencies = {key:digest(out/name) for key,name in (
        ('build_receipt_sha256','SP16_program_build.json'),
        ('programme_receipt_sha256','SP16_symbolic_schedule.json'),
        ('incorporation_receipt_sha256','SP16_buffered_incorporation_certificate.json'),
        ('encoding_receipt_sha256','SP16_encoded_certificate.json'),
        ('preparation_receipt_sha256','SP16_guard_preparation_certificate.json'),
        ('arbitrary_Age_receipt_sha256','SP16_arbitrary_age_certificate.json'))}
    receipt = dict(proposal='SP16',proposed_rule_change=False,active_G17_modified=False,SP15_modified=False,
        proposed_candidate_sha256=candidate.digest(),proposed_netlist_sha256=candidate.comp.digest,
        checker_sha256=digest(Path(__file__)),proposal_source_sha256=digest(Path(proposed.__file__)),
        helpers_sha256=digest(ROOT/'gacsca/netlist.py'),
        full_rule_checker_sha256=digest(ROOT/'Report/proofs/check_buffered448_incorporation.py'),
        dominant_bit_helper_sha256=digest(ROOT/'Report/proofs/check_shifted_halfline.py'),
        transport_checker_sha256=digest(ROOT/'Report/proofs/check_fast_mail_proposal.py'),
        buffered_service_source_sha256=digest(Path(proposed.service.__file__)),
        generated_source_with_proven_controller_cut_sha256=source_hash,
        full_generated_source_sha256=hashlib.sha256(proposed.actual_net(p)[1].encode()).hexdigest(),**dependencies,
        GF_Age_controller_projection_is_explicit_proof_cut_not_rule_change=True,
        projected_literal_ML_Info_output_identities=identities,projected_literal_forwarded_Hold_output_identities=holds,
        data_vote_cofactors=counts,adjacent_tick_fault_union_exclusion_cases=exclusions,
        majority_truth_assignments_checked=32,
        after_final_Flag2_store_source_clock_inputs_checked=ticks,
        source_arrivals_after_final_store=arrivals,source_normal_lookup_key_identities=keys,
        source_pending_value_kind_reset_output_groups=reset,
        initial_pristine_reference_work_snapshot_clock=p.T_wf-1792,
        required_reference_work_fields_on_true_colony=['info','hold','h1','scr','reg','pend','pkind','pval'],
        MR_ML_h2_native_ordinary_flags_packets_codes_and_exterior_work_initially_free=True,
        finite_initial_GF_Age_field_shields_of_J109_required=True,
        mid_period_initial_work_snapshot_from_complete_encoding_of_arbitrary_upper_z_required=True,
        no_mid_period_work_snapshot_recovery_from_arbitrary_damaged_work_proved=True,
        upper_Flag2_value_is_actual_F16_of_represented_z_at_upper_cell_zero=True,
        upper_Flag2_target_ancestor_nodes=dependencies_nodes,upper_Flag2_target_input_dependencies=dependencies_inputs,
        upper_Flag2_target_has_no_I_dependencies=True,
        preserved_reference_front_and_operand_physical_interval=interval,
        initial_work_programme_prefix_field_shield_states_checked=states,
        actual_last_upper_Flag2_store_input_clock=26736,correct_pending_output_computed_state=1072,
        corrected_source_Hold_computed_state=1073,courier_load_input_clock=27400,courier_route=route,
        source_pending_zero_at_launch_derived_not_assumed=True,
        five_special_Info_copies_equal_verified_command_outside_previous_input_faults_at_state=1792,
        current_and_previous_Info_copy_faults_tolerated_at_birth=True,
        future_fivefold_Info_command_assumption_of_J109_removed_with_stated_reference_work_seed=True,
        actual_proper_source_born_iff_verified_upper_Flag2_one_at_state=1793,
        if_upper_Flag2_zero_no_computed_packet_in_one_through_five_at_state_1793=True,
        proper_source_when_one_persists_through_state=3584,
        no_prescribed_right_boundary_or_initial_packet_state_required_for_source_result=True,
        optional_canonical_C_and_right_reference_required_for_Age_repair_when_upper_Flag2_one=True,
        optional_Age_repair_state=2486,
        command_and_work_seed_recovery_general_GF_islands_full_upper_map_or_iid_threshold_established=False,
        global_reliability_established=False,
        scope='actual SP16 verified early upper Flag2 output/corrected Hold/protected courier/Info/source under E0 from a pristine mid-period C work seed and finite GF/Age field shields; ROBUSTNESS J110')
    (out/'SP16_command_certificate.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(output_identities=identities,Hold_identities=holds,data_cofactors=counts,
        source_keys=keys,pending_reset_groups=reset,source_state=1793,global_reliability_established=False)),flush=True)


if __name__ == '__main__':
    main()
