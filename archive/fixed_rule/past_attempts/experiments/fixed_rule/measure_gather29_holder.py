"""Source-hashed CPU receipt for the fixed U=2^29 shared-gather candidate."""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import sys
import time

from gacsca.fixed_rule import gather29_holder_rule as f
from gacsca.fixed_rule import gather29_holder_program as p
from gacsca.fixed_rule import branch29_holder_program as old
from experiments.fixed_rule.certify_gather29_holder_rom import check
from experiments.fixed_rule.certify_gather29_holder_local_events import check as local_events


def costs(program,*,shared):
    g=program.layout()
    gather=sum(g.gather_schedule(i)[0] for i in range(3)) if shared else sum(
        g.schedule(*span)[0] for span in g.stage_ranges[:3])
    ticks=gather+sum(g.schedule(*span)[0] for span in g.stage_ranges[3:])
    ticks+=g.stage3_schedule()[0]
    return dict(Q=g.colony_cells,U=g.period_ticks,core_cells=g.computation_cells,
                memory_cells=g.memory_count,instruction_cells=len(g.instructions),
                controller_path_ticks=ticks,
                ROM_sha256=hashlib.sha256(program.base_rom().tobytes()).hexdigest())


def measure():
    started=time.perf_counter()
    certificate=check()
    physical_local_events=local_events()
    current=costs(p,shared=True)
    previous=costs(old,shared=False)
    assert current['controller_path_ticks']==certificate['controller_path_ticks']
    assert current['core_cells']==certificate['core_cells']
    assert current['Q']==previous['Q']==f.Q
    assert current['U']==previous['U']==f.U
    sources={Path(__file__).resolve(),
             Path('tests/fixed_rule/test_gather29_holder.py').resolve()}
    sources.update(Path(module.__file__).resolve() for module in tuple(sys.modules.values())
                   if getattr(module,'__file__',None)
                   and '/fixed_rule/' in str(Path(module.__file__).resolve()))
    hashes={str(path.relative_to(Path.cwd().resolve())):
            hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(sources)}
    return dict(passed=True,fixed_rule=f.identity(),current=current,
                separate_gathers=previous,
                core_cells_saved=previous['core_cells']-current['core_cells'],
                controller_ticks_saved=previous['controller_path_ticks']-current['controller_path_ticks'],
                conditional_certificate=certificate,
                physical_local_events=physical_local_events,source_sha256=hashes,
                seconds=time.perf_counter()-started,
                host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                physical_period_executed=False,depth2_macrostep_executed=False)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();result=measure()
    with args.output.open('x') as stream:stream.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps({key:value for key,value in result.items()
                      if key not in ('source_sha256','fixed_rule','conditional_certificate',
                                     'physical_local_events')},indent=2))


if __name__=='__main__':main()
