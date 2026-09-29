"""Reconstruct retained complete GPU states and compare literal native/scalar G."""
import argparse
import json
from pathlib import Path
import time
import numpy as np
from gacsca.fixed_rule import compact16_holder_literal_cone as cone
from gacsca.fixed_rule import compact16_holder_rule as f, compact16_holder_projected as r
from experiments.fixed_rule.run_compact16_holder_streamed_depth2 import sha


def restore(z,case,tick):
    raw=z[f'healthy_{tick}'].copy();indices=z[f'case{case}_t{tick}_indices'];values=z[f'case{case}_t{tick}_values']
    assert indices.dtype==np.uint64 and values.dtype==np.uint64 and indices.shape==values.shape
    assert len(indices)==0 or (indices[-1]<raw.size and np.all(indices[1:]>indices[:-1]))
    assert np.all(raw.ravel()[indices]!=values)
    raw.ravel()[indices]=values
    return raw


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    start=time.perf_counter();path=Path('figs/fixed_rule/compact16_holder_dense_noise_v1.json');doc=json.loads(path.read_text())
    assert doc['passed'] and sha(doc['artifact'])==doc['artifact_sha256']
    prior=json.loads(Path(doc['reference']).read_text());assert sha(doc['reference'])==doc['reference_sha256']
    assert sha(prior['artifact'])==prior['artifact_sha256']
    for source,digest in doc['source_sha256'].items():assert sha(source)==digest
    complete_outputs=0;scalar_outputs=0;cases=[]
    with np.load(doc['artifact'],allow_pickle=False) as z,np.load(prior['artifact'],allow_pickle=False) as old:
        for case in range(8):
            raw=z['healthy_0'].copy();first=prior['final_window_first'];raw[first:first+prior['final_window_sites']]=old[f'rate2_trial{case}_final']
            for tick in range(1,33):
                raw=cone.step(raw)
                if tick in (1,2,8,32):
                    np.testing.assert_array_equal(raw,restore(z,case,tick));complete_outputs+=f.Q
            before=restore(z,case,511);after=restore(z,case,512)
            np.testing.assert_array_equal(cone.step(before),after);complete_outputs+=f.Q
            indices=np.flatnonzero(np.any(after!=z['healthy_512'],axis=1))
            # Full scalar output at extremal residual sites and two seam sites;
            # neither the native nor GPU descriptor evaluator supplies this.
            probes=sorted({0,f.Q-1,*(int(x) for x in indices[:3]),*(int(x) for x in indices[-3:])})
            for pos in probes:
                hood=tuple(f.decode_cell(before[(pos+j)%f.Q]) for j in range(-7,8))
                expected=f.encode_cell(r.lift(r.project(f.local_step(hood))))
                np.testing.assert_array_equal(after[pos],expected);scalar_outputs+=1
            for row in doc['trials'][case]['trace']:
                tick=row['additional_quiet_ticks'];actual=restore(z,case,tick);different=actual!=z[f'healthy_{tick}']
                assert int(np.count_nonzero(different))==row['different_raw_words']
                assert int(np.count_nonzero(np.any(different,axis=1)))==row['different_sites']
                fields={name:int(np.count_nonzero(different[:,k])) for k,(name,_) in enumerate(f.SCHEMA) if np.any(different[:,k])}
                assert fields==row['different_fields']
                np.testing.assert_array_equal(actual,cone.normalize(actual.copy()))
            cases.append(dict(case=case,final_different_sites=len(indices),scalar_sites=probes))
            print(json.dumps(cases[-1]),flush=True)
    result=dict(passed=True,reference=str(path),reference_sha256=sha(path),
                complete_native_outputs_checked=complete_outputs,complete_raw_words_checked=complete_outputs*f.FIELDS,
                first_32_ticks_independently_replayed=True,final_tick_independently_checked=True,
                scalar_outputs_checked=scalar_outputs,all_saved_difference_counts_checked=True,cases=cases,
                source_sha256={str(Path(__file__)):sha(__file__)},seconds=time.perf_counter()-start,
                scope='Literal native replay of first32ticks, native last-tick checks and scalar frontier/seam checks. Remaining interior128/511trajectory is GPU-only; no general CUDA equivalence proof.')
    with args.output.open('x') as out:out.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result),flush=True)


if __name__=='__main__':main()
