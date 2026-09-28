"""Complete same-time zero-flag coherent image validation; no transitions."""
import numpy as np
from . import compact16_holder_rule as f,compact16_holder_program as p,compact16_holder_records as q
from . import compact16_holder_literal_cone as cone


def logical(raw):
    if not isinstance(raw,np.ndarray) or raw.dtype!=np.uint64 or raw.ndim!=2 or raw.shape[1]!=f.FIELDS or not 0<len(raw)<=64*f.Q or len(raw)%f.Q:raise ValueError('bounded complete physical colonies required')
    for k,(_,width) in enumerate(f.SCHEMA):
        if width<64 and np.any(raw[:,k]>=np.uint64(1<<width)):raise ValueError('raw word outside fixed alphabet')
    age=int(raw[0,f.COL['age']])
    if not 0<=age<f.U or np.any(raw[:,f.COL['age']]!=age):raise ValueError('uniform legal clock required')
    if not np.array_equal(raw[:,f.COL['address']],np.arange(len(raw))%f.Q):raise ValueError('canonical Address required')
    if not np.array_equal(raw,cone.normalize(raw.copy())):raise ValueError('fixed projected metadata required')
    for name in ('f1','f2',*(f'w{k}_{n}' for k in range(5) for n in ('wf1','wf2'))):
        if np.any(raw[:,f.COL[name]]):raise ValueError('zero physical flags and Wf required')
    for d in f.OFFSETS:
        for name,_ in f.PROCEDURE:
            if not np.array_equal(raw[:,f.COL[f's{d+2}_{name}']],np.roll(raw[:,f.COL[f's2_{name}']],-d)):raise ValueError('complete coherent procedures required')
        if not np.array_equal((raw[:,f.COL['signal']]>>np.uint64(d+2))&np.uint64(1),np.roll((raw[:,f.COL['signal']]>>np.uint64(2))&np.uint64(1),-d)):raise ValueError('coherent Signals required')
    out=np.zeros((len(raw),len(q.SCHEMA)),dtype=np.uint64)
    for name,_ in q.SCHEMA:
        source='s2_'+name if name in dict(f.PROCEDURE) else 'w2_'+name if name in ('wf1','wf2') else name
        out[:,q.COL[name]]=raw[:,f.COL[source]]
    address=out[:,q.COL['address']];g=p.layout()
    if np.any(out[(address>=g.memory_count)&(address<f.Q-5),q.COL['data']]):raise ValueError('non-MEM Data must be zero')
    return out
