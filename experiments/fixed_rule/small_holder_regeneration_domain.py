"""Exhaust the fixed Address alphabet through actual local regeneration code.

Each bounded batch seeds the same physical ROM/controller at the regeneration
entry with a different encoded Hold.Address. No replacement program or host
metadata write is used during evolution. This is a clean-subroutine certificate,
not a full simulation or noisy recovery theorem.
"""
import argparse
from contextlib import ExitStack
import hashlib
import json
from pathlib import Path
import resource
import time
from unittest.mock import patch
import numpy as np
from gacsca.fixed_rule import small_holder_resident_independent as gpu
from gacsca.fixed_rule import small_holder_rule as f,small_holder_projected as r
from gacsca.fixed_rule import small_holder_program as p,small_holder_core as c
from gacsca.fixed_rule import small_holder_quotient as q,small_holder_native as native
from gacsca.fixed_rule.wordcode import Program


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def execute_batch(addresses):
    addresses=tuple(addresses)
    if not addresses or len(addresses)>128 or any(type(a) is not int or not 0<=a<f.Q for a in addresses):
        raise ValueError('at most 128 fixed-alphabet Addresses')
    g=p.layout();entry=g.description_instruction+len(f.self_description().operations)+f.FIELDS
    duration=g.schedule(entry,g.stage_ranges[4][1])[0]
    logical={};poison=0xD3AD123456789ABC
    for col,address in enumerate(addresses):
        fields={g.hold[f.COL[name]]:poison for name,_ in f.STATIC}
        fields[g.hold[f.COL['address']]]=address
        for at,value in fields.items():logical[col*f.Q+at]=q.Cell(address=at,age=1,data=value)
        at=g.memory_count+entry
        logical[col*f.Q+at]=q.Cell(address=at,age=1,head=1,phase=c.FETCH,pc=entry)
    with gpu.World((r.Cell(),)*len(addresses),age=1,logical=logical) as world:
        tick=time.perf_counter()
        with ExitStack() as stack:
            for obj,name in ((Program,'evaluate'),(f,'local_step'),(r,'local_step'),(native,'local_step')):
                stack.enter_context(patch.object(obj,name,side_effect=AssertionError('host simulated transition')))
            metrics=world.batch(duration)
        seconds=time.perf_counter()-tick
        actual=np.array([[x.data for x in world.logical_cells(tuple(col*f.Q+a for a in g.hold))] for col in range(len(addresses))],dtype=np.uint64)
        expected=np.array([f.encode_cell(r.lift(r.Cell(address=a))) for a in addresses],dtype=np.uint64)
        np.testing.assert_array_equal(actual,expected)
        # The same IF_THIRD at the real ROM exit halts at this physical Age.
        end=g.memory_count+g.stage_ranges[4][1]-1
        for col in range(len(addresses)):
            records=world.logical_cells(tuple(col*f.Q+a for a in range(end-2,end+3)))
            assert all(not x.head and all(getattr(x,n)==0 for n in c.CONTROL) for x in records)
        return actual,dict(metrics,advance_seconds=seconds,resident_device_bytes=world.device_bytes)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();stem=Path(args.output)
    for ext in ('.json','.npz','.progress.json'):
        if stem.with_suffix(ext).exists():raise FileExistsError('preserve evidence')
    started=time.perf_counter();records=np.empty((f.Q,len(f.STATIC)),dtype=np.uint64);gpu_seconds=0.;events=0;evals=0;max_bytes=0;duration=None
    for begin in range(0,f.Q,128):
        addresses=tuple(range(begin,min(begin+128,f.Q)));actual,metrics=execute_batch(addresses)
        records[begin:begin+len(addresses)]=actual[:,:len(f.STATIC)]
        gpu_seconds+=metrics['advance_seconds'];events+=metrics['colony_literal_ticks'];evals+=metrics['logical_evaluations'];duration=metrics['physical_ticks']
        max_bytes=max(max_bytes,metrics['resident_device_bytes']+metrics['extra_device_bytes'])
        stem.with_suffix('.progress.json').write_text(json.dumps(dict(status='running',completed_addresses=begin+len(addresses),gpu_run_seconds=gpu_seconds))+'\n')
        if (begin//128)%32==0:print(json.dumps(dict(completed_addresses=begin+len(addresses),elapsed=time.perf_counter()-started)),flush=True)
    np.savez_compressed(stem.with_suffix('.npz'),metadata=records)
    paths=[Path(__file__),Path(gpu.__file__),Path(gpu.__file__).with_suffix('.cu'),Path(p.__file__),Path(f.__file__),Path(r.__file__)]
    result=dict(passed=True,addresses=f.Q,metadata_fields=len(f.STATIC),checked_metadata_words=records.size,checked_hold_words=f.Q*f.FIELDS,batch_colonies=128,physical_ticks_per_batch=duration,colony_literal_events=events,logical_evaluations=evals,gpu_run_seconds=gpu_seconds,seconds=time.perf_counter()-started,explicit_peak_device_bytes=max_bytes,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,source_sha256={str(path):digest(path) for path in paths},binary_sha256=digest(gpu.library()._name),descriptor_sha256=f.self_description().digest(),artifact_sha256=digest(stem.with_suffix('.npz')),scope='all 32768 Hold.Address values through the actual fixed physical regeneration subroutine in canonical clean lower geometry; seven offsets/all selectors/fallback/wrap; not a noisy or full-macrostep theorem')
    stem.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n');stem.with_suffix('.progress.json').write_text(json.dumps(dict(status='complete'))+'\n');print(json.dumps({k:v for k,v in result.items() if k!='source_sha256'},indent=2),flush=True)


if __name__=='__main__':main()
