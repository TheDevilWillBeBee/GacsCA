"""Late exact sparse events with transport of multiple separated controllers.

Existing per-head event distances remain. Additional pair bounds stop transport
before any two closing heads enter the radius-one interaction zone. Full local
ticks resolve interactions; no field is merged by the transport shortcut.
"""
import ctypes
from functools import lru_cache
import hashlib
from pathlib import Path
import subprocess
from . import compact16_holder_late_events as base

PAIR_BOUND=r'''
 // During this jump every head has a constant velocity: all individual
 // reflection, waiting and instruction events already bound limit above.
 for(size_t i=0;i<w.counts[col]&&limit;++i){
  const uint64_t*x=w.rows+(col*SLOTS+i)*PACKED_WORDS;if(!get(x,P_HEAD))continue;
  int vx=waiting(w,x)?0:get(x,P_DIRECTION)?-1:1;
  for(size_t j=i+1;j<w.counts[col]&&limit;++j){
   const uint64_t*y=w.rows+(col*SLOTS+j)*PACKED_WORDS;if(!get(y,P_HEAD))continue;
   int vy=waiting(w,y)?0:get(y,P_DIRECTION)?-1:1;
   if(vx>vy){uint64_t gap=get(y,P_ADDRESS)-get(x,P_ADDRESS);
    uint64_t safe=gap>2?(gap-2)/(vx-vy):0;if(safe<limit)limit=safe;
   }
  }
 }
'''


def source_text(*,unsafe=False):
    source=base.source_text();old='if(a>=ROM_ROWS||++heads>1){limit=0;break;}'
    assert source.count(old)==1;source=source.replace(old,'if(a>=ROM_ROWS){limit=0;break;}')
    marker=' w.status[3*col]=limit;';assert source.count(marker)==1
    return source.replace(marker,('' if unsafe else PAIR_BOUND)+marker)


@lru_cache(maxsize=2)
def library(unsafe=False):
    source=source_text(unsafe=unsafe);controller=Path(base.independent.__file__).with_suffix('.cu').read_text();header=base.period.header()
    identity=hashlib.sha256(source.encode()+controller.encode()+header.encode()+b'nvcc-O2-sm80-late-multi-v1').hexdigest()[:20]
    directory=Path(__file__).resolve().parents[2]/'figs/fixed_rule/build'/('compact16_holder_late_multi_'+identity);directory.mkdir(parents=True,exist_ok=True);target=directory/'events.so'
    if not target.exists():
        (directory/'compact16_holder_resident_period.cu').write_text(source);(directory/'compact16_holder_resident_period_generated.h').write_text(header)
        path=directory/'compact16_holder_resident_independent.cu';path.write_text(controller)
        with (directory/'build.log').open('w') as out:subprocess.run(['/usr/local/cuda/bin/nvcc','-O2','-std=c++17','-arch=sm_80','--shared','-Xcompiler','-fPIC',str(path),'-o',str(target)],check=True,stdout=out,stderr=subprocess.STDOUT)
    lib=ctypes.CDLL(str(target))
    for name in ('rp_create','rp_free','rp_info','rp_initial','rp_bank','rp_restore_age','rp_jump','rp_step','rp_read','rp_snapshot','ri_run'):
        original=getattr(base.library(),name);fn=getattr(lib,name);fn.argtypes=original.argtypes;fn.restype=original.restype
    return lib


class World(base.World):
    def __init__(self,raw,**kwargs):
        super().__init__(raw,**kwargs)
        try:self.lib=library()
        except BaseException:self.close();raise
