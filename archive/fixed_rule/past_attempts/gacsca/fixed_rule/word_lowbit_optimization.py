"""Use only the required low bit when NAND's other operand is Boolean.

For every 64-bit x: (-x)&1 == x&1. Negation is represented by
ADD(NAND(x,x),1). A Boolean co-operand masks all other bits, so replacing
that arithmetic expression (or its bitwise inverse) is exact for NAND.
"""
from .word_identity_optimization import IdentityBuilder
from .wordcode import NAND,ADD,LIT,MASK
from .word_prune import prune


class LowBitBuilder(IdentityBuilder):
    def low_equivalent(self,wire):
        if wire<self.inputs:return wire
        op,a,b=self.operations[wire-self.inputs]
        if op==ADD:
            if a==b:return self.const(0)
            for value,one in ((a,b),(b,a)):
                if self.constants.get(one)==1:
                    inverse=self.inverse(value)
                    if inverse is not None:return inverse
        if op==NAND and a==b:
            value=self.low_equivalent(a)
            if value!=a:return self.op(NAND,value,value)
        return wire
    def op(self,opcode,a,b):
        if opcode==NAND:
            if self.bounds[b][0]<=1:
                value=self.low_equivalent(a)
                if value!=a:self.rewrites['low_bit_cooperand']+=1;a=value
            if self.bounds[a][0]<=1:
                value=self.low_equivalent(b)
                if value!=b:self.rewrites['low_bit_cooperand']+=1;b=value
        return super().op(opcode,a,b)


def optimize(program,widths):
    if len(widths)!=program.inputs:raise ValueError('complete typed input widths required')
    b=LowBitBuilder(widths);mapping=list(range(program.inputs))
    for kind,a,c in program.operations:mapping.append(b.const(a) if kind==LIT else b.op(kind,mapping[a],mapping[c]))
    return prune(b.finish(tuple(mapping[w] for w in program.outputs))),dict(b.rewrites)
