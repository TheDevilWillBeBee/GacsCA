"""Diagnostic projection of fixed spatial static ROM from evolving state.

The projected rule is defined only after supplying one fixed static layout by
physical address. This is the ProgramBit-style interface for a future closed
self-description. It does not by itself prove that the layout describes this
new combined rule or that the projected rule is self-simulated.
"""
from dataclasses import dataclass

from . import spatial_epoch as physical

WIDTHS=(15,2,64,64,64,2,64,1,1,13,1,2,64,1)
WIDTH=sum(WIDTHS)
FIELDS=len(WIDTHS)
assert WIDTH==358


@dataclass(frozen=True)
class Cell:
    age:int=0
    active_slot:int=0
    source_value:int=0
    arg0:int=0
    arg1:int=0
    ready:int=0
    result:int=0
    done:int=0
    mail:physical.Packet=physical.EMPTY_PACKET
    collision:int=0

    def __post_init__(self):
        encode_cell(self)


def encode_cell(cell):
    packet=cell.mail
    words=(cell.age,cell.active_slot,cell.source_value,
           cell.arg0,cell.arg1,cell.ready,cell.result,cell.done,
           packet.valid,packet.target,packet.arg_slot,
           packet.target_gate_slot,packet.value,cell.collision)
    if any(not isinstance(value,int) or not 0<=value<1<<width
           for value,width in zip(words,WIDTHS)):
        raise ValueError('projected spatial field outside fixed width')
    return words


def decode_cell(words):
    if len(words)!=FIELDS:raise ValueError('every evolving spatial field required')
    if any(not isinstance(value,int) or not 0<=value<1<<width
           for value,width in zip(words,WIDTHS)):
        raise ValueError('projected spatial field outside fixed width')
    return Cell(*words[:8],physical.Packet(*words[8:13]),words[13])


def project(cell):
    return Cell(cell.age,cell.active_slot,cell.source_value,
                cell.arg0,cell.arg1,cell.ready,cell.result,cell.done,
                cell.mail,cell.collision)


def lift(dynamic,static):
    if not isinstance(dynamic,Cell) or not isinstance(static,physical.Cell):
        raise ValueError('projected state and fixed static cell required')
    return physical.replace(static,age=dynamic.age,
                            active_slot=dynamic.active_slot,
                            source_value=dynamic.source_value,
                            arg0=dynamic.arg0,arg1=dynamic.arg1,
                            ready=dynamic.ready,result=dynamic.result,
                            done=dynamic.done,mail=dynamic.mail,
                            collision=dynamic.collision)


def local_step(dynamic_neighbors,static_neighbors):
    if len(dynamic_neighbors)!=3 or len(static_neighbors)!=3:
        raise ValueError('exact radius-one projected neighborhood required')
    old=tuple(lift(dynamic,static) for dynamic,static in
              zip(dynamic_neighbors,static_neighbors))
    return project(physical.local_step(old))
