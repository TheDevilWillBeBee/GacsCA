"""Exact canonical Flag1 interval recurrence after the projected geometry run."""
import argparse
import json
from pathlib import Path
import resource
import time
import numpy as np
from gacsca.fixed_rule import retimed_holder_rule as f
from gacsca.fixed_rule import retimed_holder_geometry_projection as projection
from experiments.fixed_rule.audit_retimed_holder_prefix_embedding import sha


def flag_step(bits):
    if type(bits) is not int or not 0 <= bits < 1 << f.Q:
        raise ValueError('one canonical colony Flag1 bitset required')
    right=[bits >> d for d in range(1,6)]
    at_least_two=0
    for i in range(5):
        for j in range(i+1,5): at_least_two |= right[i] & right[j]
    return f.majority5(right) | (bits & at_least_two)


def interval_step(left,right):
    if left is None: return None,None
    if not 0 <= left <= right < f.Q: raise ValueError('valid Flag1 interval required')
    if right-left+1 < 3: return None,None
    return max(0,left-3),right-2


def interval_bits(left,right):
    return 0 if left is None else ((1 << (right-left+1))-1) << left


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True)
    out=Path(parser.parse_args().output)
    if out.exists(): raise FileExistsError(out)
    started=time.perf_counter();root=Path('figs/fixed_rule')
    source=root/'retimed_holder_fresh_geometry_projection_v1.json'
    doc=json.loads(source.read_text());assert doc['passed']
    assert sha(source.with_suffix('.npz'))==doc['artifact_sha256']
    for path,digest in doc['source_sha256'].items(): assert sha(path)==digest,path
    with np.load(source.with_suffix('.npz'),allow_pickle=False) as z:
        state=z['tick1024_geometry']
    np.testing.assert_array_equal(state[:,0],np.arange(f.Q));assert not np.any(state[:,2])
    active=np.flatnonzero(state[:,1]);left,right=int(active[0]),int(active[-1])
    assert len(active)==right-left+1 and (left,right)==(27889,31929)
    bits=interval_bits(left,right);tick=1024;checks=0;rows=[]
    milestones={1024,1025,10320,10321,16986,16987,16988,16989}
    while bits:
        if tick in milestones:
            old=np.column_stack((np.arange(f.Q),np.array([(bits >> i)&1 for i in range(f.Q)],dtype=np.int64),np.zeros(f.Q,dtype=np.int64)))
            expected=projection.step(old,tick)
        bits=flag_step(bits);left,right=interval_step(left,right)
        assert bits==interval_bits(left,right)
        if tick in milestones:
            wanted=np.array([(bits >> i)&1 for i in range(f.Q)],dtype=np.int64)
            np.testing.assert_array_equal(expected[:,1],wanted)
            np.testing.assert_array_equal(expected[:,0],np.arange(f.Q));assert not np.any(expected[:,2])
            checks+=3*f.Q
        tick+=1
        if tick in milestones or not bits:
            rows.append(dict(tick=tick,left=left,right=right,Flag1=bits.bit_count()))
    assert tick==16989 and tick<=32768
    result=dict(passed=True,initial_age=1024,initial_Flag1_interval=[27889,31929],
                exact_Flag1_transitions=tick-1024,final_age=tick,final_geometry_canonical=True,
                final_Flag1=0,final_Flag2=0,interval_identity_checked_every_tick=True,
                vector_projection_geometry_words_compared=checks,observations=rows,
                descriptor_sha256=f.self_description().digest(),
                input_sha256={str(source):sha(source)},
                source_sha256={str(x):sha(x) for x in (Path(__file__),Path(projection.__file__),Path(f.__file__))},
                seconds=time.perf_counter()-started,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                scope='Geometry-only restoration for the selected nine-mark trajectory, '
                      'conditional on the preceding checked geometry projection. Exact '
                      'canonical Flag1 recurrence after tick1024. Full procedure/controller '
                      'state after the literal tick128 endpoint has not been executed here.')
    with out.open('x') as stream: stream.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':main()
