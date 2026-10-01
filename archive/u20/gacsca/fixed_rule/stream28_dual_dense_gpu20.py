"""Literal CUDA executor for the one fixed U20 complete physical rule.

The device keeps every raw physical word. The host supplies an initial ring and
a tick count, never an upper transition, hierarchy depth, or event replacement.
"""
import ctypes
from functools import lru_cache
import hashlib
from pathlib import Path
import subprocess

import numpy as np

from . import stream28_dual_pass20 as physical
from . import stream28_dual_pass_optimized20 as description
from .word_allocation_and import allocate,verify
from .wordcode_and import LIT,NAND,AND,ADD,SHR,EQ,LT

WORKERS=256


def generated_header():
    program=description.build()
    if (program.inputs,len(program.outputs))!=(15*physical.FIELDS,
                                               physical.FIELDS):
        raise AssertionError('complete fixed-rule description required')
    allocation=allocate(program)
    verify(program,allocation)
    stride=WORKERS

    def ref(wire):
        if wire<program.inputs:return f'in[{wire*stride}]'
        return f'tmp[{allocation.slots[wire-program.inputs]*stride}]'

    lines=[f'#define FIELDS {physical.FIELDS}',
           f'#define WORKERS {WORKERS}',
           f'#define WORKSPACE_WORDS {(16*physical.FIELDS+allocation.count)*WORKERS}',
           '__device__ __noinline__ void fixed_local(const uint64_t* in, '
           'uint64_t* out, uint64_t* tmp) {']
    for index,(op,a,b) in enumerate(program.operations):
        aa,bb=(ref(a),ref(b)) if op!=LIT else ('','')
        if op==LIT:expr=f'UINT64_C(0x{a:016x})'
        elif op==NAND:expr=f'~({aa}&{bb})'
        elif op==AND:expr=f'{aa}&{bb}'
        elif op==ADD:expr=f'{aa}+{bb}'
        elif op==SHR:expr=f'{bb}<64?{aa}>>{bb}:0'
        elif op==EQ:expr=f'{aa}=={bb}'
        elif op==LT:expr=f'{aa}<{bb}'
        else:raise ValueError(('unsupported own-rule opcode',op))
        lines.append(f' tmp[{allocation.slots[index]*stride}]={expr};')
    lines.extend(f' out[{i*stride}]={ref(wire)};'
                 for i,wire in enumerate(program.outputs))
    lines.append('}')
    return '\n'.join(lines)+'\n'


@lru_cache(maxsize=1)
def library():
    source=Path(__file__).with_suffix('.cu')
    header=generated_header()
    identity=hashlib.sha256(source.read_bytes()+header.encode()+
                            b'nvcc-O2-sm80-full-raw-v1').hexdigest()[:20]
    build=(Path(__file__).resolve().parents[2]/'figs/fixed_rule/build'/
           ('stream28_dual_dense_gpu20_'+identity))
    build.mkdir(parents=True,exist_ok=True)
    (build/'generated.h').write_text(header)
    target=build/'rule.so'
    if not target.exists():
        with (build/'build.log').open('w') as log:
            subprocess.run(['/usr/local/cuda/bin/nvcc','-O2','-std=c++17',
                            '-arch=sm_80','--shared','-Xcompiler','-fPIC',
                            '-I',str(build),str(source),'-o',str(target)],
                           check=True,stdout=log,stderr=subprocess.STDOUT)
    lib=ctypes.CDLL(str(target))
    ptr=ctypes.POINTER(ctypes.c_uint64)
    handle=ctypes.c_void_p
    signatures={
        'fr_create':[ctypes.c_size_t,ptr,ctypes.c_uint64,
                     ctypes.POINTER(handle),ptr],
        'fr_run':[handle,ctypes.c_uint64],
        'fr_read':[handle,ptr],
        'fr_free':[handle],
    }
    for name,args in signatures.items():
        fn=getattr(lib,name)
        fn.argtypes=args
        fn.restype=None if name=='fr_free' else ctypes.c_int
    return lib


def _ptr(array):
    return array.ctypes.data_as(ctypes.POINTER(ctypes.c_uint64))


class World:
    def __init__(self,raw,*,device_budget=8*1024**3):
        if (not isinstance(raw,np.ndarray) or raw.dtype!=np.uint64 or
                raw.ndim!=2 or raw.shape[1]!=physical.FIELDS or
                len(raw)<15 or len(raw)>1<<24):
            raise ValueError('complete uint64 physical ring of at least 15 cells required')
        if type(device_budget) is not int or not 1<=device_budget<=80*1024**3:
            raise ValueError('explicit bounded device budget required')
        widths=description.WIDTHS[7*physical.FIELDS:8*physical.FIELDS]
        if len(widths)!=physical.FIELDS:raise AssertionError('center schema mismatch')
        for word,width in enumerate(widths):
            if width<64 and np.any(raw[:,word]>=np.uint64(1<<width)):
                raise ValueError(('physical alphabet exceeded',word))
        self.lib=library()
        self.handle=ctypes.c_void_p()
        bytes_used=ctypes.c_uint64()
        array=np.ascontiguousarray(raw)
        code=self.lib.fr_create(len(array),_ptr(array),device_budget,
                                ctypes.byref(self.handle),
                                ctypes.byref(bytes_used))
        if code:raise RuntimeError(('CUDA allocation failed',code))
        self.sites=len(array)
        self.device_bytes=int(bytes_used.value)
        self.time=0

    def run(self,ticks):
        if not self.handle or type(ticks) is not int or not 0<=ticks<=physical.U:
            raise ValueError('live world and bounded physical duration required')
        code=self.lib.fr_run(self.handle,ticks)
        if code:raise RuntimeError(('CUDA physical evolution failed',code))
        self.time+=ticks
        return dict(ticks=ticks,complete_site_transitions=ticks*self.sites)

    def read(self):
        if not self.handle:raise ValueError('closed world')
        result=np.empty((self.sites,physical.FIELDS),dtype=np.uint64)
        if self.lib.fr_read(self.handle,_ptr(result)):
            raise RuntimeError('CUDA readback failed')
        return result

    def close(self):
        if self.handle:self.lib.fr_free(self.handle);self.handle=None

    def __enter__(self):return self
    def __exit__(self,*args):self.close()


def step_ring(cells):
    """One complete physical F step, matching the native ring API."""
    if len(cells)<15:raise ValueError('complete physical ring required')
    raw=np.array([physical.encode_cell(row) for row in cells],
                 dtype=np.uint64)
    with World(raw) as world:
        world.run(1)
        result=world.read()
    return tuple(physical.decode_cell(row.tolist()) for row in result)
