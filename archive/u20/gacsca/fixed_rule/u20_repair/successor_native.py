"""Private C executor for the alphabet-extended lookup candidate."""
import ctypes
import hashlib
from pathlib import Path
import subprocess

import numpy as np

from ..word_native_and import expression_source
from . import successor,successor_optimized


BUILD=Path(__file__).resolve().parents[3]/'figs/fixed_rule/u20_repair/build'


def source():
    program=successor_optimized.build()
    return ('#include <stdint.h>\n#include <stddef.h>\n#include <string.h>\n'
            +expression_source(program,'u20_lookup_successor_step')
            +'\nvoid u20_lookup_successor_ring(const uint64_t *src,uint64_t *dst,size_t n){\n'
            +' for(size_t i=0;i<n;++i){\n'
            +f'  uint64_t in[15*{successor.FIELDS}];\n'
            +'  for(int j=-7;j<=7;++j){\n'
            +'   size_t k=(size_t)(((long long)i+j+(long long)n)%((long long)n));\n'
            +f'   for(int w=0;w<{successor.FIELDS};++w)'
            +f' in[(j+7)*{successor.FIELDS}+w]=src[k*{successor.FIELDS}+w];\n'
            +'  }\n'
            +f'  u20_lookup_successor_step(in,dst+i*{successor.FIELDS});\n'
            +' }\n}\n')


def library():
    code=source()
    digest=hashlib.sha256(code.encode()).hexdigest()
    directory=BUILD/digest[:20]
    directory.mkdir(parents=True,exist_ok=True)
    source_path=directory/'rule.c'
    target=directory/'rule.so'
    if source_path.exists() and source_path.read_text()!=code:
        raise AssertionError('private source collision')
    if not source_path.exists():source_path.write_text(code)
    if not target.exists():
        with (directory/'build.log').open('w') as log:
            subprocess.run(['cc','-O1','-std=c99','-Wall','-Wextra','-Werror',
                            '-shared','-fPIC',str(source_path),'-o',str(target)],
                           stdout=log,stderr=subprocess.STDOUT,check=True)
    lib=ctypes.CDLL(str(target))
    ptr=ctypes.POINTER(ctypes.c_uint64)
    lib.u20_lookup_successor_step.argtypes=[ptr,ptr]
    lib.u20_lookup_successor_step.restype=None
    lib.u20_lookup_successor_ring.argtypes=[ptr,ptr,ctypes.c_size_t]
    lib.u20_lookup_successor_ring.restype=None
    return lib,digest,str(target)


def evaluate(words):
    if len(words)!=15*successor.FIELDS:
        raise ValueError('complete radius-seven successor input required')
    ins=np.asarray(words,dtype=np.uint64)
    out=np.empty(successor.FIELDS,dtype=np.uint64)
    lib,_,_=library()
    ptr=ctypes.POINTER(ctypes.c_uint64)
    lib.u20_lookup_successor_step(ins.ctypes.data_as(ptr),out.ctypes.data_as(ptr))
    return tuple(map(int,out))


def step_ring(raw):
    if raw.ndim!=2 or raw.shape[1]!=successor.FIELDS or len(raw)<15:
        raise ValueError('complete radius-seven successor ring required')
    ins=np.ascontiguousarray(raw,dtype=np.uint64)
    out=np.empty_like(ins)
    lib,_,_=library()
    ptr=ctypes.POINTER(ctypes.c_uint64)
    lib.u20_lookup_successor_ring(ins.ctypes.data_as(ptr),
                                  out.ctypes.data_as(ptr),len(ins))
    return out
