"""Literal complete projected G on bounded rings, with no coherent-state premise.

Every mutable word and all derived metadata are retained. Reusable GPU workspace
is backend storage, not physical hardware. No depth parameter or host transition.
"""
import ctypes
from functools import lru_cache
import hashlib
from pathlib import Path
import subprocess
import numpy as np
from . import compact16_holder_rule as f, compact16_holder_core as c
from . import compact16_holder_terminal_reference as reference
from . import compact16_holder_literal_cone as cone
from .word_workspace_source import expression_source

WORKERS=512


def header():
    body,allocation=expression_source(f.self_description(),'dense_full_local',stride=WORKERS)
    text=''.join(f'#define {name} {value}ULL\n' for name,value in dict(Q=f.Q,FIELDS=f.FIELDS,ADDRESS=f.COL['address'],WORKERS=WORKERS,WORKSPACE=(16*f.FIELDS+allocation.count)*WORKERS).items())
    return text+body.replace('void dense_full_local','__device__ __noinline__ void dense_full_local',1)


@lru_cache(maxsize=1)
def library():
    source=Path(__file__).with_suffix('.cu');generated=header()
    identity=hashlib.sha256(source.read_bytes()+generated.encode()+b'nvcc-O2-sm80-literal-dense-v1').hexdigest()[:20]
    directory=source.resolve().parents[2]/'figs/fixed_rule/build'/('compact16_holder_dense_'+identity);directory.mkdir(parents=True,exist_ok=True);target=directory/'dense.so'
    if not target.exists():
        (directory/'compact16_holder_dense_generated.h').write_text(generated)
        with (directory/'build.log').open('w') as out:subprocess.run(['/usr/local/cuda/bin/nvcc','-O2','-std=c++17','-arch=sm_80','--shared','-Xcompiler','-fPIC','-I',str(directory),str(source),'-o',str(target)],check=True,stdout=out,stderr=subprocess.STDOUT)
    lib=ctypes.CDLL(str(target));ptr=ctypes.POINTER(ctypes.c_uint64);h=ctypes.c_void_p
    signatures=dict(dg_create=[ctypes.c_size_t,ptr,ptr,ctypes.c_uint64,ctypes.POINTER(h),ptr],dg_free=[h],dg_run=[h,ctypes.c_uint64],dg_read=[h,ptr])
    for name,args in signatures.items():fn=getattr(lib,name);fn.argtypes=args;fn.restype=None if name=='dg_free' else ctypes.c_int
    return lib


def pointer(array):return array.ctypes.data_as(ctypes.POINTER(ctypes.c_uint64))


class World:
    def __init__(self,raw,*,device_budget=64*1024**2):
        if not isinstance(raw,np.ndarray) or raw.dtype!=np.uint64 or raw.ndim!=2 or raw.shape[1]!=f.FIELDS or not 0<len(raw)<=1<<24:raise ValueError('complete bounded raw ring required')
        if type(device_budget) is not int or not 1<=device_budget<=1024**3:raise ValueError('explicit bounded device budget required')
        for k,(_,width) in enumerate(f.SCHEMA):
            if width<64 and np.any(raw[:,k]>=(np.uint64(1)<<np.uint64(width))):raise ValueError('raw word exceeds physical alphabet')
        if not np.array_equal(raw,cone.normalize(raw.copy())):raise ValueError('metadata outside fixed projected rule')
        raw=np.ascontiguousarray(raw);rom=np.array(reference.metadata(),dtype=np.uint64)
        self.lib=library();self.handle=ctypes.c_void_p();size=ctypes.c_uint64()
        code=self.lib.dg_create(len(raw),pointer(raw),pointer(rom),device_budget,ctypes.byref(self.handle),ctypes.byref(size))
        if code:raise RuntimeError(f'dense allocation rejected: {code}')
        self.sites=len(raw);self.device_bytes=int(size.value);self.time=0
    def run(self,ticks):
        if not self.handle or type(ticks) is not int or not 0<=ticks<=65536:raise ValueError('live bounded literal duration required')
        code=self.lib.dg_run(self.handle,ticks)
        if code:raise RuntimeError(f'literal CUDA evolution failed: {code}')
        self.time+=ticks
        return dict(physical_ticks=ticks,complete_site_transitions=self.sites*ticks)
    def read(self):
        if not self.handle:raise ValueError('closed world')
        result=np.empty((self.sites,f.FIELDS),dtype=np.uint64)
        if self.lib.dg_read(self.handle,pointer(result)):raise RuntimeError('complete readback failed')
        return result
    def close(self):
        if self.handle:self.lib.dg_free(self.handle);self.handle=None
    def __enter__(self):return self
    def __exit__(self,*args):self.close()
