"""Exact finite physical causal-window execution using the full CUDA rule.

No macrostep shortcut or upper transition is used. Each step shrinks the valid
interval by radius seven; state outside that interval is explicitly uncertified.
A fresh bounded resident bank is uploaded each tick. This is a correctness
reference for future persistent commits, not a practical depth-two executor.
"""
from dataclasses import dataclass
import numpy as np
from . import small_holder_rule as f
from .small_holder_bank import Snapshot
from .small_holder_bank_cuda import Resident, MAX_BATCH


@dataclass(frozen=True)
class Result:
    positions: tuple
    cells: tuple
    physical_ticks: int
    local_evaluations: int
    max_device_bytes: int
    final_storage_bytes: int


def run(snapshot, start, count, ticks):
    """Return [start,start+count) modulo ring after ``ticks`` literal updates."""
    if not isinstance(snapshot,Snapshot):raise ValueError('complete initial physical snapshot required')
    if any(type(x) is not int for x in (start,count,ticks)) or count<1 or ticks<0 or not 0<=start<snapshot.sites:
        raise ValueError('valid interval and finite nonnegative ticks required')
    radius=max(abs(j) for j in f.NEIGHBORHOOD)
    if count+2*radius*ticks>min(snapshot.sites,4096):
        raise ValueError('causal window requires distinct sites and at most 4096 cells')
    lo,hi=start-radius*ticks,start+count+radius*ticks
    state=snapshot; evaluations=0; peak=0
    for _ in range(ticks):
        lo+=radius;hi-=radius
        positions=tuple(x%snapshot.sites for x in range(lo,hi))
        output=[]
        with Resident(state) as world:
            peak=max(peak,world.device_bytes)
            for a in range(0,len(positions),MAX_BATCH):output.append(world.evaluate(positions[a:a+MAX_BATCH]))
        rows=np.concatenate(output);evaluations+=len(positions)
        # All raw fields at every newly certified site replace previous values.
        # Outside these positions the initial base is stale and never queried
        # by the next shrinking cone. Retain no false global-current-state API.
        order=np.argsort(np.array(positions,dtype=np.uint64))
        keys=(np.array(positions,dtype=np.uint64)[order,None]*np.uint64(f.FIELDS)+np.arange(f.FIELDS,dtype=np.uint64)[None,:]).reshape(-1)
        values=np.ascontiguousarray(rows[order].reshape(-1))
        state=Snapshot(snapshot.colonies,snapshot.age,snapshot.data,snapshot.logical_keys,snapshot.logical_values,keys,values)
    positions=tuple(x%snapshot.sites for x in range(start,start+count))
    return Result(positions,tuple(state.cell(x) for x in positions),ticks,evaluations,peak,state.storage_bytes)
