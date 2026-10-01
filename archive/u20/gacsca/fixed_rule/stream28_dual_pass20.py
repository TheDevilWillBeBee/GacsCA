"""One fixed local successor invoking the encoded 8Q evaluator twice.

The early invocation follows the first three-history vote. It captures the
same protected Data sources, runs the same spatial gate/packet rule, and
commits only the Flag1/Flag2 Hold outputs. The later invocation is the existing
full stage-five pass. A short encoded holder SEND ROM exists, but a complete
physical U-period and successive decoded upper steps remain to be checked.
"""
from dataclasses import replace

from . import spatial_epoch8 as evaluator
from . import stream28_dual_compact_vote20 as previous
from . import stream28_dual_holder_rule20 as holder
from . import stream28_spatial_overlay20 as overlay

Q,U,WIDTH,FIELDS,NEIGHBORHOOD=(getattr(previous,name) for name in
                               ('Q','U','WIDTH','FIELDS','NEIGHBORHOOD'))
Cell=previous.Cell
encode_cell=previous.encode_cell
decode_cell=previous.decode_cell

EARLY_SUPPRESS_START=holder.VOTE_AGES[0]
EARLY_CAPTURE_AGE=EARLY_SUPPRESS_START+1
EARLY_RUN_START=EARLY_CAPTURE_AGE+1
EARLY_RUN_STOP=EARLY_RUN_START+evaluator.PERIOD
# Fixed output-bank geometry of the three-history layout. The description is
# recompiled if this fixed-rule choice changes; there is no depth dispatch.
EARLY_FLAG_HOLD_ADDRESSES=(2496,2498)
assert EARLY_RUN_STOP<holder.ACTIVE_ENDS[2]


def local_step(neighbors):
    if len(neighbors)!=len(NEIGHBORHOOD):
        raise ValueError('exact radius-seven neighborhood required')
    old=neighbors[7]
    age=old.holder.age
    result=previous.local_step(neighbors)
    if age==EARLY_RUN_STOP:
        clear=(result.holder.f1 and
               result.holder.address!=old.holder.address)
        heads={f's{slot}_head':1
               for slot in range(5)
               if not clear and
               getattr(old.holder,f'p{slot+1}_first')}
        return (Cell(replace(result.holder,**heads),result.evaluator)
                if heads else result)
    if not EARLY_SUPPRESS_START<=age<EARLY_RUN_STOP:
        return result
    next_holder=replace(result.holder,
                        **{f's{slot}_head':0 for slot in range(5)})
    spatial=tuple(row.evaluator for row in neighbors)
    if age==EARLY_CAPTURE_AGE:
        value=(holder.corrected(tuple(row.holder for row in neighbors),
                                0,'data')
               if spatial[7].kind==evaluator.SOURCE else 0)
        next_spatial=overlay._reset_evaluator(spatial[7],value)
    elif EARLY_RUN_START<=age<EARLY_RUN_STOP:
        next_spatial=evaluator.local_step(spatial[6:9])
        commits={}
        for offset in range(-2,3):
            old_output=spatial[7+offset]
            if (old_output.kind!=evaluator.OUTPUT or old_output.done or
                    old_output.address not in EARLY_FLAG_HOLD_ADDRESSES):
                continue
            new_output=(next_spatial if offset==0 else
                        evaluator.local_step(spatial[6+offset:9+offset]))
            if new_output.done:
                commits[f's{offset+2}_data']=new_output.source_value
        if commits and not (next_holder.f1 and
                            next_holder.address!=old.holder.address):
            next_holder=replace(next_holder,**commits)
    else:next_spatial=spatial[7]
    return Cell(next_holder,next_spatial)
