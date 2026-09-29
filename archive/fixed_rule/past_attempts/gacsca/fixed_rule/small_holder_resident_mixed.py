"""Resident execution with independently varying right Signals, left Signals zero.

The full-rule symbolic certificate is prove_small_holder_mixed_right.py. Only
an accelerator domain guard changes; physical transitions/ROM remain identical.
Frozen resident and independent backends remain untouched reference fixtures.
"""
import ctypes
from functools import lru_cache
import hashlib
from pathlib import Path
import subprocess
import numpy as np
from . import small_holder_resident_period as period,small_holder_resident_independent as independent
from . import small_holder_rule as f,small_holder_program as p
from .small_holder_stream_initial import InitialRing,canonical_raw,CHUNK


@lru_cache(maxsize=1)
def library():
    period_path=Path(period.__file__).with_suffix('.cu')
    independent_path=Path(independent.__file__).with_suffix('.cu')
    original=period_path.read_text()
    guard='if(suffix&&(left||right!=((sig(w,Q-3)>>2)&1)))return false;'
    assert original.count(guard)==1,'frozen guard changed: review mixed-Signal proof'
    widened=original.replace(guard,'if(suffix&&left)return false;')
    expression=period.header();source=independent_path.read_text()
    identity=hashlib.sha256(widened.encode()+source.encode()+expression.encode()+b'nvcc-O2-sm80-mixed-right-v1').hexdigest()[:20]
    directory=Path(__file__).resolve().parents[2]/'figs/fixed_rule/build'/('small_holder_resident_mixed_'+identity)
    directory.mkdir(parents=True,exist_ok=True);target=directory/'mixed.so'
    if not target.exists():
        (directory/'small_holder_resident_period.cu').write_text(widened)
        (directory/'small_holder_resident_period_generated.h').write_text(expression)
        (directory/'small_holder_resident_independent.cu').write_text(source)
        with (directory/'build.log').open('w') as log:
            subprocess.run(['/usr/local/cuda/bin/nvcc','-O2','-std=c++17','-arch=sm_80','--shared','-Xcompiler','-fPIC',str(directory/'small_holder_resident_independent.cu'),'-o',str(target)],stdout=log,stderr=subprocess.STDOUT,check=True)
    lib=ctypes.CDLL(str(target))
    for name in ('rp_create','rp_free','rp_info','rp_initial','rp_bank','rp_restore_age','rp_jump','rp_step','rp_read'):
        new=getattr(lib,name);old=getattr(period.library(),name);new.argtypes=old.argtypes;new.restype=old.restype
    lib.ri_run.argtypes=independent.library().ri_run.argtypes;lib.ri_run.restype=ctypes.c_int
    return lib


class World(independent.World):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        try:self.lib=library()
        except BaseException:self.close();raise
    @classmethod
    def from_raw_chunks(cls,colonies,chunks,*,device_budget=64*1024**2):
        if type(colonies) is not int or not 0<colonies<=1<<20:raise ValueError('bounded resident colony count required')
        if type(device_budget) is not int or not 0<device_budget<=8*1024**3:raise ValueError('bounded device budget required')
        world=cls.__new__(cls);world.lib=library();world.handle=ctypes.c_void_p();allocated=ctypes.c_uint64()
        code=world.lib.rp_create(colonies,0,device_budget,period.pointer(p.base_rom()),ctypes.byref(world.handle),ctypes.byref(allocated))
        if code:raise RuntimeError(f'streaming resident allocation rejected: {code}')
        world.colonies=colonies;world.age=world.epoch=world.time=world.evaluations=0;world.device_bytes=int(allocated.value)
        try:
            done=0
            for rows in chunks:
                if not isinstance(rows,np.ndarray) or rows.dtype!=np.uint64 or rows.ndim!=2 or rows.shape[1]!=f.FIELDS or not 1<=len(rows)<=CHUNK or done+len(rows)>colonies:raise ValueError('bounded complete raw parent chunks required')
                for name,width in f.SCHEMA:
                    if width<64 and np.any(rows[:,f.COL[name]]>=1<<width):raise ValueError('raw field width exceeded')
                static=canonical_raw(tuple(map(int,rows[:,f.COL['address']])))
                if not np.array_equal(rows[:,:len(f.STATIC)],static[:,:len(f.STATIC)]):raise ValueError('raw metadata differs from fixed hard-wiring')
                rows=np.ascontiguousarray(rows)
                if world.lib.rp_info(world.handle,done,len(rows),period.pointer(rows)):raise RuntimeError('streamed Info upload failed')
                done+=len(rows)
            if done!=colonies:raise ValueError('incomplete parent stream')
            return world
        except BaseException:world.close();raise
    @classmethod
    def from_hierarchy(cls,top,depth,*,device_budget=64*1024**2):
        initial=InitialRing(top)
        if type(depth) is not int or depth<1:raise ValueError('positive encoded depth required')
        count=initial.size(depth-1)
        return cls.from_raw_chunks(count,initial.chunks(depth-1),device_budget=device_budget)
    def batch(self,ticks,*,event_budget=200000,extra_device_budget=64*1024**2):
        if not self.handle:raise ValueError('closed resident world')
        if type(ticks) is not int or not 0<ticks<1<<32:raise ValueError('positive within-period duration required')
        if type(event_budget) is not int or not 0<event_budget<=1000000:raise ValueError('bounded literal event budget required')
        if type(extra_device_budget) is not int or not 0<extra_device_budget<=8*1024**3:raise ValueError('bounded extra device budget required')
        metrics=np.zeros(4,dtype=np.uint64)
        code=self.lib.ri_run(self.handle,ticks,event_budget,extra_device_budget,period.pointer(metrics))
        if code:raise independent.BatchRejected(code)
        self.age+=ticks;self.time+=ticks;self.evaluations+=int(metrics[3])
        return dict(physical_ticks=ticks,colony_literal_ticks=int(metrics[0]),max_colony_literal_ticks=int(metrics[1]),colony_transport_or_quiet_ticks=self.colonies*ticks-int(metrics[0]),extra_device_bytes=int(metrics[2]),logical_evaluations=int(metrics[3]))
