"""Bounded raw chunks of the actual recursively encoded initial configuration.

Depth changes only immutable initial data. This module never evolves a state.
Every row contains all 154 raw fields, including controller backups and metadata.
"""
from functools import lru_cache
import numpy as np
from . import small_holder_rule as f,small_holder_projected as r,small_holder_core as c,small_holder_program as p

CHUNK=128


def canonical_raw(addresses):
    addresses=tuple(addresses)
    if len(addresses)>CHUNK or any(type(a) is not int or not 0<=a<f.Q for a in addresses):raise ValueError('bounded canonical address chunk required')
    out=np.zeros((len(addresses),f.FIELDS),dtype=np.uint64)
    if not addresses:return out
    base=np.array(addresses,dtype=np.int64);out[:,f.COL['address']]=base
    rom=p.base_rom()
    for d in f.STATIC_OFFSETS:
        at=(base+d)%f.Q;inside=at<len(rom);tail=at>=f.Q-5
        for k,name in enumerate(c.STATIC):
            values=np.zeros(len(at),dtype=np.uint64)
            if k==0:values[~tail]=c.LOOP
            elif k==1:values[:]=at
            elif k==2:values[tail]=31
            values[inside]=rom[at[inside],k]
            out[:,f.COL[f'p{d+3}_{name}']]=values
    return out


class InitialRing:
    def __init__(self,top):
        self.top=tuple(top)
        if not self.top or any(not isinstance(x,r.Cell) for x in self.top):raise ValueError('complete projected top states required')
        self.raw_top=tuple(f.encode_cell(r.lift(x)) for x in self.top)
    def size(self,depth):
        if type(depth) is not int or depth<0:raise ValueError('nonnegative encoded depth required')
        return len(self.top)*f.Q**depth
    def raw(self,depth,positions):
        size=self.size(depth);positions=tuple(positions)
        if len(positions)>CHUNK or any(type(x) is not int for x in positions):raise ValueError('bounded integral positions required')
        positions=tuple(x%size for x in positions)
        if not depth:return np.array([self.raw_top[x] for x in positions],dtype=np.uint64).reshape(-1,f.FIELDS)
        out=canonical_raw(tuple(x%f.Q for x in positions));info={a:i for i,a in enumerate(p.layout().info)}
        cache={}
        for d in f.OFFSETS:
            selected=[]
            for i,pos in enumerate(positions):
                parent,address=divmod((pos+d)%size,f.Q)
                if address in info:selected.append((i,parent,info[address]))
            needed=tuple(dict.fromkeys(parent for _,parent,_ in selected if parent not in cache))
            if needed:
                for parent,row in zip(needed,self.raw(depth-1,needed)):cache[parent]=row
            for i,parent,word in selected:out[i,f.COL[f's{d+2}_data']]=cache[parent][word]
        return out
    def chunks(self,depth,*,start=0,count=None,chunk=CHUNK):
        size=self.size(depth)
        if type(start) is not int or type(chunk) is not int or not 1<=chunk<=CHUNK:raise ValueError('bounded chunk and integral start required')
        count=size if count is None else count
        if type(count) is not int or count<0:raise ValueError('nonnegative count required')
        for offset in range(0,count,chunk):
            yield self.raw(depth,range(start+offset,start+min(count,offset+chunk)))
    def resources(self,depth):
        sites=self.size(depth)
        return dict(encoded_depth=depth,physical_sites=sites,lower_colonies=sites//f.Q if depth else 0,
                    raw_bits=f.WIDTH,projected_bits=r.WIDTH,raw_words=f.FIELDS,
                    chunk_bytes=CHUNK*f.FIELDS*8,physical_ticks_per_top_step=f.U**depth,
                    description_sha256=f.self_description().digest())
