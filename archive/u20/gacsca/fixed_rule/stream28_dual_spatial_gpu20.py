"""Exact CUDA radius-one encoded evaluator used by the fixed U20 rule.

The static gate/route rows and all mutable evaluator registers reside on GPU.
The host selects only a physical tick count and may read diagnostic state.
"""
import ctypes
from functools import lru_cache
import hashlib
from pathlib import Path
import subprocess

import numpy as np

from . import spatial_codec8 as codec
from . import spatial_epoch8 as rule


@lru_cache(maxsize=1)
def library():
    source=Path(__file__).with_suffix('.cu')
    identity=hashlib.sha256(source.read_bytes()+b'nvcc-O2-sm80-spatial-v1').hexdigest()[:20]
    build=(Path(__file__).resolve().parents[2]/'figs/fixed_rule/build'/
           ('stream28_dual_spatial_gpu20_'+identity))
    build.mkdir(parents=True,exist_ok=True)
    target=build/'spatial.so'
    if not target.exists():
        with (build/'build.log').open('w') as log:
            subprocess.run(['/usr/local/cuda/bin/nvcc','-O2','-std=c++17',
                            '-arch=sm_80','--shared','-Xcompiler','-fPIC',
                            str(source),'-o',str(target)],
                           stdout=log,stderr=subprocess.STDOUT,check=True)
    lib=ctypes.CDLL(str(target))
    ptr=ctypes.POINTER(ctypes.c_uint64)
    handle=ctypes.c_void_p
    for name,args in {'se_create':[ctypes.c_size_t,ptr,ctypes.c_uint64,
                                   ctypes.POINTER(handle),ptr],
                      'se_run':[handle,ctypes.c_uint64],
                      'se_read':[handle,ptr,ptr,ptr,ptr],
                      'se_free':[handle]}.items():
        fn=getattr(lib,name)
        fn.argtypes=args
        fn.restype=None if name=='se_free' else ctypes.c_int
    return lib


def _ptr(array):return array.ctypes.data_as(ctypes.POINTER(ctypes.c_uint64))


class World:
    def __init__(self,rows,*,device_budget=1024**3):
        if not isinstance(rows,np.ndarray) or rows.dtype!=np.uint64 or\
                rows.ndim!=2 or rows.shape[1]!=codec.FIELDS or len(rows)<3:
            raise ValueError('complete encoded spatial ring required')
        if type(device_budget) is not int or not 1<=device_budget<=80*1024**3:
            raise ValueError('explicit bounded device budget required')
        if any(np.any(rows[:,k]>=np.uint64(1<<width))
               for k,width in enumerate(codec.WIDTHS) if width<64):
            raise ValueError('word outside fixed spatial alphabet')
        if not np.all(rows[:,1]==rows[0,1]):
            raise ValueError('one physical evaluator Age required')
        if (rule.GATE_SLOTS,rule.ROUTE_SLOTS,codec.FIELDS)!=(3,38,267):
            raise AssertionError('CUDA spatial schema drift')
        self.initial=np.ascontiguousarray(rows)
        self.lib=library()
        self.handle=ctypes.c_void_p()
        bytes_used=ctypes.c_uint64()
        code=self.lib.se_create(len(rows),_ptr(self.initial),device_budget,
                                ctypes.byref(self.handle),
                                ctypes.byref(bytes_used))
        if code:raise RuntimeError(('CUDA spatial allocation failed',code))
        self.sites=len(rows)
        self.age=int(rows[0,1])
        self.time=0
        self.device_bytes=int(bytes_used.value)

    def run(self,ticks):
        if not self.handle or type(ticks) is not int or not 0<=ticks<=rule.PERIOD:
            raise ValueError('live world and bounded period required')
        code=self.lib.se_run(self.handle,ticks)
        if code:raise RuntimeError(('CUDA spatial transition failed',code))
        self.time+=ticks
        self.age=(self.age+ticks)%rule.PERIOD

    def read(self):
        if not self.handle:raise ValueError('closed world')
        dynamic=np.empty((self.sites,13),dtype=np.uint64)
        ages=np.empty(self.sites,dtype=np.uint64)
        values=np.empty(self.sites,dtype=np.uint64)
        counts=np.empty(2,dtype=np.uint64)
        code=self.lib.se_read(self.handle,_ptr(dynamic),_ptr(ages),
                              _ptr(values),_ptr(counts))
        if code:raise RuntimeError(('CUDA spatial readback failed',code))
        raw=self.initial.copy()
        raw[:,1]=self.age
        raw[:,3]=dynamic[:,0]
        raw[:,255:261]=dynamic[:,1:7]
        raw[:,261:266]=dynamic[:,8:13]
        raw[:,266]=dynamic[:,7]
        events=tuple((int(ages[i]),int(i),int(values[i]))
                     for i in np.flatnonzero(ages))
        return raw,events,tuple(map(int,counts))

    def close(self):
        if self.handle:self.lib.se_free(self.handle);self.handle=None

    def __enter__(self):return self
    def __exit__(self,*args):self.close()
