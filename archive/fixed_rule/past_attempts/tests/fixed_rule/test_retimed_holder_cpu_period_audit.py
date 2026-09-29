"""Negative checks for omissions in the independent saved-state audit."""
from dataclasses import replace
import unittest

import numpy as np

from gacsca.fixed_rule import retimed_holder_rule as f, retimed_holder_core as c
from gacsca.fixed_rule import retimed_holder_projected as r, retimed_holder_program as p
from experiments.fixed_rule.audit_retimed_holder_cpu_periods import check_boundary


class SnapshotAudit(unittest.TestCase):
    def setUp(self):
        # Synthetic audit inputs only; these are not claimed execution evidence.
        self.parent = (r.Cell(address=73, f1=1, s2_head=1, s2_phase=c.READ_B, s2_pc=23),)
        self.data = np.zeros((1, f.Q), dtype=np.uint64)
        self.data[0, list(p.layout().info)] = f.encode_cell(r.lift(self.parent[0]))
        self.right = np.array([1], dtype=np.uint64)

    def test_complete_raw_state_passes(self):
        self.assertEqual(check_boundary(self.data, self.right, self.parent), f.FIELDS)

    def test_controller_omission_rejected(self):
        self.data[0, p.layout().info[f.COL['s2_pc']]] = 0
        with self.assertRaisesRegex(AssertionError, 'raw Info'):
            check_boundary(self.data, self.right, self.parent)

    def test_metadata_substitution_rejected(self):
        self.data[0, p.layout().info[0]] ^= np.uint64(1)
        with self.assertRaisesRegex(AssertionError, 'raw Info'):
            check_boundary(self.data, self.right, self.parent)

    def test_retained_signal_and_nonmem_data_checked(self):
        with self.assertRaisesRegex(AssertionError, 'Signal'):
            check_boundary(self.data, np.array([0], dtype=np.uint64), self.parent)
        address = next(a for a in range(f.Q) if r.record(a)['kind'] != c.MEM)
        self.data[0, address] = 1
        with self.assertRaisesRegex(AssertionError, 'non-MEM'):
            check_boundary(self.data, self.right, self.parent)


if __name__ == '__main__':
    unittest.main()
