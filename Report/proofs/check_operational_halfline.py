#!/usr/bin/env python3
"""Actual-gate/support/timing certificates for the scoped J41 barrier.

The finite-horizon trajectory induction is in ROBUSTNESS.md. This checker
does not certify a hierarchy projection, higher eroder or iid threshold.
"""
import hashlib
from itertools import combinations
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from gacsca import candidates
from gacsca.netlist import Compiled
import proposed_sparse_prefix448 as proposed
from check_right_barrier import certified_build
from check_sparse_prefix448_localization import closed_colony_case
from check_sparse_prefix448_autonomy import ancestors


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def command_stores(candidate):
    p = candidate.p
    targets = (p.lo, p.hi-1)
    rows = []
    for cell in targets:
        for page in range(p.NP):
            if page in p.match_list:
                continue
            for front in range(p.fronts):
                word = int(candidate.rom[cell, page+(front << p.logNP)])
                if (word >> 2) & 3 != 1:  # K_HOLD
                    continue
                tick = (p.hi-1+front*p.delta-cell if page % 2 else
                        cell-(p.lo-p.H)-front*p.delta)
                assert 0 <= tick < p.R
                rows.append(dict(cell=cell, page=page, front=front,
                                 instruction_input_age=p.E0+page*p.R+tick))
    assert len(rows) == 2 and {row['cell'] for row in rows} == set(targets)
    # Signals are unused primaries and never legal store targets.
    for cell in (3, p.Q-3):
        assert cell < p.lo or cell >= p.hi
    return rows


def support(candidate, net, last_capture, proof_receipts):
    p = candidate.p
    assert Compiled(net).digest == candidate.comp.digest
    independent = []
    for name, node in net.outputs.items():
        if name[0] in ('laddr', 'psel', 'arrive') or name[:1] == ('y',) and name[1] in (
                'reg', 'pend', 'pkind', 'pval', 'hold', 'scr'):
            assert not any(inp[0] == 'x' and inp[2] in ('mr', 'ml') for inp in ancestors(net, node)), name
            independent.append(name)
    radius = max(abs(n[1]) for n in net.input_node if n[0] == 'x')
    lo = p.lo-p.H-2
    hi = p.hi-1+(p.fronts-1)*p.delta+2
    assert 0 < lo-radius <= hi+radius < p.Q-1
    frozen = last_capture+2
    horizon = p.T_wf-frozen
    assert horizon > 0 and horizon < p.T_wf
    starts = []
    for clock in range(p.U):
        hit = False
        for cycle in (0, 1):
            left, right = cycle*p.U+p.T_wf, cycle*p.U+p.T_wf+2*p.Q-1
            if left <= clock+horizon and clock <= right:
                hit = True
                assert cycle == 0 and clock >= frozen
        if hit:
            starts.append(clock)
    assert min(starts) == frozen and max(starts) == p.T_wf+2*p.Q-1
    stores = command_stores(candidate)
    _, left_load, right_load = p.courier_ticks()
    paths = []
    for origin, target, tick in ((p.lo, 3, left_load), (p.hi-1, p.Q-3, right_load)):
        assert tick+1+abs(target-origin) == p.T_sig
        holders = [min(origin, target)-2, max(origin, target)+2]
        assert 0 < holders[0] <= holders[1] < p.Q
        paths.append(dict(origin=origin, target=target, load_input_age=tick, holder_span=holders))
    return dict(Q=p.Q, U=p.U, radius=radius, last_capture_input_age=last_capture,
                post_gather_frozen_clock=frozen, uniform_operational_barrier_horizon=horizon,
                clock_phases_checked=p.U, phases_whose_horizon_meets_Workspace=len(starts),
                such_phase_range=[min(starts), max(starts)],
                active_register_holder_frame=[lo, hi], full_input_frame=[lo-radius, hi+radius],
                current_Mail_independent_outputs=len(independent), command_Hold_stores=stores,
                signal_courier_paths=paths,
                proof_receipt_sha256={name:digest(ROOT / 'figs/robustness' / name) for name in proof_receipts})


def main():
    original = candidates.load('G17')
    build = certified_build()
    cases = 0
    for address in range(original.p.Q):
        for faults in combinations(range(-5, 6), 2):
            closed_colony_case(original.p, build, address, faults)
            cases += 1
    assert cases == 21120
    net = original.p.fam().build(original.p)
    last = max(original.p.capture_age(offset, group)
               for offset in original.p.fam().LANE_OFFSETS for group in range(3))
    g17 = support(original, net, last, ('symbolic_schedule.json', 'right_barrier_certificate.json'))
    assert g17['uniform_operational_barrier_horizon'] == 3944
    g17.update(two_flag_quiet_colony_symbolic_cases=cases, common_Age_bits_free=original.p.m)
    proposed4 = proposed.load_artifact()
    net4, _ = proposed.cached(proposed4.p)
    last4 = max(g*proposed4.p.Q+abs(offset)*(proposed4.p.Q//8)+1
                for g in proposed4.p.gathers_q for row in proposed.dependency_table(proposed4.p)
                for offset in row['offsets'])
    sp4 = support(proposed4, net4, last4, ('SP4_symbolic_schedule.json',
                   'SP4_autonomy_certificate.json', 'SP4_localization_certificate.json'))
    assert sp4['uniform_operational_barrier_horizon'] == 15710
    out = ROOT / 'figs/robustness'
    result = dict(
        checker_sha256=digest(Path(__file__)), active_G17_modified=False,
        **candidates.digests(original),
        proposed_SP4_candidate_sha256=proposed4.digest(), proposed_SP4_netlist_sha256=proposed4.comp.digest,
        proposal_source_sha256=digest(Path(proposed.__file__)),
        locality_checker_sha256=digest(ROOT / 'Report/proofs/check_sparse_prefix448_localization.py'),
        autonomy_checker_sha256=digest(ROOT / 'Report/proofs/check_sparse_prefix448_autonomy.py'),
        maintenance_sha256=digest(ROOT / 'gacsca/maintenance.py'),
        full_rule_sha256=digest(ROOT / 'gacsca/rule_g.py'),
        G17=g17, SP4=sp4, trajectory_proof_is_separate=True,
        all_level_projection_established=False, global_reliability_established=False,
        scope='literal two-flag closure, current-Mail exclusion, frame/courier and all-clock horizon support for J41')
    (out / 'operational_halfline_certificate.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(dict(G17_horizon=3944, SP4_horizon=15710, G17_symbolic_cases=cases)), flush=True)


if __name__ == '__main__':
    main()
