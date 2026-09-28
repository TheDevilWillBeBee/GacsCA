"""Compile the one complete word-rule expression into a fixed local C function."""
import ctypes
import hashlib
from pathlib import Path
import subprocess
import numpy as np
from . import clock_rule as r
from .canonical_clock_description import build as canonical_description
from .canonical_flags import transition as check_geometry
from .wordcode import LIT,NAND,ADD,SHR,EQ,LT


def expression_source(program,name):
    lines=[f'void {name}(const uint64_t *in,uint64_t *out) {{',f' uint64_t w[{program.wires}];',f' memcpy(w,in,{program.inputs}*sizeof(uint64_t));']
    for i,(op,a,b) in enumerate(program.operations,program.inputs):
        aa,bb=f'w[{a}]',f'w[{b}]'
        if op==LIT:expr=f'UINT64_C(0x{a:016x})'
        elif op==NAND:expr=f'~({aa}&{bb})'
        elif op==ADD:expr=f'{aa}+{bb}'
        elif op==SHR:expr=f'{bb}<64?{aa}>>{bb}:0'
        elif op==EQ:expr=f'{aa}=={bb}'
        elif op==LT:expr=f'{aa}<{bb}'
        else:raise ValueError('unsupported physical arithmetic')
        lines.append(f' w[{i}]={expr};')
    lines.extend(f' out[{i}]=w[{wire}];' for i,wire in enumerate(program.outputs));lines.append('}')
    return '\n'.join(lines)+'\n'


def library():
    source='#include <stdint.h>\n#include <stddef.h>\n#include <string.h>\n'
    source+=expression_source(canonical_description(),'ww_local')
    source+=f'''void ww_dense(const uint64_t *cells,uint64_t *out,size_t n) {{
 uint64_t neighbors[{11*r.FIELDS}];
 for (size_t i=0;i<n;++i) {{
  for (int j=-5;j<=5;++j) {{
   size_t p=(i+n+(j>=0?(size_t)j%n:n-((size_t)(-j)%n)))%n;
   memcpy(neighbors+(j+5)*{r.FIELDS},cells+p*{r.FIELDS},{r.FIELDS}*sizeof(uint64_t));
  }}
  ww_local(neighbors,out+i*{r.FIELDS});
 }}
}}
'''
    digest=hashlib.sha256(source.encode()+b'cc-O2-canonical-clock-v1').hexdigest()[:16]
    build=Path(__file__).resolve().parents[2]/'figs/fixed_rule/build'/('canonical_clock_'+digest);build.mkdir(parents=True,exist_ok=True)
    target=build/'rule.so'
    if not target.exists():
        path=build/'rule.c';path.write_text(source)
        subprocess.run(['cc','-O2','-std=c99','-Wall','-Wextra','-Werror','-shared','-fPIC',str(path),'-o',str(target)],check=True)
    lib=ctypes.CDLL(str(target));ptr=ctypes.POINTER(ctypes.c_uint64)
    lib.ww_local.argtypes=[ptr,ptr];lib.ww_local.restype=None
    lib.ww_dense.argtypes=[ptr,ptr,ctypes.c_size_t];lib.ww_dense.restype=None
    return lib


def array_from_cells(cells):return np.array([r.encode_cell(c) for c in cells],dtype=np.uint64)
def cells_from_array(array):return tuple(r.decode_cell(row.tolist()) for row in array)
def pointer(array):return array.ctypes.data_as(ctypes.POINTER(ctypes.c_uint64))


def validate(array):
    if not isinstance(array,np.ndarray) or array.dtype!=np.uint64 or not array.flags.c_contiguous or array.ndim!=2 or array.shape[1]!=r.FIELDS or not len(array):
        raise ValueError('complete contiguous uint64 raw states required')
    for name,width in r.SCHEMA:
        if width<64 and np.any(array[:,r.COL[name]]>=1<<width):raise ValueError('raw field outside alphabet')


def local_step(cells,lib=None):
    check_geometry(cells)
    array=array_from_cells(cells);validate(array)
    if len(array)!=11:raise ValueError('eleven local cells required')
    out=np.empty((1,r.FIELDS),dtype=np.uint64);(lib or library()).ww_local(pointer(array),pointer(out))
    return cells_from_array(out)[0]


def dense_step(array,lib=None):
    validate(array)
    if len(array)%r.Q or np.any(array[:,r.COL['address']]!=(int(array[0,r.COL['address']])+np.arange(len(array),dtype=np.uint64))%r.Q) or np.any(array[:,r.COL['age']]!=array[0,r.COL['age']]):
        raise ValueError('canonical periodic Address and uniform Age required')
    out=np.empty_like(array);(lib or library()).ww_dense(pointer(array),pointer(out),len(array));return out
