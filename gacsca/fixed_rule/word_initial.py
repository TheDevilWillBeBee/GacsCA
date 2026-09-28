"""Lazy fixed-rule encodings and a same-rule periodic terminal configuration."""
from dataclasses import dataclass,replace
from functools import lru_cache
from . import word_rule as f,word_projected as r,word_program as p


@dataclass(frozen=True)
class TerminalOrbit:
    """Initial data: no heads or mail; canonical Address and a uniform Age.

    The same physical rule advances the uniform Age. This is a periodic terminal
    orbit, not a fixed-point claim or a separate top-level transition kernel.
    """
    payload:int=0
    age:int=0
    def __post_init__(self):r.Cell(data=self.payload,age=self.age)
    def __len__(self):return f.Q
    def __getitem__(self,index):
        if not isinstance(index,int) or not 0<=index<f.Q:raise IndexError(index)
        return r.Cell(data=self.payload,age=self.age,address=index)


@lru_cache(maxsize=1)
def template():
    a=r.project_array(p.template());a.flags.writeable=False;return a


def physical_cells(top_cells,depth):
    if not isinstance(depth,int) or depth<0 or top_cells<1:raise ValueError('invalid finite encoding size')
    return top_cells*f.Q**depth


def cell_at(top,depth,position):
    if not isinstance(position,int):raise ValueError('integral position required')
    position%=physical_cells(len(top),depth);g=p.layout();stack=[]
    while depth:
        parent,address=divmod(position,f.Q)
        if address>=g.computation_cells:cell=r.Cell(address=address);break
        cell=r.cells_from_array(template()[address:address+1])[0]
        if not g.info_start<=address<g.info_start+f.FIELDS:break
        stack.append((cell,address-g.info_start));depth-=1;position=parent
    else:cell=top[position]
    while stack:
        shell,word=stack.pop();cell=replace(shell,data=f.encode_cell(r.lift(cell))[word])
    return cell


def decode_parent(top,depth,position):
    if depth<1:raise ValueError('positive encoded depth required')
    g=p.layout();words=tuple(cell_at(top,depth,position*f.Q+g.info_start+i).data for i in range(f.FIELDS))
    full=f.decode_cell(words);raw=r.project(full)
    if r.lift(raw)!=full:raise ValueError('inconsistent projected record')
    return raw


def resources(top_cells,depth):
    sites=physical_cells(top_cells,depth);g=p.layout()
    return dict(depth=depth,physical_cells=sites,raw_physical_bits=sites*r.WIDTH,
                dense_uint64_bytes=sites*len(r.SCHEMA)*8,ticks_per_top_step=g.period_ticks**depth,
                lowest_level_core_cells=(sites//f.Q)*g.computation_cells if depth else sites,
                fixed_rule=r.identity())
