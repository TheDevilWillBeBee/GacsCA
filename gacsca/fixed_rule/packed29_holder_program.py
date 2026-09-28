"""Fixed dependency-directed self-ROM, retaining complete encoded raw states.

Only used neighbor operands get three history slots and a vote slot. Own ROM
metadata is regenerated from the voted Address before each full evaluation.
Info and Hold still contain every raw field, including every controller copy.
"""
from dataclasses import dataclass
from functools import lru_cache
import numpy as np
from . import packed29_holder_rule as f, packed29_holder_core as c
from . import packed29_holder_layout as reference
from .word_allocation_and import allocate
from .word_program import Instruction
from .wordcode_and import LIT, ADD, NAND, EQ, AND, MASK
from . import pack3_rom

RESERVED = 8
MASK_ADDRESS = 6
RESULT_CAPACITY = 256  # Fixed construction choice, never a depth input.
HISTORY_OFFSETS = (0, 2, 3)
compiled_description = reference.compiled_description


def dependencies(description):
    used = {wire for op, a, b in description.operations if op != LIT
            for wire in (a, b) if wire < description.inputs}
    used.update(wire for wire in description.outputs if wire < description.inputs)
    return tuple(sorted(used))


@dataclass(frozen=True)
class Layout(reference.Layout):
    required_inputs: tuple
    gathered_inputs: tuple
    regenerated_inputs: tuple
    branch_instruction: int
    signal_entry: int
    packed: pack3_rom.PackedROM

    @property
    def computation_cells(self):return self.memory_count+len(self.packed.rows)+1

    def physical_position(self,pc):
        return self.memory_count+self.packed.physical_of_pc[pc]

    def schedule(self,start,end):
        phase,ticks=0,1;cycle=2*self.computation_cells;rows=[]
        for pc in range(start,end):
            op=self.instructions[pc];position=self.physical_position(pc);targets=(position,)
            if op.kind in c.ALU_KINDS:targets+=(op.a,op.b,op.d)
            elif op.kind==LIT:targets+=(op.d,)
            elif op.kind in (c.SEND,c.LOAD):targets+=(op.a,)
            times=[]
            for target in targets:
                ticks+=(target-phase)%cycle+1;phase=(target+1)%cycle;times.append(ticks)
            if op.kind==c.META:
                ticks+=4*self.computation_cells+op.a-position
                phase=op.a+1;times.append(ticks)
            rows.append(tuple(times))
        return ticks,tuple(rows)

    def gather_schedule(self,stage):
        """One fixed gather body, with target slots chosen by the physical Age."""
        start,end=self.stage_ranges[stage]
        offset=c.GATHER_OFFSETS[stage]
        phase,ticks=0,1;cycle=2*self.computation_cells;rows=[]
        for pc in range(start,end):
            op=self.instructions[pc];position=self.physical_position(pc);targets=(position,)
            if op.kind in c.ALU_KINDS:
                destination=(op.d&~c.PHASE_MARK)+offset if op.d&c.PHASE_MARK else op.d
                targets+=(op.a,op.b,destination)
            elif op.kind==LIT:targets+=(op.d,)
            elif op.kind in (c.SEND,c.LOAD):targets+=(op.a,)
            times=[]
            for target in targets:
                ticks+=(target-phase)%cycle+1;phase=(target+1)%cycle;times.append(ticks)
            rows.append(tuple(times))
        return ticks,tuple(rows)

    def stage3_schedule(self):
        """Physical head path after the fixed early branch, including sends."""
        path=tuple(range(self.stage_ranges[4][0],self.branch_instruction+1))
        path+=tuple(range(self.signal_entry,len(self.instructions)))
        phase,ticks=0,1;cycle=2*self.computation_cells;rows=[]
        for pc in path:
            op=self.instructions[pc];position=self.physical_position(pc);targets=(position,)
            if op.kind in c.ALU_KINDS:targets+=(op.a,op.b,op.d)
            elif op.kind==LIT:targets+=(op.d,)
            elif op.kind in (c.SEND,c.LOAD):targets+=(op.a,)
            times=[]
            for target in targets:
                ticks+=(target-phase)%cycle+1;phase=(target+1)%cycle;times.append(ticks)
            if op.kind==c.META:
                ticks+=4*self.computation_cells+op.a-position
                phase=op.a+1;times.append(ticks)
            rows.append(tuple(times))
        return ticks,tuple(zip(path,rows))

    def timing_certificate(self):
        gathers=[]
        for stage,(start,end) in enumerate(self.stage_ranges[:3]):
            stopped,rows=self.gather_schedule(stage);packets=[]
            for op,times in zip(self.instructions[start:end],rows):
                if op.kind!=c.SEND:continue
                hops,direction=op.d>>1,op.d&1
                destination=(op.b&~c.PHASE_MARK)+c.GATHER_OFFSETS[stage]
                distance=hops*f.Q+(op.a-destination if direction==c.LEFT else destination-op.a)
                packets.append((direction,times[-1],op.a,distance))
            for i,(direction,t,source,distance) in enumerate(packets):
                line=(source+t if direction else source-t)%f.Q
                for direction2,u,source2,_ in packets[i+1:]:
                    if u>=t+distance or direction!=direction2:continue
                    if line==(source2+u if direction2 else source2-u)%f.Q:
                        raise ValueError('same-track packet collision')
            arrival=max(t+distance for _,t,_,distance in packets)
            deadline=(c.VOTE_AGES[0] if stage==2 else c.ACTIVE_ENDS[stage])-c.RESET_AGES[stage]
            gathers.append(dict(stage=stage+1,head_stopped=stopped,
                                last_arrival=arrival,deadline=deadline,
                                margin=deadline-max(stopped,arrival)))
        evaluation,_=self.schedule(*self.stage_ranges[4])
        stopped,rows=self.stage3_schedule()
        last=max((times[-1]+(op.a-op.b if op.d&1 else op.b-op.a)
                  for pc,times in rows
                  for op in (self.instructions[pc],) if op.kind==c.SEND),default=0)
        result=dict(Q=f.Q,U=f.U,core_cells=self.computation_cells,
                    descriptor_operations=len(compiled_description().operations),
                    gathers=gathers,evaluation_ticks=evaluation,
                    evaluation_budget=c.ACTIVE_ENDS[4]-c.RESET_AGES[4],
                    evaluation_margin=c.ACTIVE_ENDS[4]-c.RESET_AGES[4]-evaluation,
                    capture_budget=c.CAPTURE_AGE-c.VOTE_AGES[0],
                    third_evaluation_old_age=c.VOTE_AGES[0])
        result.update(stage3_head_stopped=stopped,stage3_last_delivery=last,
                      capture_margin=c.CAPTURE_AGE-c.VOTE_AGES[0]-last,
                      stage3_stop_margin=c.ACTIVE_ENDS[2]-c.VOTE_AGES[0]-stopped,
                      early_branch_instruction=self.branch_instruction,
                      early_signal_entry=self.signal_entry)
        result['fits']=all(row['margin']>0 for row in result['gathers']) and result['evaluation_margin']>0 and result['capture_margin']>0 and result['stage3_stop_margin']>0
        return result

    def history(self, stage, neighbor, field):
        if stage not in range(3):
            raise ValueError('three gathering stages required')
        wire = (neighbor + 7) * f.FIELDS + field
        try:
            slot = self.gathered_inputs.index(wire)
        except ValueError as error:
            raise KeyError('input has no gathered history') from error
        return RESERVED + 4 * slot + HISTORY_OFFSETS[stage]


@lru_cache(maxsize=1)
def layout():
    desc = compiled_description()
    required = dependencies(desc)
    static = tuple(w for w in required if w % f.FIELDS < len(f.STATIC))
    assert all(w // f.FIELDS == 7 for w in static)
    gathered = tuple(w for w in required if w not in set(static))
    ranks = {wire: slot for slot, wire in enumerate(gathered)}
    votes = tuple(RESERVED + 4 * slot + 1 for slot in range(len(gathered)))
    info_start = RESERVED + 4 * len(gathered)
    info = tuple(info_start + 2 * i for i in range(f.FIELDS))
    hold = tuple(at + 1 for at in info)
    static_start = info_start + 2 * f.FIELDS
    operands = [None] * desc.inputs
    for wire, address in zip(gathered, votes):
        operands[wire] = address
    for slot, wire in enumerate(static):
        operands[wire] = static_start + slot
    zero_wire = next(desc.inputs + i for i, (op, a, _) in enumerate(desc.operations)
                     if op == LIT and a == 0)
    allocation = allocate(desc, pins=(zero_wire,), capacity=RESULT_CAPACITY)
    scratch_start = static_start + len(static)
    wires = tuple(operands) + tuple(scratch_start + slot for slot in allocation.slots)
    temp = scratch_start + allocation.count
    query, memory = temp + 5, temp + 6
    instructions, entries, ranges = [], [], []

    def emit(kind, a, b, d, *, low_mask=False):
        if kind in c.ALU_KINDS:
            assert a is not None and b is not None
            if low_mask and kind == NAND and a == b:
                a, b = MASK_ADDRESS, a
            if kind in (NAND, ADD, EQ, AND) and a > b:
                a, b = b, a
        instructions.append(Instruction(kind, a, b, d))

    def regenerate(targets):
        for offset in f.STATIC_OFFSETS:
            source = targets[f.COL['address']]
            if offset:
                emit(LIT, offset & MASK, 0, temp)
                emit(ADD, source, temp, query)
                emit(LIT, f.Q - 1, 0, temp + 1)
                emit(NAND, query, temp + 1, temp + 2)
                emit(NAND, temp + 2, temp + 2, query, low_mask=True)
                source = query
            else:
                # Address retains 15 raw bits while Q has 14. Fold the
                # zero-offset query too, matching the projected lift.
                emit(LIT, f.Q - 1, 0, temp + 1)
                emit(NAND, source, temp + 1, temp + 2)
                emit(NAND, temp + 2, temp + 2, query, low_mask=True)
                source = query
            for selector, name in enumerate(c.STATIC):
                emit(c.LOAD, source, 0, 0)
                emit(c.META, targets[f.COL[f'p{offset+3}_{name}']], selector, 0)

    gather_start=len(instructions)
    for stage in range(3):
        start = gather_start
        entries.append(start)
        if stage==0:
            emit(LIT, 0, 0, temp)
            for field, source in enumerate(info):
                wire = 7 * f.FIELDS + field
                if wire in ranks:
                    target = RESERVED + 4 * ranks[wire]
                    emit(ADD, source, temp, c.PHASE_MARK|target)
            for hops in range(1, 8):
                for field, source in enumerate(info):
                    for direction, neighbor in ((c.LEFT, hops), (c.RIGHT, -hops)):
                        wire = (7 + neighbor) * f.FIELDS + field
                        if wire in ranks:
                            target = RESERVED + 4 * ranks[wire]
                            emit(c.SEND, source, c.PHASE_MARK|target,
                                 (hops << 1) | direction)
            emit(c.HALT, 0, 0, 0)
        ranges.append((start, len(instructions)))
    entries.append(len(instructions))
    emit(c.HALT, 0, 0, 0)
    ranges.append((entries[3], len(instructions)))
    start = len(instructions)
    entries.append(start)
    emit(LIT, MASK, 0, MASK_ADDRESS)
    regenerate(operands[7*f.FIELDS:8*f.FIELDS])
    description_instruction = len(instructions)
    needed=set();pending=[desc.outputs[f.COL[name]] for name in ('f1','f2')]
    while pending:
        wire=pending.pop()
        if wire<desc.inputs or wire in needed:continue
        needed.add(wire);kind,a,b=desc.operations[wire-desc.inputs]
        if kind!=LIT:pending.extend((a,b))
    last_flag_op=max(wire-desc.inputs for wire in needed)
    assert zero_wire in needed or zero_wire-desc.inputs<=last_flag_op
    branch_pc=None
    for i, (kind, a, b) in enumerate(desc.operations):
        left, right = (a, 0) if kind == LIT else (wires[a], wires[b])
        emit(kind, left, right, wires[desc.inputs+i], low_mask=True)
        if i==last_flag_op:
            for name in ('f1','f2'):
                emit(ADD,wires[desc.outputs[f.COL[name]]],wires[zero_wire],hold[f.COL[name]])
            branch_pc=len(instructions)
            emit(c.BRANCH_THIRD,0,0,0)
    assert branch_pc is not None
    for field, (target, output) in enumerate(zip(hold, desc.outputs)):
        # Static outputs are overwritten by own-ROM regeneration below. All
        # mutable raw outputs, including every controller copy, are retained.
        if field >= len(f.STATIC):
            emit(ADD, wires[output], wires[zero_wire], target)
    regenerate(hold)
    emit(c.IF_THIRD, 0, 0, 0)
    ranges.append((start, len(instructions)))
    signal_entry=len(instructions)
    instructions[branch_pc]=Instruction(c.BRANCH_THIRD,signal_entry,0,0)
    for target in range(1, 6):
        emit(c.SEND, hold[f.COL['f2']], target, c.LEFT)
    for target in range(f.Q-5, f.Q):
        emit(c.SEND, hold[f.COL['f1']], target, c.RIGHT)
    emit(c.HALT, 0, 0, 0)
    packed=pack3_rom.pack(tuple(instructions))
    result = Layout(memory, tuple(instructions), tuple(entries), info, hold, votes,
                    wires, tuple(ranges), desc.digest(), (start, len(instructions)),
                    description_instruction, required, gathered, static,
                    branch_pc,signal_entry,packed)
    assert result.computation_cells + 5 <= f.Q
    return result


@lru_cache(maxsize=1)
def base_rom():
    g = layout()
    rows = [[c.MEM, address, 31, 0, 0, int(address == 0), 0]
            for address in range(g.memory_count)]
    for slot, vote in enumerate(g.votes):
        base = RESERVED + 4 * slot
        for stage, offset in enumerate(HISTORY_OFFSETS):
            rows[base + offset][2] = (1 << (stage+1)) - 1
        rows[vote][2] = 31 | c.VOTE
    for address in g.info:
        rows[address][2] = c.INFO
    rows[0][2:5] = [g.entries[0] | g.entries[1] << 32,
                    g.entries[2] | g.entries[3] << 32, g.entries[4]]
    rows.extend([row.kind,row.micro_pc,row.a,row.b,row.d,0,0]
                for row in g.packed.rows)
    rows.append([c.LOOP, len(g.instructions), 0, 0, 0, 0, 1])
    out = np.array(rows, dtype=np.uint64)
    out.flags.writeable = False
    return out
