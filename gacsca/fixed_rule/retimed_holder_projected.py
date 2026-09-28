"""Experimental fixed hard-wiring of the equivalent optimized complete ROM."""
from dataclasses import make_dataclass,field
from functools import lru_cache
import hashlib,json
import numpy as np
from . import retimed_holder_rule as f,retimed_holder_core as c,retimed_holder_program as p

SCHEMA=f.SCHEMA[len(f.STATIC):];COL={n:i for i,(n,_) in enumerate(SCHEMA)};WIDTH=sum(w for _,w in SCHEMA);NEIGHBORHOOD=f.NEIGHBORHOOD

def validate(self):
    for name,width in SCHEMA:
        value=getattr(self,name)
        if not isinstance(value,int) or not 0<=value<1<<width:raise ValueError(f'{name} outside projected holder alphabet')
Cell=make_dataclass('Cell',[(n,int,field(default=0)) for n,_ in SCHEMA],frozen=True,namespace={'__post_init__':validate,'__module__':__name__})

def record(address):
    if address<len(p.base_rom()):return dict(zip(c.STATIC,map(int,p.base_rom()[address])))
    return {n:c.fallback(address,i) for i,n in enumerate(c.STATIC)}
def lift(cell):
    static={f'p{k+3}_{n}':value for k in f.STATIC_OFFSETS for n,value in record((cell.address+k)%f.Q).items()}
    return f.Cell(**static,**{n:getattr(cell,n) for n,_ in SCHEMA})
def project(cell):return Cell(**{n:getattr(cell,n) for n,_ in SCHEMA})
def local_step(cells):return project(f.local_step(tuple(lift(cell) for cell in cells)))
def step_ring(cells):return tuple(local_step(tuple(cells[(i+j)%len(cells)] for j in NEIGHBORHOOD)) for i in range(len(cells)))
def encode_cell(cell):return tuple(getattr(cell,n) for n,_ in SCHEMA)
def decode_cell(words):
    if len(words)!=len(SCHEMA):raise ValueError('every replica and raw geometry field required')
    return Cell(**dict(zip((n for n,_ in SCHEMA),map(int,words))))
def array_from_cells(cells):return np.array([encode_cell(cell) for cell in cells],dtype=np.uint64)
def cells_from_array(array):return tuple(decode_cell(row.tolist()) for row in array)
def identity():return dict(schema=SCHEMA,width=WIDTH,words=len(SCHEMA),neighborhood=NEIGHBORHOOD,full_rule=f.identity(),rom_sha256=hashlib.sha256(json.dumps(p.base_rom().tolist(),separators=(',',':')).encode()).hexdigest())
