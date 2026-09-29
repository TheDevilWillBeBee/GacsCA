import unittest
import numpy as np
from gacsca.fixed_rule import compact16_holder_rule as f, compact16_holder_core as c
from gacsca.fixed_rule import compact16_holder_program as p, compact16_holder_projected as r
from gacsca.fixed_rule import compact16_holder_cpu_gather as gather
from experiments.fixed_rule import audit_compact16_holder_cpu_periods as audit


class ExecutionAudit(unittest.TestCase):
    def test_sparse_packet_targets_match_actual_SENDs_and_exclude_voted_operands(self):
        g = p.layout()
        actual = {op.b for op in g.instructions if op.kind == c.SEND}
        self.assertEqual(actual, set(gather.protected_targets()))
        self.assertFalse(actual.intersection(g.info))
        self.assertFalse(actual.intersection(g.hold))
        self.assertFalse(actual.intersection(g.votes))
        for wire in g.gathered_inputs:
            for stage in range(3):
                at = g.history(stage, wire//f.FIELDS-7, wire%f.FIELDS)
                self.assertEqual(gather.protected_target(at), wire//f.FIELDS != 7)
        dense = {a for a in range(8, min(f.Q, 8+4*15*f.FIELDS))
                 if (a-8)%4 != 1 and ((a-8)//4)//f.FIELDS != 7}
        self.assertNotEqual(dense, actual)

    def test_saved_boundary_check_rejects_missing_controller_signal_flags_or_geometry(self):
        parent = r.Cell(address=7, age=123, s2_head=1, s2_pc=99, f1=1, f2=1)
        data = np.zeros((1, f.Q), dtype=np.uint64)
        data[0, list(p.layout().info)] = f.encode_cell(r.lift(parent))
        right, left = np.ones(1, dtype=np.uint64), np.ones(1, dtype=np.uint64)
        flags = np.zeros((f.Q//64, 2), dtype=np.uint64)
        self.assertEqual(audit.check_boundary(data, right, left, flags, (parent,)), f.FIELDS)
        for mode in ('controller', 'metadata', 'right', 'left', 'flags', 'nonmem', 'short'):
            d, a, b, q = data.copy(), right.copy(), left.copy(), flags.copy()
            if mode == 'controller':
                d[0, p.layout().info[f.COL['s2_pc']]] = 0
            elif mode == 'metadata':
                d[0, p.layout().info[f.COL['p3_kind']]] ^= np.uint64(1)
            elif mode == 'right':
                a[0] = 0
            elif mode == 'left':
                b[0] = 0
            elif mode == 'flags':
                q[0, 1] = 1
            elif mode == 'nonmem':
                d[0, p.layout().memory_count] = 1
            else:
                d = d[:, :-1]
            with self.assertRaises(AssertionError, msg=mode):
                audit.check_boundary(d, a, b, q, (parent,))


if __name__ == '__main__':
    unittest.main()
