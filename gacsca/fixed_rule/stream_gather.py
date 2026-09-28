"""Fixed-width, radius-one streaming gather feasibility rule.

This is an isolated *candidate communication component*, not a replacement
for packed28_holder's physical rule or a closed self-simulator.  A site has
one static Info field/mask, one static history acceptance tag, and one
moving word lane per direction.  The transition depends on exactly three
old cells.  Initial data select the 689 current-rule words to gather; no
host transition supplies moving packets after initialization.

The deterministic phase assignment makes each directed packet trajectory
unique modulo Q.  This is a healthy canonical-domain collision argument;
fault tolerance and self-description of this new component remain open.
"""
from dataclasses import dataclass, replace
from functools import lru_cache

from . import packed28_holder_program as reference
from . import packed28_holder_rule as raw

Q=8192
FIELDS=raw.FIELDS
STAGES=3
FRAME=16*Q
PERIOD=4*FRAME
WIRE_LIMIT=15*FIELDS
NO_FIELD=FIELDS
NO_WIRE=WIRE_LIMIT
NO_STAGE=STAGES
OFFSETS=tuple(range(-7,8))
assert Q==raw.Q and WIRE_LIMIT<Q


@dataclass(frozen=True)
class Packet:
    valid:int=0
    wire:int=0
    hops:int=0
    stage:int=0
    value:int=0

    def __post_init__(self):
        if self.valid not in (0,1) or not 0<=self.wire<WIRE_LIMIT or not 0<=self.hops<=7 or not 0<=self.stage<STAGES or not 0<=self.value<1<<64:
            raise ValueError('packet outside fixed finite alphabet')


EMPTY=Packet()


@dataclass(frozen=True)
class Cell:
    address:int=0
    age:int=0
    info_field:int=NO_FIELD
    emit_mask:int=0
    accept_wire:int=NO_WIRE
    accept_stage:int=NO_STAGE
    info_value:int=0
    history_value:int=0
    history_valid:int=0
    right:Packet=EMPTY
    left:Packet=EMPTY
    collision:int=0

    def __post_init__(self):
        if not (0<=self.address<Q and 0<=self.age<PERIOD and
                0<=self.info_field<=NO_FIELD and 0<=self.emit_mask<1<<15 and
                0<=self.accept_wire<=NO_WIRE and 0<=self.accept_stage<=NO_STAGE and
                0<=self.info_value<1<<64 and 0<=self.history_value<1<<64 and
                self.history_valid in (0,1) and self.collision in (0,1) and
                isinstance(self.right,Packet) and isinstance(self.left,Packet)):
            raise ValueError('cell outside fixed finite alphabet')
        if self.info_field==NO_FIELD and self.emit_mask:
            raise ValueError('only Info sites may emit')


def wire(offset,field):
    if offset not in OFFSETS or not 0<=field<FIELDS:raise ValueError('invalid wire')
    return (offset+7)*FIELDS+field


def direction(offset):
    return 1 if offset<0 else -1  # Local Info lies right of all history targets.


def launch_time(source,offset,field):
    """New-state tick 1..Q; distinct wires have distinct trajectory phases."""
    number=wire(offset,field)
    return 1+((source-number)%Q if direction(offset)==1 else (number-source)%Q)


def _incoming(packet, crossed):
    if not packet.valid:return EMPTY
    return replace(packet,hops=packet.hops-int(crossed and packet.hops>0))


def _emissions(c):
    stage,old_tick=divmod(c.age,FRAME)
    if stage>=STAGES or c.info_field==NO_FIELD:return EMPTY,EMPTY
    right,left=EMPTY,EMPTY
    for index,offset in enumerate(OFFSETS):
        if not c.emit_mask&(1<<index) or old_tick+1!=launch_time(c.address,offset,c.info_field):continue
        packet=Packet(1,wire(offset,c.info_field),abs(offset),stage,c.info_value)
        if direction(offset)==1:
            if right.valid:raise AssertionError('two same-direction launches at one site/tick')
            right=packet
        else:
            if left.valid:raise AssertionError('two same-direction launches at one site/tick')
            left=packet
    return right,left


def local_step(neighbors):
    """One complete physical step from precisely (left, center, right)."""
    if len(neighbors)!=3:raise ValueError('exact radius-one neighborhood required')
    left,c,right=neighbors
    moving_right=_incoming(left.right,left.address==Q-1 and c.address==0)
    moving_left=_incoming(right.left,right.address==0 and c.address==Q-1)
    result=c.history_value;valid=c.history_valid;collision=c.collision

    def receive(packet):
        nonlocal result,valid,collision
        if not packet.valid:return packet
        if (packet.hops==0 and packet.wire==c.accept_wire and
                packet.stage==c.accept_stage):
            if valid and result!=packet.value:collision=1
            result=packet.value;valid=1
            return EMPTY
        return packet

    moving_right=receive(moving_right)
    moving_left=receive(moving_left)
    emission_right,emission_left=_emissions(c)
    if moving_right.valid and emission_right.valid:collision=1
    if moving_left.valid and emission_left.valid:collision=1
    return replace(c,age=(c.age+1)%PERIOD,history_value=result,
                   history_valid=valid,right=moving_right if moving_right.valid else emission_right,
                   left=moving_left if moving_left.valid else emission_left,
                   collision=collision)


@lru_cache(maxsize=1)
def static_layout():
    """Compile only the initial static data of the existing own-rule gather."""
    layout=reference.layout()
    masks=[0]*FIELDS
    accepts={}
    for number in layout.gathered_inputs:
        neighbor,field=divmod(number,FIELDS);offset=neighbor-7
        masks[field]|=1<<(offset+7)
        for stage in range(STAGES):
            address=layout.history(stage,offset,field)
            assert address not in accepts
            accepts[address]=(number,stage)
    sources={address:field for field,address in enumerate(layout.info)}
    assert set(sources).isdisjoint(accepts)
    assert len(accepts)==STAGES*len(layout.gathered_inputs)
    return tuple(masks),accepts,sources


def initial_cell(address,info_words):
    if not 0<=address<Q or len(info_words)!=FIELDS:raise ValueError('complete raw Info required')
    masks,accepts,sources=static_layout()
    field=sources.get(address,NO_FIELD)
    number,stage=accepts.get(address,(NO_WIRE,NO_STAGE))
    return Cell(address=address,info_field=field,
                emit_mask=masks[field] if field<FIELDS else 0,
                accept_wire=number,accept_stage=stage,
                info_value=int(info_words[field]) if field<FIELDS else 0)


def arrival_time(source,target,offset,field):
    travel=abs(offset)*Q+(target-source if direction(offset)==1 else source-target)
    if travel<=0:raise ValueError('packet target precedes its source')
    return launch_time(source,offset,field)+travel


def schedule_certificate():
    """Exact straight-line paths implied by local_step on canonical geometry."""
    layout=reference.layout();masks,accepts,sources=static_layout()
    rows=[];phases={1:set(),-1:set()}
    for number in layout.gathered_inputs:
        neighbor,field=divmod(number,FIELDS);offset=neighbor-7
        source=layout.info[field];sign=direction(offset)
        phase=((source-launch_time(source,offset,field)) if sign==1
               else (source+launch_time(source,offset,field)))%Q
        assert phase not in phases[sign],('same-direction trajectory collision',number)
        phases[sign].add(phase)
        for stage in range(STAGES):
            target=layout.history(stage,offset,field)
            assert accepts[target]==(number,stage)
            deadline=arrival_time(source,target,offset,field)
            assert deadline<FRAME,('missed 16Q active stage',number,stage,deadline)
            rows.append((stage,number,offset,field,source,target,launch_time(source,offset,field),deadline))
    assert len(rows)==STAGES*len(layout.gathered_inputs)
    return dict(Q=Q,active_budget=FRAME,stages=STAGES,required_words=len(layout.gathered_inputs),
                local_words=sum((number//FIELDS)==7 for number in layout.gathered_inputs),
                nonlocal_words=sum((number//FIELDS)!=7 for number in layout.gathered_inputs),
                packets_per_colony=len(rows),last_delivery=max(row[-1] for row in rows),
                phase_counts={str(sign):len(values) for sign,values in phases.items()},
                maximum_emissions_per_Info_site=max(mask.bit_count() for mask in masks),
                rows=tuple(rows))
