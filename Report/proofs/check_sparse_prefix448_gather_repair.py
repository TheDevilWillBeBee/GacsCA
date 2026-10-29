#!/usr/bin/env python3
"""Arithmetic/provenance certificate for the scoped SP4 J32 proof.

The unbounded copy, history and trajectory arguments are in ROBUSTNESS.md.
This checker does not simulate noise or certify arbitrary-stage reliability.
"""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import proposed_sparse_prefix448 as proposed


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    candidate = proposed.load_artifact()
    p = candidate.p
    out = ROOT / 'figs/robustness'
    barrier = json.loads((out / 'SP4_barrier_certificate.json').read_text())
    symbolic = json.loads((out / 'SP4_symbolic_schedule.json').read_text())
    assert barrier['proposed_candidate_sha256'] == candidate.digest()
    assert symbolic['proposed_netlist_sha256'] == candidate.comp.digest
    repair = barrier['flags_clear_updates_after_first_danger']
    raw = barrier['raw_repair_updates_after_first_danger']
    assert (repair, raw) == (920, 420)
    table = proposed.dependency_table(p)
    groups = []
    captures = 0
    for gather in p.gathers_q:
        ages = [gather*p.Q + abs(offset)*(p.Q//8)+1
                for row in table for offset in row['offsets']]
        assert ages and max(ages) == gather*p.Q+673
        # Include the output tick of the latest capture conservatively.
        groups.append((gather*p.Q, max(ages)+1))
        captures += len(ages)
    assert groups == [(0, 674), (4480, 5154), (8960, 9634)]
    latest = p.E0-1-repair-1
    assert latest == 10342
    counts = {}
    for tau in range(latest+1):
        hit = sum(begin <= tau+repair and tau <= end for begin, end in groups)
        assert hit <= 1, (tau, hit)
        assert tau+repair < p.E0-1 < p.E0 < p.T_sig < p.T_wf
        assert tau+61 < p.U
        counts[hit] = counts.get(hit, 0)+1
    assert 674+repair < 4480
    last_stored_wf = p.T_wf+2*p.Q+1
    quiet = last_stored_wf+252+247
    assert (last_stored_wf, quiet) == (26242, 26741)
    assert quiet < p.U-1
    assert p.stage_wipe and p.clear_ws and p.confined and p.computed_front
    # The two upper ticks used in the proof have no evaluation, captures,
    # signal, commit or Workspace command. Source/copy formulas and all
    # fault values are covered by the separate local/schedule certificates.
    upper_ticks = []
    for tick in (0, 1):
        assert tick < min(begin for begin, _ in groups[1:])
        assert all(tick != gather*p.Q+abs(offset)*(p.Q//8)+1
                   for gather in p.gathers_q for row in table for offset in row['offsets'])
        assert tick < p.E0-1 and tick < p.T_sig and tick < p.T_wf
        assert tick != p.U-1
        upper_ticks.append(dict(tick=tick, raw_Age=p.age_code(tick),
                                evaluation=False, capture=False, signal=False,
                                commit=False, Workspace_command=False,
                                Mail_load=tick == 0))
    receipt = dict(
        proposal='SP4', proposed_rule_change=True, active_G17_modified=False,
        proposed_candidate_sha256=candidate.digest(), proposed_netlist_sha256=candidate.comp.digest,
        proposal_source_sha256=digest(Path(proposed.__file__)), checker_sha256=digest(Path(__file__)),
        timing_sha256=digest(ROOT / 'gacsca/rule.py'),
        transport_checker_sha256=digest(ROOT / 'Report/proofs/check_fast_mail_proposal.py'),
        barrier_receipt_sha256=digest(out / 'SP4_barrier_certificate.json'),
        symbolic_schedule_receipt_sha256=digest(out / 'SP4_symbolic_schedule.json'),
        maintenance_receipt_sha256=digest(out / 'SP4_maintenance_certificate.json'),
        build_receipt_sha256=digest(out / 'SP4_program_build.json'),
        capture_coordinates_enumerated=captures, gather_groups=groups,
        indirect_repair_interval_length=repair, latest_first_period_danger_tick=latest,
        danger_ticks_checked=latest+1, overlapped_group_counts=counts,
        maximum_overlapped_groups=1, raw_repair_updates_after_first_danger=raw,
        repaired_before_Hold_wipe=True, upper_tick_controls=upper_ticks,
        last_stored_Workspace_off=last_stored_wf, final_flag_quiet_bound=quiet,
        first_boundary_upper_fault_support_at_most=2, second_boundary_time=2*p.U,
        global_reliability_established=False,
        scope='arithmetic and provenance supporting J32 with two initial encodings; '
              'the unbounded history/localization proof is separate; no arbitrary-stage or iid theorem')
    (out / 'SP4_gather_repair_certificate.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(dict(latest_danger_tick=latest, gather_groups=groups,
                          overlapped_group_counts=counts, second_boundary=2*p.U)), flush=True)


if __name__ == '__main__':
    main()
