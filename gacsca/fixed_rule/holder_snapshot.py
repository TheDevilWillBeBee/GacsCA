"""Lossless endpoint storage of the physical coherent-state representation.

All control/mail/flag words must actually be zero. Data and Signal are preserved;
Address and uniform Age are reconstructed exactly, with no upper-state encoding.
There is no depth parameter and no simulated transition in this module.
"""
import numpy as np
from . import holder_rule as f,holder_program as p,holder_quotient as q,holder_projected as r


def addresses():return np.array([*range(p.layout().computation_cells),*range(f.Q-5,f.Q)],dtype=np.uint64)


def cold(cells):
    g=p.layout();out=np.zeros((len(cells),g.computation_cells+5,len(q.SCHEMA)),dtype=np.uint64);out[:,:,q.COL['address']]=addresses()
    for i,cell in enumerate(cells):out[i,g.info,q.COL['data']]=f.encode_cell(r.lift(cell))
    return out.reshape(-1,len(q.SCHEMA))


def collapse(world):
    if world.pending:raise ValueError('pending physical mail cannot be dropped')
    g=p.layout();a=world._cores.reshape(world.colonies,g.computation_cells+5,len(q.SCHEMA))
    for name,_ in q.SCHEMA:
        if name in ('data','signal'):continue
        expected=addresses()[None,:] if name=='address' else world.epoch if name=='age' else 0
        if np.any(a[:,:,q.COL[name]]!=expected):raise ValueError('noncanonical or nonzero endpoint field: '+name)
    return dict(data=np.ascontiguousarray(a[:,:,q.COL['data']]),signal=np.ascontiguousarray(a[:,:,q.COL['signal']]),age=(world.epoch+world.time)%f.U)


def expand(snapshot):
    data,signal=snapshot['data'],snapshot['signal'];age=snapshot['age'];rows=p.layout().computation_cells+5
    if data.dtype!=np.uint64 or signal.dtype!=np.uint64 or data.shape!=signal.shape or data.ndim!=2 or data.shape[1]!=rows or not len(data):raise ValueError('complete Data/Signal endpoint required')
    if not isinstance(age,int) or not 0<=age<f.U or np.any(signal>31):raise ValueError('outside physical alphabet')
    a=np.zeros((*data.shape,len(q.SCHEMA)),dtype=np.uint64);a[:,:,q.COL['address']]=addresses();a[:,:,q.COL['age']]=age;a[:,:,q.COL['data']]=data;a[:,:,q.COL['signal']]=signal
    return a.reshape(-1,len(q.SCHEMA))
