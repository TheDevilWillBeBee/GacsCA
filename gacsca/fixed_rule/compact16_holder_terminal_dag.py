"""Independent complete terminal-memory diagnostic using DAG last writers."""
import numpy as np
from . import compact16_holder_rule as f, compact16_holder_core as c
from . import compact16_holder_projected as r, compact16_holder_program as p
from .wordcode import arithmetic, LIT, MASK


def terminal(parents):
    parents = tuple(parents); n = len(parents); g = p.layout(); desc = p.compiled_description()
    if not 1 <= n <= 64 or any(not isinstance(cell, r.Cell) for cell in parents):
        raise ValueError('bounded complete projected inputs required')
    raw = tuple(f.encode_cell(r.lift(cell)) for cell in parents)
    bank = np.zeros((n, g.memory_count+5), dtype=np.uint64); temp = g.memory_count-6
    for col in range(n):
        values = [value for offset in f.NEIGHBORHOOD for value in raw[(col+offset)%n]]
        for index, (kind, a, b) in enumerate(desc.operations):
            value = a if kind == LIT else arithmetic(kind, values[a], values[b])
            values.append(value); bank[col, g.wires[desc.inputs+index]] = value
        for slot, wire in enumerate(g.gathered_inputs):
            offset, field = wire//f.FIELDS-7, wire%f.FIELDS
            for stage in range(3): bank[col, g.history(stage, offset, field)] = values[wire]
            bank[col, g.votes[slot]] = values[wire]
        for wire in g.regenerated_inputs: bank[col, g.wires[wire]] = values[wire]
        output = [values[wire] for wire in desc.outputs]; address = output[f.COL['address']]
        for offset in f.STATIC_OFFSETS:
            record = r.record((address+offset)%f.Q)
            for name in c.STATIC: output[f.COL[f'p{offset+3}_{name}']] = record[name]
        bank[col, list(g.hold)] = output; bank[col, list(g.info)] = raw[col]
        query = (address+3) & (f.Q-1)
        bank[col, p.MASK_ADDRESS] = MASK
        bank[col, temp:temp+6] = (3, f.Q-1, (~query)&MASK, 0, 0, query)
    committed = bank.copy(); committed[:, list(g.info)] = bank[:, list(g.hold)]
    return dict(precommit_bank=bank, committed_bank=committed,
                signals=bank[:, [g.hold[f.COL['f2']], g.hold[f.COL['f1']]]].copy())
