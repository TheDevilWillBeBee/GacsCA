"""Guarded actual packet transport alongside physical CPU controller events.

Only protected MEM targets can receive deferred packets, and every controller
access there rejects the staged call. Packet payloads come from full F outputs.
This is a restricted physical executor, not an upper-rule or opcode interpreter.
"""
import ctypes
from functools import lru_cache
import hashlib
from pathlib import Path
import subprocess
import numpy as np
from dataclasses import replace
from . import gather29_holder_cpu_events as base,gather29_holder_native as native
from . import gather29_holder_rule as f,gather29_holder_program as p


def protected_target(address):
    if 1<=address<=5 or f.Q-5<=address<f.Q:return True
    if not 8<=address<8+4*len(p.layout().gathered_inputs):return False
    index,slot=divmod(address-8,4)
    return slot!=1 and p.layout().gathered_inputs[index]//f.FIELDS!=7


def source():
    old=base.source();needle='extern "C" int run_events('
    assert old.count(needle)==1
    header=old[:old.index(needle)]+f'\n#define INFO_WORDS {f.FIELDS}\n'
    neighbors=tuple(wire//f.FIELDS for wire in p.layout().gathered_inputs)
    header+=f'#define GATHERED_COUNT {len(neighbors)}\n'
    header+='static const int GATHERED_NEIGHBOR[]={' + ','.join(map(str,neighbors)) + '};\n'
    header+='static const int RAW_PACKET[2][4]={'+','.join('{'+','.join(str(f.COL['s2_'+track+'_'+name]) for name in ('target','data','remaining','valid'))+'}' for track in ('lp','rp'))+'};\n'
    return header+Path(__file__).with_suffix('.cpp').read_text()


@lru_cache(None)
def library():
    text=source();digest=hashlib.sha256((text+f.self_description().digest()+'cpu-gather-O2-v1').encode()).hexdigest()[:20]
    directory=Path(__file__).resolve().parents[2]/'figs/fixed_rule/build'/('gather29_holder_cpu_gather_'+digest);directory.mkdir(parents=True,exist_ok=True)
    cpp=directory/'gather.cpp';target=directory/'gather.so'
    if cpp.exists():assert cpp.read_text()==text
    else:cpp.write_text(text)
    if not target.exists():
        with (directory/'build.log').open('w') as log:subprocess.run(['c++','-O2','-std=c++17','-Wall','-Wextra','-Werror','-shared','-fPIC',str(cpp),'-o',str(target)],stdout=log,stderr=subprocess.STDOUT,check=True)
    lib=ctypes.CDLL(str(target));ptr=ctypes.c_void_p;u=ctypes.c_uint64
    lib.run_gather.argtypes=[ptr,ptr,ptr,ptr,ptr,u,u,u,u,ptr,u,ptr,u,ptr,ptr];lib.run_gather.restype=ctypes.c_int
    return lib


class World(base.World):
    def __init__(self,*args,packets=(),**kwargs):
        super().__init__(*args,**kwargs)
        rows=tuple(tuple(row) for row in packets)
        if len(rows)>4096*self.n:raise ValueError('bounded packet count required')
        seen=set()
        for row in rows:
            if len(row)!=5 or any(type(x) is not int or x<0 for x in row):raise ValueError('complete unsigned packet record required')
            position,track,target,data,remaining=row
            if position>=self.n*f.Q or track>1 or not protected_target(target) or data>=1<<64 or remaining>7:raise ValueError('packet outside guarded domain')
            if (position,track) in seen:raise ValueError('duplicate live packet track')
            seen.add((position,track))
        self.packets=np.array(rows,dtype=np.uint64).reshape((-1,5))

    def advance(self,ticks,*,event_budget=1000000,packet_capacity=None):
        if type(ticks) is not int or ticks<1 or not any(lo<=self.age<=self.age+ticks-1<=hi for lo,hi in base.regular_intervals()):raise ValueError('single regular physical clock interval required')
        if type(event_budget) is not int or not 1<=event_budget<=1000000:raise ValueError('bounded event budget required')
        capacity=4096*self.n if packet_capacity is None else packet_capacity
        if type(capacity) is not int or not 1<=capacity<=4096*self.n:raise ValueError('bounded packet capacity required')
        data=self.data.copy();heads=self.heads.copy();where=self.where.copy();metrics=np.zeros(6,dtype=np.uint64)
        live=np.empty((capacity,5),dtype=np.uint64);count=np.zeros(1,dtype=np.uint64)
        function=ctypes.cast(native.library().gather29_holder_local,ctypes.c_void_p)
        code=library().run_gather(function,base.rom().ctypes.data,data.ctypes.data,heads.ctypes.data,where.ctypes.data,self.n,self.age,ticks,event_budget,self.packets.ctypes.data,len(self.packets),live.ctypes.data,capacity,count.ctypes.data,metrics.ctypes.data)
        if code:raise RuntimeError(f'physical packet domain/budget rejected ({code}); state unchanged')
        self.data,self.heads,self.where=data,heads,where;self.packets=live[:int(count[0])].copy();self.age+=ticks;self.time+=ticks
        return dict(physical_ticks=ticks,colony_event_ticks=int(metrics[0]),colony_travel_ticks=int(metrics[1]),
                    colony_quiet_ticks=self.n*ticks-int(metrics[0])-int(metrics[1]),full_raw_evaluations=int(metrics[2]),
                    packets_emitted=int(metrics[3]),packets_delivered=int(metrics[4]),packets_dropped=int(metrics[5]),packets_live=len(self.packets))

    def cell(self,position):
        cell=super().cell(position);changes={};size=self.n*f.Q
        lookup={(int(row[0]),int(row[1])):row for row in self.packets}
        for offset in f.OFFSETS:
            for track,prefix in ((0,'lp'),(1,'rp')):
                row=lookup.get(((position+offset)%size,track))
                if row is not None:
                    for name,value in zip(('target','data','remaining','valid'),(*row[2:],1)):
                        changes[f's{offset+2}_{prefix}_{name}']=int(value)
        return replace(cell,**changes)
