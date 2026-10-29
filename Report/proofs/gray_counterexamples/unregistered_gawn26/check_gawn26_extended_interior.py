"""Arithmetic supplements for GAWN26, with hash-checked frozen antecedents.

No native/SF history or U/2U physical execution is simulated here.
"""
import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
DATA = ROOT / 'figs/gray_counterexamples/unregistered_gawn26'
PARENT = ROOT / 'figs/gray_counterexamples/unregistered_gawn24/GAWN24_standalone_assets.json'
PROOF = HERE / 'GAWN26_EXTENDED_INTERIOR_REPAIR.md'
RULE = HERE.parent / 'unregistered_gawn2/small_rule_gawn2.py'
Q, U, R = 4096, 524288, 10238
LAST = U - 1 - R
CAPTURE_LAST = 72 * Q + 1
WINDOWS = [(s, s + 8 * Q + 1) for s in (0, 32 * Q, 64 * Q)]
TABLE = [(0, WINDOWS[0][1], 120833),
         (WINDOWS[0][1] + 1, WINDOWS[1][1], 251905),
         (WINDOWS[1][1] + 1, CAPTURE_LAST, 382977),
         (CAPTURE_LAST + 1, LAST, LAST)]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def check_assets(assets):
    for path, value in assets.items():
        assert sha(ROOT / path) == value, (path, 'hash mismatch')


def phase_predicate(tau, last):
    if not 0 <= tau <= last <= LAST:
        return False
    if tau > CAPTURE_LAST:
        return True
    quiet = last + R
    touched = sum(tau <= hi and quiet >= lo for lo, hi in WINDOWS)
    return quiet <= 96 * Q - 1 and touched <= 1


def support_counts():
    dig = hashlib.sha256()
    n = 0
    max_left = max_right = 0
    # Little-endian uint16 rows [b,w,left-holder-count,right-holder-count].
    # Only arithmetic is evaluated; these are not automaton states.
    for b in range(1, Q - 1):
        w = np.arange(1, Q - b, dtype=np.int32)
        left = np.maximum(0, np.minimum(b + w, 3) - max(b, -2))
        right = np.maximum(0, np.minimum(b + w, Q + 2) - max(b, Q - 3))
        assert np.all(left <= 2) and np.all(right <= 2)
        table = np.column_stack((np.full(len(w), b), w, left, right)).astype('<u2')
        dig.update(table.tobytes(order='C'))
        n += len(w)
        max_left = max(max_left, int(left.max()))
        max_right = max(max_right, int(right.max()))
    assert n == (Q - 2) * (Q - 1) // 2 == 8382465
    assert (max_left, max_right) == (2, 2)
    return dict(all_interior_intervals=n, maximum_width=Q - 2,
                maximum_vulnerable_endpoint_holders=[max_left, max_right],
                rows_format='little-endian uint16 [b,w,left,right]',
                endpoint_rows_sha256=dig.hexdigest())


def phase_counts():
    rows = np.empty((LAST + 1, 5), dtype='<i8')
    pairs = 0
    uniform_minimum = LAST
    for tau in range(LAST + 1):
        lo, hi, maximum = next(row for row in TABLE if row[0] <= tau <= row[1])
        assert tau <= maximum <= LAST
        assert phase_predicate(tau, tau)
        assert phase_predicate(tau, maximum)
        if maximum < LAST:
            assert not phase_predicate(tau, maximum + 1)
        # For early tau the predicate is monotone decreasing in last:
        # both the quiet deadline and touched-window count are monotone.
        # For late tau every last<=LAST is allowed. Written proof supplies
        # the monotonicity; endpoints verify its closed-form threshold.
        if tau <= CAPTURE_LAST:
            uniform_minimum = min(uniform_minimum, maximum - tau)
        last = min(LAST, tau + 88064)
        assert phase_predicate(tau, last)
        quiet = last + R
        deadline = max(last + R, 407552)
        assert deadline <= U - 1
        rows[tau] = (tau, maximum, last, quiet, deadline)
        pairs += maximum - tau + 1
    analytic_pairs = sum((hi - lo + 1) * (maximum + 1)
                         - (lo + hi) * (hi - lo + 1) // 2
                         for lo, hi, maximum in TABLE)
    assert pairs == analytic_pairs
    assert uniform_minimum == 88064
    witnesses = []
    for tau in (32769, 163841, 294913):
        last = tau + 88065
        quiet = last + R
        touched = [g + 1 for g, (lo, hi) in enumerate(WINDOWS)
                   if tau <= hi and quiet >= lo]
        assert not phase_predicate(tau, last)
        witnesses.append(dict(tau=tau, last=last, hypothetical_quiet=quiet,
                              intersected_windows=touched,
                              reference_guard_closed=quiet < 96 * Q))
    return dict(all_first_fault_rows=LAST + 1, exact_last_row_table=[list(r) for r in TABLE],
                total_admissible_tau_L_pairs=pairs,
                phase_rows_format='little-endian int64 [tau,maxL,uniformL,earlyQuiet,nativeQuiet]',
                phase_rows_sha256=hashlib.sha256(rows.tobytes(order='C')).hexdigest(),
                maximum_uniform_row_difference=88064, maximum_uniform_possible_fault_rows=88065,
                maximal_uniform_bound_for_phase_criterion_only=True,
                criterion_failure_witnesses=witnesses,
                maximum_admitted_native_quiet_row=U - 1)


def compute():
    assert sha(RULE) == '3582a3a7997ddcb17aa916d8c66be3cdf30d099947fefc8e6f802d57d5c98756'
    # Exact inspection relevant to the new early-timing composition.
    # This does not replace the written raw-holder/flag-dependency proof.
    text = RULE.read_text()
    assert "if a['f1']:ml=mr=0" in text
    assert "wipe=a['f1'] and addr!=cells[0].addr" in text
    assert "active=EARLY_BIRTH<age<75*Q or 100*Q+1<age<=127*Q" in text
    sources = [Path(__file__), PROOF, RULE, PARENT]
    return dict(passed=True, schema='GAWN26 extended interior deterministic repair v1',
                Q=Q, U=U, lambda_original=24, error_separation=104,
                unchanged_GAWN2_all_Gray_departures_required=True,
                actual_H2_start_required=True, actual_Address_retained=True,
                all_other_native_fields_and_13SF_adaptive_arbitrary=True,
                fixed_support_inside_1_Qminus1_required=True, no_other_errors_required=True,
                exact_piecewise_phase_criterion_required=True,
                both_endpoint_shields_for_all_interior_widths_proved=True,
                two_actual_outside_banks_proved=True,
                outside_early_execution_not_dependent_on_global_quiet_before75Q_proved=True,
                actual_outside_Info_closes_open_pulse_proved=True,
                native_quiet_max_Lplus10238_407552_proved=True,
                actual_U_encoding_only_upper_record0_bad_proved=True,
                complete_actual_2U_and_all_later_repair_proved=True,
                original_error_class_assigned_from_geometry=False,
                evolving_native_SF_U2U_or_noise_experiment_performed=False,
                optimal_fault_duration_for_rule_or_minimum_sufficient_fix_proved=False,
                GF_boundary_multiple_E0_higher_iid_memory_proved=False,
                faithful_Gray_G17_refutation_proved=False, global_reliability_proved=False,
                rule_ROM_constants_CURRENT_changed=False,
                integer_support_supplements=support_counts(),
                integer_phase_supplements=phase_counts(),
                source_sha256={str(p.relative_to(ROOT)):sha(p) for p in sources})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--issue', action='store_true')
    args = parser.parse_args()
    started = time.perf_counter()
    parent = json.loads(PARENT.read_text())
    assert len(parent['assets_sha256']) == 780
    check_assets(parent['assets_sha256'])
    DATA.mkdir(parents=True, exist_ok=True)
    cp, mp = DATA / 'GAWN26_extended_interior_certificate.json', DATA / 'GAWN26_standalone_assets.json'
    if args.issue:
        assert not cp.exists() and not mp.exists()
        result = compute()
        cp.write_text(json.dumps(result, indent=2) + '\n')
        assets = dict(parent['assets_sha256'])
        for p in (Path(__file__), PROOF, PARENT, cp):
            assets[str(p.relative_to(ROOT))] = sha(p)
        manifest = dict(name=result['schema'], inherited_assets=780, assets_sha256=assets,
                        extended_interior_complete2U_proved=True,
                        global_reliability_proved=False, rule_ROM_constants_CURRENT_changed=False)
        mp.write_text(json.dumps(manifest, indent=2) + '\n')
    else:
        manifest = json.loads(mp.read_text())
        assert manifest['inherited_assets'] == 780
        for path, value in parent['assets_sha256'].items():
            assert manifest['assets_sha256'][path] == value, path
        check_assets(manifest['assets_sha256'])
        result = compute()
        assert result == json.loads(cp.read_text()), 'Fresh arithmetic supplements differ'
    check_assets(manifest['assets_sha256'])
    print(json.dumps(dict(passed=True, issued=args.issue, readonly=not args.issue,
                          assets=len(manifest['assets_sha256']), inherited_assets=780,
                          all_new_integer_supplements_recomputed=True,
                          manifest_sha256=sha(mp), certificate_sha256=sha(cp),
                          extended_interior_complete2U_proved=True,
                          global_reliability_proved=False, rule_ROM_constants_CURRENT_changed=False,
                          elapsed=time.perf_counter()-started), separators=(',', ':')))


if __name__ == '__main__':
    main()
