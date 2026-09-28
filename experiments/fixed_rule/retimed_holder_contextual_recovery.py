"""Continue the saved physical burst across real lower-colony boundaries."""
import argparse
import json
import resource
import time
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import retimed_holder_rule as f, retimed_holder_projected as r
from gacsca.fixed_rule import retimed_holder_contextual_flags as adapter
from gacsca.fixed_rule import retimed_holder_general_faults as faults
from gacsca.fixed_rule import retimed_holder_cuda_general_snapshot as snapshots
from experiments.fixed_rule.retimed_holder_cuda_encoded_repair import forbidden
from experiments.fixed_rule.run_retimed_holder_streamed_repair import sha

FIELDS = ('bank','active_rows','counts','flags','signals','age','time')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    parser.add_argument('--ticks', type=int, default=16384)
    args = parser.parse_args()
    if not 16 <= args.ticks <= 32768:
        raise ValueError('bounded quiet duration required')
    out = Path(args.output)
    artifact = out.with_suffix('.npz')
    if out.exists() or artifact.exists():
        raise FileExistsError(out)
    started = time.perf_counter()
    source_path = Path('figs/fixed_rule/retimed_holder_contextual_burst_v1.json')
    source = json.loads(source_path.read_text())
    assert source['completed'] and source['error'] is None
    assert sha(source_path.with_suffix('.npz')) == source['artifact_sha256']
    with np.load(source_path.with_suffix('.npz'), allow_pickle=False) as z:
        state = {k:z['final_background_'+k].copy() for k in FIELDS}
        positions, values = z['final_positions'].copy(), z['final_values'].copy()
    saved = dict(initial_positions=positions, initial_values=values)
    def save(prefix, snapshot):
        for key, value in snapshot.items():
            saved[prefix+'_'+key] = value
    save('initial', state)
    targets = {0,1,2,8,128,1024,1774,1775,1776,1777,2048,4096,8192,args.ticks}
    observations = []
    completed, error = False, None
    with adapter.restore(state) as healthy, adapter.restore(state) as background, faults.World(background) as actual:
        actual.inject({int(pos):r.project(f.decode_cell(row)) for pos,row in zip(positions,values)})
        initial = adapter.View(*adapter.capture(actual))
        expected = adapter.View(state,positions,values)
        for col in range(background.colonies):
            sites = np.arange(col*f.Q,(col+1)*f.Q)
            np.testing.assert_array_equal(initial.cells(sites),expected.cells(sites))
        attachment = adapter.attach(actual)
        attached, attached_positions, attached_values = adapter.capture(actual)
        save('attached',attached)
        saved['attached_positions'],saved['attached_values'] = attached_positions,attached_values
        peak = healthy.device_bytes+background.device_bytes+actual.device_bytes
        assert peak < 64*1024**2
        max_exceptions, evaluations = len(actual.positions),0
        start = actual.time
        def observe(tick):
            with forbidden():
                healthy.advance(actual.time-healthy.time)
            bg,ep,ev = adapter.capture(actual)
            hs = snapshots.snapshot(healthy)
            av,hv = adapter.View(bg,ep,ev),adapter.View(hs)
            all_positions,all_values = [],[]
            counts = np.zeros(f.FIELDS,dtype=np.int64)
            flags = [0,0]
            extra_heads = []
            for col in range(background.colonies):
                sites = np.arange(col*f.Q,(col+1)*f.Q)
                a,h = av.cells(sites),hv.cells(sites)
                diff = a != h
                selected = np.flatnonzero(np.any(diff,axis=1))
                all_positions.append(sites[selected]);all_values.append(a[selected])
                counts[:] += np.count_nonzero(diff,axis=0)
                for k,name in enumerate(('f1','f2')):
                    flags[k] += int(np.count_nonzero(a[:,f.COL[name]]))
                heads = np.flatnonzero((a[:,f.COL['s2_head']] != 0) & diff[:,f.COL['s2_head']])
                extra_heads.extend((col*f.Q+heads).tolist())
            pp,vv = np.concatenate(all_positions),np.concatenate(all_values)
            prefix = f'observe{tick}'
            saved[prefix+'_positions'],saved[prefix+'_values'] = pp,vv
            save(prefix+'_background',bg);save(prefix+'_healthy',hs)
            row = dict(tick=tick,time=actual.time,discrepant_sites=len(pp),discrepant_words=int(counts.sum()),fields={name:int(counts[k]) for k,(name,_) in enumerate(f.SCHEMA) if counts[k]},affected_lower_colonies=sorted(set((pp//f.Q).tolist())),extra_primary_head_positions=extra_heads,sparse_exception_sites=len(ep),actual_flag1_sites=flags[0],actual_flag2_sites=flags[1],seconds=time.perf_counter()-started)
            observations.append(row)
            print(json.dumps(row),flush=True)
        try:
            observe(0)
            for tick in range(1,args.ticks+1):
                with forbidden():
                    metric = actual.step()
                evaluations += metric['full_local_evaluations']
                max_exceptions = max(max_exceptions,len(actual.positions))
                if tick in targets:
                    observe(tick)
                elif tick % 1024 == 0:
                    print(json.dumps(dict(tick=tick,sparse_exception_sites=len(actual.positions),seconds=time.perf_counter()-started)),flush=True)
            completed = True
        except Exception as exc:
            error = f'{type(exc).__name__}: {exc}'
        final,ep,ev = adapter.capture(actual)
        save('final_background',final)
        saved['final_exception_positions'],saved['final_exception_values'] = ep,ev
        elapsed = actual.time-start
    np.savez_compressed(artifact,**saved)
    sources = (Path(__file__),Path(adapter.__file__),Path(faults.__file__),Path(f.__file__))
    result = dict(completed=completed,error=error,colonies=len(state['bank']),requested_ticks=args.ticks,elapsed_physical_ticks=elapsed,attachment=attachment,observations=observations,maximum_sparse_exceptions=max_exceptions,full_exception_evaluations=evaluations,explicit_GPU_peak_bytes=peak,source_receipt=str(source_path),source_receipt_sha256=sha(source_path),source_artifact_sha256=source['artifact_sha256'],artifact_sha256=sha(artifact),descriptor_sha256=f.self_description().digest(),source_sha256={str(p):sha(p) for p in sources},seconds=time.perf_counter()-started,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,scope='Exact contextual burst continuation in the unchanged 17-colony physical ring, including cross-colony exceptions. No full noisy macrostep or receiving-layer repair claim.')
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k != 'observations'},indent=2),flush=True)
    if not completed:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
