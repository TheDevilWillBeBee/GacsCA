"""One immutable program projection of the coupled controller/maintenance rule.

Address now evolves. The full raw rule does NOT preserve the lift manifold;
represented program regeneration is essential, not a static-Address conjugacy.
"""
from dataclasses import make_dataclass,field
from functools import lru_cache
import hashlib
import json
import numpy as np
from . import repair_b_rule as full,repair_b_program as program

SCHEMA=tuple((name,width) for name,width in full.SCHEMA if name not in full.STATIC)
COL={name:i for i,(name,_) in enumerate(SCHEMA)}
WIDTH=sum(w for _,w in SCHEMA)
NEIGHBORHOOD=full.NEIGHBORHOOD


def validate_cell(self):
    for name,width in SCHEMA:
        value=getattr(self,name)
        if not isinstance(value,int) or not 0<=value<1<<width:raise ValueError(f'{name} outside fixed projected alphabet')


Cell=make_dataclass('Cell',[(name,int,field(default=0)) for name,_ in SCHEMA],frozen=True,namespace={'__post_init__':validate_cell,'__module__':__name__})


@lru_cache(maxsize=1)
def rom():
    table=np.ascontiguousarray(program.template()[:,[full.COL[n] for n in full.STATIC]])
    table.flags.writeable=False;return table


def static_record(address):
    if address<len(rom()):return dict(zip(full.STATIC,map(int,rom()[address])))
    return dict(zip(full.STATIC,(full.fallback(address,i) for i in range(len(full.STATIC)))))


def lift(c):return full.Cell(**static_record(c.address),**{name:getattr(c,name) for name,_ in SCHEMA})
def project(c):return Cell(**{name:getattr(c,name) for name,_ in SCHEMA})
def local_step(cells):return project(full.local_step(tuple(lift(c) for c in cells)))
def step_ring(cells):return tuple(local_step(tuple(cells[(i+j)%len(cells)] for j in NEIGHBORHOOD)) for i in range(len(cells)))
def encode_cell(c):return tuple(getattr(c,n) for n,_ in SCHEMA)
def decode_cell(words):
    if len(words)!=len(SCHEMA):raise ValueError('complete raw word record required')
    return Cell(**dict(zip((n for n,_ in SCHEMA),map(int,words))))
def array_from_cells(cells):return np.array([encode_cell(c) for c in cells],dtype=np.uint64)
def cells_from_array(array):return tuple(decode_cell(row.tolist()) for row in array)
def project_array(array):return np.ascontiguousarray(array[:,[full.COL[name] for name,_ in SCHEMA]])


def encode_cores(cells):return project_array(program.encode_cores(tuple(lift(c) for c in cells)))


def decode_cores(cores):
    g=program.layout()
    if len(cores)%g.computation_cells:raise ValueError('partial computation window')
    result=[]
    for base in range(0,len(cores),g.computation_cells):
        raw=full.decode_cell(cores[base+np.array(g.info),COL['data']].tolist())
        projected=project(raw)
        if lift(projected)!=raw:raise ValueError('represented program record inconsistent with computed Address')
        result.append(projected)
    return tuple(result)


def identity():return dict(schema=SCHEMA,width=WIDTH,words=len(SCHEMA),neighborhood=NEIGHBORHOOD,full_rule=full.identity(),rom_sha256=hashlib.sha256(json.dumps(rom().tolist(),separators=(',',':')).encode()).hexdigest())
