import random
import unittest
from gacsca.fixed_rule.flag_hash import Engine,leaf_step,MASK,FIRST
from gacsca.fixed_rule.flag_words import library,pointer
import numpy as np


class FlagHashTests(unittest.TestCase):
    def test_leaf_matches_existing_complete_rule_word_kernel(self):
        rng=random.Random(743);lib=library()
        for _ in range(1000):
            left,center=rng.getrandbits(64),rng.getrandbits(64);first=rng.randrange(2)
            inputs=np.array([0,left,0,center,0,rng.getrandbits(64)],dtype=np.uint64);out=np.empty(2,dtype=np.uint64)
            lib.fw_word(pointer(inputs),pointer(out),first,0,0,0,0)
            self.assertEqual(leaf_step(left,center|(FIRST if first else 0)),int(out[1])|(FIRST if first else 0))
            self.assertEqual(int(out[0]),0)

    def test_causal_half_recursion_matches_every_literal_word(self):
        rng=random.Random(647)
        for level in range(1,8):
            values=[rng.getrandbits(64)|(FIRST if i%13==0 else 0) for i in range(1<<level)]
            engine=Engine();nodes=[engine.leaf(value) for value in values]
            while len(nodes)>1:nodes=[engine.join(a,b) for a,b in zip(nodes[::2],nodes[1::2])]
            root=nodes[0]
            for ticks in (0,1,(1<<level)//3,1<<(level-1)):
                expected=values[:]
                for _ in range(ticks):expected=[leaf_step(expected[i-1] if i else 0,v) for i,v in enumerate(expected)]
                out=engine.half(root,ticks)
                self.assertEqual([engine.at(out,i) for i in range(1<<(level-1))],expected[1<<(level-1):])

    def test_periodic_blocks_and_full_advance_preserve_boundary_tags(self):
        e=Engine();pattern=(MASK,0,0xF3F9FCFE7F3F9FCF)
        root=e.periodic(pattern,7);root=e.set(root,0,e.at(root,0)|FIRST);root=e.set(root,64,e.at(root,64)|FIRST)
        original=[e.at(root,i) for i in range(128)]
        for ticks in (1,17,129):
            expected=original[:]
            for _ in range(ticks):expected=[leaf_step(expected[i-1] if i else 0,v) for i,v in enumerate(expected)]
            out=e.advance(root,ticks)
            self.assertEqual([e.at(out,i) for i in range(128)],expected)
            self.assertEqual([i for i in range(128) if e.at(out,i)&FIRST],[0,64])


if __name__=='__main__':unittest.main()
