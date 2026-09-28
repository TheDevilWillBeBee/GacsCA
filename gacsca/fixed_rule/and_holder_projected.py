"""Address-hard-wired projection of the fixed-AND full raw rule.

Static ProgramBit metadata is regenerated from the one own ROM at each address.
No baseline rule or external depth selector supplies evolving transitions.
"""
from dataclasses import make_dataclass, field
import hashlib
import numpy as np
from . import and_holder_rule as f, and_holder_core as c
from . import and_holder_program as p

SCHEMA = f.SCHEMA[len(f.STATIC):]
COL = {name: i for i, (name, _) in enumerate(SCHEMA)}
WIDTH = sum(width for _, width in SCHEMA)
NEIGHBORHOOD = f.NEIGHBORHOOD


def validate(self):
    for name, width in SCHEMA:
        value = getattr(self, name)
        if not isinstance(value, int) or not 0 <= value < 1 << width:
            raise ValueError(f'{name} outside fixed projected holder alphabet')


Cell = make_dataclass('Cell', [(name, int, field(default=0)) for name, _ in SCHEMA],
                      frozen=True,
                      namespace={'__post_init__': validate, '__module__': __name__})


def encode_cell(cell):
    return tuple(getattr(cell, name) for name, _ in SCHEMA)


def decode_cell(words):
    if len(words) != len(SCHEMA):
        raise ValueError('every projected replica/controller word required')
    return Cell(**dict(zip((name for name, _ in SCHEMA), map(int, words))))


def array_from_cells(cells):
    return np.array([encode_cell(cell) for cell in cells], dtype=np.uint64)


def cells_from_array(array):
    return tuple(decode_cell(row.tolist()) for row in array)


def record(address):
    if not 0 <= address < f.Q:
        raise ValueError('canonical physical address required')
    if address < len(p.base_rom()):
        return dict(zip(c.STATIC, map(int, p.base_rom()[address])))
    return {name: c.fallback(address, i) for i, name in enumerate(c.STATIC)}


def lift(cell):
    static = {f'p{offset+3}_{name}': value
              for offset in f.STATIC_OFFSETS
              for name, value in record((cell.address + offset) % f.Q).items()}
    return f.Cell(**static, **{name: getattr(cell, name) for name, _ in SCHEMA})


def project(cell):
    return Cell(**{name: getattr(cell, name) for name, _ in SCHEMA})


def local_step(cells):
    if len(cells) != len(NEIGHBORHOOD):
        raise ValueError('exact radius-seven neighborhood required')
    return project(f.local_step(tuple(lift(cell) for cell in cells)))


def step_ring(cells):
    return tuple(local_step(tuple(cells[(i+j) % len(cells)] for j in NEIGHBORHOOD))
                 for i in range(len(cells)))


def identity():
    return dict(schema=SCHEMA, width=WIDTH, words=len(SCHEMA),
                neighborhood=NEIGHBORHOOD, full_rule=f.identity(),
                ROM_sha256=hashlib.sha256(p.base_rom().tobytes()).hexdigest())
