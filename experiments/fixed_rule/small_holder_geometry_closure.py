"""Two full physical periods with upper Address repair and local ROM regeneration."""
import argparse
from contextlib import ExitStack
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import resource
import time
from unittest.mock import patch
import numpy as np
from gacsca.fixed_rule import small_holder_resident_gather as gpu
from gacsca.fixed_rule import small_holder_rule as f,small_holder_projected as r
from gacsca.fixed_rule import small_holder_program as p,small_holder_core as c
from gacsca.fixed_rule import small_holder_native as native
from gacsca.fixed_rule.wordcode import Program
from experiments.fixed_rule.small_holder_execution import initial_ring


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def rows(world,addresses):
    return np.array([[x.data for x in world.logical_cells(tuple(col*f.Q+a for a in addresses))] for col in range(world.colonies)],dtype=np.uint64)
def forbid_host_rule():
    stack=ExitStack()
    for obj,name in ((Program,'evaluate'),(f,'local_step'),(r,'local_step'),(native,'local_step')):
        stack.enter_context(patch.object(obj,name,side_effect=AssertionError('host simulated transition')))
    return stack


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();stem=Path(args.output)
    for ext in ('.json','.npz','.progress.json'):
        if stem.with_suffix(ext).exists():raise FileExistsError('preserve evidence')
    started=time.perf_counter();g=p.layout();top=list(initial_ring());top[7]=replace(top[7],address=30000)
    expected=tuple(r.lift(x) for x in top);initial=native.array_from_cells(expected)
    regen_start=g.description_instruction+len(f.self_description().operations)+f.FIELDS
    before_regen=c.VOTE_AGES[0]+g.schedule(g.entries[4],regen_start)[0]+100
    assert before_regen<f.CAPTURE_AGE
    frames=[];raw_frames=[];hold_before=[];hold_after=[];cases=[];gpu_seconds=0.
    with gpu.World(tuple(top)) as world:
        for period in range(2):
            raw=native.step_ring(expected);wanted=tuple(r.lift(r.project(x)) for x in raw)
            assert all(x.f2==0 for x in wanted)
            wrong=[(i,name) for i,(a,b) in enumerate(zip(raw,wanted)) for name,_ in f.STATIC if getattr(a,name)!=getattr(b,name)]
            if period==0:
                assert wanted[7].address==107 and len(wrong)>=49//2
                assert raw[7]!=wanted[7]
            raw_frames.append(native.array_from_cells(raw));checkpoints=[]
            for phase,offset in (('raw_output',before_regen),('regenerated',f.CAPTURE_AGE),('commit',f.U)):
                target=period*f.U+offset
                while world.time<target:
                    tick=time.perf_counter()
                    with forbid_host_rule():world.advance(min(c.T,target-world.time))
                    gpu_seconds+=time.perf_counter()-tick
                    stem.with_suffix('.progress.json').write_text(json.dumps(dict(status='running',physical_time=world.time,period=period+1,phase=phase))+'\n')
                if phase=='raw_output':
                    value=rows(world,g.hold);np.testing.assert_array_equal(value,native.array_from_cells(raw));hold_before.append(value)
                elif phase=='regenerated':
                    value=rows(world,g.hold);np.testing.assert_array_equal(value,native.array_from_cells(wanted));hold_after.append(value)
                else:
                    value=native.array_from_cells(tuple(r.lift(x) for x in world.decode()));np.testing.assert_array_equal(value,native.array_from_cells(wanted));frames.append(value)
                checkpoints.append(dict(phase=phase,time=world.time,all_154_fields_match=True))
            cases.append(dict(period=period+1,changed_addresses=[(i,a.address,b.address) for i,(a,b) in enumerate(zip(expected,wanted)) if a.address!=b.address],regenerated_fields=wrong,checkpoints=checkpoints,center_primary_data=wanted[7].s2_data))
            expected=wanted
            print(json.dumps(dict(period=period+1,time=world.time,metadata_fields_changed=len(wrong),center_data=wanted[7].s2_data)),flush=True)
        device_bytes=world.device_bytes
    np.savez_compressed(stem.with_suffix('.npz'),initial=initial,raw_outputs=np.array(raw_frames),hold_before=np.array(hold_before),hold_after=np.array(hold_after),decoded=np.array(frames))
    paths=[Path(__file__),Path(gpu.__file__),Path(gpu.__file__).with_suffix('.cu'),Path(p.__file__),Path(f.__file__),Path(r.__file__)]
    result=dict(passed=True,cases=cases,physical_ticks=2*f.U,represented_cells=len(top),physical_sites=len(top)*f.Q,before_regeneration_offset=before_regen,regeneration_instruction=regen_start,physical_descriptor_sha256=f.self_description().digest(),source_sha256={str(path):digest(path) for path in paths},binary_sha256=digest(gpu.library()._name),artifact_sha256=digest(stem.with_suffix('.npz')),gpu_run_seconds=gpu_seconds,seconds=time.perf_counter()-started,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,resident_device_bytes=device_bytes,scope='two successive one-link macrosteps with autonomous upper Address repair and observed local metadata regeneration; not a nested upper work period or arbitrary-noise theorem')
    stem.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n');stem.with_suffix('.progress.json').write_text(json.dumps(dict(status='complete'))+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ('cases','source_sha256')},indent=2),flush=True)


if __name__=='__main__':main()
