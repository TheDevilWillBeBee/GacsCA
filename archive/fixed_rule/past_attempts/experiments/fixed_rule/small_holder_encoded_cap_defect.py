"""Two versus three physical Info-bit faults under an ordinary terminal cap.

The three-copy case installs one wrong upper Address via actual local majority;
the cap's ordinary rule then preserves it. No new kernel or host transition.
"""
import argparse
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import resource
import time
import numpy as np
from gacsca.fixed_rule import small_holder_rule as f, small_holder_projected as r
from gacsca.fixed_rule import small_holder_native as native, small_holder_boundary as cap
from gacsca.fixed_rule import small_holder_program as p, small_holder_core as c
from gacsca.fixed_rule import small_holder_resident_general as gpu, small_holder_general_faults as overlay
from experiments.fixed_rule.small_holder_temporal_repair import no_host, raw
from experiments.fixed_rule.small_holder_gather_two_periods import memory


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def info(world):
    return np.array([[cell.s2_data for cell in world.read(tuple(col*f.Q+a for a in p.layout().info))] for col in range(world.reference.colonies)],dtype=np.uint64)


def next_upper(cells):
    return tuple(r.project(x) for x in native.step_ring(tuple(r.lift(x) for x in cells)))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();stem=Path(args.output)
    for suffix in ('.json','.npz','.progress.json'):
        if stem.with_suffix(suffix).exists():raise FileExistsError('preserve evidence')
    started=time.perf_counter();top=(cap.cell(),)*15;archive={'initial':raw(top)};cases=[];seconds=0.;observed=[]
    for copies,offsets,periods in ((2,(-1,1),1),(3,(-1,0,1),2)):
        prefix=f'copies{copies}_';target=7*f.Q+p.layout().info[f.COL['address']]
        probe=tuple(target+d for d in range(-14,15));expected=list(top)
        if copies==3:expected[7]=replace(expected[7],address=f.Q-2)
        expected=tuple(expected);decoded=[];faultmap=[]
        with gpu.World(top) as base,overlay.World(base) as world:
            archive[prefix+'probe']=np.array(probe,dtype=np.uint64)
            before=world.read(probe);archive[prefix+'before_fault']=raw(before)
            changes={}
            for d in offsets:
                position=target+d;name=f's{2-d}_data';old=r.project(world.read((position,))[0])
                changes[position]=replace(old,**{name:getattr(old,name)^1});faultmap.append((position,name))
            world.inject(changes);archive[prefix+'after_fault']=raw(world.read(probe));archive[prefix+'raw_info_after_fault']=info(world)
            if copies==3:
                try:world.decode()
                except ValueError:pass
                else:raise AssertionError('Address fault must leave stale Info metadata until actual regeneration')
            tick=time.perf_counter()
            with no_host():first=world.advance(1)
            seconds+=time.perf_counter()-tick
            assert not world.positions
            archive[prefix+'after_one_tick']=raw(world.read(probe));archive[prefix+'raw_info_after_one_tick']=info(world)
            assert int(archive[prefix+'raw_info_after_one_tick'][7,f.COL['address']])==(f.Q-2 if copies==3 else f.Q-1)
            observed.append(memory());checkpoints=[]
            for period in range(periods):
                target_time=(period+1)*f.U;expected=next_upper(expected)
                while world.time<target_time:
                    tick=time.perf_counter()
                    with no_host():world.advance(min(c.T,target_time-world.time))
                    seconds+=time.perf_counter()-tick
                    stem.with_suffix('.progress.json').write_text(json.dumps(dict(status='running',copies=copies,physical_time=world.time,gpu_seconds=seconds))+'\n')
                actual=world.decode();np.testing.assert_array_equal(raw(actual),raw(expected))
                assert all(x.address==(f.Q-2 if copies==3 and i==7 else f.Q-1) for i,x in enumerate(actual))
                assert all(x.age==period+1 and x.f1==x.f2==1 for x in actual)
                decoded.append(raw(actual));checkpoints.append(dict(time=world.time,center_address=actual[7].address,all154_fields_match=True,raw_metadata_consistent=True,exceptions=len(world.positions)))
                print(json.dumps(dict(copies=copies,checkpoint=checkpoints[-1],gpu_seconds=seconds)),flush=True)
            archive[prefix+'decoded']=np.array(decoded,dtype=np.uint64)
            cases.append(dict(physical_one_bit_faults=copies,faultmap=faultmap,periods=periods,first_tick=first,checkpoints=checkpoints,extra_exception_device_bytes=world.device_bytes))
            observed.append(memory())
    np.savez_compressed(stem.with_suffix('.npz'),**archive)
    files=[Path(__file__),Path(gpu.__file__),Path(overlay.__file__),Path(cap.__file__),Path('experiments/fixed_rule/small_holder_temporal_repair.py')]
    result=dict(passed=True,cases=cases,physical_sites=15*f.Q,total_executed_physical_ticks=3*f.U,gpu_seconds=seconds,seconds=time.perf_counter()-started,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,observed_process_gpu_mib=observed,physical_descriptor_sha256=f.self_description().digest(),controller_binary_sha256=sha(gpu.library()._name),fault_binary_sha256=sha(overlay.library()._name),source_sha256={str(path):sha(path) for path in files},artifact_sha256=sha(stem.with_suffix('.npz')),scope='One-link boundary failure control: two physical copies repair locally; three copies create a wrong encoded Address that persists at two decoded commits. Complete descriptor invariant proves subsequent upper Address persistence, conditional on correct continued simulation. No full nested upper work period or noise threshold.')
    stem.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
    stem.with_suffix('.progress.json').write_text(json.dumps(dict(status='complete',seconds=result['seconds']))+'\n')
    print(json.dumps(result,indent=2),flush=True)

if __name__=='__main__':main()
