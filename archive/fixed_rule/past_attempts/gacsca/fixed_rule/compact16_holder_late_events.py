"""Exact late-period events with arbitrary coherent stationary Signals.

Canonical geometry, zero flags/Wf, coherent procedures/Signals, no mail, bounded
sparse controllers, and zero non-MEM Data. Restores complete raw state without
re-encoding; stops after the current period's actual commit. No depth dispatch.
"""
import ctypes
from functools import lru_cache
import hashlib
from pathlib import Path
import subprocess
import numpy as np
from . import compact16_holder_resident_period as period,compact16_holder_resident_independent as independent
from . import compact16_holder_rule as f,compact16_holder_program as p,compact16_holder_projected as r
from . import compact16_holder_records as q,compact16_holder_packed as packed
from . import compact16_holder_literal_cone as cone,compact16_holder_terminal_reference as reference
from .compact16_holder_late_idle_gpu import LAST_EVENT

SIGNAL_GUARD=r'''
__device__ bool signal_shape(World w,size_t col,bool suffix){
 if(w.age<=RESET4||w.age>=PERIOD)return false;
 // Every possible nonzero vote neighborhood lies within two sites of a
 // stored Signal. Include absent records and cross-colony/periodic seams.
 for(size_t i=0;i<w.counts[col];++i){
  const uint64_t*row=w.rows+(col*SLOTS+i)*PACKED_WORDS;
  for(unsigned k=P_LP_TARGET;k<P_ADDRESS;++k)if(get(row,k))return false;
  uint64_t pos=col*Q+get(row,P_ADDRESS);
  for(int d=-2;d<=2;++d){uint64_t target=wrap((int64_t)pos+d,w.colonies*Q),wanted=0;
   for(int e=-2;e<=2;++e)wanted|=((sig(w,wrap((int64_t)target+e,w.colonies*Q))>>2)&1)<<(e+2);
   if(sig(w,target)!=wanted)return false;
  }
 }
 return true;
}
'''


def source_text():
    source=Path(period.__file__).with_suffix('.cu').read_text()
    first=source.index('__device__ bool signal_shape(');last=source.index('__device__ uint64_t physical_flag(',first)
    return source[:first]+SIGNAL_GUARD+source[last:]


@lru_cache(maxsize=1)
def library():
    source=source_text();controller=Path(independent.__file__).with_suffix('.cu').read_text();header=period.header()
    identity=hashlib.sha256(source.encode()+controller.encode()+header.encode()+b'nvcc-O2-sm80-late-events-v1').hexdigest()[:20]
    directory=Path(__file__).resolve().parents[2]/'figs/fixed_rule/build'/('compact16_holder_late_events_'+identity);directory.mkdir(parents=True,exist_ok=True);target=directory/'events.so'
    if not target.exists():
        (directory/'compact16_holder_resident_period.cu').write_text(source);(directory/'compact16_holder_resident_period_generated.h').write_text(header)
        path=directory/'compact16_holder_resident_independent.cu';path.write_text(controller)
        with (directory/'build.log').open('w') as out:subprocess.run(['/usr/local/cuda/bin/nvcc','-O2','-std=c++17','-arch=sm_80','--shared','-Xcompiler','-fPIC',str(path),'-o',str(target)],check=True,stdout=out,stderr=subprocess.STDOUT)
    lib=ctypes.CDLL(str(target))
    for name in ('rp_create','rp_free','rp_info','rp_initial','rp_bank','rp_restore_age','rp_jump','rp_step','rp_read','rp_snapshot','ri_run'):
        original=getattr(independent.library() if name=='ri_run' else period.library(),name);fn=getattr(lib,name);fn.argtypes=original.argtypes;fn.restype=original.restype
    return lib


def logical(raw):
    if not isinstance(raw,np.ndarray) or raw.dtype!=np.uint64 or raw.ndim!=2 or raw.shape[1]!=f.FIELDS or not 0<len(raw)<=64*f.Q or len(raw)%f.Q:raise ValueError('bounded complete physical colonies required')
    for k,(_,width) in enumerate(f.SCHEMA):
        if width<64 and np.any(raw[:,k]>=np.uint64(1<<width)):raise ValueError('raw word outside fixed alphabet')
    age=int(raw[0,f.COL['age']])
    if not LAST_EVENT<age<f.U or np.any(raw[:,f.COL['age']]!=age):raise ValueError('uniform late legal clock required')
    if not np.array_equal(raw[:,f.COL['address']],np.arange(len(raw))%f.Q):raise ValueError('canonical Address required')
    if not np.array_equal(raw,cone.normalize(raw.copy())):raise ValueError('fixed projected metadata required')
    for name in ('f1','f2',*(f'w{k}_{n}' for k in range(5) for n in ('wf1','wf2'))):
        if np.any(raw[:,f.COL[name]]):raise ValueError('zero physical flags and Wf required')
    for d in f.OFFSETS:
        for name,_ in f.PROCEDURE:
            if not np.array_equal(raw[:,f.COL[f's{d+2}_{name}']],np.roll(raw[:,f.COL[f's2_{name}']],-d)):raise ValueError('complete coherent procedures required')
        if not np.array_equal((raw[:,f.COL['signal']]>>np.uint64(d+2))&np.uint64(1),np.roll((raw[:,f.COL['signal']]>>np.uint64(2))&np.uint64(1),-d)):raise ValueError('coherent stationary Signals required')
    out=np.zeros((len(raw),len(q.SCHEMA)),dtype=np.uint64)
    for name,_ in q.SCHEMA:
        source='s2_'+name if name in dict(f.PROCEDURE) else 'w2_'+name if name in ('wf1','wf2') else name
        out[:,q.COL[name]]=raw[:,f.COL[source]]
    if np.any(out[:,[q.COL[n] for n,_ in q.SCHEMA if n.startswith(('lp_','rp_'))]]):raise ValueError('mail-free late state required')
    address=out[:,q.COL['address']];g=p.layout()
    if np.any(out[(address>=g.memory_count)&(address<f.Q-5),q.COL['data']]):raise ValueError('non-MEM Data must be zero')
    return out


class World(independent.World):
    def __init__(self,raw,*,device_budget=32*1024**2):
        rows=logical(raw);n=len(rows)//f.Q;age=int(rows[0,q.COL['age']]);active=[q.COL[x] for x in period.ACTIVE]
        parts=rows.reshape(n,f.Q,len(q.SCHEMA));selected=[np.flatnonzero(np.any(part[:,active],axis=1)) for part in parts]
        if any(len(x)>period.SLOTS for x in selected):raise ValueError('sparse storage capacity exceeded')
        super().__init__((r.Cell(),)*n,device_budget=device_budget)
        try:
            self.lib=library();g=p.layout()
            for col,(part,indices) in enumerate(zip(parts,selected)):
                records=np.zeros((1,period.SLOTS,packed.WORDS),dtype=np.uint64);records[0,:len(indices)]=packed.pack(part[indices])
                counts=np.array([len(indices)],dtype=np.uint64)
                if self.lib.rp_initial(self.handle,col,1,period.pointer(records),period.pointer(counts)):raise RuntimeError('raw controller/Signal restoration failed')
                bank=np.ascontiguousarray(np.concatenate((part[:g.memory_count,q.COL['data']],part[-5:,q.COL['data']])))
                if self.lib.rp_bank(self.handle,col,period.pointer(bank)):raise RuntimeError('complete Data restoration failed')
            if self.lib.rp_restore_age(self.handle,age):raise ValueError('GPU late Signal/domain validation failed')
            self.age=self.epoch=self.time=age
            np.testing.assert_array_equal(self.raw(),raw)
        except BaseException:self.close();raise

    def batch(self,ticks,*,event_budget=200000,extra_device_budget=32*1024**2):
        if not self.handle or type(ticks) is not int or not 0<ticks<1<<32:raise ValueError('live bounded event duration required')
        if type(event_budget) is not int or not 0<event_budget<=1000000:raise ValueError('bounded event budget required')
        if type(extra_device_budget) is not int or not 0<extra_device_budget<=64*1024**2:raise ValueError('bounded staging required')
        if not LAST_EVENT<self.age<f.U or ticks>f.U-self.age:raise ValueError('late period only')
        metrics=np.zeros(4,dtype=np.uint64);code=self.lib.ri_run(self.handle,ticks,event_budget,extra_device_budget,period.pointer(metrics))
        if code:raise independent.BatchRejected(code)
        self.age+=ticks;self.time+=ticks;self.evaluations+=int(metrics[3])
        return dict(physical_ticks=ticks,colony_literal_ticks=int(metrics[0]),max_colony_literal_ticks=int(metrics[1]),
                    colony_transport_or_quiet_ticks=self.colonies*ticks-int(metrics[0]),extra_device_bytes=int(metrics[2]),logical_evaluations=int(metrics[3]))

    def advance(self,ticks,**kwargs):
        if type(ticks) is not int or ticks<0 or (ticks and (not LAST_EVENT<self.age<f.U or ticks>f.U-self.age)):raise ValueError('stop after current period commit')
        return super().advance(ticks,**kwargs)

    def step(self):
        if not LAST_EVENT<self.age<f.U:raise ValueError('late period only')
        return super().step()

    def run(self,ticks,*,skip=True):
        if type(ticks) is not int or ticks<0 or (ticks and (not LAST_EVENT<self.age<f.U or ticks>f.U-self.age)):raise ValueError('stop after current period commit')
        return super().run(ticks,skip=skip)

    def raw(self):
        bank,packed_rows,counts=self.snapshot();g=p.layout();n=self.colonies
        logical=np.zeros((n*f.Q,len(q.SCHEMA)),dtype=np.uint64);logical[:,q.COL['address']]=np.arange(n*f.Q)%f.Q;logical[:,q.COL['age']]=self.age
        for col in range(n):
            base=col*f.Q;logical[base:base+g.memory_count,q.COL['data']]=bank[col,:g.memory_count];logical[base+f.Q-5:base+f.Q,q.COL['data']]=bank[col,-5:]
            part=packed.unpack(packed_rows[col,:int(counts[col])]);positions=base+part[:,q.COL['address']].astype(np.int64)
            for name in period.ACTIVE:logical[positions,q.COL[name]]=part[:,q.COL[name]]
        out=np.zeros((n*f.Q,f.FIELDS),dtype=np.uint64)
        for name,_ in f.GEOMETRY:out[:,f.COL[name]]=logical[:,q.COL[name]]
        for d in f.OFFSETS:
            for name,_ in f.PROCEDURE:out[:,f.COL[f's{d+2}_{name}']]=np.roll(logical[:,q.COL[name]],-d)
        return cone.normalize(out)
