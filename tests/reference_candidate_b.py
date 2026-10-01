"""Frozen independent reference for Gray's section 5.2 local structure.

This is `maintenance` from the archived U20 candidate
(`archive/u20/gacsca/fixed_rule/stream28_holder_core.py`, commit 9bfd530), copied
verbatim with only the fields it reads, so that `MaintenanceTest` keeps checking
`gacsca/maintenance.py` against code written independently of it, without importing
the archive. Q = 2^13, U = 2^28 as in that candidate.
"""
from collections import namedtuple

Q = 1 << 13
U = 1 << 28
Cell = namedtuple('Cell', 'address age f1 f2 wf1 wf2')


def maintenance(cells):
    """Independent scalar transcription, with explicit candidate-B Flag2 erasure."""
    c=cells[5];r={j:cells[j+5] for j in range(-5,6)}
    def majority(values,default):
        for candidate in values:
            if values.count(candidate)>=3:return candidate,True
        return default,False
    adjusted={j:(r[j].address-j)%Q for j in (*range(-5,0),*range(1,6))}
    v,exists=majority([adjusted[j] for j in range(1,6)],c.address)
    inside={j:exists and 0<=v+j<Q for j in range(-5,6)}
    age_r,age_exists=majority([r[j].age for j in range(1,6)],c.age)
    age_l,_=majority([r[j].age for j in range(-1,-6,-1)],c.age)
    incons=(not exists or not age_exists or
            sum(inside[j] and r[j].address!=(v+j)%Q for j in range(-1,-6,-1))>=3 or
            sum(inside[j] and r[j].age!=age_r for j in range(-1,-6,-1))>=3)
    flags=sum(inside[j] and r[j].f1 for j in range(1,6))
    f1=int(incons or sum(inside[j] and r[j].wf1 for j in range(-5,6))>=3 or
           flags>=3 or (c.f1 and flags>=2))
    d3=not exists and (age_l+1)%16==0
    d4=sum(inside[j] and r[j].wf2 for j in range(-5,6))>=3
    left_flags=[r[j].f2 for j in range(-1,-6,-1)]
    on=sum(inside[j] and r[j].f2 for j in range(-1,-6,-1))>=4 or (f1 and sum(left_flags)>=4) or d3 or d4
    erase=(not f1 and sum(inside[j] and r[j].f2 for j in range(-1,-6,-1))<=1) or (f1 and not any(left_flags))
    f2=int((d3 or d4 or not erase) if c.f2 else on)
    addr_l,_=majority([adjusted[j] for j in range(-1,-6,-1)],c.address)
    vote_right=exists and (not f1 or f2)
    return dict(address=v if vote_right else addr_l,age=((age_r if vote_right else age_l)+1)%U,f1=f1,f2=f2)
