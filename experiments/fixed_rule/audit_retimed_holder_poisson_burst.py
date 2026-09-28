"""Complete-lattice native replay, plus scalar probes, of an unfiltered GPU burst."""
import argparse
import json
import resource
import time
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import retimed_holder_rule as f, retimed_holder_projected as r
from gacsca.fixed_rule import retimed_holder_literal_cone as cone
from gacsca.fixed_rule import retimed_holder_noise_schedule as noise
from gacsca.fixed_rule import retimed_holder_active_snapshot as active
from experiments.fixed_rule.run_retimed_holder_streamed_repair import sha

FIELDS = ('bank', 'active_rows', 'counts', 'flags', 'signals', 'age', 'time')


def compare_exceptions(actual, healthy, positions, values, summary):
    diff = actual != healthy
    expected_positions = np.flatnonzero(np.any(diff, axis=1))
    np.testing.assert_array_equal(positions, expected_positions)
    np.testing.assert_array_equal(values, actual[expected_positions])
    fields = [name for col, (name, _) in enumerate(f.SCHEMA) if np.any(diff[:, col])]
    assert summary == dict(sites=len(expected_positions), raw_words=int(np.count_nonzero(diff)), fields=fields)
    return set(map(int, expected_positions)), set(fields)


def sparse(sites, width):
    sites = set(sites)
    return all(sum((p-start) % f.Q < width for p in sites) <= 2 for start in {(p-d) % f.Q for p in sites for d in range(width)})


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
    assert receipt['completed'] and receipt['error'] is None
    assert receipt['descriptor_sha256'] == f.self_description().digest()
    assert receipt['filtered_or_resampled_marks'] == receipt['representation_rebases'] == 0
    artifact = path.with_suffix('.npz')
    assert sha(artifact) == receipt['artifact_sha256'] and sha(receipt['checkpoint']) == receipt['checkpoint_sha256']
    for source, digest in receipt['source_sha256'].items():
        assert sha(source) == digest, source
    sampled = noise.sample(sites=f.Q, ticks=receipt['noise_ticks'], expected_marks=receipt['noise']['expected_marks'], seed=receipt['noise']['seed'])
    procedure = {f's{k}_{n}' for k in range(5) for n, _ in f.PROCEDURE}
    outputs = scalar_outputs = 0
    eligible_inputs = ineligible_inputs = 0
    with np.load(artifact, allow_pickle=False) as saved, np.load(receipt['checkpoint'], allow_pickle=False) as original:
        np.testing.assert_array_equal(saved['schedule'], sampled['schedule'])
        np.testing.assert_array_equal(saved['replacements'], sampled['replacements'])
        checkpoint = {key:saved['initial_'+key] for key in FIELDS}
        for key in FIELDS:
            np.testing.assert_array_equal(checkpoint[key], original['checkpoint_'+key])
        healthy = active.render(checkpoint)
        np.testing.assert_array_equal(healthy, original['checkpoint_raw'])
        actual = healthy.copy()
        previous_eligible, previous_faults = True, set()
        for row in receipt['rows']:
            tick = row['tick']
            prefix = f'tick{tick}'
            probes = {0, f.Q-1, (9565+tick) % f.Q}
            probes.update(map(int, np.flatnonzero(np.any(actual != healthy, axis=1))[:8]))
            scalar = []
            for state in (actual, healthy):
                scalar.append(np.array([f.encode_cell(r.lift(r.project(f.local_step(tuple(f.decode_cell(state[(pos+d) % f.Q]) for d in f.NEIGHBORHOOD))))) for pos in sorted(probes)], dtype=np.uint64))
            actual, healthy = cone.step(actual), cone.step(healthy)
            np.testing.assert_array_equal(actual[sorted(probes)], scalar[0])
            np.testing.assert_array_equal(healthy[sorted(probes)], scalar[1])
            scalar_outputs += 2*len(probes)
            outputs += 2*f.Q
            state = {key:saved[prefix+'_'+key] for key in FIELDS}
            assert int(state['time']) == receipt['initial_time']+tick == row['time']
            np.testing.assert_array_equal(active.render(state), healthy)
            sites, fields = compare_exceptions(actual, healthy, saved[prefix+'_pre_positions'], saved[prefix+'_pre_values'], row['pre_noise'])
            assert row['previous_input_eligible'] == previous_eligible
            confined = sites <= previous_faults and fields <= procedure
            assert confined == row['previous_output_confined']
            if previous_eligible:
                assert confined
            indices = [i for i, item in enumerate(sampled['schedule']) if int(item[0]) == tick]
            assert indices == row['mark_indices']
            current = {int(sampled['schedule'][i, 1]) for i in indices}
            assert sorted(current) == row['fault_sites']
            eligible = fields <= procedure and sparse(current, 11) and sparse(sites | current, 5)
            # Complete healthy reconstruction is canonical, zero-flag and coherent
            # throughout this late 32-tick checkpoint interval, away from capture.
            assert not np.any(state['flags']) and int(state['age']) > f.WF_END+f.Q
            assert eligible == row['next_input_eligible']
            eligible_inputs += int(eligible)
            ineligible_inputs += int(not eligible)
            for i in indices:
                pos = int(sampled['schedule'][i, 1])
                actual[pos] = f.encode_cell(r.lift(r.decode_cell(sampled['replacements'][i])))
            compare_exceptions(actual, healthy, saved[prefix+'_post_positions'], saved[prefix+'_post_values'], row['post_noise'])
            previous_eligible, previous_faults = eligible, current
            if tick % 8 == 0 or tick > receipt['noise_ticks']:
                print(json.dumps(dict(tick=tick, complete_physical_recovery=np.array_equal(actual, healthy), seconds=time.perf_counter()-started)), flush=True)
        assert len(receipt['rows']) == receipt['noise_ticks']+2 == receipt['elapsed_physical_ticks']
        final = {key:saved['final_'+key] for key in FIELDS}
        np.testing.assert_array_equal(active.render(final), healthy)
        compare_exceptions(actual, healthy, saved['final_positions'], saved['final_values'], receipt['final'])
        assert np.array_equal(actual, healthy) == receipt['final_complete_recovery']
    sources = (Path(__file__), Path(cone.__file__), Path(f.__file__), Path(r.__file__), Path(active.__file__), Path(noise.__file__))
    result = dict(passed=True, exact_noise_sample_reproduced=True, realized_marks=receipt['noise']['realized_marks'], complete_native_output_states=outputs, complete_native_output_words=outputs*f.FIELDS, scalar_source_output_states=scalar_outputs, eligible_inputs=eligible_inputs, ineligible_inputs=ineligible_inputs, final_complete_recovery=receipt['final_complete_recovery'], final=receipt['final'], source_receipt_sha256=sha(path), artifact_sha256=sha(artifact), source_sha256={str(p):sha(p) for p in sources}, seconds=time.perf_counter()-started, host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, scope='Every physical lattice output, every injection and every saved complete exception state checked by full native G replay; selected outputs also checked against scalar source. Finite burst result, not a rate threshold or complete noisy work period.')
    out.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    main()
