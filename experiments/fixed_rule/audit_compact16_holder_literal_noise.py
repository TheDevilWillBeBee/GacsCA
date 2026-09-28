"""Reproduce every sampled fault and final state; inspect retained failures."""
import argparse
import json
from pathlib import Path
import random
import time
import numpy as np
from gacsca.fixed_rule import compact16_holder_rule as f, compact16_holder_projected as r
from gacsca.fixed_rule import compact16_holder_literal_cone as cone
from experiments.fixed_rule.run_compact16_holder_streamed_depth2 import sha


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--reference',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    start=time.perf_counter();receipt=json.loads(args.reference.read_text());assert receipt['passed']
    assert receipt['descriptor_sha256']==f.self_description().digest()
    for source,digest in receipt['source_sha256'].items():assert sha(source)==digest
    assert sha(receipt['artifact'])==receipt['artifact_sha256'] and sha(receipt['fixture'])==receipt['fixture_sha256']
    fixture=json.loads(Path(receipt['fixture']).read_text());assert sha(fixture['artifact'])==fixture['artifact_sha256']
    left=receipt['initial_window_first'];ticks=receipt['noisy_ticks']+receipt['quiet_ticks'];audits=[]
    with np.load(receipt['artifact'],allow_pickle=False) as saved,np.load(fixture['artifact'],allow_pickle=False) as original:
        np.testing.assert_array_equal(saved['initial_raw'],original['checkpoint_raw'][np.arange(left,left+receipt['initial_window_sites'])%f.Q])
        healthy=[saved['initial_raw']]
        for _ in range(ticks):healthy.append(cone.step(healthy[-1])[7:-7].copy())
        np.testing.assert_array_equal(healthy[-1],saved['final_healthy'])
        for row in receipt['trial_results']:
            rng=random.Random(row['seed']);events=[]
            for tick in range(receipt['noisy_ticks']):
                for pos in range(receipt['support_first'],receipt['support_last']+1):
                    if rng.random()<row['probability']:
                        events.append((tick,pos,*(rng.getrandbits(width) for _,width in r.SCHEMA)))
            events=np.array(events,dtype=np.uint64).reshape(-1,2+len(r.SCHEMA))
            np.testing.assert_array_equal(events,saved[row['name']+'_events'])
            assert len(events)==row['physical_site_replacements']
            actual=healthy[0].copy();quiet=[]
            for tick in range(ticks):
                lo=left+7*tick
                for event in events[events[:,0]==tick]:actual[int(event[1])-lo]=f.encode_cell(r.lift(r.decode_cell(event[2:])))
                before=actual;actual=cone.step(before)[7:-7].copy();diff=actual!=healthy[tick+1];indices=np.flatnonzero(np.any(diff,axis=1))
                expected=row['trace'][tick]
                assert expected==dict(tick=tick+1,different_sites=len(indices),different_raw_words=int(np.count_nonzero(diff)))
                # Check the opposite end of the differing set from the run's
                # first-difference scalar probe; if equal, use a support edge.
                index=int(indices[-1]) if len(indices) else receipt['support_last']-(lo+7)
                neighbors=tuple(f.decode_cell(value) for value in before[index:index+15])
                np.testing.assert_array_equal(actual[index],f.encode_cell(r.lift(r.project(f.local_step(neighbors)))))
                if tick+1>=receipt['noisy_ticks'] and not len(indices):quiet.append(tick+1-receipt['noisy_ticks'])
            np.testing.assert_array_equal(actual,saved[row['name']+'_final'])
            assert row['recovered_after_eight_quiet_ticks']==bool(quiet)
            assert row['quiet_ticks_until_rejoin']==(quiet[0] if quiet else None)
            diff=actual!=healthy[-1];fields={name:int(np.count_nonzero(diff[:,k])) for k,(name,_) in enumerate(f.SCHEMA) if np.any(diff[:,k])}
            audits.append(dict(name=row['name'],events_checked=len(events),final_complete_raw_words_checked=int(actual.size),
                               recovered=not bool(fields),residual_fields=fields,scalar_output_checks=ticks))
    result=dict(passed=True,cases=audits,all_sampled_replacements_checked=sum(x['events_checked'] for x in audits),
                final_complete_raw_words_checked=sum(x['final_complete_raw_words_checked'] for x in audits),
                additional_scalar_outputs=sum(x['scalar_output_checks'] for x in audits),
                reference=str(args.reference),reference_sha256=sha(args.reference),
                source_sha256={str(Path(__file__)):sha(__file__)},seconds=time.perf_counter()-start,
                scope='Exact seed/payload and native physical replay of every unfiltered trial, plus opposite-frontier scalar probes and complete residual-field accounting. Replay shares the native descriptor backend; not an independent whole-trajectory implementation or a threshold proof.')
    with args.output.open('x') as out:out.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(passed=True,cases=len(audits),seconds=result['seconds'])),flush=True)


if __name__=='__main__':main()
