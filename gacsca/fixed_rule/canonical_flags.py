"""Printed maintenance on canonical Address/uniform Age with arbitrary flags.

A source-derived domain lemma for a future flag-wave executor. This is not wired
into any current accelerator, and it does not support noncanonical geometry.
"""
from . import clock_rule as rule


def transition(cells):
    if len(cells)!=11:raise ValueError('radius-five neighborhood required')
    c=cells[5];a=c.address
    if any(x.address!=(a+j-5)%rule.Q or x.age!=c.age for j,x in enumerate(cells)):
        raise ValueError('canonical Address and uniform Age required')
    inside=lambda j:0<=a+j<rule.Q
    right_flags=sum(cells[j+5].f1 for j in range(1,6) if inside(j))
    f1=int(sum(cells[j+5].wf1 for j in range(-5,6) if inside(j))>=3 or right_flags>=3 or (c.f1 and right_flags>=2))
    left=[cells[j+5].f2 for j in range(-1,-6,-1)]
    d4=sum(cells[j+5].wf2 for j in range(-5,6) if inside(j))>=3
    on=sum(cells[j+5].f2 for j in range(-1,-6,-1) if inside(j))>=4 or (f1 and sum(left)>=4) or d4
    erase=(not f1 and all(not inside(j) or cells[j+5].f2 for j in range(-1,-6,-1))) or (f1 and not any(left))
    f2=int((d4 or not erase) if c.f2 else on)
    return dict(address=a,age=(c.age+1)%rule.U,f1=f1,f2=f2)
