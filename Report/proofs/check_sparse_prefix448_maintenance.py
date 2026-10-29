#!/usr/bin/env python3
"""SP4 actual-gate certificates and Q448 mixed-E0 maintenance bounds.

The unbounded proof is the J24--J26 induction, with these constants and
the actual own-rule local preconditions rechecked. No iid threshold.
"""
import hashlib
from itertools import combinations
import json
from pathlib import Path
import sys
from types import FunctionType

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from gacsca.netlist import Net, Compiled, const_word
import proposed_sparse_prefix448 as proposed
import prefix_selection as selection
import check_prefix_selection_proposal as local
import check_sparse_prefix_e0 as e0
import check_quiet_majority_proposal as quiet
from check_fast_flag_proposal import pristine_symbolic, quiet_seed_symbolic, invoke
from check_sparse_phase_repair import suffix_certificate


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def flag2_formula(p, build):
    count = 0
    for address in (0, 1, 2, 3, 4, 5, p.Q//2, p.Q-1):
        net = Net()
        flags = {j: net.input(('f2', j)) for j in range(-5, 1)}
        cells = {}
        for j in range(-5, 9):
            if j >= 6:
                cells[j] = dict(f1=0)
            else:
                cells[j] = dict(addr=const_word((address+j) % p.Q, p.k),
                                age=const_word(p.age_code(2000), p.m), f1=0,
                                f2=flags[j] if j <= 0 else 0, wf1=0, wf2=0)
        actual = invoke(build, net, cells, p)
        net.set_output(('f2',), actual['f2'])
        comp = Compiled(net)
        for bits in range(64):
            values = {('f2', j): (bits >> (j+5)) & 1 for j in range(-5, 1)}
            left = sum(values['f2', j] for j in range(-5, 0) if address+j >= 0)
            expected = left >= 4 or (values['f2', 0] and left >= 2)
            assert comp.evaluate_scalar(values)['f2',] == bool(expected)
            count += 1
    return dict(actual_boundary_assignments=count,
                computed_Flag1_Workspace_sources_zero=True,
                scalar_rule='at least four inside-left flags OR current flag AND at least two inside-left flags')


def main():
    p = proposed.parameters()
    candidate = proposed.load_artifact()
    build, source = selection.proposed_build(symbolic=True)
    candidate_namespace = dict(local.__dict__, proposed=proposed)
    actual_full_rule = FunctionType(local.full_rule_independence.__code__, candidate_namespace)
    phase = local.phase_adjustment_certificate(p, build)
    phase['normalization_updates'] = (512-p.Q+2)//3
    result = dict(proposal='SP4', proposed_rule_change=True, active_G17_modified=False, SP3_modified=False,
                  proposed_candidate_sha256=candidate.digest(), proposed_netlist_sha256=candidate.comp.digest,
                  checker_sha256=digest(Path(__file__)), proposal_source_sha256=digest(Path(proposed.__file__)),
                  selection_source_sha256=digest(ROOT / 'Report/proofs/prefix_selection.py'),
                  SP3_local_checker_sha256=digest(ROOT / 'Report/proofs/check_prefix_selection_proposal.py'),
                  mixed_E0_checker_sha256=digest(ROOT / 'Report/proofs/check_sparse_prefix_e0.py'),
                  quiet_majority_checker_sha256=digest(ROOT / 'Report/proofs/check_quiet_majority_proposal.py'),
                  majority_shortcut_sha256=digest(ROOT / 'Report/proofs/check_right_barrier.py'),
                  helpers_sha256=digest(ROOT / 'gacsca/netlist.py'),
                  actual_local_source_sha256=hashlib.sha256(source.encode()).hexdigest(),
                  Q=p.Q, U=p.U, raw_width=candidate.W, radius=12,
                  geometry_independence=local.geometry_independence(p),
                  full_rule_independence=actual_full_rule(p),
                  one_step=local.one_step_prefix(p, build),
                  two_step=local.two_step_mask_certificate(p, build),
                  phase_adjustment=phase, protected_suffix=suffix_certificate(p, build),
                  Flag2_formula=flag2_formula(p, build),
                  flag_clearance_reserves=e0.flag_clearance_reserve(p.Q),
                  global_reliability_established=False)
    pairs = tuple(combinations(range(-5, 9), 2))
    healthy = 0
    for address in range(p.Q):
        for faults in pairs:
            pristine_symbolic(p, build, address, faults)
            healthy += 1
        if address % 112 == 111:
            print(f'SP4: healthy two-fault gates through Address {address}: {healthy}', flush=True)
    result['healthy_two_fault_symbolic_cases'] = healthy
    seeds = 0
    for address in (p.Q-2, p.Q-1):
        for faults in pairs:
            quiet_seed_symbolic(p, build, address, faults)
            seeds += 1
    extensions = 0
    for address in range(p.Q):
        for faults in combinations(range(-5, 0), 2):
            for first_outside in (False, True):
                quiet.suffix_extension(p, build, address, faults, first_outside)
                extensions += 1
    result.update(quiet_seed_symbolic_cases=seeds, quiet_suffix_extension_symbolic_cases=extensions)
    masks = e0.local_masks()
    result.update(local_masks=masks, retreat_packing=e0.retreat_packing(masks['charged_templates']),
                  advance_packing=e0.advance_packing())
    bounds = [e0.sustained_window(p.Q, w, startup) for w, startup in ((141, 100), (160, 112))]
    for bound in bounds:
        bound['full_self_simulation_ROM_built'] = True
        assert bound['closes'] and bound['two_true_colonies']
        assert bound['raw_geometry_repair_bound'] < p.U//32
        assert bound['all_flags_clearance_bound'] < p.T_wf
    result['mixed_E0_bounds'] = bounds
    result['scope'] = ('actual SP4 gate identities and support-mask arithmetic for initial-clock-zero arbitrary islands '
                       'through width160 with continuing E0 and a quiet first true colony; not general stages or iid reliability')
    out = ROOT / 'figs/robustness'
    result['build_receipt_sha256'] = digest(out / 'SP4_program_build.json')
    result['symbolic_schedule_receipt_sha256'] = digest(out / 'SP4_symbolic_schedule.json')
    (out / 'SP4_maintenance_certificate.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(dict(mixed_E0_bounds=bounds, healthy_symbolic_cases=healthy,
                          flag_reserves=result['flag_clearance_reserves']), indent=2))


if __name__ == '__main__':
    main()
