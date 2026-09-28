"""Depth appears only in this lazy host initializer, never in the fixed rule."""
from dataclasses import replace
from functools import lru_cache
from . import windowed as rule,window_rule as full,window_program as program


@lru_cache(maxsize=1)
def template():
    array=rule.project_array(program.template());array.flags.writeable=False
    return array


def physical_cells(top_cells,depth):
    if not isinstance(depth,int) or depth<0 or top_cells<1:
        raise ValueError('positive top size and nonnegative depth required')
    return top_cells*program.layout().colony_cells**depth


def cell_at(top,depth,position):
    top=tuple(top);position%=physical_cells(len(top),depth)
    g=program.layout();stack=[]
    while depth:
        parent,address=divmod(position,g.colony_cells)
        if address>=g.computation_cells:
            cell=rule.Cell(address=address);break
        cell=rule.cells_from_array(template()[address:address+1])[0]
        if not g.info_start<=address<g.info_start+full.WIDTH:break
        stack.append((cell,address-g.info_start));depth-=1;position=parent
    else:cell=top[position]
    while stack:
        shell,bit=stack.pop();cell=replace(shell,bit=full.encode_cell(rule.lift(cell))[bit])
    return cell


def decode_parent(top,depth,position):
    if depth<1:raise ValueError('at least one encoding level required')
    g=program.layout()
    word=tuple(cell_at(top,depth,position*g.colony_cells+g.info_start+i).bit for i in range(full.WIDTH))
    lifted=full.decode_cell(word);raw=rule.project(lifted)
    if rule.lift(raw)!=lifted:raise ValueError('inconsistent represented program')
    return raw


def resource_estimate(top_cells,depth):
    g=program.layout();sites=physical_cells(top_cells,depth)
    return dict(depth=depth,physical_cells=sites,physical_state_bits=sites*rule.WIDTH,
                dense_uint32_bytes=sites*len(rule.SCHEMA)*4,ticks_per_top_transition=g.period_ticks**depth,
                lowest_level_core_cells=(sites//g.colony_cells)*g.computation_cells if depth else sites,
                fixed_rule=rule.identity())
