"""Resident nonperiodic Data banks and sparse coherent physical prefix state.

The physical F/ROM/alphabet are unchanged. This backend is restricted to
canonical Address, uniform Age, zero physical flags/Wf, zero non-MEM Data and
old Age < WF_START-1. Arbitrary controller/mail/Signal records are retained.
It is not a full-work-period or incoherent-fault executor.
"""
import ctypes
from functools import lru_cache
import hashlib
from pathlib import Path
import subprocess
import numpy as np
from . import small_holder_core as c,small_holder_rule as f,small_holder_program as p
from . import small_holder_quotient as q,small_holder_projected as r,small_holder_packed as packed
from .small_holder_prefix_description import build
from .small_holder_initial import coherent_cell
from .word_workspace_source import expression_source

SLOTS=64
CANDIDATES=11*SLOTS+32
WORKERS=256
MAX_READ=256
CHUNK=128
ACTIVE=tuple(n for n,_ in q.SCHEMA if n not in ('data','address','age','f1','f2','wf1','wf2'))


def header():
    g=p.layout()
    # Vote destinations never overwrite another vote's old history operands.
    assert not set(g.votes).intersection({a+d for a in g.votes for d in (-1,1,2)})
    text='#include <stdint.h>\n#include <stddef.h>\n#include <string.h>\n'
    constants=dict(Q=f.Q,MEM_ROWS=g.memory_count,BANK_ROWS=g.memory_count+5,ROM_ROWS=g.computation_cells,FIELDS=c.FIELDS,P_FIELDS=len(q.SCHEMA),PACKED_WORDS=packed.WORDS,SLOTS=SLOTS,CANDIDATES=CANDIDATES,WORKERS=WORKERS,READ_CAPACITY=MAX_READ,CHUNK=CHUNK,INFO_WORDS=f.FIELDS,RESET1=c.RESET_AGES[1],RESET2=c.RESET_AGES[2],VOTE0=c.VOTE_AGES[0],CAPTURE=c.CAPTURE_AGE,PREFIX_LIMIT=c.WF_START-1,END0=c.ACTIVE_ENDS[0],END1=c.ACTIVE_ENDS[1],END2=c.ACTIVE_ENDS[2])
    for name,value in constants.items():text+=f'#define {name} UINT64_C({value})\n'
    text+='enum {'+','.join(n.upper() for n,_ in c.SCHEMA)+'};\n'
    text+='enum {'+','.join('P_'+n.upper() for n,_ in q.SCHEMA)+'};\n'
    for name,values in (('FIELD_OFFSETS',packed.OFFSETS),('FIELD_WIDTHS',[w for _,w in q.SCHEMA]),('DYNAMIC_FIELDS',[c.COL[n] for n,_ in q.SCHEMA]),('STATIC_FIELDS',[c.COL[n] for n in c.STATIC]),('ACTIVE_FIELDS',[q.COL[n] for n in ACTIVE]),('INFO_POSITIONS',g.info)):
        text+='__device__ __constant__ unsigned '+name+'[]={'+','.join(map(str,values))+'};\n'
    body,allocation=expression_source(build(),'resident_prefix_local',stride=WORKERS)
    text+=f'#define ACTIVE_FIELDS_COUNT {len(ACTIVE)}\n#define TEMP_WORDS {allocation.count}\n#define WORKSPACE_WORDS ((11*FIELDS+FIELDS+TEMP_WORDS)*WORKERS)\n'
    return text+body.replace('void resident_prefix_local','__device__ __noinline__ void resident_prefix_local',1)


@lru_cache(maxsize=1)
def library():
    source=Path(__file__).with_suffix('.cu');generated=header()
    digest=hashlib.sha256(source.read_bytes()+generated.encode()+b'nvcc-O2-sm80-resident-prefix-v1').hexdigest()[:20]
    directory=source.resolve().parents[2]/'figs/fixed_rule/build'/('small_holder_resident_prefix_'+digest);directory.mkdir(parents=True,exist_ok=True);target=directory/'prefix.so'
    if not target.exists():
        (directory/'small_holder_resident_prefix_generated.h').write_text(generated)
        with (directory/'build.log').open('w') as log:subprocess.run(['/usr/local/cuda/bin/nvcc','-O2','-std=c++17','-arch=sm_80','--shared','-Xcompiler','-fPIC','-I',str(directory),str(source),'-o',str(target)],stdout=log,stderr=subprocess.STDOUT,check=True)
    lib=ctypes.CDLL(str(target));ptr=ctypes.POINTER(ctypes.c_uint64);h=ctypes.c_void_p
    lib.rp_create.argtypes=[ctypes.c_size_t,ctypes.c_uint64,ctypes.c_uint64,ptr,ctypes.POINTER(h),ptr];lib.rp_create.restype=ctypes.c_int
    lib.rp_free.argtypes=[h];lib.rp_free.restype=None
    lib.rp_info.argtypes=[h,ctypes.c_size_t,ctypes.c_size_t,ptr];lib.rp_info.restype=ctypes.c_int
    lib.rp_initial.argtypes=[h,ctypes.c_size_t,ctypes.c_size_t,ptr,ptr];lib.rp_initial.restype=ctypes.c_int
    lib.rp_jump.argtypes=[h,ctypes.c_uint64,ptr];lib.rp_jump.restype=ctypes.c_int
    lib.rp_step.argtypes=[h,ptr];lib.rp_step.restype=ctypes.c_int
    lib.rp_read.argtypes=[h,ptr,ctypes.c_size_t,ptr];lib.rp_read.restype=ctypes.c_int
    return lib


def pointer(a):return a.ctypes.data_as(ctypes.POINTER(ctypes.c_uint64))


class World:
    def __init__(self,parents,*,age=0,logical=None,device_budget=64*1024**2):
        parents=tuple(parents)
        if not parents or any(not isinstance(x,r.Cell) for x in parents):raise ValueError('complete projected parents required')
        if type(age) is not int or not 0<=age<c.WF_START-1:raise ValueError('prefix clock domain required')
        if type(device_budget) is not int or not 1<=device_budget<=8*1024**3:raise ValueError('explicit device budget up to 8 GiB required')
        logical={} if logical is None else dict(logical);n=len(parents)
        records=[[] for _ in parents]
        for position,cell in sorted(logical.items()):
            if type(position) is not int or not 0<=position<n*f.Q or not isinstance(cell,q.Cell):raise ValueError('complete in-ring logical record required')
            col,a=divmod(position,f.Q)
            if cell.address!=a or cell.age!=age or cell.f1 or cell.f2 or cell.wf1 or cell.wf2:raise ValueError('canonical zero-flag prefix domain required')
            if p.layout().memory_count<=a<f.Q-5 and cell.data:raise ValueError('non-MEM Data must be zero')
            records[col].append(cell)
        if any(len(x)>SLOTS for x in records):raise ValueError('initial sparse capacity exceeded')
        self.lib=library();self.handle=ctypes.c_void_p();allocated=ctypes.c_uint64()
        code=self.lib.rp_create(n,age,device_budget,pointer(p.base_rom()),ctypes.byref(self.handle),ctypes.byref(allocated))
        if code:raise RuntimeError(f'resident prefix allocation failed: {code}')
        self.colonies=n;self.age=age;self.epoch=age;self.device_bytes=int(allocated.value);self.evaluations=0
        try:
            for start in range(0,n,CHUNK):
                rows=np.array([f.encode_cell(r.lift(x)) for x in parents[start:start+CHUNK]],dtype=np.uint64)
                if self.lib.rp_info(self.handle,start,len(rows),pointer(rows)):raise RuntimeError('Info upload failed')
            for start in range(0,n,CHUNK):
                part=records[start:start+CHUNK]
                a=np.zeros((len(part),SLOTS,packed.WORDS),dtype=np.uint64)
                counts=np.array([len(x) for x in part],dtype=np.uint64)
                for col,rows in enumerate(part):
                    if rows:a[col,:len(rows)]=packed.pack(q.array_from_cells(rows))
                if self.lib.rp_initial(self.handle,start,len(part),pointer(a),pointer(counts)):raise RuntimeError('sparse initialization failed')
        except BaseException:self.close();raise
    def close(self):
        if self.handle:self.lib.rp_free(self.handle);self.handle=None
    def __enter__(self):return self
    def __exit__(self,*args):self.close()
    def step(self):
        if not self.handle:raise ValueError('closed prefix world')
        metrics=np.zeros(3,dtype=np.uint64);code=self.lib.rp_step(self.handle,pointer(metrics))
        if code:raise RuntimeError(f'resident prefix step rejected: {code}')
        self.age+=1;self.evaluations+=int(metrics[0])
        return dict(age=self.age,logical_evaluations=int(metrics[0]),active_records=int(metrics[1]),max_active_per_colony=int(metrics[2]))
    def run(self,ticks,*,skip=True):
        if not self.handle:raise ValueError('closed prefix world')
        if type(ticks) is not int or ticks<0 or ticks>c.WF_START-1-self.age:raise ValueError('run exceeds certified prefix')
        stop=self.age+ticks;literal=skipped=evaluations=0
        while self.age<stop:
            delta=ctypes.c_uint64()
            if skip:
                code=self.lib.rp_jump(self.handle,stop-self.age,ctypes.byref(delta))
                if code:raise RuntimeError(f'resident jump failed: {code}')
            if delta.value:self.age+=int(delta.value);skipped+=int(delta.value)
            else:
                metrics=self.step();literal+=1;evaluations+=metrics['logical_evaluations']
        return dict(physical_ticks=ticks,literal_ticks=literal,transport_or_quiet_ticks=skipped,logical_evaluations=evaluations)
    def logical_cells(self,positions):
        if not self.handle:raise ValueError('closed prefix world')
        positions=tuple(positions)
        if not 1<=len(positions)<=MAX_READ or any(type(x) is not int or not 0<=x<self.colonies*f.Q for x in positions):raise ValueError('bounded in-ring positions required')
        a=np.array(positions,dtype=np.uint64);out=np.empty((len(a),packed.WORDS),dtype=np.uint64)
        if self.lib.rp_read(self.handle,pointer(a),len(a),pointer(out)):raise RuntimeError('resident read failed')
        return q.cells_from_array(packed.unpack(out))
    def physical_cells(self,positions):
        positions=tuple(positions);size=self.colonies*f.Q
        if not positions or any(type(x) is not int or not 0<=x<size for x in positions):raise ValueError('in-ring physical positions required')
        needed=sorted({(x+d)%size for x in positions for d in f.OFFSETS});records={}
        for start in range(0,len(needed),MAX_READ):
            chunk=needed[start:start+MAX_READ];records.update(zip(chunk,self.logical_cells(chunk)))
        return tuple(r.lift(coherent_cell(lambda x:records[x%size],position)) for position in positions)
