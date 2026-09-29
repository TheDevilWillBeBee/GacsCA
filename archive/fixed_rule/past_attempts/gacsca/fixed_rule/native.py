"""Independent CPU build and validated wrapper; never imports the CUDA backend."""
import ctypes
import hashlib
from pathlib import Path
import subprocess
import numpy as np
from .machine import SCHEMA
from .tape import COLUMNS


def library(build_dir=None):
    source = Path(__file__).with_name('native.c')
    build_dir = Path(build_dir or Path(__file__).resolve().parents[2] / 'figs/fixed_rule/build')
    build_dir.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(source.read_bytes() + b'cc-O3-std=c99-v1').hexdigest()[:16]
    target = build_dir / f'local_{digest}.so'
    if not target.exists():
        subprocess.run(['cc', '-O3', '-std=c99', '-shared', '-fPIC', str(source), '-o', str(target)], check=True)
    lib = ctypes.CDLL(str(target))
    ptr = ctypes.POINTER(ctypes.c_uint32)
    lib.fr_local.argtypes = [ptr, ptr, ptr]
    lib.fr_local.restype = None
    lib.fr_dense.argtypes = [ptr, ptr, ctypes.c_size_t]
    lib.fr_dense.restype = None
    lib.fr_run.argtypes = [ptr, ctypes.c_size_t, ctypes.c_uint64, ctypes.c_uint64,
                          ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_uint64)]
    lib.fr_run.restype = ctypes.c_int
    return lib


def validate(tape):
    if not isinstance(tape, np.ndarray) or tape.dtype != np.uint32 or not tape.flags.c_contiguous:
        raise ValueError('C-contiguous uint32 tape required')
    if tape.ndim != 2 or tape.shape[1] != len(COLUMNS) or len(tape) == 0:
        raise ValueError('incorrect tape shape')
    for j, (_, width) in enumerate(SCHEMA):
        if np.any(tape[:, j] >= 1 << width):
            raise ValueError('tape outside fixed physical alphabet')


def pointer(array):
    return array.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32))


def dense_step(tape, lib=None):
    validate(tape)
    lib = lib or library()
    out = np.empty_like(tape)
    lib.fr_dense(pointer(tape), pointer(out), len(tape))
    return out


def run(tape, *, ticks, periods=0, lib=None):
    """Mutate physical tape for literal ticks; stop after optional LOOP boundaries."""
    validate(tape)
    if not 0 <= ticks < 1 << 64 or not 0 <= periods < 1 << 64:
        raise ValueError('invalid execution budget')
    lib = lib or library()
    elapsed, complete = ctypes.c_uint64(), ctypes.c_uint64()
    code = lib.fr_run(pointer(tape), len(tape), ticks, periods,
                      ctypes.byref(elapsed), ctypes.byref(complete))
    if code:
        raise ValueError(f'single-head sparse invariant rejected: {code}')
    return {'physical_ticks': elapsed.value, 'completed_periods': complete.value}
