"""Advance the exact global contextual recovery endpoint through commit/reset."""
import argparse
import json
import resource
import time
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import retimed_holder_global_events as events
from gacsca.fixed_rule import retimed_holder_contextual_flags as adapter
from gacsca.fixed_rule import retimed_holder_rule as f, retimed_holder_projected as r
from gacsca.fixed_rule import retimed_holder_program as p
from experiments.fixed_rule.run_retimed_holder_streamed_repair import sha

FIELDS = ('bank','active_rows','counts','flags','signals','age','time')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output',required=True)
    parser.add_argument('--pilot-ticks',type=int)
    args = parser.parse_args()
    if args.pilot_ticks is not None and not 1 <= args.pilot_ticks <= 1000000:
        raise ValueError('bounded pilot duration required')
    out = Path(args.output)
    artifact = out.with_suffix('.npz')
    if out.exists() or artifact.exists():
        raise FileExistsError(out)
    started = time.perf_counter()
    source_path = Path('figs/fixed_rule/retimed_holder_contextual_recovery_16384_v1.json')
    source = json.loads(source_path.read_text())
    assert source['completed'] and sha(source_path.with_suffix('.npz')) == source['artifact_sha256']
    with np.load(source_path.with_suffix('.npz'),allow_pickle=False) as z:
        state = {k:z['final_background_'+k].copy() for k in FIELDS}
        view = adapter.View(state,z['final_exception_positions'].copy(),z['final_exception_values'].copy())
    assert not np.any(state['flags'])
    initial_time = int(state['time'])
    world = events.World(view.cells,size=view.base.size,time=initial_time)
    saved = dict(initial_words=world.words.copy(),signals=world.signals.copy())
    targets = [initial_time+args.pilot_ticks] if args.pilot_ticks is not None else [initial_time+4096,initial_time+100000,f.ACTIVE_ENDS[4],f.U-1,f.U,f.U+1]
    checkpoints = []
    completed,error = False,None
    last_update = time.perf_counter()
    try:
        for target in targets:
            while world.time < target:
                metric = world.advance(min(target-world.time,10000000))
                if time.perf_counter()-last_update > 15:
                    print(json.dumps(dict(stage='physical progress',**metric,seconds=time.perf_counter()-started)),flush=True)
                    last_update = time.perf_counter()
            prefix = f'checkpoint{len(checkpoints)}'
            saved[prefix+'_words'],saved[prefix+'_signals'] = world.words.copy(),world.signals.copy()
            row = dict(time=world.time,age=world.age,heads=list(world.heads),trace_events=len(world.trace),metrics=world.advance(0),seconds=time.perf_counter()-started)
            if world.time == f.U:
                burst_path = Path(source['source_receipt'])
                burst = json.loads(burst_path.read_text())
                assert sha(burst_path.with_suffix('.npz')) == burst['artifact_sha256']
                with np.load(burst_path.with_suffix('.npz'),allow_pickle=False) as z:
                    parent_raw = z['upper_context'][z['selected_upper_positions']].copy()
                parents = tuple(r.project(f.decode_cell(cell)) for cell in parent_raw)
                intended = r.step_ring(parents) # diagnostic comparison only
                expected = np.array([f.encode_cell(r.lift(cell)) for cell in intended],dtype=np.uint64)
                decoded = world.words[np.arange(len(parents))[:,None]*f.Q+np.array(p.layout().info),events.COL['data']]
                saved['parent_raw'],saved['decoded_raw'],saved['expected_decoded_raw'] = parent_raw,decoded.copy(),expected
                differences = np.count_nonzero(decoded != expected,axis=1)
                projected = np.count_nonzero(decoded[:,len(f.STATIC):] != expected[:,len(f.STATIC):],axis=1)
                row['decoded_raw_differences_by_colony'] = differences.tolist()
                row['decoded_mutable_differences_by_colony'] = projected.tolist()
                row['decoded_well_typed_by_colony'] = []
                for words in decoded:
                    try:
                        f.decode_cell(words)
                        row['decoded_well_typed_by_colony'].append(True)
                    except ValueError:
                        row['decoded_well_typed_by_colony'].append(False)
            checkpoints.append(row)
            print(json.dumps(row),flush=True)
        completed = True
    except Exception as exc:
        error = f'{type(exc).__name__}: {exc}'
    saved['final_words'],saved['final_signals'] = world.words.copy(),world.signals.copy()
    saved['physical_event_trace'] = np.array(world.trace,dtype=np.uint64).reshape(-1,3)
    np.savez_compressed(artifact,**saved)
    sources = (Path(__file__),Path(events.__file__),Path(events.single.__file__),Path(adapter.__file__),Path(f.__file__),Path(p.__file__),Path(r.__file__))
    result = dict(completed=completed,error=error,colonies=world.size//f.Q,initial_time=initial_time,final_time=world.time,pilot_ticks=args.pilot_ticks,checkpoints=checkpoints,final_metrics=world.advance(0),physical_trace_events=len(world.trace),source_receipt=str(source_path),source_receipt_sha256=sha(source_path),source_artifact_sha256=source['artifact_sha256'],artifact_sha256=sha(artifact),descriptor_sha256=f.self_description().digest(),source_sha256={str(x):sha(x) for x in sources},seconds=time.perf_counter()-started,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,scope='Unchanged physical G on the actual global 17-colony state, retaining all Data, controller fields and boundary copies. Full physical clock steps; guarded transport. Decoded comparison is diagnostic, with independent event-trace audit still required.')
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k != 'checkpoints'},indent=2),flush=True)
    if not completed:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
