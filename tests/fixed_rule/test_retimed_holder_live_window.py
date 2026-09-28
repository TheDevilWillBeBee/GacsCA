import unittest
import numpy as np
from gacsca.fixed_rule import retimed_holder_live_window as window
from gacsca.fixed_rule import retimed_holder_rule as f, retimed_holder_quotient as q


class LiveWindow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with np.load('figs/fixed_rule/retimed_holder_active_evaluator_faults_v1.npz', allow_pickle=False) as z:
            cls.state = {k:z['checkpoint_'+k].copy() for k in ('bank','active_rows','counts','flags','signals','age','time')}
            cls.raw = z['checkpoint_raw'].copy()

    def test_every_raw_controller_word_matches_saved_checkpoint(self):
        np.testing.assert_array_equal(window.Window(self.state).cells(np.arange(f.Q)), self.raw)

    def test_cross_colony_copies_use_actual_neighbor(self):
        state = {k:np.concatenate([v,v]) if v.ndim else v.copy() for k,v in self.state.items()}
        # Last logical tail Data of colony zero belongs in backups at the next
        # colony's beginning, not the corresponding tail of colony one.
        state['bank'][0,-1] = 0x123456789ABCDEF0
        for row in state['active_rows'][0,:int(state['counts'][0])]:
            if row[q.COL['address']] == f.Q-1:
                row[q.COL['data']] = state['bank'][0,-1]
        raw = window.Window(state).cells(np.array([0, f.Q]))
        self.assertNotEqual(raw[0,f.COL['s1_data']], raw[1,f.COL['s1_data']])
        self.assertEqual(int(raw[1,f.COL['s1_data']]), 0x123456789ABCDEF0)

    def test_mismatched_active_data_rejected(self):
        state = {k:v.copy() for k,v in self.state.items()}
        state['active_rows'][0,0,q.COL['data']] ^= np.uint64(1)
        with self.assertRaisesRegex(ValueError, 'Data differs'):
            window.Window(state)

    def test_bounded_read(self):
        with self.assertRaisesRegex(ValueError, 'bounded physical'):
            window.Window(self.state).cells(np.arange(65537))


if __name__ == '__main__':
    unittest.main()
