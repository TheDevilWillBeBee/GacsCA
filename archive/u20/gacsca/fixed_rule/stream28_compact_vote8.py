"""Fixed in-place history-vote successor with the 8Q spatial evaluator.

The static MEM ``a`` bit VOTE_SELF marks the middle of three adjacent history
cells. At either vote age it replaces that cell's Data by the bitwise majority
of corrected Data at left, self, and right. All five simulated copies are
updated by the same radius-seven local transition. The ordinary ROM has no
VOTE_SELF sites; a new three-history ROM still needs placement and closure.
"""
from dataclasses import replace

from . import stream28_holder_core as core
from . import stream28_holder_rule as holder
from . import stream28_spatial_overlay8 as previous

VOTE_SELF=1<<7
Q,U,WIDTH,FIELDS,NEIGHBORHOOD=(getattr(previous,name) for name in
                               ('Q','U','WIDTH','FIELDS','NEIGHBORHOOD'))
CAPTURE_AGE,RUN_START,RUN_STOP=(getattr(previous,name) for name in
                                ('CAPTURE_AGE','RUN_START','RUN_STOP'))
Cell=previous.Cell
encode_cell=previous.encode_cell
decode_cell=previous.decode_cell


def majority3(a,b,c):
    return (a&b)|(a&c)|(b&c)


def local_step(neighbors):
    if len(neighbors)!=len(NEIGHBORHOOD):
        raise ValueError('exact radius-seven neighborhood required')
    result=previous.local_step(neighbors)
    center=neighbors[7].holder
    if center.age not in holder.VOTE_AGES:return result
    if result.holder.f1 and result.holder.address!=center.address:return result
    cells=tuple(row.holder for row in neighbors)
    updates={}
    for offset in holder.OFFSETS:
        static=offset+3
        if (getattr(center,f'p{static}_kind')!=core.MEM or
                not getattr(center,f'p{static}_a')&VOTE_SELF):
            continue
        values=(holder.corrected(cells,offset+j,'data')
                for j in (-1,0,1))
        updates[f's{offset+2}_data']=majority3(*values)
    return (Cell(replace(result.holder,**updates),result.evaluator)
            if updates else result)
