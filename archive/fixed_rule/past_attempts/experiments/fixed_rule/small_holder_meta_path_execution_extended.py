"""Physical intermediate META checkpoints at actual fixed-ROM instructions.

Only initial fields supply queries. GPU evolves the unchanged physical rule;
expected controllers and decoding are diagnostics, guarded from evolution.
"""
import argparse
from functools import lru_cache
import hashlib
import json
import resource
import time
from pathlib import Path

import numpy as np
from gacsca.fixed_rule import small_holder_supported_events as gpu
from gacsca.fixed_rule import small_holder_rule as f, small_holder_projected as r
from gacsca.fixed_rule import small_holder_core as c, small_holder_program as p, small_holder_quotient as q
from experiments.fixed_rule.small_holder_temporal_repair import no_host
from experiments.fixed_rule.small_holder_gather_two_periods import memory

POISON=0xDEAD123498765432


def frame_times(m,d,L):
    ready=2*L-m;returned=4*L-m;duration=returned+d+1
    return (ready-1,ready,returned-1,returned,duration-1,duration)


def expected_logical(pc,queries,start_age,frame):
    g=p.layout();op=g.instructions[pc];m=g.memory_count+pc;d=op.a;s=op.b;L=len(p.base_rom())
    elapsed=frame_times(m,d,L)[frame];age=start_age+elapsed
    parentwords=f.encode_cell(r.lift(r.Cell()));info=dict(zip(g.info,parentwords));n=len(queries)
    head_address=0 if frame<4 else d if frame==4 else d+1
    @lru_cache(None)
    def cell(position):
        col,address=divmod(position%(n*f.Q),f.Q);query=queries[col]
        value=r.record(query)[c.STATIC[s]]
        data=value if address==d and frame==5 else POISON if address==d else info.get(address,0)
        control={}
        if address==head_address:
            phase=c.READ_META if frame<2 else c.WAIT_META if frame==2 and query<L else c.READ_META if frame==2 else c.WRITE if frame<5 else c.FETCH
            direction=c.LEFT if frame in (0,2) else c.RIGHT
            rd=query if frame<2 or (frame==2 and query>=L) else d
            held=0 if frame==0 else 1 if frame==1 or (frame==2 and query>=L) else value
            control=dict(head=1,pc=pc+int(frame==5),phase=phase,ra=d,rb=s,rd=rd,value=held,alu=3,direction=direction)
        return q.Cell(address=address,age=age,data=data,**control)
    return cell,head_address


def expected_raw(cell,position):
    values={name:0 for name,_ in f.SCHEMA};own=cell(position)
    values.update(address=own.address,age=own.age)
    for delta in f.STATIC_OFFSETS:
        record=r.record((own.address+delta)%f.Q)
        for name in c.STATIC:values[f'p{delta+3}_{name}']=record[name]
    for delta in f.OFFSETS:
        row=cell(position+delta)
        for name,_ in f.PROCEDURE:values[f's{delta+2}_{name}']=getattr(row,name)
    return tuple(values[name] for name,_ in f.SCHEMA)


def initial_world(parents, *, age, logical):
    """Use the existing validated complete-state restore for late initial Ages."""
    if age < c.WF_START-1:
        return gpu.World(parents, age=age, logical=logical)
    g=p.layout();addresses=np.array([*range(g.computation_cells),*range(f.Q-5,f.Q)],dtype=np.uint64)
    states=np.zeros((len(parents),len(addresses),len(q.SCHEMA)),dtype=np.uint64)
    states[:,:,q.COL['address']]=addresses;states[:,:,q.COL['age']]=age
    for col,parent in enumerate(parents):
        states[col,np.array(g.info),q.COL['data']]=f.encode_cell(r.lift(parent))
    for position,cell in logical.items():
        col,address=divmod(position,f.Q)
        row=address if address<g.computation_cells else g.computation_cells+address-(f.Q-5)
        if not 0<=row<len(addresses) or int(addresses[row])!=address:
            raise ValueError('only stored core/tail overrides are supported')
        states[col,row]=q.encode_cell(cell)
    return gpu.World.from_stored(states.reshape(-1,len(q.SCHEMA)))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--pilot',action='store_true');parser.add_argument('--late-pilot',action='store_true');parser.add_argument('--output',required=True);args=parser.parse_args();stem=Path(args.output)
    for ext in ('.json','.npz','.progress.json'):
        if stem.with_suffix(ext).exists():raise FileExistsError('preserve evidence')
    started=time.perf_counter();g=p.layout();L=len(p.base_rom())
    pcs=tuple(i for i,op in enumerate(g.instructions) if op.kind==c.META)
    if args.pilot or args.late_pilot:pcs=(pcs[0],pcs[-1])
    queries=tuple(sorted({0,1,7,8,g.memory_count-1,g.memory_count,L-2,L-1,L,L+1,f.Q-6,f.Q-5,f.Q-1}))
    starts=(c.RESET_AGES[4]+1,) if args.late_pilot else (1,) if args.pilot else (1,c.VOTE_AGES[0]+1,c.RESET_AGES[4]+1)
    heads=np.empty((len(pcs),len(starts),6,len(queries),len(q.SCHEMA)),dtype=np.uint64)
    times=np.array([frame_times(g.memory_count+pc,g.instructions[pc].a,L) for pc in pcs],dtype=np.uint64)
    raw_hash=hashlib.sha256();raw_checked=0;completions=0;gpu_seconds=0.;evaluations=0;observed=[];allocated=0
    for i,pc in enumerate(pcs):
        op=g.instructions[pc];where=g.memory_count+pc;target=op.a
        for j,start_age in enumerate(starts):
            logical={}
            for col,query in enumerate(queries):
                logical[col*f.Q+where]=q.Cell(address=where,age=start_age,head=1,pc=pc,phase=c.FETCH,ra=999,rb=777,rd=query,value=POISON,alu=3)
                logical[col*f.Q+target]=q.Cell(address=target,age=start_age,data=POISON)
            with initial_world((r.Cell(),)*len(queries),age=start_age,logical=logical) as world:
                if not observed:observed.append(memory())
                allocated=max(allocated,world.device_bytes)
                previous=0
                for frame,elapsed in enumerate(times[i]):
                    elapsed=int(elapsed);tick=time.perf_counter()
                    with no_host():metrics=world.batch(elapsed-previous)
                    gpu_seconds+=time.perf_counter()-tick;evaluations+=metrics['logical_evaluations'];previous=elapsed
                    expected,head=expected_logical(pc,queries,start_age,frame)
                    head_positions=tuple(col*f.Q+head for col in range(len(queries)))
                    actual=world.logical_cells(head_positions)
                    assert actual==tuple(expected(pos) for pos in head_positions),(pc,start_age,frame,'head')
                    heads[i,j,frame]=q.array_from_cells(actual)
                    probe=tuple((col*f.Q+address)%(len(queries)*f.Q) for col in range(len(queries)) for address in (head-2,head,head+2,where,target))
                    actual=world.physical_cells(probe)
                    for position,cell in zip(probe,actual):
                        values=f.encode_cell(cell)
                        assert values==expected_raw(expected,position),(pc,start_age,frame,position,'full raw')
                        raw_hash.update(np.array(values,dtype=np.uint64).tobytes());raw_checked+=1
                completions+=len(queries)
            stem.with_suffix('.progress.json').write_text(json.dumps(dict(status='running',instructions_completed=i+1,completions=completions,gpu_seconds=gpu_seconds))+'\n')
        if i%14==0:print(json.dumps(dict(instructions_completed=i+1,completions=completions,gpu_seconds=gpu_seconds)),flush=True)
    np.savez_compressed(stem.with_suffix('.npz'),pcs=np.array(pcs,dtype=np.uint64),queries=np.array(queries,dtype=np.uint64),start_ages=np.array(starts,dtype=np.uint64),frame_times=times,heads=heads)
    paths=[Path(__file__),Path(gpu.__file__),Path('gacsca/fixed_rule/small_holder_register_events.py'),Path('experiments/fixed_rule/small_holder_temporal_repair.py')]
    result=dict(passed=True,pilot=args.pilot or args.late_pilot,actual_META_instruction_sites=len(pcs),query_addresses=len(queries),initial_ages=starts,actual_META_completions=completions,
                checkpoints_per_completion=6,complete_raw_probe_records_checked=raw_checked,raw_probe_sha256=raw_hash.hexdigest(),
                gpu_seconds=gpu_seconds,logical_evaluations=evaluations,seconds=time.perf_counter()-started,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                observed_process_gpu_mib=observed,explicit_device_bytes=allocated,descriptor_sha256=f.self_description().digest(),binary_sha256=hashlib.sha256(Path(gpu.library()._name).read_bytes()).hexdigest(),
                source_sha256={str(path):hashlib.sha256(path.read_bytes()).hexdigest() for path in paths},artifact_sha256=hashlib.sha256(stem.with_suffix('.npz').read_bytes()).hexdigest(),
                limitation='Actual isolated clean META trajectories with six intermediate checkpoints and selected full raw physical probes; not all query values, a full-colony scan at every checkpoint, a work period, or noisy/nested execution.')
    stem.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n');stem.with_suffix('.progress.json').write_text(json.dumps(dict(status='complete',completions=completions))+'\n');print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':main()
