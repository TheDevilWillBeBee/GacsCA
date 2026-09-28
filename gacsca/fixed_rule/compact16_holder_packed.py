"""Lossless bit packing of the coherent physical execution representation.

This changes storage only. The physical holder alphabet and description remain
unchanged; every raw logical controller/mail/geometry field is retained.
"""
import numpy as np
from . import compact16_holder_records as q

WIDTH=sum(width for _,width in q.SCHEMA)
WORDS=(WIDTH+63)//64
OFFSETS=tuple(sum(width for _,width in q.SCHEMA[:i]) for i in range(len(q.SCHEMA)))


def pack(array):
    if not isinstance(array,np.ndarray) or array.dtype!=np.uint64 or array.ndim<2 or array.shape[-1]!=len(q.SCHEMA):raise ValueError('complete uint64 logical records required')
    out=np.zeros((*array.shape[:-1],WORDS),dtype=np.uint64)
    for i,((name,width),offset) in enumerate(zip(q.SCHEMA,OFFSETS)):
        value=array[...,i]
        if width<64 and np.any(value>=np.uint64(1<<width)):raise ValueError('outside field width: '+name)
        word,shift=divmod(offset,64);out[...,word]|=value<<np.uint64(shift)
        if shift+width>64:out[...,word+1]|=value>>np.uint64(64-shift)
    return out


def unpack(array):
    if not isinstance(array,np.ndarray) or array.dtype!=np.uint64 or array.ndim<2 or array.shape[-1]!=WORDS:raise ValueError('complete packed uint64 records required')
    if WIDTH%64 and np.any(array[...,-1]>>np.uint64(WIDTH%64)):raise ValueError('nonzero padding bits')
    out=np.empty((*array.shape[:-1],len(q.SCHEMA)),dtype=np.uint64)
    for i,((_,width),offset) in enumerate(zip(q.SCHEMA,OFFSETS)):
        word,shift=divmod(offset,64);value=array[...,word]>>np.uint64(shift)
        if shift+width>64:value=value|(array[...,word+1]<<np.uint64(64-shift))
        if width<64:value=value&np.uint64((1<<width)-1)
        out[...,i]=value
    return out
