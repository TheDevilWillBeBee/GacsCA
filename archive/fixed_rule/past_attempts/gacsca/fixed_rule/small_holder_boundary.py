"""Ordinary full-controller periodic cap data for the fixed holder rule.

This homogeneous cap is initial data under the same transition. It includes
one-step reset/vote head pulses in the +1 backup. It is not an organized colony
or a fault-tolerant boundary, and does not constitute deeper dynamic execution.
"""
from . import small_holder_rule as f,small_holder_core as c,small_holder_projected as r,small_holder_program as p


def pulse_entries():
    g=p.layout();return tuple(zip((a+1 for a in c.RESET_AGES),g.entries))+((c.VOTE_AGES[0]+1,g.entries[4]),)


def cell(age=0):
    if not isinstance(age,int) or not 0<=age<f.U:raise ValueError('physical clock value required')
    hits=[pc for at,pc in pulse_entries() if at==age]
    return r.Cell(address=f.Q-1,age=age,f1=1,f2=1,s3_head=int(bool(hits)),s3_pc=hits[0] if hits else 0)
