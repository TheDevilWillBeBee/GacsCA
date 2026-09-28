"""Bounded native physical flag execution with an independently checkable DAG."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import resource
import tarfile
import time
import numpy as np
from gacsca.fixed_rule import delivery_rule as r
from gacsca.fixed_rule.flag_byte_hash import BITS,WORDS,MASK
from gacsca.fixed_rule.flag_byte_native import Evolution


def count_prefix(engine,node,length,field):
    memo={}
    def full(node):
        if node in memo:return memo[node]
        level,left,right=map(int,engine.nodes[node])
        out=((left>>(BITS*field))&MASK).bit_count() if not level else full(left)+full(right)
        memo[node]=out;return out
    def prefix(node,n):
        level,left,right=map(int,engine.nodes[node])
        if n==(1<<level):return full(node)
        if not n:return 0
        half=1<<(level-1)
        return prefix(left,n) if n<=half else full(left)+prefix(right,n-half)
    return prefix(node,length)


def execute(source,output,ticks):
    if not isinstance(ticks,int) or not 0<ticks<=r.U-98*r.Q:raise ValueError("positive post-cutoff physical duration required")
    resource.setrlimit(resource.RLIMIT_CORE,(0,0))
    resource.setrlimit(resource.RLIMIT_AS,(6*1024**3,6*1024**3))
    source,output=Path(source),Path(output);paths={ext:output.with_suffix(ext) for ext in ('.json','.npz','.tar.gz')}
    if any(path.exists() for path in paths.values()):raise FileExistsError('preserve evidence')
    with np.load(source,allow_pickle=False) as a:runs=a['runs'];right=a['right_signals'];left=a['left_signals']
    root=Path(__file__).resolve().parents[2]
    names=['gacsca/fixed_rule/flag_byte_hash.py','gacsca/fixed_rule/flag_hash.py','gacsca/fixed_rule/delivery_rule.py','tests/fixed_rule/test_flag_byte_hash.py','gacsca/fixed_rule/flag_byte_native.py','gacsca/fixed_rule/flag_byte_native.cpp','tests/fixed_rule/test_flag_byte_native.py',str(Path(__file__).resolve().relative_to(root))]
    contents={name:(root/name).read_bytes() for name in names}
    with tarfile.open(paths['.tar.gz'],'x:gz') as archive:
        for name,data in contents.items():item=tarfile.TarInfo(name);item.size=len(data);archive.addfile(item,io.BytesIO(data))
    started=time.monotonic()
    with Evolution(runs,len(right),98*r.Q,ticks) as native:
        info=native.info;initial,final=info['initial'],info['final']
        print(json.dumps(dict(status='evolved',seconds=time.monotonic()-started,**info)),flush=True)
        nodes,queries=native.proof()
        binary=hashlib.sha256(Path(native.lib._name).read_bytes()).hexdigest()
    class Proof:
        pass
    engine=Proof();engine.nodes=nodes;engine.cache=queries;engine.leaf_evaluations=info['leaf_evaluations']
    counts=[count_prefix(engine,final,len(right)*WORDS,k) for k in range(2)]
    with paths['.npz'].open('xb') as stream:
        np.savez_compressed(stream,nodes=np.array(engine.nodes,dtype=np.uint64),queries=queries,initial=np.array(initial,dtype=np.uint64),final=np.array(final,dtype=np.uint64),cutoff_runs=runs,right_signals=right,left_signals=left)
    result=dict(scope=__doc__,rule=r.identity(),source_checkpoint=str(source),source_checkpoint_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),start_age=98*r.Q,ticks=ticks,final_age=(98*r.Q+ticks)%r.U,colonies=len(right),nodes=len(engine.nodes),queries=len(engine.cache),leaf_evaluations=engine.leaf_evaluations,flag_counts=counts,seconds=time.monotonic()-started,binary_sha256=binary,source_sha256={name:hashlib.sha256(data).hexdigest() for name,data in contents.items()},artifact_sha256=hashlib.sha256(paths['.npz'].read_bytes()).hexdigest(),archive_sha256=hashlib.sha256(paths['.tar.gz'].read_bytes()).hexdigest())
    paths['.json'].write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(status='complete',**{k:v for k,v in result.items() if k in ('ticks','nodes','queries','leaf_evaluations','flag_counts','seconds')})),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--input',required=True,type=Path);parser.add_argument('--output',required=True,type=Path);parser.add_argument('--ticks',required=True,type=int)
    args=parser.parse_args();execute(args.input,args.output,args.ticks)
