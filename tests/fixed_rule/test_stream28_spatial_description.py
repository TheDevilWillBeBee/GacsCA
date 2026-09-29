"""The combined rule description includes controller and evaluator dynamics."""
import unittest

from gacsca.fixed_rule import stream28_spatial_description as description
from gacsca.fixed_rule import stream28_spatial_overlay as physical
from experiments.fixed_rule.certify_stream28_spatial_description import check


class CombinedDescription(unittest.TestCase):
    def test_complete_literal_local_equivalence(self):
        program=description.build()
        self.assertEqual((program.inputs,len(program.outputs)),
                         (15*physical.FIELDS,physical.FIELDS))
        result=check()
        self.assertTrue(result['passed'])
        self.assertGreater(result['branches']['capture'],0)
        self.assertGreater(result['branches']['running'],0)
        self.assertGreater(result['branches']['hold'],0)
        self.assertGreater(result['branches']['info'],0)
        self.assertGreater(result['branches']['clear'],0)
        self.assertEqual(program.digest(),result['description_sha256'])


if __name__=='__main__':unittest.main()
