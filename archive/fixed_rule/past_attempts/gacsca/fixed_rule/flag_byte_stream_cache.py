"""Bounded-history storage for the fixed physical flag recurrence.

Only the host representation changes. No hierarchy argument, controller
interpreter, physical parameter change, or assumed flag-wave shape is used.
"""
import ctypes
from functools import lru_cache
import hashlib
from pathlib import Path
import subprocess
import numpy as np
from .flag_byte_native import pointer
from .delivery_rule import U


@lru_cache(maxsize=1)
def library():
    source=Path(__file__).with_suffix('.cpp');base=source.with_name('flag_byte_native.cpp').read_bytes()
    # Preserve the previously audited physical leaf function byte for byte.
    assert hashlib.sha256(base).hexdigest()=='bb5db0b581f5d058cd5ba25aa642b7f1573e9c276e078336b5186e0aff5d8cca'
    header=base.decode().replace('void add(uint64_t key,uint32_t value){','void add(uint64_t key,uint32_t value){if(used>=stream_limit)throw std::runtime_error("host table budget");').replace('nodes.push_back({a,b,k+1});','if(nodes.size()>=stream_limit)throw std::runtime_error("host node budget");nodes.push_back({a,b,k+1});')
    audit=source.with_name("flag_stream_cached_audit.h").read_bytes()
    digest=hashlib.sha256(source.read_bytes()+header.encode()+audit).hexdigest();build=source.resolve().parents[2]/'figs/fixed_rule/build'/('flag_stream_'+digest[:16]);build.mkdir(parents=True,exist_ok=True);target=build/'flags.so'
    if not target.exists():
        (build/'flag_stream_engine.h').write_text(header)
        subprocess.run(['c++','-O3','-std=c++17','-Wall','-Wextra','-Werror','-shared','-fPIC','-I',str(build),str(source),'-o',str(target)],check=True)
    lib=ctypes.CDLL(str(target));ptr=ctypes.POINTER(ctypes.c_uint64);handle=ctypes.c_void_p
    lib.fs_create.argtypes=[ptr,ctypes.c_size_t,ctypes.c_size_t,ctypes.c_uint64];lib.fs_create.restype=handle
    lib.fs_tables.argtypes=[handle,ctypes.POINTER(ctypes.c_uint8),ctypes.POINTER(ctypes.c_uint8)];lib.fs_tables.restype=None
    lib.fs_free.argtypes=[handle];lib.fs_free.restype=None
    lib.fs_advance.argtypes=[handle,ctypes.c_uint32,ctypes.c_size_t];lib.fs_advance.restype=ctypes.c_int
    lib.fs_info.argtypes=[handle,ptr];lib.fs_info.restype=None
    lib.fs_error.argtypes=[handle];lib.fs_error.restype=ctypes.c_char_p
    lib.fs_at.argtypes=[handle,ctypes.c_uint64];lib.fs_at.restype=ctypes.c_uint32
    lib.fs_nodes.argtypes=[handle,ptr];lib.fs_nodes.restype=None
    return lib


@lru_cache(maxsize=1)
def truth_tables():
    from .flag_native_tables import tables
    one,two=tables()
    a=np.array([one[available,current,bits] for available in range(6) for current in range(2) for bits in range(32)],dtype=np.uint8)
    b=np.array([two[available,current,flag,bits] for available in range(6) for current in range(2) for flag in range(2) for bits in range(32)],dtype=np.uint8)
    a.flags.writeable=False;b.flags.writeable=False;return a,b


class World:
    def __init__(self,runs,colonies,age):
        a=np.asarray(runs,dtype=np.uint64)
        if a.ndim!=2 or a.shape[1]!=3 or not a.flags.c_contiguous:raise ValueError('contiguous complete word runs required')
        self.lib=library();self.handle=self.lib.fs_create(pointer(a),len(a),colonies,age)
        if not self.handle:raise ValueError('canonical unforced flag state required')
        one,two=truth_tables();self.lib.fs_tables(self.handle,one.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8)),two.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8)))
    def close(self):
        if self.handle:self.lib.fs_free(self.handle);self.handle=None
    def __enter__(self):return self
    def __exit__(self,*args):self.close()
    @property
    def info(self):
        if not self.handle:raise ValueError('closed physical stream')
        a=np.empty(15,dtype=np.uint64);self.lib.fs_info(self.handle,pointer(a))
        return dict(zip(('age','time','chunks','rejected','queries','leaf_evaluations','peak_nodes','live_nodes','last_ticks','last_nodes','last_queries','period_bytes','root','verified_queries','reused_queries'),map(int,a)))
    def advance(self,ticks,*,budget=262144):
        if not self.handle:raise ValueError('closed physical stream')
        if not isinstance(ticks,int) or not 0<ticks<1<<32 or not isinstance(budget,int) or budget<1024:raise ValueError('positive bounded query and host node/table budget required')
        code=self.lib.fs_advance(self.handle,ticks,budget)
        if code:raise RuntimeError(self.lib.fs_error(self.handle).decode()+f' ({code})')
        return self.info
    def run(self,ticks,*,chunk=65536,budget=262144):
        if not isinstance(ticks,int) or ticks<0:raise ValueError('nonnegative physical duration required')
        stop=self.info['time']+ticks
        while self.info['time']<stop:self.advance(min(chunk,stop-self.info['time']),budget=budget)
        return self.info
    def at(self,position):
        if not self.handle or not isinstance(position,int) or not 0<=position<self.info['period_bytes']:raise ValueError('physical byte position outside live ring')
        value=int(self.lib.fs_at(self.handle,position))
        if value>=1<<18:raise ValueError('invalid physical byte')
        return value
    def snapshot(self):
        info=self.info;nodes=np.empty((info['live_nodes']+(1<<18),3),dtype=np.uint64);self.lib.fs_nodes(self.handle,pointer(nodes));return nodes,info['root']
