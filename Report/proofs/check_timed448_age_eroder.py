#!/usr/bin/env python3
"""Pin J82's maintenance identities and J85's birth guard to actual SP13.

This is a premise/source transfer certificate, not another enumeration.
The restricted-noise binary-GF theorem and its no-birth induction are
written in ROBUSTNESS J85. Authentic source initialization is a premise.
"""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import proposed_sparse_timed448 as proposed
import proposed_sparse_cohort448 as previous


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out = ROOT / 'figs/robustness'
    candidate = proposed.load_artifact()
    p = candidate.p
    assert proposed.proposed_build()[1] == previous.proposed_build()[1]
    maintenance_hash = hashlib.sha256(proposed.proposed_build()[1].encode()).hexdigest()
    old = json.loads((out / 'timed_packet_age_eroder_certificate.json').read_text())
    assert old['actual_maintenance_source_sha256'] == maintenance_hash
    assert old['local_identities'] == dict(packet=120, canonical_zero_holder=10,
                                          front=2646, clock_suffix=5110)
    guard = json.loads((out / 'SP13_birth_guard_certificate.json').read_text())
    assert guard['proposed_candidate_sha256'] == candidate.digest()
    assert guard['candidate_birth_centers_in_binary_phase_GF'] == list(range(1, 7))
    assert guard['protected_three_word_cohort_cases'] == 60
    assert guard['actual_packet_equals_retention_with_all_commands_free']
    retention = json.loads((out / 'SP13_packet_retention_certificate.json').read_text())
    assert retention['packet_output_node_identities'] == 17
    assert (p.Q, p.U, candidate.W) == (448, 67584, 275)
    assert old['canonical_GF_and_correct_computed_Age_by_update'] == 671
    assert 671 < proposed.packet.LIFETIME
    receipt = dict(
        proposal='SP13', proposed_rule_change=True, active_G17_modified=False,
        checker_sha256=digest(Path(__file__)),
        proposal_source_sha256=digest(Path(proposed.__file__)),
        proposed_candidate_sha256=candidate.digest(),
        proposed_netlist_sha256=candidate.comp.digest,
        actual_maintenance_source_sha256=maintenance_hash,
        full_generated_source_sha256=hashlib.sha256(proposed.actual_net(p)[1].encode()).hexdigest(),
        build_receipt_sha256=digest(out / 'SP13_program_build.json'),
        maintenance_eroder_receipt_sha256=digest(out / 'timed_packet_age_eroder_certificate.json'),
        birth_guard_receipt_sha256=digest(out / 'SP13_birth_guard_certificate.json'),
        packet_retention_receipt_sha256=digest(out / 'SP13_packet_retention_certificate.json'),
        timed_packet_certificate_sha256=digest(out / 'timed_cohort_packet_certificate.json'),
        maintenance_source_identical_to_J82=True,
        own_program_incorporation_established=True,
        binary_phase_GF_required=True,
        initial_Age_on_colony_arbitrary=True,
        correctly_initialized_five_word_timed_packet_required=True,
        every_other_initial_packet_component_zero_required=True,
        right_canonical_GF_reference_Age_prescribed=True,
        continuing_Age_faults_at_most_two_per_five_site_row_required=True,
        continuing_packet_faults_at_most_two_per_eleven_site_row_required=True,
        continuing_GF_Flag1_Flag2_or_other_field_faults_covered=False,
        further_birth_suppression_on_protected_packet_follows_from_actual_rule=True,
        NF2_positive_prefix_by_update=222,
        canonical_GF_and_correct_computed_Age_by_update=671,
        packet_lifetime=proposed.packet.LIFETIME,
        source_initialization_or_full_upper_error_map_established=False,
        global_reliability_established=False,
        scope='source/premise transfer and guarded-birth induction for conditional actual-SP13 binary-GF Age eroder; ROBUSTNESS J85')
    (out / 'SP13_age_eroder_certificate.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(dict(SP13_GF_Age_deadline=671, guarded_birth_premise_discharged=True)))


if __name__ == '__main__':
    main()
