"""Exact guarded gather packets alongside independent physical controllers."""
import ctypes
from functools import lru_cache
import hashlib
from pathlib import Path
import subprocess
import numpy as np
from . import compact16_holder_resident_mixed as mixed,compact16_holder_resident_period as period,compact16_holder_resident_independent as independent
from . import compact16_holder_rule as f,compact16_holder_core as c,compact16_holder_program as p


@lru_cache(maxsize=1)
def library():
    source=Path(__file__).with_suffix('.cu');body=period.header()
    dependencies=[Path(independent.__file__).with_suffix('.cu'),Path(period.__file__).with_suffix('.cu')]
    identity=hashlib.sha256(source.read_bytes()+b''.join(x.read_bytes() for x in dependencies)+body.encode()+b'nvcc-O2-sm80-gather-v1').hexdigest()[:20]
    directory=source.resolve().parents[2]/'figs/fixed_rule/build'/('compact16_holder_resident_gather_'+identity);directory.mkdir(parents=True,exist_ok=True);target=directory/'gather.so'
    if not target.exists():
        (directory/'compact16_holder_resident_period_generated.h').write_text(body)
        with (directory/'build.log').open('w') as log:subprocess.run(['/usr/local/cuda/bin/nvcc','-O2','-std=c++17','-arch=sm_80','--shared','-Xcompiler','-fPIC','-I',str(directory),str(source),'-o',str(target)],stdout=log,stderr=subprocess.STDOUT,check=True)
    lib=ctypes.CDLL(str(target));lib.rg_run.argtypes=independent.library().ri_run.argtypes;lib.rg_run.restype=ctypes.c_int;return lib


class World(mixed.World):
    def batch(self,ticks,*,event_budget=200000,extra_device_budget=64*1024**2):
        if self.age>=(c.CAPTURE_AGE-1):return super().batch(ticks,event_budget=event_budget,extra_device_budget=extra_device_budget)
        if not self.handle:raise ValueError('closed resident world')
        if type(ticks) is not int or not 0<ticks<=8*f.Q:raise ValueError('bounded physical gather interval required')
        if type(event_budget) is not int or not 0<event_budget<=1000000:raise ValueError('bounded event budget required')
        if type(extra_device_budget) is not int or not 0<extra_device_budget<=8*1024**3:raise ValueError('bounded extra device budget required')
        metrics=np.zeros(4,dtype=np.uint64);code=library().rg_run(self.handle,ticks,event_budget,extra_device_budget,period.pointer(metrics))
        if code:raise independent.BatchRejected(code)
        self.age+=ticks;self.time+=ticks;self.evaluations+=int(metrics[3])
        return dict(physical_ticks=ticks,colony_literal_ticks=int(metrics[0]),max_colony_literal_ticks=int(metrics[1]),colony_transport_or_quiet_ticks=self.colonies*ticks-int(metrics[0]),extra_device_bytes=int(metrics[2]),logical_evaluations=int(metrics[3]))
    def advance(self,ticks,*,chunk=c.T,event_budget=200000,extra_device_budget=64*1024**2):
        if type(ticks) is not int or not 0<=ticks<1<<63:raise ValueError('bounded duration required')
        result={};stop=self.time+ticks
        while self.time<stop:
            before=self.age<(c.CAPTURE_AGE-1);boundary=(c.CAPTURE_AGE-1) if before else c.U
            amount=min(stop-self.time,boundary-self.age)
            row=super().advance(amount,chunk=min(chunk,8*f.Q) if before else chunk,event_budget=event_budget,extra_device_budget=extra_device_budget)
            for name,value in row.items():result[name]=max(result.get(name,0),value) if name=='extra_device_bytes' else result.get(name,0)+value
        return result
