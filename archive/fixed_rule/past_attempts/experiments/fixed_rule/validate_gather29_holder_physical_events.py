"""Compare accelerated and literal full-F steps at actual new-rule events.

The event positions are reached by evolving one continuous physical state;
there is no host replacement of the represented upper transition.
"""
import hashlib
import json
from pathlib import Path
import time

import numpy as np

from gacsca.fixed_rule import gather29_holder_cpu_general as backend
from gacsca.fixed_rule import gather29_holder_cpu_events as events
from gacsca.fixed_rule import gather29_holder_core as c
from gacsca.fixed_rule import gather29_holder_program as p
from gacsca.fixed_rule import gather29_holder_projected as r
from gacsca.fixed_rule import gather29_holder_rule as f
from experiments.fixed_rule.run_gather29_holder_cpu_general_periods import parents


def check():
    start=time.perf_counter();g=p.layout();upper=parents(1)
    data=np.zeros((1,f.Q),dtype=np.uint64)
    data[0,list(g.info)]=f.encode_cell(r.lift(upper[0]))
    world=backend.World(data,np.zeros((1,len(events.CONTROL)),dtype=np.uint64),
                        np.zeros(1,dtype=np.uint64),age=0)
    checked=[]

    def advance_to(age):
        if age<world.age:raise AssertionError(('time reversal',age,world.age))
        if age>world.age:world.advance(age-world.age)

    def quiet_to(age):
        if age<world.age:raise AssertionError(('time reversal',age,world.age))
        world.quiet_advance(age-world.age)

    def compare(name,pc,old_age):
        advance_to(old_age)
        assert int(world.where[0])==g.memory_count+pc,(name,world.age,world.where[0],pc)
        head=tuple(map(int,world.heads[0]))
        assert head[0]==1 and head[1+c.CONTROL.index('phase')]==c.FETCH
        assert head[1+c.CONTROL.index('pc')]==pc
        assert not len(world.packets),('literal comparator requires no pending mail',name)
        literal=backend.World(world.data,world.heads,world.where,age=world.age,
                              right=world.right,left=world.left,flags=world.flags)
        literal.time=world.time
        literal.step();world.advance(1)
        for field in ('data','heads','where','right','left','flags'):
            np.testing.assert_array_equal(getattr(world,field),getattr(literal,field),
                                          err_msg=f'{name}: physical {field} mismatch')
        assert world.age==literal.age and world.time==literal.time
        checked.append(dict(name=name,old_age=old_age,pc=pc,
                            full_raw_literal_sites=f.Q,
                            state_sha256=hashlib.sha256(world.data.tobytes()+
                                                         world.heads.tobytes()+
                                                         world.flags.tobytes()).hexdigest()))

    for stage in range(3):
        quiet_to(c.RESET_AGES[stage]);world.step()
        _,rows=g.gather_schedule(stage)
        for kind in (c.ADD,c.SEND):
            pc=next(i for i,op in enumerate(g.instructions[:g.stage_ranges[stage][1]])
                    if op.kind==kind and ((op.d if kind==c.ADD else op.b)&c.PHASE_MARK))
            compare(f'{"ADD" if kind==c.ADD else "SEND"}_gather_{stage}',pc,
                    c.RESET_AGES[stage]+rows[pc][0]-1)
        timing=g.timing_certificate()['gathers'][stage]
        advance_to(c.RESET_AGES[stage]+max(timing['head_stopped'],timing['last_arrival']))
        assert not np.any(world.heads) and not len(world.packets)

    quiet_to(c.VOTE_AGES[0]);world.step()
    early=dict(g.stage3_schedule()[1])[g.branch_instruction][0]
    compare('BRANCH_THIRD_early',g.branch_instruction,c.VOTE_AGES[0]+early-1)
    timing=g.timing_certificate()
    advance_to(c.VOTE_AGES[0]+max(timing['stage3_head_stopped'],
                                    timing['stage3_last_delivery']))
    quiet_to(c.CAPTURE_AGE-1);world.step()
    quiet_to(c.RESET_AGES[3]);world.step()
    advance_to(c.RESET_AGES[3]+g.schedule(*g.stage_ranges[3])[0])
    quiet_to(c.WF_END)
    quiet_to(c.RESET_AGES[4]);world.step()
    _,rows=g.schedule(*g.stage_ranges[4])
    late=rows[g.branch_instruction-g.stage_ranges[4][0]][0]
    compare('BRANCH_THIRD_late',g.branch_instruction,c.RESET_AGES[4]+late-1)
    return dict(passed=True,cases=checked,case_count=len(checked),
                complete_literal_raw_site_steps=len(checked)*f.Q,
                physical_rule_sha256=f.self_description().digest(),
                seconds=time.perf_counter()-start,
                scope='Actual evolved physical event states; each compared '
                      'against one complete literal new-rule ring step.',
                limitation='Selected events only; full period uses guarded '
                           'event acceleration between literal boundaries.')


if __name__=='__main__':print(json.dumps(check(),indent=2))
