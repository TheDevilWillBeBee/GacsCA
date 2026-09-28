"""Physical FETCH dispatch, including uninterrupted ordinary-instruction successors.

SEND predecessors are deliberately excluded: their real mail requires the next
composition obligation. Initialized reset/vote entries are labeled separately.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import resource
import time
from unittest.mock import patch

import numpy as np
from gacsca.fixed_rule import small_holder_rule as f,small_holder_core as c,small_holder_program as p,small_holder_projected as r,small_holder_quotient as q
from gacsca.fixed_rule import small_holder_supported_events as gpu
from experiments.fixed_rule import small_holder_instruction_path_execution as instruction
from experiments.fixed_rule.small_holder_meta_path_execution_extended import initial_world
from experiments.fixed_rule.small_holder_meta_path_execution import expected_raw
from experiments.fixed_rule.small_holder_temporal_repair import no_host
from experiments.fixed_rule.small_holder_gather_two_periods import memory


def tasks(pilot=False):
    g=p.layout();result=[]
    for stage,pc in enumerate(g.entries):result.append(dict(origin='reset_entry',pc=pc,age=c.RESET_AGES[stage]+1,stage=stage))
    result.append(dict(origin='vote_entry',pc=g.entries[4],age=c.VOTE_AGES[0]+1,stage=0))
    pcs=[pc for pc in instruction.selected_pcs() if g.instructions[pc].kind not in (c.SEND,c.HALT)]
    if pilot:pcs=pcs[:2]
    for pc in pcs:
        for age in (1,c.VOTE_AGES[0]+1):
            if g.instructions[pc].kind==c.IF_THIRD and age==1:continue
            result.append(dict(origin='successor',pc=pc,age=age))
    return tuple(result)


def trajectory(task):
    g=p.layout();pc=task['pc'];age=task['age']
    if task['origin']=='successor':
        trace=instruction.frames(pc,age);initial=trace[0];start=copy.deepcopy(trace[-1]);target_pc=pc+1
        assert start['head'] is not None and all(not x for x in start['packets'])
    else:
        target_pc=pc;controls=[]
        for value in (0,1,0xFFFFFFFFFFFFFFFF,63,64,0x123456789ABCDE):
            ctrl={name:value&((1<<dict(c.SCHEMA)[name])-1) for name in c.CONTROL}
            ctrl.update(phase=c.FETCH,pc=pc,direction=c.RIGHT);controls.append(ctrl)
        initial=dict(time=0,head=0,controls=controls,data=[{} for _ in controls],packets=[{} for _ in controls]);start=copy.deepcopy(initial)
    target=g.memory_count+target_pc;duration=target-start['head'];assert duration>=0
    arrival=copy.deepcopy(start);arrival.update(time=start['time']+duration,head=target)
    after=copy.deepcopy(arrival);after['time']+=1;stopped=False
    info=dict(zip(g.info,f.encode_cell(r.lift(r.Cell()))))
    for col,ctrl in enumerate(arrival['controls']):
        cell=c.Cell(**r.record(target),address=target,age=age+arrival['time'],head=1,data=arrival['data'][col].get(target,info.get(target,0)),**ctrl)
        if c.halted(cell):after['controls'][col]={name:0 for name in c.CONTROL};stopped=True
        else:after['controls'][col]=dict(c.advance(cell),direction=c.RIGHT)
    after['head']=None if stopped else target+1
    return initial,(start,arrival,after),dict(target_pc=target_pc,start_address=start['head'],target_address=target,dispatch_ticks=duration,body_ticks=start['time'])


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--pilot',action='store_true');parser.add_argument('--output',required=True);args=parser.parse_args();stem=Path(args.output)
    for ext in ('.json','.npz','.progress.json'):
        if stem.with_suffix(ext).exists():raise FileExistsError('preserve evidence')
    started=time.perf_counter();records=[];indices=[];rows=[];offset=0;raw_hash=hashlib.sha256();gpu_seconds=0.;evaluations=0;observed=[];allocated=0;g=p.layout()
    for number,task in enumerate(tasks(args.pilot)):
        initial,frames,description=trajectory(task);pc=task['pc'];age=task['age'];n=len(initial['controls']);logical={}
        for col,data in enumerate(initial['data']):
            for address,value in data.items():logical[col*f.Q+address]=q.Cell(address=address,age=age,data=value)
            head=initial['head'];logical[col*f.Q+head]=q.Cell(address=head,age=age,data=data.get(head,0),head=1,**initial['controls'][col])
        begin=offset
        with initial_world((r.Cell(),)*n,age=age,logical=logical) as world:
            if not observed:observed.append(memory())
            allocated=max(allocated,world.device_bytes);elapsed=0
            for stage,frame in enumerate(frames):
                delta=frame['time']-elapsed
                if delta:
                    tick=time.perf_counter()
                    with no_host(),patch.object(c,'advance',side_effect=AssertionError('host primary transition')):
                        if stage==0 and delta>1:
                            metrics=world.batch(delta-1);evaluations+=metrics['logical_evaluations'];metrics=world.step()
                        else:metrics=world.step() if delta==1 else world.batch(delta)
                    gpu_seconds+=time.perf_counter()-tick;evaluations+=metrics.get('logical_evaluations',0)
                elapsed=frame['time'];model=instruction.logical_model(pc,age,frame)
                head=description['target_address'] if frame['head'] is None else frame['head']
                addresses=tuple(sorted({(head-2)%f.Q,head,(head+2)%f.Q,description['start_address'],description['target_address'],initial['head'],*initial['data'][0]}))
                positions=tuple(col*f.Q+a for col in range(n) for a in addresses)
                actual=world.logical_cells(positions);assert actual==tuple(model(pos) for pos in positions),(task,stage,'logical')
                records.append(q.array_from_cells(actual));indices.extend((number,stage,col,a) for col in range(n) for a in addresses);offset+=len(positions)
                for pos,cell in zip(positions,world.physical_cells(positions)):
                    value=f.encode_cell(cell);assert value==expected_raw(model,pos),(task,stage,pos,'full raw')
                    raw_hash.update(np.array(value,dtype=np.uint64).tobytes())
        rows.append(dict(task,**description,records_start=begin,records_count=offset-begin))
        stem.with_suffix('.progress.json').write_text(json.dumps(dict(status='running',tasks_completed=number+1,gpu_seconds=gpu_seconds))+'\n')
    np.savez_compressed(stem.with_suffix('.npz'),records=np.concatenate(records),indices=np.array(indices,dtype=np.uint64))
    paths=[Path(__file__),Path(instruction.__file__),Path('experiments/fixed_rule/small_holder_meta_path_execution_extended.py'),Path('experiments/fixed_rule/small_holder_meta_path_execution.py'),Path(gpu.__file__),Path('gacsca/fixed_rule/small_holder_register_events.py')]
    result=dict(passed=True,pilot=args.pilot,cases=rows,initialized_entry_tasks=sum(x['origin']!='successor' for x in rows),uninterrupted_successor_tasks=sum(x['origin']=='successor' for x in rows),data_patterns=6,
                actual_dispatches=len(rows)*6,complete_logical_records_saved=offset,complete_raw_probe_records_checked=offset,raw_probe_sha256=raw_hash.hexdigest(),gpu_seconds=gpu_seconds,logical_evaluations=evaluations,
                seconds=time.perf_counter()-started,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,observed_process_gpu_mib=observed,explicit_device_bytes=allocated,
                descriptor_sha256=f.self_description().digest(),binary_sha256=hashlib.sha256(Path(gpu.library()._name).read_bytes()).hexdigest(),source_sha256={str(path):hashlib.sha256(path.read_bytes()).hexdigest() for path in paths},artifact_sha256=hashlib.sha256(stem.with_suffix('.npz').read_bytes()).hexdigest(),
                limitation='Initialized entry dispatches and uninterrupted non-SEND instruction-to-next-FETCH trajectories with selected full-state checkpoints. No SEND mail removal, packet continuation, full period or noisy/nested execution.')
    stem.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n');stem.with_suffix('.progress.json').write_text(json.dumps(dict(status='complete',dispatches=result['actual_dispatches']))+'\n');print(json.dumps({k:v for k,v in result.items() if k!='cases'},indent=2),flush=True)


if __name__=='__main__':main()
