"""Conservative word bounds with a checked guarded-decrement refinement.

Recognizes the actual NAND/ADD lowering of a selection. No descriptor node is
changed: only an abstract possible-one mask is tightened after checking that
the decrement branch requires its unsigned operand to be nonzero.
"""
from gacsca.fixed_rule.wordcode import NAND, ADD, EQ, MASK
from experiments.fixed_rule.certify_small_holder_meta_query_bounds import KnownBits


class GuardedBounds(KnownBits):
    def __init__(self, terms):
        super().__init__(terms)
        self.refinements=[]

    def operation(self, term, kind):
        node=self.terms.nodes[term]
        return node[2:] if node[0]=='op' and node[1]==kind else None

    def inverse_of(self, term, other):
        return self.operation(term,NAND)==(other,other)

    def conjunction(self, term):
        pair=self.operation(term,NAND)
        if pair and pair[0]==pair[1]:return self.operation(pair[0],NAND)
        return None

    def nonzero(self, term, operand):
        outer=self.operation(term,EQ)
        if not outer:return False
        for inner,zero in (outer,outer[::-1]):
            if self.terms.value(zero)!=0:continue
            args=self.operation(inner,EQ)
            if args and any(x==operand and self.terms.value(z)==0 for x,z in (args,args[::-1])):
                return True
        return False

    def requires_nonzero(self, condition, operand):
        if self.nonzero(condition,operand):return True
        args=self.conjunction(condition)
        return bool(args and any(self.requires_nonzero(x,operand) for x in args))

    def selections(self, term):
        # select(p,y,n) = NAND(NAND(m,y), NAND(~m,n)), m = ~p + 1.
        pair=self.operation(term,NAND)
        if not pair:return
        for positive,negative in (pair,pair[::-1]):
            lhs=self.operation(positive,NAND);rhs=self.operation(negative,NAND)
            if not lhs or not rhs:continue
            for mask,yes in (lhs,lhs[::-1]):
                for inverse,no in (rhs,rhs[::-1]):
                    if not self.inverse_of(inverse,mask):continue
                    add=self.operation(mask,ADD)
                    if not add:continue
                    for inv,one in (add,add[::-1]):
                        args=self.operation(inv,NAND)
                        if self.terms.value(one)==1 and args and args[0]==args[1]:
                            condition=args[0]
                            # Two's-complement masks select only for Boolean p.
                            if self.masks[condition][0]<=1:yield condition,yes,no

    def at(self, term):
        while len(self.masks)<=term:
            current=len(self.masks)
            super().at(current)
            for condition,yes,no in self.selections(current):
                args=self.operation(yes,ADD)
                if not args:continue
                for count,minus_one in (args,args[::-1]):
                    if self.terms.value(minus_one)!=MASK:continue
                    if not self.requires_nonzero(condition,count):continue
                    # Under the guard, 1 <= count <= possible_one_mask(count).
                    # Thus count-1 cannot wrap. Rounding the upper bound to a
                    # low-bit mask contains every such unsigned result.
                    top=self.masks[count][0]
                    yes_mask=(1<<max(0,top-1).bit_length())-1
                    bound=yes_mask|self.masks[no][0]
                    old_ones,old_zeros=self.masks[current]
                    if bound<old_ones:
                        self.masks[current]=(old_ones&bound,old_zeros)
                        self.refinements.append(dict(term=current,count=count,condition=condition,
                                                     possible_one_mask=bound))
        return self.masks[term]
