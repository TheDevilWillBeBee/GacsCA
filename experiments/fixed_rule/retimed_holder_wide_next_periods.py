"""Physical continuation from the wider damaged commit, retaining all inert Data."""
import argparse
import json
import resource
import time
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import retimed_holder_wide_inert_storage as storage
from gacsca.fixed_rule import retimed_holder_rule as f,retimed_holder_projected as r
from gacsca.fixed_rule import retimed_holder_program as p,retimed_holder_core as c
from experiments.fixed_rule.retimed_holder_cuda_encoded_repair import forbidden
from experiments.fixed_rule.run_retimed_holder_streamed_repair import sha


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output',required=True)
    parser.add_argument('--periods',type=int,default=0)
    args = parser.parse_args()
    if not 0<=args.periods<=3:
        raise ValueError('bounded continuation experiment required')
    out = Path(args.output)
    artifact = out.with_suffix('.npz')
    if out.exists() or artifact.exists():
        raise FileExistsError(out)
    started = time.perf_counter()
    source_path = Path('figs/fixed_rule/retimed_holder_wide_macrostep_v1.json')
    source = json.loads(source_path.read_text())
    assert source['completed'] and source['error'] is None
    assert sha(source_path.with_suffix('.npz')) == source['artifact_sha256']
    with np.load(source_path.with_suffix('.npz'),allow_pickle=False) as z:
        words,signals = z['final_words'].copy(),z['final_signals'].copy()
        decoded_before = z['decoded_raw'].copy()
        healthy_upper = tuple(r.project(f.decode_cell(x)) for x in z['expected_decoded_raw'])
    g = p.layout()
    normalized_words = words.copy()
    expected_info = np.array([f.encode_cell(r.lift(r.project(f.decode_cell(x)))) for x in decoded_before],dtype=np.uint64)
    for col in range(len(decoded_before)):
        np.testing.assert_array_equal(words[col*f.Q+np.array(g.info),storage.DATA],decoded_before[col])
        normalized_words[col*f.Q+np.array(g.info),storage.DATA] = expected_info[col]
    # The checked fixed stage-zero normalization prefix has 49 LOAD/META pairs
    # and six five-instruction address calculations, then starts gathering.
    prefix = 49*2+6*5
    assert sum(op.kind==c.META for op in g.instructions[:prefix]) == 49
    assert not any(op.kind==c.SEND for op in g.instructions[:prefix])
    assert g.instructions[prefix].kind == c.LIT
    normalization_age = g.schedule(0,prefix)[0]+2
    first_send = next(i for i,op in enumerate(g.instructions) if op.kind==c.SEND)
    assert normalization_age < g.schedule(0,first_send+1)[0]
    saved = dict(decoded_before=decoded_before,expected_normalized_info=expected_info)
    def save(prefix,state):
        for key,value in state.items():saved[prefix+'_'+key] = value
    rows=[]
    completed,error = False,None
    with storage.World(words,signals,time=source['final_time']) as actual, storage.World(normalized_words,signals,time=source['final_time']) as normalized:
        initial_actual,initial_normal = actual.snapshot(),normalized.snapshot()
        save('initial_actual',initial_actual);save('initial_normalized',initial_normal)
        saved['retained_positions'],saved['retained_values'] = actual.positions.copy(),actual.values.copy()
        np.testing.assert_array_equal(actual.positions,normalized.positions)
        np.testing.assert_array_equal(actual.values,normalized.values)
        initial_bank_differences = int(np.count_nonzero(initial_actual['bank']!=initial_normal['bank']))
        assert initial_bank_differences>0
        peak_bound = actual.device_bytes+normalized.device_bytes+32*1024**2+32*(len(words)//64)+2*(len(words)//f.Q)
        assert peak_bound<64*1024**2
        try:
            target = f.U+normalization_age
            with forbidden():
                a_metrics=actual.advance(target-actual.time,extra_device_budget=32*1024**2)
                n_metrics=normalized.advance(target-normalized.time,extra_device_budget=32*1024**2)
            a,n = actual.snapshot(),normalized.snapshot()
            save('normalization_actual',a);save('normalization_reference',n)
            for key in a:np.testing.assert_array_equal(a[key],n[key],err_msg=key)
            np.testing.assert_array_equal(a['bank'][:,g.info],expected_info)
            av,nv = actual.view(),normalized.view()
            for start in range(0,len(words),f.Q):
                sites=np.arange(start,start+f.Q)
                np.testing.assert_array_equal(av.cells(sites),nv.cells(sites))
            normalization=dict(age=normalization_age,time=target,complete_raw_words_equal=len(words)*f.FIELDS,physical_actual_metrics=a_metrics,physical_reference_metrics=n_metrics,Info_metadata_regenerated_physically=True,mutable_Info_unchanged=True,seconds=time.perf_counter()-started)
            print(json.dumps(dict(stage='actual physical metadata coupling',**normalization)),flush=True)
            current = tuple(r.project(f.decode_cell(x)) for x in decoded_before)
            for step in range(1,args.periods+1):
                target = (step+1)*f.U
                with forbidden():
                    metrics=actual.advance(target-actual.time,extra_device_budget=32*1024**2)
                state=actual.snapshot();save(f'period{step}',state)
                info=state['bank'][:,g.info]
                current,healthy_upper=r.step_ring(current),r.step_ring(healthy_upper)
                expected=np.array([f.encode_cell(r.lift(x)) for x in current],dtype=np.uint64)
                np.testing.assert_array_equal(info,expected)
                saved[f'period{step}_decoded']=info.copy()
                saved[f'period{step}_healthy_upper']=r.array_from_cells(healthy_upper)
                decoded=tuple(r.project(f.decode_cell(x)) for x in info)
                differences=[i for i,(x,y) in enumerate(zip(decoded,healthy_upper)) if x!=y]
                view=actual.view()
                np.testing.assert_array_equal(view.words[actual.positions,storage.DATA],actual.values)
                row=dict(step=step,time=actual.time,decoded_matches_actual_rule_macrostep=True,upper_cells_differing_from_matching_healthy_window=differences,retained_Data_words=len(actual.positions),metrics=metrics,seconds=time.perf_counter()-started)
                rows.append(row);print(json.dumps(row),flush=True)
            completed=True
        except Exception as exc:
            error=f'{type(exc).__name__}: {exc}'
            normalization=locals().get('normalization')
        save('final',actual.snapshot())
        final_time=actual.time
        initialization=actual.initialization
    np.savez_compressed(artifact,**saved)
    sources=(Path(__file__),Path(storage.__file__),Path(storage.general.__file__),Path(f.__file__),Path(p.__file__),Path(r.__file__))
    result=dict(completed=completed,error=error,requested_periods=args.periods,final_time=final_time,initialization=initialization,initial_metadata_bank_differences=initial_bank_differences,normalization=normalization,periods=rows,explicit_GPU_peak_bound_bytes=peak_bound,source_receipt=str(source_path),source_receipt_sha256=sha(source_path),source_artifact_sha256=source['artifact_sha256'],inert_certificate=str(storage.CERTIFICATE),inert_certificate_sha256=sha(storage.CERTIFICATE),artifact_sha256=sha(artifact),descriptor_sha256=f.self_description().digest(),source_sha256={str(x):sha(x) for x in sources},seconds=time.perf_counter()-started,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,scope='Actual physical lower periods after the damaged contextual commit, with separately retained descriptor-certified Data. A normalized diagnostic twin only establishes physical coupling; no reference state is installed. Upper comparisons are diagnostic. Periodic 73-colony context, not a full-Q noisy ring or threshold experiment.')
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2),flush=True)
    if not completed:raise SystemExit(1)


if __name__=='__main__':
    main()
