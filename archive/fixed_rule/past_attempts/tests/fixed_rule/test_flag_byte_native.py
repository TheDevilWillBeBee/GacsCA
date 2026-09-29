import random
import unittest
import numpy as np
from gacsca.fixed_rule.flag_byte_native import Evolution,library
from gacsca.fixed_rule.flag_byte_hash import leaf_step,evolve,WORDS,MASK
from gacsca.fixed_rule.delivery_rule import Q


class FlagByteNativeTests(unittest.TestCase):
    def test_all_tag_types_and_random_physical_leaves_match_python(self):
        rng=random.Random(552);lib=library()
        for _ in range(10000):
            cells=[rng.getrandbits(18) for _ in range(3)]
            self.assertEqual(int(lib.fh_local(*cells)),leaf_step(*cells))

    def test_full_causal_results_and_exported_proof_match_python(self):
        rows=[(Q//128,(1<<64)-1,(1<<64)-1),(Q//64,0,(1<<64)-1)]
        for ticks in (0,1,17,1000,65536):
            e,initial,final=evolve(rows,1,98*Q,ticks)
            with Evolution(rows,1,98*Q,ticks) as native:
                for position in (*range(20),*range(WORDS//2-20,WORDS//2+20),*range(WORDS-20,WORDS)):
                    self.assertEqual(native.at(position),e.at(final,position),(ticks,position))
                nodes,queries=native.proof();info=native.info
                self.assertEqual(len(nodes),info['nodes']);self.assertEqual(len(queries),info['queries'])
                for node,t,out in queries:
                    self.assertGreaterEqual(int(nodes[node,0]),2);self.assertLessEqual(int(t),1<<(int(nodes[node,0])-2))
                    self.assertEqual(int(nodes[out,0]),int(nodes[node,0])-1)
                with self.assertRaises(ValueError):native.at(1<<63)
            with self.assertRaises(ValueError):native.at(0)


if __name__=='__main__':unittest.main()
