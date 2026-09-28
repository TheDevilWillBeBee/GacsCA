import unittest
import numpy as np
from gacsca.fixed_rule import holder_rule as f,holder_projected as r,holder_program as p,holder_quotient as q,holder_snapshot as snapshot
from gacsca.fixed_rule.holder_recurrent_prefix_world import World

class Snapshot(unittest.TestCase):
    def test_cold_state_and_lossless_complete_endpoint(self):
        top=(r.Cell(s2_data=17),r.Cell(address=100,age=19,s2_phase=3,s4_lp_data=123))
        expected=snapshot.cold(top)
        with World.encode(top) as world:np.testing.assert_array_equal(expected,world.stored)
        with World(expected) as world:
            saved=snapshot.collapse(world);np.testing.assert_array_equal(snapshot.expand(saved),world.stored)
            world.run(1)
            with self.assertRaisesRegex(ValueError,'head'):snapshot.collapse(world)
    def test_data_signal_are_not_reencoded(self):
        state=snapshot.cold((r.Cell(),));rng=np.random.default_rng(193);state[:,q.COL['data']]=rng.integers(0,2**64-1,len(state),dtype=np.uint64);state[-5:,q.COL['signal']]=[16,8,4,2,1];state[:,q.COL['age']]=80*f.Q
        with World(state) as world:
            world.run(100);np.testing.assert_array_equal(snapshot.expand(snapshot.collapse(world)),world.stored)

if __name__=='__main__':unittest.main()
