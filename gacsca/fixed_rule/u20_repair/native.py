"""Private native executor for the corrected U20 WordCode."""
import ctypes
import hashlib
from pathlib import Path
import subprocess

import numpy as np

from ..word_native_and import expression_source
from .. import stream28_dual_pass20 as physical
from . import description


BUILD = Path(__file__).resolve().parents[3] / 'figs/fixed_rule/u20_repair/build'


def source():
    program = description.build()
    return ('#include <stdint.h>\n#include <stddef.h>\n#include <string.h>\n'
            + expression_source(program, 'u20_repair_step')
            + '\nvoid u20_repair_ring(const uint64_t *src,uint64_t *dst,size_t n){\n'
            + ' for(size_t i=0;i<n;++i){\n'
            + f'  uint64_t in[15*{physical.FIELDS}];\n'
            + '  for(int j=-7;j<=7;++j){\n'
            + '   size_t k=(size_t)(((long long)i+j+(long long)n)%((long long)n));\n'
            + f'   for(int w=0;w<{physical.FIELDS};++w)'
            + f' in[(j+7)*{physical.FIELDS}+w]=src[k*{physical.FIELDS}+w];\n'
            + '  }\n'
            + f'  u20_repair_step(in,dst+i*{physical.FIELDS});\n'
            + ' }\n}\n')


def library():
    code = source()
    digest = hashlib.sha256(code.encode()).hexdigest()
    directory = BUILD / digest[:20]
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / 'rule.c'
    target = directory / 'rule.so'
    if path.exists() and path.read_text() != code:
        raise AssertionError('native source collision')
    if not path.exists():
        path.write_text(code)
    if not target.exists():
        with (directory / 'build.log').open('w') as log:
            subprocess.run(['cc', '-O1', '-std=c99', '-Wall', '-Wextra', '-Werror',
                            '-shared', '-fPIC', str(path), '-o', str(target)],
                           stdout=log, stderr=subprocess.STDOUT, check=True)
    lib = ctypes.CDLL(str(target))
    pointer = ctypes.POINTER(ctypes.c_uint64)
    lib.u20_repair_step.argtypes = [pointer, pointer]
    lib.u20_repair_step.restype = None
    lib.u20_repair_ring.argtypes = [pointer, pointer, ctypes.c_size_t]
    lib.u20_repair_ring.restype = None
    return lib, digest, str(target)


def evaluate(words):
    program = description.build()
    if len(words) != program.inputs:
        raise ValueError('complete radius-seven input required')
    ins = np.asarray(words, dtype=np.uint64)
    out = np.empty(len(program.outputs), dtype=np.uint64)
    lib, _, _ = library()
    ptr = ctypes.POINTER(ctypes.c_uint64)
    lib.u20_repair_step(ins.ctypes.data_as(ptr), out.ctypes.data_as(ptr))
    return tuple(map(int, out))


def step_ring(raw):
    if raw.ndim!=2 or raw.shape[1]!=physical.FIELDS or len(raw)<15:
        raise ValueError('complete radius-seven closed ring required')
    ins=np.ascontiguousarray(raw,dtype=np.uint64)
    out=np.empty_like(ins)
    lib,_,_=library()
    ptr=ctypes.POINTER(ctypes.c_uint64)
    lib.u20_repair_ring(ins.ctypes.data_as(ptr),out.ctypes.data_as(ptr),len(ins))
    return out
