"""Finite-ring evaluation harness, NOT a local colony block encoding.

Each output raw cell is computed by the same explicit self-description. The
physical tape does all gate evaluation and simultaneous feedback. Host code
only initializes and decodes. Space grows with the size of the represented ring;
16-bit tape labels bound this harness's capacity, not a proposed hierarchy depth.
"""
from dataclasses import dataclass
import numpy as np
from .machine import (Cell, SCHEMA, WIDTH, MASK, MEM, GATE, LOOP, CONTROL,
                      encode_cell, decode_cell, self_description)

COLUMNS = tuple(name for name, _ in SCHEMA)
COL = {name: i for i, name in enumerate(COLUMNS)}


def array_from_cells(cells):
    return np.array([[getattr(c, name) for name in COLUMNS] for c in cells], dtype=np.uint32)


def cells_from_array(array):
    return tuple(Cell(**dict(zip(COLUMNS, map(int, row)))) for row in array)


@dataclass(frozen=True)
class Layout:
    represented_cells: int
    input_count: int
    memory_count: int
    gates: tuple
    description_sha256: str

    @property
    def physical_cells(self):
        return self.memory_count + len(self.gates) + 1

    @property
    def period_ticks(self):
        # Exact data-independent route, beginning just after the LOOP site.
        position, ticks = 0, 0
        for i, (a, b, d) in enumerate(self.gates):
            for target in (self.memory_count + i, a, b, d):
                ticks += (target - position) % self.physical_cells + 1
                position = (target + 1) % self.physical_cells
        return ticks + (self.physical_cells - 1 - position) % self.physical_cells + 1

    @property
    def period_upper_bound(self):
        # Each FETCH/A/B/D search takes at most one lap, plus LOOP search.
        return (4 * len(self.gates) + 1) * self.physical_cells


def ring_layout(n):
    if n < 1:
        raise ValueError('empty represented ring')
    circuit = self_description()
    # Reject before allocating a circuit; do not expand labels or select a kernel.
    if n * (len(circuit.gates) + 2 * WIDTH) + 2 > MASK + 1:
        raise ValueError('fixed tape label capacity exceeded; this is not a hierarchy encoder')
    input_count = n * WIDTH
    next_wire = 2 + input_count
    gates, outputs = [], []
    for x in range(n):
        mapping = [0, 1]
        for site in ((x - 1) % n, x):
            mapping.extend(range(2 + site * WIDTH, 2 + (site + 1) * WIDTH))
        for a, b in circuit.gates:
            gates.append((mapping[a], mapping[b], next_wire))
            mapping.append(next_wire)
            next_wire += 1
        outputs.extend(mapping[o] for o in circuit.outputs)
    # Stage ALL outputs before overwriting ANY inputs, even direct input wires.
    staged = []
    for out in outputs:
        gates.append((out, out, next_wire))
        staged.append(next_wire)
        next_wire += 1
    for i, source in enumerate(staged):
        gates.append((source, source, 2 + i))
    if next_wire > MASK + 1 or len(gates) > MASK:
        raise ValueError('fixed tape label capacity exceeded; this is not a hierarchy encoder')
    return Layout(n, input_count, next_wire, tuple(gates), circuit.digest())


def encode_ring(cells):
    layout = ring_layout(len(cells))
    bits = [0, 1, *(bit for cell in cells for bit in encode_cell(cell))]
    tape = [Cell(kind=MEM, index=i, bit=bits[i] if i < len(bits) else 0)
            for i in range(layout.memory_count)]
    tape.extend(Cell(kind=GATE, index=i, a=a, b=b, d=d)
                for i, (a, b, d) in enumerate(layout.gates))
    tape.append(Cell(kind=LOOP, index=len(layout.gates)))
    # Canonical phase: head just after LOOP, giving one fixed macroperiod.
    # This never inserts simulated outputs.
    from dataclasses import replace
    tape[0] = replace(tape[0], head=1)
    return array_from_cells(tape), layout


def decode_ring(tape, layout):
    # Input bank is the only representation boundary; scratch is not decoded.
    bits = tape[2:2 + layout.input_count, COL['bit']].tolist()
    return tuple(decode_cell(bits[i:i + WIDTH]) for i in range(0, len(bits), WIDTH))


@dataclass(frozen=True)
class EvaluationLayout:
    memory_count: int
    gates: int
    outputs: tuple
    description_sha256: str

    @property
    def physical_cells(self):
        return self.memory_count + self.gates + 1

    @property
    def period_upper_bound(self):
        return (4 * self.gates + 1) * self.physical_cells


def encode_evaluation(circuit, bits):
    """Internal component test fixture. No hierarchy/self-reference claim from this."""
    if len(bits) != circuit.inputs or any(bit not in (0, 1) for bit in bits):
        raise ValueError('invalid input bits')
    if circuit.wires > MASK + 1 or len(circuit.gates) > MASK:
        raise ValueError('fixed tape label capacity exceeded')
    values = [0, 1, *bits]
    tape = [Cell(kind=MEM, index=i, bit=values[i] if i < len(values) else 0)
            for i in range(circuit.wires)]
    tape.extend(Cell(kind=GATE, index=i, a=a, b=b, d=2 + circuit.inputs + i,
                     head=int(i == 0)) for i, (a, b) in enumerate(circuit.gates))
    tape.append(Cell(kind=LOOP, index=len(circuit.gates), head=int(not circuit.gates)))
    layout = EvaluationLayout(circuit.wires, len(circuit.gates), circuit.outputs, circuit.digest())
    return array_from_cells(tape), layout


def decode_evaluation(tape, layout):
    return tuple(int(tape[i, COL['bit']]) for i in layout.outputs)
