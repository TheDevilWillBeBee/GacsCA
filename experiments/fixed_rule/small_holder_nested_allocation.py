"""Bounded whole-hierarchy allocation/reset pilot, with streamed Info verification.

Coordinate a large GPU reservation before depth two. Depth one is the small
reference invocation. This checks initialization and eight physical ticks, not
a simulated macrostep. The physical rule/ROM do not depend on depth.
"""
import argparse,hashlib,json,resource,time
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import small_holder_resident_mixed as gpu,small_holder_stream_initial as stream
from gacsca.fixed_rule import small_holder_rule as f,small_holder_projected as r,small_holder_quotient as q,small_holder_program as p


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--depth',type=int,required=True);parser.add_argument('--device-budget',type=int,default=64*1024**2);parser.add_argument('--extra-device-budget',type=int,default=64*1024**2);parser.add_argument('--output',required=True);args=parser.parse_args();out=Path(args.output)
    if out.exists():raise FileExistsError('preserve evidence')
    started=time.perf_counter();top=(r.Cell(address=321,age=117,s2_head=1,s2_phase=3,s2_rd=321,s2_value=0x123456789ABCDEF0),);initial=stream.InitialRing(top)
    count=initial.size(args.depth-1);resident=2799840+154456*count;extra=79416*count
    if resident>args.device_budget or extra>args.extra_device_budget:raise ValueError('requested budgets do not cover explicit resident and staged buffers')
    with gpu.World.from_hierarchy(top,args.depth,device_budget=args.device_budget) as world:
        tick=time.perf_counter();metrics=world.advance(8,extra_device_budget=args.extra_device_budget);advance_seconds=time.perf_counter()-tick
        assert world.age==8 and world.time==8
        verified=0;sha=hashlib.sha256()
        for part in initial.chunks(args.depth-1):
            for row in part:
                col=verified
                cells=world.logical_cells(tuple(col*f.Q+a for a in p.layout().info))
                words=np.array([cell.data for cell in cells],dtype=np.uint64)
                np.testing.assert_array_equal(words,row);sha.update(words.tobytes())
                head=world.logical_cells((col*f.Q+7,))[0]
                assert head==q.Cell(address=7,age=8,head=1,pc=p.layout().entries[0])
                verified+=1
        assert verified==count
        allocated=world.device_bytes
    paths=(Path(__file__),Path(gpu.__file__),Path(stream.__file__))
    result=dict(passed=True,encoded_depth=args.depth,entire_lower_ring_allocated=True,lower_colonies=count,physical_sites=count*f.Q,physical_ticks=8,advance_seconds=advance_seconds,all_encoded_raw_parent_words_verified=True,all_lower_heads_verified=True,uploaded_info_sha256=sha.hexdigest(),explicit_resident_bytes=allocated,explicit_peak_with_staging_bytes=allocated+extra,seconds=time.perf_counter()-started,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,metrics=metrics,descriptor_sha256=f.self_description().digest(),binary_sha256=hashlib.sha256(Path(gpu.library()._name).read_bytes()).hexdigest(),source_sha256={str(path):hashlib.sha256(path.read_bytes()).hexdigest() for path in paths},limitation='eight physical initialization/reset ticks only; no lower macrostep or full top step')
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))


if __name__=='__main__':main()
