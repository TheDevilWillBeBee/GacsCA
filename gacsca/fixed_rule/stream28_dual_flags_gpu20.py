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
from . import stream28_dual_holder_rule20 as f

WORDS=f.Q//64
GRAPH_TICKS=128
MAX_COLONIES=64


@lru_cache(maxsize=1)
def library():
    source=Path(__file__).with_suffix('.cu')
    header=''.join(f'#define {k} UINT64_C({v})\n' for k,v in dict(WORDS_PER_COLONY=WORDS,WF_START=f.WF_START,WF_END=f.WF_END,PERIOD=f.U,GRAPH_TICKS=GRAPH_TICKS).items())
    identity=hashlib.sha256(source.read_bytes()+header.encode()+b'nvcc-O2-sm80-dual20-flags-v1').hexdigest()[:20]
    directory=source.resolve().parents[2]/'figs/fixed_rule/build'/('stream28_dual_flags_gpu20_'+identity);directory.mkdir(parents=True,exist_ok=True);target=directory/'flags.so'
    if not target.exists():
        (directory/'stream28_dual_flags_gpu20_generated.h').write_text(header)
        with (directory/'build.log').open('w') as log:
            subprocess.run(['/usr/local/cuda/bin/nvcc','-O2','-std=c++17','-arch=sm_80','--shared','-Xcompiler','-fPIC','-I',str(directory),str(source),'-o',str(target)],check=True,stdout=log,stderr=subprocess.STDOUT)
    lib=ctypes.CDLL(str(target));ptr=ctypes.POINTER(ctypes.c_uint64);byte=ctypes.POINTER(ctypes.c_uint8);h=ctypes.c_void_p
    for name,args,result in (('uf_create',[ctypes.c_size_t,ctypes.c_uint64,byte,byte,ptr,ctypes.POINTER(h)],ctypes.c_int),('uf_free',[h],None),('uf_read',[h,ptr],ctypes.c_int),('uf_run',[h,ctypes.c_uint64],ctypes.c_int)):
        fn=getattr(lib,name);fn.argtypes=args;fn.restype=result
    return lib


class RawWorld:
    def __init__(self,right,left,*,age=0,initial=None):
        self.right=tuple(right);self.left=tuple(left);self.colonies=len(self.right)
        if not 0<self.colonies<=MAX_COLONIES or len(self.left)!=self.colonies or any(type(x) is not int or x not in (0,1) for x in (*self.right,*self.left)):raise ValueError('bounded coherent Signal pairs required')
        if type(age) is not int or not 0<=age<f.U:raise ValueError('suffix Age required')
        if initial is None:initial=np.zeros((self.colonies*WORDS,2),dtype=np.uint64)
        if not isinstance(initial,np.ndarray) or initial.dtype!=np.uint64 or initial.shape!=(self.colonies*WORDS,2):raise ValueError('complete packed physical flags required')
        data=np.ascontiguousarray(initial);right=np.array(self.right,dtype=np.uint8);left=np.array(self.left,dtype=np.uint8)
        self.lib=library();self.handle=ctypes.c_void_p();byte=ctypes.POINTER(ctypes.c_uint8)
        code=self.lib.uf_create(self.colonies,age,right.ctypes.data_as(byte),left.ctypes.data_as(byte),data.ctypes.data_as(ctypes.POINTER(ctypes.c_uint64)),ctypes.byref(self.handle))
        if code:raise RuntimeError(f'flag allocation failed: {code}')
        self.age=age;self.time=0;self.device_bytes=32*self.colonies*WORDS+2*self.colonies
    def close(self):
        if self.handle:self.lib.uf_free(self.handle);self.handle=None
    def __enter__(self):return self
    def __exit__(self,*args):self.close()
    def read(self):
        if not self.handle:raise ValueError('closed flag world')
        out=np.empty((self.colonies*WORDS,2),dtype=np.uint64)
        code=self.lib.uf_read(self.handle,out.ctypes.data_as(ctypes.POINTER(ctypes.c_uint64)))
        if code:raise RuntimeError(f'flag read failed: {code}')
        return out
    def run(self,ticks):
        if not self.handle or type(ticks) is not int or not 0<=ticks<=f.U-self.age:raise ValueError('bounded suffix duration required')
        code=self.lib.uf_run(self.handle,ticks)
        if code:raise RuntimeError(f'flag execution failed: {code}')
        self.age+=ticks;self.time+=ticks
        return dict(age=self.age,time=self.time,literal_physical_ticks=ticks)


class World:
    """Same retained physical flag state API as the checked CPU recurrence."""
    def __init__(self,right_signals,left_signals,*,age=0,runs=None):
        right_signals=tuple(right_signals)
        left_signals=tuple(left_signals)
        if len(right_signals)!=len(left_signals):
            raise ValueError('one signal pair per colony required')
        if runs is None:runs=((len(right_signals)*WORDS,0,0),)
        array=np.zeros((len(right_signals)*WORDS,2),dtype=np.uint64)
        start=0
        for stop,first,second in runs:
            if not start<int(stop)<=len(array):
                raise ValueError('ordered complete physical flag runs required')
            array[start:int(stop),0]=first
            array[start:int(stop),1]=second
            start=int(stop)
        if start!=len(array):raise ValueError('incomplete physical flag runs')
        self.raw=RawWorld(right_signals,left_signals,age=age,initial=array)
        self.signals=(right_signals,left_signals)
        self.colonies=len(right_signals)

    def close(self):self.raw.close()
    def __enter__(self):return self
    def __exit__(self,*args):self.close()

    @property
    def info(self):
        return dict(age=self.raw.age%f.U,time=self.raw.time,
                    literal_ticks=self.raw.time,quiet_ticks=0,
                    word_evaluations=self.raw.time*self.colonies*WORDS,
                    runs=len(self.runs))

    @property
    def runs(self):
        words=self.raw.read()
        runs=[]
        for index,pair in enumerate(words):
            first,second=map(int,pair)
            if runs and runs[-1][1:]==(first,second):
                runs[-1]=(index+1,first,second)
            else:runs.append((index+1,first,second))
        return np.array(runs,dtype=np.uint64)

    def run(self,ticks,*,skip_fixed=True):
        # This implementation does every physical flag tick on the GPU.
        # The keyword is accepted only for parity with the CPU API.
        if type(skip_fixed) is not bool:raise ValueError('boolean skip flag required')
        self.raw.run(ticks)
        return self.info
