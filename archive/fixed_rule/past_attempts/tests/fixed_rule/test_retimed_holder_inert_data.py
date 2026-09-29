import unittest
from gacsca.fixed_rule import retimed_holder_rule as f,retimed_holder_program as p
from gacsca.fixed_rule.wordcode import Program
from experiments.fixed_rule.certify_retimed_holder_inert_data import certify


class InertData(unittest.TestCase):
    def test_complete_actual_support_all_clock_values(self):
        result = certify()
        self.assertEqual(result['unchanged_Data_copies'],15)
        self.assertEqual(result['complete_raw_outputs'],21*f.FIELDS)
        self.assertEqual(result['all_legal_ages'],f.U)

    def test_memory_word_cannot_be_declared_inert(self):
        with self.assertRaises(AssertionError):
            certify((p.layout().info[0],))

    def test_packet_payload_dependency_is_not_misclassified_as_Data(self):
        original = f.self_description()
        outputs = list(original.outputs)
        outputs[f.COL['s2_lp_data']] = 7*f.FIELDS+f.COL['s2_data']
        mutant = Program(original.inputs,original.operations,tuple(outputs))
        with self.assertRaisesRegex(AssertionError,'another output'):
            certify(description=mutant)

    def test_signal_capture_Data_is_not_inert(self):
        with self.assertRaises(AssertionError):
            certify((f.Q-3,))


if __name__ == '__main__':
    unittest.main()
