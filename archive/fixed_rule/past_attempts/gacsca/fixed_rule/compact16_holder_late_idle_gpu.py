"""Exact guarded late idle advance, stopping before the commit transition.

Requires canonical.World and complete GPU validation of zero controllers/mail/
flags/Wf plus coherent Data/Signals. Only Age can change before U-1 in this
domain. Does not implement or replace the commit; use the literal kernel for it.
"""
import ctypes
from functools import lru_cache
import hashlib
from pathlib import Path
import subprocess
from . import compact16_holder_canonical_gpu as base, compact16_holder_rule as f

LAST_EVENT=max(*f.RESET_AGES,*f.VOTE_AGES,f.CAPTURE_AGE,f.WF_END)


@lru_cache(maxsize=1)
def library():
    source=Path(__file__).with_suffix('.cu');generated=base.header();dependency=Path(base.__file__).with_suffix('.cu').read_bytes()
    identity=hashlib.sha256(source.read_bytes()+generated.encode()+dependency+b'nvcc-O2-sm80-late-idle-v1').hexdigest()[:20]
    directory=source.resolve().parents[2]/'figs/fixed_rule/build'/('compact16_holder_late_idle_'+identity);directory.mkdir(parents=True,exist_ok=True);target=directory/'idle.so'
    if not target.exists():
        (directory/'compact16_holder_canonical_generated.h').write_text(generated)
        (directory/'compact16_holder_canonical_gpu.cu').write_bytes(dependency)
        with (directory/'build.log').open('w') as out:subprocess.run(['/usr/local/cuda/bin/nvcc','-O2','-std=c++17','-arch=sm_80','--shared','-Xcompiler','-fPIC','-I',str(directory),str(source),'-o',str(target)],check=True,stdout=out,stderr=subprocess.STDOUT)
    lib=ctypes.CDLL(str(target));lib.idle_run.argtypes=[ctypes.c_void_p,ctypes.c_uint64,ctypes.c_uint64];lib.idle_run.restype=ctypes.c_int
    return lib


def advance(world,ticks):
    if not isinstance(world,base.World) or not world.handle:raise ValueError('live canonical world required')
    if type(ticks) is not int or ticks<0 or not LAST_EVENT<world.age<=world.age+ticks<f.U:raise ValueError('late interval must stop at or before old Age U-1')
    code=library().idle_run(world.handle,ticks,world.age)
    if code:raise ValueError(f'complete idle guard rejected or CUDA failed: {code}')
    world.time+=ticks;world.age+=ticks
    return dict(physical_ticks=ticks,complete_state_guard_sites=world.sites,extra_device_bytes=4,commit_executed=False)
