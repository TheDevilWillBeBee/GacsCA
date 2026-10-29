#!/usr/bin/env python3
"""SP4 support/timing for the reduced operational restart premise.

This certifies source tags and phase cases. The cohort/programme trajectory
argument is separate in ROBUSTNESS.md. No physical repeated-core map or
uniform-depth reliability is certified here.
"""
import hashlib
import inspect
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from gacsca import rule_g
import proposed_sparse_prefix448 as proposed
from check_sparse_prefix448_autonomy import ancestors


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    candidate = proposed.load_artifact()
    p = candidate.p
    out = ROOT / 'figs/robustness'
    actual, compiled = proposed.cached(p)
    assert compiled.digest == candidate.comp.digest
    tagged = set(proposed.fivefold_fields(p))
    keys = {'laddr', 'psel', 'arrive'}
    fields = {'reg', 'pend', 'pkind', 'pval', 'hold', 'scr'}
    logical_offsets = {}
    raw_offsets = {}
    outputs = []
    for name, node in actual.outputs.items():
        if name[0] in keys or name[0] == 'y' and name[1] in fields:
            outputs.append(name)
            for inp in ancestors(actual, node):
                if inp[0] == 'x':
                    _, offset, field, bit = inp
                    assert field not in ('ml', 'mr')
                    raw_offsets.setdefault(field, set()).add(offset)
                    if field in tagged:
                        width = proposed.logical_width(field, p)
                        logical_offsets.setdefault(field, set()).add(offset+bit//width-2)
    assert len(outputs) == 134
    assert set(logical_offsets) == {'pkind', 'pend', 'pval', 'hold', 'scr', 'h1', 'info'}
    assert all(offsets == set(range(-2, 3)) for offsets in logical_offsets.values())
    assert raw_offsets['reg'] == set(range(-5, 6))
    assert raw_offsets['f1'] == set(range(9))
    assert raw_offsets['addr'] == raw_offsets['age'] == raw_offsets['wf1'] == set(range(-5, 6))
    assert all(raw_offsets[field] == set(range(-4, 5)) for field in logical_offsets)
    frame = [36, 411]
    assert 36-5 == 31 > 26
    assert 36-2 == 34 >= 28
    assert 28-2 == 26
    front = inspect.getsource(rule_g._mux_front)
    assert "new['reg'][i] = n.AND(any_arrive," in front
    assert 'kind_lines = [n.AND(inside, x) for x in kind_lines]' in front
    assert "inside = w_in_range(n, xaddr, p.lo, p.hi)" in front
    horizon = 15710
    threatened = []
    phase_cases = []
    for phi in range(p.U):
        hit = any(cycle*p.U+p.T_wf <= phi+horizon and
                  phi <= cycle*p.U+p.T_wf+2*p.Q-1 for cycle in range(2))
        if hit:
            assert 9635 <= phi <= 26240
            assert phi+horizon <= 41950 < p.U-1
            threatened.append(phi)
        if 25289 <= phi <= p.T_sig:
            primary = 3+p.T_sig-phi
            assert 3 <= primary <= 58
            phase_cases.append(dict(initial_clock=phi, remaining_ML_pulse_primary=primary,
                                   whole_word_domain_covers_all_copy_holders=primary >= 28,
                                   additional_near_pulse_premise_needed=primary <= 27))
    assert threatened == list(range(9635, 26241))
    assert len(phase_cases) == 56
    assert sum(row['additional_near_pulse_premise_needed'] for row in phase_cases) == 25
    dependencies = ('SP4_program_build.json', 'SP4_symbolic_schedule.json',
                    'SP4_autonomy_certificate.json', 'SP4_operational_certificate.json',
                    'SP4_boundary_prefix_modules_certificate.json',
                    'SP4_boundary_recovered_pulse_certificate.json', 'SP4_shifted_halfline_certificate.json')
    result = dict(
        proposal='SP4', proposed_rule_change=True, active_G17_modified=False,
        proposed_candidate_sha256=candidate.digest(), proposed_netlist_sha256=candidate.comp.digest,
        proposal_source_sha256=digest(Path(proposed.__file__)), checker_sha256=digest(Path(__file__)),
        full_rule_sha256=digest(ROOT / 'gacsca/rule_g.py'),
        autonomy_checker_sha256=digest(ROOT / 'Report/proofs/check_sparse_prefix448_autonomy.py'),
        actual_mux_front_source_sha256=hashlib.sha256(front.encode()).hexdigest(),
        consumed_programme_outputs=outputs,
        consumed_tagged_field_logical_offsets={f:sorted(o) for f,o in logical_offsets.items()},
        consumed_raw_x_offsets={f:sorted(o) for f,o in raw_offsets.items()},
        active_register_holder_frame=frame, first_consumed_register_raw_source=31,
        first_consumed_tagged_logical_primary=34, first_frozen_private_logical_primary=28,
        pristine_whole_word_domain_start=26,
        private_frozen_fields=['info', 'hold', 'h1', 'h2', 'scr', 'pend', 'pkind', 'pval'],
        compact_register_outside_arrival_frame_zero=True,
        pending_stores_outside_work_area_disabled=True,
        horizon=horizon, clock_phases_checked=p.U,
        threatened_initial_clock_range=[9635, 26240], threatened_horizon_final_clock_maximum=41950,
        remaining_pulse_clock_cases=phase_cases,
        additional_near_ML_pulse_clock_range=[25320, 25344], additional_near_ML_pulse_phases=25,
        proof_receipt_sha256={name:digest(out / name) for name in dependencies},
        trajectory_argument_is_separate=True, reduced_snapshot_barrier_proof='ROBUSTNESS J53',
        physical_damaged_prefix_capture_map_established=False,
        arbitrary_near_repeated_cores_covered=False, universal_higher_island_repair_established=False,
        global_reliability_established=False,
        scope='actual consumed logical tags, zero-register/store guards and finite-horizon phase support; reduced snapshot induction separate')
    (out / 'SP4_reduced_boundary_snapshot_certificate.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(dict(consumed_outputs=134, minimum_consumed_tagged_primary=34,
                          private_frozen_primary_start=28, additional_near_ML_pulse_phases=25,
                          finite_horizon=horizon)), flush=True)


if __name__ == '__main__':
    main()
