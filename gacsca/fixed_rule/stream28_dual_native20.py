"""Native execution of the fixed U=2^20 complete local description.

This compiles the *same* optimized 421-output own-rule WordCode used by the
spatial evaluator. It is a CPU implementation of one fixed local transition,
not a host interpreter of hierarchy depth or a second physical rule.
"""
import ctypes
from functools import lru_cache
import hashlib
from pathlib import Path
import subprocess

import numpy as np

from . import stream28_dual_pass20 as physical
from . import stream28_dual_pass_optimized20 as description
from .word_native_and import expression_source


def source():
    program=description.build()
    assert (program.inputs,len(program.outputs))==(
        len(physical.NEIGHBORHOOD)*physical.FIELDS,physical.FIELDS)
    header='#include <stdint.h>\n#include <stddef.h>\n#include <string.h>\n'
    body=expression_source(program,'stream28_dual20_local')
    ring=(
        '\nvoid stream28_dual20_ring(const uint64_t*src,uint64_t*dst,size_t n){\n'
        ' for(size_t i=0;i<n;++i){\n'
        f'  uint64_t in[15*{physical.FIELDS}];\n'
        '  for(int j=-7;j<=7;++j){\n'
        '   size_t k=(size_t)(((long long)i+j+(long long)n)%((long long)n));\n'
        f'   for(int w=0;w<{physical.FIELDS};++w)'
        f' in[(j+7)*{physical.FIELDS}+w]=src[k*{physical.FIELDS}+w];\n'
        '  }\n'
        f'  stream28_dual20_local(in,dst+i*{physical.FIELDS});\n'
        ' }\n}\n')
    return header+body+ring


@lru_cache(maxsize=1)
def library():
    code=source()
    digest=hashlib.sha256(code.encode()).hexdigest()[:20]
    directory=(Path(__file__).resolve().parents[2]/'figs/fixed_rule/build'/
               ('stream28_dual_native20_'+digest))
    directory.mkdir(parents=True,exist_ok=True)
    cpp=directory/'rule.c'
    target=directory/'rule.so'
    if cpp.exists():
        if cpp.read_text()!=code:raise AssertionError('native source collision')
    else:cpp.write_text(code)
    if not target.exists():
        with (directory/'build.log').open('w') as log:
            subprocess.run(['cc','-O1','-std=c99','-Wall','-Wextra','-Werror',
                            '-shared','-fPIC',str(cpp),'-o',str(target)],
                           stdout=log,stderr=subprocess.STDOUT,check=True)
    lib=ctypes.CDLL(str(target))
    ptr=ctypes.POINTER(ctypes.c_uint64)
    lib.stream28_dual20_local.argtypes=[ptr,ptr]
    lib.stream28_dual20_local.restype=None
    lib.stream28_dual20_ring.argtypes=[ptr,ptr,ctypes.c_size_t]
    lib.stream28_dual20_ring.restype=None
    return lib


def _ptr(array):
    return array.ctypes.data_as(ctypes.POINTER(ctypes.c_uint64))


def local_step(neighbors):
    if len(neighbors)!=len(physical.NEIGHBORHOOD):
        raise ValueError('exact radius-seven neighborhood required')
    words=np.array([physical.encode_cell(cell) for cell in neighbors],
                   dtype=np.uint64)
    result=np.empty(physical.FIELDS,dtype=np.uint64)
    library().stream28_dual20_local(_ptr(words),_ptr(result))
    return physical.decode_cell(result.tolist())


def step_ring(cells):
    if len(cells)<15:raise ValueError('complete ring of at least 15 cells required')
    words=np.array([physical.encode_cell(cell) for cell in cells],
                   dtype=np.uint64)
    result=np.empty_like(words)
    library().stream28_dual20_ring(_ptr(words),_ptr(result),len(words))
    return tuple(physical.decode_cell(row.tolist()) for row in result)
