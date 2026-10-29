"""Finite supplements and read-only receipts for the written GAWN27 eroder.

Native only. Arbitrary SF is handled by GAWN25's actual projection proof.
The finite selected histories do not prove iid or full-SF recovery.
"""
import argparse
import ctypes
import hashlib
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import time

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE.parent / 'unregistered_gawn25'))
import explore_gawn25 as e

Q, U, T0 = e.Q, e.U, e.T0
DATA = ROOT / 'figs/gray_counterexamples/unregistered_gawn27'
PARENT = ROOT / 'figs/gray_counterexamples/unregistered_gawn25/GAWN25_standalone_assets.json'
PROOF = HERE / 'GAWN27_MANY_OFFSET_PREFIX_ERODER.md'
RULE = HERE.parent / 'unregistered_gawn2/small_rule_gawn2.py'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def assets_ok(assets):
    for path, digest in assets.items():
        assert sha(ROOT / path) == digest, (path, 'hash mismatch')


def bounds(b, duration):
    c0 = min(0, b - 5 * duration)
    dmin = 9 - c0
    n = 16 * ((Q - c0 + 3 + 11) // 12)
    r = duration + Q - 2
    return c0, dmin, r, n, r + n + Q // 2


def arithmetic():
    dig = hashlib.sha256()
    phase_cases = offset_checks = wrap_checks = 0
    for c0 in range(-520, 1):
        delta = np.arange(9 - c0, Q, dtype=np.int32)
        x = np.arange(c0 - 6, c0 + 1, dtype=np.int32)
        apparent = x[:, None] + delta[None, :]
        assert apparent.min() >= 3 and apparent.max() <= Q - 1
        offset_checks += apparent.size
        dig.update(apparent.astype('<i4').tobytes())
        # These are all possible low phases modulo Q for each allowed color.
        negative = -delta[:, None] + np.arange(3, dtype=np.int32)[None, :]
        positive = Q + negative
        assert np.all(negative < c0 - 6)
        inside = positive < Q
        assert np.all(positive[inside] >= 1)
        assert np.all((positive - (Q - delta[:, None]))[inside] <= 2)
        wrap_checks += int(inside.sum())
        dig.update(positive.astype('<i4').tobytes())
        n = 16 * ((Q - c0 + 3 + 11) // 12)
        for phase in range(16):
            h = c0 - max(0, 3 - phase)
            nextphase = (phase + 1) % 16
            allowed = h + (1 if nextphase else -3)
            hnext = c0 - max(0, 3 - nextphase)
            assert hnext <= allowed
            # Exact c increment after m steps: +m minus4 per pulse.
            prefix = [h + m - 4 * ((phase + m) // 16) for m in range(17)]
            assert min(prefix) >= c0 - 3
            assert prefix[-1] == h + 12
            final = h + n - 4 * ((phase + n) // 16)
            assert final >= Q
            dig.update(np.array([c0, phase, h, *prefix, n, final], dtype='<i4').tobytes())
            phase_cases += 1
    assert phase_cases == 521 * 16 == 8336
    c0, dmin, r, n, bound = bounds(0, 104)
    assert (c0, dmin, r, n, bound) == (-520, 529, 4198, 6160, 12406)
    assert bound - 103 == 12303 and T0 + bound == 422008 < T0 + 4 * Q < U - 1
    for delta in range(1, Q):
        time_to_tag = max(1, delta - 2)
        assert Q - time_to_tag - 2 <= Q - delta
        assert time_to_tag <= Q - 2
    return dict(all_c0_phase_cases=phase_cases,
                exact_pre_tag_nonzero_offset_target_inequalities=offset_checks,
                exact_positive_wrap_candidates=wrap_checks,
                all4095_tag_deadlines_checked=True,
                arithmetic_sha256=dig.hexdigest(),
                worst_dmin=529, worst_N=6160, worst_relative_B=12406,
                worst_B_minus_L=12303, worst_absolute_B=422008)


def library(directory):
    path = Path(directory) / 'gawn27.so'
    subprocess.run(['gcc', '-std=c11', '-O3', '-fPIC', '-shared', '-Wall', '-Wextra',
                    str(HERE / 'audit_gawn27.c'), '-o', str(path)], check=True)
    lib = ctypes.CDLL(str(path))
    assert lib.gawn25_site_size() == ctypes.sizeof(e.Site) == e.DT.itemsize
    lib.gawn25_local.argtypes = [ctypes.POINTER(e.Site), ctypes.c_int, ctypes.c_int,
                                ctypes.POINTER(e.Site)]
    lib.gawn25_local.restype = ctypes.c_int
    lib.gawn27_run.argtypes = [ctypes.POINTER(e.Site)] + [ctypes.c_int] * 5 + [
        ctypes.POINTER(ctypes.c_int32), ctypes.POINTER(e.Site), ctypes.POINTER(ctypes.c_int)]
    lib.gawn27_run.restype = ctypes.c_int
    return lib


def local_prefix_checks(lib):
    """Selected templates; universal cases are proved in the Markdown text."""
    rng = random.Random(0x4741574e323701)
    dig = hashlib.sha256()
    count = missing = low_wrap = pulse = 0
    # Free right voters can miss a quorum; all left GF/F2 are actually zero.
    for index in range(4096):
        c0 = (-520, -7, 0)[index % 3]
        delta = rng.randrange(9 - c0, Q)
        wrapped = index % 2 == 0
        x = Q - delta + index % 3 if wrapped else c0 - index % 7
        palette = [0, delta, min(Q - 1, delta + 1), max(9 - c0, delta - 1), Q - 1]
        rows = [[0, rng.randrange(2), 0, rng.randrange(2), 0] for _ in range(17)]
        rows[8] = [rng.choice(palette), rng.randrange(2), rng.randrange(2), rng.randrange(2), 0]
        for j in range(1, 9):
            g = rng.choice(palette)
            tag = int(wrapped and g and Q - g <= x + j < Q)
            if x + j >= Q:
                rows[8 + j] = [0, 0, 0, 0, 0]
            else:
                rows[8 + j] = [g, tag or rng.randrange(2), rng.randrange(2), rng.randrange(2), 0]
        age = (T0 + 13 if index % 4 == 0 else T0)
        raw = (e.Site * 11)(*(e.Site(*v) for v in rows[3:14]))
        result = e.Site()
        assert lib.gawn25_local(raw, x, age + 1, ctypes.byref(result)) == 0
        values = [v[0] for v in rows[9:14]]
        quorum = next((v for v in values if values.count(v) >= 3), None)
        missing += quorum is None
        low_wrap += quorum is not None and quorum != 0 and (x + quorum) % Q <= 2
        is_pulse = (age + 1) % 16 == 0
        pulse += int(is_pulse and quorum is None)
        assert result.offset == 0
        assert result.f2 == int(is_pulse and quorum is None)
        e.actual_check(lib, rows, x, age, rng, dig)
        count += 1
    assert missing > 0 and low_wrap > 0 and pulse > 0
    return dict(selected_full_physical_prefix_kernels=count,
                arbitrary_actual_SF=True, missing_quorum_templates=missing,
                low_phase_wrap_templates=low_wrap, periodic_source_templates=pulse,
                full_kernel_inputs_outputs_sha256=dig.hexdigest(),
                templates_not_exhaustive_universal_proof=True)


def forcing_for(b, width, duration, profile):
    _, dmin, _, _, _ = bounds(b, duration)
    rng = np.random.default_rng(0x27_0000 + b * 131 + width * 13 + duration * 7 + profile)
    result = np.zeros((duration, width), dtype=e.DT)
    if profile == 0:
        colors = np.array([dmin, Q - 1, max(dmin, Q // 2), 0], dtype='<u2')
        result['offset'] = colors[(np.arange(width)[None, :] // 3
                                  + np.arange(duration)[:, None]) % len(colors)]
    elif profile == 1:
        result['offset'] = rng.integers(dmin, Q, size=(duration, width), dtype=np.uint16)
        result['offset'][::3, ::7] = 0
    else:
        colors = np.array([dmin, min(Q - 1, dmin + 1), Q - 1], dtype='<u2')
        result['offset'] = colors[(np.arange(width)[None, :] // 16
                                  + np.arange(duration)[:, None] // 11) % 3]
    for name in e.DT.names[1:]:
        result[name] = rng.integers(0, 2, size=(duration, width), dtype=np.uint8)
    return result


def campaigns(lib, write):
    parameters = [(0,104,104,0), (0,104,104,1), (0,104,1,2),
                  (1,104,104,2), (511,104,104,0), (519,104,104,1),
                  (520,104,104,2), (3992,104,104,0), (3992,104,1,1),
                  (4095,1,104,0), (100,37,17,1), (0,7,16,1)]
    records, assets = [], {}
    for b, width, duration, profile in parameters:
        forcing = forcing_for(b, width, duration, profile)
        c0, dmin, r, n, bound = bounds(b, duration)
        events = np.zeros((bound + 1, 16), dtype='<i4')
        final = np.zeros(10 * bound + width + 33, dtype=e.DT)
        summary = (ctypes.c_int * 12)()
        status = lib.gawn27_run(forcing.ctypes.data_as(ctypes.POINTER(e.Site)),
                               width, duration, b, T0, bound,
                               events.ctypes.data_as(ctypes.POINTER(ctypes.c_int32)),
                               final.ctypes.data_as(ctypes.POINTER(e.Site)), summary)
        assert status == 0 and summary[0] == 0, (b, width, duration, profile, list(summary))
        assert list(summary)[6:11] == [c0, dmin, r, n, bound]
        assert np.all(events[:,13:] == 0)
        assert np.all(events[r+n, [1,3]] == 0)
        assert np.all(events[-1,1:6] == 0)
        assert not any(np.any(final[name]) for name in e.DT.names)
        assert 0 <= summary[3] <= bound
        name = f'GAWN27_b{b}_w{width}_d{duration}_p{profile}.npz'
        path = DATA / name
        arrays = dict(forcing=forcing, events=events, final=final)
        if write:
            np.savez_compressed(path, **arrays)
        else:
            with np.load(path) as previous:
                assert set(previous.files) == set(arrays)
                for key, value in arrays.items():
                    assert np.array_equal(previous[key], value), (name, key)
        assets[str(path.relative_to(ROOT))] = sha(path)
        records.append(dict(b=b,width=width,duration=duration,profile=profile,c0=c0,dmin=dmin,
                            R_relative=r,N=n,B_relative=bound,
                            first_measured_native_quiet=int(summary[3]),
                            last_measured_GF_wrong=int(summary[4]),
                            measured_native_sites_checked=int(summary[11]),
                            no_quorum_inputs=int(events[:,10].sum()),
                            periodic_source3_updates=int(events[:,11].sum()),
                            every_row_invariant_violations=0,
                            distinct_forced_offsets=int(len(np.unique(forcing['offset']))),
                            forcing_sha256=hashlib.sha256(forcing.tobytes()).hexdigest(),
                            events_sha256=hashlib.sha256(events.tobytes()).hexdigest(),
                            final_sha256=hashlib.sha256(final.tobytes()).hexdigest(),
                            receipt=str(path.relative_to(ROOT))))
    return dict(selected_native_histories=len(records),
                all_selected_every_row_invariants_passed=True,
                measured_sites_checked=sum(r['measured_native_sites_checked'] for r in records),
                total_no_quorum_inputs=sum(r['no_quorum_inputs'] for r in records),
                total_periodic_source3_updates=sum(r['periodic_source3_updates'] for r in records),
                maximum_measured_native_quiet=max(r['first_measured_native_quiet'] for r in records),
                records=records, assets_sha256=assets)


def compute(write):
    assert sha(RULE) == '3582a3a7997ddcb17aa916d8c66be3cdf30d099947fefc8e6f802d57d5c98756'
    with tempfile.TemporaryDirectory(prefix='gawn27_checked_') as directory:
        lib = library(directory)
        kernels = local_prefix_checks(lib)
        histories = campaigns(lib, write)
    sources = [Path(__file__), HERE / 'audit_gawn27.c', PROOF, RULE, PARENT,
               e.HERE / 'gawn25_many_offset_native.c', e.HERE / 'explore_gawn25.py']
    return dict(passed=True, schema='GAWN27 many-offset common-clock prefix eroder v1',
                Q=Q,U=U,lambda_original=24,error_separation=104,
                unchanged_frozen_GAWN2_all_Gray_departures_required=True,
                actual_H2_T0_start_required=True,adaptive_arbitrary_4flags_13SF=True,
                correct_common_Age_retained_required=True,
                offset_palette_0_or_9minus_c0_to_Qminus1_required=True,
                single_inside_true_colony_interval_required=True,
                width_duration_at_most104_required=True,no_other_errors_required=True,
                missing_quorum_periodic_Flag2_source_included=True,
                capped_phase_prefix_and_simultaneous_color_tags_proved=True,
                universal_native_deadline_for_stated_class_proved=True,
                native_persists_through_current_U_boundary_proved=True,
                arbitrary_all_offset_or_Age_native_eroder_proved=False,
                full_SF_U_encoding_2U_repair_proved=False,
                surrounding_E0_higher_iid_positive_epsilon_proved=False,
                faithful_Gray_G17_refutation_or_minimal_global_fix_proved=False,
                global_reliability_proved=False,rule_ROM_constants_CURRENT_changed=False,
                complete_physical_SF_history_simulated=False,
                arithmetic=arithmetic(),selected_actual_kernels=kernels,
                selected_native_campaigns=histories,
                source_sha256={str(p.relative_to(ROOT)):sha(p) for p in sources})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--issue',action='store_true')
    args = parser.parse_args()
    started = time.perf_counter()
    parent = json.loads(PARENT.read_text())
    inherited = parent['assets_sha256']
    assert len(inherited) == 914
    assets_ok(inherited)
    DATA.mkdir(parents=True,exist_ok=True)
    cp = DATA / 'GAWN27_prefix_eroder_certificate.json'
    mp = DATA / 'GAWN27_standalone_assets.json'
    if args.issue:
        assert not cp.exists() and not mp.exists()
        result = compute(True)
        cp.write_text(json.dumps(result,indent=2)+'\n')
        assets = dict(inherited)
        assets.update(result['selected_native_campaigns']['assets_sha256'])
        for path in [Path(__file__),HERE/'audit_gawn27.c',PROOF,PARENT,cp]:
            assets[str(path.relative_to(ROOT))] = sha(path)
        manifest = dict(name=result['schema'],inherited_assets=len(inherited),assets_sha256=assets,
                        universal_native_deadline_for_stated_class_proved=True,
                        global_reliability_proved=False,rule_ROM_constants_CURRENT_changed=False)
        mp.write_text(json.dumps(manifest,indent=2)+'\n')
    else:
        manifest = json.loads(mp.read_text())
        assert manifest['inherited_assets'] == len(inherited)
        for path,digest in inherited.items():
            assert manifest['assets_sha256'][path] == digest,path
        assets_ok(manifest['assets_sha256'])
        result = compute(False)
        assert result == json.loads(cp.read_text()),'Fresh supplements differ'
    assets_ok(manifest['assets_sha256'])
    print(json.dumps(dict(passed=True,issued=args.issue,readonly=not args.issue,
                          assets=len(manifest['assets_sha256']),inherited_assets=len(inherited),
                          all_new_finite_supplements_recomputed=True,
                          manifest_sha256=sha(mp),certificate_sha256=sha(cp),
                          universal_native_deadline_for_stated_class_proved=True,
                          global_reliability_proved=False,rule_ROM_constants_CURRENT_changed=False,
                          elapsed=time.perf_counter()-started),separators=(',',':')))


if __name__ == '__main__':
    main()
