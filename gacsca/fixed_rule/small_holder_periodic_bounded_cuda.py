"""Exact synchronous full-rule GPU evolution of periodic background + defects.

The background itself evolves with F, not an assumed quiet-state formula. The
radius-seven expansion of all exceptions contains every possible difference
from that evolving background. Only full packed-row equality removes a defect.
This representation is independent of hierarchy depth. It is bounded here by
execution resources, and does not itself establish nested macrostep execution.
This revision uses 256 workers with explicitly allocated, interleaved scratch;
it avoids the earlier generated full-DAG per-thread stack.
"""
import ctypes
from functools import lru_cache
import hashlib
from pathlib import Path
import subprocess
import numpy as np
from . import small_holder_rule as f,small_holder_raw_packed as packed
from .word_workspace_source import expression_source

MAX_CANDIDATES=8192
MAX_READ=256
MAX_BACKGROUND=32768
WORKERS=256


def header():
    text='#include <stdint.h>\n#include <stddef.h>\n#include <string.h>\n'
    for name,value in dict(RAW_FIELDS=f.FIELDS,PACKED_WORDS=packed.WORDS,CAPACITY=MAX_CANDIDATES,READ_CAPACITY=MAX_READ).items():text+=f'#define {name} {value}\n'
    for name,values in (('OFFSETS',packed.OFFSETS),('WIDTHS',[w for _,w in f.SCHEMA])):
        text+='__device__ __constant__ unsigned '+name+'[]={'+','.join(map(str,values))+'};\n'
    body,allocation=expression_source(f.self_description(),'periodic_physical_local',stride=WORKERS)
    text+=f'#define WORKERS {WORKERS}\n#define TEMP_WORDS {allocation.count}\n#define WORKSPACE_WORDS ((15*RAW_FIELDS+RAW_FIELDS+TEMP_WORDS)*WORKERS)\n'
    return text+body.replace('void periodic_physical_local','__device__ __noinline__ void periodic_physical_local',1)


@lru_cache(maxsize=1)
def library():
    source=Path(__file__).with_suffix('.cu');generated=header()
    digest=hashlib.sha256(source.read_bytes()+generated.encode()+b'nvcc-O2-sm80-periodic-bounded-v1').hexdigest()[:20]
    directory=source.resolve().parents[2]/'figs/fixed_rule/build'/('small_holder_periodic_bounded_'+digest)
    directory.mkdir(parents=True,exist_ok=True);target=directory/'periodic.so'
    if not target.exists():
        (directory/'small_holder_periodic_bounded_generated.h').write_text(generated)
        with (directory/'build.log').open('w') as log:
            subprocess.run(['/usr/local/cuda/bin/nvcc','-O2','-std=c++17','-arch=sm_80','--shared','-Xcompiler','-fPIC','-I',str(directory),str(source),'-o',str(target)],stdout=log,stderr=subprocess.STDOUT,check=True)
    lib=ctypes.CDLL(str(target));ptr=ctypes.POINTER(ctypes.c_uint64);h=ctypes.c_void_p
    lib.periodic_create.argtypes=[ptr,ctypes.c_size_t,ctypes.c_uint64,ptr,ptr,ctypes.c_size_t,ctypes.POINTER(h),ptr];lib.periodic_create.restype=ctypes.c_int
    lib.periodic_free.argtypes=[h];lib.periodic_free.restype=None
    lib.periodic_prepare.argtypes=[h,ptr,ctypes.c_size_t,ptr];lib.periodic_prepare.restype=ctypes.c_int
    lib.periodic_commit.argtypes=[h,ptr,ctypes.c_size_t];lib.periodic_commit.restype=ctypes.c_int
    lib.periodic_read.argtypes=[h,ptr,ctypes.c_size_t,ptr];lib.periodic_read.restype=ctypes.c_int
    return lib


def pointer(array):return array.ctypes.data_as(ctypes.POINTER(ctypes.c_uint64))


class World:
    def __init__(self,background,sites,exceptions=None):
        if not isinstance(background,np.ndarray) or background.ndim!=2 or not 1<=len(background)<=MAX_BACKGROUND:
            raise ValueError('bounded nonempty raw background required')
        if type(sites) is not int or not len(background)<=sites<1<<63 or sites%len(background):
            raise ValueError('ring must be an integral repetition of background, below 2^63 sites')
        bg=packed.pack(background);exceptions={} if exceptions is None else dict(exceptions)
        if len(exceptions)>MAX_CANDIDATES or any(type(x) is not int or not 0<=x<sites for x in exceptions):raise ValueError('bounded in-ring exceptions required')
        if any(not isinstance(x,f.Cell) for x in exceptions.values()):raise ValueError('complete raw exceptions required')
        # Normalization is exact full-state equality, never a projected comparison.
        exceptions={x:c for x,c in exceptions.items() if tuple(f.encode_cell(c))!=tuple(map(int,background[x%len(bg)]))}
        self._positions=np.array(sorted(exceptions),dtype=np.uint64)
        raw=np.array([f.encode_cell(exceptions[int(x)]) for x in self._positions],dtype=np.uint64).reshape(-1,f.FIELDS)
        values=packed.pack(raw)
        self.lib=library();self.handle=ctypes.c_void_p();allocated=ctypes.c_uint64()
        code=self.lib.periodic_create(pointer(bg),len(bg),sites,pointer(self._positions),pointer(values),len(values),ctypes.byref(self.handle),ctypes.byref(allocated))
        if code:raise RuntimeError(f'periodic allocation failed: {code}')
        self.sites=sites;self.period=len(bg);self.time=0;self.device_bytes=int(allocated.value)
        self.local_evaluations=0;self.max_candidates=0
    @property
    def positions(self):
        return tuple(map(int,self._positions))
    def close(self):
        if self.handle:self.lib.periodic_free(self.handle);self.handle=None
    def __enter__(self):return self
    def __exit__(self,*args):self.close()
    def read(self,positions):
        if not self.handle:raise ValueError('closed periodic world')
        positions=tuple(positions)
        if not 1<=len(positions)<=MAX_READ or any(type(x) is not int or not 0<=x<self.sites for x in positions):raise ValueError('bounded in-ring positions required')
        source=np.array(positions,dtype=np.uint64);out=np.empty((len(source),packed.WORDS),dtype=np.uint64)
        code=self.lib.periodic_read(self.handle,pointer(source),len(source),pointer(out))
        if code:raise RuntimeError(f'periodic read failed: {code}')
        return tuple(f.decode_cell(row.tolist()) for row in packed.unpack(out))
    def step(self):
        if not self.handle:raise ValueError('closed periodic world')
        # A change at x can only affect outputs x-j for j in F's neighborhood.
        candidates=np.array(sorted({(int(x)-j)%self.sites for x in self._positions for j in f.NEIGHBORHOOD}),dtype=np.uint64)
        if len(candidates)>MAX_CANDIDATES:raise ValueError('candidate capacity exceeded before any state change')
        flags=np.empty(len(candidates),dtype=np.uint64)
        code=self.lib.periodic_prepare(self.handle,pointer(candidates),len(candidates),pointer(flags))
        if code:raise RuntimeError(f'periodic prepare failed: {code}')
        selected=np.flatnonzero(flags).astype(np.uint64)
        code=self.lib.periodic_commit(self.handle,pointer(selected),len(selected))
        if code:raise RuntimeError(f'periodic commit failed: {code}')
        self._positions=candidates[selected.astype(np.intp)];self.time+=1
        self.local_evaluations+=self.period+len(candidates);self.max_candidates=max(self.max_candidates,len(candidates))
        return dict(time=self.time,background_evaluations=self.period,candidate_evaluations=len(candidates),exceptions=len(self._positions))
