"""Fully literal dense CUDA executor with compact inputs and coalesced state.

This is a performance backend for the same complete U20 physical rule. It
executes one fixed radius-seven transition at every site on every requested
tick; the host never computes or skips a simulated transition.
"""
import ctypes
from functools import lru_cache
import hashlib
from pathlib import Path
import subprocess

import numpy as np

from .. import stream28_dual_pass20 as physical
from . import description
from ..word_allocation_and import allocate, verify
from ..wordcode_and import LIT, NAND, AND, ADD, SHR, EQ, LT


WORKERS = 262144


def generated_header():
    program = description.build()
    if (program.inputs, len(program.outputs)) != (15 * physical.FIELDS,
                                                 physical.FIELDS):
        raise AssertionError('complete fixed-rule description required')
    allocation = allocate(program)
    verify(program, allocation)
    used = sorted({wire for op, a, b in program.operations if op != LIT
                   for wire in (a, b) if wire < program.inputs} |
                  {wire for wire in program.outputs if wire < program.inputs})
    input_slot = {wire: index for index, wire in enumerate(used)}

    def ref(wire):
        if wire < program.inputs:
            return f'in[{input_slot[wire] * WORKERS}]'
        return f'tmp[{allocation.slots[wire - program.inputs] * WORKERS}]'

    lines = [f'#define FIELDS {physical.FIELDS}',
             f'#define WORKERS {WORKERS}',
             f'#define USED_INPUTS {len(used)}',
             f'#define WORKSPACE_WORDS {(len(used) + allocation.count) * WORKERS}',
             '__device__ __forceinline__ void gather_inputs(const uint64_t* state, '
             'size_t sites, const size_t* sources, uint64_t* in) {']
    lines.extend(f' in[{slot * WORKERS}]=state[(size_t){wire % physical.FIELDS}*sites+'
                 f'sources[{wire // physical.FIELDS}]];'
                 for slot, wire in enumerate(used))
    lines.extend(['}',
                  '__device__ __noinline__ void fixed_local(const uint64_t* in, '
                  'uint64_t* out, size_t pos, size_t sites, uint64_t* tmp) {'])
    for index, (op, a, b) in enumerate(program.operations):
        if op == LIT: expr = f'UINT64_C(0x{a:016x})'
        elif op == NAND: expr = f'~({ref(a)}&{ref(b)})'
        elif op == AND: expr = f'{ref(a)}&{ref(b)}'
        elif op == ADD: expr = f'{ref(a)}+{ref(b)}'
        elif op == SHR: expr = f'{ref(b)}<64?{ref(a)}>>{ref(b)}:0'
        elif op == EQ: expr = f'{ref(a)}=={ref(b)}'
        elif op == LT: expr = f'{ref(a)}<{ref(b)}'
        else: raise ValueError(('unsupported own-rule opcode', op))
        lines.append(f' tmp[{allocation.slots[index] * WORKERS}]={expr};')
    lines.extend(f' out[(size_t){index}*sites+pos]={ref(wire)};'
                 for index, wire in enumerate(program.outputs))
    lines.append('}')
    return '\n'.join(lines) + '\n'


@lru_cache(maxsize=1)
def library():
    source = Path(__file__).with_suffix('.cu')
    header = generated_header()
    identity = hashlib.sha256(source.read_bytes() + header.encode() +
                              b'nvcc-O2-sm80-compact-soa-unrolled-maxrreg128-v5').hexdigest()[:20]
    build = (Path(__file__).resolve().parents[3] /
             'figs/fixed_rule/gpu_validation/build' / ('dense_' + identity))
    build.mkdir(parents=True, exist_ok=True)
    (build / 'generated.h').write_text(header)
    target = build / 'rule.so'
    if not target.exists():
        with (build / 'build.log').open('w') as log:
            subprocess.run(['/usr/local/cuda/bin/nvcc', '-O2', '-std=c++17',
                            '-arch=sm_80', '-maxrregcount=128', '--shared',
                            '-Xcompiler', '-fPIC',
                            '-I', str(build), str(source), '-o', str(target)],
                           check=True, stdout=log, stderr=subprocess.STDOUT)
    lib = ctypes.CDLL(str(target))
    ptr = ctypes.POINTER(ctypes.c_uint64)
    handle = ctypes.c_void_p
    signatures = {
        'fr_create': [ctypes.c_size_t, ptr, ctypes.c_uint64,
                      ctypes.POINTER(handle), ptr],
        'fr_run': [handle, ctypes.c_uint64],
        'fr_read': [handle, ptr],
        'fr_free': [handle],
    }
    for name, args in signatures.items():
        fn = getattr(lib, name)
        fn.argtypes = args
        fn.restype = None if name == 'fr_free' else ctypes.c_int
    return lib


def _ptr(array):
    return array.ctypes.data_as(ctypes.POINTER(ctypes.c_uint64))


class World:
    def __init__(self, raw, *, device_budget=8 * 1024**3):
        if (not isinstance(raw, np.ndarray) or raw.dtype != np.uint64 or
                raw.ndim != 2 or raw.shape[1] != physical.FIELDS or
                len(raw) < 15 or len(raw) > 1 << 24):
            raise ValueError('complete uint64 physical ring of at least 15 cells required')
        if type(device_budget) is not int or not 1 <= device_budget <= 80 * 1024**3:
            raise ValueError('explicit bounded device budget required')
        widths = description.WIDTHS[7 * physical.FIELDS:8 * physical.FIELDS]
        for word, width in enumerate(widths):
            if width < 64 and np.any(raw[:, word] >= np.uint64(1 << width)):
                raise ValueError(('physical alphabet exceeded', word))
        self.lib = library()
        self.handle = ctypes.c_void_p()
        bytes_used = ctypes.c_uint64()
        array = np.ascontiguousarray(raw)
        code = self.lib.fr_create(len(array), _ptr(array), device_budget,
                                  ctypes.byref(self.handle), ctypes.byref(bytes_used))
        if code: raise RuntimeError(('CUDA allocation failed', code))
        self.sites = len(array)
        self.device_bytes = int(bytes_used.value)
        self.peak_init_or_read_bytes = self.device_bytes + array.nbytes
        self.time = 0

    def run(self, ticks):
        if not self.handle or type(ticks) is not int or not 0 <= ticks <= physical.U:
            raise ValueError('live world and bounded physical duration required')
        code = self.lib.fr_run(self.handle, ticks)
        if code: raise RuntimeError(('CUDA physical evolution failed', code))
        self.time += ticks
        return dict(ticks=ticks, complete_site_transitions=ticks * self.sites)

    def read(self):
        if not self.handle: raise ValueError('closed world')
        result = np.empty((self.sites, physical.FIELDS), dtype=np.uint64)
        if self.lib.fr_read(self.handle, _ptr(result)):
            raise RuntimeError('CUDA readback failed')
        return result

    def close(self):
        if self.handle: self.lib.fr_free(self.handle); self.handle = None

    def __enter__(self): return self
    def __exit__(self, *args): self.close()
