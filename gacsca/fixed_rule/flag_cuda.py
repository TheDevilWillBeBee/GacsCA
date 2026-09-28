"""Isolated CUDA accelerator for canonical, unforced printed physical flags.

This is an execution representation of delivery_rule, not a hierarchy kernel.
Q stays fixed, there is no depth argument, and no upper state is decoded here.
Only the interval [98Q,U] with unchanged coherent Signal is admitted. Other
controller fields must be evolved separately using the validated factorization.
"""
import ctypes
from functools import lru_cache
import hashlib
from pathlib import Path
import subprocess
import numpy as np
from . import delivery_rule as rule
from .flag_words import pointer

FROZEN_WORD_SHA='49c96efafe71825670079d0808de67e5a6be8310733d6bafb4f14acba4e67d7a'

@lru_cache(maxsize=1)
def libraries():
    here=Path(__file__).resolve().parent
    original=(here/'flag_words.c').read_bytes()
    if hashlib.sha256(original).hexdigest()!=FROZEN_WORD_SHA:raise RuntimeError('physical source changed; re-audit required')
    text=original.decode().split('void fw_free(')[0]
    for name in ('count2','count3','count4'):text=text.replace('static uint64_t '+name,'FLAG_INLINE uint64_t '+name)
    text=text.replace('void fw_word','FLAG_INLINE void fw_word')
    sources=[here/'flag_cuda.cu',here/'flag_cuda_reference.c',Path(__file__)]
    digest=hashlib.sha256(text.encode()+b''.join(p.read_bytes() for p in sources)).hexdigest()[:20]
    build=here.parents[1]/'figs/fixed_rule/build'/('flag_cuda_'+digest);build.mkdir(parents=True,exist_ok=True)
    (build/'flag_word_generated.h').write_text(text)
    gpu=build/'flags_cuda.so';cpu=build/'flags_reference.so'
    if not gpu.exists():subprocess.run(['/usr/local/cuda/bin/nvcc','-O3','-std=c++17','-arch=sm_80','--shared','-Xcompiler','-fPIC','-I',str(build),str(sources[0]),'-o',str(gpu)],check=True)
    if not cpu.exists():subprocess.run(['cc','-O3','-std=c99','-shared','-fPIC','-I',str(build),str(sources[1]),'-o',str(cpu)],check=True)
    a,b=ctypes.CDLL(str(gpu)),ctypes.CDLL(str(cpu));ptr=ctypes.POINTER(ctypes.c_uint64)
    a.flag_cuda_run.argtypes=[ptr,ptr,ctypes.c_uint64,ctypes.c_uint64,ctypes.c_int,ctypes.c_int];a.flag_cuda_run.restype=ctypes.c_int
    b.flag_reference.argtypes=[ptr,ptr,ctypes.c_uint64,ctypes.c_uint64];b.flag_reference.restype=ctypes.c_int
    return a,b


def advance(words,ticks,*,age=98*rule.Q,block_ticks=512,shortcuts=True,reference=False):
    if not isinstance(ticks,int) or ticks<0 or not isinstance(age,int) or not 98*rule.Q<=age<=rule.U or ticks>rule.U-age:raise ValueError('unforced within-period physical time required')
    if not isinstance(block_ticks,int) or not 1<=block_ticks<=512:raise ValueError('temporal block in 1..512 required')
    if not isinstance(words,np.ndarray) or words.dtype!=np.uint64 or words.ndim!=2 or words.shape[1]!=2 or not len(words) or len(words)%(rule.Q//64):raise ValueError('complete canonical colony ring of two uint64 flag planes required')
    words=np.ascontiguousarray(words);output=np.empty_like(words);gpu,cpu=libraries()
    code=cpu.flag_reference(pointer(words),pointer(output),len(words),ticks) if reference else gpu.flag_cuda_run(pointer(words),pointer(output),len(words),ticks,block_ticks,int(shortcuts))
    if code:raise RuntimeError(f'physical flag executor error {code}')
    return output
