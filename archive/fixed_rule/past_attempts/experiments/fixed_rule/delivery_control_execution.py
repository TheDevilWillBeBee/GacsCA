"""Mail-free controller suffix of the unchanged fixed delivery rule.

Four physical flag fields are represented by the separate exact flag component;
these arrays alone are deliberately labelled controller projections.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import tarfile
import time
from unittest.mock import patch
import numpy as np
from gacsca.fixed_rule import delivery_rule as f,delivery_projected as r,delivery_program as p
from gacsca.fixed_rule.delivery_control_world import World
from gacsca.fixed_rule.wordcode import Program


def words(core,addresses):
    g=p.layout();return np.stack([row[np.array(addresses),r.COL['data']] for row in core.reshape(-1,g.computation_cells,len(r.SCHEMA))])


def execute(source,output):
    source,output=Path(source),Path(output);paths={ext:output.with_suffix(ext) for ext in ('.json','.npz','.tar.gz')}
    if any(path.exists() for path in paths.values()):raise FileExistsError('preserve evidence')
    x=json.loads(source.with_suffix('.json').read_text());assert hashlib.sha256(source.with_suffix('.npz').read_bytes()).hexdigest()==x['artifact_sha256']
    with np.load(source.with_suffix('.npz'),allow_pickle=False) as a:initial=a['stored_final'];top=r.cells_from_array(a['initial_top'])
    assert x['rule']==json.loads(json.dumps(r.identity()))
    expected=r.step_ring(top);expected_raw=np.array([f.encode_cell(r.lift(c)) for c in expected],dtype=np.uint64);old=np.array([f.encode_cell(r.lift(c)) for c in top],dtype=np.uint64)
    root=Path(__file__).resolve().parents[2]
    names=sorted(set(x['source_sha256'])|{'gacsca/fixed_rule/delivery_control_world.py','gacsca/fixed_rule/delivery_control_world.c','gacsca/fixed_rule/delivery_control_description.py','tests/fixed_rule/test_delivery_control.py',str(Path(__file__).resolve().relative_to(root))})
    contents={name:(root/name).read_bytes() for name in names}
    with tarfile.open(paths['.tar.gz'],'x:gz') as archive:
        for name,data in contents.items():item=tarfile.TarInfo(name);item.size=len(data);archive.addfile(item,io.BytesIO(data))
    g=p.layout();epoch=96*f.Q-1;probes=[];snapshots={};votes=[];holds=[];metrics={};started=time.monotonic()
    with World(initial) as world:
        binary=hashlib.sha256(Path(world.lib._name).read_bytes()).hexdigest()
        for age in (96*f.Q,96*f.Q+1,104*f.Q,112*f.Q,112*f.Q+1,120*f.Q,f.U-1,f.U):
            with patch.object(Program,'evaluate',side_effect=AssertionError('host evaluation')),patch.object(f,'local_step',side_effect=AssertionError('host transition')):
                row=world.run(age-epoch-world.time)
            for key,value in row.items():metrics[key]=metrics.get(key,0)+value
            core=world.cores
            for name in ('lp_target','lp_data','lp_remaining','lp_valid','rp_target','rp_data','rp_remaining','rp_valid'):assert not np.any(world.stored[:,r.COL[name]])
            np.testing.assert_array_equal(words(core,g.info),expected_raw if age==f.U else old)
            if age==112*f.Q+1:
                expected_neighbors=np.stack([old[(np.arange(len(top))+j)%len(top)] for j in range(-5,6)],axis=1).reshape(len(top),-1)
                vote=words(core,g.votes);np.testing.assert_array_equal(vote,expected_neighbors);votes.append(vote)
            if age>=120*f.Q:
                hold=words(core,g.hold);np.testing.assert_array_equal(hold,expected_raw);holds.append(hold)
            if age in (104*f.Q,112*f.Q,120*f.Q,f.U-1,f.U):snapshots['age'+str(age)]=world.stored
            probes.append(dict(age=age%f.U,time=world.time,mail_free=True));print(json.dumps(probes[-1]),flush=True)
        assert world.decode()==expected;assert not np.any(world.stored[:,r.COL['head']]);assert world.pending==0
        with paths['.npz'].open('xb') as stream:np.savez_compressed(stream,**snapshots,votes=np.stack(votes),holds=np.stack(holds),decoded=r.array_from_cells(expected),lifted=expected_raw)
    result=dict(scope=__doc__,rule=r.identity(),input_prefix=str(source),input_json_sha256=hashlib.sha256(source.with_suffix('.json').read_bytes()).hexdigest(),input_artifact_sha256=x['artifact_sha256'],metrics=metrics,probes=probes,seconds=time.monotonic()-started,source_sha256={name:hashlib.sha256(data).hexdigest() for name,data in contents.items()},binary_sha256=binary,artifact_sha256=hashlib.sha256(paths['.npz'].read_bytes()).hexdigest(),archive_sha256=hashlib.sha256(paths['.tar.gz'].read_bytes()).hexdigest())
    paths['.json'].write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(status='complete',seconds=result['seconds'],metrics=metrics)),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--input',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();execute(args.input,args.output)
