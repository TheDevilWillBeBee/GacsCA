"""Complete physical causal replay of the wider lower burst and all central input halos."""
import argparse
import json
import resource
import time
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import retimed_holder_rule as f, retimed_holder_projected as r
from gacsca.fixed_rule import retimed_holder_live_window as live
from gacsca.fixed_rule import retimed_holder_literal_cone as cone
from gacsca.fixed_rule import retimed_holder_noise_schedule as noise
from gacsca.fixed_rule import retimed_holder_program as p
from experiments.fixed_rule.run_retimed_holder_streamed_repair import sha

FIELDS = ('bank','active_rows','counts','flags','signals','age','time')


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
    artifact = path.with_suffix('.npz')
    assert sha(artifact) == receipt['artifact_sha256']
    for source,digest in receipt['source_sha256'].items():
        assert sha(source) == digest, source
    assert sha(receipt['complete_nested_checkpoint']) == receipt['complete_nested_checkpoint_sha256']
    assert sha(receipt['inherited_bank_source']) == receipt['inherited_bank_sha256']
    assert sha(receipt['fixture']) == receipt['fixture_sha256']
    base = json.loads(Path(receipt['complete_nested_checkpoint']).read_text())
    sampled = noise.sample(sites=f.Q,ticks=32,expected_marks=8192,seed=2026092713)
    center = receipt['center_colony']
    outputs = scalar_outputs = 0
    with np.load(artifact,allow_pickle=False) as saved:
        selected = saved['selected_upper_positions']
        bank = np.load(receipt['inherited_bank_source'],mmap_mode='r',allow_pickle=False)
        np.testing.assert_array_equal(saved['inherited_bank'],bank[selected])
        del bank
        np.testing.assert_array_equal(saved['entry_bank'],saved['inherited_bank'])
        assert not np.any(saved['entry_active_rows']) and not np.any(saved['entry_flags']) and not np.any(saved['entry_counts'])
        fixture = json.loads(Path(receipt['fixture']).read_text())
        assert sha(Path(receipt['fixture']).with_suffix('.npz')) == fixture['artifact_sha256']
        with np.load(Path(receipt['fixture']).with_suffix('.npz'),allow_pickle=False) as original:
            np.testing.assert_array_equal(saved['upper_context'],original['checkpoint_raw'])
        g = p.layout()
        np.testing.assert_array_equal(saved['inherited_bank'][:,g.info],saved['upper_context'][selected])
        for col in range(center-8,center+9):
            expected=saved['upper_context'][(int(selected[col])+np.arange(-7,8)) % f.Q].reshape(-1)
            np.testing.assert_array_equal(saved['checkpoint_bank'][col,g.votes],expected)
        np.testing.assert_array_equal(saved['schedule'],sampled['schedule'])
        np.testing.assert_array_equal(saved['replacements'],sampled['replacements'])
        left=center*f.Q-14*34
        right=(center+1)*f.Q+14*34
        state={key:saved['checkpoint_'+key] for key in FIELDS}
        healthy=live.Window(state).cells(np.arange(left,right))
        actual=healthy.copy()
        for row in receipt['rows']:
            tick=row['tick']
            probes={center*f.Q+9565-left}
            probes.update(map(int,np.flatnonzero(np.any(actual!=healthy,axis=1))[:8]))
            probes=sorted(i for i in probes if 7<=i<len(actual)-7)
            expected_scalar=[]
            for values in (actual,healthy):
                expected_scalar.append(np.array([f.encode_cell(r.lift(r.project(f.local_step(tuple(f.decode_cell(values[i+d]) for d in f.NEIGHBORHOOD))))) for i in probes],dtype=np.uint64))
            actual=cone.step(actual)[7:-7].copy()
            healthy=cone.step(healthy)[7:-7].copy()
            np.testing.assert_array_equal(actual[np.array(probes)-7],expected_scalar[0])
            np.testing.assert_array_equal(healthy[np.array(probes)-7],expected_scalar[1])
            outputs+=2*len(actual);scalar_outputs+=2*len(probes)
            left+=7
            state={key:saved[f'tick{tick}_'+key] for key in FIELDS}
            assert int(state['time'])==receipt['burst_initial_age']+tick==row['time']
            assert row['absolute_physical_time']==base['period_results'][0]['physical_time']+row['time']
            np.testing.assert_array_equal(healthy,live.Window(state).cells(np.arange(left,left+len(actual))))
            before=np.flatnonzero(np.any(actual!=healthy,axis=1))
            assert len(before)==row['pre_noise_exception_sites']
            indices=np.flatnonzero(sampled['schedule'][:,0]==tick).tolist()
            assert indices==row['mark_indices']
            for index in indices:
                pos=center*f.Q+int(sampled['schedule'][index,1])
                actual[pos-left]=f.encode_cell(r.lift(r.decode_cell(sampled['replacements'][index])))
            positions=np.flatnonzero(np.any(actual!=healthy,axis=1))+left
            np.testing.assert_array_equal(positions,saved[f'tick{tick}_positions'])
            np.testing.assert_array_equal(actual[positions-left],saved[f'tick{tick}_values'])
            assert len(positions)==row['post_noise_exception_sites']
            assert sorted({int(pos)//f.Q for pos in positions})==row['affected_lower_colonies']
            if tick%8==0 or tick>32:
                print(json.dumps(dict(tick=tick,exceptions=len(positions),seconds=time.perf_counter()-started)),flush=True)
        np.testing.assert_array_equal(saved['final_positions'],positions)
        np.testing.assert_array_equal(saved['final_values'],actual[positions-left])
        for key in FIELDS:
            np.testing.assert_array_equal(saved['final_background_'+key],saved['tick34_'+key])
        diff=actual!=healthy
        final=dict(discrepant_sites=len(positions),discrepant_raw_words=int(np.count_nonzero(diff)),fields={name:int(np.count_nonzero(diff[:,i])) for i,(name,_) in enumerate(f.SCHEMA) if np.any(diff[:,i])})
    sources=(Path(__file__),Path(live.__file__),Path(cone.__file__),Path(noise.__file__),Path(f.__file__),Path(r.__file__))
    result=dict(passed=True,exact_inherited_banks_verified=True,actual_upper_controller_context_verified=True,complete_gathered_parent_halos_verified=list(range(center-8,center+9)),exact_unfiltered_sample_reproduced=True,complete_native_causal_output_states=outputs,complete_native_causal_output_words=outputs*f.FIELDS,scalar_source_output_states=scalar_outputs,final=final,source_receipt_sha256=sha(path),artifact_sha256=receipt['artifact_sha256'],source_sha256={str(x):sha(x) for x in sources},seconds=time.perf_counter()-started,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,scope='All retained raw outputs in both native causal trajectories, with padding covering the entire possible fault support; scalar probes and complete exception comparison. Actual lower input halos derive from the real upper NAND checkpoint. No complete noisy nested macrostep or receiving-layer repair claim.')
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':
    main()
