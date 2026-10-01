"""Symbolic head path and literal SEND endpoints for the compact holder ROM.

The one-head path uses the same local core.advance/reflect_left procedures and
checks every fetch, transmit, and MEM receipt with literal local steps. It is
an event witness, not a continuous colony evolution or a U retiming proof.
"""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import time

from gacsca.fixed_rule import stream28_dual_holder_rom as rom
from gacsca.fixed_rule import stream28_dual_pass20 as dual
from gacsca.fixed_rule import stream28_dual_core20 as core


def row(address,age,**dynamic):
    return core.Cell(**dict(zip(core.STATIC,rom.record(address))),
                     address=address,age=age,**dynamic)


def neighborhood(site,age,updates=None):
    updates=updates or {}
    return tuple(row((site+offset)%core.Q,age,
                     **updates.get((site+offset)%core.Q,{}))
                 for offset in core.NEIGHBORHOOD)


def check(*,flag1_value=0x5A,flag2_value=0xA5):
    if not all(isinstance(value,int) and 0<=value<1<<64
               for value in (flag1_value,flag2_value)):
        raise ValueError('two complete physical flag Hold words required')
    started=time.perf_counter()
    pos=rom.FIRST_SITE
    state={name:0 for name in core.CONTROL}
    fetches=[]
    emissions=[]
    turns=0
    for tick in range(500000):
        age=dual.EARLY_RUN_STOP+tick+1
        c=row(pos,age,head=1,**state)
        if core.halted(c):
            halt_tick=tick
            break
        moving_right=state['direction']==core.RIGHT
        if moving_right:
            if (c.phase==core.FETCH and c.index==c.pc and
                    c.kind==core.SEND):
                fetches.append((c.pc,tick,pos))
            if (c.phase==core.TRANSMIT and c.kind==core.MEM and
                    c.index==c.ra):
                emissions.append((c.pc,tick,pos,c.rb,c.rd))
            next_state=core.advance(c)
            state.update(next_state)
            if c.last:
                state['direction']=core.LEFT
                turns+=1
            else:pos=(pos+1)%core.Q
        elif c.first:
            state.update(core.reflect_left(c))
            state['direction']=core.RIGHT
            turns+=1
        else:pos=(pos-1)%core.Q
    else:raise AssertionError('short holder SEND program failed to halt')
    if ([pc for pc,_,_ in fetches]!=list(range(10)) or
            [pc for pc,_,_,_,_ in emissions]!=list(range(10))):
        raise AssertionError(('wrong program path',fetches,emissions))
    literal_fetches=literal_emissions=literal_receipts=0
    latest_delivery=0
    packet_intervals=[]
    for pc,fetch_tick,instruction in fetches:
        after=core._word_step(neighborhood(
            instruction+1,dual.EARLY_RUN_STOP+fetch_tick+1,
            {instruction:dict(head=1,phase=core.FETCH,pc=pc,
                              direction=core.RIGHT)}))
        if (after.head!=1 or after.phase!=core.TRANSMIT or
                after.ra!=(rom.FLAG2_HOLD if pc<5 else rom.FLAG1_HOLD)):
            raise AssertionError(('literal instruction fetch',pc))
        literal_fetches+=1
    for pc,tick,source,target,direction in emissions:
        expected_source=rom.FLAG2_HOLD if pc<5 else rom.FLAG1_HOLD
        expected_target=pc+1 if pc<5 else core.Q-5+pc-5
        expected_direction=core.LEFT if pc<5 else core.RIGHT
        if (source,target,direction)!=(expected_source,expected_target,
                                       expected_direction):
            raise AssertionError(('wrong SEND operands',pc))
        value=flag2_value if pc<5 else flag1_value
        age=dual.EARLY_RUN_STOP+tick+1
        launch=core._word_step(neighborhood(
            source,age,{source:dict(head=1,phase=core.TRANSMIT,pc=pc,
                                    direction=core.RIGHT,ra=source,
                                    rb=target,rd=direction,data=value)}))
        lane='lp' if direction==core.LEFT else 'rp'
        packet={field:getattr(launch,lane+'_'+field)
                for field in ('target','data','remaining','valid')}
        if packet!=dict(target=target,data=value,remaining=0,valid=1):
            raise AssertionError(('literal packet launch',pc,packet))
        literal_emissions+=1
        carrier=(target+1 if direction==core.LEFT else target-1)%core.Q
        updates={carrier:{lane+'_'+field:word
                          for field,word in packet.items()}}
        arrival=core._word_step(neighborhood(target,age,updates))
        if arrival.data!=value or getattr(arrival,lane+'_valid'):
            raise AssertionError(('literal packet receipt',pc))
        literal_receipts+=1
        distance=((source-target) if direction==core.LEFT else
                  (target-source))%core.Q
        latest_delivery=max(latest_delivery,tick+distance)
        phase=(source+tick if direction==core.LEFT else source-tick)%core.Q
        for prior_direction,prior_phase,start,stop in packet_intervals:
            if (direction==prior_direction and phase==prior_phase and
                    tick<stop and start<tick+distance):
                raise AssertionError(('same-track SEND packet collision',pc))
        packet_intervals.append((direction,phase,tick,tick+distance))
    assert halt_tick<holder_stage3_budget()
    return dict(passed=True,send_instructions=len(fetches),
                emitted_packets=len(emissions),
                literal_fetch_steps=literal_fetches,
                literal_emit_steps=literal_emissions,
                literal_receive_steps=literal_receipts,
                head_turns=turns,
                last_head_halt_tick=halt_tick,
                last_boundary_data_delivery_tick=latest_delivery,
                fixed_current_stage3_budget=holder_stage3_budget(),
                flag2_hold=rom.FLAG2_HOLD,flag1_hold=rom.FLAG1_HOLD,
                flag1_data=flag1_value,flag2_data=flag2_value,
                packet_phase_intervals_checked=len(packet_intervals),
                first_site=rom.FIRST_SITE,last_site=rom.LAST_SITE,
                max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                seconds=time.perf_counter()-started,
                limitation='Symbolic single-head path with literal local '
                           'endpoints; no full holder ring, repaired faults, '
                           'or U≈2^20 work period.')


def holder_stage3_budget():
    from gacsca.fixed_rule import stream28_dual_holder_rule20 as holder
    return holder.ACTIVE_ENDS[2]-dual.EARLY_RUN_STOP


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    result=check()
    result['source_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    print(json.dumps(result,indent=2))
    if args.output:
        if args.output.exists():raise FileExistsError(args.output)
        args.output.write_text(json.dumps(result,indent=2)+'\n')
