#!/usr/bin/env python3
"""J108: actual SP16 source delivery from finite GF/clock/command strips.

No packet is initialized. Clock support -1..7, aligned GF, a fivefold
command and an empty guard strip are still hypotheses, not consequences
of arbitrary higher errors. J94's initial counter condition localizes to
overlapping packet roots; J107 then gives arbitrary-Age repair.
"""
from itertools import combinations
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from gacsca.netlist import Net,const_word,at_least,w_eq_const
from check_shifted_halfline import dominant_bit
from check_buffered448_incorporation import full_net
from check_buffered448_arbitrary_age import GROUPS
import proposed_sparse_buffered448 as proposed

CLOCK = tuple(range(-1,8))
GUARD = tuple(range(-5,12))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_birth(p,address,faults):
    class BoundNet(Net):
        def input(self,key):
            if key[0] == 'x':
                _,off,field,bit = key
                y = address+off
                if off not in faults:
                    if field == 'addr' and y >= -8:
                        return ((y%p.Q)>>bit)&1
                    if field == 'age' and y in CLOCK:
                        return (p.age_code(p.T_wf)>>bit)&1
                    if field == 'packet_valid' and y in GUARD:
                        return 0
                    if field == 'info' and y+bit-2 == 3:
                        return super().input(('command',))
            return super().input(key)
    n,source = full_net(p,net_class=BoundNet,majority=dominant_bit,
        maintenance=proposed.proposed_build(symbolic=True)[0],observe=True)
    command = n.input(('command',))
    assert n.outputs['proof','guard'] == 0,(address,faults,'guard')
    assert n.outputs['proof','birth'] == command,(address,faults,'birth')
    assert n.outputs['y','wf2',0] == command,(address,faults,'wf2')
    assert n.outputs['y','packet_valid',0] == command,(address,faults,'valid')
    for b in range(4):
        assert n.outputs['y','packet_tag',b] == (command if ((address-1)>>b)&1 else 0),(address,faults,b)
    assert all(n.outputs['y','packet_count',b] == 0 for b in range(11)),(address,faults,'count')
    assert [n.outputs['y','addr',b] for b in range(p.k)] == const_word(address,p.k)
    return hashlib.sha256(source.encode()).hexdigest()


def initial_GF(p,build,address,faults):
    n = Net()
    cells = {}
    for off in range(-5,9):
        cells[off] = dict(addr=const_word((address+off)%p.Q,p.k) if off not in faults
            else [n.input((off,'addr',b)) for b in range(p.k)],
            age=[n.input((off,'age',b)) for b in range(p.m)],
            **{field:n.input((off,field)) for field in ('f1','f2','wf1','wf2')})
    result = build(n,cells,p.k,p.m,Q=p.Q,nb=p.nb,radix=p.R,pos_bits=p.PB,
        service_force=n.input(('arbitrary_pressure',)))
    assert result['addr'] == const_word(address%p.Q,p.k),(address,faults)


def support_audit(p):
    universe = tuple(range(-4,11))
    windows = [set(range(x-5,x+6)) for x in range(1,6)]
    admissible = []
    witness = hashlib.sha256()
    excluded = 0
    bit = next(b for b in range(p.m) if (p.age_code(p.T_wf)>>b)&1)
    for mask in range(1 << len(universe)):
        known = {y for b,y in enumerate(universe) if (mask>>b)&1}
        counts = [len(known & window) for window in windows]
        if min(counts) >= 8:
            admissible.append(tuple(sorted(known)))
            continue
        index = next(i for i,c in enumerate(counts) if c < 8)
        voters = sorted(known & windows[index])
        if len(voters) == 7:
            first = next(y for y in voters if y+1 in voters)
            faults = (first,first+1)
        elif len(voters) == 6:
            faults = (voters[0],)
        else:
            faults = ()
        survivors = len(set(voters)-set(faults))
        assert survivors <= 5
        # Set this 1-bit of every unknown/fault word to 0. The actual
        # at-least-six repair-clock vote disagrees with the birth clock.
        n = Net()
        assert at_least(n,[int(y in known and y not in faults) for y in sorted(windows[index])],6) == 0
        witness.update(bytes((mask & 255,mask >> 8,index+1,survivors,
            len(faults),faults[0]+5 if faults else 0)))
        excluded += 1
    minimum = min(map(len,admissible))
    minimal = [list(s) for s in admissible if len(s) == minimum]
    assert minimum == 9 and len(minimal) == 10 and list(CLOCK) in minimal
    assert [s for s in minimal if s[-1]-s[0]+1 == 9] == [list(CLOCK)]
    vote_cases = 0
    for address in range(1,6):
        for faults in combinations(range(-6,7),2):
            n = Net()
            vote = []
            for b in range(p.m):
                values = [((p.age_code(p.T_wf)>>b)&1) if address+off in CLOCK and off not in faults
                    else n.input((off,'age',b)) for off in range(-5,6)]
                vote.append(at_least(n,values,6))
            assert w_eq_const(n,vote,p.age_code(p.T_wf)) == 1,(address,faults)
            vote_cases += 1
    return dict(static_clock_support_masks_checked=1 << len(universe),
        sufficient_static_clock_supports=len(admissible),excluded_static_clock_supports=excluded,
        excluded_masks_clock_vote_witness_sha256=witness.hexdigest(),witness_birth_clock_one_bit=bit,
        minimum_static_clock_support_size=minimum,all_minimum_static_clock_supports=minimal,
        minimum_contiguous_static_clock_support=list(CLOCK),nine_site_free_other_Age_vote_cofactors=vote_cases)


def local_origin_audit():
    ancestry = retained = 0
    for tag in range(5):
        for off in range(-5,6):
            value = (tag-off)%16
            if value < 5:
                assert value == tag-off
                # x-v-1 == (x+off)-tag-1 for every integer x.
                assert -value-1 == off-tag-1
                retained += 1
            ancestry += 1
    roots = [r for r in range(-20,21) if set(range(r+1,r+6)) & set(range(1,6))]
    assert roots == list(range(-4,5))
    slots = 0
    for root in roots:
        for y in range(root+1,root+6):
            assert -3 <= y <= 9
            # Canonical computed GF permits birth only at1..5 and the
            # newborn integer origin is then y-GF=0.
            if 1 <= y%448 <= 5:
                assert y == y%448
                assert y-y%448 == 0
            slots += 1
    return ancestry,retained,roots,slots


def main():
    candidate = proposed.load_artifact()
    p = candidate.p
    build,source = proposed.proposed_build(symbolic=True)
    gf = 0
    for address in range(-3,5):
        for faults in GROUPS:
            initial_GF(p,build,address,faults)
            gf += 1
    support = support_audit(p)
    births = 0
    observed = None
    for address in range(1,6):
        for faults in combinations(range(-6,7),2):
            observed = source_birth(p,address,faults)
            births += 1
        print(json.dumps(dict(through_source_holder=address,full_rule_birth_cofactors=births)),flush=True)
    ancestry,retained,roots,slots = local_origin_audit()
    assert (gf,births,ancestry,retained,slots) == (176,390,55,25,45)
    out = ROOT/'figs/robustness'
    dependencies = {key:digest(out/name) for key,name in (
        ('build_receipt_sha256','SP16_program_build.json'),
        ('incorporation_receipt_sha256','SP16_buffered_incorporation_certificate.json'),
        ('arbitrary_Age_receipt_sha256','SP16_arbitrary_age_certificate.json'),
        ('guard6_receipt_sha256','packet_guard6_certificate.json'),
        ('packet_pressure_receipt_sha256','packet_pressure_certificate.json'))}
    receipt = dict(proposal='SP16',proposed_rule_change=False,active_G17_modified=False,SP15_modified=False,
        proposed_candidate_sha256=candidate.digest(),proposed_netlist_sha256=candidate.comp.digest,
        checker_sha256=digest(Path(__file__)),proposal_source_sha256=digest(Path(proposed.__file__)),
        helpers_sha256=digest(ROOT/'gacsca/netlist.py'),
        full_rule_checker_sha256=digest(ROOT/'Report/proofs/check_buffered448_incorporation.py'),
        dominant_bit_helper_sha256=digest(ROOT/'Report/proofs/check_shifted_halfline.py'),
        arbitrary_Age_checker_sha256=digest(ROOT/'Report/proofs/check_buffered448_arbitrary_age.py'),
        buffered_service_source_sha256=digest(Path(proposed.service.__file__)),
        full_generated_source_sha256=hashlib.sha256(proposed.actual_net(p)[1].encode()).hexdigest(),
        actual_maintenance_source_sha256=hashlib.sha256(source.encode()).hexdigest(),
        proof_observation_generated_source_sha256=observed,**dependencies,**support,
        initial_computed_GF_canonical_on_minus_eight_through_447_required=True,
        prescribed_right_canonical_GF_and_reference_Age_from_birth_tick_required=True,
        known_birth_clock_tick=p.T_wf,known_birth_clock_sites=list(CLOCK),
        fivefold_Info_command_at_logical_three_required=True,
        initial_packet_valid_zero_sites=list(GUARD),initial_packet_other_bits_and_all_codes_free=True,
        all_other_initial_Ages_GF_left_exterior_flags_data_and_instructions_free_with_stated_strips=True,
        no_initialized_packet_or_global_clock_or_separate_no_birth_premise=True,
        all_remote_initial_eligible_packet_counters_free_including_zero=True,
        global_24_24_separated_singleton_adjacent_pair_E0_required=True,
        proper_source_delivered_at_computed_state=1,proper_source_holders=list(range(1,6)),proper_source_count=0,
        full_rule_free_other_Age_component_and_command_birth_cofactors=births,
        initial_step_leading_and_dangerous_negative_GF_free_Age_cofactors=gf,
        packet_no_wrap_ancestry_cases=ancestry,valid_no_wrap_cases=retained,
        initial_older_counter_premise_only_for_overlapping_origins=roots,
        overlapping_root_possible_birth_position_cases=slots,
        no_nonproper_overlapping_count_zero_packet_at_state_one=True,
        all_computed_true_colony_Flag2_one_by_state=246,
        all_computed_true_colony_Age_reference_by_state=694,
        GF_and_recovered_Age_persist_through_state=1792,
        optional_post_birth_quiet_right_Flag1_required=True,
        optional_WF1_source_free_state=898,optional_Flag1_quiet_state=1150,
        optional_GF_Age_Flag1_WF1_preserve_to_current_work_period_boundary_state=p.U-p.T_wf,
        source_command_clock_GF_and_empty_guard_strip_bootstrap_from_arbitrary_errors_established=False,
        autonomous_right_boundary_full_upper_map_or_iid_threshold_established=False,
        global_reliability_established=False,
        scope='actual SP16 finite-strip source startup and localized J94/J107 Age repair; nine-site clock support minimum in stated adversarial-static-support class; ROBUSTNESS J108')
    (out/'SP16_local_startup_certificate.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(birth_cofactors=births,clock_support_minimum=support['minimum_static_clock_support_size'],
        minimum_supports=len(support['all_minimum_static_clock_supports']),Age_deadline=694,
        global_reliability_established=False)),flush=True)


if __name__ == '__main__':
    main()
