"""Saved GPU evidence must retain controller Info and physical Signal patterns."""
from pathlib import Path
import unittest
import numpy as np
from experiments.fixed_rule.audit_compact16_holder_gpu_periods import audit, check_boundary
from gacsca.fixed_rule import compact16_holder_rule as f, compact16_holder_projected as r
from gacsca.fixed_rule import compact16_holder_program as p, compact16_holder_packed as packed
from gacsca.fixed_rule import compact16_holder_records as q


class Evidence(unittest.TestCase):
    def test_successive_active_execution(self):
        result = audit('figs/fixed_rule/compact16_holder_gpu_active_v1.json')
        self.assertTrue(result['sustained_upper_arithmetic'])
        self.assertTrue(all(row['represented_controller_words_changed'] > 0 for row in result['periods']))

    def test_missing_controller_or_signal_rejected(self):
        with np.load('figs/fixed_rule/compact16_holder_gpu_active_v1.npz', allow_pickle=False) as saved:
            before = r.cells_from_array(saved['initial_upper']); n = len(before)
            expected = tuple(r.local_step(tuple(before[(col+j)%n] for j in f.NEIGHBORHOOD)) for col in range(n))
            args = [saved[name][0].copy() for name in ('boundary_banks', 'boundary_sparse', 'boundary_counts', 'boundary_right', 'boundary_left')]
            check_boundary(*args, expected)
            at = p.layout().info[f.COL['s2_head']]; original = args[0][n//2+1, at]
            self.assertEqual(original, 1)
            args[0][n//2+1, at] = 0
            with self.assertRaises(AssertionError): check_boundary(*args, expected)
            args[0][n//2+1, at] = original
            for col, count in enumerate(args[2]):
                rows = packed.unpack(args[1][col, :int(count)])
                matches = np.flatnonzero(rows[:, q.COL['signal']])
                if len(matches):
                    rows[matches[0], q.COL['signal']] = 0
                    args[1][col, :int(count)] = packed.pack(rows)
                    break
            else: self.fail('fixture needs retained Signal bits')
            with self.assertRaises(AssertionError): check_boundary(*args, expected)


if __name__ == '__main__': unittest.main()
