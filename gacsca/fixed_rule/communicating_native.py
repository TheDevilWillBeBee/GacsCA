"""Owned CPU backend for the communicating rule; no GPU dependencies."""
import ctypes
import hashlib
from pathlib import Path
import subprocess
import numpy as np
from .communicating import Cell, SCHEMA

COL = {name: i for i, (name, _) in enumerate(SCHEMA)}


def array_from_cells(cells):
    return np.array([[getattr(cell, name) for name, _ in SCHEMA] for cell in cells], dtype=np.uint32)


def cells_from_array(array):
    return tuple(Cell(**{name: int(row[i]) for name, i in COL.items()}) for row in array)


def library():
    source = Path(__file__).with_name('communicating_native.c')
    build = Path(__file__).resolve().parents[2] / 'figs/fixed_rule/build'
    build.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(source.read_bytes() + b'cc-O3-std=c99-communicating-v1').hexdigest()[:16]
    target = build / f'communicating_{digest}.so'
    if not target.exists():
        subprocess.run(['cc', '-O3', '-std=c99', '-Wall', '-Wextra', '-Werror',
                        '-shared', '-fPIC', str(source), '-o', str(target)], check=True)
    lib = ctypes.CDLL(str(target))
    ptr = ctypes.POINTER(ctypes.c_uint32)
    lib.fm_local.argtypes = [ptr, ptr, ptr, ptr]
    lib.fm_local.restype = None
    lib.fm_dense.argtypes = [ptr, ptr, ctypes.c_size_t]
    lib.fm_dense.restype = None
    lib.fm_run.argtypes = [ptr, ctypes.c_size_t, ctypes.c_uint64, ctypes.POINTER(ctypes.c_uint64)]
    lib.fm_run.restype = ctypes.c_int
    return lib


def validate(array):
    if (not isinstance(array, np.ndarray) or array.dtype != np.uint32 or
            not array.flags.c_contiguous or array.ndim != 2 or array.shape[1] != len(SCHEMA) or not len(array)):
        raise ValueError('nonempty C-contiguous uint32 state array required')
    for name, width in SCHEMA:
        if np.any(array[:, COL[name]] >= 1 << width):
            raise ValueError('state outside fixed alphabet')


def pointer(array):
    return array.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32))


def dense_step(array, lib=None):
    validate(array)
    out = np.empty_like(array)
    (lib or library()).fm_dense(pointer(array), pointer(out), len(array))
    return out


def run(array, ticks, lib=None):
    validate(array)
    if not isinstance(ticks, int) or not 0 <= ticks < 1 << 64:
        raise ValueError('invalid tick budget')
    evaluations = ctypes.c_uint64()
    code = (lib or library()).fm_run(pointer(array), len(array), ticks, ctypes.byref(evaluations))
    if code:
        raise ValueError(f'sparse controller invariant or allocation failure: {code}')
    return {'physical_ticks': ticks, 'local_evaluations': evaluations.value}
