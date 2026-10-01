"""Independent continuous dynamics for the 4Q spatial output evaluator."""
import unittest

from gacsca.fixed_rule import spatial_epoch as physical
from experiments.fixed_rule.replay_spatial_output_numpy import replay


class SpatialContinuousReplay(unittest.TestCase):
    def test_two_full_periods_under_one_fixed_rule(self):
        transition=physical.local_step
        width=physical.WIDTH
        result=replay(2)
        self.assertTrue(result['passed'])
        self.assertEqual(result['ticks_evolved'],2*physical.PERIOD)
        self.assertEqual(result['physical_site_ticks'],2*physical.PERIOD*physical.Q)
        self.assertEqual(result['packet_emissions'],[19342,19342])
        self.assertEqual(result['packet_deliveries'],[19342,19342])
        self.assertEqual(result['gate_completions'],[11065,11065])
        self.assertEqual(result['output_words_checked'],308)
        self.assertEqual(result['literal_local_site_steps'],6*physical.Q)
        self.assertIs(physical.local_step,transition)
        self.assertEqual(physical.WIDTH,width)

    def test_latched_outputs_remove_output_packets_without_new_rule(self):
        transition=physical.local_step;width=physical.WIDTH
        result=replay(2,latch_outputs=True)
        self.assertEqual(result['output_mode'],'latch')
        self.assertEqual(result['packet_emissions'],[19237,19237])
        self.assertEqual(result['packet_deliveries'],[19237,19237])
        self.assertEqual(result['gate_completions'],[11065,11065])
        self.assertEqual(result['output_words_checked'],308)
        self.assertEqual(result['literal_local_site_steps'],6*physical.Q)
        self.assertIs(physical.local_step,transition)
        self.assertEqual(physical.WIDTH,width)

    def test_direct_hold_outputs_replay_for_two_complete_periods(self):
        transition=physical.local_step;width=physical.WIDTH
        result=replay(2,output_layout='hold_left')
        self.assertEqual(result['output_mode'],'hold_left')
        self.assertEqual(result['packet_emissions'],[19391,19391])
        self.assertEqual(result['packet_deliveries'],[19391,19391])
        self.assertEqual(result['gate_completions'],[11065,11065])
        self.assertEqual(result['output_words_checked'],308)
        self.assertEqual(result['literal_local_site_steps'],6*physical.Q)
        self.assertIs(physical.local_step,transition)
        self.assertEqual(physical.WIDTH,width)


if __name__=='__main__':unittest.main()
