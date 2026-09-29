import random
import unittest
import numpy as np
from gacsca.fixed_rule.flag_pair_hash import Engine,leaf_step,segments_from_words,evolve,FIRST,LAST,MASK,WORDS
from gacsca.fixed_rule.flag_words import library,pointer,World
from gacsca.fixed_rule import delivery_rule as r


class FlagPairHashTests(unittest.TestCase):
    def test_leaf_matches_full_packed_local_rule_with_arbitrary_edge_tags(self):
        rng=random.Random(744);lib=library()
        for _ in range(1000):
            cells=[rng.getrandbits(128) for _ in range(3)];tag=rng.randrange(4)<<128;cells[1]|=tag
            values=np.array([v for c in cells for v in (c&MASK,(c>>64)&MASK)],dtype=np.uint64);out=np.empty(2,dtype=np.uint64)
            lib.fw_word(pointer(values),pointer(out),bool(tag&FIRST),bool(tag&LAST),0,0,0)
            self.assertEqual(leaf_step(*cells),int(out[0])|(int(out[1])<<64)|tag)

    def test_variable_time_center_matches_literal_physical_updates(self):
        rng=random.Random(332)
        for level in range(2,8):
            values=[rng.getrandbits(128)|(rng.randrange(4)<<128) for _ in range(1<<level)];e=Engine();nodes=[e.leaf(v) for v in values]
            while len(nodes)>1:nodes=[e.join(a,b) for a,b in zip(nodes[::2],nodes[1::2])]
            root=nodes[0];quarter=1<<(level-2)
            for ticks in (0,1,quarter//3,quarter):
                expected=values[:]
                for _ in range(ticks):expected=[leaf_step(expected[i-1] if i else 0,v,expected[i+1] if i+1<len(expected) else 0) for i,v in enumerate(expected)]
                result=e.center(root,ticks)
                self.assertEqual([e.at(result,i) for i in range(2*quarter)],expected[quarter:3*quarter])

    def test_actual_ring_periodicity_and_all_colony_boundary_words(self):
        rows=[(WORDS//2,MASK,MASK),(WORDS,0,MASK),(2*WORDS,MASK,0)]
        segments=segments_from_words(rows,2)
        e=Engine();root=e.periodic_segments(segments,21,-123)
        for i in (0,122,123,123+WORDS-1,123+WORDS,123+2*WORDS,1<<20):
            pos=(i-123)%(2*WORDS);value=next(v for end,v in segments if pos<end)
            self.assertEqual(e.at(root,i),value)
        engine,initial,final=evolve(rows,2,98*r.Q,137)
        with World((0,0),(0,0),age=98*r.Q,runs=rows) as world:
            world.run(137);output=world.runs
            for word in (*range(12),*range(WORDS-12,WORDS+12),*range(2*WORDS-12,2*WORDS),WORDS//2-1,WORDS//2):
                k=int(np.searchsorted(output[:,0],word,side='right'));v=engine.at(final,word)
                self.assertEqual(v&MASK,int(output[k,1]));self.assertEqual((v>>64)&MASK,int(output[k,2]))
        with self.assertRaises(ValueError):evolve(rows,2,98*r.Q-1,1)


if __name__=='__main__':unittest.main()
