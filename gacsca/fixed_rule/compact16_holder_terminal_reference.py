"""Diagnostic replay of the complete terminal bank; never physical evolution."""
from functools import lru_cache
import numpy as np
from . import compact16_holder_rule as f, compact16_holder_core as c
from . import compact16_holder_projected as r, compact16_holder_program as p
from .wordcode import LIT, arithmetic


@lru_cache(None)
def metadata():
    return tuple(tuple(r.record(a)[name] for name in c.STATIC) for a in range(f.Q))


def terminal(parents):
    parents = tuple(parents); n = len(parents); g = p.layout()
    if not 1 <= n <= 64 or any(not isinstance(cell, r.Cell) for cell in parents):
        raise ValueError('bounded complete projected inputs required')
    raw = tuple(f.encode_cell(r.lift(cell)) for cell in parents)
    bank = np.zeros((n, g.memory_count+5), dtype=np.uint64)
    for col in range(n):
        memory = [0]*(g.memory_count+5)
        for slot, wire in enumerate(g.gathered_inputs):
            offset, field = wire//f.FIELDS-7, wire%f.FIELDS
            value = raw[(col+offset)%n][field]
            for stage in range(3): memory[g.history(stage, offset, field)] = value
            memory[g.votes[slot]] = value
        for at, value in zip(g.info, raw[col]): memory[at] = value
        loaded = None; start, end = g.stage_ranges[4]
        for index in range(start, end):
            op = g.instructions[index]
            if op.kind == LIT: memory[op.d] = op.a
            elif op.kind in c.ALU_KINDS: memory[op.d] = arithmetic(op.kind, memory[op.a], memory[op.b])
            elif op.kind == c.LOAD: loaded = memory[op.a]
            elif op.kind == c.META:
                assert loaded is not None and 0 <= loaded < f.Q and 0 <= op.b < len(c.STATIC)
                memory[op.a] = metadata()[loaded][op.b]
            else: assert op.kind == c.IF_THIRD and index == end-1
        bank[col] = memory
    committed = bank.copy(); committed[:, list(g.info)] = bank[:, list(g.hold)]
    signals = bank[:, [g.hold[f.COL['f2']], g.hold[f.COL['f1']]]].copy()
    assert np.all(signals <= 1)
    return dict(precommit_bank=bank, committed_bank=committed, signals=signals)
