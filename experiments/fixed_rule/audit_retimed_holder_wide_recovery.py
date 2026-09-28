"""Independent scalar replay of every wider recovery tick and raw observation."""
import argparse
import json
import resource
import time
from pathlib import Path

import numpy as np

from gacsca.fixed_rule import retimed_holder_rule as f
from gacsca.fixed_rule import retimed_holder_contextual_flags as adapter
from gacsca.fixed_rule import retimed_holder_literal_cone as cone
from experiments.fixed_rule import retimed_holder_recovery_replay as replay
from experiments.fixed_rule import audit_retimed_holder_contextual_recovery as original
from experiments.fixed_rule.run_retimed_holder_streamed_repair import sha


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--input',required=True);parser.add_argument('--output',required=True)
    args=parser.parse_args();path,out=Path(args.input),Path(args.output)
    if out.exists():raise FileExistsError(out)
    started=time.perf_counter();receipt=json.loads(path.read_text())
    assert receipt['completed'] and receipt['error'] is None
    assert sha(path.with_suffix('.npz'))==receipt['artifact_sha256']
    for name,digest in receipt['source_sha256'].items():assert sha(name)==digest,name
    source=Path(receipt['source_receipt']);burst=json.loads(source.read_text())
    assert sha(source)==receipt['source_receipt_sha256']
    assert sha(source.with_suffix('.npz'))==receipt['source_artifact_sha256']==burst['artifact_sha256']
    crossing_colony=int(burst['center_colony'])+1
    outputs,first_crossing,clear_tick=0,None,None
    checks=[];targets={row['tick']:row for row in receipt['observations']}
    with np.load(path.with_suffix('.npz'),allow_pickle=False) as saved:
        def state(prefix):return {k:saved[prefix+'_'+k] for k in original.FIELDS}
        initial=state('initial')
        with np.load(source.with_suffix('.npz'),allow_pickle=False) as old:
            for k in original.FIELDS:np.testing.assert_array_equal(initial[k],old['final_background_'+k])
            for k in ('positions','values'):np.testing.assert_array_equal(saved['initial_'+k],old['final_'+k])
        view=adapter.View(initial,saved['initial_positions'],saved['initial_values'])
        attached=adapter.View(state('attached'),saved['attached_positions'],saved['attached_values'])
        for col in range(receipt['colonies']):
            sites=np.arange(col*f.Q,(col+1)*f.Q)
            np.testing.assert_array_equal(view.cells(sites),attached.cells(sites))
        assert receipt['attachment']['physical_transitions']==0
        assert receipt['attachment']['complete_raw_words_verified']==receipt['colonies']*f.Q*f.FIELDS
        actual,healthy=replay.RecoveryReplay(view),replay.RecoveryReplay(adapter.View(initial))
        age=int(initial['age']);head=original.NAMES.index('head')
        assert age>f.WF_END+f.Q
        assert age+receipt['elapsed_physical_ticks']<min(x for x in (*f.RESET_AGES,*f.VOTE_AGES,f.U) if x>age)
        for tick in range(receipt['elapsed_physical_ticks']+1):
            if tick:
                windows=[(col*f.Q,(col+1)*f.Q) for col in range(receipt['colonies'])] if tick<=2 else ([(crossing_colony*f.Q-64,crossing_colony*f.Q+64)] if 1773<=tick<=1778 else [])
                native=[]
                for lo,hi in windows:
                    for model in (actual,healthy):
                        expected=cone.step(model.cells(np.arange(lo-7,hi+7),age+tick-1))[7:-7].copy()
                        native.append((model,np.arange(lo,hi),expected));outputs+=hi-lo
                actual.step(age+tick-1);healthy.step(age+tick-1)
                for model,positions,expected in native:
                    np.testing.assert_array_equal(model.cells(positions,age+tick),expected)
                if not any(actual.flags) and clear_tick is None:clear_tick=tick
                extra=[p for p in actual.live if p//f.Q==crossing_colony and actual.words[p,head] and actual.words[p,head]!=healthy.words[p,head]]
                if extra and first_crossing is None:first_crossing=tick
            if tick in targets:
                row=targets[tick]
                healthy_view=adapter.View(state(f'observe{tick}_healthy'))
                observed=adapter.View(state(f'observe{tick}_healthy'),saved[f'observe{tick}_positions'],saved[f'observe{tick}_values'])
                positions=[];counts=np.zeros(f.FIELDS,dtype=np.int64);heads=[]
                for col in range(receipt['colonies']):
                    sites=np.arange(col*f.Q,(col+1)*f.Q)
                    a,h=actual.cells(sites,age+tick),healthy.cells(sites,age+tick)
                    np.testing.assert_array_equal(h,healthy_view.cells(sites))
                    np.testing.assert_array_equal(a,observed.cells(sites))
                    diff=a!=h;chosen=np.flatnonzero(np.any(diff,axis=1))
                    positions.extend(sites[chosen].tolist());counts+=np.count_nonzero(diff,axis=0)
                    heads.extend(sites[np.flatnonzero((a[:,f.COL['s2_head']]!=0)&diff[:,f.COL['s2_head']])].tolist())
                np.testing.assert_array_equal(saved[f'observe{tick}_positions'],positions)
                assert row['discrepant_sites']==len(positions) and row['discrepant_words']==int(counts.sum())
                assert row['extra_primary_head_positions']==heads
                assert row['actual_flag1_sites']==sum(v.bit_count() for v in actual.flags) and row['actual_flag2_sites']==0
                checks.append(dict(tick=tick,discrepant_sites=len(positions),discrepant_words=int(counts.sum()),extra_primary_head_positions=heads))
                print(json.dumps(dict(checks[-1],seconds=time.perf_counter()-started)),flush=True)
            elif tick%1024==0:print(json.dumps(dict(tick=tick,seconds=time.perf_counter()-started)),flush=True)
        final=adapter.View(state('final_background'),saved['final_exception_positions'],saved['final_exception_values'])
        for col in range(receipt['colonies']):
            sites=np.arange(col*f.Q,(col+1)*f.Q)
            np.testing.assert_array_equal(final.cells(sites),actual.cells(sites,age+receipt['elapsed_physical_ticks']))
    sources=(Path(__file__),Path(replay.__file__),Path(original.__file__),Path(replay.Replay.step.__code__.co_filename),Path(adapter.__file__),Path(cone.__file__),Path(f.__file__))
    result=dict(passed=True,all_quiet_ticks_replayed=receipt['elapsed_physical_ticks'],colonies=receipt['colonies'],
                scalar_core_candidate_evaluations=actual.evaluations+healthy.evaluations,
                unique_scalar_neighborhood_evaluations=actual.unique_evaluations+healthy.unique_evaluations,
                complete_native_output_states=outputs,complete_native_output_words=outputs*f.FIELDS,
                receiving_colony=crossing_colony,first_extra_primary_head_in_receiving_colony=first_crossing,
                first_flag_clear_tick=clear_tick,observations=checks,all_mail_outputs_zero=True,
                source_receipt_sha256=sha(path),artifact_sha256=receipt['artifact_sha256'],
                source_sha256={str(p):sha(p) for p in sources},seconds=time.perf_counter()-started,
                host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                scope='Every quiet physical tick replays complete scalar procedures in all 73 colonies, '
                      'memoizing identical complete inputs within each tick, plus exact late Flag1 recurrence. '
                      'All saved full raw observations and final state checked. No macrostep or upper repair claim.')
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='observations'},indent=2),flush=True)


if __name__=='__main__':main()
