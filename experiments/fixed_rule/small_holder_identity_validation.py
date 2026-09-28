"""Independent algebraic normalization for typed descriptor equivalence.

Uses structural widths of AND/OR expression trees, not optimizer masks or its
rewrite log. Existing arithmetic/modular normalization is retained.
"""
from functools import lru_cache
from gacsca.fixed_rule.wordcode import NAND,ADD,SHR,EQ,LT,MASK
from experiments.fixed_rule.certify_small_holder_mail_factorization import BooleanTerms


class StructuralTerms(BooleanTerms):
    def __init__(self,rom):
        super().__init__(rom)
        self.structural_width=lru_cache(None)(self._structural_width)

    def width(self,x):return self.structural_width(x)

    def _structural_width(self,x):
        base=super().width(x)
        if base<64:return base
        node=self.nodes[x]
        if node[0]=='not':
            inner=self.nodes[node[1]]
            if inner[0]=='op' and inner[1]==NAND:
                return min(self.width(inner[2]),self.width(inner[3]))
        if node[0]=='op':
            op,a,b=node[1:]
            if op==NAND:
                def complement_width(term):
                    value=self.nodes[term]
                    if value[0]=='const':return (MASK^value[1]).bit_length()
                    if value[0]=='not':return self.width(value[1])
                    if value[0]=='op' and value[1]==NAND:
                        return min(self.width(value[2]),self.width(value[3]))
                    return 64
                return max(complement_width(a),complement_width(b))
            if op==ADD:return min(64,max(self.width(a),self.width(b))+1)
            if op==SHR:
                shift=self.value(b)
                return max(0,self.width(a)-shift) if shift is not None else self.width(a)
        return base

    def op(self,kind,a,b):
        if kind==NAND:
            for x,constant in ((a,b),(b,a)):
                value=self.value(constant)
                if value is not None and value&(value+1)==0 and self.width(x)<=value.bit_length():
                    return self.inv(x)
        return super().op(kind,a,b)
