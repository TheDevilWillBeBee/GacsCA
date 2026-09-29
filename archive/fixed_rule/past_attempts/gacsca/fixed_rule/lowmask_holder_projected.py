"""One fixed experimental ProgramBit projection using the low-mask ROM."""
import hashlib
from . import retimed_holder_rule as f, retimed_holder_core as c
from . import lowmask_holder_program as p
from .retimed_holder_projected import Cell, SCHEMA, COL, WIDTH, NEIGHBORHOOD
from .retimed_holder_projected import encode_cell, decode_cell, array_from_cells, cells_from_array, project


def record(address):
    if address < len(p.base_rom()):
        return dict(zip(c.STATIC, map(int, p.base_rom()[address])))
    return {name: c.fallback(address, i) for i, name in enumerate(c.STATIC)}


def lift(cell):
    static = {f'p{offset+3}_{name}': value for offset in f.STATIC_OFFSETS
              for name, value in record((cell.address + offset) % f.Q).items()}
    return f.Cell(**static, **{name: getattr(cell, name) for name, _ in SCHEMA})


def local_step(cells):
    return project(f.local_step(tuple(lift(cell) for cell in cells)))


def identity():
    return dict(schema=SCHEMA, width=WIDTH, words=len(SCHEMA),
                neighborhood=NEIGHBORHOOD, full_rule=f.identity(),
                ROM_sha256=hashlib.sha256(p.base_rom().tobytes()).hexdigest())
