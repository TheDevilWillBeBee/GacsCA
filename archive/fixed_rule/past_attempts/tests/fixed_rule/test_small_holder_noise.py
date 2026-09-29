import itertools
import unittest
from collections import Counter
import random
import numpy as np
from gacsca.fixed_rule import small_holder_noise as noise,small_holder_projected as r


class Noise(unittest.TestCase):
    def test_uniform_subset_law_exhaustively_on_small_domain(self):
        counts=Counter()
        class Draws:
            def __init__(self,a,b):self.values=iter((a,b))
            def randrange(self,n):
                value=next(self.values);assert 0<=value<n;return value
        for a,b in itertools.product(range(3),range(4)):
            counts[noise.sample_indices(4,2,Draws(a,b))]+=1
        self.assertEqual(set(counts),set(itertools.combinations(range(4),2)))
        self.assertEqual(set(counts.values()),{2})
        # A huge volume uses only seven selected indices, not a dense allocation.
        result=noise.sample_indices(1<<60,7,random.Random(4))
        self.assertEqual(len(set(result)),7);self.assertTrue(all(0<=i<1<<60 for i in result))

    def test_time_order_every_field_reproducibility_and_zero_rate(self):
        a=noise.generate(5,3,78,0);b=noise.generate(5,3,78,0)
        np.testing.assert_array_equal(a.times,np.repeat((1,2,3),5))
        np.testing.assert_array_equal(a.positions,np.tile(np.arange(5),3))
        np.testing.assert_array_equal(a.replacements,b.replacements)
        self.assertEqual(a.replacements.shape,(15,105))
        for row in a.replacements:
            cell=r.decode_cell(row.tolist());self.assertEqual(r.encode_cell(cell),tuple(map(int,row)))
        self.assertEqual(noise.generate(10,100,78,None).replacements.shape,(0,105))
        self.assertFalse(a.replacements.flags.writeable)

    def test_limit_rejects_without_truncation_or_resampling(self):
        with self.assertRaises(noise.EventLimit) as error:noise.generate(5,3,78,0,max_events=14)
        self.assertEqual((error.exception.count,error.exception.limit),(15,14))
        with self.assertRaises(ValueError):noise.generate(1<<62,2,1)
        with self.assertRaises(ValueError):noise.generate(10,2,1,64)


if __name__=='__main__':unittest.main()
