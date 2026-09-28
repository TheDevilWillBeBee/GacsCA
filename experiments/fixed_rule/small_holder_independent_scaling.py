"""Measured independent versus synchronized physical metadata-query scheduling."""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import time

from gacsca.fixed_rule import small_holder_resident_independent as fast
from gacsca.fixed_rule import small_holder_resident_period as slow
from gacsca.fixed_rule import small_holder_projected as r,small_holder_quotient as q,small_holder_core as c,small_holder_rule as f


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();out=Path(args.output)
    if out.exists():raise FileExistsError('preserve existing evidence')
    started=time.perf_counter();rows=[]
    fast.library();slow.library()
    for count in (1,8,32,128,257):
        for varied in (False,True):
            parents=tuple(r.Cell(address=i) for i in range(count))
            logical={i*f.Q:q.Cell(address=0,age=1,head=1,phase=c.READ_META,ra=200,rb=1,rd=i if varied else 0,value=1) for i in range(count)}
            timing={};results={}
            for label,module in (('independent',fast),('synchronous',slow)):
                with module.World(parents,age=1,logical=logical) as world:
                    clock=time.perf_counter();metrics=world.batch(count+8) if label=='independent' else world.run(count+8)
                    seconds=time.perf_counter()-clock
                    positions=[i*f.Q+count+8 for i in range(count)];cells=[]
                    for offset in range(0,count,256):cells.extend(world.logical_cells(positions[offset:offset+256]))
                    for i,cell in enumerate(cells):
                        assert cell.head and cell.phase==c.WAIT_META and cell.value==(i if varied else 0) and cell.rd==200
                    timing[label]=dict(seconds=seconds,metrics=metrics,explicit_device_bytes=world.device_bytes)
                    results[label]=tuple(cells)
            assert results['independent']==results['synchronous']
            assert timing['independent']['metrics']['colony_literal_ticks']==count
            assert timing['independent']['metrics']['max_colony_literal_ticks']==1
            assert timing['synchronous']['metrics']['literal_ticks']==(count if varied else 1)
            rows.append(dict(colonies=count,distinct_addresses=varied,physical_ticks=count+8,backends=timing,speedup=timing['synchronous']['seconds']/timing['independent']['seconds']))
    paths=[Path(__file__),Path(fast.__file__),Path(fast.__file__).with_suffix('.cu'),Path(slow.__file__),Path(slow.__file__).with_suffix('.cu')]
    result=dict(passed=True,rows=rows,seconds=time.perf_counter()-started,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,physical_descriptor=f.self_description().digest(),source_sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},binary_sha256=hashlib.sha256(Path(fast.library()._name).read_bytes()).hexdigest(),limitation='physical query scaling fixture, not nested dynamics; 257 colonies also exercises reuse of the 256 worker workspaces')
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))


if __name__=='__main__':main()
