"""Lazy initialization E_G^depth for the single constant-ROM physical rule.

No evolution is implemented here. The encoded word is the complete 194-bit lift;
returned physical cells always use the same 125-bit regenerated schema.
"""
from dataclasses import replace
from functools import lru_cache
from . import regenerated as rule,regenerative,regenerative_block


@lru_cache(maxsize=1)
def template():
    array=rule.project_array(regenerative_block.template())
    array.flags.writeable=False
    return array


def physical_cells(top_cells,depth):
    if not isinstance(depth,int) or depth<0 or top_cells<1:
        raise ValueError('positive top size and nonnegative integral depth required')
    return top_cells*regenerative_block.layout().colony_cells**depth


def cell_at(top,depth,position):
    top=tuple(top)
    size=physical_cells(len(top),depth)
    if not isinstance(position,int):
        raise ValueError('integral position required')
    position%=size
    g=regenerative_block.layout()
    stack=[]
    while depth:
        parent,address=divmod(position,g.colony_cells)
        cell=rule.cells_from_array(template()[address:address+1])[0]
        if not g.info_start<=address<g.info_start+regenerative.WIDTH:
            break
        stack.append((cell,address-g.info_start))
        depth-=1
        position=parent
    else:
        cell=top[position]
    while stack:
        shell,bit=stack.pop()
        cell=replace(shell,bit=regenerative.encode_cell(rule.lift(cell))[bit])
    return cell


def decode_parent(top,depth,position):
    if depth<1:
        raise ValueError('at least one encoding level required')
    g=regenerative_block.layout()
    word=tuple(cell_at(top,depth,position*g.colony_cells+g.info_start+i).bit
               for i in range(regenerative.WIDTH))
    lifted=regenerative.decode_cell(word)
    raw=rule.project(lifted)
    if rule.lift(raw)!=lifted:
        raise ValueError('inconsistent encoded static program')
    return raw


def resource_estimate(top_cells,depth):
    sites=physical_cells(top_cells,depth)
    return dict(depth=depth,physical_cells=sites,physical_state_bits=sites*rule.WIDTH,
                dense_uint32_bytes=sites*len(rule.SCHEMA)*4,
                ticks_per_top_transition=regenerative_block.layout().period_ticks**depth,
                fixed_rule=rule.identity())
