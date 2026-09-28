import unittest
from gacsca.fixed_rule import retimed_holder_rule as f, retimed_holder_core as c
from gacsca.fixed_rule import retimed_holder_program as p
from gacsca.fixed_rule.retimed_holder_literal_cone import rom
from gacsca.fixed_rule.wordcode import Program
from experiments.fixed_rule.certify_retimed_holder_late_confinement import cut, tail_edges, no_head_birth, INTERVALS


class LateConfinement(unittest.TestCase):
    def test_all_late_clock_cases_and_controller_birth(self):
        for interval in INTERVALS:
            result = cut(interval)
            self.assertEqual(result['nonmail_raw_outputs_checked'], 2508)
            self.assertEqual(result['conditional_zero_mail_outputs'], 880)
            self.assertTrue(result['arbitrary_Flag1'])
            self.assertTrue(result['arbitrary_shared_raw_Signals'])
            self.assertEqual(tail_edges(interval)['zero_controller_outputs'], 18)
        self.assertEqual(no_head_birth()['zero_controller_outputs'], 45)

    def test_missing_first_marker_breaks_trapping(self):
        table = rom().copy()
        table[0, c.STATIC.index('first')] = 0
        with self.assertRaisesRegex(AssertionError, 'escaped into empty tail'):
            tail_edges(INTERVALS[0], fixed_rom=table)

    def test_missing_last_marker_breaks_trapping(self):
        table = rom().copy()
        table[len(p.base_rom())-1, c.STATIC.index('last')] = 0
        with self.assertRaisesRegex(AssertionError, 'escaped into empty tail'):
            tail_edges(INTERVALS[0], fixed_rom=table)

    def test_unconfined_tail_controller_breaks_separation(self):
        with self.assertRaisesRegex(AssertionError, 'foreign mutable dependence'):
            cut(INTERVALS[0], restrict_tail=False)

    def test_neighbor_Data_mutant_breaks_separation(self):
        original = f.self_description()
        outputs = list(original.outputs)
        outputs[f.COL['s2_data']] = 6*f.FIELDS+f.COL['s2_data']
        with self.assertRaisesRegex(AssertionError, 'foreign mutable dependence'):
            cut(INTERVALS[0], description=Program(original.inputs, original.operations, tuple(outputs)))


if __name__ == '__main__':
    unittest.main()
