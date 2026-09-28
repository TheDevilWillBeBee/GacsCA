"""Noise generation must preserve its declared distribution and all raw fields."""
import unittest
import numpy as np
from gacsca.fixed_rule import retimed_holder_noise_schedule as noise,retimed_holder_projected as r


class NoiseSchedule(unittest.TestCase):
    def test_reproducible_complete_typed_marks(self):
        args=dict(sites=101,ticks=1000,expected_marks=40,seed=19)
        a=noise.sample(**args);b=noise.sample(**args)
        np.testing.assert_array_equal(a['schedule'],b['schedule']);np.testing.assert_array_equal(a['replacements'],b['replacements'])
        self.assertEqual(a['realized_marks'],int(np.random.default_rng(19).poisson(40)))
        self.assertEqual(a['replacements'].shape,(a['realized_marks'],len(r.SCHEMA)))
        self.assertTrue(np.all(np.diff(a['schedule'][:,0].astype(np.int64))>=0))
        for col,(_,width) in enumerate(r.SCHEMA):
            if width<64:self.assertTrue(np.all(a['replacements'][:,col]<np.uint64(1<<width)))
        self.assertGreater(a['nonempty_probability_per_site_time'],0)

    def test_colliding_marks_are_retained_in_draw_order(self):
        result=noise.sample(sites=2,ticks=2,expected_marks=100,seed=20);rows=result['schedule']
        self.assertGreater(len(rows),4);self.assertLess(len(set(map(tuple,rows[:,:2]))),len(rows))
        self.assertEqual(set(map(int,rows[:,2])),set(range(len(rows))))
        for time in (1,2):self.assertTrue(np.all(np.diff(rows[rows[:,0]==time,2].astype(np.int64))>0))

    def test_zero_rate_and_overflow_do_not_resample(self):
        result=noise.sample(sites=2,ticks=2,expected_marks=0,seed=21)
        self.assertEqual(result['schedule'].shape,(0,3));self.assertEqual(result['replacements'].shape,(0,len(r.SCHEMA)))
        with self.assertRaises(MemoryError):noise.sample(sites=2,ticks=2,expected_marks=10000,seed=21,max_marks=1)

    def test_invalid_domain_rejected(self):
        for changes in (dict(sites=0),dict(ticks=0),dict(expected_marks=float('inf')),dict(expected_marks=-1)):
            args=dict(sites=2,ticks=2,expected_marks=1,seed=0);args.update(changes)
            with self.assertRaises(ValueError):noise.sample(**args)

if __name__=='__main__':unittest.main()
