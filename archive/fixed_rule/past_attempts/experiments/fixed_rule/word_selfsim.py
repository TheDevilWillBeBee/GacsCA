"""Successive full word-rule macrosteps with active computation and address repair."""
import argparse
from dataclasses import replace
import hashlib
import io
import json
from pathlib import Path
import tarfile
import time
import numpy as np
from gacsca.fixed_rule import word_projected as r,word_rule as f,word_program as b,word_initial
from gacsca.fixed_rule.word_world import World


def initial_ring():
    cells=[r.Cell(address=100+i,age=f.U-1) for i in range(23)]
    cells[11]=replace(cells[11],address=143,age=123,data=(1<<64)-1,f2=1,
                      head=1,phase=f.READ_B,rb=143,rd=112,value=(1<<64)-1,alu=f.NAND)
    cells[12]=replace(cells[12],data=0xFEDCBA9876543210)
    return tuple(cells)


def lifted_words(cores):
    g=b.layout()
    return np.stack([cores[base+g.info_start:base+g.info_start+f.FIELDS,r.COL['data']]
                     for base in range(0,len(cores),g.computation_cells)])


def execute(stem,steps=2,chunk_ticks=1000000):
    stem=Path(stem);stem.parent.mkdir(parents=True,exist_ok=True)
    files=[stem.with_suffix(x) for x in ('.json','.npz','.tar.gz','.progress.json')]
    if any(p.exists() for p in files):raise FileExistsError('preserve existing evidence')
    if steps<2 or chunk_ticks<1:raise ValueError('at least two macrosteps and positive chunk size')
    root=Path(__file__).resolve().parents[2]
    sources=sorted([*root.glob('gacsca/fixed_rule/*.py'),*root.glob('gacsca/fixed_rule/*.c'),
                    *root.glob('tests/fixed_rule/*.py'),*root.glob('experiments/fixed_rule/*.py')])
    contents={str(p.relative_to(root)):p.read_bytes() for p in sources}
    hashes={name:hashlib.sha256(data).hexdigest() for name,data in contents.items()}
    with tarfile.open(files[2],'x:gz') as archive:
        for name,data in contents.items():
            entry=tarfile.TarInfo(name);entry.size=len(data);archive.addfile(entry,io.BytesIO(data))
    g=b.layout();reference=initial_ring();frames=[];expanded=[];periods=[]
    with World.encode(reference) as world:
        frames.append(r.array_from_cells(reference));expanded.append(lifted_words(world.cores))
        binary_sha=hashlib.sha256(Path(world.lib._name).read_bytes()).hexdigest()
        for period in range(1,steps+1):
            started=time.monotonic();metrics=dict(physical_ticks=0,literal_core_ticks=0,wait_ticks_skipped=0,local_evaluations=0)
            while world.time<period*g.period_ticks:
                chunk=world.run(min(chunk_ticks,period*g.period_ticks-world.time))
                for key,value in chunk.items():metrics[key]+=value
                progress=dict(status='running',period=period,physical_time=world.time,
                              period_elapsed_seconds=time.monotonic()-started,pending_packets=world.pending,**metrics)
                files[3].write_text(json.dumps(progress,indent=2)+'\n');print(json.dumps(progress),flush=True)
            reference=r.step_ring(reference) # diagnostic only, never installed
            actual=world.decode();words=r.array_from_cells(actual);expected=r.array_from_cells(reference)
            lift=lifted_words(world.cores);expected_lift=np.array([f.encode_cell(r.lift(c)) for c in reference],dtype=np.uint64)
            row=dict(period=period,elapsed_seconds=time.monotonic()-started,**metrics,
                     projected_mismatches=int(np.count_nonzero(words!=expected)),
                     lifted_mismatches=int(np.count_nonzero(lift!=expected_lift)),
                     boundary=world.check_boundary(),pending_packets=world.pending,
                     center=dict(address=actual[11].address,age=actual[11].age,f2=actual[11].f2),target_data=actual[12].data)
            print(json.dumps(dict(status='macrostep',**row)),flush=True)
            if row['projected_mismatches'] or row['lifted_mismatches'] or not row['boundary']:raise AssertionError(row)
            assert metrics['physical_ticks']==metrics['literal_core_ticks']+metrics['wait_ticks_skipped']==g.period_ticks
            periods.append(row);frames.append(words);expanded.append(lift)
        with files[1].open('xb') as stream:
            np.savez_compressed(stream,frames=np.stack(frames),lifted_frames=np.stack(expanded),
                                core_final=world.cores,rom=r.rom(),padding_packet_count=np.array(world.pending))
    manifest=dict(scope='complete word controller plus printed maintenance, continuous unclocked evaluator; missing Gray stage schedule, redundancy and noise repair',
                  physical_rule=r.identity(),description_operations=len(f.self_description().operations),
                  colony_cells=g.colony_cells,computation_cells=g.computation_cells,
                  represented_cells=len(reference),physical_cells=len(reference)*g.colony_cells,
                  explicit_core_cells=len(reference)*g.computation_cells,core_array_bytes=int(frames[0].shape[0]*g.computation_cells*len(r.SCHEMA)*8),
                  period_ticks=g.period_ticks,timing=g.timing_certificate(),
                  compact_representation='healthy physical Address/flags; lazy uniform actual Age; canonical padding with packet trajectories; complete damaged upper state is data',
                  periods=periods,total_ticks=sum(p['physical_ticks'] for p in periods),
                  total_seconds=sum(p['elapsed_seconds'] for p in periods),
                  source_sha256=hashes,compiled_binary_sha256=binary_sha,
                  artifact_sha256=hashlib.sha256(files[1].read_bytes()).hexdigest(),
                  source_archive_sha256=hashlib.sha256(files[2].read_bytes()).hexdigest(),
                  initialization_only_resources=[word_initial.resources(1,d) for d in (1,2,3)])
    with files[0].open('x') as stream:json.dump(manifest,stream,indent=2);stream.write('\n')
    files[3].write_text(json.dumps(dict(status='complete',physical_time=manifest['total_ticks'],completed_periods=steps),indent=2)+'\n')
    return manifest


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path);parser.add_argument('--steps',default=2,type=int)
    parser.add_argument('--chunk-ticks',default=1000000,type=int);args=parser.parse_args()
    execute(args.output,args.steps,args.chunk_ticks)
