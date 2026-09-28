"""Literal streamed boundaries for zero-context coherent physical execution.

Every physical site is evaluated from the complete old state. A nonzero Signal,
flag/Wf or mail output rejects atomically; no such output is silently cleared.
"""
import ctypes
from functools import lru_cache
import hashlib
from pathlib import Path
import subprocess
import numpy as np
from . import compact16_holder_cpu_events as base,compact16_holder_cpu_gather as gather
from . import compact16_holder_native as native,compact16_holder_rule as f,compact16_holder_core as c


def source():
    old=base.source();needle='extern "C" int run_events('
    assert old.count(needle)==1
    header=old[:old.index(needle)]
    context=[i for i,(name,_) in enumerate(f.SCHEMA) if name in ('f1','f2','signal') or name.startswith('w')]
    header+=f'\n#define RAW_ADDRESS {f.COL["address"]}\n#define RAW_AGE {f.COL["age"]}\n#define PERIOD UINT64_C({f.U})\n#define CONTEXT_WORDS {len(context)}\n'
    header+='static const int RAW_CONTEXT[]={'+','.join(map(str,context))+'};\n'
    return header+Path(__file__).with_suffix('.cpp').read_text()


@lru_cache(None)
def library():
    text=source();digest=hashlib.sha256((text+f.self_description().digest()+'cpu-boundary-O2-v1').encode()).hexdigest()[:20]
    directory=Path(__file__).resolve().parents[2]/'figs/fixed_rule/build'/('compact16_holder_cpu_boundary_'+digest);directory.mkdir(parents=True,exist_ok=True)
    cpp=directory/'boundary.cpp';target=directory/'boundary.so'
    if cpp.exists():assert cpp.read_text()==text
    else:cpp.write_text(text)
    if not target.exists():
        with (directory/'build.log').open('w') as log:subprocess.run(['c++','-O2','-std=c++17','-Wall','-Wextra','-Werror','-shared','-fPIC',str(cpp),'-o',str(target)],stdout=log,stderr=subprocess.STDOUT,check=True)
    lib=ctypes.CDLL(str(target));ptr=ctypes.c_void_p;u=ctypes.c_uint64
    lib.boundary_step.argtypes=[ptr,ptr,ptr,ptr,ptr,u,u,ptr,ptr,ptr];lib.boundary_step.restype=ctypes.c_int
    return lib


class World(gather.World):
    def step(self):
        if len(self.packets):raise ValueError('literal boundary step requires empty old mail')
        data=np.empty_like(self.data);heads=np.zeros_like(self.heads);where=np.zeros_like(self.where)
        function=ctypes.cast(native.library().compact16_holder_local,ctypes.c_void_p)
        code=library().boundary_step(function,base.rom().ctypes.data,self.data.ctypes.data,self.heads.ctypes.data,self.where.ctypes.data,self.n,self.age,data.ctypes.data,heads.ctypes.data,where.ctypes.data)
        if code:raise RuntimeError(f'literal boundary domain rejected ({code}); state unchanged')
        self.data,self.heads,self.where=data,heads,where;self.age=(self.age+1)%f.U;self.time+=1
        return dict(physical_ticks=1,full_raw_evaluations=self.n*f.Q)

    def quiet_advance(self,ticks):
        if type(ticks) is not int or ticks<0 or self.age+ticks>f.U:raise ValueError('bounded quiet interval required')
        if np.any(self.heads) or len(self.packets):raise ValueError('quiet interval requires zero heads/controllers/mail')
        excluded=(*c.RESET_AGES,*c.VOTE_AGES,c.CAPTURE_AGE-1,f.U-1)
        if any(self.age<=at<self.age+ticks for at in excluded):raise ValueError('quiet interval crosses a physical boundary')
        self.age+=ticks;self.time+=ticks
        return dict(physical_ticks=ticks,full_raw_evaluations=0)
