"""Bounded resident bank and complete raw physical CUDA local transitions.

No coherent/healthy-prefix restriction is imposed on physical exception values.
This is a resident snapshot reader/evaluator, not yet a synchronous colony
executor: evaluate() returns exact next states without committing them.
"""
import ctypes
from functools import lru_cache
import hashlib
from pathlib import Path
import subprocess
import numpy as np
from . import small_holder_rule as f, small_holder_core as c
from . import small_holder_quotient as q, small_holder_program as p
from .small_holder_bank import Snapshot
from .word_native import expression_source

MAX_BATCH = 256


def header():
    maps = []
    for name,_ in f.SCHEMA:
        if name.startswith('p'):
            prefix, field = name.split('_',1); maps.append((-1,int(prefix[1:])-3,c.STATIC.index(field)))
        elif name.startswith(('s','w')) and name not in ('signal',):
            prefix, field = name.split('_',1); maps.append((q.COL[field],int(prefix[1:])-2,-1))
        else: maps.append((q.COL[name],0,-1))
    text = '#include <stdint.h>\n#include <stddef.h>\n#include <string.h>\n'
    for key,value in dict(Q=f.Q,RAW_FIELDS=f.FIELDS,LOGICAL_FIELDS=len(q.SCHEMA),MEM_ROWS=p.layout().memory_count,ROM_ROWS=p.layout().computation_cells,MAX_BATCH=MAX_BATCH).items():
        text += f'#define {key} {value}\n'
    text += 'enum {'+','.join('L_'+name.upper() for name,_ in q.SCHEMA)+'};\n'
    for name,values in zip(('RAW_LOGICAL','RAW_OFFSET','RAW_STATIC'),zip(*maps)):
        text += '__device__ __constant__ int '+name+'[]={'+','.join(map(str,values))+'};\n'
    return text + expression_source(f.self_description(),'bank_physical_local').replace('void bank_physical_local','__device__ __noinline__ void bank_physical_local',1)


@lru_cache(maxsize=1)
def library():
    source=Path(__file__).with_suffix('.cu'); generated=header()
    digest=hashlib.sha256(source.read_bytes()+generated.encode()+b'nvcc-O2-sm80-bank-v1').hexdigest()[:20]
    directory=source.resolve().parents[2]/'figs/fixed_rule/build'/('small_holder_bank_'+digest)
    directory.mkdir(parents=True,exist_ok=True); target=directory/'bank.so'
    if not target.exists():
        (directory/'small_holder_bank_generated.h').write_text(generated)
        with (directory/'build.log').open('w') as log:
            subprocess.run(['/usr/local/cuda/bin/nvcc','-O2','-std=c++17','-arch=sm_80','--shared','-Xcompiler','-fPIC','-I',str(directory),str(source),'-o',str(target)],stdout=log,stderr=subprocess.STDOUT,check=True)
    lib=ctypes.CDLL(str(target));ptr=ctypes.POINTER(ctypes.c_uint64);handle=ctypes.c_void_p
    lib.bank_create.argtypes=[ptr,ptr,ptr,ctypes.c_size_t,ptr,ptr,ctypes.c_size_t,ptr,ctypes.c_uint64,ctypes.c_uint64,ctypes.POINTER(handle),ptr]
    lib.bank_create.restype=ctypes.c_int
    lib.bank_free.argtypes=[handle];lib.bank_free.restype=None
    lib.bank_evaluate.argtypes=[handle,ptr,ctypes.c_size_t,ptr,ctypes.c_int];lib.bank_evaluate.restype=ctypes.c_int
    return lib


def pointer(a):return a.ctypes.data_as(ctypes.POINTER(ctypes.c_uint64))


class Resident:
    def __init__(self, snapshot):
        if not isinstance(snapshot,Snapshot):raise ValueError('validated full physical snapshot required')
        self.snapshot=snapshot;self.lib=library();self.handle=ctypes.c_void_p();allocated=ctypes.c_uint64()
        code=self.lib.bank_create(pointer(snapshot.data),pointer(snapshot.logical_keys),pointer(snapshot.logical_values),len(snapshot.logical_keys),pointer(snapshot.raw_keys),pointer(snapshot.raw_values),len(snapshot.raw_keys),pointer(p.base_rom()),snapshot.colonies,snapshot.age,ctypes.byref(self.handle),ctypes.byref(allocated))
        if code:raise RuntimeError(f'CUDA bank allocation failed: {code}')
        self.device_bytes=int(allocated.value)
    def close(self):
        if self.handle:self.lib.bank_free(self.handle);self.handle=None
    def __enter__(self):return self
    def __exit__(self,*args):self.close()
    def evaluate(self, positions, *, reconstruct=False):
        if not self.handle:raise ValueError('closed resident bank')
        positions=tuple(positions)
        if not 1 <= len(positions) <= MAX_BATCH or any(type(x) is not int or not 0 <= x < self.snapshot.sites for x in positions):
            raise ValueError('1..256 in-ring physical positions required')
        source=np.array(positions,dtype=np.uint64);out=np.empty((len(source),f.FIELDS),dtype=np.uint64)
        code=self.lib.bank_evaluate(self.handle,pointer(source),len(source),pointer(out),int(reconstruct))
        if code:raise RuntimeError(f'CUDA bank evaluation failed: {code}')
        return out
