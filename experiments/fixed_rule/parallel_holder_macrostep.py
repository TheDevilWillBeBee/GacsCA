"""Continue the actual redundant-holder prefix through one complete macrostep."""
import argparse,hashlib,io,json,tarfile,time
from pathlib import Path
from unittest.mock import patch
import numpy as np
from gacsca.fixed_rule import parallel_holder_rule as f,parallel_holder_projected as r,parallel_holder_program as p,parallel_holder_quotient as q,parallel_holder_flag_profile as profile,parallel_holder_native as native
from gacsca.fixed_rule.parallel_holder_suffix_world import World
from gacsca.fixed_rule.wordcode import Program


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def execute(prefix,output):
    prefix,stem=Path(prefix),Path(output);paths={ext:stem.with_suffix(ext) for ext in ('.json','.npz','.tar.gz','.progress.json')}
    if any(path.exists() for path in paths.values()):raise FileExistsError('preserve evidence')
    old=json.loads(prefix.with_suffix('.json').read_text());assert sha(prefix.with_suffix('.npz'))==old['artifact_sha256']
    with np.load(prefix.with_suffix('.npz'),allow_pickle=False) as data:initial=data['logical_stored_final'];expected=data['expected_hold'];top=data['initial_top'];info=data['initial_lifted']
    root=Path(__file__).resolve().parents[2]
    files=sorted([*root.glob('gacsca/fixed_rule/*.py'),*root.glob('gacsca/fixed_rule/*.c'),*root.glob('gacsca/fixed_rule/*.cpp'),*root.glob('gacsca/fixed_rule/*.h'),*root.glob('gacsca/fixed_rule/*.cu'),*root.glob('tests/fixed_rule/*.py'),*root.glob('experiments/fixed_rule/*.py')])
    contents={str(path.relative_to(root)):path.read_bytes() for path in files};hashes={name:hashlib.sha256(data).hexdigest() for name,data in contents.items()}
    with tarfile.open(paths['.tar.gz'],'x:gz') as archive:
        for name,data in contents.items():row=tarfile.TarInfo(name);row.size=len(data);archive.addfile(row,io.BytesIO(data))
    g=p.layout();metrics=dict(physical_ticks=0,literal_core_ticks=0,quiet_ticks_skipped=0,scan_ticks_skipped=0,local_evaluations=0);probes=[];samples=[];keys=[];start=time.monotonic()
    evaluation=112*f.Q+g.schedule(*g.stage_ranges[4])[0]
    milestones=sorted(set((profile.START,96*f.Q,96*f.Q+1,96*f.Q+2,96*f.Q+(f.Q-8+2)//3,98*f.Q-1,98*f.Q,98*f.Q+1,98*f.Q+f.Q//2,99*f.Q,104*f.Q,112*f.Q,112*f.Q+1,evaluation,120*f.Q,f.U-1)))
    with World(initial) as world:
        binary=sha(world.control.lib._name)
        for age in milestones:
            if age<world.age:continue
            with patch.object(Program,'evaluate',side_effect=AssertionError('host evaluator')),patch.object(f,'local_step',side_effect=AssertionError('host upper transition')):
                for ticks in (age-world.age,):
                    row=world.run(ticks)
                    for key,value in row.items():metrics[key]+=value
            lo,hi=profile.interval(age);positions=sorted({a%f.Q for base in (0,lo,hi,g.info[f.COL['s2_data']],g.computation_cells-1) for a in range(base-7,base+8)})
            before=[];case_keys=[]
            for colony in (0,7,14):
                for address in positions:
                    before.append(tuple(r.lift(world.cell(*divmod((colony*f.Q+address+j)%(world.colonies*f.Q),f.Q))) for j in range(-7,8)));case_keys.append((age,colony,address))
            want=[r.project(native.local_step(cells)) for cells in before]
            with patch.object(Program,'evaluate',side_effect=AssertionError('host evaluator')),patch.object(f,'local_step',side_effect=AssertionError('host upper transition')):row=world.run(1)
            for key,value in row.items():metrics[key]+=value
            for (a,colony,address),cell,raw in zip(case_keys,want,before):
                actual=world.cell(colony,address);assert actual==cell,(a,colony,address)
                samples.append((native.array_from_cells(raw),np.array(f.encode_cell(r.lift(actual)),dtype=np.uint64)));keys.append((a,colony,address))
            stored=world.logical_stored.reshape(world.colonies,g.computation_cells+5,len(q.SCHEMA))
            if world.age<=96*f.Q or world.age>=evaluation:np.testing.assert_array_equal(stored[:,g.hold,q.COL['data']],expected)
            np.testing.assert_array_equal(stored[:,g.info,q.COL['data']],expected if world.age==f.U else info)
            row=dict(age=world.age,flag_interval=profile.interval(world.age),complete_native_checks=len(want),pending=world.control.pending)
            probes.append(row);print(json.dumps(row),flush=True);paths['.progress.json'].write_text(json.dumps(dict(status='running',age=world.age,seconds=time.monotonic()-start))+'\n')
        assert world.age==f.U and world.control.pending==0
        decoded=world.decode();np.testing.assert_array_equal(r.array_from_cells(decoded),r.array_from_cells(tuple(r.project(f.decode_cell(row.tolist())) for row in expected)))
        final=world.logical_stored;assert not np.any(final[:,[q.COL[n] for n in ('f1','f2','wf1','wf2')]])
        with paths['.npz'].open('xb') as stream:np.savez_compressed(stream,logical_initial=initial,logical_final=final,initial_top=top,expected=expected,decoded=r.array_from_cells(decoded),sample_keys=np.array(keys),sample_inputs=np.stack([pair[0] for pair in samples]),sample_outputs=np.stack([pair[1] for pair in samples]))
    assert metrics['physical_ticks']==f.U-profile.START==sum(metrics[k] for k in ('literal_core_ticks','quiet_ticks_skipped','scan_ticks_skipped'))
    result=dict(scope=__doc__,rule=r.identity(),prefix=str(prefix),prefix_json_sha256=sha(prefix.with_suffix('.json')),source_sha256=hashes,archive_sha256=sha(paths['.tar.gz']),artifact_sha256=sha(paths['.npz']),binary_sha256=binary,physical_prefix_ticks=profile.START,total_macrostep_ticks=f.U,metrics=metrics,seconds=time.monotonic()-start,probes=probes,complete_native_checks=len(keys),limitation='one complete one-link macrostep on the certified flag-profile family; no successive periods or depth-two dynamics claimed')
    paths['.json'].write_text(json.dumps(result,indent=2)+'\n');paths['.progress.json'].write_text(json.dumps(dict(status='complete',age=f.U))+'\n');print(json.dumps(dict(status='complete',seconds=result['seconds'],metrics=metrics)))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--prefix',required=True,type=Path);parser.add_argument('--output',required=True,type=Path);args=parser.parse_args();execute(args.prefix,args.output)
