"""Fixed local stage-five coupling of stream28 holders and spatial evaluation.

This is an executable *successor rule candidate*, not a self-description
closure. All state fields, stage ages, and the radius-seven transition are
fixed independently of encoded hierarchy depth. The spatial circuit is
initial data. During the stage-five window its SOURCE cells capture the
corrected local Data words, and each accepted OUTPUT packet writes the
corresponding Data value to all five holder replicas.
"""
from dataclasses import dataclass,replace

from . import stream28_holder_rule as holder
from . import spatial_epoch as evaluator
from . import spatial_codec

Q=holder.Q
U=holder.U
WIDTH=holder.WIDTH+evaluator.WIDTH
FIELDS=holder.FIELDS+spatial_codec.FIELDS
NEIGHBORHOOD=holder.NEIGHBORHOOD
CAPTURE_AGE=holder.RESET_AGES[4]+1
RUN_START=CAPTURE_AGE+1
RUN_STOP=RUN_START+evaluator.PERIOD


@dataclass(frozen=True)
class Cell:
    holder:holder.Cell
    evaluator:evaluator.Cell

    def __post_init__(self):
        if not (isinstance(self.holder,holder.Cell) and
                isinstance(self.evaluator,evaluator.Cell)):
            raise ValueError('complete holder and evaluator state required')


def encode_cell(cell):
    return holder.encode_cell(cell.holder)+spatial_codec.encode_cell(cell.evaluator)


def decode_cell(words):
    if len(words)!=FIELDS:raise ValueError('all holder and evaluator fields required')
    return Cell(holder.decode_cell(words[:holder.FIELDS]),
                spatial_codec.decode_cell(words[holder.FIELDS:]))


def _reset_evaluator(row,source_value=0):
    # Spatial routing addresses are immutable physical ROM geometry. A
    # repairable holder address can change independently under a local fault.
    updates=dict(age=0,active_slot=0,
                 arg0=0,arg1=0,ready=0,result=0,done=0,
                 source_value=source_value,mail=evaluator.EMPTY_PACKET,
                 collision=0)
    if row.kind==evaluator.GATE:
        spec=row.gates[0]
        updates.update(arg0=spec.preload0,arg1=spec.preload1,
                       ready=spec.preload_ready,source_value=0)
    return replace(row,**updates)


def local_step(neighbors):
    if len(neighbors)!=len(NEIGHBORHOOD):
        raise ValueError('exact radius-seven neighborhood required')
    base=tuple(cell.holder for cell in neighbors)
    spatial=tuple(cell.evaluator for cell in neighbors)
    center=base[7]
    age=center.age
    next_holder=holder.local_step(base)
    if holder.RESET_AGES[4]<=age<RUN_STOP:
        # The old serial evaluator head is suppressed by the physical rule.
        next_holder=replace(next_holder,
                            **{f's{slot}_head':0 for slot in range(5)})
    if age==CAPTURE_AGE:
        input_value=(holder.corrected(base,0,'data')
                     if spatial[7].kind==evaluator.SOURCE else 0)
        next_spatial=_reset_evaluator(spatial[7],input_value)
    elif RUN_START<=age<RUN_STOP:
        next_spatial=evaluator.local_step(spatial[6:9])
        commits={}
        for offset in range(-2,3):
            old=spatial[7+offset]
            if old.kind!=evaluator.OUTPUT or old.done:continue
            new=(next_spatial if offset==0 else
                 evaluator.local_step(spatial[6+offset:9+offset]))
            if new.done:
                commits[f's{offset+2}_data']=new.source_value
        if commits and not (next_holder.f1 and
                            next_holder.address!=center.address):
            next_holder=replace(next_holder,**commits)
    else:next_spatial=spatial[7]
    return Cell(next_holder,next_spatial)
