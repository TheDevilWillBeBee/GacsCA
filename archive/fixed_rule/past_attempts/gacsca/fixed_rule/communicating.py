"""Fixed 177-bit local evaluator with addressed neighbor packets.

This candidate adds SEND and two one-site-per-tick packet tracks to the confined
rule. Its entire controller/packet transition has an explicit NAND description.
It is a noiseless computing substrate, not yet Gray maintenance or projection.
"""
from dataclasses import dataclass, replace
from functools import lru_cache
from .circuit import Builder

MEM, GATE, LOOP, SEND = range(4)
FETCH, READ_A, READ_B, WRITE, TRANSMIT = range(5)
RIGHT, LEFT = 0, 1
SCHEMA = (('kind', 2), ('index', 16), ('a', 16), ('b', 16), ('d', 16),
          ('bit', 1), ('head', 1), ('phase', 3), ('pc', 16), ('ra', 16),
          ('rb', 16), ('rd', 16), ('value', 1), ('first', 1), ('last', 1),
          ('direction', 1), ('lp_target', 16), ('lp_bit', 1), ('lp_cross', 1),
          ('lp_valid', 1), ('rp_target', 16), ('rp_bit', 1), ('rp_cross', 1), ('rp_valid', 1))
WIDTH = sum(width for _, width in SCHEMA)
CONTROL = ('phase', 'pc', 'ra', 'rb', 'rd', 'value', 'direction')
NEIGHBORHOOD = (-1, 0, 1)


@dataclass(frozen=True)
class Cell:
    kind: int = MEM
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
    first: int = 0
    last: int = 0
    direction: int = RIGHT
    lp_target: int = 0
    lp_bit: int = 0
    lp_cross: int = 0
    lp_valid: int = 0
    rp_target: int = 0
    rp_bit: int = 0
    rp_cross: int = 0
    rp_valid: int = 0

    def __post_init__(self):
        for name, width in SCHEMA:
            if not isinstance(getattr(self, name), int) or not 0 <= getattr(self, name) < 1 << width:
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


def advance(cell):
    out = {name: getattr(cell, name) for name in CONTROL if name != 'direction'}
    if cell.phase == FETCH and cell.index == cell.pc:
        if cell.kind in (GATE, SEND):
            out.update(phase=READ_A if cell.kind == GATE else TRANSMIT,
                       ra=cell.a, rb=cell.b, rd=cell.d)
        elif cell.kind == LOOP:
            out['pc'] = 0
    elif cell.kind == MEM:
        if cell.phase == READ_A and cell.index == cell.ra:
            out.update(value=cell.bit, phase=READ_B)
        elif cell.phase == READ_B and cell.index == cell.rb:
            out.update(value=1 - (cell.value & cell.bit), phase=WRITE)
        elif ((cell.phase == WRITE and cell.index == cell.rd) or
              (cell.phase == TRANSMIT and cell.index == cell.ra)):
            out.update(phase=FETCH, pc=(cell.pc + 1) & 65535)
    return out


def receive(source, center, channel, boundary):
    """Incoming packet advances exactly one site; at most one boundary crossing."""
    target = getattr(source, channel + '_target')
    bit = getattr(source, channel + '_bit')
    crossed = getattr(source, channel + '_cross')
    valid = getattr(source, channel + '_valid') and not (crossed and boundary)
    crossed = int(bool(crossed or boundary))
    delivered = bool(valid and crossed and center.kind == MEM and center.index == target)
    moving = bool(valid and not delivered)
    packet = dict(zip((channel + '_' + n for n in ('target', 'bit', 'cross', 'valid')),
                      (target, bit, crossed, 1) if moving else (0, 0, 0, 0)))
    return packet, delivered, bit


def local_step(left, center, right):
    control, head = dict.fromkeys(CONTROL, 0), 0
    if right.head and right.direction == LEFT and not right.first:
        head, control = 1, {name: getattr(right, name) for name in CONTROL}
    if left.head and left.direction == RIGHT and not left.last:
        head, control = 1, dict(advance(left), direction=RIGHT)
    if center.head and ((center.direction == RIGHT and center.last) or
                        (center.direction == LEFT and center.first)):
        head = 1
        control = (advance(center) if center.direction == RIGHT else
                   {name: getattr(center, name) for name in CONTROL if name != 'direction'})
        control['direction'] = 1 - center.direction
    lp, hit_l, bit_l = receive(right, center, 'lp', right.first)
    rp, hit_r, bit_r = receive(left, center, 'rp', left.last)
    bit = bit_r if hit_r else bit_l if hit_l else center.bit
    if center.head and center.direction == RIGHT and center.kind == MEM:
        if center.phase == WRITE and center.index == center.rd:
            bit = center.value
        if center.phase == TRANSMIT and center.index == center.ra:
            channel, packet = ('lp', lp) if center.rd & 1 else ('rp', rp)
            packet.update({channel + '_target': center.rb, channel + '_bit': center.bit,
                           channel + '_cross': 0, channel + '_valid': 1})
    return replace(center, bit=bit, head=head, **control, **lp, **rp)


def step_ring(cells):
    return tuple(local_step(cells[i - 1], cell, cells[(i + 1) % len(cells)])
                 for i, cell in enumerate(cells))


@lru_cache(maxsize=1)
def self_description():
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

    def advanced(record):
        fetch = b.both(eq(record, 'phase', FETCH), b.eq(record['index'], record['pc']))
        gate = b.both(fetch, eq(record, 'kind', GATE))
        send = b.both(fetch, eq(record, 'kind', SEND))
        loop = b.both(fetch, eq(record, 'kind', LOOP))
        load = b.either(gate, send)
        a, c, d, sent = (condition(record, phase, field) for phase, field in
                         ((READ_A, 'ra'), (READ_B, 'rb'), (WRITE, 'rd'), (TRANSMIT, 'ra')))
        done = b.either(d, sent)
        result = {name: record[name] for name in CONTROL if name != 'direction'}
        for name, source in (('ra', 'a'), ('rb', 'b'), ('rd', 'd')):
            result[name] = b.select(load, record[source], record[name])
        phase = record['phase']
        for predicate, value in ((gate, READ_A), (send, TRANSMIT), (a, READ_B), (c, WRITE), (done, FETCH)):
            phase = b.select(predicate, b.const(value, 3), phase)
        result['phase'] = phase
        result['pc'] = b.select(loop, b.const(0, 16),
                                b.select(done, b.increment(record['pc']), record['pc']))
        result['value'] = (b.mux(c, b.nand(record['value'][0], record['bit'][0]),
                                 b.mux(a, record['bit'][0], record['value'][0])),)
        return result

    from_left = b.both(left['head'][0], b.both(b.inv(left['direction'][0]), b.inv(left['last'][0])))
    from_right = b.both(right['head'][0], b.both(right['direction'][0], b.inv(right['first'][0])))
    reflect = b.both(center['head'][0], b.mux(center['direction'][0], center['first'][0], center['last'][0]))
    left_control, center_control = advanced(left), advanced(center)
    out = dict(center)
    out['head'] = (b.either(reflect, b.either(from_left, from_right)),)
    for name in CONTROL[:-1]:
        value = b.select(from_right, right[name], b.const(0, len(right[name])))
        value = b.select(from_left, left_control[name], value)
        own = b.select(center['direction'][0], center[name], center_control[name])
        out[name] = b.select(reflect, own, value)
    out['direction'] = (b.mux(reflect, b.inv(center['direction'][0]),
                              b.both(b.inv(from_left), from_right)),)
    executing = b.both(center['head'][0], b.inv(center['direction'][0]))
    sending = b.both(executing, condition(center, TRANSMIT, 'ra'))
    bit = center['bit'][0]
    for channel, source, edge in (('lp', right, right['first'][0]), ('rp', left, left['last'][0])):
        crossed = b.either(source[channel + '_cross'][0], edge)
        valid = b.both(source[channel + '_valid'][0], b.inv(b.both(source[channel + '_cross'][0], edge)))
        hit = b.both(b.both(valid, crossed),
                     b.both(eq(center, 'kind', MEM), b.eq(center['index'], source[channel + '_target'])))
        moving = b.both(valid, b.inv(hit))
        bit = b.mux(hit, source[channel + '_bit'][0], bit)
        emit = b.both(sending, center['rd'][0] if channel == 'lp' else b.inv(center['rd'][0]))
        for suffix, value, fresh in (('target', source[channel + '_target'], center['rb']),
                                     ('bit', source[channel + '_bit'], center['bit']),
                                     ('cross', (crossed,), (0,)), ('valid', (1,), (1,))):
            transported = b.select(moving, value, b.const(0, len(value)))
            out[channel + '_' + suffix] = b.select(emit, fresh, transported)
    write = b.both(executing, condition(center, WRITE, 'rd'))
    out['bit'] = (b.mux(write, center['value'][0], bit),)
    return b.finish([wire for name, _ in SCHEMA for wire in out[name]])


def identity():
    return {'schema': SCHEMA, 'width': WIDTH, 'neighborhood': NEIGHBORHOOD,
            'description_sha256': self_description().digest()}
