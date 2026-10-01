"""Literal fixed-radius successor: corrected U20 F plus physical static fetch.

The additional 144 bits are a new fixed alphabet. The existing evaluator
layout has not yet been recompiled for this successor, so this module is a
candidate local transition, not an established self-simulation.
"""
from dataclasses import dataclass,replace

from .. import stream28_dual_pass20 as base_rule
from .. import stream28_dual_holder_rule20 as holder
from .lookup_bus import ADDRESS_SOURCE,Q


BUS_SCHEMA=(('lookup_enable',1),('lookup_neighbor',4),('lookup_field',9),
            ('lookup_address',13),('broadcast_valid',1),
            ('broadcast_value',13),('packet_valid',1),('packet_source',15),
            ('packet_target',13),('packet_field',9),('packet_fetched',1),
            ('packet_value',64))
FIELDS=base_rule.FIELDS+len(BUS_SCHEMA)
WIDTH=base_rule.WIDTH+sum(width for _,width in BUS_SCHEMA)
NEIGHBORHOOD=base_rule.NEIGHBORHOOD
Q,U=base_rule.Q,base_rule.U


@dataclass(frozen=True)
class Cell:
    base:base_rule.Cell
    lookup_enable:int=0
    lookup_neighbor:int=0
    lookup_field:int=0
    lookup_address:int=0
    broadcast_valid:int=0
    broadcast_value:int=0
    packet_valid:int=0
    packet_source:int=0
    packet_target:int=0
    packet_field:int=0
    packet_fetched:int=0
    packet_value:int=0

    def __post_init__(self):
        if not isinstance(self.base,base_rule.Cell):
            raise ValueError('complete raw U20 base cell required')
        for name,width in BUS_SCHEMA:
            value=getattr(self,name)
            if not isinstance(value,int) or not 0<=value<1<<width:
                raise ValueError(f'{name} outside fixed lookup alphabet')


def encode_cell(cell):
    return base_rule.encode_cell(cell.base)+tuple(getattr(cell,name)
                                                  for name,_ in BUS_SCHEMA)


def decode_cell(words):
    if len(words)!=FIELDS:raise ValueError('all successor raw fields required')
    return Cell(base_rule.decode_cell(words[:base_rule.FIELDS]),
                *map(int,words[base_rule.FIELDS:]))


def _packet(c,left):
    """Packet after one transition, before end-of-lap valid clearing."""
    age=c.base.holder.age
    if age==0:
        return dict(packet_valid=0,packet_source=c.packet_source,
                    packet_target=c.packet_target,packet_field=c.packet_field,
                    packet_fetched=c.packet_fetched,packet_value=c.packet_value)
    if age==Q:
        return dict(packet_valid=c.lookup_enable,
                    packet_source=c.base.holder.address,
                    packet_target=(c.lookup_address+c.lookup_neighbor-7)%Q,
                    packet_field=c.lookup_field,
                    packet_fetched=0,packet_value=0)
    if Q<age<=2*Q:
        p=dict(packet_valid=left.packet_valid,
               packet_source=left.packet_source,
               packet_target=left.packet_target,
               packet_field=left.packet_field,
               packet_fetched=left.packet_fetched,
               packet_value=left.packet_value)
        if p['packet_valid'] and not p['packet_fetched'] and p['packet_target']==c.base.holder.address:
            p['packet_value']=(encode_cell(c)[p['packet_field']]
                               if p['packet_field']<FIELDS else 0)
            p['packet_fetched']=1
        return p
    return {name:getattr(c,name) for name in
            ('packet_valid','packet_source','packet_target',
             'packet_field','packet_fetched','packet_value')}


def local_step(neighbors):
    if len(neighbors)!=15:raise ValueError('exact radius-seven neighborhood required')
    c=neighbors[7]
    age=c.base.holder.age
    h=c.base.holder
    out=base_rule.local_step(tuple(row.base for row in neighbors))
    changes={}
    if age==0:
        launch=h.address==ADDRESS_SOURCE
        changes['broadcast_valid']=int(launch)
        if launch:
            value=h.s2_data&(Q-1)
            changes.update(broadcast_value=value,lookup_address=value)
    elif 0<age<Q:
        left=neighbors[6]
        changes.update(broadcast_valid=left.broadcast_valid,
                       broadcast_value=left.broadcast_value)
        if left.broadcast_valid:changes['lookup_address']=left.broadcast_value
    elif age==Q:changes['broadcast_valid']=0
    packet=_packet(c,neighbors[6])
    changes.update(packet)
    if age==2*Q+1:
        updates={}
        for d in holder.OFFSETS:
            src=neighbors[7+d]
            if (src.packet_valid and src.packet_fetched and
                    src.packet_source==(h.address+d)%Q):
                updates[f's{d+2}_data']=src.packet_value
        if updates:out=replace(out,holder=replace(out.holder,**updates))
        changes['packet_valid']=0
    return replace(c,base=out,**changes)
