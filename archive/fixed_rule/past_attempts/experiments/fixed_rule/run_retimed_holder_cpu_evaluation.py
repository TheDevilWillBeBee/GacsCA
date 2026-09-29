"""Execute the full final-evaluation controller phase using physical F events.

Histories are initial fixture data. The reference upper transition is used only
for final comparison, never by the evolving backend. This is not a whole period.
"""
import argparse
import hashlib
import json
from pathlib import Path
import random
import resource
import time
import numpy as np
from gacsca.fixed_rule import retimed_holder_cpu_events as backend
from gacsca.fixed_rule import retimed_holder_rule as f,retimed_holder_core as c,retimed_holder_program as p
from gacsca.fixed_rule import retimed_holder_projected as r,retimed_holder_initial as initial,retimed_holder_native as native
from experiments.fixed_rule.audit_small_holder_position_events import sha


def fixture(n):
    rng=random.Random(2026092671);g=p.layout()
    values=[rng.getrandbits(64) for _ in range(n)]
    def logical(pos):
        at=pos%n;values_=dict(r.record(at),address=at,age=c.RESET_AGES[4]+100,data=values[at])
        if at==n//2:values_.update(head=1,phase=c.READ_B,pc=23,rb=at,rd=(at+1)%n,value=0x123456789abcdef0,alu=c.NAND)
        return c.Cell(**values_)
    upper=tuple(initial.coherent_cell(logical,col) for col in range(n))
    raw=tuple(f.encode_cell(r.lift(cell)) for cell in upper)
    data=np.zeros((n,f.Q),dtype=np.uint64)
    for col in range(n):
        data[col,list(g.info)]=raw[col]
        for neighbor in range(-7,8):
            incoming=raw[(col+neighbor)%n]
            for k,word in enumerate(incoming):
                data[col,g.votes[(neighbor+7)*f.FIELDS+k]]=word
                for stage in range(3):data[col,g.history(stage,neighbor,k)]=word
    heads=np.zeros((n,len(backend.CONTROL)),dtype=np.uint64)
    # Bootstrap from an actual literal first-cell reset/vote output. The rest
    # of the voted history bank above is explicitly fixture initialization.
    before=backend.World(data,heads,np.zeros(n,dtype=np.uint64),age=c.RESET_AGES[4])
    for col in range(n):
        cell=native.local_step(tuple(before.cell(col*f.Q+j) for j in f.NEIGHBORHOOD))
        heads[col]=[getattr(cell,'s2_'+name) for name in backend.CONTROL]
    world=backend.World(data,heads,np.zeros(n,dtype=np.uint64),age=c.RESET_AGES[4]+1)
    return upper,world


def run(n):
    upper,world=fixture(n);g=p.layout();start=world.age
    expected=tuple(f.encode_cell(r.lift(r.project(native.local_step(tuple(r.lift(upper[(col+j)%n]) for j in f.NEIGHBORHOOD))))) for col in range(n))
    stopped=c.RESET_AGES[4]+g.schedule(*g.stage_ranges[4])[0]
    tick=time.perf_counter();metrics=world.advance(stopped-start-1)
    assert np.all(world.heads[:,0]==1),'head halted before predicted final physical tick'
    last=world.advance(1);elapsed=time.perf_counter()-tick
    assert not np.any(world.heads),'head or stale controller survived final IF_THIRD halt'
    actual=tuple(tuple(map(int,row[list(g.hold)])) for row in world.data)
    assert actual==expected,'executed full raw Hold differs from intended upper transition'
    metrics={name:metrics[name]+last[name] for name in metrics}
    return dict(passed=True,colonies=n,start_age=start,stop_age=world.age,**metrics,
                execution_seconds=elapsed,complete_raw_output_words=n*f.FIELDS,
                complete_Hold_matches_upper_rule=True,all_controller_words_zero_after_halt=True,
                nonzero_controller_before_final_tick=True,
                output_sha256=hashlib.sha256(np.array(actual,dtype=np.uint64).tobytes()).hexdigest(),
                limitation='Complete physical final-evaluation phase from explicit initialized history fixtures. Gather, capture/flags, commit and a second whole period were not executed. The backend rejects mail emission and clock-boundary crossings.')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--colonies',type=int,default=15);parser.add_argument('--output',required=True);args=parser.parse_args();out=Path(args.output)
    if out.exists():raise FileExistsError('preserve evidence')
    start=time.perf_counter();result=run(args.colonies)
    result.update(descriptor_sha256=f.self_description().digest(),rom_sha256=hashlib.sha256(p.base_rom().tobytes()).hexdigest(),
                  source_sha256={str(path):sha(path) for path in (Path(__file__),Path(backend.__file__),Path(backend.__file__).with_suffix('.cpp'),Path(native.__file__),Path(p.__file__),backend.CUDA)},
                  seconds=time.perf_counter()-start,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)

if __name__=='__main__':main()
