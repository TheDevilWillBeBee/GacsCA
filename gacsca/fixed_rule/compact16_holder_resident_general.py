"""Resident computation plus exact arbitrary-Signal canonical flag dynamics.

One fixed physical rule. The flag projection and mail-free controller operators
factor on canonical geometry; both evolve on GPU. This public wrapper deliberately
is not a period.World: the older physical-exception backend cannot reconstruct its
separate flag storage and must reject it rather than silently discard Flag2.
"""
import ctypes
from dataclasses import replace
from functools import lru_cache
import hashlib
from pathlib import Path
import subprocess
import numpy as np
from . import compact16_holder_resident_period as period,compact16_holder_resident_independent as independent,compact16_holder_resident_gather as gather
from . import compact16_holder_flags_gpu as flags,compact16_holder_rule as f


@lru_cache(maxsize=1)
def library():
    source=Path(period.__file__).with_suffix('.cu').read_text()
    guard='if(suffix&&(left||right!=((sig(w,Q-3)>>2)&1)))return false;'
    assert source.count(guard)==1,'review changed reference domain guard'
    source=source.replace(guard,'/* General flags are evolved by the exact sidecar; retain shape/mail guards. */')
    controller=Path(independent.__file__).with_suffix('.cu').read_text();header=period.header()
    identity=hashlib.sha256(source.encode()+controller.encode()+header.encode()+b'nvcc-O2-general-flags-v1').hexdigest()[:20]
    directory=Path(__file__).resolve().parents[2]/'figs/fixed_rule/build'/('compact16_holder_resident_general_'+identity);directory.mkdir(parents=True,exist_ok=True);target=directory/'general.so'
    if not target.exists():
        (directory/'compact16_holder_resident_period.cu').write_text(source);(directory/'compact16_holder_resident_period_generated.h').write_text(header)
        path=directory/'compact16_holder_resident_independent.cu';path.write_text(controller)
        with (directory/'build.log').open('w') as log:subprocess.run(['/usr/local/cuda/bin/nvcc','-O2','-std=c++17','-arch=sm_80','--shared','-Xcompiler','-fPIC',str(path),'-o',str(target)],stdout=log,stderr=subprocess.STDOUT,check=True)
    lib=ctypes.CDLL(str(target))
    for name in ('rp_create','rp_free','rp_info','rp_initial','rp_bank','rp_restore_age','rp_jump','rp_step','rp_read','rp_snapshot','ri_run'):
        original=getattr(independent.library() if name=='ri_run' else period.library(),name);new=getattr(lib,name);new.argtypes=original.argtypes;new.restype=original.restype
    return lib


class World:
    def __init__(self,parents,**kwargs):
        parents=tuple(parents)
        if not 0<len(parents)<=flags.MAX_COLONIES:raise ValueError('bounded general resident colony count required')
        self._flags=None;self._snapshot=None;self._core=gather.World(parents,**kwargs)
        try:self._core.lib=library()
        except BaseException:self._core.close();raise
        self.flag_ticks=0;self.flag_seconds=0.
    @property
    def colonies(self):return self._core.colonies
    @property
    def age(self):return self._core.age
    @property
    def time(self):return self._core.time
    @property
    def device_bytes(self):return self._core.device_bytes+(self._flags.device_bytes if self._flags is not None else 0)
    def close(self):
        if self._flags is not None:self._flags.close();self._flags=None
        self._core.close();self._snapshot=None
    def __enter__(self):return self
    def __exit__(self,*args):self.close()
    def _start_flags(self):
        assert self.age==f.WF_START-1 and self._flags is None
        right=[];left=[]
        for col in range(self.colonies):
            cells=self._core.logical_cells((col*f.Q+3,col*f.Q+f.Q-3))
            left.append((cells[0].signal>>2)&1);right.append((cells[1].signal>>2)&1)
        self._flags=flags.World(tuple(right),tuple(left));self._snapshot=None
    def advance(self,ticks,**kwargs):
        import time
        if not self._core.handle or type(ticks) is not int or not 0<=ticks<1<<63:raise ValueError('live world and bounded duration required')
        stop=self.time+ticks;metrics={};flag_ticks=0;flag_seconds=0.
        while self.time<stop:
            if self.age==f.WF_START-1:self._start_flags()
            boundary=f.WF_START-1 if self.age<f.WF_START-1 else f.WF_END+f.Q if self.age<f.WF_END+f.Q else f.U
            amount=min(stop-self.time,boundary-self.age);before=self.time
            try:row=self._core.advance(amount,**kwargs)
            finally:
                elapsed=self.time-before
                if self._flags is not None and elapsed:
                    tick=time.perf_counter();self._flags.run(elapsed);flag_seconds+=time.perf_counter()-tick;flag_ticks+=elapsed;self._snapshot=None
            for name,value in row.items():metrics[name]=max(metrics.get(name,0),value) if name=='extra_device_bytes' else metrics.get(name,0)+value
            if self._flags is not None and self.age==f.WF_END+f.Q:
                if np.any(self._flags.read()):raise AssertionError('canonical candidate-B clearing bound failed')
                self._flags.close();self._flags=None;self._snapshot=None
        self.flag_ticks+=flag_ticks;self.flag_seconds+=flag_seconds
        return dict(metrics,flag_literal_ticks=flag_ticks,flag_seconds=flag_seconds)
    def run(self,ticks,**kwargs):return self.advance(ticks,**kwargs)
    def step(self):return self.advance(1)
    def logical_cells(self,positions):
        positions=tuple(positions);cells=self._core.logical_cells(positions)
        if self._flags is None:return cells
        if self._snapshot is None:self._snapshot=self._flags.read()
        active=f.WF_START<=self.age<f.WF_END;out=[]
        for pos,cell in zip(positions,cells):
            word,bit=divmod(pos,64);col,a=divmod(pos,f.Q)
            first=(int(self._snapshot[word,0])>>bit)&1;second=(int(self._snapshot[word,1])>>bit)&1
            out.append(replace(cell,f1=first,f2=second,wf1=int(active and a>=f.Q-5 and self._flags.right[col]),wf2=int(active and a<=4 and self._flags.left[col] and not first)))
        return tuple(out)
    def physical_cells(self,positions):return period.World.physical_cells(self,positions)
    def decode(self):return period.World.decode(self)
    def stored(self):return period.World.stored(self)
