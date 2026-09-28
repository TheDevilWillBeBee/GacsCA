"""Exact compact representation; physical evolution stays in the fixed C rule.

Canonical padding has no heads or data bits and a non-memory opcode. Its two
packet tracks translate independently. No upper-cell transition is called here.
"""
import ctypes
import hashlib
from pathlib import Path
import subprocess
import numpy as np
from . import windowed as rule,window_program
from .windowed_native import validate,pointer


def library():
    root=Path(__file__).parent
    sources=[root/name for name in ('window_world.c','windowed_native.c','window_core.c')]
    header='#define ROM_ROWS '+str(len(rule.rom()))+'\n'
    header+='static const uint16_t PROJECTED_ROM[ROM_ROWS][7] = {\n'
    header+='\n'.join('{'+','.join(map(str,row))+'},' for row in rule.rom().tolist())+'\n};\n'
    digest=hashlib.sha256(b''.join(p.read_bytes() for p in sources)+header.encode()+b'cc-O3-window-world-v1').hexdigest()[:16]
    build=root.resolve().parents[1]/'figs/fixed_rule/build'/('window_world_'+digest)
    build.mkdir(parents=True,exist_ok=True); target=build/'world.so'
    if not target.exists():
        (build/'projection_rom.h').write_text(header)
        subprocess.run(['cc','-O3','-std=c99','-Wall','-Wextra','-Werror','-shared','-fPIC',
                        '-I',str(build),str(sources[0]),'-o',str(target)],check=True)
    lib=ctypes.CDLL(str(target)); ptr=ctypes.POINTER(ctypes.c_uint32); handle=ctypes.c_void_p
    lib.fw_create.argtypes=[ptr,ctypes.c_size_t];lib.fw_create.restype=handle
    lib.fw_free.argtypes=[handle];lib.fw_free.restype=None
    lib.fw_run.argtypes=[handle,ctypes.c_uint64,ctypes.POINTER(ctypes.c_uint64),ctypes.c_int];lib.fw_run.restype=ctypes.c_int
    lib.fw_time.argtypes=[handle];lib.fw_time.restype=ctypes.c_uint64
    lib.fw_pending.argtypes=[handle];lib.fw_pending.restype=ctypes.c_size_t
    lib.fw_cell.argtypes=[handle,ctypes.c_size_t,ctypes.c_uint32,ptr];lib.fw_cell.restype=ctypes.c_int
    return lib


class World:
    def __init__(self,cores):
        validate(cores)
        size=window_program.layout().computation_cells
        if len(cores)%size: raise ValueError('complete computation windows required')
        self.cores=cores.copy();self.colonies=len(cores)//size;self.lib=library()
        self.handle=self.lib.fw_create(pointer(self.cores),self.colonies)
        if not self.handle: raise ValueError('noncanonical physical Address or allocation failure')
        self.cores.flags.writeable=False

    @classmethod
    def encode(cls,cells):
        return cls(rule.encode_cores(cells))

    def close(self):
        if self.handle: self.lib.fw_free(self.handle);self.handle=None

    def __enter__(self): return self
    def __exit__(self,*args): self.close()

    @property
    def time(self): return int(self.lib.fw_time(self.handle))
    @property
    def pending(self): return int(self.lib.fw_pending(self.handle))

    def run(self,ticks,*,skip_wait=True):
        if self.handle is None: raise ValueError('closed world')
        if not isinstance(ticks,int) or not 0<=ticks<1<<64: raise ValueError('invalid tick count')
        metrics=(ctypes.c_uint64*4)()
        code=self.lib.fw_run(self.handle,ticks,metrics,int(skip_wait))
        if code: raise RuntimeError(f'window evolution failed: {code}')
        return dict(zip(('physical_ticks','literal_core_ticks','wait_ticks_skipped','local_evaluations'),map(int,metrics)))

    def cell(self,colony,address):
        if self.handle is None: raise ValueError('closed world')
        if not 0<=colony<self.colonies or not 0<=address<window_program.layout().colony_cells:
            raise ValueError('physical site outside colony ring')
        out=np.empty((1,len(rule.SCHEMA)),dtype=np.uint32)
        if self.lib.fw_cell(self.handle,colony,address,pointer(out)): raise ValueError('site outside ring')
        return rule.cells_from_array(out)[0]

    def decode(self): return rule.decode_cores(self.cores)
    def check_boundary(self):
        if self.pending: raise ValueError('packets remain in padding')
        return rule.check_boundary(self.cores)
