"""The changed 8Q rule is described, routed, and physically evaluated."""
import unittest

from gacsca.fixed_rule import spatial_epoch8 as spatial
from gacsca.fixed_rule import stream28_compact_vote8 as physical
from experiments.fixed_rule.certify_spatial_description8 import check as spatial_check
from experiments.fixed_rule.certify_stream28_compact_vote8 import check as full_check
from experiments.fixed_rule.audit_compact8_output_endpoints import check as output_check
from experiments.fixed_rule.replay_compact8_numpy import replay


class CompactEightQVertical(unittest.TestCase):
    def test_changed_rule_description_and_late_hold(self):
        self.assertEqual((spatial.PERIOD,spatial.WIDTH,physical.WIDTH),
                         (65536,2375,6465))
        self.assertTrue(spatial_check()['passed'])
        self.assertTrue(full_check()['passed'])
        output=output_check()
        self.assertEqual(output['literal_source_steps'],119)
        self.assertEqual(output['literal_fivefold_holder_steps'],595)

    def test_continuous_evaluator_period(self):
        result=replay()
        self.assertTrue(result['passed'])
        self.assertEqual(result['packet_emissions'],[25981])
        self.assertEqual(result['packet_deliveries'],[25981])
        self.assertEqual(result['gate_completions'],[14782])
        self.assertEqual(result['projected_output_words_checked'],119)
        self.assertGreater(result['literal_local_site_steps'],70000)


if __name__=='__main__':unittest.main()
