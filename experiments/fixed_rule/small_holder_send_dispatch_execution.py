"""Uninterrupted physical SEND, packet flight, dispatch and next FETCH.

Diagnostic expected states use packet coordinates; only the fixed GPU rule
advances the world. No emitted packet or intermediate controller is replaced.
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
from gacsca.fixed_rule import small_holder_rule as f, small_holder_core as c, small_holder_program as p
from gacsca.fixed_rule import small_holder_projected as r, small_holder_quotient as q, small_holder_supported_events as gpu
from experiments.fixed_rule import small_holder_instruction_path_execution as instruction
from experiments.fixed_rule.small_holder_meta_path_execution import expected_raw
from experiments.fixed_rule.small_holder_temporal_repair import no_host
from experiments.fixed_rule.small_holder_gather_two_periods import memory


def selected_pcs(pilot=False):
    pcs=tuple(pc for pc in instruction.selected_pcs() if p.layout().instructions[pc].kind==c.SEND)
    if pilot:
        pcs=tuple(next(pc for pc in pcs if p.layout().instructions[pc].d==tag) for tag in (0,1,14,15))
    return pcs


def frames(pc, age):
    g=p.layout();op=g.instructions[pc];assert op.kind==c.SEND
    trace=instruction.frames(pc,age);birth=trace[-1];n=len(birth['data'])
    target=g.memory_count+pc+1;gap=target-birth['head'];assert gap>=0
    hops,direction=op.d>>1,op.d&1;sign=-1 if direction else 1;channel='lp' if direction else 'rp'
    distance=hops*f.Q+(op.a-op.b if direction else op.b-op.a);assert distance>0
    first_edge=op.a+1 if direction else f.Q-op.a
    points={gap,gap+1}
    for tick in (distance,first_edge):
        points.update(x for x in (tick-1,tick,tick+1) if 0<x<=gap)
    for dt in sorted(points):
        if dt==0:continue
        frame=copy.deepcopy(birth);frame.update(time=birth['time']+dt,head=birth['head']+dt)
        frame['packets']=[{} for _ in range(n)]
        for source in range(n):
            payload=birth['packets'][source][op.a][channel+'_data']
            if dt>=distance:
                dest=(source+sign*hops)%n;frame['data'][dest][op.b]=payload
            else:
                position=(source*f.Q+op.a+sign*dt)%(n*f.Q);dest,address=divmod(position,f.Q)
                crossed=((f.Q-1-op.a if direction else op.a)+dt)//f.Q
                remaining=hops-crossed;assert 0<=remaining<=7
                frame['packets'][dest][address]={channel+'_target':op.b,channel+'_data':payload,
                                               channel+'_remaining':remaining,channel+'_valid':1}
        if dt==gap+1:
            halted=False
            for col,ctrl in enumerate(frame['controls']):
                cell=c.Cell(**r.record(target),address=target,age=age+frame['time']-1,head=1,**ctrl)
                if c.halted(cell):frame['controls'][col]={name:0 for name in c.CONTROL};halted=True
                else:frame['controls'][col]=dict(c.advance(cell),direction=c.RIGHT)
            frame['head']=None if halted else target+1
        trace.append(frame)
    return trace,dict(birth_tick=birth['time'],dispatch_ticks=gap,packet_distance=distance,
                      first_edge=first_edge,target_pc=pc+1,target_address=target,direction=direction,hops=hops)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--pilot',action='store_true');parser.add_argument('--output',required=True)
    args=parser.parse_args();stem=Path(args.output)
    for ext in ('.json','.npz','.progress.json'):
        if stem.with_suffix(ext).exists():raise FileExistsError('preserve evidence')
    started=time.perf_counter();pcs=selected_pcs(args.pilot);saved=[];indices=[];cases=[];digest=hashlib.sha256()
    records=0;gpu_seconds=0.;evaluations=0;allocated=0;observed=[]
    for pc in pcs:
        for age in (1,c.VOTE_AGES[0]+1):
            trace,description=frames(pc,age);initial=trace[0];n=len(initial['data']);logical={};op=p.layout().instructions[pc]
            for col,data in enumerate(initial['data']):
                for address,value in data.items():logical[col*f.Q+address]=q.Cell(address=address,age=age,data=value)
                head=initial['head'];logical[col*f.Q+head]=q.Cell(address=head,age=age,head=1,**initial['controls'][col])
            begin=records
            with gpu.World((r.Cell(),)*n,age=age,logical=logical) as world:
                if not observed:observed.append(memory())
                allocated=max(allocated,world.device_bytes);elapsed=0
                for frame in trace:
                    delta=frame['time']-elapsed
                    if delta:
                        start=time.perf_counter()
                        with no_host(),patch.object(c,'advance',side_effect=AssertionError('host primary transition')):
                            # The independent/gather batch guards exclude some live packets.
                            # Existing device-guarded transport plus literal F handles them.
                            metrics=world.run(delta) if elapsed>=description['birth_tick'] else world.step() if delta==1 else world.batch(delta)
                        gpu_seconds+=time.perf_counter()-start;evaluations+=metrics.get('logical_evaluations',0)
                    elapsed=frame['time'];model=instruction.logical_model(pc,age,frame)
                    head=description['target_address'] if frame['head'] is None else frame['head']
                    addresses={0,f.Q-1,op.a,op.b,head,(head-2)%f.Q,(head+2)%f.Q,description['target_address']}
                    for packets in frame['packets']:
                        for address in packets:addresses.update(((address-1)%f.Q,address,(address+1)%f.Q))
                    positions=tuple(col*f.Q+a for col in range(n) for a in sorted(addresses))
                    actual=world.logical_cells(positions)
                    assert actual==tuple(model(pos) for pos in positions),(pc,age,elapsed,'logical')
                    saved.append(q.array_from_cells(actual));indices.extend((pc,age,elapsed,pos//f.Q,pos%f.Q) for pos in positions);records+=len(positions)
                    for pos,cell in zip(positions,world.physical_cells(positions)):
                        values=f.encode_cell(cell);assert values==expected_raw(model,pos),(pc,age,elapsed,pos,'full raw')
                        digest.update(np.array(values,dtype=np.uint64).tobytes())
            cases.append(dict(pc=pc,age=age,**description,checkpoint_times=[x['time'] for x in trace],records_start=begin,records_count=records-begin))
            stem.with_suffix('.progress.json').write_text(json.dumps(dict(status='running',cases=len(cases),full_raw_checks=records))+'\n')
    np.savez_compressed(stem.with_suffix('.npz'),records=np.concatenate(saved),indices=np.array(indices,dtype=np.uint64))
    paths=[Path(__file__),Path(instruction.__file__),Path(gpu.__file__),Path('gacsca/fixed_rule/small_holder_register_events.py'),
           Path('experiments/fixed_rule/small_holder_meta_path_execution.py'),Path('experiments/fixed_rule/small_holder_temporal_repair.py')]
    result=dict(passed=True,pilot=args.pilot,cases=cases,SEND_sites=len(pcs),physical_SEND_successors=len(cases)*6,
                packet_tags=sorted({p.layout().instructions[pc].d for pc in pcs}),
                complete_logical_records_saved=records,complete_raw_probe_records_checked=records,raw_probe_sha256=digest.hexdigest(),
                gpu_seconds=gpu_seconds,logical_evaluations=evaluations,seconds=time.perf_counter()-started,
                host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,observed_process_gpu_mib=observed,explicit_device_bytes=allocated,
                descriptor_sha256=f.self_description().digest(),binary_sha256=hashlib.sha256(Path(gpu.library()._name).read_bytes()).hexdigest(),
                source_sha256={str(path):hashlib.sha256(path.read_bytes()).hexdigest() for path in paths},artifact_sha256=hashlib.sha256(stem.with_suffix('.npz').read_bytes()).hexdigest(),
                limitation='Actual selected SEND-to-next-FETCH trajectories with real retained packets and selected full-state checkpoints. Long-hop packets may remain in flight at final checkpoint. No arbitrary packet trains, full period or nested/noisy execution.')
    stem.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n');stem.with_suffix('.progress.json').write_text(json.dumps(dict(status='complete',successors=result['physical_SEND_successors']))+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='cases'},indent=2),flush=True)


if __name__=='__main__':main()
