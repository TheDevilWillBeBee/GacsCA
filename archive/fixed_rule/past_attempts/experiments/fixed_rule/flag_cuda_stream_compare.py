"""Time-bounded million-tick GPU pilot against an already audited CPU DAG.

Compare all physical flags, not only counts or sampled decoded observations.
The CPU derivation was checked online; this script validates its saved final
spatial DAG and compares independently evolved CUDA state to that complete DAG.
"""
import argparse,hashlib,io,json,tarfile,time
from functools import lru_cache
from pathlib import Path
import numpy as np
from gacsca.fixed_rule.flag_cuda import advance,libraries
from .flag_cuda_pilot import dense


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def expand(nodes,root,period):
    assert nodes.ndim==2 and nodes.shape[1]==3
    # Validate every explicit node, including nodes unused by the selected root.
    for i,(level,left,right) in enumerate(nodes):
        level,left,right=map(int,(level,left,right))
        if level==0:assert left==right and left<1<<18
        else:assert 0<=left<i and 0<=right<i and int(nodes[left,0])==int(nodes[right,0])==level-1
    @lru_cache(maxsize=None)
    def small(node):
        level,left,right=map(int,nodes[node])
        assert level<=12
        return np.array([left],dtype=np.uint32) if not level else np.concatenate((small(left),small(right)))
    values=np.empty(period,dtype=np.uint32)
    def fill(node,offset,n):
        if not n:return
        level,left,right=map(int,nodes[node])
        if level<=12:values[offset:offset+n]=small(node)[:n]
        else:
            half=1<<(level-1);first=min(n,half);fill(left,offset,first);fill(right,offset+first,n-first)
    assert (1<<int(nodes[root,0]))>=period;fill(root,0,period)
    positions=np.arange(period,dtype=np.uint32);m=8388608//8
    np.testing.assert_array_equal(values>>16,((positions%m==0).astype(np.uint32))|((positions%m==m-1).astype(np.uint32)<<1))
    flags=np.empty((period//8,2),dtype=np.uint64)
    for field in range(2):flags[:,field]=((values>>(8*field))&255).astype(np.uint8).view(np.uint64)
    return flags


def execute(stem,reference):
    stem,reference=Path(stem),Path(reference)
    if any(stem.with_suffix(e).exists() for e in ('.json','.npz','.tar.gz')):raise FileExistsError('preserve evidence')
    x=json.loads(reference.with_suffix('.json').read_text());assert sha(reference.with_suffix('.npz'))==x['artifact_sha256']
    assert x['final']['queries']==x['final']['verified_queries'] and x['ticks']==1048576
    root=Path(__file__).resolve().parents[2];files=[Path(__file__),root/'experiments/fixed_rule/flag_cuda_pilot.py',*[root/'gacsca/fixed_rule'/n for n in ('flag_cuda.py','flag_cuda.cu','flag_cuda_reference.c','flag_words.c','flag_words.py')]];hashes={}
    with tarfile.open(stem.with_suffix('.tar.gz'),'x:gz') as archive:
        for p in files:
            data=p.read_bytes();name=str(p.relative_to(root));hashes[name]=sha(p);info=tarfile.TarInfo(name);info.size=len(data);archive.addfile(info,io.BytesIO(data))
    with np.load(reference.with_suffix('.npz'),allow_pickle=False) as a:initial=dense(a['cutoff_runs']);nodes=a['nodes'];node=int(a['root'])
    libraries();advance(initial,0) # Separate first CUDA context creation from timing.
    start=time.monotonic();actual=advance(initial,x['ticks']);seconds=time.monotonic()-start
    print(json.dumps(dict(status='GPU_complete',ticks=x['ticks'],seconds=seconds)),flush=True)
    start=time.monotonic();expected=expand(nodes,node,len(initial)*8);np.testing.assert_array_equal(actual,expected);audit_seconds=time.monotonic()-start
    counts=[int(np.unpackbits(actual[:,k].copy().view(np.uint8)).sum()) for k in range(2)];assert counts==x['flag_counts']
    np.savez_compressed(stem.with_suffix('.npz'),final_dense=actual)
    result=dict(passed=True,scope=__doc__,ticks=x['ticks'],physical_sites=len(initial)*64,gpu_seconds=seconds,full_DAG_comparison_seconds=audit_seconds,flag_counts=counts,reference=str(reference),reference_json_sha256=sha(reference.with_suffix('.json')),reference_artifact_sha256=x['artifact_sha256'],source_sha256=hashes,archive_sha256=sha(stem.with_suffix('.tar.gz')),artifact_sha256=sha(stem.with_suffix('.npz')),binary_sha256=[sha(lib._name) for lib in libraries()],limitation='unforced canonical physical flags only; no full suffix, controller composition, deeper hierarchy or repair claim')
    stem.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input',required=True,type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args();execute(a.output,a.input)
