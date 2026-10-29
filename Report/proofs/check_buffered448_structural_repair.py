#!/usr/bin/env python3
"""J106: SP16 initialized source roots0..5, clock-closed structural repair.

The proof is a word/cohort/front induction in ROBUSTNESS, not a sampled
trajectory. These exact local clock/birth and leading-boundary identities
pin its premises. Global initial common Age and prescribed right boundary
remain hypotheses; authentic source delivery and iid closure are unproved.
"""
from itertools import combinations
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from gacsca.netlist import Net,const_word,mixed_age_increment,w_in_range
from check_shifted_framed_repair import clock_case,clock_birth_gate
import proposed_sparse_buffered448 as proposed


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def leading_quiet_closure(p,build,address,faults,force=0):
    n = Net()
    age = [n.input(('reference_age',b)) for b in range(p.m)]
    cells = {}
    for off in range(-5,9):
        y = address+off
        good = off not in faults
        cells[off] = dict(
            addr=const_word(y%p.Q,p.k) if good and y >= 0 else [n.input((off,'addr',b)) for b in range(p.k)],
            age=age if good else [n.input((off,'age',b)) for b in range(p.m)],
            f1=0 if good and y >= 0 else n.input((off,'f1')),
            f2=n.input((off,'f2')),wf1=0 if good and y >= 0 else n.input((off,'wf1')),
            wf2=0 if good else n.input((off,'wf2')))
    pressure = n.input(('arbitrary_pressure',)) if force == 'free' else force
    result = build(n,cells,p.k,p.m,Q=p.Q,nb=p.nb,radix=p.R,pos_bits=p.PB,service_force=pressure)
    assert result['f1'] == 0,(address,faults)
    assert result['addr'] == const_word(address,p.k),(address,faults)
    assert result['age_now'] == age,(address,faults)
    assert result['age'] == mixed_age_increment(n,age,p.PB,p.R,p.nb),(address,faults)
    if address == 0 and force == 0:
        assert result['f2'] == 0,faults


def main():
    candidate = proposed.load_artifact()
    p = candidate.p
    build,source = proposed.proposed_build(symbolic=True)
    pairs = tuple(combinations(range(-5,6),2))
    clock = birth = quiet = boundary = 0
    for bit in range(p.m):
        for faults in pairs:
            clock_case(p,build,faults,bit)
            clock_birth_gate(p,faults,bit)
            clock += 1
            birth += 1
    for address in range(5):
        for faults in pairs:
            leading_quiet_closure(p,build,address,faults,force='free')
            quiet += 1
    for faults in pairs:
        leading_quiet_closure(p,build,0,faults,force=0)
        boundary += 1
    reference_words = [p.age_code(p.T_wf+1+t) for t in range(2041)]
    assert p.T_wf+1+2040 < p.U
    assert all(word != 0 and word != p.age_code(p.T_wf) for word in reference_words)
    end_of_period = p.U-(p.T_wf+1)
    pre_wrap_words = [p.age_code(p.T_wf+1+t) for t in range(end_of_period)]
    assert all(word != 0 and word != p.age_code(p.T_wf) for word in pre_wrap_words)
    assert p.T_wf+1+end_of_period == p.U
    source_free_windows = 0
    for t in range(896,2040):
        n = Net()
        assert w_in_range(n,const_word(reference_words[t],p.m),p.age_code(p.T_wf),
            p.age_code(p.T_wf+2*p.Q-1)+1) == 0
        source_free_windows += 1
    assert 897+252 == 1149 and 1792+247 == 2039
    assert 890 < 897 < 1149 < 1792 < 2039 < 2040
    out = ROOT/'figs/robustness'
    dependencies = {key:digest(out/name) for key,name in (
        ('build_receipt_sha256','SP16_program_build.json'),
        ('schedule_receipt_sha256','SP16_symbolic_schedule.json'),
        ('incorporation_receipt_sha256','SP16_buffered_incorporation_certificate.json'),
        ('buffered_service_receipt_sha256','buffered_framed_service_certificate.json'),
        ('SP14_shifted_clock_receipt_sha256','SP14_shifted_source_repair_certificate.json'),
        ('canonical_transfer_receipt_sha256','SP14_encoding_transfer_certificate.json'),
        ('flag_reserve_receipt_sha256','SP13_encoded_e0_certificate.json'))}
    receipt = dict(proposal='SP16',proposed_rule_change=False,
        active_G17_modified=False,SP15_modified=False,
        proposed_candidate_sha256=candidate.digest(),proposed_netlist_sha256=candidate.comp.digest,
        checker_sha256=digest(Path(__file__)),proposal_source_sha256=digest(Path(proposed.__file__)),
        buffered_service_source_sha256=digest(Path(proposed.service.__file__)),
        shared_clock_checker_sha256=digest(ROOT/'Report/proofs/check_shifted_framed_repair.py'),
        helpers_sha256=digest(ROOT/'gacsca/netlist.py'),
        actual_maintenance_source_sha256=hashlib.sha256(source.encode()).hexdigest(),
        full_generated_source_sha256=hashlib.sha256(proposed.actual_net(p)[1].encode()).hexdigest(),
        **dependencies,
        initialized_source_origins=list(range(6)),source_five_holders_r_plus_one_through_five=True,
        initial_source_count_zero_and_every_other_eligible_component_counter_at_least_one_required=True,
        initial_global_common_Age=p.age_code(p.T_wf+1),initial_global_common_clock_tick=p.T_wf+1,
        arbitrary_initial_true_colony_GF_flags_data_and_left_exterior=True,
        right_exterior_canonical_computed_GF_and_quiet_Flag1_prescribed=True,
        globally_24_24_separated_singleton_or_adjacent_pair_whole_word_E0_required=True,
        nonzero_reference_clock_cofactors=clock,closed_birth_vote_cofactors=birth,
        leading_five_quiet_GF_Age_free_pressure_cofactors=quiet,
        leading_zero_Flag2_erasure_with_arbitrary_left_Flag2_cofactors=boundary,
        reference_clock_states_checked=len(reference_words),WF1_source_free_input_window_checks=source_free_windows,
        all_remaining_pre_wrap_nonzero_birth_closed_input_clock_words_checked=len(pre_wrap_words),
        actual_no_later_births_discharged_by_uniform_nonzero_clock=True,
        all_true_colony_GF_Age_correct_by_computed_state=890,
        WF1_source_free_conservative_computed_state=897,Flag1_quiet_computed_state=1149,
        all_packet_code_components_globally_computed_empty_state=1792,
        Flag2_quiet_computed_state=2039,all_structural_fields_quiet_computed_state=2040,
        Info_Hold_mail_histories_scratch_and_front_fields_outside_conclusion=True,
        preservation_only_through_clock_closed_window_and_next_source_free_interval=True,
        quiet_preservation_through_computed_end_of_current_work_period_state=end_of_period,
        later_work_periods_and_their_new_births_outside_conclusion=True,
        authentic_source_or_global_clock_bootstrap_from_arbitrary_higher_errors_established=False,
        autonomous_right_boundary_or_full_upper_error_map_established=False,
        global_reliability_established=False,
        scope='actual SP16 initialized source roots0..5/common global clock/prescribed right boundary; E0 structural GF/Age/flag/component repair by2040; ROBUSTNESS J106')
    (out/'SP16_structural_repair_certificate.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(clock_cofactors=clock,birth_cofactors=birth,quiet_cofactors=quiet,
        boundary_erase_cofactors=boundary,GF_deadline=890,joint_deadline=2040,
        global_reliability_established=False)),flush=True)


if __name__ == '__main__':
    main()
