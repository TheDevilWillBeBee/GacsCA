"""Compile-time word identities for the complete, typed physical descriptor.

This never evolves a cell or dispatches on hierarchy depth. It emits only the
existing word operations. Known-bit bounds justify width-dependent identities;
all raw controller inputs and all outputs remain present.
"""
from collections import Counter
from .wordcode import Builder,Program,NAND,ADD,SHR,EQ,LT,LIT,MASK,arithmetic
from .word_prune import prune


class IdentityBuilder(Builder):
    def __init__(self,widths):
        super().__init__(len(widths))
        if any(type(w) is not int or not 1<=w<=64 for w in widths):raise ValueError('input widths in 1..64 required')
        self.bounds=[((1<<w)-1,MASK) for w in widths]
        self.rewrites=Counter()

    def const(self,value):
        result=super().const(value)
        if result==len(self.bounds):self.bounds.append((value&MASK,MASK^(value&MASK)))
        return result

    def inverse(self,wire):
        if wire<self.inputs:return None
        op,a,b=self.operations[wire-self.inputs]
        return a if op==NAND and a==b else None

    def done(self,kind,value):
        self.rewrites[kind]+=1
        return value

    def op(self,opcode,a,b):
        av,bv=self.constants.get(a),self.constants.get(b)
        ao,az=self.bounds[a];bo,bz=self.bounds[b]
        if av is not None and bv is not None:return self.const(arithmetic(opcode,av,bv))
        if opcode==NAND:
            if av==0 or bv==0:return self.done('nand_zero',self.const(MASK))
            if self.inverse(a)==b or self.inverse(b)==a:return self.done('nand_complements',self.const(MASK))
            if a==b and self.inverse(a) is not None:return self.done('double_inversion',self.inverse(a))
            for x,constant,value in ((a,b,bv),(b,a,av)):
                if value is not None and x!=constant and self.bounds[x][0]&~value==0:
                    return self.done('redundant_and_mask',self.op(NAND,x,x))
        elif opcode==ADD:
            if av==0:return self.done('add_zero',b)
            if bv==0:return self.done('add_zero',a)
            if self.inverse(a)==b or self.inverse(b)==a:return self.done('add_complements',self.const(MASK))
        elif opcode==SHR:
            if bv==0:return self.done('shift_zero',a)
            if av==0 or (bv is not None and bv>=ao.bit_length()):return self.done('shift_past_width',self.const(0))
        elif opcode==EQ:
            if a==b:return self.done('equal_self',self.const(1))
            for x,value in ((a,bv),(b,av)):
                if value is None:continue
                ones,zeros=self.bounds[x]
                if value&~ones or (MASK^value)&~zeros:return self.done('equality_outside_bits',self.const(0))
                if value==1 and ones<=1:return self.done('boolean_equal_one',x)
                if value==0 and x>=self.inputs:
                    op,y,z=self.operations[x-self.inputs]
                    if op==EQ:
                        for operand,zero in ((y,z),(z,y)):
                            if self.constants.get(zero)==0 and self.bounds[operand][0]<=1:
                                return self.done('boolean_double_negation',operand)
        elif opcode==LT:
            if a==b:return self.done('less_self',self.const(0))
            if ao<(MASK^bz):return self.done('less_disjoint_ranges',self.const(1))
            if (MASK^az)>=bo:return self.done('less_disjoint_ranges',self.const(0))
        result=super().op(opcode,a,b)
        if result==len(self.bounds):
            if opcode==NAND:ones,zeros=az|bz,ao&bo
            elif opcode in (EQ,LT):ones,zeros=1,MASK
            elif opcode==ADD:
                maximum=ao+bo;ones=MASK if maximum>MASK else (1<<maximum.bit_length())-1;zeros=MASK
            elif opcode==SHR:
                ones=(ao>>bv) if bv is not None and bv<64 else 0 if bv is not None else (1<<ao.bit_length())-1
                zeros=MASK
            else:raise ValueError('unknown word operation')
            self.bounds.append((ones,zeros))
        return result


def optimize(program,*,input_widths=None):
    widths=(64,)*program.inputs if input_widths is None else tuple(input_widths)
    if len(widths)!=program.inputs:raise ValueError('all raw input widths required')
    b=IdentityBuilder(widths);mapping=list(range(program.inputs))
    for op,a,c in program.operations:
        mapping.append(b.const(a) if op==LIT else b.op(op,mapping[a],mapping[c]))
    result=prune(b.finish(tuple(mapping[x] for x in program.outputs)))
    assert result.inputs==program.inputs and len(result.outputs)==len(program.outputs)
    return result,dict(input_widths=widths,rewrites=dict(b.rewrites),
                       original_operations=len(program.operations),optimized_operations=len(result.operations),
                       original_sha256=program.digest(),optimized_sha256=result.digest())
