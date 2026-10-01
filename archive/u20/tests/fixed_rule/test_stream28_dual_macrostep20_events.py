"""Regression of an actual decoded upper transition after both physical passes."""
import unittest

from experiments.fixed_rule.run_dual_macrostep20_events import check


class U20LocalMacrostepTest(unittest.TestCase):
    def test_quiet_flags_still_produce_a_dynamic_upper_transition(self):
        result=check(upper_age=0,seed=2026092951,quiet_geometry=True)
        self.assertTrue(result['passed'])
        self.assertEqual(result['early_flag_holds'],{2496:0,2498:0})
        self.assertEqual(result['complete_gather_history_words'],34245)
        self.assertEqual(result['full_literal_ring_step_ages'],
                         [655360,688128,696315,704512,720896,720897,1048575])
        self.assertEqual(result['final_evaluator_packets'],26101)
        self.assertEqual(result['final_evaluator_gate_completions'],14851)
        self.assertEqual(result['final_literal_holder_copy_steps'],595)
        self.assertEqual(result['decoded_upper_words'],119)
        self.assertGreater(result['changed_upper_words'],0)
        self.assertEqual(result['decoded_sha256'],
                         '4a1060b7f9ba6889afa0622ccd9aa6289ad58e0f2f5dfb1d2c79c19e9240cdc9')


if __name__=='__main__':unittest.main()
