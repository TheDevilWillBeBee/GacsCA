"""Two complete clock periods of the fixed, fully described temporal scheduler."""
import argparse
from dataclasses import replace
import hashlib
import io
import json
from pathlib import Path
import tarfile
import time
import zipfile
import numpy as np
from gacsca.fixed_rule import early_projected as r,clock_rule as f,early_program as p
from gacsca.fixed_rule.early_world import World


def initial_ring():
    cells=[r.Cell(address=100+i,age=1) for i in range(23)]
    cells[11]=replace(cells[11],address=143,age=321,data=f.MASK,f2=1,head=1,phase=f.READ_B,rb=143,rd=112,value=f.MASK,alu=f.NAND)
    cells[12]=replace(cells[12],data=0xFEDCBA9876543210)
    for i,value in ((4,3),(6,5),(7,6)):cells[i]=replace(cells[i],data=value)
    cells[5]=replace(cells[5],address=101,age=112*f.Q,data=99)
    cells[18]=replace(cells[18],address=p.layout().info[0],age=f.U-1,data=123)
    cells[19]=replace(cells[19],data=0x1122334455667788)
    return tuple(cells)


def words_at(cores,addresses):
    g=p.layout();return np.stack([cores[base+np.array(addresses),r.COL['data']] for base in range(0,len(cores),g.computation_cells)])


def simulation_digest(core):
    state=core.copy();state[:,r.COL['age']]=0
    return hashlib.sha256(state.tobytes()).hexdigest()


def execute(stem,steps=2):
    stem=Path(stem);stem.parent.mkdir(parents=True,exist_ok=True)
    paths={ext:stem.with_suffix(ext) for ext in ('.json','.npz','.tar.gz','.progress.json','.rests.npz')}
    if any(path.exists() for path in paths.values()):raise FileExistsError('preserve prior evidence')
    if steps<2:raise ValueError('successive periods required')
    root=Path(__file__).resolve().parents[2]
    files=sorted([*root.glob('gacsca/fixed_rule/*.py'),*root.glob('gacsca/fixed_rule/*.c'),*root.glob('tests/fixed_rule/*.py'),*root.glob('experiments/fixed_rule/*.py')])
    contents={str(path.relative_to(root)):path.read_bytes() for path in files}
    hashes={name:hashlib.sha256(data).hexdigest() for name,data in contents.items()}
    with tarfile.open(paths['.tar.gz'],'x:gz') as archive:
        for name,data in contents.items():
            item=tarfile.TarInfo(name);item.size=len(data);archive.addfile(item,io.BytesIO(data))
    g=p.layout();reference=initial_ring();frames=[];lifts=[];periods=[];probes=[];stage_holds=[];history_frames=[];history_keys=[];vote_frames=[];repair_frames=[]
    times=(p.repair_ticks(),16*f.Q,32*f.Q,48*f.Q,64*f.Q,72*f.Q,72*f.Q+1,80*f.Q,96*f.Q,104*f.Q,112*f.Q,112*f.Q+1,120*f.Q,f.U-1,f.U)
    initial_core=r.encode_cores(reference)
    for base in range(0,len(initial_core),g.computation_cells):
        for name in f.STATIC:
            initial_core[base+g.info[f.COL[name]],r.COL['data']]^=np.uint64((1<<dict(f.SCHEMA)[name])-1)
    corrupt_initial=words_at(initial_core,g.info)
    with zipfile.ZipFile(paths['.rests.npz'],'x',compression=zipfile.ZIP_DEFLATED) as rest_archive,World(initial_core) as world:
        try:world.decode()
        except ValueError as error:
            if 'program record' not in str(error):raise
        else:raise AssertionError('corrupted program must fail strict initial decoding')
        binary=hashlib.sha256(Path(world.lib._name).read_bytes()).hexdigest()
        frames.append(r.array_from_cells(reference));lifts.append(words_at(world.cores,g.info))
        for period in range(1,steps+1):
            started=time.monotonic();expected=r.step_ring(reference) # diagnostics only
            old=np.array([f.encode_cell(r.lift(c)) for c in reference],dtype=np.uint64)
            expected_lift=np.array([f.encode_cell(r.lift(c)) for c in expected],dtype=np.uint64)
            neighbors=np.stack([old[(np.arange(23)+j)%23] for j in range(-5,6)],axis=1).reshape(23,-1)
            metrics=dict(physical_ticks=0,literal_core_ticks=0,quiet_ticks_skipped=0,scan_ticks_skipped=0,local_evaluations=0)
            rest_digest={}
            for t in times:
                target=(period-1)*f.U+t
                while world.time<target:
                    result=world.run(min(10000000,target-world.time))
                    for key,value in result.items():metrics[key]+=value
                    progress=dict(status='running',period=period,physical_time=world.time,elapsed_seconds=time.monotonic()-started,**metrics)
                    paths['.progress.json'].write_text(json.dumps(progress,indent=2)+'\n')
                core=world.cores;row=dict(period=period,offset=t,pending=world.pending)
                if t==p.repair_ticks():repair_frames.append(words_at(core,g.info))
                if t in (16*f.Q,48*f.Q,72*f.Q):
                    last={16*f.Q:0,48*f.Q:1,72*f.Q:2}[t]
                    for history in range(last+1):
                        addresses=[g.history(history,j,k) for j in range(-5,6) for k in range(f.FIELDS)]
                        gathered=words_at(core,addresses);history_frames.append(gathered);history_keys.append((period,t,history))
                        mismatch=int(np.count_nonzero(gathered!=neighbors));row['history_'+str(history)+'_mismatches']=mismatch
                        if mismatch:raise AssertionError(row)
                if t in (72*f.Q+1,112*f.Q+1):
                    voted=words_at(core,g.votes);vote_frames.append(voted)
                    row['vote_mismatches']=int(np.count_nonzero(voted!=neighbors))
                    if row['vote_mismatches']:raise AssertionError(row)
                if t in (80*f.Q,120*f.Q):
                    hold=words_at(core,g.hold);row['hold_mismatches']=int(np.count_nonzero(hold!=expected_lift));stage_holds.append(hold)
                    if row['hold_mismatches']:raise AssertionError(row)
                if t in (16*f.Q,48*f.Q,80*f.Q,104*f.Q,120*f.Q):rest_digest[t]=simulation_digest(core)
                for stage,(lo,hi) in enumerate(((16*f.Q,32*f.Q),(48*f.Q,64*f.Q),(80*f.Q,96*f.Q),(104*f.Q,112*f.Q),(120*f.Q,f.U-1))):
                    if t in (lo,hi):
                        key=f'p{period}_s{stage}_'+('begin' if t==lo else 'end')+'.npy'
                        with rest_archive.open(key,'w',force_zip64=True) as stream:np.lib.format.write_array(stream,core,allow_pickle=False)
                    if t==hi:
                        row['rest_unchanged']=simulation_digest(core)==rest_digest[lo]
                        if not row['rest_unchanged'] or world.pending:raise AssertionError(row)
                if t<f.U:
                    row['info_unchanged']=np.array_equal(words_at(core,g.info),old)
                    if not row['info_unchanged']:raise AssertionError(row)
                probes.append(row);print(json.dumps(dict(status='probe',**row)),flush=True)
            actual=world.decode();observed=r.array_from_cells(actual);lifted=words_at(world.cores,g.info)
            row=dict(period=period,elapsed_seconds=time.monotonic()-started,**metrics,
                     projected_mismatches=int(np.count_nonzero(observed!=r.array_from_cells(expected))),
                     lifted_mismatches=int(np.count_nonzero(lifted!=expected_lift)),boundary=world.check_boundary(),pending_packets=world.pending)
            assert row['projected_mismatches']==row['lifted_mismatches']==row['pending_packets']==0 and row['boundary']
            assert sum(metrics[k] for k in ('literal_core_ticks','quiet_ticks_skipped','scan_ticks_skipped'))==metrics['physical_ticks']==f.U
            periods.append(row);frames.append(observed);lifts.append(lifted);reference=actual
            print(json.dumps(dict(status='period',**row)),flush=True)
        with paths['.npz'].open('xb') as stream:
            np.savez_compressed(stream,frames=np.stack(frames),lifted_frames=np.stack(lifts),holds=np.stack(stage_holds),core_final=world.cores,rom=r.rom(),padding_packet_count=np.array(world.pending),corrupt_initial=corrupt_initial,repair_frames=np.stack(repair_frames),history_frames=np.stack(history_frames),history_keys=np.array(history_keys,dtype=np.int64),vote_frames=np.stack(vote_frames))
    manifest=dict(scope='early program-repair plus clocked complete-controller self-simulation; corrupted raw program words at initialization; signal/trickle initiation and spatial redundancy missing',
        physical_rule=r.identity(),timing=g.timing_certificate(),represented_cells=23,physical_cells=23*f.Q,
        explicit_core_cells=23*g.computation_cells,core_array_bytes=23*g.computation_cells*len(r.SCHEMA)*8,
        periods=periods,probes=probes,total_ticks=sum(row['physical_ticks'] for row in periods),total_seconds=sum(row['elapsed_seconds'] for row in periods),
        source_sha256=hashes,compiled_binary_sha256=binary,artifact_sha256=hashlib.sha256(paths['.npz'].read_bytes()).hexdigest(),source_archive_sha256=hashlib.sha256(paths['.tar.gz'].read_bytes()).hexdigest(),
        rest_artifact_sha256=hashlib.sha256(paths['.rests.npz'].read_bytes()).hexdigest(),early_repair_ticks=p.repair_ticks(),
        restriction='canonical healthy physical structure, uniform actual Age; exact quiet and guarded head-scan acceleration; no upper-transition replacement')
    paths['.json'].write_text(json.dumps(manifest,indent=2)+'\n');paths['.progress.json'].write_text(json.dumps(dict(status='complete',physical_time=manifest['total_ticks'],periods=steps),indent=2)+'\n')
    return manifest


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path);parser.add_argument('--steps',type=int,default=2)
    args=parser.parse_args();execute(args.output,args.steps)
