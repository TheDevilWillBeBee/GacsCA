"""Check actual evolved PACK3 fetches against literal complete physical steps."""
import json
import time

import numpy as np

from gacsca.fixed_rule import packed29_holder_cpu_general as backend
from gacsca.fixed_rule import packed29_holder_cpu_events as events
from gacsca.fixed_rule import packed29_holder_core as c
from gacsca.fixed_rule import packed29_holder_program as p
from gacsca.fixed_rule import packed29_holder_projected as r
from gacsca.fixed_rule import packed29_holder_rule as f
from experiments.fixed_rule.run_packed29_holder_cpu_general_periods import parents


def check():
    started=time.perf_counter();g=p.layout();upper=parents(1)
    data=np.zeros((1,f.Q),dtype=np.uint64)
    data[0,list(g.info)]=f.encode_cell(r.lift(upper[0]))
    world=backend.World(data,np.zeros((1,len(events.CONTROL)),dtype=np.uint64),
                        np.zeros(1,dtype=np.uint64),age=0)

    def advance_to(age):
        assert age>=world.age
        if age>world.age:world.advance(age-world.age)

    def quiet_to(age):
        assert age>=world.age
        if age>world.age:world.quiet_advance(age-world.age)

    timing=g.timing_certificate()
    for stage in range(3):
        quiet_to(c.RESET_AGES[stage]);world.step()
        advance_to(c.RESET_AGES[stage]+max(timing['gathers'][stage]['head_stopped'],
                                             timing['gathers'][stage]['last_arrival']))
        assert not np.any(world.heads) and not len(world.packets)
    quiet_to(c.VOTE_AGES[0]);world.step()
    advance_to(c.VOTE_AGES[0]+max(timing['stage3_head_stopped'],
                                    timing['stage3_last_delivery']))
    quiet_to(c.CAPTURE_AGE-1);world.step()
    quiet_to(c.RESET_AGES[3]);world.step()
    advance_to(c.RESET_AGES[3]+g.schedule(*g.stage_ranges[3])[0])
    quiet_to(c.WF_END)
    quiet_to(c.RESET_AGES[4]);world.step()

    start,end=g.stage_ranges[4]
    _,rows=g.schedule(start,end)
    row=next(row for row in g.packed.rows
             if row.kind==c.PACK3 and row.count==3 and start<=row.micro_pc<end-2)
    checked=[]
    for slot in range(3):
        pc=row.micro_pc+slot;at=g.physical_position(pc)
        age=c.RESET_AGES[4]+rows[pc-start][0]-1
        advance_to(age)
        assert int(world.where[0])==at,(slot,world.age,world.where[0],at)
        head=tuple(map(int,world.heads[0]))
        assert head[0]==1 and head[1+c.CONTROL.index('phase')]==c.FETCH
        assert head[1+c.CONTROL.index('pc')]==pc
        assert not len(world.packets)
        positions=range(at-4,at+5)
        expected={position:f.local_step(tuple(world.cell(position+j)
                                             for j in f.NEIGHBORHOOD))
                  for position in positions}
        literal=backend.World(world.data,world.heads,world.where,age=world.age,
                              right=world.right,left=world.left,flags=world.flags)
        literal.time=world.time
        literal.step();world.advance(1)
        for field in ('data','heads','where','right','left','flags'):
            np.testing.assert_array_equal(getattr(world,field),getattr(literal,field),
                                          err_msg=f'packed slot {slot}: {field}')
        for position,want in expected.items():
            assert literal.cell(position)==want,('scalar complete F mismatch',slot,position)
        checked.append(dict(slot=slot,virtual_pc=pc,physical_row=at,
                            age=age,scalar_sites=len(expected),literal_ring_sites=f.Q))
    return dict(passed=True,cases=checked,seconds=time.perf_counter()-started,
                complete_raw_fields=f.FIELDS,
                scope='Three naturally evolved packed fetches; accelerated, literal native, '
                      'and scalar complete physical F agree on local sites.')


if __name__=='__main__':print(json.dumps(check(),indent=2))
