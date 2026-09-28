"""Resident physical periods in the certified coherent uniform-right family.

Before Wf this is the canonical zero-flag prefix. The suffix composes the same
controller with the independently certified flag profile, guarded by zero mail,
coherent left-zero Signals and uniform right Signal zero or one. Arbitrary
physical faults/Signal profiles are rejected, not replaced by this recurrence.
The same physical rule, alphabet, ROM and local procedure run at every depth.
"""
import ctypes
from functools import lru_cache
import hashlib
from pathlib import Path
import subprocess
import numpy as np
from . import compact16_holder_core as c,compact16_holder_rule as f,compact16_holder_program as p
from . import compact16_holder_records as q,compact16_holder_projected as r,compact16_holder_packed as packed
from .compact16_holder_prefix_description import build
from .compact16_holder_initial import coherent_cell
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
    assert not set(g.info).intersection({a+1 for a in g.info})
    text='#include <stdint.h>\n#include <stddef.h>\n#include <string.h>\n'
    constants=dict(Q=f.Q,MEM_ROWS=g.memory_count,BANK_ROWS=g.memory_count+5,ROM_ROWS=g.computation_cells,FIELDS=c.FIELDS,P_FIELDS=len(q.SCHEMA),PACKED_WORDS=packed.WORDS,SLOTS=SLOTS,CANDIDATES=CANDIDATES,WORKERS=WORKERS,READ_CAPACITY=MAX_READ,CHUNK=CHUNK,INFO_WORDS=f.FIELDS,RESET1=c.RESET_AGES[1],RESET2=c.RESET_AGES[2],VOTE0=c.VOTE_AGES[0],CAPTURE=c.CAPTURE_AGE,PREFIX_LIMIT=c.WF_START-1,END0=c.ACTIVE_ENDS[0],END1=c.ACTIVE_ENDS[1],END2=c.ACTIVE_ENDS[2],WF_START=c.WF_START,WF_END=c.WF_END,RESET4=c.RESET_AGES[4],END3=c.ACTIVE_ENDS[3],END4=c.ACTIVE_ENDS[4],PERIOD=c.U)
    for name,value in constants.items():text+=f'#define {name} UINT64_C({value})\n'
    text+='enum {'+','.join(n.upper() for n,_ in c.SCHEMA)+'};\n'
    text+='enum {'+','.join('P_'+n.upper() for n,_ in q.SCHEMA)+'};\n'
    for name,values in (('FIELD_OFFSETS',packed.OFFSETS),('FIELD_WIDTHS',[w for _,w in q.SCHEMA]),('DYNAMIC_FIELDS',[c.COL[n] for n,_ in q.SCHEMA]),('STATIC_FIELDS',[c.COL[n] for n in c.STATIC]),('ACTIVE_FIELDS',[q.COL[n] for n in ACTIVE]),('INFO_POSITIONS',g.info)):
        text+='__device__ __constant__ unsigned '+name+'[]={'+','.join(map(str,values))+'};\n'
    from .compact16_holder_cpu_gather import protected_targets
    text+='__device__ __constant__ unsigned char PROTECTED[Q]={'+','.join(str(int(a in protected_targets())) for a in range(f.Q))+'};\n'
    body,allocation=expression_source(build(),'resident_prefix_local',stride=WORKERS)
    text+=f'#define ACTIVE_FIELDS_COUNT {len(ACTIVE)}\n#define TEMP_WORDS {allocation.count}\n#define WORKSPACE_WORDS ((11*FIELDS+FIELDS+TEMP_WORDS)*WORKERS)\n'
    return text+body.replace('void resident_prefix_local','__device__ __noinline__ void resident_prefix_local',1)


@lru_cache(maxsize=1)
def library():
    source=Path(__file__).with_suffix('.cu');generated=header()
    digest=hashlib.sha256(source.read_bytes()+generated.encode()+b'nvcc-O2-sm80-resident-period-v1').hexdigest()[:20]
    directory=source.resolve().parents[2]/'figs/fixed_rule/build'/('compact16_holder_resident_period_'+digest);directory.mkdir(parents=True,exist_ok=True);target=directory/'prefix.so'
    if not target.exists():
        (directory/'compact16_holder_resident_period_generated.h').write_text(generated)
        with (directory/'build.log').open('w') as log:subprocess.run(['/usr/local/cuda/bin/nvcc','-O2','-std=c++17','-arch=sm_80','--shared','-Xcompiler','-fPIC','-I',str(directory),str(source),'-o',str(target)],stdout=log,stderr=subprocess.STDOUT,check=True)
    lib=ctypes.CDLL(str(target));ptr=ctypes.POINTER(ctypes.c_uint64);h=ctypes.c_void_p
    lib.rp_create.argtypes=[ctypes.c_size_t,ctypes.c_uint64,ctypes.c_uint64,ptr,ctypes.POINTER(h),ptr];lib.rp_create.restype=ctypes.c_int
    lib.rp_free.argtypes=[h];lib.rp_free.restype=None
    lib.rp_info.argtypes=[h,ctypes.c_size_t,ctypes.c_size_t,ptr];lib.rp_info.restype=ctypes.c_int
    lib.rp_initial.argtypes=[h,ctypes.c_size_t,ctypes.c_size_t,ptr,ptr];lib.rp_initial.restype=ctypes.c_int
    lib.rp_bank.argtypes=[h,ctypes.c_size_t,ptr];lib.rp_bank.restype=ctypes.c_int
    lib.rp_restore_age.argtypes=[h,ctypes.c_uint64];lib.rp_restore_age.restype=ctypes.c_int
    lib.rp_jump.argtypes=[h,ctypes.c_uint64,ptr];lib.rp_jump.restype=ctypes.c_int
    lib.rp_step.argtypes=[h,ptr];lib.rp_step.restype=ctypes.c_int
    lib.rp_read.argtypes=[h,ptr,ctypes.c_size_t,ptr];lib.rp_read.restype=ctypes.c_int
    lib.rp_snapshot.argtypes=[h,ptr,ptr,ptr];lib.rp_snapshot.restype=ctypes.c_int
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
        self.colonies=n;self.age=age;self.epoch=age;self.device_bytes=int(allocated.value);self.evaluations=0;self.time=0
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
    @classmethod
    def from_stored(cls,array,*,device_budget=64*1024**2):
        """Restore complete coherent core/tail state; no decoded transition."""
        from . import compact16_holder_flag_profile as profile
        g=p.layout();rows=g.computation_cells+5
        if not isinstance(array,np.ndarray) or array.dtype!=np.uint64 or array.ndim!=2 or array.shape[1]!=len(q.SCHEMA) or not len(array) or len(array)%rows:raise ValueError('complete coherent core/tail rows required')
        shaped=array.reshape(-1,rows,len(q.SCHEMA));age=int(shaped[0,0,q.COL['age']])
        if age>=f.U:raise ValueError('Age outside physical alphabet')
        addresses=np.array([*range(g.computation_cells),*range(f.Q-5,f.Q)],dtype=np.uint64)
        for part in shaped:
            if not np.array_equal(part[:,q.COL['address']],addresses) or not np.all(part[:,q.COL['age']]==age):raise ValueError('canonical geometry and common clock required')
            packed.pack(part) # checks every width; one-colony staging only
            if np.any(part[g.memory_count:g.computation_cells,q.COL['data']]):raise ValueError('non-MEM Data must be zero')
            right=(int(part[-3,q.COL['signal']])>>2)&1
            if age>=profile.START:
                wanted=np.array([profile.bits(age,int(a)) for a in addresses],dtype=np.uint64)*right
            else:wanted=np.zeros((rows,4),dtype=np.uint64)
            if not np.array_equal(part[:,[q.COL[x] for x in ('f1','f2','wf1','wf2')]],wanted):raise ValueError('flags outside certified physical profile')
        world=cls((r.Cell(),)*len(shaped),device_budget=device_budget)
        try:
            for col,part in enumerate(shaped):
                bank=np.ascontiguousarray(np.concatenate((part[:g.memory_count,q.COL['data']],part[-5:,q.COL['data']])))
                live=np.flatnonzero(np.any(part[:,[q.COL[x] for x in ACTIVE]],axis=1))
                if len(live)>SLOTS:raise ValueError('restored sparse capacity exceeded')
                selected=part[live].copy();selected[:,[q.COL[x] for x in ('f1','f2','wf1','wf2')]]=0
                records=np.zeros((1,SLOTS,packed.WORDS),dtype=np.uint64)
                if len(live):records[0,:len(live)]=packed.pack(selected)
                counts=np.array([len(live)],dtype=np.uint64)
                if world.lib.rp_initial(world.handle,col,1,pointer(records),pointer(counts)):raise RuntimeError('controller restore failed')
                if world.lib.rp_bank(world.handle,col,pointer(bank)):raise RuntimeError('Data-bank restore failed')
            if world.lib.rp_restore_age(world.handle,age):raise ValueError('unsupported restored suffix Signals or mail')
            world.age=world.epoch=age
            return world
        except BaseException:world.close();raise
    def snapshot(self):
        """Read every actual Data word and valid sparse record; omit no controller."""
        if not self.handle:raise ValueError('closed resident world')
        bank=np.empty((self.colonies,p.layout().memory_count+5),dtype=np.uint64)
        rows=np.zeros((self.colonies,SLOTS,packed.WORDS),dtype=np.uint64)
        counts=np.empty(self.colonies,dtype=np.uint64)
        code=self.lib.rp_snapshot(self.handle,pointer(bank),pointer(rows),pointer(counts))
        if code:raise RuntimeError(f'physical snapshot failed: {code}')
        return bank,rows,counts
    def stored(self):
        g=p.layout();addresses=tuple(range(g.computation_cells))+tuple(range(f.Q-5,f.Q))
        result=np.empty((self.colonies*(g.computation_cells+5),len(q.SCHEMA)),dtype=np.uint64)
        for col in range(self.colonies):
            for start in range(0,len(addresses),MAX_READ):
                selected=addresses[start:start+MAX_READ]
                result[col*len(addresses)+start:col*len(addresses)+start+len(selected)]=q.array_from_cells(self.logical_cells(tuple(col*f.Q+a for a in selected)))
        return result
    def decode(self):
        parents=[]
        for col in range(self.colonies):
            cells=self.logical_cells(tuple(col*f.Q+a for a in p.layout().info))
            raw=f.decode_cell(tuple(x.data for x in cells));value=r.project(raw)
            if r.lift(value)!=raw:raise ValueError('decoded raw metadata does not match fixed projection')
            parents.append(value)
        return tuple(parents)
    def close(self):
        if self.handle:self.lib.rp_free(self.handle);self.handle=None
    def __enter__(self):return self
    def __exit__(self,*args):self.close()
    def step(self):
        if not self.handle:raise ValueError('closed prefix world')
        metrics=np.zeros(3,dtype=np.uint64);code=self.lib.rp_step(self.handle,pointer(metrics))
        if code:raise RuntimeError(f'resident prefix step rejected: {code}')
        self.age=(self.age+1)%f.U;self.time+=1;self.evaluations+=int(metrics[0])
        return dict(age=self.age,logical_evaluations=int(metrics[0]),active_records=int(metrics[1]),max_active_per_colony=int(metrics[2]))
    def run(self,ticks,*,skip=True):
        if not self.handle:raise ValueError('closed prefix world')
        if type(ticks) is not int or not 0<=ticks<1<<63:raise ValueError('bounded nonnegative physical duration required')
        stop=self.time+ticks;literal=skipped=evaluations=0
        while self.time<stop:
            delta=ctypes.c_uint64()
            if skip:
                code=self.lib.rp_jump(self.handle,stop-self.time,ctypes.byref(delta))
                if code:raise RuntimeError(f'resident jump failed: {code}')
            if delta.value:self.age=(self.age+int(delta.value))%f.U;self.time+=int(delta.value);skipped+=int(delta.value)
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
