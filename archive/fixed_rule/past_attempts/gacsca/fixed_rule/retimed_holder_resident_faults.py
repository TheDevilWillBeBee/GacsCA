"""Arbitrary projected physical exceptions over a nonperiodic resident reference.

The physical transition is G = project(F(lift(.))), with fixed program metadata.
All 105 mutable physical fields are retained; the 49 metadata words are derived.
Full local G runs on GPU while exceptions persist. Host code manages positions,
external fault injection and diagnostics, never evolving simulated transitions.
"""
import ctypes
from functools import lru_cache
import hashlib
from pathlib import Path
import subprocess
import numpy as np
from . import retimed_holder_resident_gather as resident,retimed_holder_resident_period as period
from . import retimed_holder_rule as f,retimed_holder_projected as r,retimed_holder_core as c,retimed_holder_quotient as q,retimed_holder_raw_packed as packed,retimed_holder_program as p
from .word_workspace_source import expression_source

CAPACITY=8192
MAX_READ=256
WORKERS=period.WORKERS


def header():
    maps=[]
    for name,_ in f.SCHEMA:
        if name.startswith('p'):
            prefix,field=name.split('_',1);maps.append((-1,int(prefix[1:])-3,c.STATIC.index(field)))
        elif name.startswith(('s','w')) and name!='signal':
            prefix,field=name.split('_',1);maps.append((q.COL[field],int(prefix[1:])-2,-1))
        else:maps.append((q.COL[name],0,-1))
    text=''
    for name,value in dict(R_FIELDS=f.FIELDS,R_WORDS=packed.WORDS,R_CAPACITY=CAPACITY,R_READ=MAX_READ,R_ADDRESS=f.COL['address']).items():text+=f'#define {name} {value}\n'
    for name,values in (('R_OFFSETS',packed.OFFSETS),('R_WIDTHS',[w for _,w in f.SCHEMA]),('R_DATA_FIELDS',[f.COL[f's{i}_data'] for i in range(5)]),*zip(('R_LOGICAL','R_OFFSET','R_STATIC'),zip(*maps))):
        text+='__device__ __constant__ int '+name+'[]={'+','.join(map(str,values))+'};\n'
    body,allocation=expression_source(f.self_description(),'fault_full_local',stride=WORKERS)
    text+=f'#define R_WORKSPACE ((16*R_FIELDS+{allocation.count})*WORKERS)\n'
    return text+body.replace('void fault_full_local','__device__ __noinline__ void fault_full_local',1)


@lru_cache(maxsize=1)
def library():
    source=Path(__file__).with_suffix('.cu');generated=header();base=period.header()
    identity=hashlib.sha256(source.read_bytes()+Path(period.__file__).with_suffix('.cu').read_bytes()+generated.encode()+base.encode()+b'nvcc-O2-sm80-projected-faults-v1').hexdigest()[:20]
    directory=source.resolve().parents[2]/'figs/fixed_rule/build'/('retimed_holder_resident_faults_'+identity);directory.mkdir(parents=True,exist_ok=True);target=directory/'faults.so'
    if not target.exists():
        (directory/'retimed_holder_resident_faults_generated.h').write_text(generated);(directory/'retimed_holder_resident_period_generated.h').write_text(base)
        with (directory/'build.log').open('w') as log:subprocess.run(['/usr/local/cuda/bin/nvcc','-O2','-std=c++17','-arch=sm_80','--shared','-Xcompiler','-fPIC','-I',str(directory),str(source),'-o',str(target)],stdout=log,stderr=subprocess.STDOUT,check=True)
    lib=ctypes.CDLL(str(target));ptr=ctypes.POINTER(ctypes.c_uint64);h=ctypes.c_void_p
    signatures={'rf_create':([ctypes.POINTER(h),ptr],ctypes.c_int),'rf_free':([h],None),'rf_upload':([h,ptr,ptr,ctypes.c_size_t],ctypes.c_int),'rf_prepare':([h,h,ptr,ctypes.c_size_t,ptr],ctypes.c_int),'rf_commit':([h,ptr,ctypes.c_size_t],ctypes.c_int),'rf_read':([h,h,ptr,ctypes.c_size_t,ptr],ctypes.c_int),'rf_absorb':([h,h,ptr,ctypes.c_size_t,ptr],ctypes.c_int),'rf_normalize':([h,h,ptr],ctypes.c_int)}
    for name,(args,result) in signatures.items():getattr(lib,name).argtypes=args;getattr(lib,name).restype=result
    return lib


class World:
    def __init__(self,background):
        if not isinstance(background,period.World) or not background.handle:raise ValueError('live supported resident reference required')
        self.background=background;self.sites=background.colonies*f.Q;self.lib=library();self.handle=ctypes.c_void_p();size=ctypes.c_uint64()
        code=self.lib.rf_create(ctypes.byref(self.handle),ctypes.byref(size))
        if code:raise RuntimeError(f'physical exception allocation failed: {code}')
        self.device_bytes=int(size.value);self._positions=np.array([],dtype=np.uint64);self._time=background.time;self.evaluations=0
    def close(self):
        if self.handle:self.lib.rf_free(self.handle);self.handle=None
    def __enter__(self):return self
    def __exit__(self,*args):self.close()
    @property
    def positions(self):return tuple(map(int,self._positions))
    @property
    def time(self):return self._time
    def _check(self):
        if not self.handle or not self.background.handle:raise ValueError('closed exception/reference world')
        if self.background.time!=self._time:raise ValueError('reference advanced outside exception owner')
    def read(self,positions):
        self._check();positions=tuple(positions)
        if not 1<=len(positions)<=MAX_READ or any(type(x) is not int or not 0<=x<self.sites for x in positions):raise ValueError('bounded in-ring physical positions required')
        source=np.array(positions,dtype=np.uint64);target=np.empty((len(source),packed.WORDS),dtype=np.uint64)
        code=self.lib.rf_read(self.background.handle,self.handle,period.pointer(source),len(source),period.pointer(target))
        if code:raise RuntimeError(f'exception read failed: {code}')
        return tuple(f.decode_cell(row.tolist()) for row in packed.unpack(target))
    def inject(self,replacements):
        self._check();replacements=dict(replacements)
        if any(type(x) is not int or not 0<=x<self.sites or not isinstance(cell,r.Cell) for x,cell in replacements.items()):raise ValueError('complete projected physical replacements required')
        positions=sorted(set(self.positions)|set(replacements))
        if len(positions)>CAPACITY:raise ValueError('exception capacity exceeded before injection')
        values={}
        for at in range(0,len(positions),MAX_READ):
            part=positions[at:at+MAX_READ];actual=self.read(part);base=self.background.physical_cells(part)
            for pos,old,reference in zip(part,actual,base):
                cell=r.lift(replacements[pos]) if pos in replacements else old
                if cell!=reference:values[pos]=cell
        keys=np.array(sorted(values),dtype=np.uint64)
        raw=np.array([f.encode_cell(values[int(x)]) for x in keys],dtype=np.uint64).reshape(-1,f.FIELDS);data=packed.pack(raw)
        code=self.lib.rf_upload(self.handle,period.pointer(keys),period.pointer(data),len(keys))
        if code:raise RuntimeError(f'fault injection failed: {code}')
        self._positions=keys
    def step(self):
        self._check()
        if not len(self._positions):
            self.background.step();self._time=self.background.time
            return dict(time=self.time,candidates=0,exceptions=0,full_local_evaluations=0)
        positions=np.array(sorted({(int(x)-j)%self.sites for x in self._positions for j in f.NEIGHBORHOOD}),dtype=np.uint64)
        if len(positions)>CAPACITY:raise ValueError('causal frontier capacity exceeded before state change')
        flags=np.empty(len(positions),dtype=np.uint64)
        code=self.lib.rf_prepare(self.background.handle,self.handle,period.pointer(positions),len(positions),period.pointer(flags))
        if code:raise RuntimeError(f'full physical preparation failed: {code}')
        selected=np.flatnonzero(flags).astype(np.uint64)
        # Preparation has not changed either represented state. The validated
        # resident reference advances once before publishing the actual rows.
        self.background.step()
        code=self.lib.rf_commit(self.handle,period.pointer(selected),len(selected))
        if code:raise RuntimeError(f'physical exception commit failed: {code}')
        self._positions=positions[selected.astype(np.intp)];self._time=self.background.time;self.evaluations+=2*len(positions)
        return dict(time=self.time,candidates=len(positions),exceptions=len(selected),full_local_evaluations=2*len(positions))
    def absorb_data(self):
        """State-preserving rebase, not correction: wrong coherent Data stays wrong.

        Only equal values in all five actual physical holders may enter the MEM
        bank. Full remaining exceptions are retained by exact state comparison.
        """
        self._check()
        if not len(self._positions):return dict(data_cells=0,exceptions=0)
        targets=np.array(sorted({(int(x)+d)%self.sites for x in self._positions for d in f.OFFSETS}),dtype=np.uint64)
        if len(targets)>CAPACITY:raise ValueError('rebase workspace capacity exceeded before state change')
        changed=np.empty(len(targets),dtype=np.uint64)
        code=self.lib.rf_absorb(self.background.handle,self.handle,period.pointer(targets),len(targets),period.pointer(changed))
        if code:raise RuntimeError(f'Data rebase failed: {code}')
        flags=np.empty(len(self._positions),dtype=np.uint64)
        code=self.lib.rf_normalize(self.background.handle,self.handle,period.pointer(flags))
        if code:raise RuntimeError(f'rebased normalization failed: {code}')
        selected=np.flatnonzero(flags).astype(np.uint64)
        code=self.lib.rf_commit(self.handle,period.pointer(selected),len(selected))
        if code:raise RuntimeError(f'rebased exception commit failed: {code}')
        self._positions=self._positions[selected.astype(np.intp)]
        return dict(data_cells=int(np.count_nonzero(changed)),exceptions=len(selected))
    def advance(self,ticks,*,absorb_data=True,literal_budget=4096):
        self._check()
        if type(ticks) is not int or ticks<0 or type(literal_budget) is not int or not 1<=literal_budget<=100000:raise ValueError('nonnegative duration and bounded literal budget required')
        stop=self.time+ticks;literal=fast=rebased=0
        while self.time<stop:
            if len(self._positions):
                if literal>=literal_budget:raise RuntimeError('literal defect budget exhausted; exact current state retained')
                self.step();literal+=1
                if absorb_data and len({(int(x)+d)%self.sites for x in self._positions for d in f.OFFSETS})<=CAPACITY:
                    rebased+=self.absorb_data()['data_cells']
            else:
                amount=stop-self.time;getattr(self.background,'advance',self.background.run)(amount);self._time=self.background.time;fast+=amount
        return dict(time=self.time,literal_exception_ticks=literal,coherent_accelerated_ticks=fast,rebased_data_cells=rebased,exceptions=len(self._positions))
    def decode(self):
        parents=[]
        for col in range(self.background.colonies):
            words=tuple(cell.s2_data for cell in self.read(tuple(col*f.Q+a for a in p.layout().info)))
            raw=f.decode_cell(words);value=r.project(raw)
            if r.lift(value)!=raw:raise ValueError('raw decoded metadata does not satisfy fixed projection')
            parents.append(value)
        return tuple(parents)
