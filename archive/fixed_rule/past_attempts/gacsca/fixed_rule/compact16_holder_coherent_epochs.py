"""Full coherent work periods retaining arbitrary stationary residual Signals.

Physical controller/gather kernels remain unchanged. Exact packed flag dynamics
are coupled only during the guarded mail-free forcing interval. Complete image
restoration never decodes or repairs the encoded upper Data words.
"""
import ctypes
from functools import lru_cache
import hashlib
from pathlib import Path
import subprocess
import time
import numpy as np
from . import compact16_holder_late_mail_events as late,compact16_holder_late_events as base
from . import compact16_holder_resident_gather as gather,compact16_holder_resident_period as period
from . import compact16_holder_resident_independent as independent,compact16_holder_flags_gpu as flags
from . import compact16_holder_rule as f,compact16_holder_core as c,compact16_holder_program as p
from . import compact16_holder_projected as r,compact16_holder_records as q,compact16_holder_packed as packed
from . import compact16_holder_coherent_image as image


def source_text():
    source=late.source_text()
    old=' if(w.age<=RESET4||w.age>=PERIOD)return false;';assert source.count(old)==1
    source=source.replace(old,' if(w.age>=PERIOD)return false;')
    # Raw output Signal may briefly be incoherent at capture. The unchanged
    # local kernel resolves it; stationary jumps are rejected until it agrees.
    marker='  uint64_t pos=col*Q+get(row,P_ADDRESS);';assert source.count(marker)==1
    source=source.replace(marker,'  if(w.age>=PREFIX_LIMIT&&w.age<WF_END+Q)for(unsigned k=P_LP_TARGET;k<P_ADDRESS;++k)if(get(row,k))return false;\n'+marker)
    marker='if(bankrow(get(row,P_ADDRESS))<0&&get(row,P_DATA))w.status[3*col+2]=1;';assert source.count(marker)==1
    source=source.replace(marker,'if(w.age>=PREFIX_LIMIT&&w.age<WF_END+Q)for(unsigned k=P_LP_TARGET;k<P_ADDRESS;++k)if(get(row,k))w.status[3*col+2]=1;'+marker)
    # Frozen controllers cannot close gaps. This removes a conservative
    # performance restriction without changing any active transport bound.
    old=' for(size_t i=0;i<w.counts[col]&&limit;++i){\n  const uint64_t*x=';assert source.count(old)==1
    source=source.replace(old,' for(size_t i=0;moving&&i<w.counts[col]&&limit;++i){\n  const uint64_t*x=')
    return source


@lru_cache(maxsize=1)
def library():
    source=source_text();controller=Path(independent.__file__).with_suffix('.cu').read_text();transport=Path(gather.__file__).with_suffix('.cu').read_text();header=period.header()
    identity=hashlib.sha256(source.encode()+controller.encode()+transport.encode()+header.encode()+b'nvcc-O2-sm80-coherent-epochs-v1').hexdigest()[:20]
    directory=Path(__file__).resolve().parents[2]/'figs/fixed_rule/build'/('compact16_holder_coherent_epochs_'+identity);directory.mkdir(parents=True,exist_ok=True);target=directory/'epochs.so'
    if not target.exists():
        (directory/'compact16_holder_resident_period.cu').write_text(source);(directory/'compact16_holder_resident_period_generated.h').write_text(header)
        (directory/'compact16_holder_resident_independent.cu').write_text(controller);path=directory/'compact16_holder_resident_gather.cu';path.write_text(transport)
        with (directory/'build.log').open('w') as out:subprocess.run(['/usr/local/cuda/bin/nvcc','-O2','-std=c++17','-arch=sm_80','--shared','-Xcompiler','-fPIC',str(path),'-o',str(target)],check=True,stdout=out,stderr=subprocess.STDOUT)
    lib=ctypes.CDLL(str(target))
    for name in ('rp_create','rp_free','rp_info','rp_initial','rp_bank','rp_restore_age','rp_jump','rp_step','rp_read','rp_snapshot','ri_run'):
        original=getattr(late.library(),name);fn=getattr(lib,name);fn.argtypes=original.argtypes;fn.restype=original.restype
    lib.rg_run.argtypes=lib.ri_run.argtypes;lib.rg_run.restype=ctypes.c_int
    return lib


class Core(independent.World):
    def __init__(self,parents,*,raw=None,device_budget=32*1024**2):
        parents=tuple(parents)
        if not 0<len(parents)<=64:raise ValueError('bounded coherent colony count required')
        logical=None if raw is None else image.logical(raw)
        if logical is not None and len(logical)!=len(parents)*f.Q:raise ValueError('complete matching colony image required')
        super().__init__(parents,device_budget=device_budget)
        try:
            self.lib=library()
            if logical is not None:
                age=int(logical[0,q.COL['age']])
                if f.WF_START-1<=age<f.WF_END+f.Q:raise ValueError('restore outside forcing interval; live coupling handles its interior')
                active=[q.COL[name] for name in period.ACTIVE];g=p.layout()
                for col,part in enumerate(logical.reshape(self.colonies,f.Q,len(q.SCHEMA))):
                    indices=np.flatnonzero(np.any(part[:,active],axis=1))
                    if len(indices)>period.SLOTS:raise ValueError('complete sparse capacity exceeded')
                    records=np.zeros((1,period.SLOTS,packed.WORDS),dtype=np.uint64);records[0,:len(indices)]=packed.pack(part[indices]);counts=np.array([len(indices)],dtype=np.uint64)
                    if self.lib.rp_initial(self.handle,col,1,period.pointer(records),period.pointer(counts)):raise RuntimeError('complete controller/Signal/mail restoration failed')
                    bank=np.ascontiguousarray(np.concatenate((part[:g.memory_count,q.COL['data']],part[-5:,q.COL['data']])))
                    if self.lib.rp_bank(self.handle,col,period.pointer(bank)):raise RuntimeError('complete Data restoration failed')
                if self.lib.rp_restore_age(self.handle,age):raise ValueError('restored state outside current domain')
                self.age=self.epoch=self.time=age
                np.testing.assert_array_equal(self.raw(),raw)
        except BaseException:self.close();raise

    raw=base.World.raw

    def batch(self,ticks,*,event_budget=200000,extra_device_budget=32*1024**2):
        if not self.handle or type(ticks) is not int or not 0<ticks<1<<32:raise ValueError('live bounded duration required')
        if type(event_budget) is not int or not 0<event_budget<=1000000:raise ValueError('bounded event budget required')
        if type(extra_device_budget) is not int or not 0<extra_device_budget<=64*1024**2:raise ValueError('bounded staging required')
        before=self.age<f.CAPTURE_AGE-1
        if before and ticks>8*f.Q:raise ValueError('bounded gather interval required')
        metrics=np.zeros(4,dtype=np.uint64);fn=self.lib.rg_run if before else self.lib.ri_run
        code=fn(self.handle,ticks,event_budget,extra_device_budget,period.pointer(metrics))
        if code:raise independent.BatchRejected(code)
        self.age+=ticks;self.time+=ticks;self.evaluations+=int(metrics[3])
        return dict(physical_ticks=ticks,colony_literal_ticks=int(metrics[0]),max_colony_literal_ticks=int(metrics[1]),
                    colony_transport_or_quiet_ticks=self.colonies*ticks-int(metrics[0]),extra_device_bytes=int(metrics[2]),logical_evaluations=int(metrics[3]))

    def advance(self,ticks,*,chunk=c.T,**kwargs):
        if type(ticks) is not int or ticks<0 or ticks>f.U-self.age:raise ValueError('bounded within-period core advance required')
        return super().advance(ticks,chunk=min(chunk,8*f.Q),**kwargs)


class World:
    def __init__(self,parents=None,*,raw=None,device_budget=32*1024**2):
        if raw is not None:
            if parents is not None:raise ValueError('one complete initialization source required')
            parents=(r.Cell(),)*(len(raw)//f.Q)
        self.core=Core(parents,raw=raw,device_budget=device_budget);self._flags=None
    @property
    def age(self):return self.core.age
    @property
    def time(self):return self.core.time
    @property
    def device_bytes(self):return self.core.device_bytes+(self._flags.device_bytes if self._flags is not None else 0)
    def close(self):
        if self._flags is not None:self._flags.close();self._flags=None
        self.core.close()
    def __enter__(self):return self
    def __exit__(self,*args):self.close()
    def raw(self):
        out=self.core.raw()
        if self._flags is None:return out
        planes=self._flags.read();positions=np.arange(len(out));bits=(planes[positions//64]>>(positions%64).astype(np.uint64)[:,None])&np.uint64(1)
        out[:,[f.COL['f1'],f.COL['f2']]]=bits
        if f.WF_START<=self.age<f.WF_END:
            wf1=np.tile(np.arange(f.Q)>=f.Q-5,self.core.colonies)*np.repeat(np.array(self._flags.right,dtype=np.uint64),f.Q)
            wf2=np.tile(np.arange(f.Q)<=4,self.core.colonies)*np.repeat(np.array(self._flags.left,dtype=np.uint64),f.Q)*(1-bits[:,0])
            for d in f.OFFSETS:
                out[:,f.COL[f'w{d+2}_wf1']]=np.roll(wf1,-d);out[:,f.COL[f'w{d+2}_wf2']]=np.roll(wf2,-d)
        return out
    def advance(self,ticks,**kwargs):
        if type(ticks) is not int or not 0<=ticks<1<<63:raise ValueError('bounded physical duration required')
        stop=self.time+ticks;result={};flag_seconds=0.;flag_ticks=0;peak=self.device_bytes
        while self.time<stop:
            if self.age==f.WF_START-1 and self._flags is None:
                left=[];right=[]
                for col in range(self.core.colonies):
                    a,b=self.core.logical_cells((col*f.Q+3,col*f.Q+f.Q-3));left.append((a.signal>>2)&1);right.append((b.signal>>2)&1)
                self._flags=flags.World(tuple(right),tuple(left));peak=max(peak,self.device_bytes)
            boundary=f.WF_START-1 if self.age<f.WF_START-1 else f.WF_END+f.Q if self.age<f.WF_END+f.Q else f.U
            amount=min(stop-self.time,boundary-self.age);before=self.time
            try:row=self.core.advance(amount,**kwargs)
            finally:
                elapsed=self.time-before
                if self._flags is not None and elapsed:
                    t=time.perf_counter();self._flags.run(elapsed);flag_seconds+=time.perf_counter()-t;flag_ticks+=elapsed
            for name,value in row.items():result[name]=max(result.get(name,0),value) if name=='extra_device_bytes' else result.get(name,0)+value
            if self._flags is not None and self.age==f.WF_END+f.Q:
                if np.any(self._flags.read()):raise AssertionError('complete physical flag clearing bound failed')
                self._flags.close();self._flags=None
        return dict(result,flag_physical_ticks=flag_ticks,flag_seconds=flag_seconds,peak_explicit_device_bytes=peak)
