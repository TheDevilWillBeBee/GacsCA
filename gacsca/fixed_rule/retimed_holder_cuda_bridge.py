"""Bounded host initialization of the exact zero-context CPU state on GPU.

This transfers existing physical words only. It does not evaluate an upper
transition, change depth, or insert a state during GPU evolution.
"""
import numpy as np
from . import retimed_holder_resident_independent as gpu,retimed_holder_resident_period as resident
from . import retimed_holder_cpu_events as cpu,retimed_holder_rule as f
from . import retimed_holder_program as p,retimed_holder_projected as r
from . import retimed_holder_quotient as q,retimed_holder_packed as packed


def from_cpu(state, *, device_budget=32*1024**2):
    if not isinstance(state,cpu.World) or not 1<=state.n<=15:
        raise ValueError('bounded canonical CPU state required')
    for name in ('flags','right','left','packets'):
        if hasattr(state,name) and np.any(getattr(state,name)):
            raise ValueError('initial CUDA bridge requires zero context/mail')
    g = p.layout()
    if np.any(state.data[:,g.memory_count:f.Q-5]):
        raise ValueError('non-MEM Data must be zero')
    world = gpu.World((r.Cell(),)*state.n,device_budget=device_budget)
    try:
        for col in range(state.n):
            rows = np.zeros((1,resident.SLOTS,packed.WORDS),dtype=np.uint64)
            count = int(bool(state.heads[col,0]))
            if count:
                address = int(state.where[col])
                control = {name:int(value) for name,value in zip(cpu.CONTROL,state.heads[col])}
                record = q.Cell(address=address,data=int(state.data[col,address]),**control)
                rows[0,0] = packed.pack(q.array_from_cells((record,)))[0]
            elif np.any(state.heads[col]):
                raise ValueError('inactive controller residues are unsupported')
            counts = np.array([count],dtype=np.uint64)
            if world.lib.rp_initial(world.handle,col,1,resident.pointer(rows),resident.pointer(counts)):
                raise RuntimeError('physical sparse-state upload failed')
            bank = np.ascontiguousarray(np.concatenate((state.data[col,:g.memory_count],state.data[col,f.Q-5:])))
            if world.lib.rp_bank(world.handle,col,resident.pointer(bank)):
                raise RuntimeError('physical Data-bank upload failed')
        if world.lib.rp_restore_age(world.handle,state.age):
            raise ValueError('unsupported physical clock/context')
        world.age = world.epoch = state.age
        world.time = state.time
        return world
    except BaseException:
        world.close()
        raise
