"""Bounded initialization of one full physical colony, with complete raw Info.

Its repetitions are a convenient GPU reference background, not an assertion
that repeating a colony is the same as initializing arbitrary hierarchy depth.
"""
import numpy as np
from . import small_holder_rule as f,small_holder_core as c,small_holder_program as p
from . import small_holder_projected as r


def encoded_background(parent):
    if not isinstance(parent,r.Cell):raise ValueError('complete projected parent required')
    address=np.arange(f.Q,dtype=np.uint64);rom=np.zeros((f.Q,len(c.STATIC)),dtype=np.uint64)
    base=p.base_rom();rom[:len(base)]=base
    for a in range(len(base),f.Q):rom[a]=[c.fallback(a,j) for j in range(len(c.STATIC))]
    out=np.zeros((f.Q,f.FIELDS),dtype=np.uint64)
    for d in f.STATIC_OFFSETS:
        indices=(address+np.uint64(d%f.Q))%np.uint64(f.Q)
        for j,name in enumerate(c.STATIC):out[:,f.COL[f'p{d+3}_{name}']]=rom[indices,j]
    data=np.zeros(f.Q,dtype=np.uint64);data[np.array(p.layout().info)]=f.encode_cell(r.lift(parent))
    for d in f.OFFSETS:out[:,f.COL[f's{d+2}_data']]=np.roll(data,-d)
    out[:,f.COL['address']]=address
    return out
