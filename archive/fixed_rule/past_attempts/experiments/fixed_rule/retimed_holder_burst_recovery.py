"""Resume the exact higher-rate burst state; follow quiet physical recovery."""
import argparse
import json
import resource
import time
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import retimed_holder_rule as f, retimed_holder_projected as r
from gacsca.fixed_rule import retimed_holder_active_snapshot as active
from gacsca.fixed_rule import retimed_holder_late_flags as late
from gacsca.fixed_rule import retimed_holder_general_faults as faults
from gacsca.fixed_rule import retimed_holder_cuda_general_snapshot as snapshots
from experiments.fixed_rule.retimed_holder_cuda_encoded_repair import forbidden
from experiments.fixed_rule.run_retimed_holder_streamed_repair import sha

FIELDS = ('bank', 'active_rows', 'counts', 'flags', 'signals', 'age', 'time')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    parser.add_argument('--ticks', type=int, default=16384)
    args = parser.parse_args()
    if not 16 <= args.ticks <= 32768:
        raise ValueError('bounded literal recovery duration required')
    out = Path(args.output)
    artifact = out.with_suffix('.npz')
    if out.exists() or artifact.exists():
        raise FileExistsError(out)
    started = time.perf_counter()
    source_path = Path('figs/fixed_rule/retimed_holder_poisson_burst_8192_v1.json')
    source = json.loads(source_path.read_text())
    assert source['completed'] and not source['final_complete_recovery']
    assert sha(source_path.with_suffix('.npz')) == source['artifact_sha256']
    with np.load(source_path.with_suffix('.npz'), allow_pickle=False) as z:
        state = {k:z['final_'+k].copy() for k in FIELDS}
        initial_positions, initial_values = z['final_positions'].copy(), z['final_values'].copy()
    saved = dict(initial_positions=initial_positions, initial_values=initial_values)
    for key, value in state.items():
        saved['initial_'+key] = value
    observations = []
    targets = {0, *range(1, 9), 16, 128, 1024, 4096, 8192, args.ticks}
    targets = {t for t in targets if t <= args.ticks}
    completed, error = False, None
    with active.restore(state) as healthy, active.restore(state) as background, faults.World(background) as actual:
        actual.inject({int(pos):r.project(f.decode_cell(row)) for pos, row in zip(initial_positions, initial_values)})
        expected_initial = active.render(state)
        expected_initial[initial_positions] = initial_values
        np.testing.assert_array_equal(late.physical(actual), expected_initial)
        saved['before_attach'] = expected_initial
        attachment = late.attach(actual)
        saved['after_attach'] = late.physical(actual)
        peak = healthy.device_bytes + background.device_bytes + actual.device_bytes
        assert peak < 64*1024**2
        start = actual.time
        max_exceptions = len(actual.positions)
        full_evaluations = 0
        def observe(tick):
            with forbidden():
                healthy.advance(actual.time-healthy.time)
            observed, expected = late.physical(actual), active.render(snapshots.snapshot(healthy))
            diff = observed != expected
            positions = np.flatnonzero(np.any(diff, axis=1))
            fields = {name:int(np.count_nonzero(diff[:, k])) for k,(name,_) in enumerate(f.SCHEMA) if np.any(diff[:, k])}
            prefix = f'observe{tick}'
            saved[prefix+'_positions'], saved[prefix+'_values'] = positions, observed[positions]
            for label, world in (('background', background), ('healthy', healthy)):
                for key, value in snapshots.snapshot(world).items():
                    saved[prefix+'_'+label+'_'+key] = value
            row = dict(tick=tick, time=actual.time, discrepant_sites=len(positions), discrepant_words=int(np.count_nonzero(diff)), fields=fields, sparse_exception_sites=len(actual.positions), actual_flag1_sites=int(np.count_nonzero(observed[:, f.COL['f1']])), actual_flag2_sites=int(np.count_nonzero(observed[:, f.COL['f2']])), seconds=time.perf_counter()-started)
            observations.append(row)
            print(json.dumps(row), flush=True)
        try:
            observe(0)
            for tick in range(1, args.ticks+1):
                with forbidden():
                    metric = actual.step()
                full_evaluations += metric['full_local_evaluations']
                max_exceptions = max(max_exceptions, len(actual.positions))
                if tick in targets:
                    observe(tick)
                elif tick % 1024 == 0:
                    print(json.dumps(dict(tick=tick, sparse_exception_sites=len(actual.positions), seconds=time.perf_counter()-started)), flush=True)
            completed = True
        except Exception as exc:
            error = f'{type(exc).__name__}: {exc}'
        for key, value in snapshots.snapshot(background).items():
            saved['final_background_'+key] = value
        positions = actual.positions
        chunks = [np.array([f.encode_cell(cell) for cell in actual.read(positions[i:i+256])], dtype=np.uint64) for i in range(0, len(positions), 256)]
        saved['final_exception_positions'] = np.array(positions, dtype=np.uint64)
        saved['final_exception_values'] = np.concatenate(chunks) if chunks else np.empty((0, f.FIELDS), dtype=np.uint64)
        elapsed = actual.time-start
    np.savez_compressed(artifact, **saved)
    sources = (Path(__file__), Path(late.__file__), Path(active.__file__), Path(faults.__file__), Path(f.__file__))
    result = dict(completed=completed, error=error, requested_ticks=args.ticks, elapsed_physical_ticks=elapsed, attachment=attachment, observations=observations, maximum_sparse_exceptions=max_exceptions, full_exception_evaluations=full_evaluations, explicit_GPU_peak_bytes=peak, source_receipt=str(source_path), source_receipt_sha256=sha(source_path), source_artifact_sha256=source['artifact_sha256'], artifact_sha256=sha(artifact), descriptor_sha256=f.self_description().digest(), source_sha256={str(p):sha(p) for p in sources}, seconds=time.perf_counter()-started, host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, scope='Exact same-time late-flag representation plus literal full-G exception evolution of the saved damaged burst state. Quiet recovery only, no decoded macrostep or permanent-failure claim.')
    out.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k != 'observations'}, indent=2), flush=True)
    if not completed:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
