"""Audit physical entry normalization and complete subsequent terminal states.

Native global physical events and independent guarded scalar replay verify the
GPU normalization prefix. Existing diagnostic terminal formulas check every
bank word, controller, Signal and flag at each actual GPU macrostep. Diagnostic
results are never uploaded into an evolving state.
"""
import argparse
import json
import resource
import time
from pathlib import Path
from types import SimpleNamespace
import numpy as np
from gacsca.fixed_rule import retimed_holder_wide_inert_storage as storage
from gacsca.fixed_rule import retimed_holder_compiled_events as events
from gacsca.fixed_rule import retimed_holder_rule as f,retimed_holder_projected as r
from gacsca.fixed_rule import retimed_holder_program as p
from gacsca.fixed_rule import retimed_holder_terminal_reference as terminal
from gacsca.fixed_rule import retimed_holder_literal_cone as cone
from experiments.fixed_rule.audit_retimed_holder_contextual_macrostep import Replay,TransportGuard
from experiments.fixed_rule.certify_retimed_holder_inert_data import certify
from experiments.fixed_rule.run_retimed_holder_streamed_repair import sha

FIELDS=('bank','active_rows','counts','flags','signals','age','time')


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--input',required=True)
    parser.add_argument('--output',required=True)
    args=parser.parse_args();path,out=Path(args.input),Path(args.output)
    if out.exists():raise FileExistsError(out)
    started=time.perf_counter();receipt=json.loads(path.read_text())
    assert receipt['completed'] and receipt['error'] is None
    assert sha(path.with_suffix('.npz'))==receipt['artifact_sha256']
    assert sha(receipt['source_receipt'])==receipt['source_receipt_sha256']
    assert sha(Path(receipt['source_receipt']).with_suffix('.npz'))==receipt['source_artifact_sha256']
    assert sha(receipt['inert_certificate'])==receipt['inert_certificate_sha256']
    for source,digest in receipt['source_sha256'].items():assert sha(source)==digest,source
    proof=certify();prior=storage.certificate()
    for key,value in proof.items():assert prior[key]==value,key
    observations=[];raw_words_checked=0
    with np.load(path.with_suffix('.npz'),allow_pickle=False) as saved,np.load(Path(receipt['source_receipt']).with_suffix('.npz'),allow_pickle=False) as original:
        def state(prefix):return {k:saved[prefix+'_'+k] for k in FIELDS}
        words,signals=original['final_words'],original['final_signals']
        size=len(words);g=p.layout()
        positions,values=saved['retained_positions'],saved['retained_values']
        mask=(np.arange(size)%f.Q>=g.memory_count)&(np.arange(size)%f.Q<f.Q-5)&(words[:,storage.DATA]!=0)
        np.testing.assert_array_equal(positions,np.flatnonzero(mask))
        np.testing.assert_array_equal(values,words[positions,storage.DATA])
        np.testing.assert_array_equal(saved['decoded_before'],original['decoded_raw'])
        initial=storage.View(state('initial_actual'),positions,values)
        normalized=storage.View(state('initial_normalized'),positions,values)
        np.testing.assert_array_equal(initial.words,words)
        np.testing.assert_array_equal(initial.signals,signals)
        normalized_words=words.copy()
        parents=tuple(r.project(f.decode_cell(row)) for row in original['decoded_raw'])
        expected_info=np.array([f.encode_cell(r.lift(x)) for x in parents],dtype=np.uint64)
        np.testing.assert_array_equal(expected_info,saved['expected_normalized_info'])
        for col in range(size//f.Q):normalized_words[col*f.Q+np.array(g.info),storage.DATA]=expected_info[col]
        np.testing.assert_array_equal(normalized.words,normalized_words)
        np.testing.assert_array_equal(normalized.signals,signals)
        assert receipt['initialization']['physical_transitions']==0
        assert receipt['initialization']['complete_raw_words_verified']==size*f.FIELDS
        # Execute the actual prefix with another physical backend retaining
        # every global Data word; no inert component is omitted in this run.
        begin=f.U+1;target=receipt['normalization']['time']
        cpu=events.World(lambda sites:storage.raw_words(words,signals,1,sites),size=size,time=begin)
        cpu.advance(target-begin)
        actual_normal=storage.View(state('normalization_actual'),positions,values)
        twin_normal=storage.View(state('normalization_reference'),positions,values)
        for start in range(0,size,f.Q):
            sites=np.arange(start,start+f.Q)
            np.testing.assert_array_equal(cpu.cells(sites),actual_normal.cells(sites))
            np.testing.assert_array_equal(cpu.cells(sites),twin_normal.cells(sites))
            raw_words_checked+=f.Q*f.FIELDS
        # Independently validate every transport interval and scalar local event
        # in that native prefix; raw metadata and controllers come from the source.
        view=SimpleNamespace(base=SimpleNamespace(size=size,age=1),cells=lambda sites:storage.raw_words(words,signals,1,sites))
        model,guard=Replay(view),TransportGuard();clock=begin
        for kind,start,duration in cpu.trace:
            assert clock==start
            if kind==0:guard.advance(model,clock%f.U,duration)
            else:
                assert kind==1 and duration==1
                model.step(clock%f.U)
            clock+=duration
        assert clock==target
        np.testing.assert_array_equal(model.words,cpu.words)
        np.testing.assert_array_equal(model.words,actual_normal.words)
        print(json.dumps(dict(stage='actual normalization independently verified',trace_events=len(cpu.trace),scalar_candidates=model.evaluations,seconds=time.perf_counter()-started)),flush=True)
        healthy=tuple(r.project(f.decode_cell(row)) for row in original['expected_decoded_raw'])
        for row in receipt['periods']:
            step=row['step'];actual=state(f'period{step}')
            expected=terminal.terminal(parents)
            np.testing.assert_array_equal(actual['bank'],expected['committed_bank'])
            np.testing.assert_array_equal(actual['signals'],expected['signals'])
            assert int(actual['age'])==0 and int(actual['time'])==(step+1)*f.U
            assert not np.any(actual['flags'])
            reference=cone.BankImage(expected['committed_bank'],expected['signals'])
            observed=storage.View(actual,positions,values)
            for start in range(0,size,f.Q):
                sites=np.arange(start,start+f.Q)
                raw=reference.cells(sites)
                for pos,value in zip(positions,values):
                    for d in f.OFFSETS:
                        holder=(int(pos)-d)%size
                        if start<=holder<start+f.Q:raw[holder-start,f.COL[f's{d+2}_data']]=value
                np.testing.assert_array_equal(observed.cells(sites),raw)
                raw_words_checked+=f.Q*f.FIELDS
            next_parents=r.step_ring(parents);healthy=r.step_ring(healthy)
            decoded=tuple(r.project(f.decode_cell(x)) for x in actual['bank'][:,g.info])
            assert decoded==next_parents
            differences=[i for i,(a,b) in enumerate(zip(decoded,healthy)) if a!=b]
            assert differences==row['upper_cells_differing_from_matching_healthy_window']
            np.testing.assert_array_equal(saved[f'period{step}_decoded'],actual['bank'][:,g.info])
            np.testing.assert_array_equal(saved[f'period{step}_healthy_upper'],r.array_from_cells(healthy))
            parents=next_parents
            observations.append(dict(step=step,time=int(actual['time']),complete_bank_words=actual['bank'].size,raw_words_verified=size*f.FIELDS,upper_differing_cells=differences))
            print(json.dumps(dict(observations[-1],seconds=time.perf_counter()-started)),flush=True)
        final_prefix=f'period{receipt["requested_periods"]}' if receipt['requested_periods'] else 'normalization_actual'
        for key in FIELDS:np.testing.assert_array_equal(saved['final_'+key],saved[final_prefix+'_'+key])
    from experiments.fixed_rule import audit_retimed_holder_contextual_macrostep as scalar
    sources=(Path(__file__),Path(storage.__file__),Path(events.__file__),Path(events.__file__).with_suffix('.cc'),Path(events.global_events.__file__),Path(scalar.__file__),Path(terminal.__file__),Path('experiments/fixed_rule/certify_retimed_holder_inert_data.py'),Path(f.__file__))
    result=dict(passed=True,exact_previous_noisy_state_verified=True,inert_Data_descriptor_certificate_replayed=True,physical_normalization_trace_events=len(cpu.trace),normalization_scalar_core_candidates=model.evaluations,normalization_unique_scalar_neighborhoods=model.unique_evaluations,normalization_native_full_local_outputs=cpu.local_evaluations,complete_raw_words_checked=raw_words_checked,periods=observations,upper_window_rejoined_after_two_periods=len(observations)>=2 and observations[1]['upper_differing_cells']==[],retained_Data_unchanged=values.tolist(),source_receipt_sha256=sha(path),artifact_sha256=receipt['artifact_sha256'],source_sha256={str(x):sha(x) for x in sources},seconds=time.perf_counter()-started,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,scope='Independent native/scalar physical normalization prefix plus existing conditional full-bank terminal identity checked against actual GPU endpoints. Retained Data proved independent and unchanged by complete descriptor. This is repair in the matched periodic 73-colony context, not full-Q noisy evolution, literal replay of every intervening tick, complete physical-state erasure or a noise threshold.')
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':main()
