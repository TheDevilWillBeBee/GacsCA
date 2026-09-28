"""Physical checkpoints for representative ordinary fixed-ROM instructions.

Expected states are diagnostic scalar primary-controller calculations. They are
never installed after initialization; host transition calls are forbidden during
GPU advance. SEND stops immediately after its literal packet-birth transition.
"""
import argparse
from functools import lru_cache
import hashlib
import json
import random
import resource
import time
from pathlib import Path
from unittest.mock import patch

import numpy as np
from gacsca.fixed_rule import small_holder_supported_events as gpu
from gacsca.fixed_rule import small_holder_rule as f, small_holder_core as c, small_holder_program as p, small_holder_projected as r, small_holder_quotient as q
from gacsca.fixed_rule.wordcode import LIT,MASK
from experiments.fixed_rule.small_holder_temporal_repair import no_host
from experiments.fixed_rule.small_holder_gather_two_periods import memory
from experiments.fixed_rule.small_holder_meta_path_execution import expected_raw

POISON=0xDEAD123498765432


def selected_pcs():
    groups={}
    for pc,op in enumerate(p.layout().instructions):
        if op.kind==c.META:continue
        key=(op.kind,op.d if op.kind==c.SEND else (op.a==op.b,op.a==op.d,op.b==op.d,op.a<=op.b,op.b<=op.d) if op.kind in c.ALU_KINDS else None)
        groups.setdefault(key,[]).append(pc)
    return tuple(sorted({pc for rows in groups.values() for pc in (rows[0],rows[-1])}))


def input_data(pc):
    op=p.layout().instructions[pc];rng=random.Random(2026092701+pc)
    patterns=((0,0),(MASK,MASK),(MASK,1),(0x123456789ABCDE,63),(MASK,64),(rng.getrandbits(64),rng.getrandbits(64)))
    rows=[]
    for a,b in patterns:
        data={}
        if op.kind in c.ALU_KINDS:data[op.a]=a;data.setdefault(op.b,b)
        elif op.kind in (c.SEND,c.LOAD):data[op.a]=a
        if op.kind in c.ALU_KINDS or op.kind==LIT:data.setdefault(op.d,POISON)
        rows.append(data)
    return tuple(rows)


def frames(pc,start_age):
    """Independent scalar event contract and cyclic timing, not an executor."""
    g=p.layout();op=g.instructions[pc];m=g.memory_count+pc;L=len(p.base_rom())
    data=[dict(row) for row in input_data(pc)];packets=[{} for _ in data]
    controls=[dict(phase=c.FETCH,pc=pc,ra=777,rb=888,rd=999,value=POISON,alu=3,direction=c.RIGHT) for _ in data]
    info=dict(zip(g.info,f.encode_cell(r.lift(r.Cell()))));output=[];elapsed=0;coordinate=m
    targets=[m]
    if op.kind in c.ALU_KINDS:targets.extend((op.a,op.b,op.d))
    elif op.kind==LIT:targets.append(op.d)
    elif op.kind in (c.SEND,c.LOAD):targets.append(op.a)
    def capture(at,head):
        snap=dict(time=at,head=head,controls=[dict(x) for x in controls],data=[dict(x) for x in data],packets=[{a:dict(v) for a,v in x.items()} for x in packets])
        if output and output[-1]['time']==at:assert output[-1]==snap
        else:output.append(snap)
    for target in targets:
        elapsed+=(target-coordinate)%(2*L);capture(elapsed,target)
        stopped=False
        for col,ctrl in enumerate(controls):
            word=data[col].get(target,info.get(target,0));cell=c.Cell(**r.record(target),address=target,age=start_age+elapsed,data=word,head=1,**ctrl)
            if c.halted(cell):controls[col]={name:0 for name in c.CONTROL};stopped=True;continue
            advanced=c.advance(cell);controls[col]=dict(advanced,direction=c.RIGHT)
            if cell.phase==c.WRITE and cell.kind==c.MEM and cell.index==cell.rd:data[col][target]=cell.value
            if cell.phase==c.TRANSMIT and cell.kind==c.MEM and cell.index==cell.ra:
                track='lp' if cell.rd&1 else 'rp'
                packets[col][target]={track+'_target':cell.rb&0xFFFFFFFF,track+'_data':word,track+'_remaining':(cell.rd>>1)&7,track+'_valid':1}
        elapsed+=1;coordinate=target+1;capture(elapsed,None if stopped else coordinate)
        if stopped:break
    return output


def logical_model(pc,start_age,frame):
    g=p.layout();info=dict(zip(g.info,f.encode_cell(r.lift(r.Cell()))));n=len(frame['data'])
    @lru_cache(None)
    def cell(position):
        col,address=divmod(position%(n*f.Q),f.Q)
        fields=dict(frame['packets'][col].get(address,{}))
        if address==frame['head']:fields.update(head=1,**frame['controls'][col])
        return q.Cell(address=address,age=start_age+frame['time'],data=frame['data'][col].get(address,info.get(address,0)),**fields)
    return cell


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--pilot',action='store_true');parser.add_argument('--output',required=True);args=parser.parse_args();stem=Path(args.output)
    for ext in ('.json','.npz','.progress.json'):
        if stem.with_suffix(ext).exists():raise FileExistsError('preserve evidence')
    start=time.perf_counter();pcs=selected_pcs()
    if args.pilot:
        pcs=tuple(next(pc for pc in pcs if p.layout().instructions[pc].kind==kind) for kind in (*c.ALU_KINDS,LIT,c.LOAD,c.SEND,c.HALT,c.IF_THIRD))
    starts=(1,c.VOTE_AGES[0]+1);records=[];indices=[];cases=[];offset=0;raw_hash=hashlib.sha256();raw_checks=0;gpu_seconds=0.;evaluations=0;observed=[];allocated=0;g=p.layout()
    for pc in pcs:
        where=g.memory_count+pc;op=g.instructions[pc]
        for age in starts:
            trace=frames(pc,age);rows=input_data(pc);n=len(rows);logical={}
            for col,data in enumerate(rows):
                for address,value in data.items():logical[col*f.Q+address]=q.Cell(address=address,age=age,data=value)
                logical[col*f.Q+where]=q.Cell(address=where,age=age,head=1,**trace[0]['controls'][col])
            begin=offset
            with gpu.World((r.Cell(),)*n,age=age,logical=logical) as world:
                if not observed:observed.append(memory())
                allocated=max(allocated,world.device_bytes);previous=0
                for frame in trace:
                    delta=frame['time']-previous
                    if delta:
                        tick=time.perf_counter()
                        with no_host(),patch.object(c,'advance',side_effect=AssertionError('host primary transition')):
                            metrics=world.step() if delta==1 else world.batch(delta)
                        gpu_seconds+=time.perf_counter()-tick;evaluations+=metrics.get('logical_evaluations',0)
                    previous=frame['time'];expected=logical_model(pc,age,frame)
                    head=where if frame['head'] is None else frame['head']
                    addresses=tuple(sorted({(head-2)%f.Q,head,(head+2)%f.Q,where,*rows[0]}))
                    positions=tuple(col*f.Q+a for col in range(n) for a in addresses)
                    actual=world.logical_cells(positions)
                    assert actual==tuple(expected(pos) for pos in positions),(pc,age,frame['time'],'logical')
                    records.append(q.array_from_cells(actual));indices.extend((pc,age,frame['time'],pos//f.Q,pos%f.Q) for pos in positions);offset+=len(positions)
                    for pos,cell in zip(positions,world.physical_cells(positions)):
                        values=f.encode_cell(cell)
                        assert values==expected_raw(expected,pos),(pc,age,frame['time'],pos,'full raw')
                        raw_hash.update(np.array(values,dtype=np.uint64).tobytes());raw_checks+=1
            cases.append(dict(pc=pc,kind=op.kind,start_age=age,duration=trace[-1]['time'],records_start=begin,records_count=offset-begin,checkpoint_times=[x['time'] for x in trace]))
        stem.with_suffix('.progress.json').write_text(json.dumps(dict(status='running',sites_completed=len(cases)//len(starts),full_raw_checks=raw_checks,gpu_seconds=gpu_seconds))+'\n')
        if len(cases)%28==0:print(json.dumps(dict(cases=len(cases),gpu_seconds=gpu_seconds)),flush=True)
    np.savez_compressed(stem.with_suffix('.npz'),records=np.concatenate(records),indices=np.array(indices,dtype=np.uint64),pcs=np.array(pcs,dtype=np.uint64))
    paths=[Path(__file__),Path(gpu.__file__),Path('gacsca/fixed_rule/small_holder_register_events.py'),Path('experiments/fixed_rule/small_holder_meta_path_execution.py'),Path('experiments/fixed_rule/small_holder_temporal_repair.py')]
    result=dict(passed=True,pilot=args.pilot,instruction_sites=len(pcs),cases=cases,data_patterns=6,actual_instruction_completions=len(cases)*6,complete_logical_records_saved=offset,complete_raw_probe_records_checked=raw_checks,raw_probe_sha256=raw_hash.hexdigest(),
                gpu_seconds=gpu_seconds,logical_evaluations=evaluations,seconds=time.perf_counter()-start,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,observed_process_gpu_mib=observed,explicit_device_bytes=allocated,
                descriptor_sha256=f.self_description().digest(),binary_sha256=hashlib.sha256(Path(gpu.library()._name).read_bytes()).hexdigest(),source_sha256={str(path):hashlib.sha256(path.read_bytes()).hexdigest() for path in paths},artifact_sha256=hashlib.sha256(stem.with_suffix('.npz').read_bytes()).hexdigest(),
                limitation='Representative isolated ordinary instructions, read/write/FETCH checkpoints and SEND birth. No packet continuation, all-site concrete enumeration, whole-colony scan at each checkpoint, whole period or nested/noisy execution.')
    stem.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n');stem.with_suffix('.progress.json').write_text(json.dumps(dict(status='complete',completions=result['actual_instruction_completions']))+'\n');print(json.dumps({k:v for k,v in result.items() if k!='cases'},indent=2),flush=True)


if __name__=='__main__':main()
