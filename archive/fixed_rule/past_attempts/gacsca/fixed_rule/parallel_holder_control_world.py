"""Exact mail-free controller/Signal suffix component, with flags separate.

Stored arrays here are a quotient with all four flag fields zero. They become
physical states only when composed with the actual independently evolved flag
component. Initial and every output mail word must be zero; otherwise reject.
The physical rule and its immutable self-description/ROM are unchanged.
"""
import ctypes
from functools import lru_cache
import hashlib
from pathlib import Path
import subprocess
import numpy as np
from . import parallel_holder_core as full,parallel_holder_quotient as rule,parallel_holder_program as program
from .parallel_holder_control_description import build
from .word_native import expression_source


def kernel_header():
    text='#include <stdint.h>\n#include <stddef.h>\n#include <stdlib.h>\n#include <string.h>\n'
    text+='#define COLONY_CELLS UINT64_C('+str(full.Q)+')\n#define STRUCT_PERIOD UINT64_C('+str(full.U)+')\n'
    text+='enum {'+','.join(n.upper() for n,_ in full.SCHEMA)+',FIELDS};\n'
    text+='enum {'+','.join('P_'+n.upper() for n,_ in rule.SCHEMA)+',P_FIELDS};\n'
    text+='enum {MEM=0,LOOP=6,WAIT=10,FETCH=0};\n'
    text+='#define MEMORY_ROWS '+str(program.layout().memory_count)+'\n#define PROGRAM_ROWS '+str(len(program.layout().instructions))+'\n'
    text+='#define ROM_ROWS '+str(len(rule.rom()))+'\nstatic const uint64_t PROJECTED_ROM[ROM_ROWS][7]={\n'
    text+='\n'.join('{'+','.join('UINT64_C(0x%016x)'%value for value in row)+'},' for row in rule.rom().tolist())+'\n};\n'
    text+='static const int static_fields[7]={'+','.join(n.upper() for n in full.STATIC)+'};\n'
    text+='static const int dynamic_fields[P_FIELDS]={'+','.join(n.upper() for n,_ in rule.SCHEMA)+'};\n'
    text+='''static void lift_projected(const uint64_t *p,uint64_t *u) {
 uint64_t a=p[P_ADDRESS];
 for(int j=0;j<7;++j)u[static_fields[j]]=a<ROM_ROWS?PROJECTED_ROM[a][j]:0;
 if(a>=ROM_ROWS){u[KIND]=a>=COLONY_CELLS-5?MEM:LOOP;u[INDEX]=a;u[A]=a>=COLONY_CELLS-5?31:0;}
 for(int j=0;j<P_FIELDS;++j)u[dynamic_fields[j]]=p[j];
}
static int waiting(const uint64_t *u){return u[HEAD]&&!u[DIRECTION]&&u[PHASE]==FETCH&&u[KIND]==WAIT&&u[INDEX]==u[PC]&&u[RD]>0;}
'''
    text+=expression_source(build(),'ww_prefix_local')
    return text


@lru_cache(maxsize=1)
def library():
    source=Path(__file__).with_name('parallel_holder_control_world.c');header=kernel_header()
    digest=hashlib.sha256(source.read_bytes()+header.encode()+b'cc-O2-delivery-control-v1').hexdigest()[:16]
    builddir=source.resolve().parents[2]/'figs/fixed_rule/build'/('parallel_holder_control_'+digest);builddir.mkdir(parents=True,exist_ok=True)
    target=builddir/'world.so'
    if not target.exists():
        (builddir/'parallel_holder_control_kernel.h').write_text(header)
        subprocess.run(['cc','-O2','-std=c99','-Wall','-Wextra','-Werror','-shared','-fPIC','-I',str(builddir),str(source),'-o',str(target)],check=True)
    lib=ctypes.CDLL(str(target));ptr=ctypes.POINTER(ctypes.c_uint64);handle=ctypes.c_void_p
    lib.fw_create.argtypes=[ptr,ctypes.c_size_t];lib.fw_create.restype=handle
    lib.fw_free.argtypes=[handle];lib.fw_free.restype=None
    lib.fw_run.argtypes=[handle,ctypes.c_uint64,ptr,ctypes.c_int];lib.fw_run.restype=ctypes.c_int
    lib.fw_time.argtypes=[handle];lib.fw_time.restype=ctypes.c_uint64
    lib.fw_pending.argtypes=[handle];lib.fw_pending.restype=ctypes.c_size_t
    lib.fw_cell.argtypes=[handle,ctypes.c_size_t,ctypes.c_uint64,ptr];lib.fw_cell.restype=ctypes.c_int
    lib.ww_prefix_local.argtypes=[ptr,ptr];lib.ww_prefix_local.restype=None
    return lib


def pointer(array):return array.ctypes.data_as(ctypes.POINTER(ctypes.c_uint64))


class World:
    def __init__(self,cores):
        if not isinstance(cores,np.ndarray) or cores.dtype!=np.uint64 or cores.ndim!=2 or cores.shape[1]!=len(rule.SCHEMA) or not cores.flags.c_contiguous or not len(cores):raise ValueError('complete contiguous projected cores required')
        for name,width in rule.SCHEMA:
            if width<64 and np.any(cores[:,rule.COL[name]]>=1<<width):raise ValueError('state outside alphabet')
        g=program.layout()
        if not g.timing_certificate()['fits']:raise ValueError('fixed program exceeds stage capacity')
        if len(cores)%(g.computation_cells+5):raise ValueError('complete computation windows required')
        self._cores=cores.copy();self.colonies=len(cores)//(g.computation_cells+5);self.epoch=int(cores[0,rule.COL['age']]);self.lib=library()
        self.handle=self.lib.fw_create(pointer(self._cores),self.colonies)
        if not self.handle:raise ValueError('canonical Address, uniform suffix Age, zero quotient flags/mail and no tail heads required')
        # Signal support is fixed after capture. Check the precise five-copy
        # pattern needed by the compressed-padding and quiet guards.
        shaped=self._cores.reshape(self.colonies,g.computation_cells+5,len(rule.SCHEMA))
        try:
            for row in shaped:
                expected=np.zeros(len(row),dtype=np.uint64)
                for sites in (np.arange(1,6),np.arange(g.computation_cells,g.computation_cells+5)):
                    bit=(int(row[sites[2],rule.COL['signal']])>>2)&1
                    expected[sites]=np.array([16,8,4,2,1],dtype=np.uint64)*bit
                if not np.array_equal(row[:,rule.COL['signal']],expected):raise ValueError('coherent boundary signals required')
        except Exception:
            self.close();raise
        self._cores.flags.writeable=False
    def close(self):
        if self.handle:self.lib.fw_free(self.handle);self.handle=None
    def __enter__(self):return self
    def __exit__(self,*args):self.close()
    @property
    def time(self):return int(self.lib.fw_time(self.handle))
    @property
    def pending(self):return int(self.lib.fw_pending(self.handle))
    @property
    def stored(self):
        array=self._cores.copy();array[:,rule.COL['age']]=(self.epoch+self.time)%full.U;return array
    @property
    def cores(self):
        g=program.layout();a=self.stored.reshape(self.colonies,g.computation_cells+5,len(rule.SCHEMA))
        return np.ascontiguousarray(a[:,:g.computation_cells].reshape(-1,len(rule.SCHEMA)))
    @property
    def tails(self):
        g=program.layout();a=self.stored.reshape(self.colonies,g.computation_cells+5,len(rule.SCHEMA))
        return np.ascontiguousarray(a[:,g.computation_cells:])
    def run(self,ticks,*,skip_wait=True,skip_scan=True):
        if self.handle is None:raise ValueError('closed world')
        if not isinstance(ticks,int) or not 0<=ticks<1<<64:raise ValueError('invalid ticks')
        metrics=(ctypes.c_uint64*5)();code=self.lib.fw_run(self.handle,ticks,metrics,int(skip_wait)|2*int(skip_scan))
        if code:raise RuntimeError(f'word execution failed: {code}')
        return dict(zip(('physical_ticks','literal_core_ticks','quiet_ticks_skipped','scan_ticks_skipped','local_evaluations'),map(int,metrics)))
    def cell(self,colony,address):
        if self.handle is None:raise ValueError('closed world')
        if not 0<=colony<self.colonies or not 0<=address<full.Q:raise ValueError('site outside ring')
        out=np.empty((1,len(rule.SCHEMA)),dtype=np.uint64)
        if self.lib.fw_cell(self.handle,colony,address,pointer(out)):raise ValueError('invalid site')
        return rule.decode_cell(out[0].tolist())
    def decode(self):return rule.decode_cores(self.cores)
