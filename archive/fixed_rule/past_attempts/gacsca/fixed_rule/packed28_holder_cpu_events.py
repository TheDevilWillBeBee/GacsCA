"""Bounded CPU physical events on the canonical coherent, zero-context domain.

Every event calls the complete native physical descriptor. Travel is skipped
only within a regular clock interval and a confined one-head core. Mail-emitting
trajectories are rejected atomically. This execution adapter is not the physical
alphabet, self-description, or a host interpreter of the represented rule.
"""
import ctypes
from functools import lru_cache
import hashlib
from pathlib import Path
import subprocess
import numpy as np
from . import packed28_holder_rule as f,packed28_holder_core as c,packed28_holder_program as p
from . import packed28_holder_projected as r,packed28_holder_native as native,packed28_holder_quotient as q

CONTROL=('head',*c.CONTROL)


def regular_intervals():
    excluded=set(c.RESET_AGES)|set(c.VOTE_AGES)|{c.CAPTURE_AGE-1,f.U-1};result=[]
    for lo,hi in zip(c.RESET_AGES,c.ACTIVE_ENDS):
        at=lo
        for value in sorted(x for x in excluded if lo<=x<hi):
            if at<value:result.append((at,value-1))
            at=value+1
        if at<hi:result.append((at,hi-1))
    return tuple(result)


def distance_source():
    # The hardware head carries a virtual PC. Its immutable physical ROM
    # location is determined by the fixed packed program in the initial data.
    # This table only accelerates travel between literal physical local steps.
    locations=p.layout().packed.physical_of_pc
    table='static const uint16_t PC_PHYSICAL[]={'+','.join(map(str,locations))+'};\n'
    return table+'''uint64_t independent_distance(World w,uint64_t a,const uint64_t*h){
 (void)w;
 const unsigned H=P_HEAD;
 if(h[P_DIRECTION-H])return a;
 uint64_t target=ROM_ROWS-1,x=UINT64_MAX,phase=h[P_PHASE-H];
 if(phase==0&&h[P_PC-H]<PC_COUNT)x=MEM_ROWS+PC_PHYSICAL[h[P_PC-H]];
 else if((phase==1||phase==4||phase==5)&&h[P_RA-H]<MEM_ROWS)x=h[P_RA-H];
 else if(phase==2&&h[P_RB-H]<MEM_ROWS)x=h[P_RB-H];
 else if(phase==3&&h[P_RD-H]<MEM_ROWS)x=h[P_RD-H];
 else if(phase==6&&h[P_VALUE-H]&&h[P_RD-H]<ROM_ROWS)x=h[P_RD-H];
 if(x>=a&&x<target)target=x;
 return target-a;
}\n'''


def source():
    assert f.NEIGHBORHOOD==tuple(range(-7,8)) and len(p.base_rom())+9<f.Q
    assert np.any(p.base_rom()[:,0]==c.PACK3)
    fields=[]
    for name,_ in f.SCHEMA:
        if name.startswith('p'):
            slot,suffix=name.split('_',1);fields.append((0,int(slot[1:])-3,c.STATIC.index(suffix)))
        elif name.startswith('s') and '_' in name:
            slot,suffix=name.split('_',1);offset=int(slot[1:])-2
            fields.append((1,offset,0) if suffix=='data' else (2,offset,CONTROL.index(suffix)) if suffix in CONTROL else (5,offset,0))
        else:fields.append((3 if name=='address' else 4 if name=='age' else 5,0,0))
    header='#include <cstdint>\n#include <cstddef>\n'
    for name,value in dict(Q=f.Q,RAW_FIELDS=f.FIELDS,ROM_ROWS=len(p.base_rom()),MEM_ROWS=p.layout().memory_count,PC_COUNT=len(p.layout().instructions),HWORDS=len(CONTROL),RAW_HEAD=f.COL['s2_head'],RAW_DATA=f.COL['s2_data']).items():header+=f'#define {name} UINT64_C({value})\n'
    for name,index in q.COL.items():header+=f'#define P_{name.upper()} {index}\n'
    arrays={'RAW_KIND':[row[0] for row in fields],'RAW_OFFSET':[row[1] for row in fields],'RAW_ARG':[row[2] for row in fields],
            'RAW_CONTROL':[f.COL['s2_'+name] for name in CONTROL],
            'RAW_MAIL':[i for i,(name,_) in enumerate(f.SCHEMA) if name.startswith('s') and '_' in name and name.split('_',1)[1].startswith(('lp_','rp_'))]}
    header+=f'#define MAIL_WORDS {len(arrays["RAW_MAIL"])}\n'
    for name,values in arrays.items():header+='static const int '+name+'[]={'+','.join(map(str,values))+'};\n'
    body=Path(__file__).with_suffix('.cpp').read_text()
    assert body.count('// DISTANCE_FUNCTION')==1
    return header+body.replace('// DISTANCE_FUNCTION',distance_source().replace('__device__ ',''))


@lru_cache(None)
def library():
    text=source();digest=hashlib.sha256((text+f.self_description().digest()+'cpu-events-O2-v1').encode()).hexdigest()[:20]
    directory=Path(__file__).resolve().parents[2]/'figs/fixed_rule/build'/('packed28_holder_cpu_events_'+digest)
    directory.mkdir(parents=True,exist_ok=True);cpp=directory/'events.cpp';target=directory/'events.so'
    if cpp.exists():assert cpp.read_text()==text
    else:cpp.write_text(text)
    if not target.exists():
        with (directory/'build.log').open('w') as log:
            subprocess.run(['c++','-O2','-std=c++17','-Wall','-Wextra','-Werror','-shared','-fPIC',str(cpp),'-o',str(target)],stdout=log,stderr=subprocess.STDOUT,check=True)
    lib=ctypes.CDLL(str(target));ptr=ctypes.c_void_p
    lib.run_events.argtypes=[ptr,ptr,ptr,ptr,ptr,ctypes.c_uint64,ctypes.c_uint64,ctypes.c_uint64,ctypes.c_uint64,ptr]
    lib.run_events.restype=ctypes.c_int
    return lib


@lru_cache(None)
def rom():
    array=np.array([tuple(r.record(a)[name] for name in c.STATIC) for a in range(f.Q)],dtype=np.uint64)
    array.flags.writeable=False;return array


class World:
    def __init__(self,data,heads,where,*,age):
        self.data=np.array(data,dtype=np.uint64,copy=True,order='C')
        self.heads=np.array(heads,dtype=np.uint64,copy=True,order='C');self.where=np.array(where,dtype=np.uint64,copy=True)
        if self.data.ndim!=2 or self.data.shape[1]!=f.Q or not 1<=len(self.data)<=64:raise ValueError('one to 64 complete Q-cell Data banks required')
        self.n=len(self.data)
        if self.heads.shape!=(self.n,len(CONTROL)) or self.where.shape!=(self.n,):raise ValueError('complete controller and location required')
        if type(age) is not int or not 0<=age<f.U:raise ValueError('legal physical Age required')
        for row,at in zip(self.heads,self.where):
            if not 0<=at<len(p.base_rom()):raise ValueError('head outside fixed core')
            if any(int(value)>=1<<dict(c.SCHEMA)[name] for name,value in zip(CONTROL,row)):raise ValueError('controller outside fixed alphabet')
            if not row[0] and np.any(row[1:]):raise ValueError('inactive controller must be zero')
        if np.any(self.data[:,p.layout().memory_count:f.Q-5]):raise ValueError('non-MEM Data must be zero')
        self.age=age;self.time=0

    def advance(self,ticks,*,event_budget=1000000):
        if type(ticks) is not int or ticks<1 or not any(lo<=self.age<=self.age+ticks-1<=hi for lo,hi in regular_intervals()):raise ValueError('single regular physical clock interval required')
        if type(event_budget) is not int or not 1<=event_budget<=1000000:raise ValueError('bounded event budget required')
        data=self.data.copy();heads=self.heads.copy();where=self.where.copy();metrics=np.zeros(3,dtype=np.uint64)
        function=ctypes.cast(native.library().packed28_holder_local,ctypes.c_void_p)
        code=library().run_events(function,rom().ctypes.data,data.ctypes.data,heads.ctypes.data,where.ctypes.data,self.n,self.age,ticks,event_budget,metrics.ctypes.data)
        if code:raise RuntimeError(f'physical event domain/budget rejected ({code}); state unchanged')
        self.data,self.heads,self.where=data,heads,where;self.age+=ticks;self.time+=ticks
        return dict(physical_ticks=ticks,colony_event_ticks=int(metrics[0]),colony_travel_ticks=int(metrics[1]),
                    colony_quiet_ticks=self.n*ticks-int(metrics[0])-int(metrics[1]),full_raw_evaluations=int(metrics[2]))

    def cell(self,position):
        position%=self.n*f.Q;values=dict(address=position%f.Q,age=self.age)
        for offset in f.OFFSETS:
            primary=(position+offset)%(self.n*f.Q);col,at=divmod(primary,f.Q)
            values[f's{offset+2}_data']=int(self.data[col,at])
            if at==self.where[col]:
                for name,value in zip(CONTROL,self.heads[col]):values[f's{offset+2}_{name}']=int(value)
        return r.lift(r.Cell(**values))
