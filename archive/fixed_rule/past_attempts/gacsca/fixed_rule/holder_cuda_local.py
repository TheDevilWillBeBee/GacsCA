"""Bounded CUDA checks for the unchanged physical prefix, with lossless packing.

At most 4096 neighborhoods per call; explicit device allocations <64 MiB and
host arrays <16 MiB. This is a local-kernel building block, not a complete GPU
colony executor or a completed depth-two run. CUDA context memory is additional.
"""
import ctypes,hashlib,subprocess
from functools import lru_cache
from pathlib import Path
import numpy as np
from . import holder_core as c,holder_rule as f,holder_quotient as q,holder_program as p,holder_packed as packed
from .holder_prefix_description import build
from .word_native import expression_source


def header():
    text='#include <stdint.h>\n#include <stddef.h>\n#include <string.h>\n'
    text+=f'#define COLONY_CELLS UINT64_C({f.Q})\n#define ROM_ROWS {p.layout().computation_cells}\n#define PACKED_WORDS {packed.WORDS}\n'
    text+='enum {'+','.join(n.upper() for n,_ in c.SCHEMA)+',FIELDS};\n'
    text+='enum {'+','.join('P_'+n.upper() for n,_ in q.SCHEMA)+',P_FIELDS};\n'
    for name,values in (('STATIC_FIELDS',[c.COL[n] for n in c.STATIC]),('DYNAMIC_FIELDS',[c.COL[n] for n,_ in q.SCHEMA]),('FIELD_OFFSETS',packed.OFFSETS),('FIELD_WIDTHS',[w for _,w in q.SCHEMA])):
        text+='__device__ __constant__ unsigned '+name+'[]={'+','.join(map(str,values))+'};\n'
    return text+expression_source(build(),'holder_prefix_local').replace('void holder_prefix_local','__device__ __noinline__ void holder_prefix_local',1)


@lru_cache(maxsize=1)
def library():
    here=Path(__file__).resolve().parent;source=here/'holder_cuda_local.cu';generated=header()
    digest=hashlib.sha256(source.read_bytes()+generated.encode()+b'nvcc-O2-sm80-holder-local-v1').hexdigest()[:20]
    directory=here.parents[1]/'figs/fixed_rule/build'/('holder_cuda_local_'+digest);directory.mkdir(parents=True,exist_ok=True);target=directory/'holder_cuda_local.so'
    if not target.exists():
        (directory/'holder_cuda_local_generated.h').write_text(generated)
        with (directory/'build.log').open('w') as log:subprocess.run(['/usr/local/cuda/bin/nvcc','-O2','-std=c++17','-arch=sm_80','--shared','-Xcompiler','-fPIC','-I',str(directory),str(source),'-o',str(target)],stdout=log,stderr=subprocess.STDOUT,check=True)
    lib=ctypes.CDLL(str(target));ptr=ctypes.POINTER(ctypes.c_uint64)
    lib.holder_cuda_local.argtypes=[ptr,ptr,ptr,ctypes.c_size_t,ptr];lib.holder_cuda_local.restype=ctypes.c_int;return lib


def pointer(a):return a.ctypes.data_as(ctypes.POINTER(ctypes.c_uint64))


def step(neighborhoods):
    if not isinstance(neighborhoods,np.ndarray) or neighborhoods.dtype!=np.uint64 or neighborhoods.ndim!=3 or neighborhoods.shape[1:]!=(11,len(q.SCHEMA)) or not 1<=len(neighborhoods)<=4096:raise ValueError('1..4096 complete radius-five logical neighborhoods required')
    ages=neighborhoods[:,:,q.COL['age']];centers=neighborhoods[:,5,q.COL['address']]
    if np.any(ages!=ages[:,5,None]) or np.any(ages>=96*f.Q-1):raise ValueError('uniform prefix clock domain required')
    wanted=(centers[:,None]+np.array([j%f.Q for j in range(-5,6)],dtype=np.uint64))%np.uint64(f.Q)
    if np.any(neighborhoods[:,:,q.COL['address']]!=wanted):raise ValueError('canonical geometry required')
    if np.any(neighborhoods[:,:,[q.COL[n] for n in ('f1','f2','wf1','wf2')]]):raise ValueError('zero flags/Wf required')
    source=packed.pack(neighborhoods);target=np.empty((len(source),packed.WORDS),dtype=np.uint64);allocated=ctypes.c_uint64()
    code=library().holder_cuda_local(pointer(source),pointer(target),pointer(p.base_rom()),len(source),ctypes.byref(allocated))
    if code:raise RuntimeError(f'CUDA local transition failed: {code}')
    return packed.unpack(target),dict(explicit_device_bytes=int(allocated.value),host_transfer_bytes=source.nbytes+target.nbytes+p.base_rom().nbytes,packed_bits=packed.WIDTH,packed_words=packed.WORDS,full_physical_rule=f.self_description().digest())
