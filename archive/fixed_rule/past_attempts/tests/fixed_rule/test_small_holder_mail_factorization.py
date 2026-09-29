from dataclasses import replace
import unittest
from unittest.mock import patch

from gacsca.fixed_rule import small_holder_rule as f, small_holder_core as c, small_holder_program as p
from gacsca.fixed_rule.wordcode import ADD, EQ, LT
from experiments.fixed_rule import certify_small_holder_mail_factorization as proof
from experiments.fixed_rule.audit_small_holder_position_events import evaluate


class MailFactorization(unittest.TestCase):
    def test_raw_controller_independence_and_track_separation(self):
        result = proof.certify_support()
        self.assertEqual(result['controller_outputs_independent_of_all_old_mail'], 45)
        self.assertTrue(result['packet_outputs_track_separable'])

    def test_mail_dependent_controller_mutation_is_rejected(self):
        desc = f.self_description()
        outputs = list(desc.outputs)
        outputs[f.COL['s2_head']] = 7*f.FIELDS + f.COL['s2_lp_valid']
        with self.assertRaises(AssertionError):
            proof.certify_support(replace(desc, outputs=tuple(outputs)))

    def test_cross_track_mutation_is_rejected(self):
        desc = f.self_description()
        outputs = list(desc.outputs)
        outputs[f.COL['s2_lp_data']] = 7*f.FIELDS + f.COL['s2_rp_data']
        with self.assertRaises(AssertionError):
            proof.certify_support(replace(desc, outputs=tuple(outputs)))

    def test_boolean_sum_normalization_and_width_guard(self):
        for width in (1, 2):
            for count in range(1, 6):
                for threshold in range(1, count+1):
                    terms = proof.BooleanTerms(p.base_rom())
                    bit = terms.variable('x', width)
                    total = terms.const(0)
                    for _ in range(count):
                        total = terms.op(ADD, total, bit)
                    predicate = terms.not_(terms.op(LT, total, terms.const(threshold)))
                    for value in range(1 << width):
                        values = evaluate(terms, {'x': value})
                        self.assertEqual(values[predicate], int(count*value >= threshold))
                    if width == 1:
                        self.assertEqual(predicate, bit)
                    else:
                        self.assertNotEqual(predicate, bit)

    def test_every_phase_with_arbitrary_mail(self):
        for phase in (None, *range(8)):
            result = proof.certify_case(phase, proof.clock.regular_intervals()[0])
            self.assertEqual(result['full_raw_output_words'], f.FIELDS*(1 if phase is None else 9))

    def test_discarding_incoming_deliveries_is_rejected(self):
        original = proof.prepare
        def wrong(phase, interval):
            terms, raw, local = original(phase, interval)
            def changed(site):
                result = local(site)
                result['data'] = terms.variable(f'proc_{site}_data', 64)
                return result
            return terms, raw, changed
        with patch.object(proof, 'prepare', side_effect=wrong), self.assertRaises(AssertionError):
            proof.certify_case(None, proof.clock.regular_intervals()[0])


if __name__ == '__main__':
    unittest.main()
