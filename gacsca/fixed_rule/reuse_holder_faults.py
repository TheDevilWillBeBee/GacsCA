"""Finite causal-patch diagnostics for physical holder faults.

Only ordinary projected transitions evolve states. Trimming seven sites per
edge keeps every reported output independent of artificial patch boundaries.
Comparing the entire fault cone then certifies global equality outside/inside it.
"""
import numpy as np
from . import parallel_holder_rule as f,reuse_holder_projected as r,parallel_holder_native as native

RADIUS=7


def advance_patch(cells):
    if len(cells)<=2*RADIUS:raise ValueError('causal patch needs a retained interior')
    raw=tuple(r.lift(cell) for cell in cells)
    out=native.step_ring(raw)
    return tuple(r.project(cell) for cell in out[RADIUS:-RADIUS])


def recovery(read,faults,ticks):
    if not faults or not isinstance(ticks,int) or ticks<1:raise ValueError('nonempty faults and positive finite time required')
    lo,hi=min(faults)-2*RADIUS*ticks,max(faults)+2*RADIUS*ticks
    clean=tuple(read(pos) for pos in range(lo,hi+1));dirty=list(clean)
    for pos,cell in faults.items():dirty[pos-lo]=cell
    dirty=tuple(dirty);frames=[(clean,dirty)];start=lo
    for _ in range(ticks):clean=advance_patch(clean);dirty=advance_patch(dirty);start+=RADIUS;frames.append((clean,dirty))
    assert start==min(faults)-RADIUS*ticks and start+len(clean)-1==max(faults)+RADIUS*ticks
    mismatch=[(start+i,[name for name,_ in r.SCHEMA if getattr(a,name)!=getattr(b,name)]) for i,(a,b) in enumerate(zip(clean,dirty)) if a!=b]
    return dict(restored=not mismatch,steps=ticks,final_start=start,initial_start=lo,mismatch=mismatch,frames=frames)
