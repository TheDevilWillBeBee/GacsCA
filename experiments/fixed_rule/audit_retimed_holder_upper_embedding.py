"""Check the measured upper defect in the complete saved upper colony.

This is a diagnostic full-colony embedding, not an executed lower-lattice
continuation. The lower transfer into this state remains a separate obligation.
All full-ring transitions use the fixed native G; scalar G checks the changing
support and every contextual window output. Nothing is installed in lower state.
"""
import argparse
import json
import resource
import time
from pathlib import Path

import numpy as np

from gacsca.fixed_rule import retimed_holder_rule as f
from gacsca.fixed_rule import retimed_holder_projected as r
from gacsca.fixed_rule import retimed_holder_literal_cone as cone
from experiments.fixed_rule.run_retimed_holder_streamed_repair import sha


def checked_receipt(path):
    path = Path(path)
    result = json.loads(path.read_text())
    assert result.get('completed', result.get('passed', False)), path
    assert result.get('error') is None, path
    assert sha(path.with_suffix('.npz')) == result['artifact_sha256'], path
    for source, digest in result.get('source_sha256', {}).items():
        assert sha(source) == digest, source
    return result


def scalar_outputs(source, target, positions):
    """Full G scalar outputs, including all mutable controller words."""
    for pos in sorted(set(map(int, positions))):
        cells = tuple(r.project(f.decode_cell(source[(pos+d) % len(source)]))
                      for d in f.NEIGHBORHOOD)
        result = f.encode_cell(r.lift(r.local_step(cells)))
        np.testing.assert_array_equal(target[pos], result, err_msg=f'site {pos}')
    return len(set(map(int, positions)))


def differences(actual, healthy):
    return np.flatnonzero(np.any(actual != healthy, axis=1)).tolist()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    out = Path(args.output)
    artifact = out.with_suffix('.npz')
    if out.exists() or artifact.exists():
        raise FileExistsError(out)
    started = time.perf_counter()
    paths = {
        'burst': Path('figs/fixed_rule/retimed_holder_contextual_burst_v1.json'),
        'macrostep': Path('figs/fixed_rule/retimed_holder_contextual_macrostep_v1.json'),
        'continuation': Path('figs/fixed_rule/retimed_holder_contextual_next_periods_3_v1.json'),
    }
    receipts = {name: checked_receipt(path) for name, path in paths.items()}
    with np.load(paths['burst'].with_suffix('.npz'), allow_pickle=False) as saved:
        upper = saved['upper_context'].copy()
        selected = saved['selected_upper_positions'].astype(np.int64)
    with np.load(paths['macrostep'].with_suffix('.npz'), allow_pickle=False) as saved:
        parents = saved['parent_raw'].copy()
        window_actual = cone.normalize(saved['decoded_raw'].copy())
        window_healthy = saved['expected_decoded_raw'].copy()
    assert upper.shape == (f.Q, f.FIELDS)
    assert len(selected) == 17 and len(np.unique(selected)) == 17
    np.testing.assert_array_equal(parents, upper[selected])
    np.testing.assert_array_equal(upper, cone.normalize(upper.copy()))
    np.testing.assert_array_equal(window_healthy, cone.step(parents))
    # This is the measured decoded error, not an arbitrary synthetic mutation.
    bad = differences(window_actual, window_healthy)
    assert bad == [9], bad
    healthy = cone.step(upper)
    checks = scalar_outputs(upper, healthy, selected)
    actual = healthy.copy()
    actual[selected[bad]] = window_actual[bad]
    saved = dict(selected=selected, upper_before=upper,
                 initial_full_healthy=healthy, initial_full_actual=actual)
    rows = []
    with np.load(paths['continuation'].with_suffix('.npz'), allow_pickle=False) as prior:
        for tick in range(4):
            support = differences(actual, healthy)
            window_actual_mismatches = differences(actual[selected], window_actual)
            window_healthy_mismatches = differences(healthy[selected], window_healthy)
            delta_full = actual[selected] != healthy[selected]
            delta_window = window_actual != window_healthy
            row = dict(tick=tick, full_colony_different_sites=support,
                       full_colony_different_raw_words=int(np.count_nonzero(actual != healthy)),
                       window_actual_mismatch_indices=window_actual_mismatches,
                       window_healthy_mismatch_indices=window_healthy_mismatches,
                       difference_field_mask_matches_window=bool(np.array_equal(delta_full, delta_window)))
            rows.append(row)
            saved[f'tick{tick}_actual'] = actual.copy()
            saved[f'tick{tick}_healthy'] = healthy.copy()
            saved[f'tick{tick}_window_actual'] = window_actual.copy()
            saved[f'tick{tick}_window_healthy'] = window_healthy.copy()
            print(json.dumps(row), flush=True)
            if tick == 3:
                break
            next_actual, next_healthy = cone.step(actual), cone.step(healthy)
            possible = {(pos+d) % f.Q for pos in support for d in f.NEIGHBORHOOD}
            next_support = set(differences(next_actual, next_healthy))
            assert next_support <= possible, 'difference escaped declared radius-seven cone'
            probes = possible | set(map(int, selected)) | {0, 1, f.Q-2, f.Q-1}
            checks += scalar_outputs(actual, next_actual, probes)
            checks += scalar_outputs(healthy, next_healthy, probes)
            actual, healthy = next_actual, next_healthy
            window_actual = cone.step(window_actual)
            window_healthy = cone.step(window_healthy)
            np.testing.assert_array_equal(window_actual, prior[f'period{tick+1}_decoded'])
            np.testing.assert_array_equal(window_healthy[:, len(f.STATIC):],
                                          prior[f'period{tick+1}_healthy_upper'])
    # This is a distinguishing diagnostic: save observations even if the
    # larger embedding does not rejoin. Successful execution is not recovery.
    np.savez_compressed(artifact, **saved)
    sources = (Path(__file__), Path(f.__file__), Path(r.__file__), Path(cone.__file__),
               Path(cone.native.__file__))
    result = dict(passed=True, full_upper_sites=f.Q, physical_neighborhood=list(f.NEIGHBORHOOD),
                  initial_measured_error_sites=selected[bad].tolist(), rows=rows,
                  full_colony_rejoined_after_two_steps=not rows[2]['full_colony_different_sites'],
                  scalar_complete_output_checks=checks,
                  full_native_output_states=7*f.Q,
                  source_receipts={str(path):sha(path) for path in paths.values()},
                  source_artifacts={str(path.with_suffix('.npz')):receipts[name]['artifact_sha256']
                                    for name,path in paths.items()},
                  source_sha256={str(path):sha(path) for path in sources},
                  descriptor_sha256=f.self_description().digest(), artifact_sha256=sha(artifact),
                  seconds=time.perf_counter()-started,
                  host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  scope='Diagnostic complete-upper-colony embedding of the measured decoded defect. '
                        'Full native and scalar G transitions with every raw field; no lower transition '
                        'or lower boundary-transfer equivalence is asserted or installed.')
    out.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    main()
