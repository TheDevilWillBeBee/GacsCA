"""Independent scalar-source audit of every fault-influenced output in both sweeps."""
import argparse,json,resource,time
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import retimed_holder_literal_cone as cone,retimed_holder_rule as f,retimed_holder_projected as r
from experiments.fixed_rule.run_retimed_holder_streamed_repair import sha


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();out=Path(args.output)
    if out.exists():raise FileExistsError(out)
    started=time.perf_counter();references={};checks=[];evaluations=0
    basepath=Path('figs/fixed_rule/retimed_holder_timed_depth2_checkpoint_v1.json');base=json.loads(basepath.read_text())
    with np.load(base['small_artifact'],allow_pickle=False) as z:signals=z['step1_signals']
    image=cone.BankImage(np.load(base['bank_paths'][0],mmap_mode='r'),signals)
    for label in ('boundary','forcing'):
        path=Path(f'figs/fixed_rule/retimed_holder_{label}_fault_sweep_v1.json');receipt=json.loads(path.read_text());assert receipt['passed']
        assert sha(path.with_suffix('.npz'))==receipt['artifact_sha256']
        for source,digest in receipt['source_sha256'].items():assert sha(source)==digest
        references[str(path)]=sha(path)
        with np.load(path.with_suffix('.npz'),allow_pickle=False) as z:
            tables={}
            if label=='forcing':
                for context in range(len(receipt['contexts'])):tables[context]={int(pos):row for pos,row in zip(z[f'context{context}_positions'],z[f'context{context}_raw'])}
            for case in receipt['cases']:
                key=f"case{case['index']}";positions=tuple(map(int,z[key+'_positions']));deadline=receipt['deadline'];lo=min(positions)-14*deadline;hi=max(positions)+14*deadline+1
                if label=='boundary':healthy=image.cells(np.arange(lo,hi,dtype=np.int64));size=image.size
                else:
                    table=tables[case['context']];size=f.Q;healthy=np.array([table[pos%size] for pos in range(lo,hi)],dtype=np.uint64)
                actual=healthy.copy()
                np.testing.assert_array_equal(healthy[np.array(positions)-lo],z[key+'_before'])
                actual[np.array(positions)-lo]=z[key+'_injected']
                for tick in range(1,case['ticks']+1):
                    old_actual,old_healthy=actual,healthy
                    actual=cone.step(actual)[7:-7].copy();healthy=cone.step(healthy)[7:-7].copy();old_lo=lo;lo+=7
                    # Verify every output in the whole possible physical fault
                    # cone in both actual and comparison trajectories.
                    for pos in range(min(positions)-7*tick,max(positions)+7*tick+1):
                        for old,new in ((old_actual,actual),(old_healthy,healthy)):
                            neighbors=tuple(f.decode_cell(old[pos-old_lo+d]) for d in f.NEIGHBORHOOD)
                            expected=f.encode_cell(r.lift(r.project(f.local_step(neighbors))))
                            np.testing.assert_array_equal(new[pos-lo],expected);evaluations+=1
                    different=actual!=healthy;sites=np.flatnonzero(np.any(different,axis=1));row=case['trace'][tick-1]
                    assert len(sites)==row['different_sites'] and int(np.count_nonzero(different))==row['different_raw_words']
                    counts=np.count_nonzero(different,axis=0);fields={name:int(counts[k]) for k,(name,_) in enumerate(f.SCHEMA) if counts[k]}
                    assert fields==row['fields']
                assert case['rejoined']==(not len(sites))
                np.testing.assert_array_equal((sites+lo)%size,z[key+'_last_positions']%size)
                np.testing.assert_array_equal(actual[sites],z[key+'_last_actual']);np.testing.assert_array_equal(healthy[sites],z[key+'_last_healthy'])
                checks.append(dict(sweep=label,case=case['index'],ticks=case['ticks'],rejoined=case['rejoined']))
                if len(checks)%40==0:print(json.dumps(dict(cases=len(checks),scalar_outputs=evaluations,seconds=time.perf_counter()-started)),flush=True)
    result=dict(passed=True,cases=len(checks),rejoined_cases=sum(x['rejoined'] for x in checks),nonrejoined_cases=sum(not x['rejoined'] for x in checks),full_scalar_physical_outputs_checked=evaluations,raw_fields_per_output=f.FIELDS,references=references,source_sha256={str(x):sha(x) for x in (Path(__file__),Path(cone.__file__),Path(f.__file__))},seconds=time.perf_counter()-started,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,scope='Independent scalar physical rule matches every output in every possible fault cone, on every executed tick, for all boundary and forcing sweep cases. Four finite-deadline non-rejoins remain explicit; no general threshold or arbitrary-pattern theorem.')
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)

if __name__=='__main__':main()
