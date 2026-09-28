import unittest
import numpy as np
from gacsca.fixed_rule import retimed_holder_rule as f, retimed_holder_literal_cone as cone
from experiments.fixed_rule.audit_retimed_holder_residual_noise import VALUES
from experiments.fixed_rule.audit_retimed_holder_residual_reactivation import continue_pair


def entry():
    a = 30960
    positions = np.arange(a-72, a+75)
    comparison = np.zeros((147, f.FIELDS), dtype=np.uint64)
    comparison[:, f.COL['address']] = positions
    cone.normalize(comparison)
    actual = comparison.copy()
    for offset, value in enumerate(VALUES):
        for d in f.OFFSETS:
            actual[positions+d == a+offset, f.COL[f's{d+2}_data']] = value
    return actual, comparison, positions, a


class ResidualReactivation(unittest.TestCase):
    def test_actual_even_value_enters_controller_then_pair_couples(self):
        row, arrays = continue_pair(*entry())
        self.assertEqual(row['fresh_full_state_marks'], 9)
        self.assertEqual(row['trace'][3]['differing_controller_words'], 1)
        index = np.flatnonzero(arrays['tick4_positions'] == 30960)[0]
        self.assertEqual(int(arrays['tick4_actual'][index, f.COL['s4_value']]), VALUES[1])
        self.assertTrue(row['paired_rejoined'])
        self.assertFalse(row['fault_free_rejoined'])

    def test_no_geometry_faults_leave_residue_separated(self):
        row, _ = continue_pair(*entry(), geometry=False)
        self.assertEqual(row['fresh_full_state_marks'], 3)
        self.assertFalse(row['paired_rejoined'])
        self.assertTrue(all(x['differing_controller_words'] == 0 for x in row['trace']))

    def test_no_injected_controller_prevents_controller_read(self):
        row, _ = continue_pair(*entry(), controller=False)
        self.assertEqual(row['fresh_full_state_marks'], 6)
        self.assertTrue(all(x['differing_controller_words'] == 0 for x in row['trace']))

    def test_early_snapshots_are_not_mutated_by_later_faults(self):
        _, arrays = continue_pair(*entry())
        for tick in (1, 2):
            positions = arrays[f'tick{tick}_positions']
            for offset, value in enumerate(VALUES):
                for d in f.OFFSETS:
                    i = np.flatnonzero(positions+d == 30960+offset)[0]
                    self.assertEqual(int(arrays[f'tick{tick}_actual'][i, f.COL[f's{d+2}_data']]), value)

    def test_short_or_shifted_causal_window_rejected(self):
        actual, comparison, positions, anchor = entry()
        with self.assertRaisesRegex(ValueError, 'causal window'):
            continue_pair(actual[:-1], comparison[:-1], positions[:-1], anchor)
        with self.assertRaisesRegex(ValueError, 'causal window'):
            continue_pair(actual, comparison, positions, anchor+1)


if __name__ == '__main__':
    unittest.main()
