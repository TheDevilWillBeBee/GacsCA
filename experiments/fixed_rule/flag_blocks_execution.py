"""Continue actual signals with an exact change of physical-state compression.

This executes the exact closed flag component; the separate controller suffix
must be executed and composed before claiming a completed full macrostep.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import tarfile
import time
import numpy as np
from gacsca.fixed_rule import delivery_rule as f,delivery_program as p,delivery_projected as r
from gacsca.fixed_rule.flag_words import World
from gacsca.fixed_rule.flag_blocks import World as BlockWorld,from_word_runs,BLOCK


def execute(source,output):
    source,output=Path(source),Path(output)
    paths={ext:output.with_suffix(ext) for ext in ('.json','.npz','.progress.json','.tar.gz','.checkpoint.npz')}
    if any(path.exists() for path in paths.values()):raise FileExistsError('preserve prior evidence')
    x=json.loads(source.with_suffix('.json').read_text())
    assert hashlib.sha256(source.with_suffix('.npz').read_bytes()).hexdigest()==x['artifact_sha256']
    assert x['rule']==json.loads(json.dumps(r.identity()))
    with np.load(source.with_suffix('.npz'),allow_pickle=False) as a:stored=a['stored_final']
    g=p.layout();stored=stored.reshape(-1,g.computation_cells+5,len(r.SCHEMA));n=len(stored)
    assert np.all(stored[:,:,r.COL['age']]==96*f.Q-1)
    for name in ('f1','f2','wf1','wf2'):assert not np.any(stored[:,:,r.COL[name]])
    left=[];right=[]
    for c in stored:
        expected=np.zeros(len(c),dtype=np.uint64)
        for holders,target in ((range(1,6),left),(range(g.computation_cells,g.computation_cells+5),right)):
            holders=list(holders);bit=(int(c[holders[2],r.COL['signal']])>>2)&1;target.append(bit)
            expected[holders]=np.array([16,8,4,2,1])*bit
        np.testing.assert_array_equal(c[:,r.COL['signal']],expected)
    root=Path(__file__).resolve().parents[2]
    names=['gacsca/fixed_rule/flag_words.py','gacsca/fixed_rule/flag_words.c','tests/fixed_rule/test_flag_words.py','gacsca/fixed_rule/flag_blocks.py','gacsca/fixed_rule/flag_blocks.c','tests/fixed_rule/test_flag_blocks.py',str(Path(__file__).resolve().relative_to(root)),*x['source_sha256']]
    names=sorted(set(names));contents={name:(root/name).read_bytes() for name in names}
    with tarfile.open(paths['.tar.gz'],'x:gz') as archive:
        for name,data in contents.items():item=tarfile.TarInfo(name);item.size=len(data);archive.addfile(item,io.BytesIO(data))
    frames={};records=[];started=time.monotonic()
    times=(0,1,257,65537,1+f.Q//4,1+f.Q//2,1+f.Q,1+2*f.Q,1+3*f.Q,8*f.Q+1,16*f.Q+1,24*f.Q+1,32*f.Q+1)
    offset=0;prior=dict(literal_ticks=0,quiet_ticks=0,word_evaluations=0);representation='words64';world=World(tuple(right),tuple(left))
    binaries={representation:hashlib.sha256(Path(world.lib._name).read_bytes()).hexdigest()}
    try:
        for target in times:
            if target>1+2*f.Q and representation=='words64':
                assert world.info['age']==98*f.Q
                old=world.runs;old_info=world.info;converted=from_word_runs(old,n)
                new=BlockWorld(tuple(right),tuple(left),age=old_info['age'],runs=converted)
                # Exact conversion is tested exhaustively elsewhere; check the
                # whole word plane here too, without taking any physical tick.
                a=np.zeros((n*(f.Q//64),2),dtype=np.uint64);begin=0
                for end,x,y in old:
                    end=int(end);a[begin:end]=(x,y);begin=end
                b=np.zeros((((len(a)+BLOCK-1)//BLOCK)*BLOCK,2),dtype=np.uint64);begin=0
                for row in converted:
                    end=int(row[0]);b[begin*BLOCK:end*BLOCK,0]=np.tile(row[1:1+BLOCK],end-begin);b[begin*BLOCK:end*BLOCK,1]=np.tile(row[1+BLOCK:],end-begin);begin=end
                np.testing.assert_array_equal(a,b[:len(a)]);del a,b
                offset=old_info['time'];prior={name:old_info[name] for name in prior};world.close();world=new;representation='blocks576'
                binaries[representation]=hashlib.sha256(Path(world.lib._name).read_bytes()).hexdigest()
            while offset+world.info['time']<target:
                world.run(min(250000,target-offset-world.info['time']))
                paths['.progress.json'].write_text(json.dumps(dict(status='running',seconds=time.monotonic()-started,physical_time=offset+world.info['time'],representation=representation,**world.info),indent=2)+'\n')
            frames['t'+str(target)]=world.runs;counts=[0,0];begin=0
            for row in world.runs:
                end=int(row[0])
                if representation=='words64':pop=(int(row[1]).bit_count(),int(row[2]).bit_count())
                else:pop=(sum(int(v).bit_count() for v in row[1:1+BLOCK]),sum(int(v).bit_count() for v in row[1+BLOCK:]))
                for k in range(2):counts[k]+=(end-begin)*pop[k]
                begin=end
            info=world.info;info['time']+=offset
            for key,value in prior.items():info[key]+=value
            row=dict(**info,representation=representation,flag_counts=counts,seconds=time.monotonic()-started);records.append(row);print(json.dumps(row),flush=True)
            np.savez_compressed(paths['.checkpoint.npz'],**frames,right_signals=np.array(right,dtype=np.uint8),left_signals=np.array(left,dtype=np.uint8))
        final=info
    finally:world.close()
    with paths['.npz'].open('xb') as stream:np.savez_compressed(stream,**frames,right_signals=np.array(right,dtype=np.uint8),left_signals=np.array(left,dtype=np.uint8))
    result=dict(scope=__doc__,input_prefix=str(source),input_json_sha256=hashlib.sha256(source.with_suffix('.json').read_bytes()).hexdigest(),input_artifact_sha256=x['artifact_sha256'],rule=r.identity(),colonies=n,records=records,final=final,seconds=time.monotonic()-started,binary_sha256=binaries,source_sha256={name:hashlib.sha256(data).hexdigest() for name,data in contents.items()},artifact_sha256=hashlib.sha256(paths['.npz'].read_bytes()).hexdigest(),archive_sha256=hashlib.sha256(paths['.tar.gz'].read_bytes()).hexdigest())
    paths['.json'].write_text(json.dumps(result,indent=2)+'\n');paths['.progress.json'].write_text(json.dumps(dict(status='complete',**final),indent=2)+'\n')
    print(json.dumps(dict(status='complete',seconds=result['seconds'],**final)),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--input',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();execute(args.input,args.output)
