import unittest
from gacsca.fixed_rule.word_bdd import BDD
from gacsca.fixed_rule.wordcode import NAND,ADD,SHR,EQ,LT,arithmetic

class ExactWordBDD(unittest.TestCase):
    def test_exhaustive_four_bit_operations(self):
        b=BDD(8);left=tuple(b.variable(i) for i in range(4));right=tuple(b.variable(4+i) for i in range(4))
        for op in (NAND,ADD,SHR,EQ,LT):
            out=b.arithmetic(op,left,right)
            for a in range(16):
                for c in range(16):
                    got=sum(b.value(bit,a|(c<<4))<<i for i,bit in enumerate(out))
                    self.assertEqual(got,arithmetic(op,a,c)&15,(op,a,c))
    def test_reduction_and_witness(self):
        b=BDD(4);x,y=b.variable(0),b.variable(1)
        self.assertEqual(b.and_(x,x),x);self.assertEqual(b.xor(x,x),0)
        self.assertEqual(b.or_(b.and_(x,y),b.and_(x,b.inv(y))),x)
        term=b.and_(x,b.inv(y));w=b.witness(term);self.assertEqual(b.value(term,w),1)
        self.assertIsNone(b.witness(0))

if __name__=='__main__':unittest.main()
