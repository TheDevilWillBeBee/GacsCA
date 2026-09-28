"""Continue the exact recovered burst state through commit and next reset.

Native full physical G handles literal events and whole-lattice clock events;
the new multihead scheduler skips only guarded physical transport/quiet ticks.
Decoding is diagnostic and never installs the simulated transition.
"""
import argparse
import json
import resource
import time
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import retimed_holder_multihead_events as events
from gacsca.fixed_rule import retimed_holder_active_snapshot as active
from gacsca.fixed_rule import retimed_holder_late_flags as late
from gacsca.fixed_rule import retimed_holder_rule as f, retimed_holder_projected as r
from gacsca.fixed_rule import retimed_holder_program as p
from experiments.fixed_rule.run_retimed_holder_streamed_repair import sha

FIELDS = ('bank', 'active_rows', 'counts', 'flags', 'signals', 'age', 'time')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    parser.add_argument('--pilot-ticks', type=int)
    args = parser.parse_args()
    if args.pilot_ticks is not None and not 1 <= args.pilot_ticks <= 1000000:
        raise ValueError('bounded pilot duration required')
    out = Path(args.output)
    artifact = out.with_suffix('.npz')
    if out.exists() or artifact.exists():
        raise FileExistsError(out)
    started = time.perf_counter()
    source_path = Path('figs/fixed_rule/retimed_holder_burst_recovery_16384_v1.json')
    source = json.loads(source_path.read_text())
    assert source['completed'] and sha(source_path.with_suffix('.npz')) == source['artifact_sha256']
    with np.load(source_path.with_suffix('.npz'), allow_pickle=False) as z:
        state = {k:z['final_background_'+k] for k in FIELDS}
        assert not np.any(state['flags'])
        initial = late.render(state)
        initial[z['final_exception_positions']] = z['final_exception_values']
        initial_time = int(state['time'])
    world = events.World(initial, time=initial_time)
    assert len(world.heads) == 3
    saved = dict(initial=initial)
    targets = [initial_time+args.pilot_ticks] if args.pilot_ticks is not None else [initial_time+4096, initial_time+100000, f.ACTIVE_ENDS[4], f.U-1, f.U, f.U+1]
    checkpoints = []
    completed, error = False, None
    last_update = time.perf_counter()
    try:
        for target in targets:
            while world.time < target:
                metric = world.advance(min(target-world.time, 10000000))
                if time.perf_counter()-last_update > 15:
                    print(json.dumps(dict(stage='progress', **metric, seconds=time.perf_counter()-started)), flush=True)
                    last_update = time.perf_counter()
            current = world.raw()
            prefix = f'checkpoint{len(checkpoints)}'
            saved[prefix] = current
            row = dict(time=world.time, age=world.age, heads=list(world.heads), metrics=world.advance(0), seconds=time.perf_counter()-started)
            if world.time == f.U:
                with np.load('figs/fixed_rule/retimed_holder_active_evaluator_faults_v1.npz', allow_pickle=False) as original:
                    healthy = active.render({k:original['healthy_terminal_'+k] for k in FIELDS})
                saved['healthy_terminal'] = healthy
                words = world.words[list(p.layout().info), events.COL['data']]
                healthy_words = healthy[list(p.layout().info), f.COL['s2_data']]
                saved['decoded_words'], saved['healthy_decoded_words'] = words.copy(), healthy_words.copy()
                row['decoded_raw_word_differences'] = int(np.count_nonzero(words != healthy_words))
                row['complete_physical_raw_word_differences'] = int(np.count_nonzero(current != healthy))
                try:
                    decoded = f.decode_cell(words)
                    r.project(decoded)
                    row['decoded_well_typed'] = True
                except ValueError as exc:
                    row['decoded_well_typed'] = False
                    row['decode_error'] = str(exc)
            checkpoints.append(row)
            print(json.dumps(row), flush=True)
        completed = True
    except Exception as exc:
        error = f'{type(exc).__name__}: {exc}'
    saved['final'] = world.raw()
    np.savez_compressed(artifact, **saved)
    sources = (Path(__file__), Path(events.__file__), Path(f.__file__), Path(p.__file__), Path(late.__file__))
    result = dict(completed=completed, error=error, initial_time=initial_time, final_time=world.time, pilot_ticks=args.pilot_ticks, checkpoints=checkpoints, final_metrics=world.advance(0), source_receipt=str(source_path), source_receipt_sha256=sha(source_path), source_artifact_sha256=source['artifact_sha256'], artifact_sha256=sha(artifact), descriptor_sha256=f.self_description().digest(), source_sha256={str(x):sha(x) for x in sources}, seconds=time.perf_counter()-started, host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, scope='Exact saved burst-state continuation with all heads and out-of-workspace Data preserved. Fixed full local native G at events; guarded physical transport scheduling. Experimental macrostep result pending independent audit.')
    out.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k != 'checkpoints'}, indent=2), flush=True)
    if not completed:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
