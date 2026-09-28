import random
import unittest
from experiments.fixed_rule.word_temporal_capacity import majority,composition
from gacsca.fixed_rule.wordcode import MASK,arithmetic,LIT
from gacsca.fixed_rule import word_rule as f


class WordTemporalCapacityTests(unittest.TestCase):
    def test_bitwise_majority_not_whole_word_voting(self):
        rng=random.Random(2541)
        for a in (0,1,MASK,0xFEDCBA9876543210):
            for b in (0,1,MASK,rng.getrandbits(64)):
                for c in (0,1,MASK,rng.getrandbits(64)):
                    self.assertEqual(majority(a,b,c),(a&b)|(a&c)|(b&c))
        self.assertEqual(majority(3,5,6),7) # all three whole words differ
        for _ in range(32):
            a,b=rng.getrandbits(64),rng.getrandbits(64)
            for row in ((a,a,b),(a,b,a),(b,a,a)):self.assertEqual(majority(*row),a)

    def test_composed_descriptor_operates_on_voted_raw_words(self):
        layout,result=composition();desc=f.self_description();rng=random.Random(2542)
        cells=[f.Cell(**{n:rng.randrange(1<<w) for n,w in f.SCHEMA}) for _ in range(11)]
        good=[x for cell in cells for x in f.encode_cell(cell)]
        corrupt=[x^MASK for x in good]
        for histories in ((good,good,corrupt),(good,corrupt,good),(corrupt,good,good)):
            mem=[0]*layout.memory_count;mem[:3*desc.inputs]=sum((list(h) for h in histories),[])
            count=result['vote_operations']+result['descriptor_operations']
            for op in layout.instructions[:count+f.FIELDS]:
                mem[op.d]=op.a if op.kind==LIT else arithmetic(op.kind,mem[op.a],mem[op.b])
            hold=3*desc.inputs+count
            self.assertEqual(tuple(mem[hold:hold+f.FIELDS]),desc.evaluate(good))
        self.assertEqual(result['vote_operations'],6*desc.inputs)


if __name__=='__main__':unittest.main()
