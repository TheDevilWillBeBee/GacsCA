"""One fixed local block encoding for the communicating computation rule.

The input for each physical colony is ONLY its own represented raw cell. Neighbor
arguments are initialized to zero and retrieved by physical SEND packets. The
same complete-rule program, shape, state width and runtime kernel serve all rings.
No hierarchy depth appears in the transition or program construction.
"""
from dataclasses import dataclass
from functools import lru_cache
import numpy as np
from . import communicating as rule
from .communicating_native import COL, array_from_cells


@dataclass(frozen=True)
class Instruction:
    kind: int
    a: int
    b: int
    d: int


@dataclass(frozen=True)
class Layout:
    memory_count: int
    instructions: tuple
    description_sha256: str
    info_start: int = 2 + rule.WIDTH
    info_width: int = rule.WIDTH

    @property
    def colony_cells(self):
        return self.memory_count + len(self.instructions) + 1

    def schedule(self):
        phase, ticks = 0, 0
        cycle = 2 * self.colony_cells
        rows = []
        for i, instruction in enumerate(self.instructions):
            targets = (self.memory_count + i, instruction.a)
            if instruction.kind == rule.GATE:
                targets += (instruction.b, instruction.d)
            times = []
            for target in targets:
                ticks += (target - phase) % cycle + 1
                phase = (target + 1) % cycle
                times.append(ticks)  # time AFTER local processing at this site
            rows.append(tuple(times))
        ticks += (self.colony_cells - 1 - phase) % cycle + 1 + self.colony_cells
        return ticks, tuple(rows)

    @property
    def period_ticks(self):
        return self.schedule()[0]

    def timing_certificate(self):
        period, rows = self.schedule()
        sends = [times[-1] for op, times in zip(self.instructions, rows) if op.kind == rule.SEND]
        first_read = rows[2 * rule.WIDTH + 2][1] - 1  # two guard NANDs precede the description
        packet_hops = self.colony_cells - rule.WIDTH
        arrival = max(sends) + packet_hops
        separation = min(b - a for a, b in zip(sends, sends[1:]))
        if first_read < arrival or separation < packet_hops:
            raise ValueError('retrieval schedule is not safe')
        return dict(period_ticks=period, packet_hops=packet_hops,
                    last_arrival=arrival, first_description_read=first_read,
                    arrival_margin=first_read-arrival, minimum_send_separation=separation)


@lru_cache(maxsize=1)
def layout():
    circuit = rule.self_description()
    guard = circuit.wires + rule.WIDTH
    memory_count = guard + 1
    instructions = []
    for bit in range(rule.WIDTH):
        source = 2 + rule.WIDTH + bit
        instructions.append(Instruction(rule.SEND, source, 2 + 2*rule.WIDTH + bit, rule.LEFT))
        instructions.append(Instruction(rule.SEND, source, 2 + bit, rule.RIGHT))
    # These local operations provide an explicit travel-time guard.
    instructions.extend([Instruction(rule.GATE, 1, 1, guard)] * 2)
    for i, (a, b) in enumerate(circuit.gates):
        instructions.append(Instruction(rule.GATE, a, b, 2 + circuit.inputs + i))
    # Stage ALL output wires before updating ANY center Info input, including
    # outputs that are direct references to old neighbor/center input wires.
    for i, out in enumerate(circuit.outputs):
        instructions.append(Instruction(rule.GATE, out, out, circuit.wires + i))
    for i in range(rule.WIDTH):
        staged = circuit.wires + i
        instructions.append(Instruction(rule.GATE, staged, staged, 2 + rule.WIDTH + i))
    if memory_count > 65536 or len(instructions) > 65535:
        raise ValueError('fixed local workspace capacity exceeded')
    result = Layout(memory_count, tuple(instructions), circuit.digest())
    result.timing_certificate()
    return result


@lru_cache(maxsize=1)
def template():
    geometry = layout()
    cells = [rule.Cell(kind=rule.MEM, index=i, bit=int(i == 1), first=int(i == 0), head=int(i == 0))
             for i in range(geometry.memory_count)]
    cells.extend(rule.Cell(kind=op.kind, index=i, a=op.a, b=op.b, d=op.d)
                 for i, op in enumerate(geometry.instructions))
    cells.append(rule.Cell(kind=rule.LOOP, index=len(geometry.instructions), last=1))
    array = array_from_cells(cells)
    array.flags.writeable = False
    return array


def encode(cells):
    """Block-local initialization E: no neighbor input is read or installed."""
    cells = tuple(cells)
    if not cells:
        raise ValueError('nonempty upper configuration required')
    geometry = layout()
    physical = np.tile(template(), (len(cells), 1))
    for i, cell in enumerate(cells):
        start = i*geometry.colony_cells + geometry.info_start
        physical[start:start+rule.WIDTH, COL['bit']] = rule.encode_cell(cell)
    return physical


def decode(physical):
    geometry = layout()
    if len(physical) % geometry.colony_cells:
        raise ValueError('partial colony')
    return tuple(rule.decode_cell(physical[base+geometry.info_start:base+geometry.info_start+rule.WIDTH,
                                               COL['bit']].tolist())
                 for base in range(0, len(physical), geometry.colony_cells))


def check_boundary(physical):
    """Diagnostic admissibility at a macroperiod boundary, not physical repair."""
    geometry = layout()
    if len(physical) % geometry.colony_cells:
        raise ValueError('partial colony')
    shaped = physical.reshape(-1, geometry.colony_cells, len(rule.SCHEMA))
    base = template()
    for name in ('kind', 'index', 'a', 'b', 'd', 'first', 'last'):
        if not np.all(shaped[:, :, COL[name]] == base[None, :, COL[name]]):
            raise ValueError(f'changed layout field {name}')
    for name in ('head', 'phase', 'pc', 'direction'):
        if not np.all(shaped[:, :, COL[name]] == base[None, :, COL[name]]):
            raise ValueError(f'noncanonical boundary {name}')
    for name in ('ra', 'rb', 'rd', 'value'):
        if np.any(shaped[:, 1:, COL[name]]):
            raise ValueError(f'stale headless controller {name}')
    for name in COL:
        if name.startswith(('lp_', 'rp_')) and np.any(shaped[:, :, COL[name]]):
            raise ValueError(f'pending packet {name}')
    if np.any(shaped[:, 0, COL['bit']]) or not np.all(shaped[:, 1, COL['bit']] == 1):
        raise ValueError('changed constant wires')
    return True
