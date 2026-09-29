"""Complete 119-word evolving-state projection of the dual-pass rule.

Both static ROM rows are supplied as fixed address data by the diagnostic
caller. This module defines the decoding relation; it does not perform a
simulated transition for the physical evaluator circuit.
"""
from . import stream28_compact_projected8 as base
from . import stream28_dual_pass8 as physical

Cell=base.Cell
WIDTH=base.WIDTH
FIELDS=base.FIELDS
NEIGHBORHOOD=base.NEIGHBORHOOD
encode_cell=base.encode_cell
decode_cell=base.decode_cell
project=base.project
lift=base.lift


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
