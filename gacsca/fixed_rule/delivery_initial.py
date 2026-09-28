"""Finite initial-data nesting for the same clocked rule, with no top kernel.

The optional zero-payload cap is a flagged homogeneous periodic orbit. It is NOT an
organized quiet colony or a proved noise-robustness boundary. Its payload must
be zero because the new fixed tail-buffer metadata causes stage resets.
The old unclocked no-head canonical cap is not an orbit of the clocked rule:
its stage reset creates a head at Address 0.
"""
from dataclasses import replace
from functools import lru_cache
from . import delivery_rule as f,delivery_projected as r,delivery_program as p


def terminal_data(payload=0,age=0):
    if payload!=0:raise ValueError('tail-buffer reset invalidates a nonzero homogeneous cap payload')
    return (r.Cell(address=f.Q-1,age=age,f1=1,f2=1),)


@lru_cache(maxsize=1)
def template():
    array=r.project_array(p.template());array.flags.writeable=False;return array


@lru_cache(maxsize=1)
def info_positions():return {address:i for i,address in enumerate(p.layout().info)}


def physical_cells(top_cells,depth):
    if not isinstance(depth,int) or depth<0 or top_cells<1:raise ValueError('invalid finite initial size')
    return top_cells*f.Q**depth


def cell_at(top,depth,position):
    if not isinstance(position,int):raise ValueError('integral position required')
    position%=physical_cells(len(top),depth);g=p.layout();stack=[];positions=info_positions()
    while depth:
        parent,address=divmod(position,f.Q)
        if address>=g.computation_cells:cell=r.Cell(address=address);break
        cell=r.decode_cell(template()[address].tolist())
        if address not in positions:break
        stack.append((cell,positions[address]));position=parent;depth-=1
    else:cell=top[position]
    while stack:
        shell,word=stack.pop();cell=replace(shell,data=f.encode_cell(r.lift(cell))[word])
    return cell


def decode_parent(top,depth,position):
    if depth<1:raise ValueError('positive encoded depth required')
    raw=f.decode_cell(tuple(cell_at(top,depth,position*f.Q+a).data for a in p.layout().info))
    projected=r.project(raw)
    if r.lift(projected)!=raw:raise ValueError('inconsistent raw program record')
    return projected


def resources(top_cells,depth):
    cells=physical_cells(top_cells,depth)
    return dict(depth=depth,physical_cells=cells,raw_bits=cells*r.WIDTH,dense_bytes=cells*len(r.SCHEMA)*8,
                ticks_per_top_step=f.U**depth,lowest_core_cells=cells//f.Q*p.layout().computation_cells if depth else cells,
                fixed_rule=r.identity())
