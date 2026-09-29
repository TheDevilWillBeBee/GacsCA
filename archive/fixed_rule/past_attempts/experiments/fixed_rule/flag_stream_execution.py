"""Bounded-history execution of actual post-cutoff physical flags.

Each accepted chunk's entire ephemeral query DAG is independently checked before
commit/collection. Only physical spacetime is accelerated; the delivery rule,
its self-description, evaluator state and hierarchy encoding are unchanged.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import resource
import tarfile
import time
import numpy as np
from gacsca.fixed_rule import delivery_rule as f
from gacsca.fixed_rule.flag_byte_stream import World
from .flag_byte_native_execution import count_prefix


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def execute(checkpoint,output,ticks,chunk,budget):
    if not 0<ticks<=f.U-98*f.Q:raise ValueError('physical suffix duration required')
    output,checkpoint=Path(output),Path(checkpoint)
    paths={ext:output.with_suffix(ext) for ext in ('.json','.npz','.tar.gz','.progress.json','.checkpoint.npz')}
    if any(path.exists() for path in paths.values()):raise FileExistsError('preserve evidence')
    root=Path(__file__).resolve().parents[2];base=json.loads((root/'figs/fixed_rule/delivery_execution_v1.json').read_text())
    names=sorted(set(base['source_sha256'])|{'gacsca/fixed_rule/flag_byte_stream.cpp','gacsca/fixed_rule/flag_byte_stream.py','gacsca/fixed_rule/flag_stream_audit.h','gacsca/fixed_rule/flag_native_tables.py','gacsca/fixed_rule/flag_byte_native.cpp','gacsca/fixed_rule/flag_byte_native.py','gacsca/fixed_rule/flag_byte_hash.py','gacsca/fixed_rule/flag_hash.py','tests/fixed_rule/test_flag_stream.py','experiments/fixed_rule/flag_byte_native_execution.py',str(Path(__file__).resolve().relative_to(root))})
    contents={name:(root/name).read_bytes() for name in names}
    with tarfile.open(paths['.tar.gz'],'x:gz') as archive:
        for name,data in contents.items():item=tarfile.TarInfo(name);item.size=len(data);archive.addfile(item,io.BytesIO(data))
    with np.load(checkpoint,allow_pickle=False) as a:runs=a['runs'];right=a['right_signals'];left=a['left_signals']
    identity=f.identity();baseline={line.split(':',1)[0]:line.split(':',1)[1].strip() for line in Path('/proc/self/status').read_text().splitlines() if line.startswith(('Vm','Threads'))}
    resource.setrlimit(resource.RLIMIT_CORE,(0,0));resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3))
    records=[];started=time.monotonic();proposal=chunk
    with World(runs,len(right),98*f.Q) as world:
        binary=sha(world.lib._name)
        while world.info['time']<ticks:
            row=world.advance(min(proposal,ticks-world.info['time']),budget=budget)
            assert row['queries']==row['verified_queries']
            row['seconds']=time.monotonic()-started;records.append(row)
            paths['.progress.json'].write_text(json.dumps(dict(status='running',**row),indent=2)+'\n')
            if len(records)%16==0 or row['time']==ticks:
                nodes,root_id=world.snapshot();np.savez_compressed(paths['.checkpoint.npz'],nodes=nodes,root=np.array(root_id,dtype=np.uint64),time=np.array(row['time'],dtype=np.uint64));print(json.dumps(row),flush=True)
            proposal=row['last_ticks']*2 if row['last_nodes']<budget//8 and row['last_queries']<budget//8 else row['last_ticks']
            proposal=min(chunk,max(1,proposal))
        nodes,root_id=world.snapshot();final=world.info
    class Proof:pass
    proof=Proof();proof.nodes=nodes
    counts=[count_prefix(proof,root_id,len(right)*(f.Q//8),field) for field in range(2)]
    with paths['.npz'].open('xb') as stream:np.savez_compressed(stream,nodes=nodes,root=np.array(root_id,dtype=np.uint64),cutoff_runs=runs,right_signals=right,left_signals=left)
    result=dict(scope=__doc__,rule=identity,start_age=98*f.Q,ticks=ticks,final_age=(98*f.Q+ticks)%f.U,colonies=len(right),flag_counts=counts,final=final,records=records,seconds=time.monotonic()-started,baseline=baseline,virtual_memory_limit_bytes=2*1024**3,host_node_table_budget=budget,source_checkpoint=str(checkpoint),source_checkpoint_sha256=sha(checkpoint),source_sha256={name:hashlib.sha256(data).hexdigest() for name,data in contents.items()},binary_sha256=binary,artifact_sha256=sha(paths['.npz']),archive_sha256=sha(paths['.tar.gz']),limitation='ephemeral derivations checked online, not retained for offline replay; complete controller composition and subsequent work periods separate')
    paths['.json'].write_text(json.dumps(result,indent=2)+'\n');paths['.progress.json'].write_text(json.dumps(dict(status='complete',**final),indent=2)+'\n');print(json.dumps(dict(status='complete',seconds=result['seconds'],flag_counts=counts,**final)),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input',required=True,type=Path);p.add_argument('--output',required=True,type=Path);p.add_argument('--ticks',required=True,type=int);p.add_argument('--chunk',type=int,default=65536);p.add_argument('--budget',type=int,default=262144);a=p.parse_args();execute(a.input,a.output,a.ticks,a.chunk,a.budget)
