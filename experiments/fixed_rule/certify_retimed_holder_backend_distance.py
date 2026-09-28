"""Audit CUDA flight distance with independent values in unused registers.

All positions between event breakpoints are affine branches of the inspected
function. The finite check covers their endpoints for every target equivalence
class; the report records that piecewise argument separately. No GPU or upper
transition is executed. The original CUDA source is never changed.
"""
import argparse
import ctypes
import hashlib
import json
from pathlib import Path
import resource
import subprocess
import time

import numpy as np
from gacsca.fixed_rule import retimed_holder_core as c, retimed_holder_rule as f
from gacsca.fixed_rule import retimed_holder_program as p, retimed_holder_quotient as q
from experiments.fixed_rule.audit_small_holder_position_events import sha

CUDA=Path('gacsca/fixed_rule/small_holder_resident_independent.cu')


def function_source():
    source=CUDA.read_text();start=source.index('__device__ uint64_t independent_distance(')
    end=source.index('\n}\n',start)+3
    return source[start:end]


def audit(body=None):
    body=function_source() if body is None else body
    rom=np.ascontiguousarray(p.base_rom(),dtype=np.uint64);g=p.layout()
    assert not np.any(rom[:,0]==c.WAIT),'WAIT needs a separate counter-flight proof'
    assert np.flatnonzero(rom[:,5]).tolist()==[0]
    assert np.flatnonzero(rom[:,6]).tolist()==[len(rom)-1]
    definitions='\n'.join(f'#define P_{name.upper()} {index}' for name,index in q.COL.items())
    source='#include <cstdint>\n#include <set>\n#include <vector>\n#include <unordered_map>\n#define __device__\n'+definitions+f'\n#define ROM_ROWS {len(rom)}\n#define MEM_ROWS {g.memory_count}\n#define Q {f.Q}\n'
    source+='struct World { const uint64_t *rom; };\nuint64_t meta(World w,uint64_t a,unsigned k){return w.rom[a*7+k];}\n'+body
    source+='\nextern "C" uint64_t check(const uint64_t *rom,uint64_t *bad){\n World w{rom};\n // Derive possible non-flight actions from actual ROM records, not address\n // arithmetic in the function under test. Endpoint reflection is always an\n // event, even when a particular controller value would be unchanged.\n std::unordered_map<uint64_t,std::vector<uint64_t>> fetch,memory;\n for(uint64_t a=0;a<ROM_ROWS;++a){\n  const uint64_t *r=rom+7*a;\n  if(r[0]==0)memory[r[1]].push_back(a);\n  else fetch[r[1]].push_back(a);\n }\n uint64_t checked=0;\n for(unsigned phase=0;phase<8;++phase)\n for(unsigned direction=0;direction<2;++direction)\n for(unsigned value=0;value<2;++value)\n for(uint64_t index=0;index<Q+4;++index){\n  const uint64_t extras[]={Q,UINT64_C(0xffffffff),UINT64_C(0x100000000),UINT64_MAX};\n  uint64_t target=index<Q?index:extras[index-Q];\n  uint64_t h[P_LP_TARGET-P_HEAD]={0};\n  h[0]=1;h[P_PHASE-P_HEAD]=phase;h[P_DIRECTION-P_HEAD]=direction;\n  h[P_PC-P_HEAD]=17;h[P_RA-P_HEAD]=31;h[P_RB-P_HEAD]=47;h[P_RD-P_HEAD]=61;\n  if(phase==0)h[P_PC-P_HEAD]=target&UINT64_C(0xffffffff);\n  if(phase==1||phase==4||phase==5)h[P_RA-P_HEAD]=target&UINT64_C(0xffffffff);\n  if(phase==2)h[P_RB-P_HEAD]=target;\n  if(phase==3||phase==6)h[P_RD-P_HEAD]=target;\n  h[P_VALUE-P_HEAD]=value;\n  std::vector<uint64_t> events{ROM_ROWS-1};\n  auto append=[&](const std::unordered_map<uint64_t,std::vector<uint64_t>>& map,uint64_t key){\n   auto it=map.find(key);if(it!=map.end())for(auto a:it->second)events.push_back(a);\n  };\n  if(phase==0)append(fetch,h[P_PC-P_HEAD]);\n  if(phase==1||phase==4||phase==5)append(memory,h[P_RA-P_HEAD]);\n  if(phase==2)append(memory,h[P_RB-P_HEAD]);\n  if(phase==3)append(memory,h[P_RD-P_HEAD]);\n  if(phase==6&&value&&target<ROM_ROWS)events.push_back(target);\n  std::set<uint64_t> positions{0,1,ROM_ROWS-2,ROM_ROWS-1};\n  for(auto a:events){positions.insert(a);if(a)positions.insert(a-1);if(a+1<ROM_ROWS)positions.insert(a+1);}\n  for(auto a:positions){\n   uint64_t expected=a;\n   if(!direction){uint64_t next=ROM_ROWS-1;for(auto event:events)if(event>=a&&event<next)next=event;expected=next-a;}\n   uint64_t got=independent_distance(w,a,h);++checked;\n   if(got!=expected){bad[0]=phase;bad[1]=direction;bad[2]=value;bad[3]=target;bad[4]=a;bad[5]=expected;bad[6]=got;return 0;}\n  }\n }\n return checked;\n}\n'
    digest=hashlib.sha256(source.encode()).hexdigest()
    directory=Path('figs/fixed_rule/build')/('retimed_backend_distance_'+digest[:20]);directory.mkdir(parents=True,exist_ok=True)
    cpp=directory/'check.cpp';library=directory/'check.so'
    if cpp.exists():assert cpp.read_text()==source
    else:cpp.write_text(source)
    if not library.exists():
        with (directory/'build.log').open('w') as log:
            subprocess.run(['c++','-O2','-std=c++17','-shared','-fPIC',str(cpp),'-o',str(library)],stdout=log,stderr=subprocess.STDOUT,check=True)
    lib=ctypes.CDLL(str(library.resolve()));lib.check.argtypes=[ctypes.c_void_p,ctypes.c_void_p];lib.check.restype=ctypes.c_uint64
    bad=np.zeros(7,dtype=np.uint64);count=lib.check(rom.ctypes.data,bad.ctypes.data)
    assert count,('flight distance crossed or missed event',bad.tolist())
    return dict(passed=True,checked_breakpoint_cases=count,phases=8,directions=2,nonzero_value_classes=2,
                target_classes=f.Q+4,unused_registers_distinct=True,WAIT_absent_from_fixed_ROM=True,
                extracted_function_sha256=hashlib.sha256(body.encode()).hexdigest(),
                generated_source=str(cpp),generated_source_sha256=sha(cpp),binary_sha256=sha(library),
                scope='Canonical coherent one-head core, actual fixed ROM, regular active clock, mail noninterference supplied separately. Between target/endpoints the inspected distance and next-event oracle are affine in head Address. This is a skip-distance check, not a whole backend or depth-two execution proof.')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();out=Path(args.output)
    if out.exists():raise FileExistsError('preserve evidence')
    start=time.perf_counter();result=audit();body=function_source()
    result['mutations_rejected']=[]
    for name,old,new in (('overshoot','return target-a;','return target-a+1;'),
                         ('wrong_target_register','x=h[P_RA-H];','x=h[P_RB-H];')):
        bad=body.replace(old,new);assert bad!=body
        try:audit(bad)
        except AssertionError as error:
            assert 'flight distance crossed or missed event' in str(error)
            result['mutations_rejected'].append(name)
        else:raise AssertionError(('distance mutation accepted',name))
    result.update(descriptor_sha256=f.self_description().digest(),rom_sha256=hashlib.sha256(p.base_rom().tobytes()).hexdigest(),
                  source_sha256={str(path):sha(path) for path in (Path(__file__),CUDA,Path(p.__file__),Path(q.__file__))},
                  seconds=time.perf_counter()-start,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':main()
