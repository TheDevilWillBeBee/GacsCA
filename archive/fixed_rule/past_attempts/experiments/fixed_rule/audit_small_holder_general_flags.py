"""Audit general-Signal physical macrosteps and exact flag trajectory evidence."""
import argparse,hashlib,json,resource,time
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import small_holder_rule as f,small_holder_projected as r,small_holder_native as native
from gacsca.fixed_rule import small_holder_resident_general as general,small_holder_flags_gpu as flags,small_holder_flag_profile as profile


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def load(stem):
    m=json.loads(stem.with_suffix('.json').read_text());assert m['passed']
    for path,h in m['source_sha256'].items():assert sha(path)==h,path
    assert sha(stem.with_suffix('.npz'))==m['artifact_sha256']
    with np.load(stem.with_suffix('.npz'),allow_pickle=False) as z:data={k:z[k] for k in z.files}
    return m,data


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--macrosteps',required=True);parser.add_argument('--trajectories',required=True);parser.add_argument('--proof',required=True);parser.add_argument('--output',required=True);args=parser.parse_args();out=Path(args.output)
    if out.exists():raise FileExistsError('preserve evidence')
    started=time.perf_counter();m,z=load(Path(args.macrosteps));fm,fz=load(Path(args.trajectories));proof=json.loads(Path(args.proof).read_text());desc=f.self_description()
    assert m['physical_descriptor_sha256']==fm['descriptor_sha256']==desc.digest()
    assert sha(general.library()._name)==m['binary_sha256'];assert sha(flags.library()._name)==m['flag_binary_sha256']==fm['binary_sha256']
    assert proof['passed'] and len(proof['cases'])==4
    assert proof['source_sha256']==sha('experiments/fixed_rule/prove_small_holder_general_flags.py')
    assert all(x['passed'] and x['independent_bits']==51 and x['descriptor_sha256']==desc.digest() for x in proof['cases'])
    state=tuple(f.decode_cell(row.tolist()) for row in z['initial']);counts=[]
    for period in range(2):
        raw=f.step_ring(state);assert raw==native.step_ring(state)
        for i,cell in enumerate(raw):
            inputs=tuple(word for j in f.NEIGHBORHOOD for word in f.encode_cell(state[(i+j)%len(state)]))
            assert f.decode_cell(desc.evaluate(inputs))==cell
        target=tuple(r.lift(r.project(cell)) for cell in raw)
        assert all(x.f1==1 and x.f2==1 for x in target)
        for name,expected in (('raw_outputs',raw),('hold_before',raw),('hold_after',target),('decoded',target)):
            np.testing.assert_array_equal(z[name][period],native.array_from_cells(expected))
        packed=z['flags_at_cutoff'][period]
        counts.append([sum(int(v).bit_count() for v in packed[:,i]) for i in range(2)])
        assert counts[-1][0]>0 and counts[-1][1]>0
        state=target
    assert m['flag_literal_ticks']==2*(3*f.Q+1)
    assert z['decoded'][0,7,f.COL['address']]==107 and z['decoded'][1,7,f.COL['s2_data']]==0x123456789ABCDEF0
    # Flag1 remains independently given by the previously certified front profile.
    for case,pattern in enumerate(fz['patterns']):
        for frame,age in enumerate(fz['ages']):
            age=int(age);lo,hi=profile.interval(age)
            for col in range(2):
                number=((1<<(hi-lo))-1)<<lo if pattern[col] else 0
                expected=np.array([(number>>(64*i))&((1<<64)-1) for i in range(flags.WORDS)],dtype=np.uint64)
                np.testing.assert_array_equal(fz['frames'][case,frame,col*flags.WORDS:(col+1)*flags.WORDS,0],expected)
            if age>=f.WF_END+f.Q//2:assert not np.any(fz['frames'][case,frame,:,0])
            if age>=f.WF_END+f.Q:assert not np.any(fz['frames'][case,frame])
    assert not np.any(fz['random_clearing'][0,:,0]) and not np.any(fz['random_clearing'][1])
    patterns=[tuple(map(int,row)) for row in fz['patterns']];i=patterns.index((1,1,0,1));j=patterns.index((1,1,0,0));at=list(map(int,fz['ages'])).index(f.WF_END)
    cross_difference=np.any(fz['frames'][i,at,:flags.WORDS,1]!=fz['frames'][j,at,:flags.WORDS,1]);assert cross_difference
    result=dict(passed=True,complete_macrosteps_match_scalar_native_descriptor=True,nonzero_both_flags_at_cutoff=counts,all_flag1_frames_match_independent_profile=True,clearing_bounds_observed=True,cross_colony_flag2_dependency_witness=True,symbolic_proof_cases=4,macrostep_manifest_sha256=sha(Path(args.macrosteps).with_suffix('.json')),trajectory_manifest_sha256=sha(Path(args.trajectories).with_suffix('.json')),proof_sha256=sha(args.proof),audit_source_sha256=sha(__file__),seconds=time.perf_counter()-started,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,scope='Complete saved upper outputs independently audited; Flag1 frames checked by a separate certified formula; Flag2 full trajectory/clearing are runtime assertions plus full-rule local tests and the symbolic recurrence certificate. No arbitrary faulty-geometry or nested-period claim.')
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))


if __name__=='__main__':main()
