"""Native radius-seven physical transition, compiled from the full descriptor."""
import ctypes,hashlib,subprocess
from functools import lru_cache
from pathlib import Path
import numpy as np
from . import packed29_holder_rule as f
from .word_native_and import expression_source

@lru_cache(maxsize=1)
def library():
    text='#include <stdint.h>\n#include <stddef.h>\n#include <string.h>\n'+expression_source(f.self_description(),'packed29_holder_local')
    text+='\nvoid packed29_holder_ring(const uint64_t*src,uint64_t*dst,size_t n){for(size_t i=0;i<n;++i){uint64_t in[15*'+str(f.FIELDS)+'];for(int j=-7;j<=7;++j){size_t k=(i+n+(size_t)(j+((long long)n)*7))%n;for(int w=0;w<'+str(f.FIELDS)+';++w)in[(j+7)*'+str(f.FIELDS)+'+w]=src[k*'+str(f.FIELDS)+'+w];}packed29_holder_local(in,dst+i*'+str(f.FIELDS)+');}}\n'
    digest=hashlib.sha256(text.encode()+b'holder-native-O1').hexdigest()[:20];base=Path(__file__).resolve().parents[2]/'figs/fixed_rule/build'/('packed29_holder_native_'+digest);base.mkdir(parents=True,exist_ok=True);target=base/'holder.so'
    if not target.exists():
        source=base/'holder.c';source.write_text(text);subprocess.run(['cc','-O1','-std=c99','-Wall','-Wextra','-Werror','-shared','-fPIC',str(source),'-o',str(target)],check=True)
    lib=ctypes.CDLL(str(target));ptr=ctypes.POINTER(ctypes.c_uint64)
    lib.packed29_holder_local.argtypes=[ptr,ptr];lib.packed29_holder_local.restype=None;lib.packed29_holder_ring.argtypes=[ptr,ptr,ctypes.c_size_t];lib.packed29_holder_ring.restype=None
    return lib

def pointer(a):return a.ctypes.data_as(ctypes.POINTER(ctypes.c_uint64))
def array_from_cells(cells):return np.array([f.encode_cell(cell) for cell in cells],dtype=np.uint64)
def cells_from_array(a):return tuple(f.decode_cell(row.tolist()) for row in a)
def local_step(cells):
    if len(cells)!=15:raise ValueError('exact radius seven required')
    a=array_from_cells(cells);out=np.empty(f.FIELDS,dtype=np.uint64);library().packed29_holder_local(pointer(a),pointer(out));return f.decode_cell(out.tolist())
def step_ring(cells):
    if not cells:raise ValueError('nonempty ring required')
    a=array_from_cells(cells);out=np.empty_like(a);library().packed29_holder_ring(pointer(a),pointer(out),len(a));return cells_from_array(out)
