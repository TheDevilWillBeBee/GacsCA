#!/usr/bin/env python3
"""SP28 half-line physical-step interfaces, ROBUSTNESS J145.

The proof uses exact existing local/transport/programme certificates;
this pins their identities and checks all geographic margins. No sampled
trajectories, arbitrary-data recovery or iid theorem are asserted.
"""
from pathlib import Path
import hashlib
import json
import sys
import time
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import proposed_sparse_distant_epoch1024 as proposed


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    started = time.monotonic()
    out = ROOT/'figs/robustness'
    p = proposed.parameters()
    table = proposed.dependency_table(p)
    encoded = json.loads((out/'SP28_encoded_certificate.json').read_text())
    family = json.loads((out/'SP28_encoding_family_certificate.json').read_text())
    native = json.loads((out/'SP28_epoch_halfline_certificate.json').read_text())
    fast = json.loads((out/'SP28_fast_native_front_certificate.json').read_text())
    canonical = json.loads((out/'SP28_canonicalization_certificate.json').read_text())
    programme = json.loads((out/'SP28_symbolic_schedule.json').read_text())
    front = json.loads((out/'SP28_front_certificate.json').read_text())
    sha = encoded['proposed_netlist_sha256']
    for receipt in (family, native, fast, canonical, programme, front):
        assert receipt['proposed_netlist_sha256'] == sha
    assert family['broad_encoding_contracts_to_narrow_E28_after_one_period_under_actual_E0']
    assert native['stable_quiet_Flag1_suffix_cofactors'] == 93184
    assert native['all_period_three_colony_native_halfline_expansion_proved']
    assert fast['all_period_nine_colony_autonomous_native_halfline_expansion_proved']
    assert canonical['fivefold_computed_boundary_layout_with_independent_auxiliary_flags_proved']
    assert not canonical['complete_computed_boundary_encoding_of_some_upper_halfline_proved']
    assert programme['final_hold_equalities'] == 842
    assert encoded['complete_encoded_noiseless_and_all_period_E0_simulation_proved']
    assert (min(row['address'] for row in table), max(row['address'] for row in table)) == (59, 900)
    r = 37
    assert min(row['address'] for row in table)-2-r == 20 > 0
    traces = 0
    for row in table:
        a = row['address']
        for offset in row['offsets']:
            destination = r*p.Q+a
            source = destination+offset*p.Q
            assert source >= a >= 59
            # Between source and destination, the speed-eight path is
            # monotone. Its smallest five-holder/native margin is at
            # the smaller endpoint; bound it without a time-cone proxy.
            assert min(source, destination)-2-r >= 20
            for gather in p.gathers_q:
                capture = gather*p.Q+abs(offset)*(p.Q//8)+1
                assert capture < p.E0 < p.T_wf
                traces += 1
    assert traces == 25284
    minimum_center = p.lo-p.H
    maximum_center = minimum_center+(p.PL-1)+(p.fronts-1)*p.delta
    assert (minimum_center, maximum_center) == (38, 985)
    assert (minimum_center-r, maximum_center+r) == (1, 1022)
    assert p.lo-r >= 0 and p.hi-1+r < p.Q
    earliest_load, left_load, right_load = p.courier_ticks()
    signal = p.T_sig
    assert earliest_load == min(left_load, right_load)
    assert p.T_sig+1 == p.T_wf
    assert left_load+1+p.lo-3 == signal
    assert right_load+1+p.Q-3-(p.hi-1) == signal
    for endpoint in (3, p.Q-3, p.lo, p.hi-1):
        assert endpoint-2 >= 0 and endpoint+2 < p.Q
    assert encoded['all_computed_Flag1_quiet_clock'] < p.U-1
    strip = r+9
    assert strip == 46
    proof = ROOT/'Report/proofs/SP28_HALFLINE_STEP.md'
    receipt = dict(
        proposal='SP28', proposed_rule_change=False, additional_rule_change=False,
        active_G17_modified=False, checker_sha256=digest(Path(__file__)),
        written_proof_sha256=digest(proof),
        proposal_source_sha256=digest(Path(proposed.__file__)),
        full_generated_source_sha256=hashlib.sha256(proposed.generated_source(p).encode()).hexdigest(),
        proposed_netlist_sha256=sha,
        proposed_candidate_sha256=encoded['proposed_candidate_sha256'],
        dependencies_sha256={name:digest(out/name) for name in (
            'SP28_encoded_certificate.json', 'SP28_encoding_family_certificate.json',
            'SP28_epoch_halfline_certificate.json', 'SP28_fast_native_front_certificate.json',
            'SP28_canonicalization_certificate.json', 'SP28_symbolic_schedule.json',
            'SP28_front_certificate.json')},
        Q=p.Q, U=p.U, radius=r, width=proposed.width(p),
        gathered_reference_trace_margins_checked=traces,
        smallest_required_normal_Info_primary_relative_to_native_boundary=59,
        smallest_required_normal_Info_holder_relative_to_native_boundary=57,
        smallest_required_native_sample_relative_to_native_boundary=20,
        actual_front_center_phase_bounds=[minimum_center, maximum_center],
        full_radius_front_footprint_phase_bounds=[minimum_center-r, maximum_center+r],
        upper_interior_margin_colonies=r,
        recovered_halfline_native_growth_per_period_colonies=9,
        moving_unsupported_upper_transition_strip_colonies=strip,
        physical_one_period_interior_halfline_simulation_proved=True,
        autonomous_recovered_halfline_upper_interior_recurrence_proved=True,
        initial_encoded_halfline_and_actual_global_E0_required=True,
        arbitrary_initial_exterior_and_coherent_unused_Info_allowed=True,
        no_future_boundary_or_work_command_prescribed=True,
        immediate_arbitrary_work_narrow_encoding_alias_equality_proved=False,
        original_data_recovery_or_finite_island_extinction_proved=False,
        complete_upper_noise_class_map_proved=False,
        iid_threshold_established=False, global_reliability_established=False,
        numerical_trajectories_used=False, seconds=time.monotonic()-started,
        scope='J145 actual encoded right halfline/E0, one upper step beyond37colonies; J139/J142 decoded recovered halfline recurrence with46colony moving unsupported strip; no original-data/extinction/noise-map/iid theorem',
    )
    (out/'SP28_halfline_step_certificate.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(dict(traces=traces, front_footprint=receipt['full_radius_front_footprint_phase_bounds'],
                         interior_margin=r, unsupported_strip=strip,
                         halfline_step=True, iid=False, seconds=receipt['seconds'])), flush=True)


if __name__ == '__main__':
    main()
