"""Full projected physical exceptions over the general-Signal GPU reference.

Reuse the frozen exception transition/compaction/rebase machinery. The only
changed reconstruction reads the reference's actual packed flags, including all
backup Wf fields. Neither faults nor controller state are projected away.
"""
import ctypes
from functools import lru_cache
import hashlib
from pathlib import Path
import subprocess
import numpy as np
from . import retimed_holder_resident_faults as old,retimed_holder_resident_general as general
from . import retimed_holder_resident_period as period,retimed_holder_flags_gpu as flags,retimed_holder_rule as f


FLAG_RECONSTRUCTION=r'''
/* ABI prefix of the frozen flags engine's host owner. Borrowed, never owned. */
struct FlagView{uint64_t *a,*b;uint8_t *right,*left;size_t colonies,words;uint64_t age;};
__device__ uint64_t reference_flag(World w,Faults e,uint64_t position,unsigned field){
 if(!e.flagbits)return physical_flag(w,position,field);
 uint64_t a=position%Q,col=position/Q,bit=position%64,word=position/64;
 uint64_t first=(e.flagbits[2*word]>>bit)&1;
 if(field==P_F1)return first;
 if(field==P_F2)return (e.flagbits[2*word+1]>>bit)&1;
 bool on=w.age>=WF_START&&w.age<WF_END;
 if(field==P_WF1)return on&&a>=Q-5&&((sig(w,col*Q+Q-3)>>2)&1);
 return on&&a<=4&&((sig(w,col*Q+3)>>2)&1)&&!first;
}
extern "C" int rf_bind(void*base,void*handle,void*flaghandle){
 World*w=(World*)base;Faults*e=(Faults*)handle;FlagView*v=(FlagView*)flaghandle;
 if(!w||!e)return -1;
 if(v&&(v->colonies!=w->colonies||v->words!=w->colonies*(Q/64)||v->age!=w->age))return -2;
 if(!v&&w->age>=WF_START&&w->age<WF_END+Q)return -3;
 e->flagbits=v?v->a:nullptr;return 0;
}
'''


FLAG_ABSORPTION=r'''
/* Same-time representation change, never flag repair. Every altered derived
   WF2 copy must already have its required value in the actual physical state. */
__global__ void absorb_flags(World w,Faults e){
 size_t i=(size_t)blockIdx.x*blockDim.x+threadIdx.x;if(i>=e.used)return;
 uint64_t pos=e.keys[i],a=pos%Q,col=pos/Q,word=pos/64,bit=UINT64_C(1)<<(pos%64);
 const uint64_t*actual=e.values+i*R_WORDS;uint64_t wanted1=raw_get(actual,@F1@),wanted2=raw_get(actual,@F2@);
 uint64_t old1=(e.flagbits[2*word]>>(pos%64))&1,old2=(e.flagbits[2*word+1]>>(pos%64))&1;bool coherent=true;
 if(old1!=wanted1){uint64_t wantedwf=w.age>=WF_START&&w.age<WF_END&&a<=4&&((sig(w,col*Q+3)>>2)&1)&&!wanted1;
  for(int d=-2;d<=2&&coherent;++d){uint64_t holder=wrap((int64_t)pos+d,w.colonies*Q);unsigned field=@WF2@+2*(2-d);const uint64_t*row=exception(e,holder);
   uint64_t value=row?raw_get(row,field):base_raw(w,e,holder,field);coherent=value==wantedwf;
  }
 }
 uint64_t changes=0;
 if(old1!=wanted1&&coherent){unsigned long long*target=(unsigned long long*)(e.flagbits+2*word);if(wanted1)atomicOr(target,(unsigned long long)bit);else atomicAnd(target,(unsigned long long)~bit);changes|=1;}
 if(old2!=wanted2){unsigned long long*target=(unsigned long long*)(e.flagbits+2*word+1);if(wanted2)atomicOr(target,(unsigned long long)bit);else atomicAnd(target,(unsigned long long)~bit);changes|=2;}
 e.flags[i]=changes;
}
extern "C" int rf_absorb_flags(void*base,void*handle,uint64_t*changes){World*w=(World*)base;Faults*e=(Faults*)handle;
 if(!w||!e||!e->used||!e->flagbits||w->age>WF_END)return -1;
 absorb_flags<<<(unsigned)((e->used+127)/128),128>>>(*w,*e);cudaError_t error=cudaGetLastError();
 if(error==cudaSuccess)error=cudaMemcpy(changes,e->flags,e->used*8,cudaMemcpyDeviceToHost);return (int)error;
}
'''


def source_text():
    source=Path(old.__file__).with_suffix('.cu').read_text()
    before='*readout,*work;size_t used;};'
    assert source.count(before)==1
    source=source.replace(before,'*readout,*work,*flagbits;size_t used;};')
    marker='__device__ uint64_t raw_get'
    assert source.count(marker)==1
    source=source.replace(marker,FLAG_RECONSTRUCTION+'\n'+marker)
    source=source.replace('base_raw(World w,uint64_t position','base_raw(World w,Faults e,uint64_t position')
    source=source.replace('base_raw(w,','base_raw(w,e,')
    before='return physical_flag(w,source,k);'
    assert source.count(before)==1
    extra=FLAG_ABSORPTION.replace('@F1@',str(f.COL['f1'])).replace('@F2@',str(f.COL['f2'])).replace('@WF2@',str(f.COL['w0_wf2']))
    return source.replace(before,'return reference_flag(w,e,source,k);')+extra


@lru_cache(maxsize=1)
def library():
    source=source_text();header=old.header();base=period.header();dependency=Path(period.__file__).with_suffix('.cu').read_bytes()
    # Include the borrowed flags-owner ABI in the build identity.
    flag_source=Path(flags.__file__).with_suffix('.cu').read_bytes()
    identity=hashlib.sha256(source.encode()+header.encode()+base.encode()+dependency+flag_source+b'nvcc-O2-sm80-general-faults-v1').hexdigest()[:20]
    directory=Path(__file__).resolve().parents[2]/'figs/fixed_rule/build'/('retimed_holder_general_faults_'+identity);directory.mkdir(parents=True,exist_ok=True);target=directory/'faults.so'
    if not target.exists():
        path=directory/'faults.cu';path.write_text(source)
        (directory/'retimed_holder_resident_faults_generated.h').write_text(header);(directory/'retimed_holder_resident_period_generated.h').write_text(base)
        (directory/'retimed_holder_resident_period.cu').write_bytes(dependency)
        with (directory/'build.log').open('w') as log:subprocess.run(['/usr/local/cuda/bin/nvcc','-O2','-std=c++17','-arch=sm_80','--shared','-Xcompiler','-fPIC',str(path),'-o',str(target)],check=True,stdout=log,stderr=subprocess.STDOUT)
    lib=ctypes.CDLL(str(target))
    for name in ('rf_create','rf_free','rf_upload','rf_prepare','rf_commit','rf_read','rf_absorb','rf_normalize'):
        original=getattr(old.library(),name);fn=getattr(lib,name);fn.argtypes=original.argtypes;fn.restype=original.restype
    lib.rf_bind.argtypes=[ctypes.c_void_p]*3;lib.rf_bind.restype=ctypes.c_int
    lib.rf_absorb_flags.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.POINTER(ctypes.c_uint64)];lib.rf_absorb_flags.restype=ctypes.c_int
    return lib


class _Reference:
    def __init__(self,world):self.world=world
    @property
    def handle(self):return self.world._core.handle
    def __getattr__(self,name):return getattr(self.world,name)


class World(old.World):
    def __init__(self,background):
        if not isinstance(background,general.World) or not background._core.handle:raise ValueError('live general-Signal reference required')
        self.reference=background;self.background=_Reference(background);self.sites=background.colonies*f.Q
        self.lib=library();self.handle=ctypes.c_void_p();size=ctypes.c_uint64()
        code=self.lib.rf_create(ctypes.byref(self.handle),ctypes.byref(size))
        if code:raise RuntimeError(f'general physical exception allocation failed: {code}')
        self.device_bytes=int(size.value);self._positions=np.array([],dtype=np.uint64);self._time=background.time;self.evaluations=0
        try:self._check()
        except BaseException:self.close();raise
    def _check(self):
        super()._check()
        flagstate=self.reference._flags
        code=self.lib.rf_bind(self.background.handle,self.handle,flagstate.handle if flagstate is not None else None)
        if code:raise ValueError(f'general flag/reference clock mismatch: {code}')

    def absorb_flags(self):
        """Preserve actual flags in the reference, provided every derived Wf agrees.

        Restricted to the forcing epoch so the later clearing deadline remains
        valid. Empty exceptions afterward is coherence, not physical recovery.
        """
        self._check()
        if not len(self._positions) or self.reference._flags is None or self.reference.age>f.WF_END:
            return dict(flag_fields=0,exceptions=len(self._positions))
        changes=np.empty(len(self._positions),dtype=np.uint64)
        code=self.lib.rf_absorb_flags(self.background.handle,self.handle,period.pointer(changes))
        if code:raise RuntimeError(f'flag rebase failed: {code}')
        self.reference._snapshot=None
        different=np.empty(len(self._positions),dtype=np.uint64)
        code=self.lib.rf_normalize(self.background.handle,self.handle,period.pointer(different))
        if code:raise RuntimeError(f'flag rebase normalization failed: {code}')
        selected=np.flatnonzero(different).astype(np.uint64)
        code=self.lib.rf_commit(self.handle,period.pointer(selected),len(selected))
        if code:raise RuntimeError(f'flag rebase commit failed: {code}')
        self._positions=self._positions[selected.astype(np.intp)]
        return dict(flag_fields=int(np.count_nonzero(changes&1)+np.count_nonzero(changes&2)),exceptions=len(selected))
    def advance(self,ticks,*,absorb_data=True,absorb_flags=True,literal_budget=4096):
        self._check()
        if type(ticks) is not int or ticks<0 or type(literal_budget) is not int or not 1<=literal_budget<=100000:raise ValueError('nonnegative duration and bounded literal budget required')
        stop=self.time+ticks;literal=fast=data=flag_fields=0
        while self.time<stop:
            if len(self._positions):
                if literal>=literal_budget:raise RuntimeError('literal defect budget exhausted; exact current state retained')
                self.step();literal+=1
                if absorb_data and len({(int(x)+d)%self.sites for x in self._positions for d in f.OFFSETS})<=old.CAPACITY:
                    data+=self.absorb_data()['data_cells']
                if absorb_flags:flag_fields+=self.absorb_flags()['flag_fields']
            else:
                amount=stop-self.time
                try:self.reference.advance(amount,extra_device_budget=32*1024**2)
                finally:self._time=self.reference.time
                fast+=amount
        return dict(time=self.time,literal_exception_ticks=literal,coherent_accelerated_ticks=fast,rebased_data_cells=data,rebased_flag_fields=flag_fields,exceptions=len(self._positions))
