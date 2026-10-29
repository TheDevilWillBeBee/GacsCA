#!/usr/bin/env python3
"""J111: actual SP16 quiet native-region preparation and autonomous GF/Age.

Local exact Boolean cofactors and arithmetic, not full noisy trajectories.
Pre-window fields are canonical GF/common Age on a colony-aligned
interval, with native F1/WF1 quiet in only the first two colonies.
Its left edge is fixed; right GF/Age contraction is5.
A valid C work seed is still needed for the command. A fresh actual
origin0 packet subsequently seals a canonical GF/Age right half-line.
No general damaged-island recovery, full upper map or iid threshold.
"""
from itertools import combinations
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from gacsca.netlist import Net,const_word,mixed_age_increment,w_in_range
from check_buffered448_arbitrary_age import raw_cells,invoke
from check_buffered448_incorporation import full_net
from check_buffered448_command import read,forwarded_hold
from check_shifted_halfline import dominant_bit
from check_right_barrier import check_dominance_primitive
import proposed_sparse_buffered448 as proposed

PAIRS = tuple(combinations(range(-5,9),2))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def native_case(p,build,address,faults,quiet,two_mode=False):
    n = Net()
    age = [n.input(('common_age',b)) for b in range(p.m)]
    cells = raw_cells(n,p,address,faults,quiet=quiet,reference_age=age)
    if two_mode:
        assert not quiet
        for off in range(-5,0):
            if address+off < 0 and off not in faults:
                cells[off]['addr'] = const_word((address+off)%p.Q,p.k)
                cells[off]['age'] = age
    # Quiet F1/WF1 are needed only in the reader's own true colony.
    # Ordinary flags of the next colony remain free, even in quiet cases.
    for off in range(-5,9):
        if address+off >= p.Q:
            cells[off]['f1'] = n.input((off,'f1'))
            cells[off]['wf1'] = n.input((off,'wf1'))
    pressure = n.input(('arbitrary_pressure',)) if quiet or two_mode or address >= 5 else 1
    result = invoke(build,n,cells,p,pressure)
    if quiet:
        assert result['f1'] == 0,(address,faults,'F1')
    assert result['addr'] == const_word(address,p.k),(address,faults,'GF')
    assert result['age_now'] == age,(address,faults,'current_Age')
    assert result['age'] == mixed_age_increment(n,age,p.PB,p.R,p.nb),(address,faults,'next_Age')


def WF1_identities(p):
    count = 0
    for address in range(p.Q-5,p.Q):
        def controller(n,*args,**kwargs):
            age = [n.input(('proof_common_Age',b)) for b in range(p.m)]
            return dict(addr=const_word(address,p.k),age_now=age,
                age=mixed_age_increment(n,age,p.PB,p.R,p.nb),f1=0,
                f2=n.input(('proof_free_F2',)))
        n,source = full_net(p,maintenance=controller)
        age = [n.input(('proof_common_Age',b)) for b in range(p.m)]
        window = w_in_range(n,age,p.age_code(p.T_wf),p.age_code(p.T_wf+2*p.Q-1)+1)
        expected = n.AND(window,read(n,p,address,p.Q-3,'info'))
        assert n.outputs['y','wf1',0] == expected,address
        count += 1
    assert count == 5
    return count,hashlib.sha256(source.encode()).hexdigest()


def quiet_data_votes(p):
    counts = {}
    pairs = tuple(combinations(range(-5,6),2))
    for stage,primary in [('entry',p.lo),('carry',p.lo),('load',p.lo),('transfer',p.lo-1),('signal',3)]:
        source = primary+1 if stage == 'transfer' else primary
        field = 'ml' if stage in ('transfer','signal') else 'hold'
        checked = 0
        for reader in range(primary-2,primary+3):
            for faults in pairs:
                class BoundNet(Net):
                    def input(self,key):
                        if key[0] == 'x':
                            _,off,f,b = key
                            y = reader+off
                            width = proposed.logical_width(f,p)
                            logical = y+b//width-2
                            if logical == source and source-2 <= y <= source+2 and off not in faults:
                                if stage == 'entry':
                                    if f == 'pend': return 1
                                    if f == 'pkind': return 0
                                    if f == 'pval': return super().input(('command',))
                                else:
                                    if f == field: return super().input(('command',))
                                    if f == 'pend' and stage in ('carry','load'): return 0
                        return super().input(key)
                n = BoundNet()
                # Native computed F1=0 makes the actual keep factor1,
                # including a currently overwritten output holder.
                result = forwarded_hold(n,p,reader,source,dominant_bit) if stage in ('entry','carry','load') else read(n,p,reader,source,'ml',majority=dominant_bit)
                assert result == n.input(('command',)),(stage,reader,faults)
                checked += 1
        assert checked == 275
        counts[stage] = checked
    return counts


def interval_arithmetic(p):
    left,right,L = -p.Q,p.Q+4+5*1792,1792
    assert (left,right) == (-448,9412)
    assert right-left+1 == 22*p.Q+5
    clocks = containment = increments = 0
    for t in range(L):
        word = p.age_code(25665+t)
        n = Net()
        assert w_in_range(n,const_word(word,p.m),p.age_code(p.T_wf),p.age_code(p.T_wf+2*p.Q-1)+1) == 0
        assert mixed_age_increment(n,const_word(word,p.m),p.PB,p.R,p.nb) == const_word(p.age_code(25666+t),p.m)
        clocks += 1
        increments += 1
    for t in range(L+1):
        assert left <= -12 and right-5*t >= p.Q+4
        assert left <= -1 and right-5*t >= 7
        assert left <= 30 and right-5*t >= 417
        containment += 1
    phases = 0
    for address in range(p.Q):
        for off in (*range(-5,0),*range(1,6)):
            assert ((address+off)%p.Q-off)%p.Q == address
            phases += 1
    assert (clocks,containment,increments,phases) == (1792,1793,1792,4480)
    return dict(initial_finite_GF_Age_interval_inclusive=[left,right],
        initial_finite_GF_Age_interval_cells=right-left+1,
        initial_finite_GF_Age_interval_complete_colonies=22,
        initial_finite_GF_Age_interval_extra_cells=5,
        initial_quiet_Flag1_WF1_interval_inclusive=[left,p.Q-1],initial_quiet_Flag1_WF1_cells=2*p.Q,
        initial_GF_Age_right_reserve_beyond_C_cells=right-(p.Q-1),
        fixed_left_edge_is_a_true_colony_boundary=True,right_interval_contraction_sites_per_update=5,
        pre_window_clock_exclusion_checks=clocks,native_field_interval_containment_states=containment,
        pre_window_reference_clock_increment_checks=increments,canonical_adjusted_GF_phase_cases=phases)


def main():
    candidate = proposed.load_artifact()
    p = candidate.p
    build,source = proposed.proposed_build(symbolic=True)
    assert len(PAIRS) == 91
    quiet = sealed = 0
    for address in range(p.Q):
        for faults in PAIRS:
            native_case(p,build,address,faults,True)
            quiet += 1
            native_case(p,build,address,faults,False)
            sealed += 1
        if address%64 == 63:
            print(json.dumps(dict(through_phase=address,quiet_native_cofactors=quiet,sealed_GF_Age_cofactors=sealed)),flush=True)
    assert quiet == sealed == 40768
    two_mode_extra = 0
    for address in range(5):
        for faults in PAIRS:
            native_case(p,build,address,faults,False,two_mode=True)
            two_mode_extra += 1
    assert two_mode_extra == 455
    assert check_dominance_primitive() == 160
    wf,full_source = WF1_identities(p)
    data = quiet_data_votes(p)
    arithmetic = interval_arithmetic(p)
    out = ROOT/'figs/robustness'
    dependencies = {key:digest(out/name) for key,name in (
        ('build_receipt_sha256','SP16_program_build.json'),
        ('programme_receipt_sha256','SP16_symbolic_schedule.json'),
        ('incorporation_receipt_sha256','SP16_buffered_incorporation_certificate.json'),
        ('preparation_receipt_sha256','SP16_guard_preparation_certificate.json'),
        ('command_receipt_sha256','SP16_command_certificate.json'),
        ('guard6_receipt_sha256','packet_guard6_certificate.json'),
        ('packet_pressure_receipt_sha256','packet_pressure_certificate.json'))}
    receipt = dict(proposal='SP16',proposed_rule_change=False,active_G17_modified=False,SP15_modified=False,
        checker_sha256=digest(Path(__file__)),proposal_source_sha256=digest(Path(proposed.__file__)),
        proposed_candidate_sha256=candidate.digest(),proposed_netlist_sha256=candidate.comp.digest,
        helpers_sha256=digest(ROOT/'gacsca/netlist.py'),
        full_rule_checker_sha256=digest(ROOT/'Report/proofs/check_buffered448_incorporation.py'),
        arbitrary_Age_checker_sha256=digest(ROOT/'Report/proofs/check_buffered448_arbitrary_age.py'),
        command_checker_sha256=digest(ROOT/'Report/proofs/check_buffered448_command.py'),
        dominant_majority_helper_sha256=digest(ROOT/'Report/proofs/check_right_barrier.py'),
        dominant_bit_helper_sha256=digest(ROOT/'Report/proofs/check_shifted_halfline.py'),
        buffered_service_source_sha256=digest(Path(proposed.service.__file__)),
        actual_maintenance_source_sha256=hashlib.sha256(source.encode()).hexdigest(),
        full_generated_source_sha256=full_source,**dependencies,**arithmetic,
        quiet_native_GF_Age_Flag1_cofactors=quiet,source_sealed_GF_Age_free_flags_cofactors=sealed,
        two_mode_GF_Age_cofactors=40768,two_mode_first_five_phase_extra_cofactors=two_mode_extra,
        free_next_colony_ordinary_flags_in_all_cofactors=True,
        majority_dominance_truth_assignments_checked=160,
        projected_actual_WF1_window_Info_output_identities=wf,
        quiet_copied_data_votes_including_current_output_holder_overwrites=data,
        pre_window_density_at_most_two_current_whole_word_errors_per_fourteen_sites_suffices=True,
        no_temporal_separation_needed_for_preparation_and_command=True,
        initial_GF_Age_canonical_on_displayed_native_interval_required=True,
        initial_Flag1_WF1_quiet_only_in_first_two_colonies_required=True,
        valid_C_mid_period_work_seed_of_J110_still_required=True,
        GF_Age_correct_on_fixed_left_shrinking_right_interval_through_state=1792,
        Flag1_WF1_quiet_in_first_two_colonies_through_state=1792,
        future_exterior_boundary_or_canonical_fields_left_of_minus_Q_not_prescribed=True,
        exact_all_five_special_Info_command_copies_at_computed_state=1792,
        actual_proper_source_born_iff_verified_upper_Flag2_one_at_computed_state=1793,
        initial_packet_code_counter_and_NF2_fields_arbitrary=True,
        global_E0_after_birth_required_for_guard6_packet_persistence=True,
        proper_source_when_one_persists_through_state=3584,
        infinite_initial_canonical_GF_Age_halfline_and_two_quiet_colonies_variant_also_proved=True,
        when_command_one_halfline_variant_GF_Age_autonomously_correct_on_x_ge_zero_through_state=3584,
        no_future_right_GF_Age_boundary_prescribed_for_halfline_active_source_conclusion=True,
        post_birth_native_Flag1_WF1_quiet_not_asserted=True,
        general_damaged_seed_recovery_autonomous_full_period_reset_upper_map_or_iid_threshold_established=False,
        global_reliability_established=False,
        scope='ROBUSTNESS J111: pre-window quiet native-region invariant with arbitrary left exterior; verified command/source from valid mid-period C work seed; autonomous GF/Age right-halfline barrier during protected source lifetime')
    (out/'SP16_quiet_region_certificate.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(quiet_cofactors=quiet,sealed_cofactors=sealed,WF1_identities=wf,
        data_cofactors=data,initial_native_cells=arithmetic['initial_finite_GF_Age_interval_cells'],
        source_state=1793,autonomous_active_source_GF_Age_through=3584,global_reliability_established=False)),flush=True)


if __name__ == '__main__':
    main()
