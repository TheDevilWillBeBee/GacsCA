"""Measure synchronization loss when colonies query distinct metadata addresses.

This is a physical-controller stress fixture, not a nested execution benchmark.
No large CPU state or depth-two-sized device allocation is made.
"""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import time
from gacsca.fixed_rule import small_holder_resident_prefix as gpu,small_holder_projected as r,small_holder_quotient as q,small_holder_core as c,small_holder_rule as f


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();rows=[];started=time.perf_counter()
    for count in (1,8,32,128):
        for varied in (False,True):
            parents=tuple(r.Cell(address=i) for i in range(count))
            logical={i*f.Q:q.Cell(address=0,age=1,head=1,phase=c.READ_META,ra=200,rb=1,rd=i if varied else 0,value=1) for i in range(count)}
            with gpu.World(parents,age=1,logical=logical) as world:
                tick=time.perf_counter();metrics=world.run(count+8);seconds=time.perf_counter()-tick
                cells=world.logical_cells(tuple(i*f.Q+count+8 for i in range(count)))
                for i,cell in enumerate(cells):
                    assert cell.head==1 and cell.phase==c.WAIT_META and cell.value==(i if varied else 0) and cell.rd==200
                assert metrics['literal_ticks']==(count if varied else 1)
                rows.append(dict(colonies=count,distinct_metadata_addresses=varied,physical_ticks=count+8,metrics=metrics,run_seconds=seconds,explicit_device_bytes=world.device_bytes))
    one=next(x['explicit_device_bytes'] for x in rows if x['colonies']==1);eight=next(x['explicit_device_bytes'] for x in rows if x['colonies']==8)
    per=(eight-one)//7;fixed=one-per
    assert all(x['explicit_device_bytes']==fixed+per*x['colonies'] for x in rows)
    result=dict(passed=True,rows=rows,per_colony_device_bytes=per,fixed_device_bytes=fixed,depth_two_Q_colonies_estimated_device_bytes=fixed+per*f.Q,large_allocation_performed=False,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,seconds=time.perf_counter()-started,descriptor_sha256=f.self_description().digest(),source_sha256={str(path):hashlib.sha256(path.read_bytes()).hexdigest() for path in (Path(__file__),Path(gpu.__file__),Path(gpu.__file__).with_suffix('.cu'))},limitation='independent metadata queries destroy shared-time jumps; this is not a measured full depth-two runtime')
    path=Path(args.output)
    if path.exists():raise FileExistsError('preserve evidence')
    path.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))


if __name__=='__main__':main()
