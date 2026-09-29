import unittest
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import retimed_holder_late_flags as late
from gacsca.fixed_rule import retimed_holder_active_snapshot as active
from gacsca.fixed_rule import retimed_holder_rule as f, retimed_holder_quotient as q


class LateFlags(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = Path('figs/fixed_rule/retimed_holder_poisson_burst_8192_v1.npz')
        with np.load(path, allow_pickle=False) as saved:
            cls.state = {k:saved['final_'+k].copy() for k in ('bank', 'active_rows', 'counts', 'flags', 'signals', 'age', 'time')}

    def test_zero_flags_reconstruct_complete_active_state(self):
        np.testing.assert_array_equal(late.render(self.state), active.render(self.state))

    def test_flags_and_all_controller_words_are_retained(self):
        state = {k:v.copy() for k,v in self.state.items()}
        positions = (0, 9599, f.Q-1)
        for pos in positions:
            state['flags'][pos//64, :] |= np.uint64(1) << np.uint64(pos%64)
        for row in state['active_rows'][0, :int(state['counts'][0])]:
            pos = int(row[q.COL['address']])
            for index, name in enumerate(('f1', 'f2')):
                row[q.COL[name]] = (state['flags'][pos//64, index] >> np.uint64(pos%64)) & np.uint64(1)
        expected = active.render(self.state)
        expected[list(positions), f.COL['f1']] = 1
        expected[list(positions), f.COL['f2']] = 1
        np.testing.assert_array_equal(late.render(state), expected)

    def test_inconsistent_active_flag_record_rejected(self):
        state = {k:v.copy() for k,v in self.state.items()}
        state['active_rows'][0, 0, q.COL['f1']] ^= np.uint64(1)
        with self.assertRaisesRegex(ValueError, 'disagree'):
            late.render(state)

    def test_forcing_domain_rejected(self):
        state = dict(self.state, age=np.array(f.WF_START, dtype=np.uint64))
        with self.assertRaisesRegex(ValueError, 'late nonforcing'):
            late.render(state)


if __name__ == '__main__':
    unittest.main()
