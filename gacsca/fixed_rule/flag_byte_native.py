"""Compact native storage for the tested physical light-cone algorithm.

No rule or ROM changes. Node IDs below 2^18 are literal physical eight-site
flag/tag leaves. All other nodes and query results are hash-consed proofs.
"""
import ctypes
from functools import lru_cache
import hashlib
from pathlib import Path
import subprocess
import numpy as np


@lru_cache(maxsize=1)
def library():
    source=Path(__file__).with_suffix('.cpp');digest=hashlib.sha256(source.read_bytes()+b'cxx-O3-flag-byte-v1').hexdigest()[:16]
    build=source.resolve().parents[2]/'figs/fixed_rule/build'/('flag_byte_'+digest);build.mkdir(parents=True,exist_ok=True);target=build/'flags.so'
    if not target.exists():subprocess.run(['c++','-O3','-std=c++17','-Wall','-Wextra','-Werror','-shared','-fPIC',str(source),'-o',str(target)],check=True)
    lib=ctypes.CDLL(str(target));ptr=ctypes.POINTER(ctypes.c_uint64);handle=ctypes.c_void_p
    lib.fh_evolve.argtypes=[ptr,ctypes.c_size_t,ctypes.c_size_t,ctypes.c_uint64,ctypes.c_uint32];lib.fh_evolve.restype=handle
    lib.fh_free.argtypes=[handle];lib.fh_free.restype=None
    for name in ('fh_info','fh_nodes','fh_queries'):getattr(lib,name).argtypes=[handle,ptr];getattr(lib,name).restype=None
    lib.fh_at.argtypes=[handle,ctypes.c_uint32,ctypes.c_uint64];lib.fh_at.restype=ctypes.c_uint32
    lib.fh_local.argtypes=[ctypes.c_uint32]*3;lib.fh_local.restype=ctypes.c_uint32
    return lib


def pointer(a):return a.ctypes.data_as(ctypes.POINTER(ctypes.c_uint64))


class Evolution:
    def __init__(self,runs,colonies,age,ticks):
        if not isinstance(ticks,int) or not 0<=ticks<1<<32:raise ValueError('bounded physical work-period ticks required')
        a=np.asarray(runs,dtype=np.uint64)
        if a.ndim!=2 or a.shape[1]!=3 or not a.flags.c_contiguous:raise ValueError('complete contiguous word runs required')
        self.lib=library();self.handle=self.lib.fh_evolve(pointer(a),len(a),colonies,age,ticks)
        if not self.handle:raise RuntimeError('native light-cone construction failed or exceeded resource/domain bounds')
    def close(self):
        if self.handle:self.lib.fh_free(self.handle);self.handle=None
    def __enter__(self):return self
    def __exit__(self,*args):self.close()
    @property
    def info(self):
        if not self.handle:raise ValueError('closed physical evolution')
        a=np.empty(5,dtype=np.uint64);self.lib.fh_info(self.handle,pointer(a))
        return dict(zip(('nodes','queries','leaf_evaluations','initial','final'),map(int,a)))
    def at(self,position,*,initial=False):
        if not isinstance(position,int) or not 0<=position<1<<64:raise ValueError('nonnegative physical byte position required')
        value=int(self.lib.fh_at(self.handle,self.info['initial' if initial else 'final'],position))
        if value>=1<<18:raise ValueError('position outside physical block')
        return value
    def proof(self):
        info=self.info;nodes=np.empty((info['nodes'],3),dtype=np.uint64);queries=np.empty((info['queries'],3),dtype=np.uint64)
        self.lib.fh_nodes(self.handle,pointer(nodes));self.lib.fh_queries(self.handle,pointer(queries))
        # Subqueries have strictly smaller input spatial levels; this sorts the
        # proof topologically without relying on native hash-table bucket order.
        if len(queries):queries=queries[np.argsort(nodes[queries[:,0],0],kind='stable')]
        return nodes,queries
