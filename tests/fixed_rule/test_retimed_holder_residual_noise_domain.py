import unittest
from gacsca.fixed_rule import retimed_holder_rule as f, retimed_holder_program as p
from gacsca.fixed_rule.wordcode import Program
from experiments.fixed_rule.certify_retimed_holder_residual_noise_domain import certify
from experiments.fixed_rule.audit_retimed_holder_residual_noise import address_counterexample, fresh_noise


class ResidualNoiseDomain(unittest.TestCase):
    def test_arbitrary_independent_clocks_and_incoherent_copies(self):
        row = certify()
        self.assertEqual(row['independent_clock_bits_per_physical_site'], 32)
        self.assertFalse(row['initial_Data_coherence_required'])
        self.assertEqual(row['corrected_Data_copies'], 15)
        self.assertEqual(row['complete_raw_outputs'], 21*f.FIELDS)

    def test_memory_data_is_not_inert(self):
        with self.assertRaises(AssertionError):
            certify((p.layout().info[0],))

    def test_copying_own_data_instead_of_correcting_is_rejected(self):
        original = f.self_description()
        out = list(original.outputs)
        out[f.COL['s2_data']] = 7*f.FIELDS+f.COL['s2_data']
        with self.assertRaisesRegex(AssertionError, 'not majority-corrected'):
            certify(description=Program(original.inputs, original.operations, tuple(out)))

    def test_leaking_data_into_controller_is_rejected(self):
        original = f.self_description()
        out = list(original.outputs)
        out[f.COL['s2_value']] = 7*f.FIELDS+f.COL['s2_data']
        with self.assertRaisesRegex(AssertionError, 'another output'):
            certify(description=Program(original.inputs, original.operations, tuple(out)))

    def test_address_premise_has_scalar_native_counterexample(self):
        row, _ = address_counterexample()
        self.assertEqual(row['actual_output_Signal'], 4)
        self.assertEqual(row['comparison_output_Signal'], 0)

    def test_actual_residual_values_under_repeated_fresh_replacements(self):
        row = fresh_noise(ticks=3)
        self.assertEqual(row['address_preserving_full_state_faults'], 12)
        self.assertTrue(all(x['different_words_outside_selected_Data'] == 0 for x in row['trace']))


if __name__ == '__main__':
    unittest.main()
