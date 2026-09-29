"""Same scalar event expression, gathering only its exact syntactic input support.

All 70 referenced words are supplied, including zero packet inputs. There is no
change to event timing, guards, hard-wired ROM or physical transition semantics.
"""
import ctypes
from functools import lru_cache
import hashlib
from pathlib import Path
import subprocess
from . import small_holder_register_events as registers
from . import small_holder_core as c
from . import small_holder_quotient as q
from . import small_holder_resident_period as period
from . import small_holder_resident_independent as independent
from .wordcode import LIT

event_program = registers.event_program
EVENT_FIELDS = registers.EVENT_FIELDS


def support():
    p=registers.event_program()
    return tuple(sorted({w for op,a,b in p.operations if op!=LIT for w in (a,b) if w<p.inputs}
                        | {w for w in p.outputs if w<p.inputs}))


def input_source():
    used=set(support())
    lines=['__device__ void supported_event_input(World w,size_t col,uint64_t a,const uint64_t*h,uint64_t where,uint64_t age,uint64_t*in){']
    for offset in range(-5,6):
        fields=[(k,n) for k,(n,_) in enumerate(c.SCHEMA) if (offset+5)*c.FIELDS+k in used]
        if not fields:continue
        lines.append('{')
        lines.append(f'int64_t neighbor=(int64_t)a+({offset}); size_t source_col=col;')
        lines.append('if(neighbor<0){neighbor+=Q;source_col=col?col-1:w.colonies-1;}')
        # Same event-center domain as frozen kernel: a < ROM_ROWS and ROM_ROWS+5 < Q.
        lines.append('uint64_t at=(uint64_t)neighbor;')
        for k,name in fields:
            if name in c.STATIC:value=f'meta(w,at,{c.STATIC.index(name)})'
            elif name=='address':value='at'
            elif name=='age':value='age'
            elif name=='data':value='bankrow(at)<0?0:w.data[source_col*BANK_ROWS+bankrow(at)]'
            elif name in ('head',*c.CONTROL):value=f'(source_col==col&&at==where)?h[{q.COL[name]-q.COL["head"]}]:0'
            elif name.startswith(('lp_','rp_')):value='0'
            else:raise AssertionError(f'review new event input {name}')
            lines.append(f'in[{((offset+5)*c.FIELDS+k)*period.WORKERS}]={value};')
        lines.append('}')
    return '\n'.join(lines+['}'])+'\n'


@lru_cache(maxsize=1)
def library():
    base=Path(registers.library()._name).parent
    names=('small_holder_resident_period.cu','small_holder_resident_independent.cu','small_holder_resident_gather.cu','small_holder_resident_period_generated.h')
    sources={name:(base/name).read_text() for name in names}
    for name in names[1:3]:
        source=sources[name]
        begin=source.index('    for(int j=-5;j<=5;++j)')
        end=source.index('    register_event_local(in,out,tmp);++evaluations;',begin)
        old=source[begin:end]
        # Refuse source drift rather than replacing an unreviewed calculation.
        if old.count('independent_input(')!=1 or old.count('source_col=col')!=2:
            raise AssertionError('review changed neighborhood construction')
        source=source[:begin]+'    supported_event_input(w,col,(uint64_t)a,h,where,w.age+elapsed,in);\n'+source[end:]
        if name==names[1]:
            needle='#include "small_holder_resident_period.cu"\n'
            if source.count(needle)!=1:raise AssertionError('changed include')
            source=source.replace(needle,needle+input_source())
        sources[name]=source
    identity=hashlib.sha256(('nvcc-O2-sm80-supported-events-v1'+''.join(k+v for k,v in sorted(sources.items()))).encode()).hexdigest()[:20]
    directory=base.parent/('small_holder_supported_events_'+identity);directory.mkdir(parents=True,exist_ok=True)
    target=directory/'events.so'
    if not target.exists():
        for name,text in sources.items():(directory/name).write_text(text)
        with (directory/'build.log').open('w') as log:
            subprocess.run(['/usr/local/cuda/bin/nvcc','-O2','-std=c++17','-arch=sm_80','--shared','-Xcompiler','-fPIC','--ptxas-options=-v',str(directory/names[2]),'-o',str(target)],stdout=log,stderr=subprocess.STDOUT,check=True)
    lib=ctypes.CDLL(str(target))
    for name in ('rp_create','rp_free','rp_info','rp_initial','rp_bank','rp_restore_age','rp_jump','rp_step','rp_read','ri_run','rg_run'):
        new,old=getattr(lib,name),getattr(registers.library(),name)
        new.argtypes,new.restype=old.argtypes,old.restype
    return lib


class World(registers.World):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        try:self.lib=library()
        except BaseException:self.close();raise

    @classmethod
    def from_raw_chunks(cls,*args,**kwargs):
        world=super().from_raw_chunks(*args,**kwargs)
        try:world.lib=library();return world
        except BaseException:world.close();raise
