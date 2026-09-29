"""Lossless packed storage for all 154 raw small-holder fields, including ROM."""
import numpy as np
from . import retimed_holder_rule as f
WIDTH=f.WIDTH
WORDS=(WIDTH+63)//64
OFFSETS=tuple(sum(w for _,w in f.SCHEMA[:i]) for i in range(f.FIELDS))


def pack(array):
    if not isinstance(array,np.ndarray) or array.dtype!=np.uint64 or array.ndim!=2 or array.shape[1]!=f.FIELDS:
        raise ValueError('complete uint64 raw physical rows required')
    result=np.zeros((len(array),WORDS),dtype=np.uint64)
    for i,((name,width),offset) in enumerate(zip(f.SCHEMA,OFFSETS)):
        value=array[:,i]
        if width<64 and np.any(value>=np.uint64(1<<width)):raise ValueError('field outside alphabet: '+name)
        word,shift=divmod(offset,64);result[:,word]|=value<<np.uint64(shift)
        if shift+width>64:result[:,word+1]|=value>>np.uint64(64-shift)
    return result


def unpack(array):
    if not isinstance(array,np.ndarray) or array.dtype!=np.uint64 or array.ndim!=2 or array.shape[1]!=WORDS:
        raise ValueError('complete packed raw rows required')
    if WIDTH%64 and np.any(array[:,-1]>>np.uint64(WIDTH%64)):raise ValueError('nonzero raw padding')
    result=np.empty((len(array),f.FIELDS),dtype=np.uint64)
    for i,((_,width),offset) in enumerate(zip(f.SCHEMA,OFFSETS)):
        word,shift=divmod(offset,64);value=array[:,word]>>np.uint64(shift)
        if shift+width>64:value=value|(array[:,word+1]<<np.uint64(64-shift))
        if width<64:value=value&np.uint64((1<<width)-1)
        result[:,i]=value
    return result
