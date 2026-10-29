#!/usr/bin/env python3
"""Certificate/retained finite runs for the exact Info/native factor.

The symbolic recurrences are proved in SP28_INFO_NATIVE_FACTOR.md. Finite
trajectories from prepared tracks do not prove intact-hierarchy reachability.
"""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import proposed_sparse_distant_epoch1024 as baseline
import proposed_sparse_short_epoch_duration as family


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    started = time.monotonic()
    out = ROOT / 'figs/robustness'
    p = baseline.parameters()
    N = 256 * p.Q
    source = Path(__file__).with_name('native_address_info_factor.c')
    executable = Path('/tmp/SP28_info_factor_certificate')
    subprocess.run(['cc', '-O3', '-std=c11', '-Wall', '-Wextra', '-Werror',
                    str(source), '-o', str(executable)], check=True)
    generated = baseline.generated_source(p)
    assert 'new[f][(slot + 2) * w + i] = n.AND(keep, vals[f][i])' in generated
    assert 'wf1 = n.all([right_end, in_wf, sim_r])' in generated
    assert 'sim_r = n.OR(sim_r, n.AND(w_eq_const(n, addr_now, A_val), lv((Q - 3) - A_val, \'info\')))' in generated
    assert tuple(baseline.SLOTS) == (-2, -1, 0, 1, 2)
    assert (p.T_sig, p.T_wf, p.U) == (278400, 278401, 475136)
    # Exhaustive Boolean identity on the actual five-copy carry/wipe shape.
    boolean_cases = 0
    for bits in range(32):
        majority = int(bits.bit_count() >= 3)
        for keeps in range(32):
            outputs = [majority & ((keeps >> s) & 1) for s in range(5)]
            assert int(sum(outputs) >= 3) == (majority & int(keeps.bit_count() >= 3))
            boolean_cases += 1
    source_routes = 0
    for x in range(p.Q):
        for label in (0, 1):
            addr = (x + 512 * label) % p.Q
            if addr >= p.Q - 5:
                y = x + p.Q - 3 - addr
                assert -2 <= y - x <= 2
                assert y % p.Q == (1021 if label == 0 else 509)
                source_routes += 1
    assert source_routes == 10
    clocks = np.arange(p.T_wf, p.T_wf + 6 * p.Q, dtype=np.int64)
    assert not np.any(clocks == p.T_sig) and not np.any(clocks == p.U - 1)
    packed = np.array([p.age_code(int(t)) for t in clocks])
    assert np.array_equal((packed >= p.age_code(p.T_wf)) &
                         (packed < p.age_code(p.T_wf + 2 * p.Q - 1) + 1),
                         clocks < p.T_wf + 2 * p.Q)
    print(json.dumps(dict(phase='identities_passed', boolean_cases=boolean_cases,
                          source_routes=source_routes)), flush=True)

    def run(case):
        duration, mode = case
        log = out / f'SP28_info_factor_{duration}_mode{mode}_run.jsonl'
        print(json.dumps(dict(phase='run_start', duration=duration, Info_mode=mode)), flush=True)
        with log.open('w') as stream:
            proc = subprocess.run([str(executable), str(duration), str(mode)],
                                  stdout=stream, stderr=subprocess.PIPE, text=True)
        rows = [json.loads(line) for line in log.read_text().splitlines()]
        assert proc.returncode == 0 and not proc.stderr
        assert rows[-1]['stage'] == 'final' and rows[-1]['offset'] == 6 * p.Q
        print(json.dumps(dict(phase='run_done', duration=duration, Info_mode=mode,
                              final=rows[-1])), flush=True)
        return duration, mode, log, rows

    with ThreadPoolExecutor(max_workers=2) as pool:
        runs = list(pool.map(run, [(duration, mode) for duration in (p.Q, 2 * p.Q)
                                  for mode in (0, 1, 2)]))
    frames = {}
    summaries = []
    for duration, mode, log, rows in runs:
        for row in rows:
            name = f'SP28_info_factor_{duration}_mode{mode}_{row["stage"]}_{row["offset"]}'
            raw = Path('/tmp', name + '.bin').read_bytes()
            assert len(raw) == 11 * N
            planes = np.frombuffer(raw[:8 * N], np.uint8).reshape(8, N).copy()
            code = np.frombuffer(raw[8 * N:10 * N], np.uint16).copy()
            info = np.frombuffer(raw[10 * N:], np.uint8).copy()
            assert int(planes[0].sum()) == row['wrong_Addresses']
            assert [int(info[np.arange(residue, N, p.Q)].sum()) for residue in (509, 1021)] == [
                row['Info509_ones'], row['Info1021_ones']]
            frames[name + '_planes'] = planes
            frames[name + '_code'] = code
            frames[name + '_info'] = info
        summaries.append(dict(duration=duration, Info_mode=mode, final=rows[-1],
                              measured_only=True, intact_initial_M_reachability_proved=False))
    asset = out / 'SP28_info_factor_states.npz'
    np.savez_compressed(asset, **frames)
    dependencies = ('SP28_short_epoch_enclosure_gap_certificate.json',
                    'SP28_full_Address_island_certificate.json',
                    'SP28_auxiliary_lifetime_certificate.json',
                    'SP28_info_factor_incomplete_first_run.json')
    result = dict(
        name='Exact actual-Info/native short-pulse factor and prepared finite trajectories',
        Q=p.Q, U=p.U, T_wf=p.T_wf, durations=[p.Q, 2 * p.Q], radius=37,
        pulse_updates=6 * p.Q, periodic_array_cells=N,
        actual_Info_native_closed_factor_proved=True,
        retained_Info_source_residues=[509, 1021],
        Info_majority_monotonicity_without_writes_proved=True,
        exhaustive_carry_wipe_majority_assignments=boolean_cases,
        exact_guarded_two_phase_source_routes=source_routes,
        legal_no_write_clock_cases=len(clocks),
        WF1_reads_old_Info_majority_without_reader_keep_multiplier=True,
        initial_raw_Info_copy_coherence_required=False,
        arbitrary_other_private_and_instruction_inputs_irrelevant_to_factor_proved=True,
        finite_prepared_trajectories_measured_only=summaries,
        actual_intact_history_supplies_prepared_M_patterns_proved=False,
        finite_trajectory_infinite_line_or_all_period_result_claimed=False,
        matching_changed_duration_own_programmes_proved=False,
        finite_eroder_or_all_time_reliability_proved=False,
        global_reliability_established=False,
        no_additional_native_rule_or_interface_change=True,
        existing_Q_2Q_duration_changes_explicit=True,
        active_G17_modified=False, original_SP28_modified=False,
        checker_sha256=digest(__file__), C_source_sha256=digest(source),
        C_executable_sha256=digest(executable),
        proof_sha256=digest(Path(__file__).with_name('SP28_INFO_NATIVE_FACTOR.md')),
        baseline_source_sha256=digest(baseline.__file__),
        family_source_sha256=digest(family.__file__),
        generated_source_sha256=hashlib.sha256(generated.encode()).hexdigest(),
        receipt_dependencies_sha256={name: digest(out / name) for name in dependencies},
        run_logs_sha256={log.name: digest(log) for _, _, log, _ in runs},
        state_asset_sha256=digest(asset), wall_seconds=time.monotonic() - started)
    (out / 'SP28_info_native_factor_certificate.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(phase='certificate_written', full_runs=len(runs),
                          global_reliability_established=False,
                          wall_seconds=result['wall_seconds'])), flush=True)


if __name__ == '__main__':
    main()
