"""Experimental fixed ROM reducing repeated-operand controller scans.

NAND(x,x) becomes NAND(MASK,x), with MASK in reserved low MEM Address 6.
The existing physical transition/alphabet is unchanged. The new projected
hard-wiring is a separate candidate, fixed independently of hierarchy depth.
"""
from dataclasses import replace
from functools import lru_cache
import numpy as np
from . import retimed_holder_program as reference
from . import retimed_holder_core as c, retimed_holder_rule as f
from .wordcode import NAND, LIT, MASK
from .word_program import Instruction

MASK_ADDRESS = 6
compiled_description = reference.compiled_description


def accessed_addresses(op):
    if op.kind in c.ALU_KINDS:
        return (op.a, op.b, op.d)
    if op.kind == LIT:
        return (op.d,)
    if op.kind == c.SEND:
        return (op.a, op.b)
    if op.kind == c.LOAD:
        return (op.a,)
    if op.kind == c.META:
        return (op.a,)
    return ()


@lru_cache(maxsize=1)
def layout():
    old = reference.layout()
    assert MASK_ADDRESS < reference.RESERVED
    assert all(MASK_ADDRESS not in accessed_addresses(op) for op in old.instructions)
    start = old.description_instruction
    assert old.stage_ranges[4][0] == old.delivery_range[0] == start
    instructions = []
    for pc, op in enumerate(old.instructions):
        if pc == start:
            instructions.append(Instruction(LIT, MASK, 0, MASK_ADDRESS))
        # Input metadata normalization precedes this initialization and must
        # retain its original operands. Both evaluator entries execute the LIT.
        if pc >= start and op.kind == NAND and op.a == op.b:
            assert op.a > MASK_ADDRESS
            op = replace(op, a=MASK_ADDRESS, b=op.a)
        instructions.append(op)
    shift_end = lambda index: index + int(index > start)
    result = replace(old, instructions=tuple(instructions),
                     stage_ranges=tuple((shift_end(a), shift_end(b))
                                        for a, b in old.stage_ranges),
                     delivery_range=tuple(shift_end(i) for i in old.delivery_range),
                     description_instruction=start + 1)
    assert result.computation_cells + 5 <= f.Q
    return result


@lru_cache(maxsize=1)
def base_rom():
    g = layout()
    # MEM layout, reset masks, Info, histories, temporaries and entry PCs stay
    # the same. Only instruction addresses and the last-cell position move.
    rows = reference.base_rom()[:g.memory_count].tolist()
    rows.extend([op.kind, pc, op.a, op.b, op.d, 0, 0]
                for pc, op in enumerate(g.instructions))
    rows.append([c.LOOP, len(g.instructions), 0, 0, 0, 0, 1])
    out = np.array(rows, dtype=np.uint64)
    out.flags.writeable = False
    return out
