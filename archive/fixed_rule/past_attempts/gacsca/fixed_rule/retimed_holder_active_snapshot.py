"""Lossless diagnostics/restoration for canonical, zero-flag live checkpoints.

No transitions run here. All procedure/controller/mail fields are retained.
Restoration is limited to the late mail-free domain of the existing executor.
"""
import numpy as np
from . import retimed_holder_rule as f, retimed_holder_core as c
from . import retimed_holder_program as p, retimed_holder_quotient as q
from . import retimed_holder_packed as packed, retimed_holder_resident_period as period
from .retimed_holder_terminal_reference import metadata


def logical(snapshot, *, max_bytes=256*1024**2):
    g=p.layout();bank=snapshot['bank'];rows=snapshot['active_rows'];counts=snapshot['counts']
    if not isinstance(bank,np.ndarray) or bank.dtype!=np.uint64 or bank.ndim!=2 or bank.shape[1]!=g.memory_count+5 or not len(bank):raise ValueError('complete bank required')
    n=len(bank)
    if type(max_bytes) is not int or n*f.Q*(f.FIELDS+len(q.SCHEMA))*8>max_bytes:raise ValueError('bounded complete reconstruction required')
    for value,shape in ((rows,(n,period.SLOTS,len(q.SCHEMA))),(counts,(n,)),(snapshot['flags'],(n*f.Q//64,2)),(snapshot['signals'],(n,2))):
        if not isinstance(value,np.ndarray) or value.dtype!=np.uint64 or value.shape!=shape:raise ValueError('complete typed snapshot required')
    age=int(snapshot['age']);time=int(snapshot['time'])
    if not 0<=age<f.U or time<0 or time%f.U!=age or np.any(snapshot['flags']) or np.any(snapshot['signals']>1):raise ValueError('canonical zero-flag clock required')
    out=np.zeros((n*f.Q,len(q.SCHEMA)),dtype=np.uint64)
    out[:,q.COL['address']]=np.tile(np.arange(f.Q,dtype=np.uint64),n);out[:,q.COL['age']]=age
    for col in range(n):
        base=col*f.Q;out[base:base+g.memory_count,q.COL['data']]=bank[col,:g.memory_count]
        out[base+f.Q-5:base+f.Q,q.COL['data']]=bank[col,-5:]
        count=int(counts[col])
        if count>period.SLOTS or np.any(rows[col,count:]):raise ValueError('bounded normalized active rows required')
        part=rows[col,:count];packed.pack(part)
        addresses=part[:,q.COL['address']].astype(np.int64)
        if np.any(addresses>=f.Q) or (count>1 and np.any(np.diff(addresses)<=0)):raise ValueError('sorted unique canonical addresses required')
        if np.any(part[:,q.COL['age']]!=age) or np.any(part[:,[q.COL[x] for x in ('f1','f2','wf1','wf2')]]):raise ValueError('zero-flag normalized rows required')
        if not np.array_equal(part[:,q.COL['data']],out[base+addresses,q.COL['data']]):raise ValueError('active Data differs from bank')
        out[base+addresses]=part
        signals=np.zeros(f.Q,dtype=np.uint64);pattern=np.array([16,8,4,2,1],dtype=np.uint64)
        signals[1:6]=snapshot['signals'][col,0]*pattern;signals[-5:]=snapshot['signals'][col,1]*pattern
        if not np.array_equal(out[base:base+f.Q,q.COL['signal']],signals):raise ValueError('incomplete localized Signal records')
    return out


def render(snapshot, *, max_bytes=256*1024**2):
    source=logical(snapshot,max_bytes=max_bytes);out=np.zeros((len(source),f.FIELDS),dtype=np.uint64)
    addresses=source[:,q.COL['address']];rom=np.array(metadata(),dtype=np.uint64)
    for offset in f.STATIC_OFFSETS:
        for selector,name in enumerate(c.STATIC):out[:,f.COL[f'p{offset+3}_{name}']]=rom[(addresses+(f.Q+offset))%f.Q,selector]
    for name,_ in f.GEOMETRY:out[:,f.COL[name]]=source[:,q.COL[name]]
    for offset in f.OFFSETS:
        for name,_ in f.PROCEDURE:out[:,f.COL[f's{offset+2}_{name}']]=np.roll(source[:,q.COL[name]],-offset)
    return out


def restore(snapshot, *, device_budget=32*1024**2):
    """Upload the exact saved state; never compute or replace a transition."""
    from . import retimed_holder_resident_general as general, retimed_holder_projected as r
    logical(snapshot) # validate complete input before allocation or mutation
    age=int(snapshot['age']);rows=snapshot['active_rows'];counts=snapshot['counts']
    if age<f.WF_END+f.Q or np.any(rows[:,:,[q.COL[x] for x,_ in q.SCHEMA if x.startswith(('lp_','rp_'))]]):raise ValueError('late mail-free checkpoint required')
    world=general.World((r.Cell(),)*len(counts),device_budget=device_budget)
    try:
        for col,count in enumerate(counts):
            records=np.zeros((1,period.SLOTS,packed.WORDS),dtype=np.uint64);count=int(count)
            records[0,:count]=packed.pack(rows[col,:count]);sizes=np.array([count],dtype=np.uint64)
            core=world._core
            if core.lib.rp_initial(core.handle,col,1,period.pointer(records),period.pointer(sizes)):raise RuntimeError('controller upload failed')
            bank=np.ascontiguousarray(snapshot['bank'][col])
            if core.lib.rp_bank(core.handle,col,period.pointer(bank)):raise RuntimeError('Data bank upload failed')
        if core.lib.rp_restore_age(core.handle,age):raise ValueError('checkpoint outside resident domain')
        core.age=core.epoch=age;core.time=int(snapshot['time'])
        return world
    except BaseException:world.close();raise
