"""Known-bit abstraction soundness and complete-rule Address range."""
import random
import unittest

from gacsca.fixed_rule import small_holder_rule as f, small_holder_program as p
from gacsca.fixed_rule.wordcode import NAND,ADD,SHR,EQ,LT,MASK,arithmetic
from experiments.fixed_rule.certify_small_holder_rom_dataflow import Terms
from experiments.fixed_rule.certify_small_holder_meta_query_bounds import KnownBits


class QueryBounds(unittest.TestCase):
    def test_masked_query_and_unbounded_word_are_distinguished(self):
        t=Terms(p.base_rom());x=t.intern(('input',0,'x',15));wide=t.intern(('input',0,'wide',64))
        q=t.band(t.op(ADD,x,t.const(MASK-4)),t.const(f.Q-1));bounds=KnownBits(t)
        self.assertLess(bounds.valid_query(q),f.Q)
        with self.assertRaisesRegex(AssertionError,'exceeds certified Address'):bounds.valid_query(wide)

    def test_complete_descriptor_Address_is_bounded(self):
        t=Terms(p.base_rom())
        inputs=tuple(t.intern(('input',col,name,width)) for col in range(15) for name,width in f.SCHEMA)
        outputs=t.expression(f.self_description(),inputs)
        self.assertLess(KnownBits(t).valid_query(outputs[f.COL['address']]),f.Q)

    def test_known_masks_contain_concrete_arithmetic_values(self):
        t=Terms(p.base_rom());x=t.intern(('input',0,'x',8));y=t.intern(('input',0,'y',64))
        terms=[x,y]
        for op in (NAND,ADD,SHR,EQ,LT):terms.append(t.op(op,x,y))
        terms.extend((t.band(t.op(ADD,x,t.const(MASK)),t.const(f.Q-1)),
                      t.op(SHR,y,t.const(63)),t.op(SHR,y,t.const(64)),
                      t.op(NAND,t.op(NAND,x,y),t.op(NAND,x,y))))
        bound=KnownBits(t);masks=[bound.at(term) for term in terms];rng=random.Random(2026092614)
        for a,b in [(0,0),(255,MASK),(1,64),(255,63)]+[(rng.randrange(256),rng.getrandbits(64)) for _ in range(100)]:
            values=[]
            for node in t.nodes:
                if node[0]=='input':value=a if node[2]=='x' else b
                elif node[0]=='const':value=node[1]
                else:value=arithmetic(node[1],values[node[2]],values[node[3]])
                values.append(value)
            for term,(ones,zeros) in zip(terms,masks):
                self.assertEqual(values[term] & (MASK^ones),0)
                self.assertEqual((MASK^values[term]) & (MASK^zeros),0)


if __name__=='__main__':unittest.main()
