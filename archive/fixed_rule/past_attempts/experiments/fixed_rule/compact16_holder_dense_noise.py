"""Continue every retained high-rate failure with literal complete GPU G.

Restore the saved state at the same clock, with its complete causal complement.
No fault is removed, no new encoding is substituted, and no recovery shortcut
is used. Sparse saved differences are lossless diagnostics against saved healthy
states, never inputs to a simulated transition after initialization.
"""
import argparse
import json
from pathlib import Path
import time
import numpy as np
from gacsca.fixed_rule import compact16_holder_dense_gpu as gpu
from gacsca.fixed_rule import compact16_holder_literal_cone as cone
from gacsca.fixed_rule import compact16_holder_rule as f
from experiments.fixed_rule.validate_compact16_holder_endpoint import guard
from experiments.fixed_rule.run_compact16_holder_streamed_depth2 import sha

CHECKPOINTS=(1,2,8,32,128,511,512)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    artifact=args.output.with_suffix('.npz')
    if args.output.exists() or artifact.exists():raise FileExistsError('preserve evidence')
    start=time.perf_counter();prior_path=Path('figs/fixed_rule/compact16_holder_literal_noise_v1.json')
    prior=json.loads(prior_path.read_text());assert prior['passed'] and sha(prior['artifact'])==prior['artifact_sha256']
    fixture=json.loads(Path(prior['fixture']).read_text());assert sha(fixture['artifact'])==fixture['artifact_sha256']
    with np.load(fixture['artifact'],allow_pickle=False) as z:checkpoint=z['checkpoint_raw'].copy()
    with np.load(prior['artifact'],allow_pickle=False) as z:
        window_healthy=z['final_healthy'].copy()
        damaged=[z[f'rate2_trial{k}_final'].copy() for k in range(8)]
    saved={};healthy={};elapsed=[]
    # Literal CPU is used only as a diagnostic cross-check of the GPU healthy
    # complement. The actual damaged continuation never calls a CPU evaluator.
    cpu=checkpoint
    for _ in range(prior['noisy_ticks']+prior['quiet_ticks']):cpu=cone.step(cpu)
    with gpu.World(checkpoint) as world:
        device_bytes=world.device_bytes
        with guard():world.run(prior['noisy_ticks']+prior['quiet_ticks'])
        base=world.read();np.testing.assert_array_equal(base,cpu)
        first=prior['final_window_first'];last=first+len(window_healthy)
        np.testing.assert_array_equal(base[first:last],window_healthy)
        healthy[0]=base;saved['healthy_0']=base
        previous=0
        for tick in CHECKPOINTS:
            t=time.perf_counter()
            with guard():world.run(tick-previous)
            healthy[tick]=world.read();saved[f'healthy_{tick}']=healthy[tick]
            elapsed.append(dict(case='healthy',tick=tick,seconds=time.perf_counter()-t));previous=tick
    trials=[]
    for case,window in enumerate(damaged):
        raw=base.copy();raw[first:last]=window
        # Faults end at tick16; at tick24 their maximum radius-seven support is
        # strictly contained in the retained window. All other sites are healthy.
        assert first<=prior['support_first']-7*24 and last>prior['support_last']+7*24
        one=cone.step(raw);two=cone.step(one);trace=[];previous=0;penultimate=None
        with gpu.World(raw) as world:
            assert world.device_bytes==device_bytes
            np.testing.assert_array_equal(world.read(),raw)
            for tick in CHECKPOINTS:
                t=time.perf_counter()
                with guard():world.run(tick-previous)
                actual=world.read();seconds=time.perf_counter()-t
                if tick in (1,2):np.testing.assert_array_equal(actual,one if tick==1 else two)
                if tick==511:penultimate=actual.copy()
                if tick==512:np.testing.assert_array_equal(actual,cone.step(penultimate))
                indices=np.flatnonzero((actual!=healthy[tick]).ravel()).astype(np.uint64)
                saved[f'case{case}_t{tick}_indices']=indices
                saved[f'case{case}_t{tick}_values']=actual.ravel()[indices]
                fields={name:int(np.count_nonzero(actual[:,k]!=healthy[tick][:,k])) for k,(name,_) in enumerate(f.SCHEMA)}
                row=dict(additional_quiet_ticks=tick,total_quiet_ticks=tick+prior['quiet_ticks'],
                         different_sites=int(np.count_nonzero(np.any(actual!=healthy[tick],axis=1))),
                         different_raw_words=len(indices),different_fields={k:v for k,v in fields.items() if v},seconds=seconds)
                trace.append(row);previous=tick
                print(json.dumps(dict(case=case,**{k:v for k,v in row.items() if k!='different_fields'})),flush=True)
        trials.append(dict(case=case,source_trial=f'rate2_trial{case}',trace=trace,
                           first_checked_rejoin=next((x['additional_quiet_ticks'] for x in trace if not x['different_raw_words']),None)))
    np.savez_compressed(artifact,**saved)
    result=dict(passed=True,reference=str(prior_path),reference_sha256=sha(prior_path),
                descriptor_sha256=f.self_description().digest(),sites=f.Q,fields=f.FIELDS,
                all_eight_failures_retained=True,all_transitions_literal_complete_GPU=True,
                no_coherent_or_zero_flag_premise=True,initial_same_time_restoration=True,
                exact_healthy_complement_CPU_ticks=24,complete_CPU_checked_ticks_per_trial=[1,2,512],
                literal_GPU_site_transitions=f.Q*(24+9*512),checkpoints=list(CHECKPOINTS),
                trials=trials,healthy_timings=elapsed,explicit_peak_device_bytes=device_bytes,
                artifact=str(artifact),artifact_sha256=sha(artifact),seconds=time.perf_counter()-start,
                source_sha256={str(Path(path)):sha(path) for path in (__file__,gpu.__file__,Path(gpu.__file__).with_suffix('.cu'))},
                scope='Eight retained local-noise failures, one periodic colony, 512 additional fault-free literal ticks. No ongoing noise, threshold or full-period/cross-level claim.')
    with args.output.open('x') as out:out.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(output=str(args.output),seconds=result['seconds'],rejoined=sum(x['first_checked_rejoin'] is not None for x in trials))),flush=True)


if __name__=='__main__':main()
