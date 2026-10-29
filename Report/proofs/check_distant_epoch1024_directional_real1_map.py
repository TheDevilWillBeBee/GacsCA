#!/usr/bin/env python3
"""Exact SP28 arbitrary-upper-state fixed-pair map counterexample, J147.

Physical composition is in SP28_DIRECTIONAL_REAL1_MAP.md. Checks a
literal local injection, actual gather controls/ROM identities and all
25 upper output bits. Not an intact-hierarchy or iid counterexample.
"""
from pathlib import Path
import hashlib
import json
import sys
import time
import numpy as np
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from gacsca.netlist import Net
from gacsca.gray_errors import classify
import proposed_sparse_distant_epoch1024 as proposed


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def upper_bit(p, holder, field, bit):
    if field == 'addr':
        return ((holder % p.Q) >> bit) & 1
    if field == 'info':
        primary = holder+bit-2
        if primary in range(-2, 3) and holder != 0:
            others = [x for x in range(primary-2, primary+3) if x != 0]
            return int(holder in others[:2])
    return 0


def local_injection(p, primaries, tick):
    bits = checks = 0
    for reader in range(min(primaries)-10, max(primaries)+11):
        class BoundNet(Net):
            def input(self, key):
                if key[0] == 'x':
                    _, off, field, bit = key
                    holder = reader+off
                    if field == 'addr':
                        return ((holder % p.Q) >> bit) & 1
                    if field == 'age':
                        return (p.age_code(tick) >> bit) & 1
                    if field in ('f1', 'wf1'):
                        return 0
                    if field in ('info', 'mr', 'ml'):
                        primary = holder+bit-2
                        return int(field != 'ml' and primary in primaries)
                return super().input(key)
        n, _ = proposed.full_net(p, BoundNet)
        assert [n.outputs['y','addr',b] for b in range(p.k)] == [(reader%p.Q >> b)&1 for b in range(p.k)]
        assert n.outputs['y','f1',0] == 0
        checks += 1
        for a in primaries:
            for field, target, expected in (('info',a,1), ('mr',a+8,1), ('ml',a-8,0)):
                slot = target-reader
                if -2 <= slot <= 2:
                    assert n.outputs['y',field,slot+2] == expected, (reader,field,a)
                    bits += 1
    assert (checks, bits) == (25, 75)
    return checks, bits


def actual_upper_outputs(candidate):
    p, comp = candidate.p, candidate.comp
    receivers = list(range(-4, 5))
    values = {}
    for name in comp.inputs:
        if name[0] == 'x':
            _, off, field, bit = name
            data = []
            for receiver in receivers:
                source = receiver+off
                value = upper_bit(p,source,field,bit)
                if source == 0 and field == 'info':
                    value = int(receiver >= 0)
                data.append(value)
            values[name] = np.array(data,dtype=bool)
        else:
            values[name] = np.zeros(len(receivers),dtype=bool)
    outputs = comp.evaluate(values,bool)
    selector = sum(outputs['psel',b].astype(np.int64)<<b for b in range(p.PW))
    address = sum(outputs['laddr',b].astype(np.int64)<<b for b in range(p.k))
    words = candidate.rom[address,selector]
    assert not words.any()
    for b in range(p.IW):
        values['I',b] = ((words>>b)&1).astype(bool)
    outputs = comp.evaluate(values,bool)
    groups = {}
    assert not outputs['y','f1',0].any()
    assert not outputs['y','f2',0].any()
    for b in range(p.k):
        assert np.array_equal(outputs['y','addr',b],
                              np.asarray([((j % p.Q) >> b)&1 for j in receivers],dtype=bool))
    for primary in range(-2, 3):
        data = []
        for holder in range(primary-2,primary+3):
            slot = primary-holder
            bit = int(outputs['y','info',slot+2][receivers.index(holder)])
            assert bit == int(holder >= 0), (primary,holder,bit)
            data.append(bit)
        groups[str(primary)] = data
    assert groups['0'] == [0,0,1,1,1] and groups['2'] == [1,1,1,1,1]
    return groups, address.tolist(), selector.tolist()


def main():
    started = time.monotonic()
    out = ROOT/'figs/robustness'
    candidate = proposed.load_artifact()
    p = candidate.p
    primaries = [int(candidate.layout[candidate.row['info',b]]) for b in range(5)]
    assert primaries == [92,93,94,95,96]
    tick = p.gathers_q[1]*p.Q+1
    assert tick == 10241
    error = [(x,tick) for x in range(min(primaries)-2,max(primaries)+3)]
    classification = classify(error,Q=p.Q,U=p.U,sep=16)
    assert classification['level1'] and classification['level0'] == 0
    assert len(error) == 9 and classification['extent'] == (9,1)
    readers, bits = local_injection(p,primaries,tick)
    groups, keys, selectors = actual_upper_outputs(candidate)
    tuple_references = 0
    for receiver in range(-4,5):
        offset = -receiver
        for a in primaries:
            for gather in p.gathers_q:
                if offset:
                    capture = gather*p.Q+abs(offset)*(p.Q//8)+1
                    shifts = capture-(gather*p.Q+1)
                    assert 8*shifts == abs(offset)*p.Q
                    assert capture < p.E0
                tuple_references += 1
    assert tuple_references == 135
    # For arbitrary A, P0 coherence leaves only A={-2,-1}. Check all
    # intersections of an adjacent pair with the five observed holders.
    possible = []
    for start in range(-3,3):
        remaining = [int(x>=0) for x in range(-2,3) if x not in (start,start+1)]
        if len(set(remaining)) == 1:
            possible.append([start,start+1])
    assert possible == [[-2,-1]]
    minus_one_outside = [groups['-1'][holder+3] for holder in range(-3,2)
                         if holder not in possible[0]]
    assert minus_one_outside == [0,1,1]
    assert not set(possible[0]).intersection(range(0,5))
    assert sum(upper_bit(p,x,'info',4-x) for x in range(0,5)) == 2
    encoded = json.loads((out/'SP28_encoded_certificate.json').read_text())
    programme = json.loads((out/'SP28_symbolic_schedule.json').read_text())
    native = json.loads((out/'SP28_native_certificate.json').read_text())
    assert encoded['proposed_candidate_sha256'] == programme['proposed_candidate_sha256'] == candidate.digest()
    assert native['proposed_netlist_sha256'] == candidate.comp.digest
    assert native['all_time_computed_GF_Age_under_E0_plus_real1_proved']
    assert programme['final_hold_equalities'] == 842 and programme['early_flag_equalities'] == 2
    assert encoded['physical_transport_certificate']['all_requested_gather_coordinates_proved']
    proof = ROOT/'Report/proofs/SP28_DIRECTIONAL_REAL1_MAP.md'
    result = dict(
        proposal='SP28', proposed_rule_change=False, active_G17_modified=False,
        checker_sha256=digest(Path(__file__)), written_proof_sha256=digest(proof),
        proposal_source_sha256=digest(Path(proposed.__file__)),
        proposed_candidate_sha256=candidate.digest(),proposed_netlist_sha256=candidate.comp.digest,
        Q=p.Q,U=p.U,width=candidate.W,radius=37,lambda0=24,error_class_separation=16,
        error_input_tick=tick,error_locations=[list(x) for x in error],
        error_location_classification=classification,upper_source_cell=0,
        altered_upper_fields=['info[0]','info[1]','info[2]','info[3]','info[4]'],
        lower_represented_Info_primaries=primaries,
        error_payload='Info=MR=1 and ML=0 on all five copies of each primary92..96; every other bit unchanged',
        actual_local_transition_readers_checked=readers,
        literal_Info_MR_ML_injection_output_equalities=bits,
        upper_tuple_receivers_checked=9,actual_upper_Info_output_equalities=25,
        physical_three_gather_reference_coordinates_checked=tuple_references,
        actual_upper_ROM_lookup_addresses=keys,actual_upper_ROM_lookup_selectors=selectors,
        decoded_upper_Info_primary_output_groups=groups,
        sole_pair_allowed_by_primary_zero_coherence=possible[0],
        primary_two_original_vote=0,primary_two_actual_decoded_output=1,
        dependencies_sha256={name:digest(out/name) for name in (
            'SP28_encoded_certificate.json','SP28_native_certificate.json',
            'SP28_symbolic_schedule.json','SP28_encoding_family_certificate.json')},
        error_classifier_sha256=digest(ROOT/'gacsca/gray_errors.py'),
        immutable_ROM_artifact_sha256=digest(out/'SP28_program.npz'),
        initial_complete_lower_encoding_of_arbitrary_upper_state=True,
        initial_upper_Info_deliberately_incoherent=True,
        initial_recursive_intact_hierarchy=False,
        no_later_errors=True,physical_boundary_composition_proved=True,
        unrestricted_arbitrary_upper_fixed_adjacent_pair_input_output_map_refuted=True,
        all_possible_upper_replacement_payloads_in_any_one_adjacent_pair_excluded=True,
        independent_adjacent_input_and_output_exception_pairs_excluded=True,
        native_GF_Age_E0_real1_theorem_invalidated=False,
        E0_encoded_period_theorem_invalidated=False,
        intact_hierarchy_reachability_proved=False,
        Gray_or_Gacs_reliability_refuted=False,iid_unreliability_proved=False,
        smallest_sufficient_reliability_change_proved=False,
        global_reliability_established=False,numerical_U_tick_trajectory_used=False,
        seconds=time.monotonic()-started,
        scope='J147 actual SP28 one-period boundary witness from arbitrary upper z with incoherent Info, one9-site real1 core; every fixed adjacent-pair input/output map excluded; not recursively intact/iid counterexample',
    )
    (out/'SP28_directional_real1_map_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(readers=readers,local_equalities=bits,upper_outputs=25,
                         real1=classification['level1'],groups=groups,
                         unrestricted_fixed_pair_map_refuted=True,iid=False,
                         seconds=result['seconds'])),flush=True)


if __name__ == '__main__':
    main()
