import unittest
import numpy as np
from gacsca.fixed_rule import retimed_holder_contextual_flags as adapter
from gacsca.fixed_rule import retimed_holder_live_window as live
from gacsca.fixed_rule import retimed_holder_late_flags as late
from gacsca.fixed_rule import retimed_holder_rule as f, retimed_holder_quotient as q


class ContextualFlags(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with np.load('figs/fixed_rule/retimed_holder_contextual_burst_v1.npz', allow_pickle=False) as z:
            cls.state = {k:z['final_background_'+k].copy() for k in ('bank','active_rows','counts','flags','signals','age','time')}
            cls.positions, cls.values = z['final_positions'].copy(), z['final_values'].copy()

    def test_all_raw_fields_with_cross_boundary_exceptions(self):
        positions = np.array([9*f.Q-1, 9*f.Q], dtype=np.int64)
        values = live.Window(self.state).cells(positions)
        values[:, f.COL['s2_pc']] = [19871, 23]
        values[:, f.COL['s2_data']] = [191, 391]
        actual = adapter.View(self.state, positions, values)
        probe = np.arange(9*f.Q-8, 9*f.Q+8)
        expected = live.Window(self.state).cells(probe)
        expected[7:9] = values
        np.testing.assert_array_equal(actual.cells(probe), expected)

    def test_two_colony_flag_view_matches_existing_complete_renderer(self):
        state = {k:v.copy() for k,v in self.state.items()}
        for k in ('bank','active_rows','counts','signals'):
            state[k] = state[k][8:10].copy()
        state['flags'] = state['flags'][8*f.Q//64:10*f.Q//64].copy()
        pos = np.array([0, f.Q-1, f.Q, 2*f.Q-1], dtype=np.int64)
        for p in pos:
            state['flags'][p//64] |= np.uint64(1) << np.uint64(p%64)
        for col, count in enumerate(state['counts']):
            for row in state['active_rows'][col, :int(count)]:
                p = col*f.Q+int(row[q.COL['address']])
                for k, name in enumerate(('f1','f2')):
                    row[q.COL[name]] = (state['flags'][p//64,k] >> np.uint64(p%64)) & np.uint64(1)
        expected = late.render(state)
        actual = adapter.View(state)
        for col in range(2):
            np.testing.assert_array_equal(actual.cells(np.arange(col*f.Q,(col+1)*f.Q)), expected[col*f.Q:(col+1)*f.Q])

    def test_saved_full_exception_rows_retained(self):
        view = adapter.View(self.state,self.positions,self.values)
        np.testing.assert_array_equal(view.cells(self.positions),self.values)

    def test_inconsistent_active_flags_rejected(self):
        state = dict(self.state, active_rows=self.state['active_rows'].copy())
        state['active_rows'][0,0,q.COL['f1']] ^= np.uint64(1)
        with self.assertRaisesRegex(ValueError,'disagree'):
            adapter.View(state)

    def test_incomplete_exception_state_rejected(self):
        with self.assertRaisesRegex(ValueError,'complete exception'):
            adapter.View(self.state,self.positions,self.values[:,:-1])


if __name__ == '__main__':
    unittest.main()
