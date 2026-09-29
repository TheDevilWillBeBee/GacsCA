"""Bounded final-evaluation CUDA parity, including complete stored physical state.

Initialized histories are fixture data; this is not a whole period or depth-two
execution. Host reference computation finishes before any GPU evolution begins.
"""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import time
from unittest.mock import patch
import numpy as np
from experiments.fixed_rule.run_retimed_holder_cpu_evaluation import fixture
from gacsca.fixed_rule import retimed_holder_cuda_bridge as bridge
from gacsca.fixed_rule import retimed_holder_cpu_events as cpu, retimed_holder_rule as f
from gacsca.fixed_rule import retimed_holder_core as c,retimed_holder_program as p
from gacsca.fixed_rule import retimed_holder_projected as r,retimed_holder_packed as packed
from gacsca.fixed_rule import retimed_holder_quotient as q,retimed_holder_native as native
from gacsca.fixed_rule import retimed_holder_resident_independent as independent
from gacsca.fixed_rule import retimed_holder_resident_period as resident
from gacsca.fixed_rule.wordcode import Program


def compare(world, reference):
    bank,rows,counts=world.snapshot();g=p.layout()
    expected=np.concatenate((reference.data[:,:g.memory_count],reference.data[:,f.Q-5:]),axis=1)
    np.testing.assert_array_equal(bank,expected)
    for col,count in enumerate(counts):
        assert int(count)==int(bool(reference.heads[col,0])),(col,count,reference.heads[col])
        if count:
            record=packed.unpack(rows[col,:1])[0]
            assert int(record[q.COL['address']])==int(reference.where[col])
            np.testing.assert_array_equal(record[[q.COL[n] for n in cpu.CONTROL]],reference.heads[col])
            assert not any(record[q.COL[n]] for n in resident.ACTIVE if n not in cpu.CONTROL)
    assert world.age==reference.age
    return bank,rows,counts


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--colonies',type=int,choices=(1,15),default=1)
    parser.add_argument('--ticks',type=int,default=100000);parser.add_argument('--full',action='store_true');parser.add_argument('--output',required=True)
    args=parser.parse_args();out=Path(args.output);artifact=out.with_suffix('.npz')
    if out.exists() or artifact.exists():raise FileExistsError('preserve evidence')
    started=time.perf_counter();upper,reference=fixture(args.colonies);g=p.layout()
    initial=cpu.World(reference.data,reference.heads,reference.where,age=reference.age)
    stop=c.RESET_AGES[4]+g.schedule(*g.stage_ranges[4])[0]
    ticks=stop-reference.age if args.full else args.ticks
    expected=np.array([f.encode_cell(r.lift(r.project(native.local_step(tuple(r.lift(upper[(col+j)%args.colonies]) for j in f.NEIGHBORHOOD))))) for col in range(args.colonies)],dtype=np.uint64)
    tick=time.perf_counter();cpu_metrics=reference.advance(ticks-1)
    before_last=reference.heads.copy();cpu_last=reference.advance(1);cpu_seconds=time.perf_counter()-tick
    if args.full:
        assert np.all(before_last[:,0]);assert not np.any(reference.heads)
        np.testing.assert_array_equal(reference.data[:,list(g.hold)],expected)
    print(json.dumps(dict(stage='CPU reference complete',seconds=cpu_seconds,ticks=ticks)),flush=True)
    tick=time.perf_counter()
    with bridge.from_cpu(initial,device_budget=32*1024**2) as world:
        compare(world,initial);init_seconds=time.perf_counter()-tick
        # No upper oracle may participate in physical GPU evolution.
        def forbidden(*a,**kw):raise AssertionError('host upper transition during GPU evolution')
        with patch.object(Program,'evaluate',forbidden),patch.object(f,'local_step',forbidden),patch.object(r,'local_step',forbidden):
            tick=time.perf_counter()
            metrics=world.batch(ticks-1,event_budget=1000000,extra_device_budget=32*1024**2)
            _,raw_before,counts_before=world.snapshot()
            for col,count in enumerate(counts_before):
                assert int(count)==int(bool(before_last[col,0]))
                if count:np.testing.assert_array_equal(packed.unpack(raw_before[col,:1])[0,[q.COL[n] for n in cpu.CONTROL]],before_last[col])
            last=world.batch(1,event_budget=1000000,extra_device_budget=32*1024**2)
            gpu_seconds=time.perf_counter()-tick
        bank,rows,counts=compare(world,reference)
        assert world.device_bytes+max(metrics['extra_device_bytes'],last['extra_device_bytes'])<=64*1024**2
        np.savez_compressed(artifact,initial_data=initial.data,initial_heads=initial.heads,initial_where=initial.where,initial_age=initial.age,cpu_final_data=reference.data,cpu_final_heads=reference.heads,cpu_final_where=reference.where,final_age=reference.age,gpu_bank=bank,gpu_sparse_rows=rows,gpu_counts=counts,expected_Hold=expected)
        result=dict(passed=True,colonies=args.colonies,full_final_evaluation=args.full,physical_ticks=ticks,initial_age=initial.age,final_age=world.age,all_Data_and_controllers_match=True,cpu_seconds=cpu_seconds,gpu_initialization_seconds=init_seconds,gpu_evolution_seconds=gpu_seconds,base_device_bytes=world.device_bytes,cpu_metrics=cpu_metrics,cpu_last=cpu_last,gpu_metrics=metrics,gpu_last=last,descriptor_sha256=f.self_description().digest(),rom_sha256=hashlib.sha256(p.base_rom().tobytes()).hexdigest(),artifact_sha256=hashlib.sha256(artifact.read_bytes()).hexdigest(),source_sha256={str(Path(module.__file__)):hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest() for module in (bridge,independent,resident,packed)},seconds=time.perf_counter()-started,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,limitation='Initialized-history final-evaluation phase on canonical zero-context domain only. No GPU gather, full period, general noise or complete depth-two trajectory is established.')
        for module in (independent,resident):
            path=Path(module.__file__).with_suffix('.cu');result['source_sha256'][str(path)]=hashlib.sha256(path.read_bytes()).hexdigest()
        result['source_sha256'][str(Path(__file__))]=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)

if __name__=='__main__':main()
