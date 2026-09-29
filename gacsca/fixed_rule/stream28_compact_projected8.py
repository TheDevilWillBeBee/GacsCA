"""Projected evolving state of the fixed 8Q compact-vote successor.

Static holder and spatial ROM rows are separate address-indexed data inputs.
The diagnostic transition only verifies the projection relation; supplying
those rows is not an implemented self-referential lookup mechanism.
"""
from dataclasses import dataclass

from . import spatial_epoch8
from . import spatial_projected8 as evaluator
from . import stream28_holder_projected as holder
from . import stream28_holder_rule as raw_holder
from . import stream28_compact_vote8 as physical

WIDTH=holder.WIDTH+evaluator.WIDTH
FIELDS=len(holder.SCHEMA)+evaluator.FIELDS
NEIGHBORHOOD=physical.NEIGHBORHOOD
assert (WIDTH,FIELDS)==(3063,119)


@dataclass(frozen=True)
class Cell:
    holder:holder.Cell
    evaluator:evaluator.Cell

    def __post_init__(self):
        if not (isinstance(self.holder,holder.Cell) and
                isinstance(self.evaluator,evaluator.Cell)):
            raise ValueError('complete projected holder/evaluator state')


def encode_cell(cell):
    return holder.encode_cell(cell.holder)+evaluator.encode_cell(cell.evaluator)


def decode_cell(words):
    if len(words)!=FIELDS:raise ValueError('all 119 evolving words required')
    count=len(holder.SCHEMA)
    return Cell(holder.decode_cell(words[:count]),
                evaluator.decode_cell(words[count:]))


def project(cell):
    return Cell(holder.project(cell.holder),evaluator.project(cell.evaluator))


def lift(cell,static_holder,static_evaluator):
    if (not isinstance(cell,Cell) or
            not isinstance(static_holder,raw_holder.Cell) or
            not isinstance(static_evaluator,spatial_epoch8.Cell)):
        raise ValueError('projected state and both static ROM rows required')
    static={name:getattr(static_holder,name)
            for name,_ in raw_holder.STATIC}
    dynamic=dict(zip((name for name,_ in holder.SCHEMA),
                     holder.encode_cell(cell.holder)))
    return physical.Cell(raw_holder.Cell(**static,**dynamic),
                         evaluator.lift(cell.evaluator,static_evaluator))


def local_step(neighbors,static_holder_neighbors,static_evaluator_neighbors):
    if (len(neighbors)!=len(NEIGHBORHOOD) or
            len(static_holder_neighbors)!=len(NEIGHBORHOOD) or
            len(static_evaluator_neighbors)!=len(NEIGHBORHOOD)):
        raise ValueError('exact radius-seven static/dynamic neighborhood')
    full=tuple(lift(dynamic,hstatic,sstatic)
               for dynamic,hstatic,sstatic in
               zip(neighbors,static_holder_neighbors,
                   static_evaluator_neighbors))
    return project(physical.local_step(full))
