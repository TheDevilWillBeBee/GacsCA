"""One finite radius-one tape CA, with a NAND description of its entire rule.

No depth parameter, program callback, or host interpreter in local_step. A valid
single-head ring is a convenient invariant subset; local_step is total on the
entire 135-bit alphabet, including malformed/multiple-head configurations.
"""
from dataclasses import dataclass, fields, replace
from functools import lru_cache
from .circuit import Builder

WORD = 16
MASK = (1 << WORD) - 1
MEM, GATE, LOOP, INERT = range(4)
FETCH, READ_A, READ_B, WRITE = range(4)
SCHEMA = (('kind', 2), ('index', WORD), ('a', WORD), ('b', WORD),
          ('d', WORD), ('bit', 1), ('head', 1), ('phase', 2),
          ('pc', WORD), ('ra', WORD), ('rb', WORD), ('rd', WORD), ('value', 1))
WIDTH = sum(w for _, w in SCHEMA)
CONTROL = ('phase', 'pc', 'ra', 'rb', 'rd', 'value')
NEIGHBORHOOD = (-1, 0)  # contained in radius one; no hidden tape/global reads


@dataclass(frozen=True)
class Cell:
    kind: int = INERT
    index: int = 0
    a: int = 0
    b: int = 0
    d: int = 0
    bit: int = 0
    head: int = 0
    phase: int = FETCH
    pc: int = 0
    ra: int = 0
    rb: int = 0
    rd: int = 0
    value: int = 0

    def __post_init__(self):
        for name, width in SCHEMA:
            if not isinstance(getattr(self, name), int) or not 0 <= getattr(self, name) < 1 << width:
                raise ValueError(f'{name} outside fixed alphabet')


def encode_cell(cell):
    return tuple((getattr(cell, name) >> i) & 1 for name, width in SCHEMA for i in range(width))


def decode_cell(bits):
    if len(bits) != WIDTH or any(b not in (0, 1) for b in bits):
        raise ValueError('raw cell encoding must include every binary field')
    values, offset = {}, 0
    for name, width in SCHEMA:
        values[name] = sum(int(bits[offset + i]) << i for i in range(width))
        offset += width
    return Cell(**values)


def advance_token(cell):
    """Controller after processing only its present site; independent scalar spec."""
    out = {name: getattr(cell, name) for name in CONTROL}
    if cell.phase == FETCH:
        if cell.index == cell.pc:
            if cell.kind == GATE:
                out.update(phase=READ_A, ra=cell.a, rb=cell.b, rd=cell.d)
            elif cell.kind == LOOP:
                out['pc'] = 0
    elif cell.kind == MEM:
        if cell.phase == READ_A and cell.index == cell.ra:
            out.update(value=cell.bit, phase=READ_B)
        elif cell.phase == READ_B and cell.index == cell.rb:
            out.update(value=1 - (cell.value & cell.bit), phase=WRITE)
        elif cell.phase == WRITE and cell.index == cell.rd:
            out.update(pc=(cell.pc + 1) & MASK, phase=FETCH)
    return out


def local_step(left, center):
    bit = center.bit
    if center.head and center.kind == MEM and center.phase == WRITE and center.index == center.rd:
        bit = center.value
    control = advance_token(left) if left.head else dict.fromkeys(CONTROL, 0)
    return replace(center, bit=bit, head=left.head, **control)


def step_ring(cells):
    return tuple(local_step(cells[i - 1], cell) for i, cell in enumerate(cells))


@lru_cache(maxsize=1)
def self_description():
    """Explicit finite NAND circuit for local_step, including evaluator registers.

    No opcode meaning 'run Python', 'evaluate self', or depth dispatch occurs.
    The output contains every raw field. Identity outputs remain explicit wires.
    """
    b = Builder(2 * WIDTH)
    neighbors = []
    for k in range(2):
        offset, record = 2 + k * WIDTH, {}
        for name, width in SCHEMA:
            record[name] = tuple(range(offset, offset + width))
            offset += width
        neighbors.append(record)
    left, center = neighbors

    def eq(record, name, value):
        return b.eq(record[name], b.const(value, len(record[name])))

    def condition(record, phase, field):
        return b.both(b.both(eq(record, 'kind', MEM), eq(record, 'phase', phase)),
                      b.eq(record['index'], record[field]))

    fetch = b.both(eq(left, 'phase', FETCH), b.eq(left['index'], left['pc']))
    gate = b.both(fetch, eq(left, 'kind', GATE))
    loop = b.both(fetch, eq(left, 'kind', LOOP))
    a, c, d = (condition(left, phase, field) for phase, field in
               ((READ_A, 'ra'), (READ_B, 'rb'), (WRITE, 'rd')))
    control = {name: left[name] for name in CONTROL}
    for name, source in (('ra', 'a'), ('rb', 'b'), ('rd', 'd')):
        control[name] = b.select(gate, left[source], left[name])
    phase = left['phase']
    for predicate, value in ((gate, READ_A), (a, READ_B), (c, WRITE), (d, FETCH)):
        phase = b.select(predicate, b.const(value, 2), phase)
    control['phase'] = phase
    control['pc'] = b.select(loop, b.const(0, WORD), b.select(d, b.increment(left['pc']), left['pc']))
    control['value'] = (b.mux(c, b.nand(left['value'][0], left['bit'][0]),
                             b.mux(a, left['bit'][0], left['value'][0])),)
    out = dict(center)
    out['bit'] = (b.mux(b.both(center['head'][0], condition(center, WRITE, 'rd')),
                         center['value'][0], center['bit'][0]),)
    out['head'] = left['head']
    for name in CONTROL:
        out[name] = b.select(left['head'][0], control[name], b.const(0, len(control[name])))
    return b.finish([wire for name, _ in SCHEMA for wire in out[name]])


def identity():
    return {'schema': SCHEMA, 'width': WIDTH, 'neighborhood': NEIGHBORHOOD,
            'description_sha256': self_description().digest()}
