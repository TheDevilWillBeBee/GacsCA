#!/usr/bin/env python3
"""J102: SP15 origin-five source leaves three leading GF cells unrepaired.

Exact seam cofactors and an origin/count induction, not a sampled trace.
The initialized source and wrong left half-line are prescribed; no claim
of reachability from an intact hierarchy or of iid unreliability is made.
No CA, registered candidate, or existing proposal is changed.
"""
from itertools import combinations
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from gacsca.netlist import Net, const_word, mixed_age_increment, w_eq_const, w_add_const, w_eq, at_least
import proposed_sparse_guarded_pressure448 as proposed
from check_guarded_pressure448_incorporation import full_net

SOURCE_ROOT = 5
HOLDERS = tuple(range(6, 11))
LAST_INPUT_STATE = 1791


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def component_cells(n, x):
    """All possible root-five carriers; each coded alive/count is free.

    Initially only the five proper packets are present. Stored-component
    origin preservation gives exactly this overapproximation thereafter.
    Invalid coded words' payloads are irrelevant and may be taken in-frame.
    """
    count = [n.input(('packet_count', b)) for b in range(11)]
    cells = {}
    for off in range(-5, 6):
        y = x + off
        alive = y in HOLDERS
        cells[off] = dict(wf2=int(alive), packet_valid=int(alive),
            packet_tag=const_word(y - SOURCE_ROOT - 1 if alive else 0, 4),
            packet_count=count, flag_valid=n.input((y, 'flag_valid')) if 5 <= y <= 452 else 0,
            flag_position=const_word((y-SOURCE_ROOT) % 512, 9),
            flag_count=[n.input((y, 'flag_count', b)) for b in range(11)])
    return cells


def force_cases():
    negative = positive = 0
    for x in range(-8, 6):
        n = Net()
        result = proposed.service.build(n, component_cells(n, x))
        assert result['service_force'] == int(x >= 3), x
        if x <= 2:
            negative += 1
        else:
            positive += 1
    return negative, positive


def seam_cases(p):
    build, _ = proposed.proposed_build(symbolic=True)
    gf = f1 = f2 = clocks = 0
    for x in range(-8, 14):
        n = Net()
        age = [n.input(('reference_age', b)) for b in range(p.m)]
        cells = {}
        for off in range(-5, 9):
            y = x + off
            cells[off] = dict(addr=const_word((y-1 if y <= 2 else y) % p.Q, p.k),
                age=age, f1=n.input((y, 'f1')) if y < 0 else int(y <= 5),
                f2=0 if y <= 2 else n.input((y, 'f2')),
                wf1=0, wf2=int(y in HOLDERS))
        pressure = int(x >= 3) if x <= 5 else n.input(('positive_pressure',))
        result = build(n, cells, p.k, p.m, Q=p.Q, nb=p.nb, radix=p.R,
            pos_bits=p.PB, service_force=pressure)
        assert result['addr'] == const_word((x-1 if x <= 2 else x) % p.Q, p.k), x
        gf += 1
        assert result['age_now'] == age, x
        assert result['age'] == mixed_age_increment(n, age, p.PB, p.R, p.nb), x
        clocks += 1
        if x >= 0:
            assert result['f1'] == int(x <= 5), x
            f1 += 1
        if x <= 2:
            assert result['f2'] == 0, x
            f2 += 1
    return dict(GF=gf, common_clock=clocks, nonnegative_Flag1=f1, nonpositive_and_leading_Flag2=f2)


def leading_pressure_override(p):
    """A pressure-only counterfactual repairs this clean seam in one update."""
    build, _ = proposed.proposed_build(symbolic=True)
    for x in range(3):
        n = Net()
        age = [n.input(('reference_age',b)) for b in range(p.m)]
        cells = {}
        for off in range(-5,9):
            y = x+off
            cells[off] = dict(addr=const_word((y-1 if y <= 2 else y)%p.Q,p.k),
                age=age, f1=n.input((y,'f1')) if y < 0 else int(y <= 5),
                f2=0 if y <= 2 else n.input((y,'f2')), wf1=0, wf2=int(y in HOLDERS))
        result = build(n,cells,p.k,p.m,Q=p.Q,nb=p.nb,radix=p.R,pos_bits=p.PB,service_force=1)
        assert result['addr'] == const_word(x,p.k)
        assert result['f2'] == 1
        assert result['age_now'] == age
    return 3


def actual_initial_seam(p):
    """Full-rule, one-update seam checks with other raw fields free.

    Info copies are zero; clock is after the signal/initial birth. These
    bind full-rule wiring to the induction; other data/work are arbitrary.
    """
    start = p.T_wf + 1
    cases = 0
    for x in range(-1, 7):
        class BoundNet(Net):
            def input(self, key):
                if key[0] == 'x':
                    _, off, field, bit = key
                    y = x + off
                    if field == 'addr':
                        return (((y-1 if y <= 2 else y) % p.Q) >> bit)&1
                    if field == 'age':
                        return (p.age_code(start) >> bit)&1
                    if field == 'info':
                        return 0
                    if field == 'f1' and y >= 0:
                        return int(y <= 5)
                    if field == 'f2' and y <= 2:
                        return 0
                    if field == 'wf1':
                        return 0
                    if field in ('wf2', 'packet_valid'):
                        return int(y in HOLDERS)
                    if field == 'packet_tag':
                        return (((y-6) if y in HOLDERS else 0) >> bit)&1
                    if field in ('packet_count','service_valid','service_position','service_count'):
                        return 0
                return super().input(key)
        n, _ = full_net(p, net_class=BoundNet,
            maintenance=proposed.proposed_build(symbolic=True)[0], observe=True)
        expected_gf = (x-1 if x <= 2 else x) % p.Q
        assert [n.outputs['y','addr',b] for b in range(p.k)] == const_word(expected_gf,p.k), x
        assert [n.outputs['y','age',b] for b in range(p.m)] == const_word(p.age_code(start+1),p.m), x
        assert n.outputs['proof','birth'] == 0, x
        assert n.outputs['y','wf1',0] == 0, x
        assert all(n.outputs['y','info',b] == 0 for b in range(5)), x
        if x >= 0:
            assert n.outputs['y','f1',0] == int(x <= 5), x
        if x <= 2:
            assert n.outputs['y','f2',0] == 0, x
        cases += 1
    return cases


def clock_window(p):
    start = p.T_wf + 1
    assert start + LAST_INPUT_STATE + 1 < p.U
    for t in range(LAST_INPUT_STATE+1):
        n = Net()
        age = const_word(p.age_code(start+t),p.m)
        # Literal generated-rule birth/special/commit predicates. With
        # Info=0, sim_r=0 and hence WF1=0 even during its active window.
        assert w_eq_const(n, age, p.age_code(p.T_wf)) == 0
        assert w_eq_const(n, age, p.age_code(p.T_sig)) == 0
        assert w_eq_const(n, age, p.age_code(p.U-1)) == 0
        assert mixed_age_increment(n, age, p.PB, p.R, p.nb) == const_word(p.age_code(start+t+1),p.m)
    return start, LAST_INPUT_STATE+1


def raw_pressure(n, radius, proper):
    """Hypothetical pressure-only detection; no stored output changed here."""
    cells = {}
    count = [n.input(('common_count', b)) for b in range(11)]
    for off in range(-radius, radius+1):
        cells[off] = dict(alive=int(off in proper),
            tag=const_word(off-6 if off in proper else 0,4), count=count)
    adjusted = {off:w_add_const(n,c['tag'],(-off)%16) for off,c in cells.items()}
    matches = []
    for off,c in cells.items():
        votes = [n.all([d['alive'],w_eq(n,adjusted[off],adjusted[j]),w_eq(n,c['count'],d['count'])])
            for j,d in cells.items()]
        matches.append(n.AND(c['alive'],at_least(n,votes,3)))
    return n.any(matches)


def minimal_direct_pressure_window():
    # At true leading cell0, root5 occupies positive offsets6..10.
    # A clean triple is first visible at radius8. Under arbitrary two
    # holder erasures, all five must be visible: radius10 is necessary.
    checks = 0
    for radius in range(5,11):
        n = Net()
        assert raw_pressure(n,radius,HOLDERS) == int(radius >= 8)
        checks += 1
    for radius in range(5,11):
        for erased in combinations(HOLDERS,2):
            survivors = tuple(y for y in HOLDERS if y not in erased)
            n = Net()
            expected = len([y for y in survivors if y <= radius]) >= 3
            assert raw_pressure(n,radius,survivors) == int(expected)
            checks += 1
        if radius < 10:
            visible = tuple(y for y in HOLDERS if y <= radius)
            erased = visible[:min(2,len(visible))]
            assert len(visible)-len(erased) < 3
    return checks


def main():
    candidate = proposed.load_artifact()
    p = candidate.p
    negative,positive = force_cases()
    seam = seam_cases(p)
    override_cases = leading_pressure_override(p)
    full_cases = actual_initial_seam(p)
    start,clock_cases = clock_window(p)
    direct_cases = minimal_direct_pressure_window()
    primary_addresses = [a for a in range(p.lo,p.hi) if a not in proposed.reserved_cells(p)]
    added_forward_ranks = tuple(range(7,11))
    extra_raw_history_bits = 2*5*len(added_forward_ranks)
    assert (len(primary_addresses), candidate.W, extra_raw_history_bits) == (330,316,40)
    assert candidate.W + extra_raw_history_bits > len(primary_addresses)
    out = ROOT/'figs/robustness'
    receipt = dict(proposal='SP15', proposed_rule_change=False,
        active_G17_modified=False, SP15_modified=False,
        checker_sha256=digest(Path(__file__)), proposal_source_sha256=digest(Path(proposed.__file__)),
        proposed_candidate_sha256=candidate.digest(), proposed_netlist_sha256=candidate.comp.digest,
        pressure_source_sha256=digest(Path(proposed.service.__file__)),
        base_rule_source_sha256=digest(ROOT/'gacsca/rule_g.py'), helpers_sha256=digest(ROOT/'gacsca/netlist.py'),
        actual_maintenance_source_sha256=hashlib.sha256(proposed.proposed_build()[1].encode()).hexdigest(),
        full_generated_source_sha256=hashlib.sha256(proposed.actual_net(p)[1].encode()).hexdigest(),
        full_rule_checker_sha256=digest(ROOT/'Report/proofs/check_guarded_pressure448_incorporation.py'),
        incorporation_receipt_sha256=digest(out/'SP15_guarded_pressure_incorporation_certificate.json'),
        source_guard_receipt_sha256=digest(out/'packet_guard6_certificate.json'),
        source_frame_receipt_sha256=digest(out/'framed_service_certificate.json'),
        source_root=SOURCE_ROOT, source_holders=list(HOLDERS), initial_source_count=0,
        every_other_initial_component_word_empty=True, subsequent_errors_empty=True,
        arbitrary_GF_phase_minus_one_left_halfline_through_site_two_required=True,
        GF_canonical_from_site_three=True,
        initial_Flag1_one_on_zero_through_five_zero_on_sites_at_least_six=True,
        initial_Flag2_zero_on_sites_at_most_two=True,
        negative_Flag1_and_positive_Flag2_and_non_Info_data_work_free=True,
        all_Info_copies_initially_zero_and_invariant=True,
        initial_global_common_clock_tick=start, input_clock_states_checked=clock_cases,
        negative_pressure_free_code_cofactors=negative, positive_pressure_free_code_cofactors=positive,
        seam_cofactors=seam, actual_full_rule_initial_seam_cofactors=full_cases,
        birth_closed_and_actual_WF1_zero_through_all_1792_updates=True,
        unrepaired_true_colony_GF_sites=[0,1,2], wrong_GF_words=[447,0,1],
        wrong_GF_persists_through_computed_state=1792,
        initialized_source_included_in_counterexample=True,
        general_origin_five_extension_of_J90_refuted=True,
        direct_pressure_radius_minimum_clean=8, direct_pressure_radius_minimum_two_erasures=10,
        direct_pressure_window_cofactors=direct_cases,
        hypothetical_leading_pressure_repairs_clean_seam_in_one_update_cofactors=override_cases,
        radius_changes_are_hypothetical_pressure_only_and_not_implemented=True,
        present_primary_addresses=len(primary_addresses), present_raw_width=candidate.W,
        hypothetical_asymmetric_forward_pressure_additional_ranks=list(added_forward_ranks),
        hypothetical_same_layout_extra_raw_history_bits=extra_raw_history_bits,
        hypothetical_same_layout_raw_width=candidate.W+extra_raw_history_bits,
        sufficient_general_repair_change_or_minimal_reliability_change_established=False,
        authentic_birth_reachability_from_pristine_hierarchy_established=False,
        iid_unreliability_established=False, global_reliability_established=False,
        scope='exact initialized origin5 source boundary obstruction in unchanged SP15 for1792 clean updates; local direct-pressure radius lower bounds only; ROBUSTNESS J102')
    (out/'SP15_displaced_pressure_boundary_certificate.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(seam=seam, full_cases=full_cases, pressure_zero_cases=negative,
        pressure_one_cases=positive, clock_cases=clock_cases, direct_pressure_cases=direct_cases,
        global_reliability_established=False)),flush=True)


if __name__ == '__main__':
    main()
