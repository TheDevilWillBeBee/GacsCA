"""Conservative per-bit mutable-owner dependencies for checked word terms.

Unknown bits retain every possible owner dependency. Constant Boolean identities
and carry propagation can discard dependencies only when the bit is determined.
This avoids treating discarded low Signal bits as influences on higher bits.
"""
from functools import lru_cache
from gacsca.fixed_rule.wordcode import ADD,EQ,LT,NAND,SHR

EMPTY=frozenset()
ZERO=(0,EMPTY)
ONE=(1,EMPTY)


def neg(value):return (None if value[0] is None else 1-value[0],value[1])
def both(a,b):
    if a[0]==0 or b[0]==0:return ZERO
    if a[0]==1:return b
    if b[0]==1:return a
    return None,a[1]|b[1]
def either(a,b):
    if a[0]==1 or b[0]==1:return ONE
    if a[0]==0:return b
    if b[0]==0:return a
    return None,a[1]|b[1]
def xor(a,b):
    if a[0] is not None and b[0] is not None:return a[0]^b[0],EMPTY
    return None,a[1]|b[1]


class BitDependencies:
    def __init__(self,terms,owners):
        self.terms,self.owners=terms,owners

    @lru_cache(None)
    def whole(self,word):
        if word in self.owners:return frozenset((self.owners[word],))
        node=self.terms.nodes[word]
        if node[0] in ('variable','const'):return EMPTY
        if node[0]=='op':return self.whole(node[2])|self.whole(node[3])
        if node[0] in ('not','modadd'):return self.whole(node[1])
        raise AssertionError(('unreviewed term',node))

    def operand(self,operand,k):
        return self.bit(operand[1],k) if operand[0]=='word' else ((operand[1]>>k)&1,EMPTY)

    @lru_cache(None)
    def carry(self,a,b,k):
        if k==0:return ZERO
        x,y=self.operand(a,k-1),self.operand(b,k-1)
        return either(both(x,y),both(self.carry(a,b,k-1),xor(x,y)))

    @lru_cache(None)
    def bit(self,word,k):
        if not 0<=k<64:return ZERO
        node=self.terms.nodes[word]
        if node[0]=='const':return (node[1]>>k)&1,EMPTY
        if node[0]=='variable':
            if k>=node[2]:return ZERO
            return None,self.whole(word)
        if node[0]=='not':return neg(self.bit(node[1],k))
        if node[0]=='modadd':
            if k>=node[3]:return ZERO
            a,b=('word',node[1]),('const',node[2] % (1<<node[3]))
            return xor(xor(self.operand(a,k),self.operand(b,k)),self.carry(a,b,k))
        if node[0]!='op':raise AssertionError(('unreviewed bit term',node))
        kind,a,b=node[1:]
        if kind==NAND:return neg(both(self.bit(a,k),self.bit(b,k)))
        if kind==SHR:
            distance=self.terms.value(b)
            if distance is not None:return self.bit(a,k+distance)
            if self.terms.value(a)==0:return ZERO
            return None,self.whole(a)|self.whole(b)
        if kind in (EQ,LT):return (None,self.whole(a)|self.whole(b)) if k==0 else ZERO
        if kind==ADD:
            if a==b:return self.bit(a,k-1)
            aa,bb=('word',a),('word',b)
            return xor(xor(self.bit(a,k),self.bit(b,k)),self.carry(aa,bb,k))
        raise AssertionError(('unreviewed word operation',kind))
