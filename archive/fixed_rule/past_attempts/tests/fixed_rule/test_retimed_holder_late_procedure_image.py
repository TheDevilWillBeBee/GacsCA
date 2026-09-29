import unittest
from gacsca.fixed_rule import retimed_holder_rule as f
from gacsca.fixed_rule.wordcode import Program
from experiments.fixed_rule.certify_retimed_holder_late_procedure_image import certify, INTERVALS


class LateImage(unittest.TestCase):
    def test_arbitrary_multihead_images_all_late_phases(self):
        for interval in INTERVALS:
            result = certify(interval)
            self.assertEqual(result['coherent_nonmail_output_words'], 50)
            self.assertTrue(result['shared_Signal_inputs_remain_shared'])
            self.assertTrue(result['zero_output_mail_required_for_full_procedure_image'])

    def test_dropped_controller_replica_is_rejected(self):
        desc = f.self_description()
        outputs = list(desc.outputs)
        outputs[f.COL['s0_pc']] = desc.outputs[f.COL['s1_pc']]
        with self.assertRaisesRegex(AssertionError, 'incoherent output'):
            certify(INTERVALS[0], description=Program(desc.inputs, desc.operations, tuple(outputs)))


if __name__ == '__main__':
    unittest.main()
