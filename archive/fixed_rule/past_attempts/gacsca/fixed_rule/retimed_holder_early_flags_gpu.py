"""Early-clock wrapper for the unchanged canonical GPU flag transition.

Only the constructor clock guard differs from the frozen suffix wrapper. The
device flag_step body and graph execution are byte-identical. No shared build
artifact is overwritten. This represents flags, not complete procedure state.
"""
import ctypes
from functools import lru_cache
import hashlib
from pathlib import Path
import subprocess
import numpy as np
from . import retimed_holder_flags_gpu as old,retimed_holder_rule as f


def source_text():
    source=Path(old.__file__).with_suffix('.cu').read_text()
    guard='age<WF_START-1||age>=PERIOD'
    assert source.count(guard)==1
    return source.replace(guard,'age>=UINT64_C(32768)')


@lru_cache(None)
def library():
    source=source_text()
    header=''.join(f'#define {k} UINT64_C({v})\n' for k,v in dict(WORDS_PER_COLONY=old.WORDS,WF_START=f.WF_START,WF_END=f.WF_END,PERIOD=f.U,GRAPH_TICKS=old.GRAPH_TICKS).items())
    identity=hashlib.sha256(source.encode()+header.encode()+b'early-flags-guard-only-v1').hexdigest()[:20]
    directory=Path(__file__).resolve().parents[2]/'figs/fixed_rule/build'/('retimed_holder_early_flags_'+identity)
    directory.mkdir(parents=True,exist_ok=True);target=directory/'flags.so'
    if not target.exists():
        path=directory/'flags.cu';path.write_text(source)
        (directory/'retimed_holder_flags_generated.h').write_text(header)
        with (directory/'build.log').open('w') as log:
            subprocess.run(['/usr/local/cuda/bin/nvcc','-O2','-std=c++17','-arch=sm_80','--shared','-Xcompiler','-fPIC','-I',str(directory),str(path),'-o',str(target)],check=True,stdout=log,stderr=subprocess.STDOUT)
    lib=ctypes.CDLL(str(target))
    for name in ('sf_create','sf_free','sf_read','sf_run'):
        original=getattr(old.library(),name);fn=getattr(lib,name)
        fn.argtypes=original.argtypes;fn.restype=original.restype
    return lib


class World(old.World):
    def __init__(self,right,left,*,age,initial):
        self.right,self.left=tuple(right),tuple(left);self.colonies=len(self.right)
        if not 0<self.colonies<=old.MAX_COLONIES or len(self.left)!=self.colonies or any(type(x) is not int or x not in (0,1) for x in (*self.right,*self.left)):
            raise ValueError('typed bounded Signal bits required')
        if type(age) is not int or not 0<=age<32768:raise ValueError('certified early clock required')
        if not isinstance(initial,np.ndarray) or initial.dtype!=np.uint64 or initial.shape!=(self.colonies*old.WORDS,2):raise ValueError('complete typed flag planes required')
        self.lib=library();self.handle=ctypes.c_void_p();byte=ctypes.POINTER(ctypes.c_uint8)
        rr=np.array(self.right,dtype=np.uint8);ll=np.array(self.left,dtype=np.uint8);data=np.ascontiguousarray(initial)
        code=self.lib.sf_create(self.colonies,age,rr.ctypes.data_as(byte),ll.ctypes.data_as(byte),data.ctypes.data_as(ctypes.POINTER(ctypes.c_uint64)),ctypes.byref(self.handle))
        if code:raise RuntimeError(f'early flag allocation failed: {code}')
        self.age=age;self.time=0;self.device_bytes=32*self.colonies*old.WORDS+2*self.colonies

    def run(self,ticks):
        if type(ticks) is not int or not 0<=ticks<=32768-self.age:raise ValueError('early flag certificate interval exceeded')
        return super().run(ticks)
