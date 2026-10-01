"""The spatial evaluator's own transition has a complete WordCode model."""
import unittest

from gacsca.fixed_rule import spatial_description,spatial_codec,spatial_epoch
from experiments.fixed_rule.certify_spatial_description import check


class SpatialDescription(unittest.TestCase):
    def test_literal_local_equivalence_across_packet_directions(self):
        program=spatial_description.build()
        self.assertEqual((program.inputs,len(program.outputs)),
                         (3*spatial_codec.FIELDS,spatial_codec.FIELDS))
        result=check()
        self.assertTrue(result['passed'])
        self.assertGreater(result['branches']['right_mail'],0)
        self.assertGreater(result['branches']['left_mail'],0)
        self.assertGreater(result['branches']['collision'],0)
        self.assertEqual(spatial_epoch.WIDTH,2334)


if __name__=='__main__':unittest.main()
