#!/usr/bin/env python3
"""J112: autonomous SP16 GF/Age/F1/WF1 current-period barrier and decoder.

Exact quiet-suffix/native/commit cofactors plus source/programme reuse.
Requires J111's infinite initial GF/Age variant and valid mid-period C
work seed, with the verified upper Flag2 output1 and global E0.
Full component/NF2 reset and general damaged-work recovery are unproved.
An actual-rule endpoint birth-clock counterexample pins one invalid
shortcut; its reachability from the initial seed is not established.
"""
from itertools import combinations
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from gacsca import rule
from gacsca.netlist import Net,const_word,mixed_age_increment,w_in_range,w_eq
from check_buffered448_arbitrary_age import raw_cells,invoke
from check_buffered448_incorporation import full_net
from check_buffered448_command import forwarded_hold
import proposed_sparse_buffered448 as proposed

PAIRS = tuple(combinations(range(-5,9),2))
RESET_FIELDS = ('hold','mr','ml','h1','h2','scr','reg','pend','pkind','pval')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def suffix_case(p,build,address,faults,front=None):
    n = Net()
    age = [n.input(('reference_Age',b)) for b in range(p.m)]
    cells = raw_cells(n,p,address,faults,reference_age=age)
    for off in range(-5,9):
        y = address+off
        good = off not in faults
        cells[off]['wf1'] = 0 if good and 0 <= y < p.Q else n.input((off,'wf1'))
        cells[off]['f1'] = 0 if good and front is not None and front <= y < p.Q else n.input((off,'f1'))
    result = invoke(build,n,cells,p,n.input(('arbitrary_service_pressure',)))
    assert result['f1'] == 0,(address,faults,front)
    assert result['addr'] == const_word(address,p.k),(address,faults,front)
    assert result['age_now'] == age,(address,faults,front)
    assert result['age'] == mixed_age_increment(n,age,p.PB,p.R,p.nb)


def quieting_arithmetic(p):
    exclusions = 0
    for gap in range(1,9):
        for advance in range(0,2*gap+1,2):
            for old_offset in range(7):
                for new_offset in range(7):
                    assert abs(-advance+new_offset-old_offset) < 24
                    assert gap < 24
                    exclusions += 1
    assert exclusions == 2156
    updates = next(t for t in range(1000) if 2*t-2*((t+8)//9) >= p.Q-2)
    assert updates == 251
    W=2690
    assert W+1+updates == 2942 < 3584
    return dict(source_free_WF1_computed_state=W,last_two_Flag1_quiet_computed_state=W+1,
        quiet_suffix_current_fault_charge_interval_relative_to_front=[0,6],
        minimum_charged_row_tick_gap=9,charged_row_exclusion_cases=exclusions,
        further_quiet_suffix_updates=updates,all_C_Flag1_quiet_computed_state=W+1+updates)


def commit_identities(p):
    def controller(n,*args,**kwargs):
        return dict(addr=[n.input(('proof_free_computed_GF',b)) for b in range(p.k)],
            age_now=const_word(p.age_code(p.U-1),p.m),age=const_word(0,p.m),
            f1=n.input(('proof_free_computed_F1',)),f2=n.input(('proof_free_computed_F2',)))
    n,source = full_net(p,maintenance=controller)
    zeros = 0
    for field,width in proposed.schema(p):
        if field in RESET_FIELDS:
            for b in range(width):
                assert n.outputs['y',field,b] == 0,(field,b)
                zeros += 1
    assert zeros == 244
    gf = [n.input(('proof_free_computed_GF',b)) for b in range(p.k)]
    raw = [n.input(('x',0,'addr',b)) for b in range(p.k)]
    keep = n.NOT(n.AND(n.input(('proof_free_computed_F1',)),n.NOT(w_eq(n,gf,raw))))
    infos = 0
    for slot in range(-2,3):
        expected = n.AND(keep,forwarded_hold(n,p,0,slot))
        assert n.outputs['y','info',slot+2] == expected,slot
        infos += 1
    assert infos == 5 and n.outputs['y','wf1',0] == 0
    return zeros,infos,hashlib.sha256(source.encode()).hexdigest()


def clock_and_idle(p):
    base=25665
    boundary=p.U-base
    assert boundary == 41919
    excluded=0
    for t in range(2689,boundary):
        n=Net()
        word=p.age_code(base+t)
        assert w_in_range(n,const_word(word,p.m),p.age_code(p.T_wf),p.age_code(p.T_wf+2*p.Q-1)+1) == 0
        excluded += 1
    assert excluded == 39230
    increments=0
    for clock in range(base,p.U):
        n=Net()
        assert mixed_age_increment(n,const_word(p.age_code(clock),p.m),p.PB,p.R,p.nb) == const_word(p.age_code((clock+1)%p.U),p.m)
        increments += 1
    assert increments == 41919
    idle=0
    evaluation_end=p.E0+p.NP*p.PL
    assert evaluation_end == 56320
    for clock in range(evaluation_end,p.U):
        n=Net()
        addr=[n.input(('arbitrary_computed_GF',b)) for b in range(p.k)]
        ctl=rule.front_controls(n,p,dict(age=const_word(p.age_code(clock),p.m),addr=addr))
        assert ctl['arrive'] == 0,clock
        idle += 1
    assert idle == 11264
    latest=p.gathers_q[-1]*p.Q+12*(p.Q//8)+1
    assert latest == 9633 < base
    assert p.lo-p.H-3 == 35 and p.lo-p.H+p.PL-1+(p.fronts-1)*p.delta+3 == 412
    return dict(reference_current_period_boundary_state=boundary,
        remaining_GF_Age_reference_increments_checked=increments,
        after_window_before_wrap_WF1_excluded_input_clocks=excluded,
        programme_evaluation_end_input_clock=evaluation_end,pre_commit_idle_input_clocks=idle,
        latest_history_capture_clock=latest,remaining_programme_operand_holder_interval=[35,412])


def late_birth_case(p,reader):
    fault_sites=(1,2)
    late=p.U-1
    class BoundNet(Net):
        def input(self,key):
            if key[0] == 'x':
                _,off,field,b=key
                y=reader+off
                if field == 'addr': return (((y if y >= 0 else y+4)%p.Q)>>b)&1
                if field == 'age':
                    clock=p.T_wf if y < 0 or y in fault_sites else late
                    return (p.age_code(clock)>>b)&1
                if field == 'f1': return int(y < 0)
                if field in ('f2','wf1','wf2','packet_valid','service_valid','pend'): return 0
                if field == 'info': return int(y+b-2 in (-1,3))
                if field == 'hold': return 0
            return super().input(key)
    n,source=full_net(p,net_class=BoundNet,observe=True)
    born=reader in (-3,-2,-1,1)
    gf=reader+4 if reader < 0 else reader
    clock=p.T_wf if reader < 0 else late
    assert [n.outputs['y','addr',b] for b in range(p.k)] == const_word(gf,p.k),reader
    assert [n.outputs['y','age',b] for b in range(p.m)] == const_word(p.age_code((clock+1)%p.U),p.m),reader
    assert n.outputs['y','f1',0] == int(reader < 0),reader
    assert n.outputs['proof','guard'] == 0,reader
    assert n.outputs['proof','birth'] == int(born),reader
    assert n.outputs['y','packet_valid',0] == n.outputs['y','wf2',0] == int(born),reader
    assert [n.outputs['y','packet_tag',b] for b in range(4)] == const_word(gf-1 if born else 0,4),reader
    assert all(n.outputs['y','packet_count',b] == 0 for b in range(11)),reader
    for field,width in proposed.schema(p):
        if field.startswith('service_'):
            assert all(n.outputs['y',field,b] == 0 for b in range(width)),(reader,field)
    if reader >= 0:
        for field,width in proposed.schema(p):
            if field in RESET_FIELDS:
                assert all(n.outputs['y',field,b] == 0 for b in range(width)),(reader,field)
    return dict(reader=reader,new_GF=gf,new_clock=(clock+1)%p.U,
        packet_valid=int(born),packet_tag=gf-1 if born else 0,
        newborn_integer_origin=reader-gf if born else None),hashlib.sha256(source.encode()).hexdigest()


def main():
    candidate=proposed.load_artifact()
    p=candidate.p
    build,source=proposed.proposed_build(symbolic=True)
    seed=stable=growth=0
    for address in (p.Q-2,p.Q-1):
        for faults in PAIRS:
            suffix_case(p,build,address,faults)
            seed += 1
    for address in range(p.Q):
        for faults in PAIRS:
            suffix_case(p,build,address,faults,front=address)
            stable += 1
        for delta in (1,2):
            front=address+delta
            if front > p.Q-2:
                continue
            for faults in PAIRS:
                if any(front <= address+off <= front+6 for off in faults):
                    continue
                suffix_case(p,build,address,faults,front=front)
                growth += 1
        if address%112 == 111:
            print(json.dumps(dict(through_phase=address,seed=seed,stable=stable,growth=growth)),flush=True)
    assert (seed,stable,growth) == (182,40768,18711)
    quiet=quieting_arithmetic(p)
    arithmetic=clock_and_idle(p)
    reset,info,full_source=commit_identities(p)
    late_rows=[]
    for reader in range(-3,6):
        row,observed_source=late_birth_case(p,reader)
        late_rows.append(row)
    out=ROOT/'figs/robustness'
    dependencies={key:digest(out/name) for key,name in (
        ('build_receipt_sha256','SP16_program_build.json'),
        ('programme_receipt_sha256','SP16_symbolic_schedule.json'),
        ('incorporation_receipt_sha256','SP16_buffered_incorporation_certificate.json'),
        ('encoding_receipt_sha256','SP16_encoded_certificate.json'),
        ('command_receipt_sha256','SP16_command_certificate.json'),
        ('quiet_region_receipt_sha256','SP16_quiet_region_certificate.json'))}
    receipt=dict(proposal='SP16',proposed_rule_change=False,active_G17_modified=False,SP15_modified=False,
        checker_sha256=digest(Path(__file__)),proposal_source_sha256=digest(Path(proposed.__file__)),
        proposed_candidate_sha256=candidate.digest(),proposed_netlist_sha256=candidate.comp.digest,
        helpers_sha256=digest(ROOT/'gacsca/netlist.py'),base_front_controls_source_sha256=digest(ROOT/'gacsca/rule.py'),
        full_rule_checker_sha256=digest(ROOT/'Report/proofs/check_buffered448_incorporation.py'),
        arbitrary_Age_checker_sha256=digest(ROOT/'Report/proofs/check_buffered448_arbitrary_age.py'),
        command_checker_sha256=digest(ROOT/'Report/proofs/check_buffered448_command.py'),
        buffered_service_source_sha256=digest(Path(proposed.service.__file__)),
        actual_maintenance_source_sha256=hashlib.sha256(source.encode()).hexdigest(),
        full_generated_source_sha256=full_source,late_birth_observation_generated_source_sha256=observed_source,
        **dependencies,**quiet,**arithmetic,
        last_two_Flag1_seed_cofactors=seed,stable_quiet_Flag1_suffix_cofactors=stable,
        two_cell_quiet_suffix_growth_outside_charge_zone_cofactors=growth,
        next_colony_Flag1_WF1_and_service_pressure_free_in_local_cofactors=True,
        actual_commit_workspace_zero_output_bits=reset,actual_commit_forwarded_Hold_Info_output_identities=info,
        actual_commit_reset_fields=list(RESET_FIELDS),
        J111_initial_infinite_GF_Age_halfline_and_two_quiet_colonies_required=True,
        J110_valid_initial_C_mid_period_work_seed_required=True,
        verified_upper_Flag2_output_one_required=True,
        global_E0_from_initial_seed_through_current_boundary_required=True,
        initial_packet_code_NF2_and_exterior_work_fields_arbitrary=True,
        no_future_left_or_right_boundary_prescribed=True,
        GF_Age_autonomously_correct_on_x_ge_zero_through_current_boundary=True,
        Flag1_WF1_quiet_on_C_from_state_2942_through_current_boundary=True,
        full_current_own_programme_continues_using_correct_controllers_and_E0_copy_argument=True,
        all_316_represented_upper_outputs_and_all_five_stored_copies_correct_at_current_boundary=True,
        exact_decoded_C_upper_word_equals_actual_F16_of_represented_z=True,
        histories_mail_Hold_scratch_and_front_fields_zero_at_current_boundary=True,
        boundary_Age_zero=True,
        remaining_boundary_packet_code_NF2_WF2_and_unrepresented_Info_margin_bits_outside_reset_claim=True,
        late_birth_clock_endpoint_cofactors=late_rows,
        endpoint_counterexample_input_clock=p.U-1,endpoint_current_E0_adjacent_pair=[1,2],
        endpoint_negative_GF_phase_shift=4,endpoint_negative_Age_and_fault_Age_clock=p.T_wf,
        endpoint_nonnegative_computed_GF_Age_Flag1_WF1_premises_correct=True,
        endpoint_all_old_packet_code_components_inactive=True,
        endpoint_Info_commands_at_logical_minus_one_and_three_one=True,
        endpoint_negative_three_newborns_origin_minus_four_and_single_positive_newborn_origin_zero=True,
        canonical_GF_Age_quiet_Flag1_WF1_and_late_clock_do_not_imply_birth_exclusion=True,
        endpoint_reachability_from_J111_initial_work_and_native_seed_established=False,
        full_boundary_encoding_or_NF2_packet_code_reset_established=False,
        general_damaged_seed_recovery_repeated_periods_full_upper_error_map_or_iid_threshold_established=False,
        global_reliability_established=False,
        scope='ROBUSTNESS J112: autonomous current-period GF/Age/F1/WF1 barrier and exact C decoder/work reset from stated J111 initial halfline/work seed with upper Flag2=1; late-birth endpoint shortcut refuted, pristine-seed reachability unproved')
    (out/'SP16_period_barrier_certificate.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(seed=seed,stable=stable,growth=growth,F1_quiet=2942,boundary=41919,
        reset_bits=reset,Info_identities=info,late_birth_cofactors=len(late_rows),global_reliability_established=False)),flush=True)


if __name__ == '__main__':
    main()
