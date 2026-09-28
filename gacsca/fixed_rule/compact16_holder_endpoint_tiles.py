"""Fixed GPU endpoint operator with tiled raw/image input and complete output.

Source is immutable data, either raw physical cells or a complete canonical image.
The same compiled evaluator handles both through a fixed physical-cell accessor.
There is no hierarchy-depth argument, host rule evaluation or recursive execution.
"""
import ctypes
from functools import lru_cache
import hashlib
from pathlib import Path
import subprocess
import numpy as np
from . import compact16_holder_endpoint_gpu as base,compact16_holder_rule as f,compact16_holder_program as p


def generated_source():
    original=Path(base.__file__).with_suffix('.cu').read_text()
    body=original[original.index('__global__ void terminal(World w)'):original.index('__global__ void commit(World w)')]
    body=body.replace('terminal(World w)','terminal(Window w)',1)
    old='size_t neighbor=(col+w.n+(j%w.n))%w.n;neighbor=(neighbor+w.n-(7%w.n))%w.n;'
    assert body.count(old)==1;body=body.replace(old,'size_t neighbor=col+j;')
    assert body.count('w.raw[col*FIELDS+k]')==1;body=body.replace('w.raw[col*FIELDS+k]','w.raw[(col+7)*FIELDS+k]')
    source=Path(__file__).with_suffix('.cu').read_text();assert source.count('// GENERATED_TERMINAL')==1
    return source.replace('// GENERATED_TERMINAL',body)


def header():
    value=base.header()
    value+=f'#define MEMORY {p.layout().memory_count}ULL\n#define RAW_AGE {f.COL["age"]}ULL\n#define RAW_SIGNAL {f.COL["signal"]}ULL\n#define DATA_PRIMARY {f.COL["s2_data"]}ULL\n'
    value+='__device__ __constant__ unsigned DATA_FIELDS[]={'+','.join(str(f.COL[f's{i}_data']) for i in range(5))+'};\n'
    return value


@lru_cache(maxsize=1)
def library():
    source=generated_source();generated=header();identity=hashlib.sha256(source.encode()+generated.encode()+b'nvcc-O2-sm80-endpoint-tiles-v1').hexdigest()[:20]
    directory=Path(__file__).resolve().parents[2]/'figs/fixed_rule/build'/('compact16_holder_endpoint_tiles_'+identity);directory.mkdir(parents=True,exist_ok=True);target=directory/'tiles.so'
    if not target.exists():
        src=directory/'endpoint_tiles.cu';src.write_text(source);(directory/'compact16_holder_endpoint_tiles_generated.h').write_text(generated)
        with (directory/'build.log').open('w') as log:subprocess.run(['/usr/local/cuda/bin/nvcc','-O2','-std=c++17','-arch=sm_80','--shared','-Xcompiler','-fPIC',str(src),'-o',str(target)],stdout=log,stderr=subprocess.STDOUT,check=True)
    lib=ctypes.CDLL(str(target));h=ctypes.c_void_p;u=ctypes.c_uint64;n=ctypes.c_size_t;ptr=ctypes.POINTER(u);hp=ctypes.POINTER(h)
    arguments=dict(tt_source_free=[h],tt_raw=[n,ptr,u,hp,ptr],tt_initial=[h,u,hp,ptr],tt_free=[h],tt_create=[n,u,hp,ptr],tt_evaluate=[h,h,u,n,ctypes.c_int],tt_read=[h,ptr,ptr],tt_freeze=[h,u,u,hp,ptr],tt_cells=[h,h,u,n,ptr],tt_collect=[h,h,u],tt_decode=[h,h,u,hp,ptr])
    for name,args in arguments.items():method=getattr(lib,name);method.argtypes=args;method.restype=None if name in ('tt_source_free','tt_free') else ctypes.c_int
    return lib


def pointer(array):return array.ctypes.data_as(ctypes.POINTER(ctypes.c_uint64))


def budget(value):
    if type(value) is not int or not 0<value<=8*1024**3:raise ValueError('positive explicit budget at most 8 GiB required')
    return value


class Source:
    def __init__(self,handle,n,kind,age,device_bytes,*,ready=True):
        self.handle=handle;self.n=n;self.kind=kind;self.age=age;self.device_bytes=device_bytes;self.ready=ready;self.progress=n if ready else 0;self.lib=library()
    @classmethod
    def raw(cls,array,*,device_budget=64*1024**2):
        if not isinstance(array,np.ndarray) or array.dtype!=np.uint64 or array.ndim!=2 or array.shape[1]!=f.FIELDS or not len(array):raise ValueError('all raw physical fields required')
        out=ctypes.c_void_p();size=ctypes.c_uint64();array=np.ascontiguousarray(array)
        code=library().tt_raw(len(array),pointer(array),budget(device_budget),ctypes.byref(out),ctypes.byref(size))
        if code:raise ValueError(f'raw source allocation rejected: {code}')
        return cls(out,len(array),0,None,int(size.value))
    @classmethod
    def empty_raw(cls,n,*,device_budget=64*1024**2):
        if type(n) is not int or n<1:raise ValueError('positive cell count required')
        out=ctypes.c_void_p();size=ctypes.c_uint64();code=library().tt_raw(n,None,budget(device_budget),ctypes.byref(out),ctypes.byref(size))
        if code:raise ValueError(f'raw sink allocation rejected: {code}')
        return cls(out,n,0,None,int(size.value),ready=False)
    def initial_image(self,*,device_budget=32*1024**2):
        if not self.handle or not self.ready or self.kind:raise ValueError('complete raw source required')
        out=ctypes.c_void_p();size=ctypes.c_uint64();code=self.lib.tt_initial(self.handle,budget(device_budget),ctypes.byref(out),ctypes.byref(size))
        if code:raise ValueError(f'initial image allocation rejected: {code}')
        return Source(out,self.n*f.Q,1,0,int(size.value))
    def close(self):
        if self.handle:self.lib.tt_source_free(self.handle);self.handle=None
    def __enter__(self):return self
    def __exit__(self,*args):self.close()


class Window:
    def __init__(self,capacity=128,*,device_budget=32*1024**2):
        if type(capacity) is not int or not 1<=capacity<=1<<20:raise ValueError('positive tile capacity required')
        self.lib=library();self.handle=ctypes.c_void_p();size=ctypes.c_uint64()
        code=self.lib.tt_create(capacity,budget(device_budget),ctypes.byref(self.handle),ctypes.byref(size))
        if code:raise ValueError(f'tile allocation rejected: {code}')
        self.capacity=capacity;self.device_bytes=int(size.value);self.valid=False
    def evaluate(self,source,start,count,*,committed=False):
        self.valid=False
        if not self.handle or not source.handle or not source.ready or type(start) is not int or type(count) is not int or start<0 or count<1 or count>self.capacity or start+count>source.n:raise ValueError('live complete source and in-range tile required')
        code=self.lib.tt_evaluate(self.handle,source.handle,start,count,int(committed))
        if code:raise ValueError(f'tiled endpoint rejected: {code}')
        self.start=start;self.count=count;self.source_size=source.n;self.age=0 if committed else f.U-1;self.valid=True
    def read(self):
        if not self.valid:raise ValueError('no valid output tile')
        bank=np.empty((self.count,p.layout().memory_count+5),dtype=np.uint64);signals=np.empty((self.count,2),dtype=np.uint64)
        if self.lib.tt_read(self.handle,pointer(bank),pointer(signals)):raise RuntimeError('tile read failed')
        return bank,signals
    def freeze_image(self,*,device_budget=32*1024**2):
        if not self.valid or self.start!=0 or self.count!=self.source_size:raise ValueError('complete image required, not a partial tile')
        out=ctypes.c_void_p();size=ctypes.c_uint64();code=self.lib.tt_freeze(self.handle,self.age,budget(device_budget),ctypes.byref(out),ctypes.byref(size))
        if code:raise ValueError(f'image allocation rejected: {code}')
        return Source(out,self.count*f.Q,1,self.age,int(size.value))
    def cells(self,source,start,count):
        if not self.handle or not source.handle or not source.ready or type(start) is not int or type(count) is not int or start<0 or not 1<=count<=self.capacity+14:raise ValueError('live source and bounded read required')
        output=np.empty((count,f.FIELDS),dtype=np.uint64)
        if self.lib.tt_cells(self.handle,source.handle,start%source.n,count,pointer(output)):raise RuntimeError('physical cell read failed')
        return output
    def collect_info(self,destination):
        if not self.valid or not destination.handle or destination.kind or destination.ready or destination.n!=self.source_size or destination.progress!=self.start:raise ValueError('ordered complete Info collection required')
        if self.lib.tt_collect(self.handle,destination.handle,self.start):raise RuntimeError('Info collection failed')
        destination.progress+=self.count;destination.ready=destination.progress==destination.n
    def decode(self,source,*,device_budget=32*1024**2):
        if not self.handle or not source.handle or not source.ready or source.n%f.Q:raise ValueError('complete encoded block source required')
        out=ctypes.c_void_p();size=ctypes.c_uint64();code=self.lib.tt_decode(self.handle,source.handle,budget(device_budget),ctypes.byref(out),ctypes.byref(size))
        if code:raise ValueError(f'device decode failed: {code}')
        return Source(out,source.n//f.Q,0,None,int(size.value))
    def close(self):
        if self.handle:self.lib.tt_free(self.handle);self.handle=None;self.valid=False
    def __enter__(self):return self
    def __exit__(self,*args):self.close()
