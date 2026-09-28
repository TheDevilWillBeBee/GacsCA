"""Fixed dependency-directed self-ROM, retaining complete encoded raw states.

Only used neighbor operands get three history slots and a vote slot. Own ROM
metadata is regenerated from the voted Address before each full evaluation.
Info and Hold still contain every raw field, including every controller copy.
"""
from dataclasses import dataclass
from functools import lru_cache
import numpy as np
from . import compact16_holder_rule as f, compact16_holder_core as c
from . import compact16_holder_layout as reference
from .word_allocation import allocate
from .word_program import Instruction
from .wordcode import LIT, ADD, NAND, EQ, MASK

RESERVED = 8
MASK_ADDRESS = 6
RESULT_CAPACITY = 320  # Fixed construction choice, never a depth input.
HISTORY_OFFSETS = (0, 2, 3)
compiled_description = reference.compiled_description


def dependencies(description):
    used = {wire for op, a, b in description.operations if op != LIT
            for wire in (a, b) if wire < description.inputs}
    used.update(wire for wire in description.outputs if wire < description.inputs)
    return tuple(sorted(used))


@dataclass(frozen=True)
class Layout(reference.Layout):
    required_inputs: tuple
    gathered_inputs: tuple
    regenerated_inputs: tuple

    def history(self, stage, neighbor, field):
        if stage not in range(3):
            raise ValueError('three gathering stages required')
        wire = (neighbor + 7) * f.FIELDS + field
        try:
            slot = self.gathered_inputs.index(wire)
        except ValueError as error:
            raise KeyError('input has no gathered history') from error
        return RESERVED + 4 * slot + HISTORY_OFFSETS[stage]


@lru_cache(maxsize=1)
def layout():
    desc = compiled_description()
    required = dependencies(desc)
    static = tuple(w for w in required if w % f.FIELDS < len(f.STATIC))
    assert all(w // f.FIELDS == 7 for w in static)
    gathered = tuple(w for w in required if w not in set(static))
    ranks = {wire: slot for slot, wire in enumerate(gathered)}
    votes = tuple(RESERVED + 4 * slot + 1 for slot in range(len(gathered)))
    info_start = RESERVED + 4 * len(gathered)
    info = tuple(info_start + 2 * i for i in range(f.FIELDS))
    hold = tuple(at + 1 for at in info)
    static_start = info_start + 2 * f.FIELDS
    operands = [None] * desc.inputs
    for wire, address in zip(gathered, votes):
        operands[wire] = address
    for slot, wire in enumerate(static):
        operands[wire] = static_start + slot
    zero_wire = next(desc.inputs + i for i, (op, a, _) in enumerate(desc.operations)
                     if op == LIT and a == 0)
    allocation = allocate(desc, pins=(zero_wire,), capacity=RESULT_CAPACITY)
    scratch_start = static_start + len(static)
    wires = tuple(operands) + tuple(scratch_start + slot for slot in allocation.slots)
    temp = scratch_start + allocation.count
    query, memory = temp + 5, temp + 6
    instructions, entries, ranges = [], [], []

    def emit(kind, a, b, d, *, low_mask=False):
        if kind in c.ALU_KINDS:
            assert a is not None and b is not None
            if low_mask and kind == NAND and a == b:
                a, b = MASK_ADDRESS, a
            if kind in (NAND, ADD, EQ) and a > b:
                a, b = b, a
        instructions.append(Instruction(kind, a, b, d))

    def regenerate(targets):
        for offset in f.STATIC_OFFSETS:
            source = targets[f.COL['address']]
            if offset:
                emit(LIT, offset & MASK, 0, temp)
                emit(ADD, source, temp, query)
                emit(LIT, f.Q - 1, 0, temp + 1)
                emit(NAND, query, temp + 1, temp + 2)
                emit(NAND, temp + 2, temp + 2, query, low_mask=True)
                source = query
            else:
                # Address retains 15 raw bits while Q has 14. Fold the
                # zero-offset query too, matching the projected lift.
                emit(LIT, f.Q - 1, 0, temp + 1)
                emit(NAND, source, temp + 1, temp + 2)
                emit(NAND, temp + 2, temp + 2, query, low_mask=True)
                source = query
            for selector, name in enumerate(c.STATIC):
                emit(c.LOAD, source, 0, 0)
                emit(c.META, targets[f.COL[f'p{offset+3}_{name}']], selector, 0)

    for stage in range(3):
        start = len(instructions)
        entries.append(start)
        emit(LIT, 0, 0, temp)
        for field, source in enumerate(info):
            wire = 7 * f.FIELDS + field
            if wire in ranks:
                target = RESERVED + 4 * ranks[wire] + HISTORY_OFFSETS[stage]
                emit(ADD, source, temp, target)
        for hops in range(1, 8):
            for field, source in enumerate(info):
                for direction, neighbor in ((c.LEFT, hops), (c.RIGHT, -hops)):
                    wire = (7 + neighbor) * f.FIELDS + field
                    if wire in ranks:
                        target = RESERVED + 4 * ranks[wire] + HISTORY_OFFSETS[stage]
                        emit(c.SEND, source, target, (hops << 1) | direction)
        emit(c.HALT, 0, 0, 0)
        ranges.append((start, len(instructions)))
    entries.append(len(instructions))
    emit(c.HALT, 0, 0, 0)
    ranges.append((entries[3], len(instructions)))
    start = len(instructions)
    entries.append(start)
    emit(LIT, MASK, 0, MASK_ADDRESS)
    regenerate(operands[7*f.FIELDS:8*f.FIELDS])
    description_instruction = len(instructions)
    for i, (kind, a, b) in enumerate(desc.operations):
        left, right = (a, 0) if kind == LIT else (wires[a], wires[b])
        emit(kind, left, right, wires[desc.inputs+i], low_mask=True)
    for field, (target, output) in enumerate(zip(hold, desc.outputs)):
        # Static outputs are overwritten by own-ROM regeneration below. All
        # mutable raw outputs, including every controller copy, are retained.
        if field >= len(f.STATIC):
            emit(ADD, wires[output], wires[zero_wire], target)
    regenerate(hold)
    emit(c.IF_THIRD, 0, 0, 0)
    ranges.append((start, len(instructions)))
    for target in range(1, 6):
        emit(c.SEND, hold[f.COL['f2']], target, c.LEFT)
    for target in range(f.Q-5, f.Q):
        emit(c.SEND, hold[f.COL['f1']], target, c.RIGHT)
    emit(c.HALT, 0, 0, 0)
    result = Layout(memory, tuple(instructions), tuple(entries), info, hold, votes,
                    wires, tuple(ranges), desc.digest(), (start, len(instructions)),
                    description_instruction, required, gathered, static)
    assert result.computation_cells + 5 <= f.Q
    return result


@lru_cache(maxsize=1)
def base_rom():
    g = layout()
    rows = [[c.MEM, address, 31, 0, 0, int(address == 0), 0]
            for address in range(g.memory_count)]
    for slot, vote in enumerate(g.votes):
        base = RESERVED + 4 * slot
        for stage, offset in enumerate(HISTORY_OFFSETS):
            rows[base + offset][2] = (1 << (stage+1)) - 1
        rows[vote][2] = 31 | c.VOTE
    for address in g.info:
        rows[address][2] = c.INFO
    rows[0][2:5] = [g.entries[0] | g.entries[1] << 32,
                    g.entries[2] | g.entries[3] << 32, g.entries[4]]
    rows.extend([op.kind, pc, op.a, op.b, op.d, 0, 0]
                for pc, op in enumerate(g.instructions))
    rows.append([c.LOOP, len(g.instructions), 0, 0, 0, 0, 1])
    out = np.array(rows, dtype=np.uint64)
    out.flags.writeable = False
    return out
