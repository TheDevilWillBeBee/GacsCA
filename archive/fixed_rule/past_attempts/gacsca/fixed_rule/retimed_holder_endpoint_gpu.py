"""GPU endpoint acceleration for the proved, noiseless canonical entry domain.

This software backend advances U-1 ticks by the complete C image, then performs
commit. It does not redefine the physical rule. One fixed instruction stream and
ROM serve every colony count; no hierarchy-depth branch or host transition runs.
General faults and intermediate-time evolution are outside this backend domain.
"""
import ctypes
from functools import lru_cache
import hashlib
from pathlib import Path
import subprocess
import numpy as np
from . import retimed_holder_rule as f,retimed_holder_core as c,retimed_holder_program as p
from . import retimed_holder_projected as r,retimed_holder_quotient as q,retimed_holder_terminal_checks as checks


def header():
    from experiments.fixed_rule.certify_retimed_holder_terminal_layout import certify
    certify();g=p.layout();start,end=g.stage_ranges[4]
    code=g.instructions[start:end]
    # This is a fixed source-generation check, not evolving level dispatch.
    assert f.self_description().digest()=='6e2f29f61bf281ec5d346cd58e717cf7e5b0afea263d2c17a18a58de295d8d23'
    assert hashlib.sha256(p.base_rom().tobytes()).hexdigest()=='4dc026b976c541001421dd214df9c9e33f6f851053d4ba5f53dbbec925ba5645'
    for op in code:
        if op.kind==c.LIT:assert op.d<g.memory_count
        elif op.kind in c.ALU_KINDS:assert max(op.a,op.b,op.d)<g.memory_count
        elif op.kind==c.LOAD:assert op.a<g.memory_count
        elif op.kind==c.META:assert op.a<g.memory_count and op.b<7
        else:assert op.kind==c.IF_THIRD
    constants=dict(Q=f.Q,FIELDS=f.FIELDS,BANK=g.memory_count+5,INFO_BASE=g.info[0],RESERVED=p.RESERVED,INSTRUCTIONS=len(code),ADDRESS=f.COL['address'],FLAG1=f.COL['f1'],FLAG2=f.COL['f2'])
    constants.update({'OP_'+name:getattr(c,name) for name in ('LIT','NAND','ADD','SHR','EQ','LT','LOAD','META','IF_THIRD')})
    result=''.join(f'#define {key} {value}ULL\n' for key,value in constants.items())
    result+='__device__ __constant__ unsigned WIDTHS[]={'+','.join(str(w) for _,w in f.SCHEMA)+'};\n'
    def array(name,values):return 'static const uint64_t '+name+'[]={'+','.join('UINT64_C('+str(int(v))+')' for v in values)+'};\n'
    result+=array('ROM_INIT',(r.record(a)[name] for a in range(f.Q) for name in c.STATIC))
    result+=array('CODE_INIT',(value for op in code for value in (op.kind,op.a,op.b,op.d)))
    return result


@lru_cache(maxsize=1)
def library():
    source=Path(__file__).with_suffix('.cu');generated=header()
    identity=hashlib.sha256(source.read_bytes()+generated.encode()+b'nvcc-O2-sm80-endpoint-v1').hexdigest()[:20]
    directory=source.resolve().parents[2]/'figs/fixed_rule/build'/('retimed_holder_endpoint_'+identity);directory.mkdir(parents=True,exist_ok=True)
    target=directory/'endpoint.so'
    if not target.exists():
        (directory/'retimed_holder_endpoint_generated.h').write_text(generated)
        with (directory/'build.log').open('w') as log:subprocess.run(['/usr/local/cuda/bin/nvcc','-O2','-std=c++17','-arch=sm_80','--shared','-Xcompiler','-fPIC','-I',str(directory),str(source),'-o',str(target)],stdout=log,stderr=subprocess.STDOUT,check=True)
    lib=ctypes.CDLL(str(target));ptr=ctypes.POINTER(ctypes.c_uint64);handle=ctypes.c_void_p
    for name,args in dict(te_create=[ctypes.c_size_t,ctypes.c_uint64,ptr,ptr,ctypes.POINTER(handle),ptr],te_free=[handle],te_precommit=[handle],te_commit=[handle],te_read=[handle,ptr,ptr]).items():
        method=getattr(lib,name);method.argtypes=args;method.restype=None if name=='te_free' else ctypes.c_int
    return lib


def pointer(array):return array.ctypes.data_as(ctypes.POINTER(ctypes.c_uint64))


def allocation_bytes(n):
    g=p.layout();instructions=g.stage_ranges[4][1]-g.stage_ranges[4][0]
    return 8*(2*n*(g.memory_count+5)+n*f.FIELDS+4*n+f.Q*7+instructions*4)+4*n


class World:
    def __init__(self,bank,signals,*,device_budget=32*1024**2):
        # Canonical geometry, coherent replicas, zero controller/mail/flags/Wf
        # are built into this representation. Importing a full state uses the
        # guarded from_snapshot constructor below.
        g=p.layout()
        if not isinstance(bank,np.ndarray) or bank.dtype!=np.uint64 or bank.ndim!=2 or bank.shape[1]!=g.memory_count+5 or not 0<len(bank)<=1<<20:raise ValueError('complete uint64 MEM/tail banks required')
        if not isinstance(signals,np.ndarray) or signals.dtype!=np.uint64 or signals.shape!=(len(bank),2) or np.any(signals>1):raise ValueError('localized coherent Boolean Signals required')
        if type(device_budget) is not int or not 1<=device_budget<=8*1024**3 or allocation_bytes(len(bank))>device_budget:raise ValueError('explicit endpoint device budget exceeded')
        self.lib=library();self.handle=ctypes.c_void_p();allocated=ctypes.c_uint64()
        code=self.lib.te_create(len(bank),device_budget,pointer(np.ascontiguousarray(bank)),pointer(np.ascontiguousarray(signals)),ctypes.byref(self.handle),ctypes.byref(allocated))
        if code:raise RuntimeError(f'endpoint allocation failed: {code}')
        self.colonies=len(bank);self.device_bytes=int(allocated.value);assert self.device_bytes==allocation_bytes(self.colonies)
        self.age=0;self.time=0
    @classmethod
    def from_snapshot(cls,state,**kwargs):
        if int(state['age'])!=0 or int(state['time'])<0 or int(state['time'])%f.U:raise ValueError('Age-zero period boundary required')
        wanted=dict(precommit_bank=state['bank'],committed_bank=state['bank'],signals=state['signals'])
        checks.check(state,wanted,age=0,time=int(state['time']))
        world=cls(state['bank'],state['signals'],**kwargs);world.time=int(state['time']);return world
    def precommit(self):
        if not self.handle or self.age!=0:raise ValueError('live Age-zero endpoint world required')
        code=self.lib.te_precommit(self.handle)
        if code:raise ValueError(f'endpoint input/computation rejected atomically: {code}')
        self.age=f.U-1;self.time+=f.U-1
    def commit(self):
        if not self.handle or self.age!=f.U-1:raise ValueError('live precommit world required')
        code=self.lib.te_commit(self.handle)
        if code:raise RuntimeError(f'endpoint commit failed: {code}')
        self.age=0;self.time+=1
    def period(self):self.precommit();self.commit()
    def read(self,*,max_bytes=64*1024**2):
        count=self.colonies*(p.layout().memory_count+7)*8
        if not self.handle or count>max_bytes:raise ValueError('live world and adequate readback budget required')
        bank=np.empty((self.colonies,p.layout().memory_count+5),dtype=np.uint64);signals=np.empty((self.colonies,2),dtype=np.uint64)
        if self.lib.te_read(self.handle,pointer(bank),pointer(signals)):raise RuntimeError('endpoint readback failed')
        return bank,signals
    def snapshot(self):
        bank,signals=self.read();n=self.colonies
        rows=np.zeros((n,64,len(q.SCHEMA)),dtype=np.uint64);counts=np.zeros(n,dtype=np.uint64)
        for col in range(n):
            for a in (*range(1,6),*range(f.Q-5,f.Q)):
                signal=checks.signal_word(a,*signals[col])
                if not signal:continue
                at=int(counts[col]);counts[col]+=1
                data=bank[col,a] if a<p.layout().memory_count else bank[col,p.layout().memory_count+a-(f.Q-5)]
                rows[col,at]=q.encode_cell(q.Cell(data=int(data),address=a,age=self.age,signal=signal))
        return dict(bank=bank,signals=signals,active_rows=rows,counts=counts,flags=np.zeros((n*f.Q//64,2),dtype=np.uint64),age=np.array(self.age,dtype=np.uint64),time=np.array(self.time,dtype=np.uint64))
    def close(self):
        if self.handle:self.lib.te_free(self.handle);self.handle=None
    def __enter__(self):return self
    def __exit__(self,*args):self.close()
