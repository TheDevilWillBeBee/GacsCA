"""Nonuniform physical SEND payloads plus metadata queries, 1–257 colonies."""
import argparse,hashlib,json,resource,time
from pathlib import Path
from gacsca.fixed_rule import small_holder_resident_gather as fast,small_holder_resident_mixed as slow
from gacsca.fixed_rule import small_holder_rule as f,small_holder_core as c,small_holder_program as p,small_holder_projected as r,small_holder_quotient as q


def read(world,positions):
    out=[]
    for at in range(0,len(positions),256):out.extend(world.logical_cells(positions[at:at+256]))
    return tuple(out)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();out=Path(args.output)
    if out.exists():raise FileExistsError('preserve evidence')
    start=time.perf_counter();fast.library();rows=[];g=p.layout()
    source=g.info[f.COL['s2_value']];target=g.history(0,1,f.COL['s2_value']);ticks=8*f.Q
    unfolded=(source+ticks)%(2*g.computation_cells);head=unfolded if unfolded<g.computation_cells else 2*g.computation_cells-1-unfolded
    for count in (1,8,32,128,257):
        values=tuple(0xABC000+i*19 for i in range(count));parents=tuple(r.Cell(address=i,s2_value=values[i]) for i in range(count))
        logical={i*f.Q+source:q.Cell(address=source,age=1,head=1,phase=c.TRANSMIT,ra=source,rb=target,rd=2,data=values[i]) for i in range(count)}
        timing={};states={}
        for name,module in (('gather',fast),('synchronous',slow)):
            with module.World(parents,age=1,logical=logical) as world:
                clock=time.perf_counter();metrics=world.batch(ticks) if name=='gather' else world.run(ticks);seconds=time.perf_counter()-clock
                delivered=read(world,tuple(i*f.Q+target for i in range(count)))
                assert tuple(x.data for x in delivered)==tuple(values[(i-1)%count] for i in range(count))
                controllers=read(world,tuple(i*f.Q+head for i in range(count)));assert all(x.head for x in controllers)
                states[name]=(delivered,controllers)
                timing[name]=dict(seconds=seconds,metrics=metrics,resident_bytes=world.device_bytes)
        assert states['gather']==states['synchronous']
        rows.append(dict(colonies=count,physical_ticks=ticks,backends=timing,speedup=timing['synchronous']['seconds']/timing['gather']['seconds']))
    paths=[Path(__file__),Path(fast.__file__),Path(fast.__file__).with_suffix('.cu'),Path(slow.__file__)]
    result=dict(passed=True,rows=rows,seconds=time.perf_counter()-start,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,source_sha256={str(path):hashlib.sha256(path.read_bytes()).hexdigest() for path in paths},binary_sha256=hashlib.sha256(Path(fast.library()._name).read_bytes()).hexdigest(),scope='all delivered foreign-history payloads and live controller records match synchronous evolution; 257 colonies exercises workspace reuse; not a nested runtime estimate')
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))


if __name__=='__main__':main()
