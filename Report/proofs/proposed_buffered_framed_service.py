"""Explicit buffered-code-frame revision, separate from G17 and SP15.

Only coded service words change: convert packet tag to position tag+6
instead of tag+1 and accept code positions0..452 instead of0..447.
Packet state/selection, guard6 and the twelve-history-rank schema need
no extra input offsets. A packet with integer origin r now seeds coded
origin r-5 and frame[r-5,r+447]. All38 state bits are retained.
The conditional repair theorem is J103; no own CA/ROM or iid theorem is
supplied by this standalone module.
"""
from functools import lru_cache
import inspect
import proposed_framed_service as original

COLONY_SIZE = 448
LEFT_BUFFER = 5
FRAME_SIZE = COLONY_SIZE + LEFT_BUFFER


@lru_cache(None)
def generated_build():
    source = inspect.getsource(original.build)
    old = "(POSITION_BITS - TAG_BITS))], 1)"
    new = f"(POSITION_BITS - TAG_BITS))], {1+LEFT_BUFFER})"
    assert source.count(old) == 1
    source = source.replace(old,new)
    namespace = dict(original.__dict__,Q=FRAME_SIZE)
    exec(compile(source,'<explicit buffered service frame, not SP15>','exec'),namespace)
    return namespace['build'],source


def build(n,cells):
    result = generated_build()[0](n,cells)
    result['service_force'] = n.OR(result['service_force'],result['packet_any_cohort'])
    return result
