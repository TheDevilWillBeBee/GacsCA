"""Local evaluation regions with repeated labels, not yet neighbor retrieval.

Each region receives a complete raw three-cell neighborhood at initialization.
Evolving these snapshots into a block simulation requires autonomous retrieval
and output-to-Info commit; callers must not emulate those by refilling inputs.
"""
from dataclasses import dataclass
import numpy as np
from .confined import Cell, MEM, GATE, LOOP, WIDTH, encode_cell, decode_cell, self_description
from .confined_native import COL, array_from_cells


@dataclass(frozen=True)
class Layout:
    memory_count: int
    gates: tuple
    outputs: tuple
    description_sha256: str

    @property
    def colony_cells(self):
        return self.memory_count + len(self.gates) + 1

    @property
    def period_ticks(self):
        # Unfold the reflecting path into a directed cycle of 2Q phases.
        phase, ticks = 0, 0
        cycle = 2 * self.colony_cells
        for i, (a, b) in enumerate(self.gates):
            destination = 2 + 3 * WIDTH + i
            for target in (self.memory_count + i, a, b, destination):
                ticks += (target - phase) % cycle + 1
                phase = (target + 1) % cycle
        ticks += (self.colony_cells - 1 - phase) % cycle + 1
        # LOOP is executed rightward at the final cell; return to cell zero.
        return ticks + self.colony_cells


def layout():
    circuit = self_description()
    if circuit.wires > 65536 or len(circuit.gates) > 65535:
        raise ValueError('description exceeds fixed local workspace')
    return Layout(circuit.wires, circuit.gates, circuit.outputs, circuit.digest())


def encode_evaluations(neighborhoods):
    """Initialize disjoint colonies; only the number of colonies varies."""
    neighborhoods = tuple(tuple(row) for row in neighborhoods)
    if not neighborhoods or any(len(row) != 3 for row in neighborhoods):
        raise ValueError('one or more three-cell neighborhoods required')
    geometry = layout()
    base = [Cell(kind=MEM, index=i, bit=int(i == 1), first=int(i == 0), head=int(i == 0))
            for i in range(geometry.memory_count)]
    base.extend(Cell(kind=GATE, index=i, a=a, b=b, d=2 + 3 * WIDTH + i)
                for i, (a, b) in enumerate(geometry.gates))
    base.append(Cell(kind=LOOP, index=len(geometry.gates), last=1))
    array = np.tile(array_from_cells(base), (len(neighborhoods), 1))
    for i, neighborhood in enumerate(neighborhoods):
        bits = [bit for cell in neighborhood for bit in encode_cell(cell)]
        start = i * geometry.colony_cells + 2
        array[start:start + len(bits), COL['bit']] = bits
    return array, geometry


def decode_evaluations(array, geometry):
    if len(array) % geometry.colony_cells:
        raise ValueError('partial colony')
    return tuple(decode_cell([int(array[base + wire, COL['bit']]) for wire in geometry.outputs])
                 for base in range(0, len(array), geometry.colony_cells))
