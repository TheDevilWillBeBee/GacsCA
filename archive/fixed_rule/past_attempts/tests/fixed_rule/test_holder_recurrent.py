import unittest
import numpy as np
from gacsca.fixed_rule import holder_rule as f,holder_projected as r,holder_program as p,holder_quotient as q,holder_native as native
from gacsca.fixed_rule.holder_recurrent_prefix_world import World

class HolderRecurrent(unittest.TestCase):
    def initial(self):
        with World.encode((r.Cell(),)) as world:a=world.stored
        a[-5:,q.COL['signal']]=[16,8,4,2,1]
        return a
    def test_prior_signals_survive_reset_and_match_full_rule(self):
        state=self.initial();g=p.layout()
        with World(state) as fast,World(state) as slow:
            for ticks in (1,8,91):
                age=fast.time
                points=(0,1,4,100,g.computation_cells-1,f.Q-7,f.Q-3,f.Q-1)
                expected={a:r.project(native.local_step(tuple(r.lift(fast.cell(0,(a+j)%f.Q)) for j in range(-7,8)))) for a in points}
                fast.run(1);slow.run(1,skip_wait=False,skip_scan=False)
                for a in points:self.assertEqual(fast.cell(0,a),expected[a],(age,a))
                fast.run(ticks);slow.run(ticks,skip_wait=False,skip_scan=False);np.testing.assert_array_equal(fast.stored,slow.stored)
                self.assertEqual(fast.cell(0,f.Q-3).signal,4)
    def test_rejects_incoherent_old_signal(self):
        state=self.initial();state[100,q.COL['signal']]=4
        with self.assertRaises(ValueError):World(state)

if __name__=='__main__':unittest.main()
