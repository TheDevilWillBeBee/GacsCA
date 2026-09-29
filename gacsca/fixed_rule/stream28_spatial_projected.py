"""Projected combined-state interface for the fixed spatial successor.

Holder and evaluator static ROM are supplied from fixed address-indexed data.
The 3062 evolving bits include every holder controller replica and every
spatial operand, result, latch, mail, and collision field. This module is a
diagnostic projected transition, not a closed own-ROM construction.
"""
from dataclasses import dataclass

from . import stream28_holder_projected as holder
from . import stream28_spatial_overlay as physical
from . import spatial_projected as evaluator
from . import spatial_epoch

WIDTH=holder.WIDTH+evaluator.WIDTH
FIELDS=len(holder.SCHEMA)+evaluator.FIELDS
NEIGHBORHOOD=physical.NEIGHBORHOOD
assert (WIDTH,FIELDS)==(3062,119)


@dataclass(frozen=True)
class Cell:
    holder:holder.Cell
    evaluator:evaluator.Cell

    def __post_init__(self):
        if not (isinstance(self.holder,holder.Cell) and
                isinstance(self.evaluator,evaluator.Cell)):
            raise ValueError('complete projected combined state required')


def encode_cell(cell):
    return holder.encode_cell(cell.holder)+evaluator.encode_cell(cell.evaluator)


def decode_cell(words):
    if len(words)!=FIELDS:raise ValueError('all projected controller/evaluator words required')
    count=len(holder.SCHEMA)
    return Cell(holder.decode_cell(words[:count]),
                evaluator.decode_cell(words[count:]))


def project(cell):
    return Cell(holder.project(cell.holder),evaluator.project(cell.evaluator))


def lift(cell,static_evaluator):
    if not isinstance(cell,Cell) or not isinstance(static_evaluator,spatial_epoch.Cell):
        raise ValueError('projected state and fixed evaluator ROM cell required')
    return physical.Cell(holder.lift(cell.holder),
                         evaluator.lift(cell.evaluator,static_evaluator))


def local_step(neighbors,static_evaluator_neighbors):
    if (len(neighbors)!=len(NEIGHBORHOOD) or
            len(static_evaluator_neighbors)!=len(NEIGHBORHOOD)):
        raise ValueError('exact radius-seven projected neighborhood required')
    full=tuple(lift(dynamic,static) for dynamic,static in
               zip(neighbors,static_evaluator_neighbors))
    return project(physical.local_step(full))
