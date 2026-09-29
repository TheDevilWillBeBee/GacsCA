"""Independent GPU physical-event scheduling between common clock barriers.

No new physical rule or interpreter. Each literal event reuses the frozen
resident local expression. Batches require a communication-free product domain,
retain every evolving field and commit only after all colonies accept.
"""
import ctypes
from functools import lru_cache
import hashlib
from pathlib import Path
import subprocess

import numpy as np

from . import small_holder_resident_period as resident
from . import small_holder_core as c


@lru_cache(maxsize=1)
def library():
    source=Path(__file__).with_suffix('.cu')
    physical_source=Path(resident.__file__).with_suffix('.cu')
    generated=resident.header()
    identity=hashlib.sha256(source.read_bytes()+physical_source.read_bytes()+generated.encode()+b'nvcc-O2-sm80-independent-v1').hexdigest()[:20]
    directory=source.resolve().parents[2]/'figs/fixed_rule/build'/('small_holder_resident_independent_'+identity)
    directory.mkdir(parents=True,exist_ok=True)
    target=directory/'independent.so'
    if not target.exists():
        (directory/'small_holder_resident_period_generated.h').write_text(generated)
        with (directory/'build.log').open('w') as log:
            subprocess.run(['/usr/local/cuda/bin/nvcc','-O2','-std=c++17','-arch=sm_80','--shared','-Xcompiler','-fPIC','-I',str(directory),str(source),'-o',str(target)],stdout=log,stderr=subprocess.STDOUT,check=True)
    lib=ctypes.CDLL(str(target))
    lib.ri_run.argtypes=[ctypes.c_void_p,ctypes.c_uint64,ctypes.c_uint64,ctypes.c_uint64,ctypes.POINTER(ctypes.c_uint64)]
    lib.ri_run.restype=ctypes.c_int
    return lib


class BatchRejected(RuntimeError):
    def __init__(self,code):
        self.code=code
        super().__init__(f'independent physical batch rejected: {code}')


def distance_to_barrier(age):
    points=(*c.RESET_AGES,*c.ACTIVE_ENDS,*c.VOTE_AGES,c.CAPTURE_AGE-1,
            c.CAPTURE_AGE,c.WF_START-1,c.WF_END,c.U-1,c.U)
    return min(point-age for point in points if point>age)


class World(resident.World):
    def batch(self,ticks,*,event_budget=200000,extra_device_budget=64*1024**2):
        """Advance equal physical time using independent per-colony event clocks.

        Crossed barriers, mail, multiple heads, non-head controller residues,
        moving Signals and emitted packets reject atomically. Use inherited
        synchronous run/step for the intervals that need communication.
        """
        if not self.handle:raise ValueError('closed resident world')
        if type(ticks) is not int or not 0<ticks<1<<32:raise ValueError('positive within-period duration required')
        if type(event_budget) is not int or not 0<event_budget<=1000000:raise ValueError('bounded literal event budget required')
        if type(extra_device_budget) is not int or not 0<extra_device_budget<=8*1024**3:raise ValueError('bounded extra device budget required')
        metrics=np.zeros(4,dtype=np.uint64)
        code=library().ri_run(self.handle,ticks,event_budget,extra_device_budget,resident.pointer(metrics))
        if code:raise BatchRejected(code)
        self.age+=ticks;self.time+=ticks
        self.evaluations+=int(metrics[3])
        return dict(physical_ticks=ticks,colony_literal_ticks=int(metrics[0]),
                    max_colony_literal_ticks=int(metrics[1]),
                    colony_transport_or_quiet_ticks=self.colonies*ticks-int(metrics[0]),
                    extra_device_bytes=int(metrics[2]),logical_evaluations=int(metrics[3]))

    def advance(self,ticks,*,chunk=c.T,event_budget=200000,extra_device_budget=64*1024**2):
        """Full physical advance with atomic batch attempts and synchronous fallback.

        This changes only scheduling. Communication/barrier transitions still
        use the frozen synchronous local backend. Failed batch attempts never
        install staged Data or controllers.
        """
        if type(ticks) is not int or not 0<=ticks<1<<63:raise ValueError('bounded duration required')
        if type(chunk) is not int or not 0<chunk<1<<32:raise ValueError('bounded chunk required')
        result=dict(physical_ticks=0,independent_ticks=0,independent_batches=0,
                    rejected_batches=0,colony_literal_ticks=0,
                    colony_transport_or_quiet_ticks=0,synchronous_literal_ticks=0,
                    synchronous_transport_or_quiet_ticks=0,logical_evaluations=0,
                    extra_device_bytes=0)
        stop=self.time+ticks
        bulk=(*c.RESET_AGES,c.VOTE_AGES[0],c.CAPTURE_AGE-1,c.WF_START-1,c.U-1)
        while self.time<stop:
            amount=min(stop-self.time,chunk,distance_to_barrier(self.age))
            if self.age in bulk:amount=1
            elif c.active(self.age):
                try:
                    row=self.batch(amount,event_budget=event_budget,extra_device_budget=extra_device_budget)
                except BatchRejected as exc:
                    if exc.code!=-4:raise
                    result['rejected_batches']+=1
                else:
                    result['physical_ticks']+=amount;result['independent_ticks']+=amount
                    result['independent_batches']+=1
                    for name in ('colony_literal_ticks','colony_transport_or_quiet_ticks','logical_evaluations'):result[name]+=row[name]
                    result['extra_device_bytes']=max(result['extra_device_bytes'],row['extra_device_bytes'])
                    continue
            row=super().run(amount)
            result['physical_ticks']+=amount
            result['synchronous_literal_ticks']+=row['literal_ticks']
            result['synchronous_transport_or_quiet_ticks']+=row['transport_or_quiet_ticks']
            result['logical_evaluations']+=row['logical_evaluations']
        return result
