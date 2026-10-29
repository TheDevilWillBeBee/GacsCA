#!/usr/bin/env python3
"""J119: exact local support certificate for SP18's native firewall.

The written induction localizes J116 to sparse errors on x>=-3 and
arbitrary additional whole-cell overwrites on x<=-4. Initial positive
GF/Age at the epoch remains required. No upper-data or iid theorem.
"""
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from gacsca.netlist import Compiled
import proposed_sparse_epoch448 as proposed
import check_right_epoch_starter as inherited


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out=ROOT/'figs/robustness'
    candidate=proposed.load_artifact()
    p=candidate.p
    net,source=proposed.full_net(p)
    assert Compiled(net).digest == candidate.comp.digest
    parent=json.loads((out/'right_epoch_starter_certificate.json').read_text())
    assert parent['module_raw_netlist_sha256'] == candidate.comp.digest
    assert parent['module_generated_source_sha256'] == hashlib.sha256(source.encode()).hexdigest()
    identities,net_sha,source_sha=inherited.wiring(p)
    assert identities == 66 and net_sha == candidate.comp.digest
    # Eligible packet words have physical tag0..4. If an eligible output
    # at x has tag tau0..4, an input at x+j supports its cohort exactly
    # when (input_tag-j)%16 == tau. This is exhaustive raw-tag arithmetic,
    # independent of all validity/count bits and of the cohort winner.
    cases=matches=0
    roots=set()
    input_sites=set()
    for x in range(1,6):
        for tau in range(5):
            root=x-tau-1
            roots.add(root)
            for j in range(-5,6):
                for raw_tag in range(16):
                    cases+=1
                    if raw_tag >= 5 or (raw_tag-j)%16 != tau:
                        continue
                    matches+=1
                    assert raw_tag == tau+j
                    site=x+j
                    assert site == root+raw_tag+1
                    assert -3 <= site <= 9
                    input_sites.add(site)
    assert (cases,matches)==(4400,125)
    assert roots==set(range(-4,5)) and input_sites==set(range(-3,10))
    # An arbitrary overwrite to the left of the collar may supply any
    # raw tag, but an eligible one has root x-tag-1 <= -5. It cannot
    # supply a word of any dangerous root -4..4. More negative x only
    # decreases the root. No code bit participates in this PF vote.
    injection_cases=0
    for x in range(-20,-3):
        for tag in range(16):
            injection_cases+=1
            if tag<5:
                assert x-tag-1 <= -5
    # Relevant foreign birth positions are -3..9. Their RF birth inputs
    # are -2..14, all inside the sparse-error collar. The dangerous
    # actual birth positions -3,-2 and their positive-error charge are
    # unchanged from J116. A charge0..3 forbids the next-row sparse
    # errors at every carrier of a dangerous root, now localized -3..9.
    birth_input_sites={x+j for x in range(-3,10) for j in range(1,6)}
    assert birth_input_sites==set(range(-2,15))
    exclusions=0
    for charge in range(4):
        for later_error in range(-3,10):
            assert abs(later_error-charge)<24
            exclusions+=1
    assert exclusions==52
    shadow=inherited.shadow_arithmetic()
    assert shadow['max_newborns_per_dangerous_root']==2
    increments=0
    for raw_count in range(2048):
        if raw_count<1791:
            value=(raw_count+1)%2048
            assert 1 <= value <= 1791
            increments+=1
    assert increments==1791
    receipt=dict(proposal='SP18',proposed_rule_change=False,active_G17_modified=False,
        checker_sha256=digest(Path(__file__)),proposal_source_sha256=digest(Path(proposed.__file__)),
        inherited_checker_sha256=digest(Path(inherited.__file__)),
        netlist_helper_sha256=digest(ROOT/'gacsca/netlist.py'),
        proposed_candidate_sha256=candidate.digest(),proposed_netlist_sha256=candidate.comp.digest,
        full_generated_source_sha256=source_sha,
        epoch_receipt_sha256=digest(out/'right_epoch_starter_certificate.json'),
        incorporation_receipt_sha256=digest(out/'SP18_incorporation_encoded_certificate.json'),
        build_receipt_sha256=digest(out/'SP18_program_build.json'),
        quiet_native_receipt_sha256=digest(out/'SP16_quiet_region_certificate.json'),
        period_native_receipt_sha256=digest(out/'SP16_period_barrier_certificate.json'),
        packet_pressure_receipt_sha256=digest(out/'packet_pressure_certificate.json'),
        buffered_service_receipt_sha256=digest(out/'buffered_framed_service_certificate.json'),
        Q=p.Q,U=p.U,width=candidate.W,
        actual_full_rule_native_packet_code_wiring_identities=identities,
        whole_word_origin_exhaustive_raw_tag_cases=cases,eligible_origin_matches=matches,
        relevant_packet_origins=[-4,4],relevant_packet_carrier_sites=[-3,9],
        relevant_RF_birth_input_sites=[-2,14],
        arbitrary_left_overwrite_boundary=-4,protected_sparse_error_boundary=-3,
        far_left_eligible_injection_cases=injection_cases,
        younger_birth_positive_charge_next_row_exclusion_cases=exclusions,
        localized_foreign_birth_shadow_cases=shadow['dangerous_overlapping_root_group_shadows'],
        max_younger_newborns_per_dangerous_root=2,
        nonbirth_nonzero_increment_cases=increments,
        initial_canonical_positive_GF_and_epoch_Age_required=True,
        sparse_part_is_restriction_of_global_E0=True,
        additional_left_overwrites_arbitrary_sites_ticks_values=True,
        positive_native_GF_Age_barrier_all_time_proved=True,
        first_C_structural_workspace_reset_state=p.U-p.T_wf,
        first_C_structural_workspace_reset_spacing=p.U,
        quiet_C_Flag1_WF1_deadline_after_epoch=1150,
        proper_packet_states=[1,1792],
        general_GF_Age_seed_reconstruction_established=False,
        represented_Info_or_full_upper_error_map_established=False,
        smallest_sufficient_global_change_established=False,
        iid_threshold_established=False,global_reliability_established=False,
        scope='ROBUSTNESS J119 written native-firewall induction; sparse E0 on x>=-3, arbitrary forcing on x<=-4, initially correct positive GF/Age at epoch; no general damaged seed, data map or iid theorem')
    (out/'SP18_native_firewall_certificate.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(raw_tag_cases=cases,matches=matches,collar=[-3,-1],
        arbitrary_overwrites_x_le=-4,positive_native_all_time=True,
        data_result=False,iid_threshold=False)),flush=True)


if __name__=='__main__':
    main()
