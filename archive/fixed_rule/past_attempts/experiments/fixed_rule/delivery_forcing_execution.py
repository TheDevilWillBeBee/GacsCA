"""Full-state composition through the entire actual physical forcing window.

Replay from the audited delivery prefix, compare the previous saved cutoff,
and save complete core/tail state plus exact flags over every physical site.
This stops at 98Q; it does not claim a full work-period macrostep.
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
from gacsca.fixed_rule import delivery_rule as f,delivery_projected as r,delivery_program as p,delivery_native as native
from gacsca.fixed_rule.delivery_composed_world import World
from gacsca.fixed_rule.wordcode import Program


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def execute(source,checkpoint,output):
    source,checkpoint,output=Path(source),Path(checkpoint),Path(output)
    paths={ext:output.with_suffix(ext) for ext in ('.json','.npz','.tar.gz','.progress.json')}
    if any(path.exists() for path in paths.values()):raise FileExistsError('preserve prior evidence')
    x=json.loads(source.with_suffix('.json').read_text());assert sha(source.with_suffix('.npz'))==x['artifact_sha256']
    assert x['rule']==json.loads(json.dumps(r.identity()))
    with np.load(source.with_suffix('.npz'),allow_pickle=False) as a:initial=a['stored_final'];old=a['initial_lifted']
    with np.load(checkpoint,allow_pickle=False) as a:cutoff={name:a[name] for name in a.files}
    assert np.all(initial[:,r.COL['age']]==96*f.Q-1)
    root=Path(__file__).resolve().parents[2]
    added=['gacsca/fixed_rule/delivery_control_world.py','gacsca/fixed_rule/delivery_control_world.c','gacsca/fixed_rule/delivery_control_description.py','gacsca/fixed_rule/delivery_composed_world.py','gacsca/fixed_rule/flag_words.py','gacsca/fixed_rule/flag_words.c','tests/fixed_rule/test_delivery_composed.py','tests/fixed_rule/test_flag_words.py',str(Path(__file__).resolve().relative_to(root))]
    names=sorted(set(x['source_sha256'])|set(added));contents={name:(root/name).read_bytes() for name in names}
    with tarfile.open(paths['.tar.gz'],'x:gz') as archive:
        for name,data in contents.items():item=tarfile.TarInfo(name);item.size=len(data);archive.addfile(item,io.BytesIO(data))
    started=time.monotonic();g=p.layout();records=[];frames={};checks=0;controller_metrics={}
    with World(initial) as w:
        np.testing.assert_array_equal(w.flags.signals[0],cutoff['right_signals']);np.testing.assert_array_equal(w.flags.signals[1],cutoff['left_signals'])
        binaries={name:sha(part.lib._name) for name,part in (('controller',w.control),('flags',w.flags))}
        for target in (0,1,257,65537,1+f.Q,1+2*f.Q):
            while w.time<target:
                with patch.object(Program,'evaluate',side_effect=AssertionError('host evaluator')),patch.object(f,'local_step',side_effect=AssertionError('host transition')):metrics=w.run(min(250000,target-w.time))
                for key,value in metrics['controller'].items():controller_metrics[key]=controller_metrics.get(key,0)+value
                paths['.progress.json'].write_text(json.dumps(dict(status='running',seconds=time.monotonic()-started,**w.flags.info),indent=2)+'\n')
            info=w.flags.info;frames['flags_t'+str(target)]=w.flags.runs
            # Sample every spatial RLE boundary, every physical boundary and
            # actual core state against complete native F on the next tick.
            # This is a cross-check; the long replay uses the packed engine.
            positions={c*f.Q+a for c in range(w.colonies) for a in (0,3,g.info[0],g.hold[0],f.Q-3,f.Q-1)}
            for end in w.flags.runs[:,0]:
                for delta in (-6,-1,0,1,5):positions.add((int(end)*64+delta)%(w.colonies*f.Q))
            expected={}
            for position in sorted(positions):
                cells=tuple(r.lift(w.cell(*divmod((position+j)%(w.colonies*f.Q),f.Q))) for j in range(-5,6))
                expected[position]=r.project(native.local_step(cells))
            # A separately constructed one-tick composed world does not alter
            # the main replay, including at the immutable cutoff checkpoint.
            with World(w.control.stored,flag_runs=w.flags.runs) as probe:
                probe.run(1)
                for position,value in expected.items():assert probe.cell(*divmod(position,f.Q))==value,(target,position)
            checks+=len(expected)
            a=w.stored.reshape(w.colonies,g.computation_cells+5,len(r.SCHEMA));np.testing.assert_array_equal(a[:,np.array(g.info),r.COL['data']],old)
            records.append(dict(**info,complete_native_cross_checks=len(expected),seconds=time.monotonic()-started));print(json.dumps(records[-1]),flush=True)
        np.testing.assert_array_equal(w.flags.runs,cutoff['runs'])
        assert w.flags.info['age']==98*f.Q
        stored=w.stored
        assert not np.any(stored[:,[r.COL['wf1'],r.COL['wf2']]])
        counts=[0,0];begin=0
        for end,a,b in map(lambda row:tuple(map(int,row)),w.flags.runs):
            for k,value in enumerate((a,b)):counts[k]+=(end-begin)*value.bit_count()
            begin=end
        with paths['.npz'].open('xb') as stream:np.savez_compressed(stream,**frames,stored_final=stored,controller_final=w.control.stored,right_signals=cutoff['right_signals'],left_signals=cutoff['left_signals'],decoded=r.array_from_cells(w.decode()))
    result=dict(passed=True,scope=__doc__,rule=r.identity(),input_prefix=str(source),input_artifact_sha256=x['artifact_sha256'],checkpoint=str(checkpoint),checkpoint_sha256=sha(checkpoint),checkpoint_replay_exact=True,start_age=96*f.Q-1,final_age=98*f.Q,physical_ticks=2*f.Q+1,physical_sites=len(old)*f.Q,flag_counts=counts,records=records,controller_metrics=controller_metrics,complete_native_cross_checks=checks,seconds=time.monotonic()-started,binary_sha256=binaries,source_sha256={name:hashlib.sha256(data).hexdigest() for name,data in contents.items()},artifact_sha256=sha(paths['.npz']),archive_sha256=sha(paths['.tar.gz']),limitation='30Q physical flag ticks remain before commit; no complete delivery-rule macrostep or deeper dynamics')
    paths['.json'].write_text(json.dumps(result,indent=2)+'\n');paths['.progress.json'].write_text(json.dumps(dict(status='complete',final_age=98*f.Q))+'\n');print(json.dumps(dict(status='complete',seconds=result['seconds'],checks=checks,flag_counts=counts)),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--input',type=Path,required=True);parser.add_argument('--checkpoint',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();execute(args.input,args.checkpoint,args.output)
