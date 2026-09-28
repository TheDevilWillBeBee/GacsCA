import unittest
from gacsca.fixed_rule import retimed_holder_rule as f
from gacsca.fixed_rule.wordcode import Program
from experiments.fixed_rule.certify_retimed_holder_empty_tail_interior import certify


class EmptyTail(unittest.TestCase):
    def test_only_three_empty_records_needed(self):
        self.assertEqual(certify()['complete_zero_controller_copies'], 45)

    def test_first_marker_can_create_a_head_at_reset(self):
        with self.assertRaisesRegex(AssertionError, 'controller birth'):
            certify(zero_first=False)

    def test_hidden_distance_two_controller_read_rejected(self):
        desc = f.self_description()
        outputs = list(desc.outputs)
        outputs[f.COL['s2_pc']] = 9*f.FIELDS+f.COL['s2_pc']
        with self.assertRaisesRegex(AssertionError, 'controller birth'):
            certify(description=Program(desc.inputs, desc.operations, tuple(outputs)))


if __name__ == '__main__':
    unittest.main()
