"""Complete physical candidate-B suffix, including actual flags and Info commit.

Consumes a physical prefix artifact, never a freshly encoded upper state.
Controller/Data/Signal and all actual flags are composed under the tested
canonical, mail-free factorization. Host upper transitions are only diagnostics.
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
from gacsca.fixed_rule import serial_vote_rule as f,serial_vote_projected as r,serial_vote_program as p
from gacsca.fixed_rule.serial_vote_composed_world import World
from gacsca.fixed_rule.wordcode import Program


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def execute(source,output):
    source,output=Path(source),Path(output);paths={ext:output.with_suffix(ext) for ext in ('.json','.npz','.tar.gz','.progress.json')}
    if any(path.exists() for path in paths.values()):raise FileExistsError('preserve prior evidence')
    x=json.loads(source.with_suffix('.json').read_text());assert sha(source.with_suffix('.npz'))==x['artifact_sha256'];assert x['rule']==json.loads(json.dumps(r.identity()))
    with np.load(source.with_suffix('.npz'),allow_pickle=False) as a:initial=a['stored_final'];top=r.cells_from_array(a['initial_top']);old=a['initial_lifted']
    expected=r.step_ring(top);raw=np.array([f.encode_cell(r.lift(c)) for c in expected],dtype=np.uint64)
    assert np.all(initial[:,r.COL['age']]==96*f.Q-1)
    root=Path(__file__).resolve().parents[2];names=sorted(set(x['source_sha256'])|{str(Path(__file__).resolve().relative_to(root))})
    contents={name:(root/name).read_bytes() for name in names}
    with tarfile.open(paths['.tar.gz'],'x:gz') as archive:
        for name,data in contents.items():item=tarfile.TarInfo(name);item.size=len(data);archive.addfile(item,io.BytesIO(data))
    started=time.monotonic();g=p.layout();vote_complete=112*f.Q+g.schedule(g.entries[4],g.description_instruction)[0];epoch=96*f.Q-1;frames={};records=[];metrics={};votes=[];holds=[]
    with World(initial) as world:
        binaries={name:sha(part.lib._name) for name,part in (('controller',world.control),('flags',world.flags))}
        for age in (96*f.Q,98*f.Q,99*f.Q,104*f.Q,112*f.Q,112*f.Q+1,vote_complete,120*f.Q,f.U-1,f.U):
            target=age-epoch
            while world.time<target:
                with patch.object(Program,'evaluate',side_effect=AssertionError('host evaluator')),patch.object(f,'local_step',side_effect=AssertionError('host upper transition')):row=world.run(min(250000,target-world.time))
                for key,value in row['controller'].items():metrics[key]=metrics.get(key,0)+value
                paths['.progress.json'].write_text(json.dumps(dict(status='running',time=world.time,seconds=time.monotonic()-started,flags=world.flags.info),indent=2)+'\n')
            stored=world.stored;a=stored.reshape(world.colonies,g.computation_cells+5,len(r.SCHEMA))
            np.testing.assert_array_equal(a[:,np.array(g.info),r.COL['data']],raw if age==f.U else old)
            for name,_ in r.SCHEMA:
                if name.startswith(('lp_','rp_')):assert not np.any(stored[:,r.COL[name]])
            if age>=99*f.Q:
                np.testing.assert_array_equal(world.flags.runs,np.array([(world.colonies*f.Q//64,0,0)],dtype=np.uint64))
                assert not np.any(stored[:,[r.COL[name] for name in ('f1','f2','wf1','wf2')]])
            if age==112*f.Q+1:assert not np.any(a[:,np.array(g.votes),r.COL['data']])
            if age==vote_complete:
                want=np.stack([old[(np.arange(len(top))+j)%len(top)] for j in range(-5,6)],axis=1).reshape(len(top),-1)
                value=a[:,np.array(g.votes),r.COL['data']];np.testing.assert_array_equal(value,want);votes.append(value)
            if age>=120*f.Q:
                value=a[:,np.array(g.hold),r.COL['data']];np.testing.assert_array_equal(value,raw);holds.append(value)
            frames['flags_age'+str(age)]=world.flags.runs
            if age in (98*f.Q,99*f.Q,f.U-1,f.U):frames['stored_age'+str(age)]=stored
            records.append(dict(age=age%f.U,physical_time=world.time,flags=world.flags.info,seconds=time.monotonic()-started));print(json.dumps(records[-1]),flush=True)
        assert world.decode()==expected and world.control.pending==0
        assert not np.any(world.stored[:,r.COL['head']])
        # The whole padding state must be recoverable at the period boundary.
        for c in range(world.colonies):
            for address in (g.computation_cells,f.Q//2,f.Q-6):
                assert world.cell(c,address)==r.Cell(address=address)
        with paths['.npz'].open('xb') as stream:np.savez_compressed(stream,**frames,stored_final=world.stored,initial_top=r.array_from_cells(top),initial_lifted=old,decoded=r.array_from_cells(expected),lifted=raw,votes=np.stack(votes),holds=np.stack(holds))
        final_flags=world.flags.info
    assert metrics['physical_ticks']==32*f.Q+1==sum(metrics[k] for k in ('literal_core_ticks','quiet_ticks_skipped','scan_ticks_skipped'))
    result=dict(scope=__doc__,rule=r.identity(),input_prefix=str(source),input_json_sha256=sha(source.with_suffix('.json')),input_artifact_sha256=x['artifact_sha256'],records=records,controller_metrics=metrics,final_flags=final_flags,complete_physical_macrostep_ticks=f.U,prefix_ticks=epoch,suffix_ticks=32*f.Q+1,seconds=time.monotonic()-started,source_sha256={name:hashlib.sha256(data).hexdigest() for name,data in contents.items()},binary_sha256=binaries,artifact_sha256=sha(paths['.npz']),archive_sha256=sha(paths['.tar.gz']),limitation='serial temporal-vote candidate-B rule; canonical noiseless domain; no complete spatial repair, organized termination, deeper dynamics or noise theorem')
    paths['.json'].write_text(json.dumps(result,indent=2)+'\n');paths['.progress.json'].write_text(json.dumps(dict(status='complete',physical_time=32*f.Q+1))+'\n');print(json.dumps(dict(status='complete',seconds=result['seconds'],flags=final_flags)),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--input',required=True,type=Path);parser.add_argument('--output',required=True,type=Path);args=parser.parse_args();execute(args.input,args.output)
