"""Literal paired fresh-fault probes and an Address-premise counterexample.

All evolving states execute complete physical G. Fault replacements are identical
between paired trajectories; only the initial selected Data overlay differs.
"""
import argparse
import json
from pathlib import Path
import resource
import time
import numpy as np
from gacsca.fixed_rule import retimed_holder_rule as f, retimed_holder_projected as r
from gacsca.fixed_rule import retimed_holder_literal_cone as cone
from experiments.fixed_rule.audit_retimed_holder_prefix_embedding import sha

TARGETS = (30960, 30961, 30962)
VALUES = (648528792106043840, 2418452793257099264, 72061992092962836)


def raw_random(positions, rng):
    out = np.empty((len(positions), f.FIELDS), dtype=np.uint64)
    for j, (_, width) in enumerate(f.SCHEMA):
        out[:, j] = rng.integers(0, 1 << width, size=len(positions), dtype=np.uint64)
    out[:, f.COL['address']] = np.asarray(positions) % f.Q
    return cone.normalize(out)


def support(positions):
    mask = np.zeros((len(positions), f.FIELDS), dtype=bool)
    for d in f.OFFSETS:
        mask[:, f.COL[f's{d+2}_data']] = np.isin(positions+d, TARGETS)
    return mask


def scalar_at(raw, index):
    cells = tuple(r.project(f.decode_cell(row)) for row in raw[index-7:index+8])
    return np.asarray(f.encode_cell(r.lift(r.local_step(cells))), dtype=np.uint64)


def fresh_noise(seed=913, ticks=12):
    if type(ticks) is not int or not 1 <= ticks <= 32:
        raise ValueError('bounded literal probe required')
    rng = np.random.default_rng(seed)
    positions = np.arange(TARGETS[0]-14*ticks-20, TARGETS[-1]+14*ticks+21)
    clean = raw_random(positions, rng)
    actual = clean.copy()
    for a, value in zip(TARGETS, VALUES):
        for d in f.OFFSETS:
            actual[positions+d == a, f.COL[f's{d+2}_data']] = value
            clean[positions+d == a, f.COL[f's{d+2}_data']] = 0
    rows = []
    scalar_words = 0
    for tick in range(ticks):
        # One replaced holder inside the residual support plus three outside.
        # Replacement includes every physical mutable word, with Address fixed.
        fault_sites = np.array([TARGETS[tick % 3], TARGETS[0]-12, TARGETS[-1]+12, TARGETS[-1]+15])
        replacement = raw_random(fault_sites, rng)
        idx = fault_sites-positions[0]
        actual[idx] = replacement
        clean[idx] = replacement
        for current in (actual, clean):
            assert np.array_equal(current[:, f.COL['address']], positions % f.Q)
        next_actual = cone.step(actual)[7:-7].copy()
        next_clean = cone.step(clean)[7:-7].copy()
        # Independent scalar transcription at the complete residual support and
        # at two freshly replaced exterior sites, for both actual trajectories.
        for at in (*range(TARGETS[0]-2, TARGETS[-1]+3), TARGETS[0]-12, TARGETS[-1]+12):
            index = at-int(positions[0])
            for source, target in ((actual, next_actual), (clean, next_clean)):
                np.testing.assert_array_equal(scalar_at(source, index), target[index-7])
                scalar_words += f.FIELDS
        new_positions = positions[7:-7]
        for source, target in ((actual, next_actual), (clean, next_clean)):
            for a in TARGETS:
                inputs = [source[a+e-positions[0], f.COL[f's{2-e}_data']] for e in f.OFFSETS]
                expected = f.majority5(tuple(map(int, inputs)))
                for d in f.OFFSETS:
                    assert int(target[a-d-new_positions[0], f.COL[f's{d+2}_data']]) == expected
        different = next_actual != next_clean
        assert not np.any(different & ~support(new_positions)), 'residual effect escaped Data support'
        assert np.array_equal(next_actual[:, f.COL['address']], new_positions % f.Q)
        assert np.array_equal(next_clean[:, f.COL['address']], new_positions % f.Q)
        rows.append(dict(tick=tick+1, identical_full_state_replacements=len(fault_sites),
                         different_raw_words=int(np.count_nonzero(different)),
                         different_words_outside_selected_Data=0))
        actual, clean, positions = next_actual, next_clean, new_positions
    return dict(passed=True, seed=seed, ticks=ticks, trace=rows,
                independent_scalar_raw_words=scalar_words,
                literal_native_output_words=2*sum((len(positions)+14*(ticks-i-1))*f.FIELDS for i in range(ticks)),
                address_preserving_full_state_faults=4*ticks,
                initial_values=list(VALUES), all_input_clocks_independent_32bit=True,
                scope='Residual separation under fresh Address-preserving replacements; '
                      'neither background controller repair nor arbitrary-Address noise tested here.')


def address_counterexample():
    # A legal one-bit residual illustrates necessity of the Address premise.
    # It is deliberately NOT one of the three observed even-valued residuals.
    a = TARGETS[0]
    positions = np.arange(a-20, a+21)
    clean = np.zeros((len(positions), f.FIELDS), dtype=np.uint64)
    clean[:, f.COL['address']] = positions % f.Q
    clean[:, f.COL['age']] = f.CAPTURE_AGE-1
    cone.normalize(clean)
    actual = clean.copy()
    for d in f.OFFSETS:
        actual[positions+d == a, f.COL[f's{d+2}_data']] = 1
    for e in (-5, -4, -3, 3, 4, 5):
        index = a+e-positions[0]
        replacement = clean[index:index+1].copy()
        replacement[0, f.COL['address']] = (3+e) % f.Q
        cone.normalize(replacement)
        actual[index] = clean[index] = replacement[0]
    index = a-positions[0]
    out_a, out_c = cone.step(actual)[index], cone.step(clean)[index]
    np.testing.assert_array_equal(out_a, scalar_at(actual, index))
    np.testing.assert_array_equal(out_c, scalar_at(clean, index))
    assert out_a[f.COL['address']] == out_c[f.COL['address']] == 3
    assert out_a[f.COL['f1']] == out_c[f.COL['f1']] == 0
    assert out_a[f.COL['age']] == out_c[f.COL['age']] == f.CAPTURE_AGE
    assert out_a[f.COL['signal']] == 4 and out_c[f.COL['signal']] == 0
    return dict(passed=True, same_full_replacements=6,
                fault_offsets=[-5, -4, -3, 3, 4, 5], input_residual_value=1,
                observed_experiment_residual_value=False, target_physical_address=a,
                output_Address=3, output_Flag1=0, output_Age=f.CAPTURE_AGE,
                actual_output_Signal=4, comparison_output_Signal=0,
                independent_scalar_and_native_match=True), dict(
                    positions=positions, actual_input=actual, comparison_input=clean,
                    actual_output=out_a, comparison_output=out_c)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    out = Path(parser.parse_args().output)
    artifact = out.with_suffix('.npz')
    if out.exists() or artifact.exists():
        raise FileExistsError(out)
    started = time.perf_counter()
    cases = [fresh_noise(seed) for seed in (913, 914, 915)]
    witness, arrays = address_counterexample()
    np.savez_compressed(artifact, **arrays)
    sources = (Path(__file__), Path(f.__file__), Path(r.__file__), Path(cone.__file__))
    result = dict(passed=True, fresh_noise_cases=cases, address_counterexample=witness,
                  descriptor_sha256=f.self_description().digest(),
                  source_sha256={str(path): sha(path) for path in sources},
                  artifact_sha256=sha(artifact), seconds=time.perf_counter()-started,
                  host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  scope='Literal complete-rule bounded tests of residual separation and '
                        'a concrete counterexample to removing its Address premise. '
                        'No general error correction or stochastic threshold claim.')
    with out.open('x') as stream:
        stream.write(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    main()
