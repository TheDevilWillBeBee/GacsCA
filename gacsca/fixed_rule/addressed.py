"""Unprojected computing rule with an explicit static physical Address.

Every evaluator/packet field of the communicating candidate is retained. Address
is part of the complete description and is unchanged by this preliminary rule.
That restriction is essential to the current projection proof, not a repair rule.
"""
from dataclasses import dataclass
from functools import lru_cache
from . import communicating as base
from .circuit import Circuit

MEM, GATE, LOOP, SEND = base.MEM, base.GATE, base.LOOP, base.SEND
FETCH, READ_A, READ_B, WRITE, TRANSMIT = base.FETCH, base.READ_A, base.READ_B, base.WRITE, base.TRANSMIT
RIGHT, LEFT = base.RIGHT, base.LEFT
SCHEMA = base.SCHEMA + (('address', 16),)
WIDTH = sum(width for _, width in SCHEMA)
NEIGHBORHOOD = (-1, 0, 1)


@dataclass(frozen=True)
class Cell(base.Cell):
    address: int = 0

    def __post_init__(self):
        super().__post_init__()
        if not isinstance(self.address, int) or not 0 <= self.address < 65536:
            raise ValueError('Address outside fixed alphabet')


def local_step(left, center, right):
    # dataclasses.replace preserves the subclass's Address. No hidden program
    # lookup is present in this unprojected rule or its NAND description.
    return base.local_step(left, center, right)


def step_ring(cells):
    return tuple(local_step(cells[i-1], cell, cells[(i+1) % len(cells)])
                 for i,cell in enumerate(cells))


def encode_cell(cell):
    return tuple((getattr(cell,name) >> i) & 1 for name,width in SCHEMA for i in range(width))


def decode_cell(bits):
    if len(bits) != WIDTH or any(bit not in (0,1) for bit in bits):
        raise ValueError('complete binary raw state required')
    values, offset = {}, 0
    for name,width in SCHEMA:
        values[name] = sum(int(bits[offset+i]) << i for i in range(width))
        offset += width
    return Cell(**values)


@lru_cache(maxsize=1)
def self_description():
    """Complete 193-bit rule, including static Address, in explicit NAND form."""
    source = base.self_description()
    mapping = [0,1]
    for j in range(3):
        mapping.extend(range(2+j*WIDTH,2+j*WIDTH+base.WIDTH))
    gates = []
    for a,b in source.gates:
        gates.append((mapping[a],mapping[b]))
        mapping.append(2+3*WIDTH+len(gates)-1)
    outputs = [mapping[wire] for wire in source.outputs]
    outputs.extend(range(2+WIDTH+base.WIDTH,2+2*WIDTH))
    return Circuit(3*WIDTH,tuple(gates),tuple(outputs))


def identity():
    return dict(schema=SCHEMA,width=WIDTH,neighborhood=NEIGHBORHOOD,
                description_sha256=self_description().digest())
