"""Unfiltered full-state Poisson burst at an actual active physical checkpoint.

Every tick is executed by the existing full physical exception evaluator. All
background snapshots and complete exception rows are retained. Recovery is an
observation, not a condition for accepting a noise realization.
"""
import argparse
import json
import resource
import time
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import retimed_holder_rule as f, retimed_holder_projected as r
from gacsca.fixed_rule import retimed_holder_active_snapshot as active
from gacsca.fixed_rule import retimed_holder_cuda_general_snapshot as snapshots
from gacsca.fixed_rule import retimed_holder_general_faults as faults
from gacsca.fixed_rule import retimed_holder_noise_schedule as noise
from gacsca.fixed_rule import retimed_holder_spacetime_domain as domain
from experiments.fixed_rule.retimed_holder_cuda_encoded_repair import forbidden, raw
from experiments.fixed_rule.run_retimed_holder_streamed_repair import sha

FIELDS = ('bank', 'active_rows', 'counts', 'flags', 'signals', 'age', 'time')
PROCEDURE = {f's{k}_{name}' for k in range(5) for name, _ in f.PROCEDURE}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    parser.add_argument('--expected-marks', type=float, required=True)
    parser.add_argument('--ticks', type=int, default=32)
    parser.add_argument('--seed', type=int, default=2026092713)
    args = parser.parse_args()
    if not 1 <= args.ticks <= 64:
        raise ValueError('bounded burst duration required')
    out = Path(args.output)
    artifact = out.with_suffix('.npz')
    if out.exists() or artifact.exists():
        raise FileExistsError(out)
    started = time.perf_counter()
    checkpoint_path = Path('figs/fixed_rule/retimed_holder_active_evaluator_faults_v1.npz')
    checkpoint_receipt = json.loads(checkpoint_path.with_suffix('.json').read_text())
    assert checkpoint_receipt['passed'] and sha(checkpoint_path) == checkpoint_receipt['artifact_sha256']
    with np.load(checkpoint_path, allow_pickle=False) as source:
        checkpoint = {key: source['checkpoint_'+key].copy() for key in FIELDS}
    assert len(checkpoint['bank']) == 1
    sampled = noise.sample(sites=f.Q, ticks=args.ticks, expected_marks=args.expected_marks, seed=args.seed)
    schedule, replacements = sampled.pop('schedule'), sampled.pop('replacements')
    saved = dict(schedule=schedule, replacements=replacements)
    for key, value in checkpoint.items():
        saved['initial_'+key] = value
    groups = {}
    for index, (tick, pos, draw) in enumerate(schedule):
        groups.setdefault(int(tick), []).append(index)
    rows = []
    completed, error = False, None
    with active.restore(checkpoint) as background, faults.World(background) as actual:
        start = actual.time
        peak = background.device_bytes + actual.device_bytes
        assert peak < 64*1024**2
        def exception_snapshot():
            positions = list(actual.positions)
            chunks = [raw(actual.read(positions[i:i+256])) for i in range(0, len(positions), 256)]
            values = np.concatenate(chunks) if chunks else np.empty((0, f.FIELDS), dtype=np.uint64)
            healthy = raw(background.physical_cells(positions)) if positions else values
            diff = values != healthy
            fields = [name for col, (name, _) in enumerate(f.SCHEMA) if np.any(diff[:, col])]
            return np.array(positions, dtype=np.uint64), values, dict(sites=len(positions), raw_words=int(np.count_nonzero(diff)), fields=fields)
        previous_eligible, previous_fault_sites = True, set()
        try:
            for tick in range(1, args.ticks+3):
                with forbidden():
                    metric = actual.step()
                prefix = f'tick{tick}'
                state = snapshots.snapshot(background)
                for key, value in state.items():
                    saved[prefix+'_'+key] = value
                pre_positions, pre_values, pre = exception_snapshot()
                saved[prefix+'_pre_positions'], saved[prefix+'_pre_values'] = pre_positions, pre_values
                confined = set(map(int, pre_positions)) <= previous_fault_sites and set(pre['fields']) <= PROCEDURE
                if previous_eligible:
                    assert confined, 'certified continuing-noise output invariant violated'
                indices = groups.get(tick, [])
                changes = {int(schedule[index, 1]): r.decode_cell(replacements[index]) for index in indices}
                clean = not np.any(state['flags']) and not (f.WF_START <= background.age < f.WF_END)
                eligible = clean and set(pre['fields']) <= PROCEDURE and domain.eligible(tuple(map(int, pre_positions)), changes, size=f.Q)
                if changes:
                    actual.inject(changes)
                post_positions, post_values, post = exception_snapshot()
                saved[prefix+'_post_positions'], saved[prefix+'_post_values'] = post_positions, post_values
                row = dict(tick=tick, time=actual.time, mark_indices=indices, fault_sites=sorted(changes), literal_metrics=metric, pre_noise=pre, post_noise=post, previous_input_eligible=previous_eligible, previous_output_confined=confined, next_input_eligible=eligible)
                rows.append(row)
                previous_eligible, previous_fault_sites = eligible, set(changes)
                if tick % 8 == 0 or tick > args.ticks:
                    print(json.dumps({key:row[key] for key in ('tick', 'pre_noise', 'post_noise', 'next_input_eligible')}), flush=True)
            completed = True
        except Exception as exc:
            error = f'{type(exc).__name__}: {exc}'
        for key, value in snapshots.snapshot(background).items():
            saved['final_'+key] = value
        positions, values, final = exception_snapshot()
        saved['final_positions'], saved['final_values'] = positions, values
        elapsed_ticks = actual.time-start
    np.savez_compressed(artifact, **saved)
    sources = (Path(__file__), Path(noise.__file__), Path(domain.__file__), Path(active.__file__), Path(faults.__file__), Path(snapshots.__file__), Path(f.__file__), Path(r.__file__))
    result = dict(completed=completed, error=error, noise=sampled, noise_ticks=args.ticks, elapsed_physical_ticks=elapsed_ticks, initial_time=int(checkpoint['time']), physical_sites=f.Q, rows=rows, final_complete_recovery=not final['sites'], final=final, filtered_or_resampled_marks=0, representation_rebases=0, checkpoint=str(checkpoint_path), checkpoint_sha256=sha(checkpoint_path), artifact_sha256=sha(artifact), descriptor_sha256=f.self_description().digest(), source_sha256={str(p):sha(p) for p in sources}, explicit_GPU_peak_bytes=peak, seconds=time.perf_counter()-started, host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, scope='Unfiltered independent Poisson full-state burst on 32 or fewer/64 bounded physical ticks at a real active checkpoint, followed by two quiet ticks. No conditioning on repair, no stochastic threshold or full-period/depth-two noise claim.')
    out.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k != 'rows'}, indent=2), flush=True)
    if not completed:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
