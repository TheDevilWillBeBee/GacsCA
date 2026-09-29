"""Finite encoded-depth initializer; never an evolution backend."""
from functools import lru_cache
from . import retimed_holder_rule as f, sparse_holder_program as p
from . import sparse_holder_projected as r
from .retimed_holder_initial import physical_cells, coherent_cell


@lru_cache(maxsize=1)
def info_positions():
    return {address: i for i, address in enumerate(p.layout().info)}


def cell_at(top, depth, position):
    if type(position) is not int:
        raise ValueError('integral physical position required')
    size = physical_cells(len(top), depth)
    position %= size
    if depth == 0:
        return top[position]
    values, parents = {'address': position % f.Q}, {}
    info = info_positions()
    for offset in f.OFFSETS:
        parent, address = divmod((position + offset) % size, f.Q)
        if address in info:
            if parent not in parents:
                parents[parent] = f.encode_cell(r.lift(cell_at(top, depth - 1, parent)))
            values[f's{offset+2}_data'] = parents[parent][info[address]]
    return r.Cell(**values)


def decode_parent(top, depth, position):
    if depth < 1:
        raise ValueError('positive encoded depth required')
    raw = f.decode_cell(tuple(cell_at(top, depth, position * f.Q + a).s2_data
                              for a in p.layout().info))
    result = r.project(raw)
    if r.lift(result) != raw:
        raise ValueError('all seven metadata records must match own fixed ROM')
    return result
