"""Depth is initialization data for the experimental fixed optimized ROM.

Both logical procedure backups and represented raw holder/controller fields are
materialized. This initializer is not an evolving host interpreter.
"""
from functools import lru_cache
from . import packed28_holder_rule as f,packed28_holder_projected as r,packed28_holder_program as p


@lru_cache(maxsize=1)
def info_positions():return {address:i for i,address in enumerate(p.layout().info)}


def physical_cells(top_cells,depth):
    if not isinstance(depth,int) or depth<0 or not isinstance(top_cells,int) or top_cells<1:raise ValueError('positive top size and finite nonnegative depth required')
    return top_cells*f.Q**depth


def cell_at(top,depth,position):
    if not isinstance(position,int):raise ValueError('integral physical position required')
    size=physical_cells(len(top),depth);position%=size
    if depth==0:return top[position]
    values={'address':position%f.Q};parents={};info=info_positions()
    for d in f.OFFSETS:
        logical=(position+d)%size;parent,address=divmod(logical,f.Q)
        if address in info:
            if parent not in parents:parents[parent]=f.encode_cell(r.lift(cell_at(top,depth-1,parent)))
            values[f's{d+2}_data']=parents[parent][info[address]]
    return r.Cell(**values)


def decode_parent(top,depth,position):
    if depth<1:raise ValueError('positive encoded depth required')
    words=tuple(cell_at(top,depth,position*f.Q+address).s2_data for address in p.layout().info)
    raw=f.decode_cell(words);value=r.project(raw)
    if r.lift(value)!=raw:raise ValueError('all seven metadata records must match computed Address')
    return value


def resources(top_cells,depth):
    sites=physical_cells(top_cells,depth)
    return dict(depth=depth,physical_cells=sites,packed_bits=sites*r.WIDTH,dense_bytes=sites*len(r.SCHEMA)*8,ticks_per_top_step=f.U**depth,fixed_rule=r.identity())


def coherent_cell(logical,position):
    """Diagnostic/initialization lift of a logical core-state accessor.

    Copies all procedures and Wf; own raw geometry/Signal stays at this holder.
    Caller supplies immutable initial data, never evolving simulated transitions.
    """
    own=logical(position);values={n:getattr(own,n) for n,_ in f.GEOMETRY}
    for d in f.OFFSETS:
        source=logical(position+d)
        for n,_ in f.PROCEDURE:values[f's{d+2}_{n}']=getattr(source,n)
        for n in ('wf1','wf2'):values[f'w{d+2}_{n}']=getattr(source,n)
    return r.Cell(**values)
