"""Continue actual delivered signals through the full physical flag window.

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


def execute(source,output):
    source,output=Path(source),Path(output)
    paths={ext:output.with_suffix(ext) for ext in ('.json','.npz','.progress.json','.tar.gz')}
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
    names=['gacsca/fixed_rule/flag_words.py','gacsca/fixed_rule/flag_words.c','tests/fixed_rule/test_flag_words.py',str(Path(__file__).resolve().relative_to(root)),*x['source_sha256']]
    names=sorted(set(names));contents={name:(root/name).read_bytes() for name in names}
    with tarfile.open(paths['.tar.gz'],'x:gz') as archive:
        for name,data in contents.items():item=tarfile.TarInfo(name);item.size=len(data);archive.addfile(item,io.BytesIO(data))
    frames={};records=[];started=time.monotonic()
    times=(0,1,257,65537,1+f.Q//4,1+f.Q//2,1+f.Q,1+2*f.Q,1+3*f.Q,8*f.Q+1,16*f.Q+1,24*f.Q+1,32*f.Q+1)
    with World(tuple(right),tuple(left)) as world:
        binary=hashlib.sha256(Path(world.lib._name).read_bytes()).hexdigest()
        for target in times:
            while world.info['time']<target:
                world.run(min(250000,target-world.info['time']))
                paths['.progress.json'].write_text(json.dumps(dict(status='running',seconds=time.monotonic()-started,**world.info),indent=2)+'\n')
            frames['t'+str(target)]=world.runs;counts=[0,0];begin=0
            for end,a,b in map(lambda row:tuple(map(int,row)),world.runs):
                counts[0]+=(end-begin)*a.bit_count();counts[1]+=(end-begin)*b.bit_count();begin=end
            row=dict(**world.info,flag_counts=counts,seconds=time.monotonic()-started);records.append(row);print(json.dumps(row),flush=True)
        final=world.info
    with paths['.npz'].open('xb') as stream:np.savez_compressed(stream,**frames,right_signals=np.array(right,dtype=np.uint8),left_signals=np.array(left,dtype=np.uint8))
    result=dict(scope=__doc__,input_prefix=str(source),input_json_sha256=hashlib.sha256(source.with_suffix('.json').read_bytes()).hexdigest(),input_artifact_sha256=x['artifact_sha256'],rule=r.identity(),colonies=n,records=records,final=final,seconds=time.monotonic()-started,binary_sha256=binary,source_sha256={name:hashlib.sha256(data).hexdigest() for name,data in contents.items()},artifact_sha256=hashlib.sha256(paths['.npz'].read_bytes()).hexdigest(),archive_sha256=hashlib.sha256(paths['.tar.gz'].read_bytes()).hexdigest())
    paths['.json'].write_text(json.dumps(result,indent=2)+'\n');paths['.progress.json'].write_text(json.dumps(dict(status='complete',**final),indent=2)+'\n')
    print(json.dumps(dict(status='complete',seconds=result['seconds'],**final)),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--input',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();execute(args.input,args.output)
