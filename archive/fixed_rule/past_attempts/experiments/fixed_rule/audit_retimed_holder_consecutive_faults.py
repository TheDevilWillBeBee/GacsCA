"""Independent scalar audit of every retained consecutive-fault output state."""
import argparse
import json
import resource
import time
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import retimed_holder_rule as f, retimed_holder_projected as r
from experiments.fixed_rule.run_retimed_holder_streamed_repair import sha


def scalar_interior(raw):
    cells = [f.decode_cell(row) for row in raw]
    return np.array([f.encode_cell(r.lift(r.project(f.local_step(tuple(cells[i+j] for j in f.NEIGHBORHOOD))))) for i in range(7, len(cells)-7)], dtype=np.uint64)


def sparse(sites, width):
    sites = set(sites)
    starts = {(site-j) % f.Q for site in sites for j in range(width)}
    return all(sum((site-start) % f.Q < width for site in sites) <= 2 for start in starts)


def difference(actual, healthy, left):
    diff = actual != healthy
    return dict(sites=(np.flatnonzero(np.any(diff, axis=1))+left).tolist(), fields=[name for i, (name, _) in enumerate(f.SCHEMA) if np.any(diff[:, i])], raw_words=int(np.count_nonzero(diff)))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    path, out = Path(args.input), Path(args.output)
    if out.exists():
        raise FileExistsError(out)
    started = time.perf_counter()
    receipt = json.loads(path.read_text())
    assert receipt['passed'] and receipt['descriptor_sha256'] == f.self_description().digest()
    artifact = path.with_suffix('.npz')
    assert sha(artifact) == receipt['artifact_sha256']
    assert sha(receipt['checkpoint']) == receipt['checkpoint_sha256']
    for source, digest in receipt['source_sha256'].items():
        assert sha(source) == digest, source
    procedure = {f's{k}_{n}' for k in range(5) for n, _ in f.PROCEDURE}
    outputs = 0
    checks = []
    with np.load(artifact, allow_pickle=False) as saved, np.load(receipt['checkpoint'], allow_pickle=False) as checkpoint:
        for case in receipt['cases']:
            label = case['label']
            healthy = saved[label+'_initial'].copy()
            actual = healthy.copy()
            left = case['initial_left']
            assert len(healthy) < f.Q
            if case['expect_eligible']:
                np.testing.assert_array_equal(healthy, checkpoint['checkpoint_raw'][np.arange(left, left+len(healthy)) % f.Q])
            previous = set()
            prior_discrepancy_ticks = 0
            for row in case['steps']:
                prefix = f"{label}_step{row['tick']}"
                prior = difference(actual, healthy, left)
                assert prior == row['prior']
                positions = list(map(int, saved[prefix+'_positions']))
                assert positions == sorted(set(positions)) == row['current_fault_sites']
                assert sorted(previous) == row['previous_fault_sites']
                replacements = saved[prefix+'_replacements']
                assert replacements.shape == (len(positions), f.FIELDS)
                eligible = sparse(positions, 11) and sparse(previous | set(positions), 5)
                assert eligible == row['eligible']
                if case['expect_eligible']:
                    assert eligible and set(prior['fields']) <= procedure and set(prior['sites']) <= previous
                if positions and prior['raw_words']:
                    prior_discrepancy_ticks += 1
                for pos, replacement in zip(positions, replacements):
                    cell = f.decode_cell(replacement)
                    assert r.lift(r.project(cell)) == cell
                    actual[pos-left] = replacement
                np.testing.assert_array_equal(actual, saved[prefix+'_injected'])
                actual = scalar_interior(actual)
                healthy = scalar_interior(healthy)
                left += 7
                outputs += len(actual)+len(healthy)
                assert left == row['left']
                np.testing.assert_array_equal(actual, saved[prefix+'_actual'])
                np.testing.assert_array_equal(healthy, saved[prefix+'_healthy'])
                after = difference(actual, healthy, left)
                assert after == row['after']
                confined = set(after['sites']) <= set(positions) and set(after['fields']) <= procedure
                assert confined == row['output_confined_to_current_procedures']
                if case['expect_eligible']:
                    assert confined
                previous = set(positions)
            rejoined = np.array_equal(actual, healthy)
            assert rejoined == case['fully_rejoined'] == case['expect_eligible']
            if case['expect_eligible']:
                assert prior_discrepancy_ticks > 0
            else:
                assert all(sparse(row['current_fault_sites'], 11) for row in case['steps'])
                assert not sparse(set(case['steps'][0]['current_fault_sites']) | set(case['steps'][1]['current_fault_sites']), 5)
                assert set(difference(actual, healthy, left)['fields']) <= {f's{k}_data' for k in range(5)}
            check = dict(label=label, steps=len(case['steps']), fully_rejoined=rejoined, noise_ticks_with_existing_discrepancy=prior_discrepancy_ticks, final_differences=difference(actual, healthy, left))
            checks.append(check)
            print(json.dumps(check), flush=True)
    result = dict(passed=True, checks=checks, complete_scalar_output_states=outputs, raw_words_checked=outputs*f.FIELDS, source_receipt_sha256=sha(path), artifact_sha256=sha(artifact), source_sha256={str(x):sha(x) for x in (Path(__file__), Path(f.__file__), Path(r.__file__))}, seconds=time.perf_counter()-started, host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, scope='Every retained output of both actual and healthy finite causal windows, replayed with scalar G independently of the native executor. Positive streams overlap real surviving controller discrepancies; negative stream has individually sparse pulses but violates their union bound.')
    out.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    main()
