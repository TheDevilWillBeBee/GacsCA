"""Candidate-B unforced clearing-bound probe on explicitly supplied flag data.

The input is a literal-rule checkpoint used only as arbitrary initial flag data.
This is NOT a continuation of that history under the same rule and is NOT a
candidate-B hierarchical macrostep. It exercises the bound: canonical geometry,
zero Wf, age >=98Q => F1 clears within Q/2 ticks, then F2 within another Q/2.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import tarfile
import time
import numpy as np
from gacsca.fixed_rule import repair_b_rule as f
from gacsca.fixed_rule.repair_b_flags import World


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def execute(source,output):
    source,output=Path(source),Path(output);paths={ext:output.with_suffix(ext) for ext in ('.json','.npz','.tar.gz')}
    if any(path.exists() for path in paths.values()):raise FileExistsError('preserve evidence')
    with np.load(source,allow_pickle=False) as a:runs=a['runs'];right=a['right_signals'];left=a['left_signals']
    root=Path(__file__).resolve().parents[2];files=sorted([*root.glob('gacsca/fixed_rule/repair_b_*.py'),*root.glob('gacsca/fixed_rule/repair_b_*.c'),*root.glob('tests/fixed_rule/test_repair_b_*.py'),Path(__file__).resolve()])
    contents={str(path.relative_to(root)):path.read_bytes() for path in files}
    with tarfile.open(paths['.tar.gz'],'x:gz') as archive:
        for name,data in contents.items():item=tarfile.TarInfo(name);item.size=len(data);archive.addfile(item,io.BytesIO(data))
    started=time.monotonic();frames={};records=[]
    with World(right.tolist(),left.tolist(),age=98*f.Q,runs=runs) as world:
        for target in (0,f.Q//2,f.Q,30*f.Q):
            world.run(target-world.info['time']);a=world.runs;frames['t'+str(target)]=a
            if target>=f.Q//2:assert not np.any(a[:,1])
            if target>=f.Q:np.testing.assert_array_equal(a,np.array([(len(right)*f.Q//64,0,0)],dtype=np.uint64))
            row=dict(**world.info,seconds=time.monotonic()-started);records.append(row);print(json.dumps(row),flush=True)
        binary=sha(world.lib._name)
    with paths['.npz'].open('xb') as stream:np.savez_compressed(stream,**frames,initial_runs=runs,right_signals=right,left_signals=left)
    result=dict(scope=__doc__,rule=f.identity(),passed=True,records=records,seconds=time.monotonic()-started,source_input=str(source),source_input_sha256=sha(source),source_sha256={name:hashlib.sha256(data).hexdigest() for name,data in contents.items()},artifact_sha256=sha(paths['.npz']),archive_sha256=sha(paths['.tar.gz']),binary_sha256=binary)
    paths['.json'].write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(status='complete',seconds=result['seconds'])),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--input',required=True,type=Path);parser.add_argument('--output',required=True,type=Path);args=parser.parse_args();execute(args.input,args.output)
