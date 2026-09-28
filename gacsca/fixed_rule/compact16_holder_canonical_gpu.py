"""Factored literal G with canonical Address and a uniform legal Age.

All other mutable raw words are arbitrary, including incoherent replicas, flags,
Wf, Signals, mail and multiple or missing heads. No physical ticks are skipped.
"""
import ctypes
from functools import lru_cache
import hashlib
from pathlib import Path
import subprocess
import numpy as np
from . import compact16_holder_rule as f, compact16_holder_core as c
from . import compact16_holder_core_clock_description as clock
from . import compact16_holder_terminal_reference as reference
from . import compact16_holder_literal_cone as cone
from .word_workspace_source import expression_source

WORKERS=512


def header():
    body,allocation=expression_source(clock.build(healthy_domain=True),'canonical_clock',stride=WORKERS)
    constants=dict(Q=f.Q,U=f.U,FIELDS=f.FIELDS,CORE=c.FIELDS,PROC=len(f.PROCEDURE),WORKERS=WORKERS,
                   WORKSPACE=(6*c.FIELDS+allocation.count)*WORKERS,CAPTURE=f.CAPTURE_AGE,WF_START=f.WF_START,WF_END=f.WF_END)
    constants.update({'F_'+n.upper():f.COL[n] for n in ('address','age','f1','f2','signal','w0_wf1','w2_wf1','w2_wf2')})
    constants.update({'C_'+n.upper():c.COL[n] for n in ('address','age','data')})
    text=''.join(f'#define {name} {value}ULL\n' for name,value in constants.items())
    for name,values in (('proc_core',[c.COL[n] for n,_ in f.PROCEDURE]),('static_core',[c.COL[n] for n in c.STATIC])):
        text+='__device__ __constant__ unsigned '+name+'[]={'+','.join(map(str,values))+'};\n'
    return text+body.replace('void canonical_clock','__device__ __noinline__ void canonical_clock',1)


@lru_cache(maxsize=1)
def library():
    source=Path(__file__).with_suffix('.cu');generated=header()
    identity=hashlib.sha256(source.read_bytes()+generated.encode()+b'nvcc-O2-sm80-canonical-full-v1').hexdigest()[:20]
    directory=source.resolve().parents[2]/'figs/fixed_rule/build'/('compact16_holder_canonical_'+identity);directory.mkdir(parents=True,exist_ok=True);target=directory/'canonical.so'
    if not target.exists():
        (directory/'compact16_holder_canonical_generated.h').write_text(generated)
        with (directory/'build.log').open('w') as out:subprocess.run(['/usr/local/cuda/bin/nvcc','-O2','-std=c++17','-arch=sm_80','--shared','-Xcompiler','-fPIC','-I',str(directory),str(source),'-o',str(target)],check=True,stdout=out,stderr=subprocess.STDOUT)
    lib=ctypes.CDLL(str(target));ptr=ctypes.POINTER(ctypes.c_uint64);h=ctypes.c_void_p
    signatures=dict(cf_create=[ctypes.c_size_t,ptr,ptr,ctypes.c_uint64,ctypes.POINTER(h),ptr],cf_free=[h],cf_run=[h,ctypes.c_uint64],cf_read=[h,ptr])
    for name,args in signatures.items():fn=getattr(lib,name);fn.argtypes=args;fn.restype=None if name=='cf_free' else ctypes.c_int
    return lib


def pointer(array):return array.ctypes.data_as(ctypes.POINTER(ctypes.c_uint64))


class World:
    def __init__(self,raw,*,device_budget=64*1024**2):
        if not isinstance(raw,np.ndarray) or raw.dtype!=np.uint64 or raw.ndim!=2 or raw.shape[1]!=f.FIELDS or not 0<len(raw)<=1<<24 or len(raw)%f.Q:raise ValueError('complete canonical colonies required')
        if type(device_budget) is not int or not 1<=device_budget<=1024**3:raise ValueError('bounded device budget required')
        for k,(_,width) in enumerate(f.SCHEMA):
            if width<64 and np.any(raw[:,k]>=(np.uint64(1)<<np.uint64(width))):raise ValueError('word exceeds fixed physical alphabet')
        if not np.array_equal(raw[:,f.COL['address']],np.arange(len(raw))%f.Q):raise ValueError('canonical Address required')
        age=int(raw[0,f.COL['age']])
        if age>=f.U or np.any(raw[:,f.COL['age']]!=age):raise ValueError('uniform legal Age required')
        if not np.array_equal(raw,cone.normalize(raw.copy())):raise ValueError('projected metadata required')
        raw=np.ascontiguousarray(raw);rom=np.array(reference.metadata(),dtype=np.uint64)
        self.lib=library();self.handle=ctypes.c_void_p();size=ctypes.c_uint64()
        code=self.lib.cf_create(len(raw),pointer(raw),pointer(rom),device_budget,ctypes.byref(self.handle),ctypes.byref(size))
        if code:raise RuntimeError(f'canonical allocation rejected: {code}')
        self.sites=len(raw);self.device_bytes=int(size.value);self.time=0;self.age=age
    def run(self,ticks):
        if not self.handle or type(ticks) is not int or not 0<=ticks<=65536:raise ValueError('live bounded literal duration required')
        code=self.lib.cf_run(self.handle,ticks)
        if code:raise RuntimeError(f'canonical CUDA evolution failed: {code}')
        self.time+=ticks;self.age=(self.age+ticks)%f.U
        return dict(physical_ticks=ticks,complete_site_transitions=self.sites*ticks)
    def read(self):
        if not self.handle:raise ValueError('closed world')
        result=np.empty((self.sites,f.FIELDS),dtype=np.uint64)
        if self.lib.cf_read(self.handle,pointer(result)):raise RuntimeError('complete readback failed')
        return result
    def close(self):
        if self.handle:self.lib.cf_free(self.handle);self.handle=None
    def __enter__(self):return self
    def __exit__(self,*args):self.close()
