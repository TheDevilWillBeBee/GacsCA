"""Physical execution on canonical healthy structure with an explicit Age clock.

Age is an actual CA field, included in the full self-description. This reference
represents its proven uniform increment lazily; it never installs upper outputs.
Damaged physical structure is rejected. Simulated damaged structure is ordinary
encoded data and is processed by the complete described rule.
"""
import ctypes
import hashlib
from pathlib import Path
import subprocess
import numpy as np
from . import clock_rule as full,clock_projected as rule,clock_program as program
from .clock_description import build
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
 if(a>=ROM_ROWS){u[KIND]=LOOP;u[INDEX]=a;}
 for(int j=0;j<P_FIELDS;++j)u[dynamic_fields[j]]=p[j];
}
static int waiting(const uint64_t *u){return u[HEAD]&&!u[DIRECTION]&&u[PHASE]==FETCH&&u[KIND]==WAIT&&u[INDEX]==u[PC]&&u[RD]>0;}
'''
    text+=expression_source(build(healthy_domain=True),'ww_healthy_local')
    text+='''static void fp_local(const uint64_t *l,const uint64_t *c,const uint64_t *r,const uint64_t *r2,uint64_t *out,uint64_t age) {
 uint64_t inputs[5*FIELDS]={0},o[FIELDS];
 lift_projected(l,inputs+FIELDS);lift_projected(c,inputs+2*FIELDS);lift_projected(r,inputs+3*FIELDS);lift_projected(r2,inputs+4*FIELDS);
 for(int j=0;j<5;++j)inputs[j*FIELDS+AGE]=age;
 ww_healthy_local(inputs,o);
 for(int j=0;j<P_FIELDS;++j)out[j]=o[dynamic_fields[j]];
}
'''
    return text


def library():
    source=Path(__file__).with_suffix('.c');header=kernel_header()
    digest=hashlib.sha256(source.read_bytes()+header.encode()+b'cc-O2-clock-world-v1').hexdigest()[:16]
    builddir=source.resolve().parents[2]/'figs/fixed_rule/build'/('clock_world_'+digest);builddir.mkdir(parents=True,exist_ok=True)
    target=builddir/'world.so'
    if not target.exists():
        (builddir/'clock_world_kernel.h').write_text(header)
        subprocess.run(['cc','-O2','-std=c99','-Wall','-Wextra','-Werror','-shared','-fPIC','-I',str(builddir),str(source),'-o',str(target)],check=True)
    lib=ctypes.CDLL(str(target));ptr=ctypes.POINTER(ctypes.c_uint64);handle=ctypes.c_void_p
    lib.fw_create.argtypes=[ptr,ctypes.c_size_t];lib.fw_create.restype=handle
    lib.fw_free.argtypes=[handle];lib.fw_free.restype=None
    lib.fw_run.argtypes=[handle,ctypes.c_uint64,ptr,ctypes.c_int];lib.fw_run.restype=ctypes.c_int
    lib.fw_time.argtypes=[handle];lib.fw_time.restype=ctypes.c_uint64
    lib.fw_pending.argtypes=[handle];lib.fw_pending.restype=ctypes.c_size_t
    lib.fw_cell.argtypes=[handle,ctypes.c_size_t,ctypes.c_uint64,ptr];lib.fw_cell.restype=ctypes.c_int
    lib.ww_healthy_local.argtypes=[ptr,ptr];lib.ww_healthy_local.restype=None
    return lib


def pointer(array):return array.ctypes.data_as(ctypes.POINTER(ctypes.c_uint64))


class World:
    def __init__(self,cores):
        if not isinstance(cores,np.ndarray) or cores.dtype!=np.uint64 or cores.ndim!=2 or cores.shape[1]!=len(rule.SCHEMA) or not cores.flags.c_contiguous or not len(cores):raise ValueError('complete contiguous projected cores required')
        for name,width in rule.SCHEMA:
            if width<64 and np.any(cores[:,rule.COL[name]]>=1<<width):raise ValueError('state outside alphabet')
        g=program.layout()
        if len(cores)%g.computation_cells:raise ValueError('complete computation windows required')
        self._cores=cores.copy();self.colonies=len(cores)//g.computation_cells;self.epoch=int(cores[0,rule.COL['age']]);self.lib=library()
        self.handle=self.lib.fw_create(pointer(self._cores),self.colonies)
        if not self.handle:raise ValueError('canonical Address, uniform Age and zero physical flags required')
        self._cores.flags.writeable=False
    @classmethod
    def encode(cls,cells):return cls(rule.encode_cores(cells))
    def close(self):
        if self.handle:self.lib.fw_free(self.handle);self.handle=None
    def __enter__(self):return self
    def __exit__(self,*args):self.close()
    @property
    def time(self):return int(self.lib.fw_time(self.handle))
    @property
    def pending(self):return int(self.lib.fw_pending(self.handle))
    @property
    def cores(self):
        array=self._cores.copy();array[:,rule.COL['age']]=(self.epoch+self.time)%full.U;return array
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
    def decode(self):return rule.decode_cores(self._cores)
    def check_boundary(self):
        g=program.layout();shaped=self._cores.reshape(self.colonies,g.computation_cells,len(rule.SCHEMA))
        template=rule.project_array(program.template())
        for name in ('address','head','phase','pc','direction'):
            if not np.all(shaped[:,:,rule.COL[name]]==template[None,:,rule.COL[name]]):raise ValueError(f'boundary {name}')
        for name in ('ra','rb','rd','value','alu'):
            if np.any(shaped[:,:,rule.COL[name]]):raise ValueError(f'stale headless {name}')
        for name,_ in rule.SCHEMA:
            if name.startswith(('lp_','rp_')) and np.any(shaped[:,:,rule.COL[name]]):raise ValueError('pending core packet')
        if self.pending:raise ValueError('pending padding packet')
        return True
