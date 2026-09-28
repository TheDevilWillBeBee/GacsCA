"""Finite local evaluator with reflecting, configuration-defined colony boundaries.

An experimental successor to machine.py, not a depth-selected kernel. Both the
135-bit historical rule and its archived evidence remain unchanged. This single
138-bit rule supports any number of separated computation regions with repeated
local labels; no global workspace label is required. Neighbor retrieval and
ProgramBit projection are still separate construction obligations.
"""
from dataclasses import dataclass, replace
from functools import lru_cache
from . import machine
from .circuit import Builder

MEM, GATE, LOOP, INERT = machine.MEM, machine.GATE, machine.LOOP, machine.INERT
FETCH, READ_A, READ_B, WRITE = machine.FETCH, machine.READ_A, machine.READ_B, machine.WRITE
RIGHT, LEFT = 0, 1
SCHEMA = machine.SCHEMA + (('first', 1), ('last', 1), ('direction', 1))
WIDTH = sum(width for _, width in SCHEMA)
CONTROL = machine.CONTROL + ('direction',)
NEIGHBORHOOD = (-1, 0, 1)


@dataclass(frozen=True)
class Cell(machine.Cell):
    first: int = 0
    last: int = 0
    direction: int = RIGHT

    def __post_init__(self):
        super().__post_init__()
        for name in ('first', 'last', 'direction'):
            if not isinstance(getattr(self, name), int) or getattr(self, name) not in (0, 1):
                raise ValueError(f'{name} outside fixed alphabet')


def encode_cell(cell):
    return tuple((getattr(cell, name) >> i) & 1 for name, width in SCHEMA for i in range(width))


def decode_cell(bits):
    if len(bits) != WIDTH or any(bit not in (0, 1) for bit in bits):
        raise ValueError('complete binary raw state required')
    values, offset = {}, 0
    for name, width in SCHEMA:
        values[name] = sum(int(bits[offset + j]) << j for j in range(width))
        offset += width
    return Cell(**values)


def local_step(left, center, right):
    """Total radius-one rule, including malformed boundaries and head collisions.

    A rightward head executes the present record, then moves or reflects. A
    leftward head returns without executing records. Reflection stays one tick
    at the endpoint. Collision priority is own reflection > from left > from
    right; this total extension is a design convention, not a repair mechanism.
    """
    control = dict.fromkeys(CONTROL, 0)
    head = 0
    if right.head and right.direction == LEFT and not right.first:
        head = 1
        control = {name: getattr(right, name) for name in CONTROL}
    if left.head and left.direction == RIGHT and not left.last:
        head = 1
        control = dict(machine.advance_token(left), direction=RIGHT)
    if center.head and ((center.direction == RIGHT and center.last) or
                        (center.direction == LEFT and center.first)):
        head = 1
        control = (machine.advance_token(center) if center.direction == RIGHT else
                   {name: getattr(center, name) for name in machine.CONTROL})
        control['direction'] = 1 - center.direction
    bit = center.bit
    if (center.head and center.direction == RIGHT and center.kind == MEM and
            center.phase == WRITE and center.index == center.rd):
        bit = center.value
    return replace(center, bit=bit, head=head, **control)


def step_ring(cells):
    return tuple(local_step(cells[i - 1], cell, cells[(i + 1) % len(cells)])
                 for i, cell in enumerate(cells))


@lru_cache(maxsize=1)
def self_description():
    """NAND description of every raw field, including reflection and collisions."""
    b = Builder(3 * WIDTH)
    records, offset = [], 2
    for _ in range(3):
        record = {}
        for name, width in SCHEMA:
            record[name] = tuple(range(offset, offset + width))
            offset += width
        records.append(record)
    left, center, right = records

    def eq(record, name, value):
        return b.eq(record[name], b.const(value, len(record[name])))

    def condition(record, phase, field):
        return b.both(b.both(eq(record, 'kind', MEM), eq(record, 'phase', phase)),
                      b.eq(record['index'], record[field]))

    def advance(record):
        fetch = b.both(eq(record, 'phase', FETCH), b.eq(record['index'], record['pc']))
        gate = b.both(fetch, eq(record, 'kind', GATE))
        loop = b.both(fetch, eq(record, 'kind', LOOP))
        a, c, d = (condition(record, phase, field) for phase, field in
                   ((READ_A, 'ra'), (READ_B, 'rb'), (WRITE, 'rd')))
        result = {name: record[name] for name in machine.CONTROL}
        for name, source in (('ra', 'a'), ('rb', 'b'), ('rd', 'd')):
            result[name] = b.select(gate, record[source], record[name])
        phase = record['phase']
        for predicate, value in ((gate, READ_A), (a, READ_B), (c, WRITE), (d, FETCH)):
            phase = b.select(predicate, b.const(value, 2), phase)
        result['phase'] = phase
        result['pc'] = b.select(loop, b.const(0, 16),
                                b.select(d, b.increment(record['pc']), record['pc']))
        result['value'] = (b.mux(c, b.nand(record['value'][0], record['bit'][0]),
                                 b.mux(a, record['bit'][0], record['value'][0])),)
        return result

    from_left = b.both(left['head'][0], b.both(b.inv(left['direction'][0]), b.inv(left['last'][0])))
    from_right = b.both(right['head'][0], b.both(right['direction'][0], b.inv(right['first'][0])))
    reflect = b.both(center['head'][0], b.mux(center['direction'][0], center['first'][0], center['last'][0]))
    left_control, center_control = advance(left), advance(center)
    out = dict(center)
    out['head'] = (b.either(reflect, b.either(from_left, from_right)),)
    for name in machine.CONTROL:
        value = b.select(from_right, right[name], b.const(0, len(right[name])))
        value = b.select(from_left, left_control[name], value)
        own = b.select(center['direction'][0], center[name], center_control[name])
        out[name] = b.select(reflect, own, value)
    out['direction'] = (b.mux(reflect, b.inv(center['direction'][0]),
                              b.both(b.inv(from_left), from_right)),)
    write = b.both(center['head'][0], b.both(b.inv(center['direction'][0]),
                                           condition(center, WRITE, 'rd')))
    out['bit'] = (b.mux(write, center['value'][0], center['bit'][0]),)
    return b.finish([wire for name, _ in SCHEMA for wire in out[name]])


def identity():
    return {'schema': SCHEMA, 'width': WIDTH, 'neighborhood': NEIGHBORHOOD,
            'description_sha256': self_description().digest()}
