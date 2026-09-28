"""Bounded physical initialization and complete-state comparison for CUDA packets.

No host transition is applied to a running GPU state. Diagnostic comparison
covers all Data and every explicit live controller, packet and Signal record.
"""
import numpy as np
from . import retimed_holder_cpu_events as events,retimed_holder_cpu_gather as cpu
from . import retimed_holder_cpu_profile as profile
from . import retimed_holder_resident_gather as gpu,retimed_holder_resident_period as resident
from . import retimed_holder_projected as r,retimed_holder_rule as f,retimed_holder_program as p
from . import retimed_holder_quotient as q,retimed_holder_packed as packed


def records(state):
    if type(state) not in (events.World,cpu.World,profile.World):raise ValueError('canonical supported physical CPU state required')
    result=[{} for _ in range(state.n)]
    def row(col,at):return result[col].setdefault(at,dict(address=at))
    for col in range(state.n):
        if state.heads[col,0]:row(col,int(state.where[col])).update(zip(events.CONTROL,map(int,state.heads[col])))
        elif np.any(state.heads[col]):raise ValueError('inactive controller residue')
    for pos,track,target,data,remaining in getattr(state,'packets',()):
        col,at=divmod(int(pos),f.Q);prefix='lp' if track==0 else 'rp'
        row(col,at).update({prefix+'_'+name:value for name,value in zip(('target','data','remaining','valid'),(int(target),int(data),int(remaining),1))})
    for col,right in enumerate(getattr(state,'right',())):
        if right:
            for at in range(f.Q-5,f.Q):row(col,at)['signal']=1<<(f.Q-1-at)
    return result


def from_cpu(state,*,device_budget=32*1024**2):
    explicit=records(state);g=p.layout()
    if not 1<=state.n<=64:raise ValueError('bounded colony count required')
    if np.any(state.data[:,g.memory_count:f.Q-5]):raise ValueError('non-MEM Data outside canonical domain')
    if any(len(rows)>resident.SLOTS for rows in explicit):raise ValueError('sparse capacity exceeded')
    world=gpu.World((r.Cell(),)*state.n,device_budget=device_budget)
    try:
        for col,entries in enumerate(explicit):
            raw=np.zeros((1,resident.SLOTS,packed.WORDS),dtype=np.uint64)
            if entries:
                cells=tuple(q.Cell(data=int(state.data[col,at]),**values) for at,values in sorted(entries.items()))
                raw[0,:len(cells)]=packed.pack(q.array_from_cells(cells))
            count=np.array([len(entries)],dtype=np.uint64)
            if world.lib.rp_initial(world.handle,col,1,resident.pointer(raw),resident.pointer(count)):raise RuntimeError('sparse upload failed')
            bank=np.ascontiguousarray(np.concatenate((state.data[col,:g.memory_count],state.data[col,f.Q-5:])))
            if world.lib.rp_bank(world.handle,col,resident.pointer(bank)):raise RuntimeError('Data upload failed')
        if world.lib.rp_restore_age(world.handle,state.age):raise ValueError('unsupported physical context')
        world.age=world.epoch=state.age;world.time=state.time
        return world
    except BaseException:world.close();raise


def compare(world,state):
    expected=records(state);bank,raw,counts=world.snapshot();g=p.layout()
    np.testing.assert_array_equal(bank,np.concatenate((state.data[:,:g.memory_count],state.data[:,f.Q-5:]),axis=1))
    assert (world.colonies,world.age,world.time)==(state.n,state.age,state.time)
    fields=('address',*resident.ACTIVE)
    for col,entries in enumerate(expected):
        assert int(counts[col])==len(entries),(col,counts[col],len(entries))
        unpacked=packed.unpack(raw[col,:int(counts[col])])
        for actual,(at,values) in zip(unpacked,sorted(entries.items())):
            for name in fields:assert int(actual[q.COL[name]])==values.get(name,0),(col,at,name,int(actual[q.COL[name]]),values.get(name,0))
    return bank,raw,counts
