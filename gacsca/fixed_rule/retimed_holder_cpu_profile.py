"""Physical CPU periods with captured mixed right Signals and exact flag fronts.

The profile is an execution representation of existing raw fields. Controller
context erasure uses the proved canonical factorization. Packets are prohibited
during forcing/clearing; unsupported left Signals reject atomically.
"""
import ctypes
from dataclasses import replace
from functools import lru_cache
import hashlib
from pathlib import Path
import subprocess
import numpy as np
from . import retimed_holder_cpu_boundary as boundary,retimed_holder_cpu_events as base
from . import retimed_holder_native as native,retimed_holder_rule as f,retimed_holder_core as c,retimed_holder_flag_profile as profile


def source():
    old=base.source();needle='extern "C" int run_events('
    assert old.count(needle)==1
    header=old[:old.index(needle)]
    values=dict(RAW_ADDRESS=f.COL['address'],RAW_AGE=f.COL['age'],RAW_F1=f.COL['f1'],RAW_F2=f.COL['f2'],RAW_SIGNAL=f.COL['signal'],PERIOD=f.U,WF_START=f.WF_START,WF_END=f.WF_END,CAPTURE=c.CAPTURE_AGE)
    for name,value in values.items():header+=f'\n#define {name} UINT64_C({value})\n'
    for name in ('wf1','wf2'):header+='static const int RAW_'+name.upper()+'[]={'+','.join(str(f.COL[f'w{k}_{name}']) for k in range(5))+'};\n'
    return header+Path(__file__).with_suffix('.cpp').read_text()


@lru_cache(None)
def library():
    text=source();digest=hashlib.sha256((text+f.self_description().digest()+'cpu-profile-O2-v1').encode()).hexdigest()[:20]
    directory=Path(__file__).resolve().parents[2]/'figs/fixed_rule/build'/('retimed_holder_cpu_profile_'+digest);directory.mkdir(parents=True,exist_ok=True)
    cpp=directory/'profile.cpp';target=directory/'profile.so'
    if cpp.exists():assert cpp.read_text()==text
    else:cpp.write_text(text)
    if not target.exists():
        with (directory/'build.log').open('w') as log:subprocess.run(['c++','-O2','-std=c++17','-Wall','-Wextra','-Werror','-shared','-fPIC',str(cpp),'-o',str(target)],stdout=log,stderr=subprocess.STDOUT,check=True)
    lib=ctypes.CDLL(str(target));ptr=ctypes.c_void_p;u=ctypes.c_uint64
    lib.profile_step.argtypes=[ptr,ptr,ptr,ptr,ptr,u,u,ptr,ptr,ptr,ptr,ptr];lib.profile_step.restype=ctypes.c_int
    return lib


class World(boundary.World):
    def __init__(self,*args,right=None,**kwargs):
        super().__init__(*args,**kwargs)
        right=tuple([0]*self.n if right is None else right)
        if len(right)!=self.n or any(value not in (0,1) for value in right):raise ValueError('one Boolean right Signal per colony required')
        self.right=np.array(right,dtype=np.uint64)
        if c.WF_START-1<=self.age<c.WF_END+f.Q and len(self.packets):raise ValueError('mail absent during forcing/clearing required')

    def step(self):
        if len(self.packets):raise ValueError('literal boundary step requires empty old mail')
        data=np.empty_like(self.data);heads=np.zeros_like(self.heads);where=np.zeros_like(self.where);right=np.empty_like(self.right)
        function=ctypes.cast(native.library().retimed_holder_local,ctypes.c_void_p)
        code=library().profile_step(function,base.rom().ctypes.data,self.data.ctypes.data,self.heads.ctypes.data,self.where.ctypes.data,self.n,self.age,self.right.ctypes.data,data.ctypes.data,heads.ctypes.data,where.ctypes.data,right.ctypes.data)
        if code:raise RuntimeError(f'physical profile domain rejected ({code}); state unchanged')
        self.data,self.heads,self.where,self.right=data,heads,where,right;self.age=(self.age+1)%f.U;self.time+=1
        return dict(physical_ticks=1,full_raw_evaluations=self.n*f.Q)

    def advance(self,ticks,**kwargs):
        forcing=self.age<c.WF_END+f.Q and self.age+ticks>c.WF_START-1
        if forcing and len(self.packets):raise ValueError('mail absent during forcing/clearing required')
        saved=(self.data,self.heads,self.where,self.packets,self.age,self.time)
        result=super().advance(ticks,**kwargs)
        if forcing and (result['packets_emitted'] or len(self.packets)):
            self.data,self.heads,self.where,self.packets,self.age,self.time=saved
            raise RuntimeError('packet emission during forcing/clearing; state unchanged')
        return result

    def cell(self,position):
        cell=super().cell(position);position%=self.n*f.Q;col,at=divmod(position,f.Q)
        first=0 if self.age<profile.START or not self.right[col] else profile.bits(self.age,at)[0]
        changes=dict(f1=first,signal=profile.signal(at)*int(self.right[col]))
        for delta in f.OFFSETS:
            primary=(position+delta)%(self.n*f.Q);col_,at_=divmod(primary,f.Q)
            changes[f'w{delta+2}_wf1']=int(bool(self.right[col_]) and c.WF_START<=self.age<c.WF_END and at_>=f.Q-5)
        return replace(cell,**changes)
