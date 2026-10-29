#!/usr/bin/env python3
"""Arithmetic/provenance for the scoped all-first-period J34 reset proof.

Local program, copy and trajectory proofs are in ROBUSTNESS.md. This
does not certify higher islands, an effective-noise process or iid memory.
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
    low = json.loads((out / 'SP4_gather_repair_certificate.json').read_text())
    late = json.loads((out / 'SP4_autonomy_certificate.json').read_text())
    assert low['latest_first_period_danger_tick'] >= late['post_gather_core_begin']-1
    assert late['raw_geometry_repair_updates_after_core'] == 420
    maximum = 0
    for tau in range(p.U):
        settle = max(p.U, tau+420)
        relative = settle-p.U
        maximum = max(maximum, relative)
        assert 0 <= relative <= 419
        assert tau+61 < settle
        assert relative+500 <= 919 < p.gathers_q[1]*p.Q
        assert p.gathers_q[1]*p.Q < p.gathers_q[2]*p.Q
        assert p.gathers_q[2]*p.Q+674 < p.E0-1
        assert settle+500 < 2*p.U
    assert maximum == 419
    listing_path = out / 'SP4_program_listing.json'
    listing = json.loads(listing_path.read_text())
    sources = proposed.source_names(p)
    layout = set(candidate.layout.tolist())
    lane_reads = 0
    own_info_addresses = set()
    for _, _, _, _, cell, _, _, a, b, _, _ in listing:
        for code in (a, b):
            family, _ = sources[code]
            if family in ('reg', 'scr', 'const'):
                continue
            assert family in ('info', 'ln'), (cell, family)
            assert cell in layout, (cell, family)
            lane_reads += 1
            if family == 'info':
                own_info_addresses.add(cell)
    assert own_info_addresses.isdisjoint((p.lo, p.hi-1, 3, p.Q-3))
    receipt = dict(
        proposal='SP4', proposed_rule_change=True, active_G17_modified=False,
        proposed_candidate_sha256=candidate.digest(), proposed_netlist_sha256=candidate.comp.digest,
        proposal_source_sha256=digest(Path(proposed.__file__)), checker_sha256=digest(Path(__file__)),
        gather_repair_receipt_sha256=digest(out / 'SP4_gather_repair_certificate.json'),
        autonomy_receipt_sha256=digest(out / 'SP4_autonomy_certificate.json'),
        maintenance_receipt_sha256=digest(out / 'SP4_maintenance_certificate.json'),
        symbolic_schedule_receipt_sha256=digest(out / 'SP4_symbolic_schedule.json'),
        build_receipt_sha256=digest(out / 'SP4_program_build.json'),
        listing_sha256=digest(listing_path),
        lane_operand_reads_checked=lane_reads,
        own_Info_operand_addresses=sorted(own_info_addresses),
        unused_auxiliary_Info_read=False,
        first_period_core_ticks_checked=p.U, early_and_late_ranges_cover_all_core_ticks=True,
        first_boundary_decode_fault_support_at_most=2,
        first_boundary_complete_encoding_claimed=False,
        maximum_alignment_tick_into_second_period=maximum,
        maximum_quiet_tick_into_second_period=919,
        later_gathers_before_Hold_wipe=True, last_S_before_alignment=True,
        second_boundary_time=2*p.U, global_reliability_established=False,
        scope='arithmetic/provenance for one real S, two initial encodings and continuing E0; '
              'unbounded reset proof separate; arbitrary higher commands and iid reliability unproved')
    (out / 'SP4_period_repair_certificate.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(dict(core_ticks=p.U, latest_alignment_into_second_period=maximum,
                          latest_quiet_into_second_period=919, second_boundary=2*p.U)), flush=True)


if __name__ == '__main__':
    main()
