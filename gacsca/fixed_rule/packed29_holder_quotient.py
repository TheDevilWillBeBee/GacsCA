"""Coherent-state representation of the single holder physical rule.

This 25-word representation is valid only when the five procedure/Wf replicas
are coherent. It is not a physical alphabet, a self-description or a depth kernel.
The prefix executor additionally requires canonical geometry and zero flags/Wf.
Every physical 105-word state is reconstructed from five adjacent records.
"""
from dataclasses import make_dataclass,field
from functools import lru_cache
import hashlib
import json
import numpy as np
from . import packed29_holder_core as full,packed29_holder_program as program,packed29_holder_rule as physical,packed29_holder_projected as projected

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
    table=np.ascontiguousarray(program.base_rom())
    table.flags.writeable=False;return table


def static_record(address):
    if address<len(rom()):return dict(zip(full.STATIC,map(int,rom()[address])))
    return dict(zip(full.STATIC,(full.fallback(address,i) for i in range(len(full.STATIC)))))


def lift(c):return full.Cell(**static_record(c.address),**{name:getattr(c,name) for name,_ in SCHEMA})
def project(c):return Cell(**{name:getattr(c,name) for name,_ in SCHEMA})
def encode_cell(c):return tuple(getattr(c,n) for n,_ in SCHEMA)
def decode_cell(words):
    if len(words)!=len(SCHEMA):raise ValueError('complete raw word record required')
    return Cell(**dict(zip((n for n,_ in SCHEMA),map(int,words))))
def array_from_cells(cells):return np.array([encode_cell(c) for c in cells],dtype=np.uint64)
def cells_from_array(array):return tuple(decode_cell(row.tolist()) for row in array)
def project_array(array):return np.ascontiguousarray(array[:,[full.COL[name] for name,_ in SCHEMA]])


def encode_cores(cells):
    g=program.layout();template=array_from_cells(tuple(project(c) for c in program.base_template()));out=[]
    for cell in cells:
        part=template.copy();part[np.array(g.info),COL['data']]=physical.encode_cell(projected.lift(cell));out.append(part)
    return np.concatenate(out)


def decode_cores(cores):
    g=program.layout()
    if len(cores)%g.computation_cells:raise ValueError('partial logical computation window')
    result=[]
    for base in range(0,len(cores),g.computation_cells):
        raw=physical.decode_cell(cores[base+np.array(g.info),COL['data']].tolist())
        cell=projected.project(raw)
        if projected.lift(cell)!=raw:raise ValueError('all seven represented metadata records must match Address')
        result.append(cell)
    return tuple(result)
