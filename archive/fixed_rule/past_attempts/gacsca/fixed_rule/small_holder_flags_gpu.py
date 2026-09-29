"""Exact packed physical flags for canonical geometry and coherent fixed Signals.

No front shape is assumed. The unchanged rule is evaluated bit-parallel on GPU.
This projection alone does not evolve the computation fields.
"""
import ctypes
from functools import lru_cache
import hashlib
from pathlib import Path
import subprocess
import numpy as np
from . import small_holder_rule as f

WORDS=f.Q//64
GRAPH_TICKS=128
MAX_COLONIES=128


@lru_cache(maxsize=1)
def library():
    source=Path(__file__).with_suffix('.cu')
    header=''.join(f'#define {k} UINT64_C({v})\n' for k,v in dict(WORDS_PER_COLONY=WORDS,WF_START=f.WF_START,WF_END=f.WF_END,PERIOD=f.U,GRAPH_TICKS=GRAPH_TICKS).items())
    identity=hashlib.sha256(source.read_bytes()+header.encode()+b'nvcc-O2-sm80-flags-v1').hexdigest()[:20]
    directory=source.resolve().parents[2]/'figs/fixed_rule/build'/('small_holder_flags_'+identity);directory.mkdir(parents=True,exist_ok=True);target=directory/'flags.so'
    if not target.exists():
        (directory/'small_holder_flags_generated.h').write_text(header)
        with (directory/'build.log').open('w') as log:
            subprocess.run(['/usr/local/cuda/bin/nvcc','-O2','-std=c++17','-arch=sm_80','--shared','-Xcompiler','-fPIC','-I',str(directory),str(source),'-o',str(target)],check=True,stdout=log,stderr=subprocess.STDOUT)
    lib=ctypes.CDLL(str(target));ptr=ctypes.POINTER(ctypes.c_uint64);byte=ctypes.POINTER(ctypes.c_uint8);h=ctypes.c_void_p
    for name,args,result in (('sf_create',[ctypes.c_size_t,ctypes.c_uint64,byte,byte,ptr,ctypes.POINTER(h)],ctypes.c_int),('sf_free',[h],None),('sf_read',[h,ptr],ctypes.c_int),('sf_run',[h,ctypes.c_uint64],ctypes.c_int)):
        fn=getattr(lib,name);fn.argtypes=args;fn.restype=result
    return lib


class World:
    def __init__(self,right,left,*,age=f.WF_START-1,initial=None):
        self.right=tuple(right);self.left=tuple(left);self.colonies=len(self.right)
        if not 0<self.colonies<=MAX_COLONIES or len(self.left)!=self.colonies or any(type(x) is not int or x not in (0,1) for x in (*self.right,*self.left)):raise ValueError('bounded coherent Signal pairs required')
        if type(age) is not int or not f.WF_START-1<=age<f.U:raise ValueError('suffix Age required')
        if initial is None:initial=np.zeros((self.colonies*WORDS,2),dtype=np.uint64)
        if not isinstance(initial,np.ndarray) or initial.dtype!=np.uint64 or initial.shape!=(self.colonies*WORDS,2):raise ValueError('complete packed physical flags required')
        data=np.ascontiguousarray(initial);right=np.array(self.right,dtype=np.uint8);left=np.array(self.left,dtype=np.uint8)
        self.lib=library();self.handle=ctypes.c_void_p();byte=ctypes.POINTER(ctypes.c_uint8)
        code=self.lib.sf_create(self.colonies,age,right.ctypes.data_as(byte),left.ctypes.data_as(byte),data.ctypes.data_as(ctypes.POINTER(ctypes.c_uint64)),ctypes.byref(self.handle))
        if code:raise RuntimeError(f'flag allocation failed: {code}')
        self.age=age;self.time=0;self.device_bytes=32*self.colonies*WORDS+2*self.colonies
    def close(self):
        if self.handle:self.lib.sf_free(self.handle);self.handle=None
    def __enter__(self):return self
    def __exit__(self,*args):self.close()
    def read(self):
        if not self.handle:raise ValueError('closed flag world')
        out=np.empty((self.colonies*WORDS,2),dtype=np.uint64)
        code=self.lib.sf_read(self.handle,out.ctypes.data_as(ctypes.POINTER(ctypes.c_uint64)))
        if code:raise RuntimeError(f'flag read failed: {code}')
        return out
    def run(self,ticks):
        if not self.handle or type(ticks) is not int or not 0<=ticks<=f.U-self.age:raise ValueError('bounded suffix duration required')
        code=self.lib.sf_run(self.handle,ticks)
        if code:raise RuntimeError(f'flag execution failed: {code}')
        self.age+=ticks;self.time+=ticks
        return dict(age=self.age,time=self.time,literal_physical_ticks=ticks)
