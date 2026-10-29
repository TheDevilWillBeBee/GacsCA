#!/usr/bin/env python3
"""SP28 broad coherent-Info encoding contraction, ROBUSTNESS J144.

This audits all actual own-ROM data reads and gather coordinates. The
physical E0 copy/programme induction is reused, with the generalized
premises proved in SP28_ENCODING_FAMILY.md. No trajectories are sampled.
It does not prove a real1/higher-error map or an iid noise threshold.
"""
from collections import Counter
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
    out = ROOT / 'figs/robustness'
    p = proposed.parameters()
    table = proposed.dependency_table(p)
    normal = {row['address'] for row in table}
    profile = {row['address']: row['offsets'] for row in table}
    assert normal == set(range(59, 901))
    assert normal.isdisjoint({p.lo, p.hi-1, 3, p.Q-3})
    sources = proposed.source_names(p)
    listing_file = out / 'SP28_program_listing.json'
    listing = json.loads(listing_file.read_text())
    families = Counter()
    direct = histories = 0
    for row in listing:
        cell = row[4]
        for source_code in row[7:9]:
            family, index = sources[source_code]
            families[family] += 1
            if family == 'info':
                assert cell in normal and index == 0, (row, family, index)
                direct += 1
            elif family == 'ln':
                assert cell in normal and 0 <= index < len(profile[cell]), (row, family, index)
                histories += 1
            else:
                assert family in ('reg', 'scr', 'const'), (row, family, index)
    assert len(listing) == 130974
    assert (direct, histories) == (1368, 17715)
    assert sum(families.values()) == 2*len(listing)
    # A gathered reference may cross colony boundaries, but its phase
    # remains the normal primary's phase. Thus no unused Info primary is
    # a gathered programme input, including the two auxiliary flag copies.
    coordinates = 0
    for row in table:
        a = row['address']
        assert a in normal
        for gather in p.gathers_q:
            for offset in row['offsets']:
                shifts = abs(offset)*(p.Q//8)
                assert shifts <= 37*(p.Q//8)
                actual_source = a + offset*p.Q
                assert actual_source % p.Q == a
                assert actual_source % p.Q not in (p.lo, p.hi-1, 3, p.Q-3)
                assert 8*shifts == abs(offset)*p.Q
                assert gather*p.Q+shifts+1 < p.E0
                coordinates += 1
    assert coordinates == 25284

    source = proposed.generated_source(p)
    # Pin the literal expressions on which the new premise argument rests.
    for line in (
        "            info = n.MUX(commit, lv(x, 'hold'),\n",
        "                         n.MUX(sp3, lv(x, 'ml'), n.MUX(spq, lv(x, 'mr'), lv(x, 'info'))))\n",
        "    in_wf = w_in_range(n, age_now, p.age_code(p.T_wf), p.age_code(p.T_wf + 2 * Q - 1) + 1)\n",
        "    wf1 = n.all([right_end, in_wf, sim_r])\n",
        "    wipe = n.AND(f1_new, n.NOT(w_eq(n, addr_now, c['addr'])))\n",
        "    keep = n.NOT(wipe)\n",
        "    sig = age_is(p.T_sig)\n",
    ):
        assert source.count(line) == 1, line
    generated_sha = hashlib.sha256(source.encode()).hexdigest()
    encoded = json.loads((out/'SP28_encoded_certificate.json').read_text())
    programme = json.loads((out/'SP28_symbolic_schedule.json').read_text())
    build = json.loads((out/'SP28_program_build.json').read_text())
    assert encoded['full_generated_source_sha256'] == generated_sha
    assert encoded['complete_encoded_noiseless_and_all_period_E0_simulation_proved']
    assert programme['final_hold_equalities'] == 842
    assert programme['early_flag_equalities'] == 2
    assert encoded['proposed_candidate_sha256'] == programme['proposed_candidate_sha256'] == build['proposed_candidate_sha256']
    assert encoded['proposed_netlist_sha256'] == programme['proposed_netlist_sha256']
    assert build['listing_sha256'] == digest(listing_file)
    assert max(programme['latest_capture_input_ages']) < p.E0 < p.T_sig < p.T_wf
    assert p.T_sig+1 == p.T_wf == 278401
    assert max(programme['early_flag_store_ages'].values()) < min(p.courier_ticks()[1:])

    proof_file = ROOT/'Report/proofs/SP28_ENCODING_FAMILY.md'
    assert proof_file.exists()
    receipt = dict(
        proposal='SP28', proposed_rule_change=True, additional_rule_change=False,
        active_G17_modified=False, checker_sha256=digest(Path(__file__)),
        written_proof_sha256=digest(proof_file),
        proposal_source_sha256=digest(Path(proposed.__file__)),
        full_generated_source_sha256=generated_sha,
        proposed_candidate_sha256=encoded['proposed_candidate_sha256'],
        proposed_netlist_sha256=encoded['proposed_netlist_sha256'],
        listing_sha256=digest(listing_file),
        encoded_receipt_sha256=digest(out/'SP28_encoded_certificate.json'),
        programme_receipt_sha256=digest(out/'SP28_symbolic_schedule.json'),
        build_receipt_sha256=digest(out/'SP28_program_build.json'),
        Q=p.Q, U=p.U, width=proposed.width(p), radius=37,
        represented_Info_primaries=len(normal), unused_Info_primaries=p.Q-len(normal),
        actual_instructions_checked=len(listing), actual_operand_reads_checked=sum(families.values()),
        actual_operand_read_family_counts=dict(families),
        direct_Info_reads_at_represented_primaries=direct,
        gathered_history_reads_at_represented_primaries=histories,
        gathered_input_reference_coordinates_preserving_represented_phase=coordinates,
        special_Info_overwrite_input_clock=p.T_sig,
        first_WF1_enabled_input_clock=p.T_wf,
        arbitrary_coherent_unused_Info_allowed=True,
        initial_auxiliary_flag_alias_equality_required=False,
        broad_encoding_contracts_to_narrow_E28_after_one_period_under_actual_E0=True,
        all_period_boundary_decoder_proved=True,
        arbitrary_work_commit_immediately_equals_narrow_E28_proved=False,
        arbitrary_work_commit_layout_is_in_broad_encoding_family=True,
        original_upper_data_recovery_proved=False,
        real1_data_map_or_higher_error_map_proved=False,
        iid_threshold_established=False, global_reliability_established=False,
        errors_restricted_to_actual_global_E0=True,
        initial_native_canonical_Age_zero_and_private_fields_zero_required=True,
        numerical_trajectories_used=False, seconds=time.monotonic()-started,
        scope='J144 all upper configurations; arbitrary unused coherent Info; global canonical/native/private-zero start; actual E0 only; no arbitrary-work alias equality, original-data, real1/higher or iid theorem',
    )
    (out/'SP28_encoding_family_certificate.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(dict(instructions=len(listing), operand_reads=sum(families.values()),
                         coordinates=coordinates, broad_encoded_E0=True,
                         original_data_recovered=False, iid=False,
                         seconds=receipt['seconds'])), flush=True)


if __name__ == '__main__':
    main()
