"""Depth-independent three-ALU-instruction ROM encoding feasibility probe.

This is only a host compiler and decoder for a proposed fixed physical PACK3
instruction. It does not implement a physical transition or prove closure.
Every packed operand must be a 12-bit physical MEM address. Special and marked
instructions remain separate. No evolving transition uses these functions.
"""
from dataclasses import dataclass

from .word_program import Instruction
from . import gather29_holder_core as c

PACK3=10  # Prospective replacement for WAIT, absent from the current own ROM.
ADDRESS_BITS=12
ADDRESS_LIMIT=1<<ADDRESS_BITS
COUNT_SHIFT=40
MASK40=(1<<40)-1


@dataclass(frozen=True)
class Row:
    micro_pc:int
    kind:int
    a:int
    b:int
    d:int
    count:int=1


@dataclass(frozen=True)
class PackedROM:
    rows:tuple[Row,...]
    physical_of_pc:tuple[int,...]
    virtual_count:int

    def decode(self):
        result=[]
        for row in self.rows:
            if row.kind!=PACK3:
                result.append(Instruction(row.kind,row.a,row.b,row.d))
                continue
            assert 2<=row.count<=3
            for slot in range(row.count):
                if slot<2:
                    word=(row.a if slot==0 else row.b)&MASK40
                    result.append(Instruction(word&15,(word>>4)&4095,
                                              (word>>16)&4095,(word>>28)&4095))
                else:
                    result.append(Instruction(row.d&15,(row.d>>4)&4095,
                                              (row.d>>16)&4095,(row.a>>40)&4095))
        return tuple(result)


def eligible(op):
    return op.kind in c.ALU_KINDS and all(0<=at<ADDRESS_LIMIT
                                           for at in (op.a,op.b,op.d))


def word(op):
    assert eligible(op)
    return op.kind|(op.a<<4)|(op.b<<16)|(op.d<<28)


def pack(instructions):
    instructions=tuple(instructions)
    rows=[];locations=[];pc=0
    while pc<len(instructions):
        if eligible(instructions[pc]):
            run=pc
            while run<len(instructions) and eligible(instructions[run]):run+=1
            length=min(3,run-pc)
            if length>=2:
                ops=instructions[pc:pc+length]
                a=word(ops[0])
                b=word(ops[1])|(length<<COUNT_SHIFT)
                d=0
                if length==3:
                    a|=ops[2].d<<COUNT_SHIFT
                    d=ops[2].kind|(ops[2].a<<4)|(ops[2].b<<16)
                rows.append(Row(pc,PACK3,a,b,d,length))
                locations.extend((len(rows)-1,)*length)
                pc+=length
                continue
        op=instructions[pc]
        rows.append(Row(pc,op.kind,op.a,op.b,op.d))
        locations.append(len(rows)-1);pc+=1
    result=PackedROM(tuple(rows),tuple(locations),len(instructions))
    assert result.decode()==instructions
    assert len(result.physical_of_pc)==len(instructions)
    cursor=0
    for at,row in enumerate(result.rows):
        assert row.micro_pc==cursor
        assert all(result.physical_of_pc[pc]==at
                   for pc in range(cursor,cursor+row.count))
        cursor+=row.count
    assert cursor==len(instructions)
    return result
