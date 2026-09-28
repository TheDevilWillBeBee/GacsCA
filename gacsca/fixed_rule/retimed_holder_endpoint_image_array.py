"""Independent diagnostic vector reconstruction of complete canonical images.

This is read-only host analysis, never a simulated transition implementation.
"""
import numpy as np
from . import retimed_holder_rule as f,retimed_holder_program as p,retimed_holder_core as c
from .retimed_holder_terminal_reference import metadata


def render(bank,signals,age,*,max_bytes=256*1024**2):
    g=p.layout()
    if not isinstance(bank,np.ndarray) or bank.dtype!=np.uint64 or bank.ndim!=2 or bank.shape[1]!=g.memory_count+5 or not len(bank):raise ValueError('complete uint64 bank required')
    n=len(bank)
    if not isinstance(signals,np.ndarray) or signals.dtype!=np.uint64 or signals.shape!=(n,2) or np.any(signals>1):raise ValueError('Boolean localized Signal bits required')
    if age not in (0,f.U-1) or n*f.Q*f.FIELDS*8>max_bytes:raise ValueError('endpoint Age and bounded reconstruction required')
    result=np.zeros((n*f.Q,f.FIELDS),dtype=np.uint64);addresses=np.tile(np.arange(f.Q,dtype=np.uint64),n)
    rom=np.array(metadata(),dtype=np.uint64)
    for offset in f.STATIC_OFFSETS:
        for selector,name in enumerate(c.STATIC):result[:,f.COL[f'p{offset+3}_{name}']]=rom[(addresses+(f.Q+offset))%f.Q,selector]
    data=np.zeros((n,f.Q),dtype=np.uint64);data[:,:g.memory_count]=bank[:,:g.memory_count];data[:,-5:]=bank[:,g.memory_count:]
    for offset in f.OFFSETS:result[:,f.COL[f's{offset+2}_data']]=np.roll(data.ravel(),-offset)
    result[:,f.COL['address']]=addresses;result[:,f.COL['age']]=age
    pattern=np.array([16,8,4,2,1],dtype=np.uint64)
    for col in range(n):
        result[col*f.Q+np.arange(1,6),f.COL['signal']]=signals[col,0]*pattern
        result[col*f.Q+np.arange(f.Q-5,f.Q),f.COL['signal']]=signals[col,1]*pattern
    return result
