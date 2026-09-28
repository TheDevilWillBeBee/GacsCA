"""Unfiltered independent site-replacement noise at a live physical checkpoint.

Every transition is literal G in a padded, shrinking physical causal window.
This is a bounded local noise pilot, not whole-lattice independent noise or a
hierarchical threshold experiment. No pulse theorem substitutes for evolution.
"""
import argparse
import hashlib
import json
from pathlib import Path
import random
import time
import numpy as np
from gacsca.fixed_rule import compact16_holder_rule as f, compact16_holder_projected as r
from gacsca.fixed_rule import compact16_holder_literal_cone as cone
from experiments.fixed_rule.run_compact16_holder_streamed_depth2 import sha


def healthy_premises(raw,positions,age):
    np.testing.assert_array_equal(raw[:,f.COL['address']],positions%f.Q)
    assert np.all(raw[:,f.COL['age']]==age%f.U)
    assert not np.any(raw[:,[f.COL['f1'],f.COL['f2'],*(f.COL[f'w{k}_{field}'] for k in range(5) for field in ('wf1','wf2'))]])
    for offset in f.OFFSETS:
        for name,_ in f.PROCEDURE:
            np.testing.assert_array_equal(raw[2:-2,f.COL[f's{offset+2}_{name}']],raw[2+offset:len(raw)-2+offset,f.COL[f's2_{name}']])
        np.testing.assert_array_equal((raw[2:-2,f.COL['signal']]>>np.uint64(offset+2))&np.uint64(1),
                                      (raw[2+offset:len(raw)-2+offset,f.COL['signal']]>>np.uint64(2))&np.uint64(1))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();artifact=args.output.with_suffix('.npz')
    if args.output.exists() or artifact.exists():raise FileExistsError('preserve evidence')
    started=time.perf_counter();fixture_path=Path('figs/fixed_rule/compact16_holder_active_faults_v1.json');fixture=json.loads(fixture_path.read_text())
    assert fixture['passed'] and sha(fixture['artifact'])==fixture['artifact_sha256']
    center=fixture['rom_operands']['b'];noisy_ticks=16;quiet_ticks=8;ticks=noisy_ticks+quiet_ticks
    support=tuple(range(center-32,center+33));left=support[0]-2*7*ticks;right=support[-1]+2*7*ticks+1
    assert right-left<f.Q
    with np.load(fixture['artifact'],allow_pickle=False) as z:initial=z['checkpoint_raw'][np.arange(left,right)%f.Q].copy()
    healthy=[initial]
    for tick in range(ticks):
        positions=np.arange(left+7*tick,right-7*tick)
        healthy_premises(healthy[-1],positions,fixture['age']+tick)
        healthy.append(cone.step(healthy[-1])[7:-7].copy())
    saved=dict(initial_raw=initial,final_healthy=healthy[-1]);rows=[];base_seed=2026092781
    for rate_index,probability in enumerate((0.005,0.02,0.1)):
        for replicate in range(8):
            seed=base_seed+1000*rate_index+replicate;rng=random.Random(seed);events=[]
            # Draw every site/time independently, without filtering by sparsity
            # or observed recovery. Replacement words are independent typed data.
            for tick in range(noisy_ticks):
                for pos in support:
                    if rng.random()<probability:
                        cell=r.Cell(**{name:rng.getrandbits(width) for name,width in r.SCHEMA})
                        events.append((tick,pos,*r.encode_cell(cell)))
            actual=initial.copy();trace=[];scalar_checks=0
            for tick in range(ticks):
                lo=left+7*tick
                for event in events:
                    if event[0]==tick:actual[event[1]-lo]=f.encode_cell(r.lift(r.decode_cell(event[2:])))
                old=actual;actual=cone.step(old)[7:-7].copy();different=actual!=healthy[tick+1]
                indices=np.flatnonzero(np.any(different,axis=1))
                # An independent scalar check at an actual differing output,
                # or the live-head area if the complete states already agree.
                index=int(indices[0]) if len(indices) else center-(lo+7)
                neighbors=tuple(f.decode_cell(row) for row in old[index:index+15])
                wanted=f.encode_cell(r.lift(r.project(f.local_step(neighbors))))
                np.testing.assert_array_equal(actual[index],wanted);scalar_checks+=1
                for index in indices:
                    pos=int(index)+lo+7
                    assert any(abs(pos-event[1])<=7*(tick+1-event[0]) for event in events if event[0]<=tick),'difference outside full causal support'
                trace.append(dict(tick=tick+1,different_sites=len(indices),different_raw_words=int(np.count_nonzero(different))))
            name=f'rate{rate_index}_trial{replicate}'
            saved[name+'_events']=np.array(events,dtype=np.uint64).reshape(-1,2+len(r.SCHEMA));saved[name+'_final']=actual
            recovered=not np.any(actual!=healthy[-1])
            quiet_rejoin=next((row['tick']-noisy_ticks for row in trace[noisy_ticks-1:] if row['different_sites']==0),None)
            row=dict(name=name,seed=seed,probability=probability,replicate=replicate,physical_site_replacements=len(events),
                     recovered_after_eight_quiet_ticks=recovered,quiet_ticks_until_rejoin=quiet_rejoin,
                     final_different_sites=trace[-1]['different_sites'],final_different_raw_words=trace[-1]['different_raw_words'],
                     independent_scalar_outputs=scalar_checks,trace=trace)
            rows.append(row);print(json.dumps({k:v for k,v in row.items() if k!='trace'}),flush=True)
    summaries=[]
    for probability in (0.005,0.02,0.1):
        group=[row for row in rows if row['probability']==probability]
        summaries.append(dict(probability=probability,trials=len(group),fault_events=sum(row['physical_site_replacements'] for row in group),
                              recovered=sum(row['recovered_after_eight_quiet_ticks'] for row in group),
                              failed_by_deadline=sum(not row['recovered_after_eight_quiet_ticks'] for row in group)))
    np.savez_compressed(artifact,**saved)
    result=dict(passed=True,fixture=str(fixture_path),fixture_sha256=sha(fixture_path),age=fixture['age'],
                support_sites=len(support),support_first=support[0],support_last=support[-1],noisy_ticks=noisy_ticks,quiet_ticks=quiet_ticks,
                initial_window_first=left,initial_window_sites=right-left,final_window_first=left+7*ticks,final_window_sites=len(healthy[-1]),
                all_samples_retained=True,no_sparsity_filter=True,all_transitions_literal=True,healthy_context_checked_every_tick=True,
                trial_results=rows,summaries=summaries,artifact=str(artifact),artifact_sha256=sha(artifact),
                descriptor_sha256=f.self_description().digest(),source_sha256={str(Path(__file__)):sha(__file__),str(Path(cone.__file__)):sha(cone.__file__)},
                seconds=time.perf_counter()-started,
                scope='Independent Bernoulli site replacements on65fixed sites for16ticks at one actual active checkpoint,8quiet ticks,8trials/rate. Outside the finite support no faults occur. Complete physical transitions and failures retained. Not a whole-lattice noise threshold, full-period reliability estimate or cross-level stochastic experiment.')
    with args.output.open('x') as out:out.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(summaries=summaries,seconds=result['seconds'])),flush=True)


if __name__=='__main__':main()
