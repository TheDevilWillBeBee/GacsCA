#!/usr/bin/env python3
"""J107: actual SP16 canonical-GF/arbitrary-Age repair with later births.

Exact local and full-rule cofactor premises for the displayed prefix/
suffix induction. No global clock or externally imposed no-birth premise.
Initial canonical colony GF, proper origin0 packet/older initial packets,
E0 and a prescribed right GF/Age boundary remain hypotheses. No iid claim.
"""
from itertools import combinations
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from gacsca.netlist import Net,const_word,w_mux,mixed_age_increment
from check_framed_birth_origin import restriction
from check_buffered448_incorporation import full_net
import proposed_sparse_buffered448 as proposed

GROUPS = ((),) + tuple((y,) for y in range(-5,6)) + tuple((y,y+1) for y in range(-5,5))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def raw_cells(n,p,address,faults=(),known_f2=(),quiet=False,reference_age=None):
    cells = {}
    for off in range(-5,9):
        y = address+off
        good = off not in faults
        canonical = good and y >= 0
        age = reference_age if canonical and reference_age is not None else [n.input((off,'age',b)) for b in range(p.m)]
        cells[off] = dict(
            addr=const_word(y%p.Q,p.k) if canonical else [n.input((off,'addr',b)) for b in range(p.k)],
            age=age, f2=1 if good and off in known_f2 else n.input((off,'f2')),
            f1=0 if canonical and quiet else n.input((off,'f1')),
            wf1=0 if canonical and quiet else n.input((off,'wf1')),wf2=n.input((off,'wf2')))
    return cells


def invoke(build,n,cells,p,pressure):
    return build(n,cells,p.k,p.m,Q=p.Q,nb=p.nb,radix=p.R,pos_bits=p.PB,service_force=pressure)


def GF_closure(p,build,address,faults):
    n = Net()
    cells = raw_cells(n,p,address,faults)
    force = 1 if address < 5 else n.input(('arbitrary_pressure',))
    result = invoke(build,n,cells,p,force)
    assert result['addr'] == const_word(address,p.k),(address,faults)


def stable_prefix(p,build,address,faults):
    n = Net()
    cells = raw_cells(n,p,address,faults,known_f2=range(-5,1))
    result = invoke(build,n,cells,p,n.input(('arbitrary_pressure',)))
    assert result['f2'] == 1,(address,faults)
    assert result['addr'] == const_word(address,p.k),(address,faults)


def grow_prefix(p,build,address,faults,support):
    assert not set(faults).intersection(support)
    n = Net()
    cells = raw_cells(n,p,address,faults,known_f2=support)
    result = invoke(build,n,cells,p,n.input(('arbitrary_pressure',)))
    assert result['f2'] == 1,(address,faults,support)
    assert result['addr'] == const_word(address,p.k),(address,faults,support)


def boundary_quiet(p,build,address,faults):
    n = Net()
    age = [n.input(('reference_age',b)) for b in range(p.m)]
    cells = raw_cells(n,p,address,faults,quiet=True,reference_age=age)
    result = invoke(build,n,cells,p,n.input(('arbitrary_pressure',)))
    assert result['f1'] == 0,(address,faults)
    assert result['addr'] == const_word(address,p.k),(address,faults)
    assert result['age_now'] == age,(address,faults)
    assert result['age'] == mixed_age_increment(n,age,p.PB,p.R,p.nb),(address,faults)


def boundary_clean_retreat(p,build,address,gap):
    n = Net()
    age = [n.input(('reference_age',b)) for b in range(p.m)]
    cells = raw_cells(n,p,address,quiet=True,reference_age=age)
    for off in range(-5,9):
        y = address+off
        cells[off]['f1'] = 0 if y >= address+gap else n.input((off,'f1'))
    result = invoke(build,n,cells,p,n.input(('arbitrary_pressure',)))
    assert result['f1'] == 0,(address,gap)
    assert result['addr'] == const_word(address,p.k)
    assert result['age_now'] == age


def actual_birth_law(p):
    base,_ = proposed.proposed_build()
    def cut(n,*args,**kwargs):
        result = base(n,*args,**kwargs)
        result['addr'] = [n.input(('computed_GF_cut',b)) for b in range(p.k)]
        return result
    n,source = full_net(p,maintenance=cut,observe=True)
    cells = {off:dict(packet_tag=[n.input_node['x',off,'packet_tag',b] for b in range(4)],
        packet_valid=n.input_node['x',off,'packet_valid',0],packet_count=[n.input_node['x',off,'packet_count',b] for b in range(11)],
        wf2=n.input_node['x',off,'wf2',0],flag_valid=n.input_node['x',off,'service_valid',0],
        flag_position=[n.input_node['x',off,'service_position',b] for b in range(9)],
        flag_count=[n.input_node['x',off,'service_count',b] for b in range(11)]) for off in range(-5,6)}
    retained = proposed.service.build(n,cells)
    cut_nodes = [n.input_node['computed_GF_cut',b] for b in range(p.k)]
    length = len(n.kind)
    dependent = [False]*length
    for node in cut_nodes:
        dependent[node] = True
    for node in range(length):
        if n.gate[node] is not None:
            _,a,b = n.gate[node]
            dependent[node] = dependent[a] or dependent[b]
    absent = identities = 0
    for word in range(1 << p.k):
        cf = restriction(n,cut_nodes,word,length,dependent)
        born = cf(n.outputs['proof','birth'])
        if not 1 <= word <= 5:
            assert born == 0,word
            absent += 1
        expected = dict(wf2=n.OR(born,retained['wf2']),packet_valid=n.OR(born,retained['packet_valid']),
            packet_tag=w_mux(n,born,const_word((word-1)%16,4),retained['packet_tag']),
            packet_count=w_mux(n,born,[0]*11,retained['packet_count']),
            service_valid=retained['flag_valid'],service_position=retained['flag_position'],service_count=retained['flag_count'])
        for field,value in expected.items():
            for b,node in enumerate(value if isinstance(value,list) else [value]):
                assert cf(n.outputs['y',field,b]) == node,(word,field,b)
                identities += 1
    return absent,identities,hashlib.sha256(source.encode()).hexdigest()


def guard_trios():
    count = 0
    for center in range(1,6):
        for trio in combinations(range(1,6),3):
            n = Net()
            age = [n.input(('common_count',b)) for b in range(11)]
            cells = {}
            for off in range(-6,7):
                y = center+off
                cells[off] = dict(packet_valid=1 if y in trio else n.input((off,'packet_valid')),
                    wf2=1 if y in trio else n.input((off,'wf2')),
                    packet_tag=const_word(y-1,4) if y in trio else [n.input((off,'packet_tag',b)) for b in range(4)],
                    packet_count=age if y in trio else [n.input((off,'packet_count',b)) for b in range(11)])
            assert proposed.guard.build(n,cells) == 1,(center,trio)
            count += 1
    return count


def frontier_bound():
    # A charged row meets[b-3,b]. The selected front advances by0 or2,
    # so two charged sites at a gap<=10 have |dx|<=2*gap+3<24.
    exclusions = 0
    for gap in range(1,11):
        for advancement in range(0,2*gap+1,2):
            for old_offset in range(-3,1):
                for new_offset in range(-3,1):
                    assert abs(advancement+new_offset-old_offset) < 24
                    assert gap < 24
                    exclusions += 1
    n = 244
    bad = (n+10)//11
    assert 6+2*n-2*bad >= 447
    assert 6+2*(n-1)-2*((n-1+10)//11) < 447
    return exclusions,1+n,1+n+448


def main():
    candidate = proposed.load_artifact()
    p = candidate.p
    build,source = proposed.proposed_build(symbolic=True)
    assert source == proposed.service.original.maintenance_build()[1]
    counts = dict(canonical_GF_free_Age=0,stable_Flag2_prefix_free_Age=0,two_site_prefix_growth_free_Age=0)
    for address in range(p.Q):
        for faults in GROUPS:
            GF_closure(p,build,address,faults)
            counts['canonical_GF_free_Age'] += 1
            if address >= 7:
                stable_prefix(p,build,address,faults)
                counts['stable_Flag2_prefix_free_Age'] += 1
        if address % 112 == 111:
            print(json.dumps(dict(through_address=address,counts=counts)),flush=True)
    for front in range(6,p.Q-1):
        for delta,support in ((1,tuple(range(-4,0))),(2,tuple(range(-5,-1)))):
            if front+delta >= p.Q:
                continue
            for faults in GROUPS:
                if not set(faults).intersection(support):
                    grow_prefix(p,build,front+delta,faults,support)
                    counts['two_site_prefix_growth_free_Age'] += 1
    quiet = clean_retreat = 0
    for address in range(5):
        for faults in combinations(range(-5,9),2):
            boundary_quiet(p,build,address,faults)
            quiet += 1
        for gap in (1,2):
            boundary_clean_retreat(p,build,address,gap)
            clean_retreat += 1
    absent,identities,cut_hash = actual_birth_law(p)
    guards = guard_trios()
    exclusion,prefix_deadline,age_deadline = frontier_bound()
    assert counts == dict(canonical_GF_free_Age=9856,stable_Flag2_prefix_free_Age=9702,two_site_prefix_growth_free_Age=11893)
    assert (quiet,clean_retreat,absent,identities,guards,prefix_deadline,age_deadline) == (455,10,507,19456,50,245,693)
    assert age_deadline < 897 < 1149 < 1792
    out = ROOT/'figs/robustness'
    dependencies = {key:digest(out/name) for key,name in (
        ('build_receipt_sha256','SP16_program_build.json'),
        ('incorporation_receipt_sha256','SP16_buffered_incorporation_certificate.json'),
        ('guard6_receipt_sha256','packet_guard6_certificate.json'),
        ('packet_pressure_receipt_sha256','packet_pressure_certificate.json'),
        ('RF_suffix_receipt_sha256','framed_service_certificate.json'),
        ('flag_retreat_receipt_sha256','SP13_encoded_e0_certificate.json'))}
    receipt = dict(proposal='SP16',proposed_rule_change=False,active_G17_modified=False,SP15_modified=False,
        checker_sha256=digest(Path(__file__)),proposal_source_sha256=digest(Path(proposed.__file__)),
        proposed_candidate_sha256=candidate.digest(),proposed_netlist_sha256=candidate.comp.digest,
        buffered_service_source_sha256=digest(Path(proposed.service.__file__)),
        birth_restriction_helper_sha256=digest(ROOT/'Report/proofs/check_framed_birth_origin.py'),
        full_rule_checker_sha256=digest(ROOT/'Report/proofs/check_buffered448_incorporation.py'),
        helpers_sha256=digest(ROOT/'gacsca/netlist.py'),actual_maintenance_source_sha256=hashlib.sha256(source.encode()).hexdigest(),
        full_generated_source_sha256=hashlib.sha256(proposed.actual_net(p)[1].encode()).hexdigest(),
        GF_cut_observation_generated_source_sha256=cut_hash,**dependencies,
        all_other_initial_Age_bits_globally_arbitrary_except_right_reference=True,
        initial_GF_canonical_on_true_colony_and_prescribed_right_required=True,
        initialized_origin_zero_packet_one_through_five_count_zero_required=True,
        other_initial_eligible_packet_counters_at_least_one_required=True,
        all_initial_coded_fields_arbitrary_including_count_zero=True,
        arbitrary_later_actual_births_in_left_and_right_exteriors_allowed=True,
        no_global_clock_or_separate_no_birth_premise=True,
        actual_births_inside_true_colony_blocked_through_active_packet_window=True,
        every_raw_GF_Age_ordinary_flag_workspace_data_instruction_fault_payload_arbitrary=True,
        globally_24_24_separated_singleton_or_adjacent_pair_whole_word_E0_required=True,
        prescribed_right_canonical_GF_and_legal_reference_Age_required=True,
        local_cofactors=counts,leading_quiet_free_exterior_Age_GF_pressure_cofactors=quiet,
        leading_clean_one_two_retreat_free_exterior_Age_cofactors=clean_retreat,
        cut_GF_words=512,birth_closed_GF_words=absent,full_component_birth_output_identities=identities,
        five_protected_birth_center_surviving_trio_guard_cofactors=guards,
        prefix_charge_window_relative_to_front=[-3,0],prefix_blocking_group_minimum_tick_gap=11,
        frontier_E0_exclusion_arithmetic_cases=exclusion,
        whole_true_colony_computed_Flag2_one_by_state=prefix_deadline,
        every_true_colony_computed_Age_reference_by_state=age_deadline,
        GF_canonical_through_state_1791_and_Age_reference_from_693_through_1791=True,
        optional_post_birth_reference_clock_tick=p.T_wf+1,
        optional_quiet_right_Flag1_and_post_birth_reference_required_for_Flag1_quiet=True,
        optional_WF1_source_free_computed_state=897,optional_Flag1_quiet_computed_state=1149,
        optional_GF_Age_Flag1_WF1_persist_to_current_reference_work_period_boundary=True,
        optional_current_reference_work_period_boundary_state=p.U-(p.T_wf+1),
        NF2_packet_code_and_simulation_data_quieting_or_reset_outside_conclusion=True,
        general_arbitrary_GF_or_authentic_source_delivery_established=False,
        autonomous_right_boundary_or_full_upper_map_or_iid_threshold_established=False,
        global_reliability_established=False,
        scope='actual SP16 canonical-GF/arbitrary-Age E0 source-driven prefix245/Age693 despite exterior births; optional NF1 quiet1149 on post-birth right reference; ROBUSTNESS J107')
    (out/'SP16_arbitrary_age_certificate.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(counts=counts,boundary_quiet=quiet,birth_identities=identities,
        prefix_deadline=prefix_deadline,Age_deadline=age_deadline,global_reliability_established=False)),flush=True)


if __name__ == '__main__':
    main()
