#!/usr/bin/env python3
"""J109: actual SP16 local packet clearing, guard preparation and source birth.

Initial packet/code state is arbitrary. A finite GF/clock space-time
strip closes births of the relevant origins for1792 updates; their
counter/witness induction then opens all five guards. A finite initial
GF/Age field shield suffices for the strips. The command at the birth
tick is still a hypothesis; no higher-island or iid theorem is claimed.
"""
from itertools import combinations
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from gacsca.netlist import Net,at_least,const_word,mixed_age_increment
from check_buffered448_local_startup import initial_GF
from check_buffered448_arbitrary_age import GROUPS
import proposed_sparse_buffered448 as proposed

ROOTS = tuple(range(-8,9))
GF_STRIP = (-12,18)
CLOCK_STRIP = (-1,7)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def guard_visibility():
    """Every possible >=3-tag cohort has one integer root in the stated band.

    Counter equality can only remove voters. Enumerate all16 adjusted
    tag values, every tag/offset input and every matching triple. The
    only modulo alias has two available slots and cannot be a quorum.
    """
    groups = triples = ancestry = membership = 0
    for center in range(1,6):
        table = {v:[] for v in range(16)}
        for off in range(-6,7):
            for tag in range(16):
                ancestry += 1
                if tag < 5:
                    table[(tag-off)%16].append((off,tag,center+off-tag-1))
        for value,rows in table.items():
            groups += 1
            if len(rows) < 3:
                continue
            roots = {row[2] for row in rows}
            assert len(roots) == 1,(center,value,rows)
            root = next(iter(roots))
            assert center-9 <= root <= center+3
            assert root in ROOTS
            membership += 1
            for trio in combinations(rows,3):
                n = Net()
                count = [n.input(('common_count',b)) for b in range(11)]
                fixed = {row[0]:row[1] for row in trio}
                cells = {off:dict(packet_valid=1 if off in fixed else n.input((off,'valid')),
                    wf2=1 if off in fixed else n.input((off,'wf2')),
                    packet_tag=const_word(fixed[off],4) if off in fixed
                        else [n.input((off,'tag',b)) for b in range(4)],
                    packet_count=count if off in fixed else [n.input((off,'count',b)) for b in range(11)])
                    for off in range(-6,7)}
                assert proposed.guard.build(n,cells) == 1,(center,value,trio)
                triples += 1
    assert (groups,triples,ancestry,membership) == (80,500,1040,65)
    # Any root in ROOTS can birth only in[-7,13]. No remote birth can
    # inject a count-zero carrier of these roots.
    positions = 0
    for root in ROOTS:
        for y in range(root+1,root+6):
            assert -7 <= y <= 13
            positions += 1
    assert positions == 85
    return dict(guard_adjusted_tag_cases=groups,guard_tag_offset_eligibility_cases=ancestry,
        guard_possible_quorum_single_integer_origin_cases=membership,
        guard_free_other_word_common_counter_trio_cofactors=triples,
        relevant_origin_possible_birth_position_cases=positions)


def clock_exclusion(p):
    cases = 0
    for address in range(1,6):
        for faults in combinations(range(-6,7),2):
            for b in range(p.m):
                n = Net()
                opposite = 1-((p.age_code(p.T_wf)>>b)&1)
                values = [opposite if -1 <= address+off <= 7 and off not in faults
                    else n.input((off,'age_bit')) for off in range(-5,6)]
                assert at_least(n,values,6) == opposite,(address,faults,b)
                cases += 1
    assert cases == 6630
    return cases


def counter_arithmetic(lifetime):
    eligible = examined = 0
    for elapsed in range(lifetime):
        for counter in range(elapsed,1 << 11):
            examined += 1
            if counter < lifetime-1:
                assert elapsed+1 <= counter+1 <= lifetime-1
                eligible += 1
            elif elapsed == lifetime-1:
                assert counter >= lifetime-1
    assert eligible == (lifetime-1)*lifetime//2
    return examined,eligible


def main():
    candidate = proposed.load_artifact()
    p = candidate.p
    lifetime = proposed.service.original.LIFETIME
    assert lifetime == 1792 and p.T_wf-lifetime == 25665
    build,source = proposed.proposed_build(symbolic=True)
    gf = 0
    for address in range(-7,14):
        for faults in GROUPS:
            initial_GF(p,build,address,faults)
            gf += 1
    assert gf == 462
    visibility = guard_visibility()
    clock_cases = clock_exclusion(p)
    examined,eligible = counter_arithmetic(lifetime)
    assert (examined,eligible) == (2065280,1604736)
    clock_states = 0
    for t in range(lifetime+1):
        tick = p.T_wf-lifetime+t
        word = p.age_code(tick)
        assert word != 0
        assert (word == p.age_code(p.T_wf)) == (t == lifetime)
        n = Net()
        assert mixed_age_increment(n,const_word(word,p.m),p.PB,p.R,p.nb) == const_word(p.age_code(tick+1),p.m)
        clock_states += 1
    gf_shield = [GF_STRIP[0]-5*lifetime,GF_STRIP[1]+5*lifetime]
    age_shield = [CLOCK_STRIP[0]-5*lifetime,CLOCK_STRIP[1]+5*lifetime]
    for t in range(lifetime+1):
        assert gf_shield[0]+5*t <= GF_STRIP[0]
        assert gf_shield[1]-5*t >= GF_STRIP[1]
        assert age_shield[0]+5*t <= CLOCK_STRIP[0]
        assert age_shield[1]-5*t >= CLOCK_STRIP[1]
    out = ROOT/'figs/robustness'
    dependencies = {key:digest(out/name) for key,name in (
        ('build_receipt_sha256','SP16_program_build.json'),
        ('incorporation_receipt_sha256','SP16_buffered_incorporation_certificate.json'),
        ('local_startup_receipt_sha256','SP16_local_startup_certificate.json'),
        ('arbitrary_Age_receipt_sha256','SP16_arbitrary_age_certificate.json'),
        ('nonzero_clock_receipt_sha256','SP16_structural_repair_certificate.json'),
        ('guard6_receipt_sha256','packet_guard6_certificate.json'),
        ('packet_pressure_receipt_sha256','packet_pressure_certificate.json'))}
    receipt = dict(proposal='SP16',proposed_rule_change=False,active_G17_modified=False,SP15_modified=False,
        proposed_candidate_sha256=candidate.digest(),proposed_netlist_sha256=candidate.comp.digest,
        proposal_source_sha256=digest(Path(proposed.__file__)),checker_sha256=digest(Path(__file__)),
        helpers_sha256=digest(ROOT/'gacsca/netlist.py'),
        local_startup_checker_sha256=digest(ROOT/'Report/proofs/check_buffered448_local_startup.py'),
        arbitrary_Age_checker_sha256=digest(ROOT/'Report/proofs/check_buffered448_arbitrary_age.py'),
        buffered_service_source_sha256=digest(Path(proposed.service.__file__)),
        full_generated_source_sha256=hashlib.sha256(proposed.actual_net(p)[1].encode()).hexdigest(),
        actual_maintenance_source_sha256=hashlib.sha256(source.encode()).hexdigest(),**dependencies,
        initial_packet_code_and_other_component_fields_globally_arbitrary=True,
        packet_birth_free_relevant_origin_counter_lower_bound_induction=True,
        relevant_packet_origins=list(ROOTS),relevant_birth_sites_inclusive=[-7,13],
        minimum_counter_by_elapsed_state_until_expiry=True,
        counter_lower_bound_pairs_examined=examined,eligible_counter_increment_bound_cases=eligible,
        relevant_computed_packets_all_inactive_by_state=lifetime,
        relevant_births_in_preparation_window_closed_by_actual_GF_clock_law=True,
        preparation_GF_input_strip_inclusive=list(GF_STRIP),preparation_clock_strip_inclusive=list(CLOCK_STRIP),
        preparation_computed_GF_clock_strips_required_for_states_zero_through=lifetime,
        preparation_reference_initial_tick=p.T_wf-lifetime,
        preparation_reference_clock_states_and_increments_checked=clock_states,
        birth_band_GF_free_Age_flags_pressure_cofactors=gf,
        nine_site_unequal_clock_bit_free_other_Age_cofactors=clock_cases,**visibility,
        guard_retention_zero_follows_from_missing_relevant_origins_and_at_most_two_raw_faults=True,
        J108_actual_birth_output_algebra_applies_after_proved_guard_and_retention_zero=True,
        command_at_preparation_end_fivefold_logical_three_required=True,
        proper_source_delivered_at_computed_state=lifetime+1,
        proper_source_holders=list(range(1,6)),proper_source_count=0,
        proper_source_persists_through_computed_state=2*lifetime,
        proper_source_clears_at_computed_state=2*lifetime+1,
        initialized_packet_inactive_guard_global_clock_or_right_boundary_not_required_for_source_theorem=True,
        arbitrary_initial_remote_counts_and_later_exterior_births_allowed=True,
        global_24_24_separated_singleton_adjacent_pair_E0_required=True,
        finite_initial_GF_shield_suffices_for_GF_strip=True,finite_initial_nonzero_Age_shield_suffices_for_clock_strip=True,
        finite_initial_GF_shield_inclusive=gf_shield,finite_initial_Age_shield_inclusive=age_shield,
        finite_initial_GF_shield_cells=gf_shield[1]-gf_shield[0]+1,
        finite_initial_Age_shield_cells=age_shield[1]-age_shield[0]+1,
        field_cone_strip_containment_states_checked=lifetime+1,
        optional_colony_GF_at_preparation_end_and_prescribed_right_GF_Age_required_for_Age_repair=True,
        optional_colony_Flag2_one_computed_state=lifetime+246,
        optional_colony_Age_reference_computed_state=lifetime+694,
        optional_GF_recovered_Age_persist_through_computed_state=2*lifetime,
        optional_quiet_right_Flag1_required_for_extended_quieting=True,
        optional_WF1_source_free_computed_state=lifetime+898,
        optional_Flag1_quiet_computed_state=lifetime+1150,
        optional_GF_Age_Flag1_WF1_current_work_period_boundary_state=lifetime+p.U-p.T_wf,
        command_authentication_and_GF_clock_strip_delivery_from_arbitrary_higher_errors_established=False,
        arbitrary_colony_GF_repair_autonomous_boundary_full_upper_map_or_iid_threshold_established=False,
        global_reliability_established=False,
        scope='actual SP16 local packet/guard preparation from arbitrary components, finite field shields and conditional source delivery; optional J107 Age repair; ROBUSTNESS J109')
    (out/'SP16_guard_preparation_certificate.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(packet_clear=lifetime,actual_source=lifetime+1,
        GF_cofactors=gf,clock_cofactors=clock_cases,guard_trio_cofactors=visibility['guard_free_other_word_common_counter_trio_cofactors'],
        optional_Age_repair=lifetime+694,global_reliability_established=False)),flush=True)


if __name__ == '__main__':
    main()
