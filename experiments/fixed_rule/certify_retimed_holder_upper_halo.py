"""Verify a sufficient upper halo for the next physical lower-window run.

The 73-cell window preserves the central 17 cells for four radius-seven steps.
The measured defect is conditionally embedded after the first step; this is
not evidence that a lower burst transfers identically in the larger window.
"""
import argparse
import json
import resource
import time
from pathlib import Path

import numpy as np

from gacsca.fixed_rule import retimed_holder_rule as f
from gacsca.fixed_rule import retimed_holder_literal_cone as cone
from experiments.fixed_rule.audit_retimed_holder_upper_embedding import scalar_outputs
from experiments.fixed_rule.run_retimed_holder_streamed_repair import sha


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    out = Path(args.output)
    artifact = out.with_suffix('.npz')
    if out.exists() or artifact.exists():
        raise FileExistsError(out)
    started = time.perf_counter()
    source = Path('figs/fixed_rule/retimed_holder_upper_embedding_v1.json')
    receipt = json.loads(source.read_text())
    assert receipt['passed'] and sha(source.with_suffix('.npz')) == receipt['artifact_sha256']
    for path, digest in receipt['source_sha256'].items():
        assert sha(path) == digest, path
    radius, steps = max(abs(x) for x in f.NEIGHBORHOOD), 4
    assert tuple(f.NEIGHBORHOOD) == tuple(range(-radius, radius+1))
    halo = radius*steps
    saved, rows, scalar_checks = {}, [], 0
    with np.load(source.with_suffix('.npz'), allow_pickle=False) as previous:
        selected = previous['selected']
        np.testing.assert_array_equal(selected, (selected[0]+np.arange(len(selected))) % f.Q)
        positions = (int(selected[0])-halo+np.arange(len(selected)+2*halo)) % f.Q
        target = np.arange(halo, halo+len(selected))
        np.testing.assert_array_equal(positions[target], selected)
        initial = previous['upper_before'][positions].copy()
        healthy = cone.step(initial)
        actual = healthy.copy()
        measured_sites = receipt['initial_measured_error_sites']
        for pos in measured_sites:
            at = np.flatnonzero(positions == pos)
            assert len(at) == 1 and int(at[0]) in target
            actual[int(at[0])] = previous['initial_full_actual'][pos]
        saved.update(positions=positions, target=target, initial=initial)
        for tick in range(steps):
            # A margin of radius*(tick+1) removes every artificial wrap path.
            margin = radius*(tick+1)
            safe = np.arange(margin, len(positions)-margin)
            assert set(target) <= set(safe)
            full_actual = previous[f'tick{tick}_actual']
            full_healthy = previous[f'tick{tick}_healthy']
            np.testing.assert_array_equal(actual[safe], full_actual[positions[safe]])
            np.testing.assert_array_equal(healthy[safe], full_healthy[positions[safe]])
            rows.append(dict(upper_steps_from_original=tick+1, safe_window_indices=safe.tolist(),
                             safe_complete_raw_words_per_trajectory=len(safe)*f.FIELDS,
                             central_17_complete_raw_words_equal=True))
            saved[f'tick{tick}_actual'] = actual.copy()
            saved[f'tick{tick}_healthy'] = healthy.copy()
            if tick+1 < steps:
                next_actual, next_healthy = cone.step(actual), cone.step(healthy)
                scalar_checks += scalar_outputs(actual, next_actual, target)
                scalar_checks += scalar_outputs(healthy, next_healthy, target)
                actual, healthy = next_actual, next_healthy
    np.savez_compressed(artifact, **saved)
    from experiments.fixed_rule import audit_retimed_holder_upper_embedding as embedding
    sources = (Path(__file__), Path(embedding.__file__), Path(f.__file__), Path(cone.__file__))
    result = dict(passed=True, radius=radius, upper_steps=steps, window_cells=len(positions),
                  central_cells=len(target), halo_each_side=halo, rows=rows,
                  scalar_complete_output_checks=scalar_checks,
                  all_central_raw_fields_match_full_colony=True,
                  sufficient_by_declared_radius_not_claimed_minimal=True,
                  source_receipt=str(source), source_receipt_sha256=sha(source),
                  source_artifact_sha256=receipt['artifact_sha256'],
                  source_sha256={str(path):sha(path) for path in sources},
                  descriptor_sha256=f.self_description().digest(), artifact_sha256=sha(artifact),
                  seconds=time.perf_counter()-started,
                  host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  scope='Upper-rule halo certificate for four steps, conditional on the measured '
                        'decoded defect at the first step. No full lower-lattice noisy transfer '
                        'or subsequent physical lower periods are asserted.')
    out.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    main()
