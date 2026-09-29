"""Exact run-length compression of repeated nine-word physical flag blocks.

Coherent boundary signals, canonical geometry and post-capture ages are required.
Each packed output bit still has radius five. Arbitrary run compression does not
assume a wave shape/speed; the only time skip is an actual fixed-point check,
stopped at a forcing-clock boundary. The full evaluator is not replaced here.
"""
import ctypes
from functools import lru_cache
import hashlib
from pathlib import Path
import subprocess
import numpy as np
from . import delivery_rule as r

WORDS=r.Q//64
BLOCK=9
COLUMNS=1+2*BLOCK
MASK=(1<<64)-1


@lru_cache(maxsize=1)
def library():
    source=Path(__file__).with_suffix('.c');old=source.with_name('flag_words.c').read_text()
    kernel=old[old.index('static int window'):old.index('void fw_free')]
    digest=hashlib.sha256(source.read_bytes()+kernel.encode()+b'cc-O3-flag-blocks-v1').hexdigest()[:16]
    build=source.resolve().parents[2]/'figs/fixed_rule/build'/('flag_blocks_'+digest);build.mkdir(parents=True,exist_ok=True);target=build/'flags.so'
    if not target.exists():
        (build/'flag_word_kernel.h').write_text(kernel)
        subprocess.run(['cc','-O3','-std=c99','-Wall','-Wextra','-Werror','-shared','-fPIC','-I',str(build),str(source),'-o',str(target)],check=True)
    lib=ctypes.CDLL(str(target));ptr=ctypes.POINTER(ctypes.c_uint64);byte=ctypes.POINTER(ctypes.c_uint8);handle=ctypes.c_void_p
    lib.fb_create.argtypes=[ptr,ctypes.c_size_t,byte,byte,ctypes.c_size_t,ctypes.c_uint64];lib.fb_create.restype=handle
    lib.fb_free.argtypes=[handle];lib.fb_free.restype=None
    lib.fb_run.argtypes=[handle,ctypes.c_uint64,ctypes.c_int];lib.fb_run.restype=ctypes.c_int
    lib.fb_size.argtypes=[handle];lib.fb_size.restype=ctypes.c_size_t
    lib.fb_export.argtypes=[handle,ptr];lib.fb_export.restype=None
    lib.fb_info.argtypes=[handle,ptr];lib.fb_info.restype=None
    lib.fw_word.argtypes=[ptr,ptr,*([ctypes.c_int]*5)];lib.fw_word.restype=None
    return lib


def pointer(a):return a.ctypes.data_as(ctypes.POINTER(ctypes.c_uint64))


class World:
    def __init__(self,right_signals,left_signals,*,age=96*r.Q-1,runs=None):
        right_signals,left_signals=tuple(right_signals),tuple(left_signals)
        if not right_signals or len(right_signals)!=len(left_signals) or any(v not in (0,1) for v in (*right_signals,*left_signals)):raise ValueError('one pair of coherent signal bits per colony required')
        if not isinstance(age,int) or not 96*r.Q-1<=age<r.U:raise ValueError('post-capture epoch required')
        self.signals=(right_signals,left_signals);self.colonies=len(right_signals);self.lib=library()
        if runs is None:runs=[((self.colonies*WORDS+BLOCK-1)//BLOCK,*([0]*(2*BLOCK)))]
        raw=tuple(tuple(row) for row in runs)
        if any(len(row)!=COLUMNS or any(not isinstance(v,(int,np.integer)) or not 0<=v<=MASK for v in row) for row in raw):raise ValueError('complete uint64 run records required')
        a=np.array(raw,dtype=np.uint64);s1=np.array(right_signals,dtype=np.uint8);s2=np.array(left_signals,dtype=np.uint8)
        byte=ctypes.POINTER(ctypes.c_uint8)
        self.handle=self.lib.fb_create(pointer(a),len(a),s1.ctypes.data_as(byte),s2.ctypes.data_as(byte),self.colonies,age)
        if not self.handle:raise ValueError('ordered full-ring run intervals required')
    def close(self):
        if self.handle:self.lib.fb_free(self.handle);self.handle=None
    def __enter__(self):return self
    def __exit__(self,*args):self.close()
    @property
    def info(self):
        if not self.handle:raise ValueError('closed flag world')
        a=np.empty(6,dtype=np.uint64);self.lib.fb_info(self.handle,pointer(a))
        return dict(zip(('age','time','literal_ticks','quiet_ticks','word_evaluations','runs'),map(int,a)))
    @property
    def runs(self):
        if not self.handle:raise ValueError('closed flag world')
        a=np.empty((self.lib.fb_size(self.handle),COLUMNS),dtype=np.uint64);self.lib.fb_export(self.handle,pointer(a));return a
    def run(self,ticks,*,skip_fixed=True):
        if not isinstance(ticks,int) or ticks<0 or ticks>=1<<64:raise ValueError('nonnegative ticks required')
        if not self.handle:raise ValueError('closed flag world')
        code=self.lib.fb_run(self.handle,ticks,int(skip_fixed))
        if code:raise ValueError(f'flag-domain run failed: {code}')
        return self.info
    def cell(self,colony,address):
        if not 0<=colony<self.colonies or not 0<=address<r.Q:raise ValueError('site outside ring')
        a=self.runs;word=colony*WORDS+address//64;block,slot=divmod(word,BLOCK);i=int(np.searchsorted(a[:,0],block,side='right'));f1=(int(a[i,1+slot])>>(address%64))&1;f2=(int(a[i,1+BLOCK+slot])>>(address%64))&1
        age=self.info['age'];window=96*r.Q<=age<98*r.Q
        wf1=int(window and address>=r.Q-5 and self.signals[0][colony])
        wf2=int(window and address<=4 and self.signals[1][colony] and not f1)
        return f1|(f2<<1)|(wf1<<2)|(wf2<<3)


def from_word_runs(runs,colonies):
    """Lossless representation conversion; no physical transition is taken."""
    total=colonies*WORDS;blocks=(total+BLOCK-1)//BLOCK
    planes=np.zeros((2,blocks*BLOCK),dtype=np.uint64);begin=0
    for end,a,b in runs:
        end,a,b=map(int,(end,a,b))
        if not begin<end<=total or not 0<=a<=MASK or not 0<=b<=MASK:raise ValueError('invalid full word runs')
        planes[0,begin:end]=a;planes[1,begin:end]=b;begin=end
    if begin!=total:raise ValueError('incomplete word runs')
    values=np.concatenate((planes[0].reshape(blocks,BLOCK),planes[1].reshape(blocks,BLOCK)),axis=1)
    starts=np.r_[0,np.flatnonzero(np.any(values[1:]!=values[:-1],axis=1))+1]
    ends=np.r_[starts[1:],blocks]
    return np.ascontiguousarray(np.column_stack((ends.astype(np.uint64),values[starts])),dtype=np.uint64)
