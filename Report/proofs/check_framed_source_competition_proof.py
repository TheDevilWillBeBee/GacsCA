#!/usr/bin/env python3
"""Proof-only local certificate for J93; literal full-state replay separate."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from gacsca.netlist import Net, const_word
import check_framed_source_competition as replay


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def packet_case(t, x):
    n = Net()
    cells = {}
    for off in range(-5, 6):
        y = x + off
        young = -3 <= y <= (-1 if t == 1 else 1)
        old = (1 <= y <= 5) if t == 1 else (2 <= y <= 5)
        if t == 25 and y in (2, 3):
            old = False
        cells[off] = dict(packet_valid=int(young or old), wf2=int(young or old),
            packet_tag=const_word(y + 3 if young else y - 1 if old else 0, 4),
            packet_count=const_word(t - 1 if young else t if old else 0, 11),
            flag_valid=n.input((off, 'coded_valid')),
            flag_position=[n.input((off, 'coded_position', b)) for b in range(9)],
            flag_count=[n.input((off, 'coded_count', b)) for b in range(11)])
    result = replay.proposed.service.build(n, cells)
    young = -3 <= x <= 1
    old = 2 <= x <= 5 and t != 25
    assert result['packet_valid'] == int(young or old), (t, x)
    assert result['wf2'] == int(young or old), (t, x)
    assert result['packet_tag'] == const_word(x + 3 if young else x - 1 if old else 0, 4), (t, x)
    assert result['packet_count'] == const_word(t if young else t + 1 if old else 0, 11), (t, x)


def geometry_case(p, build, t, x):
    n = Net()
    cells = {off: dict(addr=const_word((x + off + 4) % p.Q, p.k),
        age=const_word(p.age_code(p.T_wf + t), p.m),
        **{f: n.input((off, f)) for f in ('f1', 'f2', 'wf1', 'wf2')}) for off in range(-5, 9)}
    result = build(n, cells, p.k, p.m, Q=p.Q, nb=p.nb, radix=p.R,
                   pos_bits=p.PB, service_force=n.input(('arbitrary_service_force',)))
    assert result['addr'] == const_word((x + 4) % p.Q, p.k), (t, x)
    assert result['age_now'] == const_word(p.age_code(p.T_wf + t), p.m), (t, x)
    assert result['age'] == const_word(p.age_code(p.T_wf + t + 1), p.m), (t, x)


def main():
    candidate = replay.proposed.load_artifact()
    p = candidate.p
    build, source = replay.proposed.proposed_build(symbolic=True)
    for x in range(-4, 7):
        replay.birth_case(p, x)
    packet_cases, geometry_cases = 0, 0
    for t in range(1, 26):
        for x in range(-4, 7):
            packet_case(t, x)
            packet_cases += 1
    for t in range(26):
        for x in range(-4, 7):
            geometry_case(p, build, t, x)
            geometry_cases += 1
    assert all(p.age_code(p.T_wf + t) != p.age_code(p.T_wf) for t in range(1, 27))
    assert p.T_wf + 26 < p.U
    out = ROOT / 'figs/robustness'
    receipt = dict(proposal='SP14', proposed_rule_change=False, active_G17_modified=False,
        proposed_candidate_sha256=candidate.digest(), proposed_netlist_sha256=candidate.comp.digest,
        proposal_source_sha256=digest(Path(replay.proposed.__file__)), checker_sha256=digest(Path(__file__)),
        source_competition_checker_sha256=digest(Path(replay.__file__)),
        helpers_sha256=digest(ROOT / 'gacsca/netlist.py'),
        build_receipt_sha256=digest(out / 'SP14_program_build.json'),
        framed_service_certificate_sha256=digest(out / 'framed_service_certificate.json'),
        canonical_birth_receipt_sha256=digest(out / 'SP14_packet_birth_certificate.json'),
        full_generated_source_sha256=hashlib.sha256(replay.proposed.actual_net(p)[1].encode()).hexdigest(),
        actual_maintenance_source_sha256=hashlib.sha256(source.encode()).hexdigest(),
        actual_full_rule_initial_birth_cofactors=11,
        free_coded_word_packet_retention_cofactors=packet_cases,
        free_flag_pressure_GF_and_clock_cofactors=geometry_cases,
        all_input_GF_phase_four_and_Age_current_reference_required=True,
        initial_Info_all_one_only_at_first_birth_step_required=True,
        current_pair_faults_erase_packet_and_code_preserve_GF_Age_required=True,
        fault_groups=[dict(tick=0, sites=[1, 2]), dict(tick=25, sites=[2, 3])],
        global_E0_separation_satisfied=True, later_birth_clock_closed_updates=list(range(1, 26)),
        initial_proper_packet_origin=0, initial_proper_packet_count=0,
        foreign_newborn_origin=-4, foreign_newborn_sites=[-3, -2, -1],
        old_packet_first_incomplete_state=2, old_packet_erased_state=26,
        free_other_flags_data_and_instructions=True,
        iid_unreliability_established=False, global_reliability_established=False,
        scope='exact local identities plus integer-origin/count/infinite coherent-geometry induction, ROBUSTNESS J93; no finite replay needed for this certificate')
    (out / 'SP14_source_competition_proof_certificate.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(dict(birth_cases=11, packet_cases=packet_cases, GF_clock_cases=geometry_cases,
                         original_source_erased_state=26)))


if __name__ == '__main__':
    main()
