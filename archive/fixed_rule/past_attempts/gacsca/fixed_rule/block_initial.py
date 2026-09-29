"""Depth is initial data: lazy access to E^depth of a finite top ring.

This module never evolves a state. It permits inspection of depth-two/three
initializations without allocating their full physical arrays. It is not evidence
of deeper physical execution or an alternative transition kernel.
"""
from dataclasses import replace
from . import block, communicating as rule
from .communicating_native import cells_from_array


def physical_cells(top_cells, depth):
    if not isinstance(depth, int) or depth < 0 or top_cells < 1:
        raise ValueError('positive top size and nonnegative integral depth required')
    return top_cells * block.layout().colony_cells ** depth


def cell_at(top, depth, position):
    """Exact raw cell of the recursively block-encoded initial configuration.

    Explicit stack avoids a host recursion-depth ceiling. Workspace addresses in
    every returned physical cell remain 16-bit; only the host's initial position
    and requested configuration length grow. No simulated transitions are run.
    """
    top = tuple(top)
    size = physical_cells(len(top), depth)
    if not isinstance(position, int):
        raise ValueError('integral position required')
    position %= size
    geometry = block.layout()
    stack = []
    while depth:
        parent, address = divmod(position, geometry.colony_cells)
        cell = cells_from_array(block.template()[address:address+1])[0]
        if not geometry.info_start <= address < geometry.info_start + rule.WIDTH:
            break
        stack.append((cell, address - geometry.info_start))
        depth -= 1
        position = parent
    else:
        cell = top[position]
    while stack:
        shell, selected_bit = stack.pop()
        cell = replace(shell, bit=rule.encode_cell(cell)[selected_bit])
    return cell


def decode_parent(top, depth, parent_position):
    if depth < 1:
        raise ValueError('at least one encoding level required')
    g = block.layout()
    return rule.decode_cell(tuple(cell_at(top, depth, parent_position*g.colony_cells+g.info_start+i).bit
                                  for i in range(rule.WIDTH)))


def resource_estimate(top_cells, depth):
    """Exact dense storage and literal time counts, not a feasible-runtime claim."""
    sites = physical_cells(top_cells, depth)
    return dict(depth=depth, physical_cells=sites, physical_state_bits=sites*rule.WIDTH,
                dense_uint32_bytes=sites*len(rule.SCHEMA)*4,
                ticks_per_top_transition=block.layout().period_ticks**depth,
                fixed_rule=rule.identity())
