"""Three-history encoded gather layout for the compact-vote own-F inputs.

This is initialization data and an analytical route schedule. It deliberately
does not invent a self-ROM for the 390 address-indexed static dependencies.
"""
from dataclasses import dataclass
from functools import lru_cache

from . import spatial_codec
from . import stream28_holder_core as core
from . import stream28_holder_rule as holder
from . import stream28_spatial_projected as projected
from . import stream28_compact_vote as physical
from . import stream28_compact_vote_optimized as optimized
from .wordcode_and import LIT

RESERVED=8
HISTORY_SLOTS=3
SPATIAL_DYNAMIC_FIELDS=(1,3,*range(spatial_codec.FIELDS-12,
                                    spatial_codec.FIELDS))
assert len(SPATIAL_DYNAMIC_FIELDS)==14


@dataclass(frozen=True)
class Route:
    stage:int
    neighbor:int
    field:int
    wire_tag:int
    source:int
    target:int
    direction:int
    launch:int
    arrival:int
    phase:int


@dataclass(frozen=True)
class Layout:
    gathered:tuple
    static_inputs:tuple
    info:tuple
    hold:tuple
    routes:tuple
    memory_after_banks:int

    def history(self,stage,neighbor,field):
        return RESERVED+HISTORY_SLOTS*self.gathered.index((neighbor,field))+stage

    def metadata(self,address):
        """Only MEM metadata needed by the already local stream/vote rules."""
        if not 0<=address<self.memory_after_banks:
            raise ValueError('site outside compact gather and state banks')
        if address<RESERVED:return dict(kind=core.MEM,index=address,a=31)
        history_end=RESERVED+HISTORY_SLOTS*len(self.gathered)
        if address<history_end:
            slot,stage=divmod(address-RESERVED,HISTORY_SLOTS)
            neighbor,field=self.gathered[slot]
            wire=neighbor*core.STREAM_FIELDS+field
            return dict(kind=core.MEM,index=address,
                        a=(1<<(stage+1))-1|
                          (physical.VOTE_SELF if stage==1 else 0),
                        d=core.STREAM_TAG_MARK+
                          (stage<<core.STREAM_TAG_SHIFT)+wire)
        slot,bank=divmod(address-history_end,2)
        mask=sum(1<<neighbor for neighbor,field in self.gathered
                 if field==slot)
        if bank==0:
            return dict(kind=core.MEM,index=address,
                        a=core.INFO,
                        b=((slot+1)<<core.STREAM_FIELD_SHIFT)|mask)
        return dict(kind=core.MEM,index=address,a=31)


@lru_cache(maxsize=1)
def build():
    program=optimized.build()
    stride=physical.FIELDS
    used={wire for opcode,a,b in program.operations if opcode!=LIT
          for wire in (a,b) if wire<program.inputs}
    used.update(wire for wire in program.outputs if wire<program.inputs)
    gathered=set()
    static=[]
    for wire in sorted(used):
        neighbor,field=divmod(wire,stride)
        if field<holder.FIELDS:
            if field<len(holder.STATIC):static.append(wire)
            else:gathered.add((neighbor,field-len(holder.STATIC)))
        else:
            spatial_field=field-holder.FIELDS
            if spatial_field in SPATIAL_DYNAMIC_FIELDS:
                gathered.add((neighbor,len(holder.SCHEMA)-len(holder.STATIC)+
                              SPATIAL_DYNAMIC_FIELDS.index(spatial_field)))
            else:static.append(wire)
    gathered=tuple(sorted(gathered))
    assert len(gathered)==761 and len(static)==390
    info_start=RESERVED+HISTORY_SLOTS*len(gathered)
    info=tuple(info_start+2*field for field in range(projected.FIELDS))
    hold=tuple(site+1 for site in info)
    routes=[]
    phases={core.RIGHT:set(),core.LEFT:set()}
    for stage in range(3):
        for slot,(neighbor,field) in enumerate(gathered):
            offset=neighbor-7
            wire=neighbor*core.STREAM_FIELDS+field
            source=info[field]
            target=RESERVED+HISTORY_SLOTS*slot+stage
            if offset<0:
                direction=core.RIGHT
                launch=2+((source-wire)%physical.Q)
                distance=-offset*physical.Q+target-source
                phase=(source-launch)%physical.Q
            else:
                direction=core.LEFT
                launch=2+((wire-source)%physical.Q)
                distance=offset*physical.Q+source-target
                phase=(source+launch)%physical.Q
            if distance<=0 or launch+distance>=core.STREAM_FRAME:
                raise AssertionError(('gather deadline',stage,neighbor,field))
            if phase in phases[direction] and stage==0:
                raise AssertionError(('mail phase collision',direction,phase))
            if stage==0:phases[direction].add(phase)
            routes.append(Route(stage,neighbor,field,wire,source,target,
                                direction,launch,launch+distance,phase))
    result=Layout(gathered,tuple(static),info,hold,tuple(routes),
                  info_start+2*projected.FIELDS)
    assert len(routes)==3*len(gathered)
    assert max(hold)<physical.Q-5
    assert core.STREAM_FIELDS>=projected.FIELDS
    return result
