"""Compile one constant-ROM CPU rule, independent of size and hierarchy depth."""
import ctypes
import hashlib
from pathlib import Path
import subprocess
import numpy as np
from . import windowed as rule


def library():
    source=Path(__file__).with_name('windowed_native.c')
    base=source.with_name('window_core.c')
    header='#define ROM_ROWS '+str(len(rule.rom()))+'\n'
    header+='static const uint16_t PROJECTED_ROM[ROM_ROWS][7] = {\n'
    header+='\n'.join('{'+','.join(map(str,row))+'},' for row in rule.rom().tolist())
    header+='\n};\n'
    digest=hashlib.sha256(source.read_bytes()+base.read_bytes()+header.encode()+b'cc-O3-windowed-v1').hexdigest()[:16]
    build=Path(__file__).resolve().parents[2]/'figs/fixed_rule/build'/('windowed_'+digest)
    target=build/'windowed.so'
    build.mkdir(parents=True,exist_ok=True)
    if not target.exists():
        (build/'projection_rom.h').write_text(header)
        subprocess.run(['cc','-O3','-std=c99','-Wall','-Wextra','-Werror','-shared','-fPIC',
                        '-I',str(build),str(source),'-o',str(target)],check=True)
    lib=ctypes.CDLL(str(target))
    ptr=ctypes.POINTER(ctypes.c_uint32)
    lib.fp_local.argtypes=[ptr,ptr,ptr,ptr]
    lib.fp_local.restype=None
    lib.fp_dense.argtypes=[ptr,ptr,ctypes.c_size_t]
    lib.fp_dense.restype=None
    lib.fp_run.argtypes=[ptr,ctypes.c_size_t,ctypes.c_uint64,ctypes.POINTER(ctypes.c_uint64)]
    lib.fp_run.restype=ctypes.c_int
    return lib


def validate(array):
    if (not isinstance(array,np.ndarray) or array.dtype!=np.uint32 or not array.flags.c_contiguous or
            array.ndim!=2 or array.shape[1]!=len(rule.SCHEMA) or not len(array)):
        raise ValueError('nonempty contiguous windowed uint32 array required')
    for name,width in rule.SCHEMA:
        if np.any(array[:,rule.COL[name]]>=1<<width):
            raise ValueError('state outside fixed windowed alphabet')


def pointer(array):
    return array.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32))


def dense_step(array,lib=None):
    validate(array)
    out=np.empty_like(array)
    (lib or library()).fp_dense(pointer(array),pointer(out),len(array))
    return out


def run(array,ticks,lib=None):
    validate(array)
    if not isinstance(ticks,int) or not 0<=ticks<1<<64:
        raise ValueError('invalid physical tick budget')
    evaluations=ctypes.c_uint64()
    code=(lib or library()).fp_run(pointer(array),len(array),ticks,ctypes.byref(evaluations))
    if code:
        raise MemoryError(f'windowed execution allocation failure: {code}')
    return dict(physical_ticks=ticks,local_evaluations=evaluations.value)
