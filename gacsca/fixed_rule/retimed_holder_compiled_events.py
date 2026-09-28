"""Compiled event-loop acceleration of the existing complete global executor.

Clock-wide transitions still use the complete native G on every physical cell.
The C++ loop reconstructs the same raw neighborhoods and calls the identical
native F function for every literal event. No simulated rule is evaluated here.
"""
import ctypes
from functools import lru_cache
import hashlib
from pathlib import Path
import subprocess

import numpy as np

from . import retimed_holder_global_events as global_events
from . import retimed_holder_rule as f, retimed_holder_core as c
from . import retimed_holder_program as p, retimed_holder_native as native


@lru_cache(maxsize=1)
def library():
    code = Path(__file__).with_suffix('.cc').read_text()
    names, col = global_events.NAMES, global_events.COL
    constants = dict(Q=f.Q, FIELDS=f.FIELDS, PROCS=len(names),
                     ROM_ROWS=len(p.base_rom()), MEM_ROWS=p.layout().memory_count,
                     RAW_AGE=f.COL['age'], RAW_ADDRESS=f.COL['address'], RAW_SIGNAL=f.COL['signal'])
    constants.update({name.upper():col[name] for name in ('head','phase','pc','ra','rb','rd','value','direction')})
    constants.update({name:getattr(c,name) for name in ('FETCH','WAIT','READ_A','READ_B','WRITE','TRANSMIT','READ_LOAD','READ_META')})
    header = ''.join(f'constexpr uint64_t {name} = {value};\n' for name,value in constants.items())
    for name,values in [('CONTROL',global_events.CONTROL),('MAIL',global_events.MAIL),
                        ('RAW_FLAGS',[f.COL[x] for x in ('f1','f2',*(f'w{k}_{n}' for k in range(5) for n in ('wf1','wf2')))])]:
        header += f'constexpr unsigned {name}[] = {{'+','.join(map(str,values))+'};\n'
    rows = [[f.COL[f's{k}_{name}'] for name in names] for k in range(5)]
    header += 'constexpr unsigned RAW_PROC[5][PROCS] = {'+','.join('{'+','.join(map(str,row))+'}' for row in rows)+'};\n'
    physical = Path(native.library()._name).resolve()
    identity = hashlib.sha256(code.encode()+header.encode()+physical.read_bytes()+b'compiled-global-events-cxx17-O2-v1').hexdigest()[:20]
    directory = Path(__file__).resolve().parents[2]/'figs/fixed_rule/build'/('retimed_holder_compiled_events_'+identity)
    directory.mkdir(parents=True,exist_ok=True)
    target = directory/'events.so'
    if not target.exists():
        source = directory/'events.cc';source.write_text(code)
        (directory/'events_config.h').write_text(header)
        with (directory/'build.log').open('w') as log:
            subprocess.run(['c++','-O2','-std=c++17','-Wall','-Wextra','-Werror','-shared','-fPIC',str(source),str(physical),'-o',str(target)],stdout=log,stderr=subprocess.STDOUT,check=True)
    lib = ctypes.CDLL(str(target));ptr = ctypes.POINTER(ctypes.c_uint64)
    lib.ce_run.argtypes = [ptr,ptr,ptr,ptr,*([ctypes.c_uint64]*5),ptr,ctypes.c_uint64,ptr,ctypes.c_uint64,ptr]
    lib.ce_run.restype = ctypes.c_int
    return lib


class World(global_events.World):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.compiled = library()

    def advance(self,ticks,*,event_budget=1000000):
        if type(ticks) is not int or ticks<0 or type(event_budget) is not int or event_budget<1:
            raise ValueError('bounded nonnegative duration and event budget required')
        stop = self.time+ticks
        events = 0
        while self.time<stop:
            if events>=event_budget:
                raise RuntimeError('event budget exhausted; exact physical state retained')
            if self.age in (*f.RESET_AGES,*f.VOTE_AGES,f.CAPTURE_AGE-1,f.WF_START-1,f.U-1):
                self.bulk();events += 1;continue
            if f.WF_START<=self.age<=f.WF_END+f.Q:
                raise global_events.DomainError('forcing/flag interval requires another exact executor')
            amount = min(stop-self.time,min(t-self.age for t in global_events.single.BARRIERS if t>self.age))
            if not c.active(self.age):
                self.age += amount;self.time += amount;self.quiet_ticks += amount;continue
            heads = np.empty(32*(self.size//f.Q),dtype=np.uint64)
            heads[:len(self.heads)] = self.heads
            trace = np.empty((16384,3),dtype=np.uint64)
            stats = np.zeros(6,dtype=np.uint64)
            code = self.compiled.ce_run(native.pointer(self.words),native.pointer(self.signals),
                        native.pointer(self.template),native.pointer(self.rom),self.size,self.age,self.time,
                        amount,event_budget-events,native.pointer(heads),len(self.heads),native.pointer(trace),len(trace),native.pointer(stats))
            elapsed,literal,transport,evaluations,count,head_count = map(int,stats)
            self.time += elapsed;self.age += elapsed;events += literal
            self.literal_ticks += literal;self.transport_ticks += transport
            self.local_evaluations += evaluations
            self.heads = tuple(map(int,heads[:head_count]))
            self.trace.extend(map(tuple,trace[:count].tolist()))
            if code:
                raise global_events.DomainError(f'compiled event domain/budget stop {code}; last valid state retained')
            if not elapsed:
                raise RuntimeError('compiled executor made no progress')
        return dict(time=self.time,age=self.age,head_positions=list(self.heads),literal_ticks=self.literal_ticks,
                    transport_ticks=self.transport_ticks,quiet_ticks=self.quiet_ticks,bulk_ticks=self.bulk_ticks,
                    full_local_evaluations=self.local_evaluations)
