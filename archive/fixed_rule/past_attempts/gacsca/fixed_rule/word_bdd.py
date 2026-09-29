"""Small exact ROBDD checker for fixed-rule word-expression identities.

Diagnostic proof tooling only. Never called by a physical transition/executor.
Bits are little endian; variable order is increasing variable index. Unique,
reduced ordered nodes give canonical Boolean functions without sampling.
"""
from functools import lru_cache
from .wordcode import NAND,ADD,SHR,EQ,LT,LIT


class BDD:
    def __init__(self,variables):
        self.variables=variables;self.nodes=[(variables,0,0),(variables,1,1)];self.unique={}
    def node(self,var,lo,hi):
        if lo==hi:return lo
        assert 0<=var<self.variables and self.nodes[lo][0]>var and self.nodes[hi][0]>var
        key=(var,lo,hi)
        if key not in self.unique:self.unique[key]=len(self.nodes);self.nodes.append(key)
        return self.unique[key]
    def variable(self,var):return self.node(var,0,1)
    @lru_cache(maxsize=None)
    def binary(self,truth,a,b):
        # truth bit index = 2*a+b at terminals.
        if a<2 and b<2:return (truth>>(2*a+b))&1
        va,la,ha=self.nodes[a];vb,lb,hb=self.nodes[b];v=min(va,vb)
        if va!=v:la=ha=a
        if vb!=v:lb=hb=b
        return self.node(v,self.binary(truth,la,lb),self.binary(truth,ha,hb))
    def inv(self,a):return self.binary(6,a,1)
    def and_(self,a,b):return self.binary(8,a,b)
    def or_(self,a,b):return self.binary(14,a,b)
    def xor(self,a,b):return self.binary(6,a,b)
    def ite(self,c,a,b):return self.or_(self.and_(c,a),self.and_(self.inv(c),b))
    def const(self,value,width=64):return tuple((value>>i)&1 for i in range(width))
    def add(self,a,b):
        carry=0;out=[]
        for x,y in zip(a,b):
            parity=self.xor(x,y);out.append(self.xor(parity,carry));carry=self.or_(self.and_(x,y),self.and_(parity,carry))
        return tuple(out)
    def less(self,a,b):
        value=0
        for x,y in zip(a,b):value=self.or_(self.and_(self.inv(x),y),self.and_(self.inv(self.xor(x,y)),value))
        return value
    def arithmetic(self,op,a,b):
        width=len(a);assert len(b)==width
        if op==NAND:return tuple(self.inv(self.and_(x,y)) for x,y in zip(a,b))
        if op==ADD:return self.add(a,b)
        if op==EQ:
            value=1
            for x,y in zip(a,b):value=self.and_(value,self.inv(self.xor(x,y)))
            return (value,)+(0,)*(width-1)
        if op==LT:return (self.less(a,b),)+(0,)*(width-1)
        if op==SHR:
            value=a
            for i,control in enumerate(b):
                shift=1<<i
                moved=value[shift:]+(0,)*shift if shift<width else (0,)*width
                value=tuple(self.ite(control,x,y) for x,y in zip(moved,value))
            return value
        raise ValueError('unsupported word operation')
    def evaluate(self,program,inputs):
        assert len(inputs)==program.inputs
        wires=list(inputs)
        for op,a,b in program.operations:wires.append(self.const(a) if op==LIT else self.arithmetic(op,wires[a],wires[b]))
        return tuple(wires[i] for i in program.outputs)
    def value(self,node,assignment):
        while node>=2:
            var,lo,hi=self.nodes[node];node=hi if (assignment>>var)&1 else lo
        return node
    def witness(self,node):
        if node==0:return None
        assignment=0
        while node>=2:
            var,lo,hi=self.nodes[node]
            if lo:node=lo
            else:assignment|=1<<var;node=hi
        assert node==1
        return assignment
