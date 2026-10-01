"""Finite 64-bit expressions specialized to the complete Gacs/Gray rule family.

Compilation is host initialization. Program.evaluate is a diagnostic oracle;
physical evaluation is performed by the word CA's local instruction controller.
"""
from dataclasses import dataclass
import hashlib
import json

MASK=(1<<64)-1
NAND,ADD,SHR,EQ,LT,LIT=1,2,3,4,5,11
AND_ALU,AND=6,14


def arithmetic(op,a,b):
    if op==NAND:return (~(a&b))&MASK
    if op in (AND_ALU,AND):return a&b
    if op==ADD:return (a+b)&MASK
    if op==SHR:return a>>b if b<64 else 0
    if op==EQ:return int(a==b)
    if op==LT:return int(a<b)
    return 0


@dataclass(frozen=True)
class Program:
    inputs:int
    operations:tuple
    outputs:tuple

    @property
    def wires(self):return self.inputs+len(self.operations)

    def evaluate(self,words):
        if len(words)!=self.inputs or any(not 0<=int(x)<=MASK for x in words):
            raise ValueError('complete unsigned 64-bit input words required')
        values=list(map(int,words))
        for op,a,b in self.operations:
            values.append(a if op==LIT else arithmetic(op,values[a],values[b]))
        return tuple(values[i] for i in self.outputs)

    def digest(self):
        return hashlib.sha256(json.dumps((self.inputs,self.operations,self.outputs),separators=(',',':')).encode()).hexdigest()


class Builder:
    def __init__(self,inputs):
        self.inputs=inputs;self.operations=[];self.memo={};self.constants={}

    def const(self,value):
        value&=MASK
        key=(LIT,value,0)
        if key not in self.memo:
            self.memo[key]=self.inputs+len(self.operations);self.operations.append(key)
            self.constants[self.memo[key]]=value
        return self.memo[key]

    def op(self,opcode,a,b):
        if a in self.constants and b in self.constants:
            return self.const(arithmetic(opcode,self.constants[a],self.constants[b]))
        if opcode in (NAND,ADD,EQ,AND) and a>b:a,b=b,a
        key=(opcode,a,b)
        if key not in self.memo:
            self.memo[key]=self.inputs+len(self.operations);self.operations.append(key)
        return self.memo[key]

    def nand(self,a,b):return self.op(NAND,a,b)
    def inv(self,a):return self.nand(a,a)
    def band(self,a,b):return self.inv(self.nand(a,b))
    def bor(self,a,b):return self.nand(self.inv(a),self.inv(b))
    def add(self,a,b):return self.op(ADD,a,b)
    def shr(self,a,b):return self.op(SHR,a,b)
    def eq(self,a,b):return self.op(EQ,a,b)
    def lt(self,a,b):return self.op(LT,a,b)
    def not_(self,a):return self.eq(a,self.const(0))
    def nonzero(self,a):return self.not_(self.not_(a))
    def mask(self,a,width):return self.band(a,self.const((1<<width)-1))
    def select(self,condition,yes,no):
        if yes==no:return yes
        mask=self.add(self.inv(condition),self.const(1))
        return self.nand(self.nand(mask,yes),self.nand(self.inv(mask),no))
    def any(self,*values):
        result=self.const(0)
        for value in values:result=self.bor(result,value)
        return result
    def all(self,*values):
        result=self.const(1)
        for value in values:result=self.band(result,value)
        return result
    def count(self,values,k):
        result=self.const(0)
        for value in values:result=self.add(result,value)
        return self.not_(self.lt(result,self.const(k)))
    def finish(self,outputs):return Program(self.inputs,tuple(self.operations),tuple(outputs))
