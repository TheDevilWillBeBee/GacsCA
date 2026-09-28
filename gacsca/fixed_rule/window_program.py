"""Fixed compiler with a compact computation window and pipelined colony mail.

The generated program evaluates the full rule, regenerates static fields by local
META reads at the computed Hold.Address, and commits. The input for each physical colony is ONLY its own represented raw cell. Neighbor
arguments are initialized to zero and retrieved by physical SEND packets. The
same complete-rule program, shape, state width and runtime kernel serve all rings.
No hierarchy depth appears in the transition or program construction.
"""
from dataclasses import dataclass
from functools import lru_cache
import numpy as np
from . import window_rule as rule
COL = {name:i for i,(name,_) in enumerate(rule.SCHEMA)}


def array_from_cells(cells):
    return np.array([[getattr(cell,name) for name,_ in rule.SCHEMA] for cell in cells],dtype=np.uint32)


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
        return rule.COLONY_CELLS

    @property
    def computation_cells(self):
        return self.memory_count+len(self.instructions)+1

    @property
    def description_instruction(self):
        return 2*rule.WIDTH+2+rule.WORD+2

    @property
    def hold_start(self):
        return rule.self_description().wires+rule.WIDTH

    @property
    def regeneration_instruction(self):
        return self.description_instruction+len(rule.self_description().gates)+2*rule.WIDTH

    @property
    def commit_instruction(self):
        return self.regeneration_instruction+(rule.WORD+2)*rule.STATIC_WIDTH

    def schedule(self):
        phase, ticks = 0, 0
        cycle = 2 * self.computation_cells
        rows = []
        for i, instruction in enumerate(self.instructions):
            position=self.memory_count+i
            targets=(position,)
            if instruction.kind in (rule.GATE,rule.SEND,rule.LOAD):
                targets+=(instruction.a,)
            if instruction.kind == rule.GATE:
                targets += (instruction.b, instruction.d)
            times = []
            for target in targets:
                ticks += (target - phase) % cycle + 1
                phase = (target + 1) % cycle
                times.append(ticks)  # time AFTER local processing at this site
            if instruction.kind==rule.META:
                # Fixed full lookup pass followed by a first-site-synchronized write.
                ticks+=4*self.computation_cells+instruction.a-position
                phase=instruction.a+1
                times.append(ticks)
            if instruction.kind==rule.WAIT:
                ticks+=rule.COLONY_CELLS
                times[-1]=ticks
            rows.append(tuple(times))
        ticks += (self.computation_cells - 1 - phase) % cycle + 1 + self.computation_cells
        return ticks, tuple(rows)

    @property
    def period_ticks(self):
        return self.schedule()[0]

    def timing_certificate(self):
        period, rows = self.schedule()
        sends = [times[-1] for op, times in zip(self.instructions, rows) if op.kind == rule.SEND]
        first_read = rows[self.description_instruction][1] - 1  # two guard NANDs precede the description
        packet_hops = self.colony_cells - rule.WIDTH
        arrival = max(sends) + packet_hops
        separation = min(b - a for a, b in zip(sends, sends[1:]))
        packets=[(op.d&1,times[-1],op.a) for op,times in zip(self.instructions,rows)
                 if op.kind==rule.SEND]
        for i,(direction,t,source) in enumerate(packets):
            characteristic=(source+t if direction==rule.LEFT else source-t)%self.colony_cells
            for other_direction,u,other_source in packets[i+1:]:
                if u-t>=packet_hops: break
                if direction!=other_direction: continue
                other=(other_source+u if direction==rule.LEFT else other_source-u)%self.colony_cells
                if characteristic==other:
                    raise ValueError('pipelined packets collide on a physical track')
        if first_read < arrival:
            raise ValueError('retrieval schedule is not safe')
        return dict(period_ticks=period, packet_hops=packet_hops,
                    last_arrival=arrival, first_description_read=first_read,
                    arrival_margin=first_read-arrival, minimum_send_separation=separation,packet_characteristics_distinct=True,
                    computation_cells=self.computation_cells)


@lru_cache(maxsize=1)
def layout():
    circuit = rule.self_description()
    guard = circuit.wires + 2*rule.WIDTH
    memory_count = guard + 1
    instructions = []
    for bit in range(rule.WIDTH):
        source = 2 + rule.WIDTH + bit
        instructions.append(Instruction(rule.SEND, source, 2 + 2*rule.WIDTH + bit, rule.LEFT))
        instructions.append(Instruction(rule.SEND, source, 2 + bit, rule.RIGHT))
    # These local operations provide an explicit travel-time guard.
    instructions.extend([Instruction(rule.GATE, 1, 1, guard)] * 2)
    # Constant bits are read from the two existing constant wires. WAIT remains
    # a described local countdown; no host delay replaces its transition.
    instructions.append(Instruction(rule.CLEAR,0,0,0))
    for digit in reversed(range(rule.WORD)):
        instructions.append(Instruction(rule.LOAD,(rule.COLONY_CELLS>>digit)&1,0,0))
    instructions.append(Instruction(rule.WAIT,0,0,0))
    for i, (a, b) in enumerate(circuit.gates):
        instructions.append(Instruction(rule.GATE, a, b, 2 + circuit.inputs + i))
    # Stage a true full Hold word before metadata regeneration or any Info write.
    hold=circuit.wires+rule.WIDTH
    for i,out in enumerate(circuit.outputs):
        inverse=circuit.wires+i
        instructions.append(Instruction(rule.GATE,out,out,inverse))
        instructions.append(Instruction(rule.GATE,inverse,inverse,hold+i))
    offsets={}; offset=0
    for name,width in rule.SCHEMA:
        offsets[name]=offset; offset+=width
    selector=0
    for name,width in rule.STATIC_SCHEMA:
        for bit in range(width):
            instructions.append(Instruction(rule.CLEAR,0,0,0))
            for address_bit in reversed(range(rule.WORD)):
                instructions.append(Instruction(rule.LOAD,hold+offsets['address']+address_bit,0,0))
            instructions.append(Instruction(rule.META,hold+offsets[name]+bit,selector,0))
            selector+=1
    # Commit every raw field, including the regenerated instruction record.
    for i in range(rule.WIDTH):
        inverse=circuit.wires+i
        instructions.append(Instruction(rule.GATE,hold+i,hold+i,inverse))
        instructions.append(Instruction(rule.GATE,inverse,inverse,2+rule.WIDTH+i))
    if memory_count > rule.MASK or len(instructions) > rule.MASK:
        raise ValueError('fixed local workspace capacity exceeded')
    result = Layout(memory_count, tuple(instructions), circuit.digest())
    if result.computation_cells>=result.colony_cells:
        raise ValueError('computation window exceeds fixed colony')
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
    array[:,COL['address']] = np.arange(len(array),dtype=np.uint32)
    array.flags.writeable = False
    return array


def encode_cores(cells):
    """Block-local initialization E: no neighbor input is read or installed."""
    cells = tuple(cells)
    if not cells:
        raise ValueError('nonempty upper configuration required')
    geometry = layout()
    physical = np.tile(template(), (len(cells), 1))
    for i, cell in enumerate(cells):
        start = i*geometry.computation_cells + geometry.info_start
        physical[start:start+rule.WIDTH, COL['bit']] = rule.encode_cell(cell)
    return physical


def decode_cores(physical):
    geometry = layout()
    if len(physical) % geometry.computation_cells:
        raise ValueError('partial colony')
    return tuple(rule.decode_cell(physical[base+geometry.info_start:base+geometry.info_start+rule.WIDTH,
                                               COL['bit']].tolist())
                 for base in range(0, len(physical), geometry.computation_cells))


def check_boundary(physical):
    """Diagnostic admissibility at a macroperiod boundary, not physical repair."""
    geometry = layout()
    if len(physical) % geometry.computation_cells:
        raise ValueError('partial colony')
    shaped = physical.reshape(-1, geometry.computation_cells, len(rule.SCHEMA))
    base = template()
    for name in ('kind', 'index', 'a', 'b', 'd', 'first', 'last', 'address'):
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
