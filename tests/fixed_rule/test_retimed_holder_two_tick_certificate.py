"""Mutation tests for the exact geometry and complete-controller repair proof."""
import unittest
from gacsca.fixed_rule import retimed_holder_rule as f
from gacsca.fixed_rule.wordcode import Program
from experiments.fixed_rule.prove_retimed_holder_two_site_geometry import prove_case
from experiments.fixed_rule.certify_retimed_holder_two_tick_repair import structural


def output_changed(name,wire):
    desc=f.self_description();outputs=list(desc.outputs);outputs[f.COL[name]]=wire
    return Program(desc.inputs,desc.operations,tuple(outputs))


class TwoTickCertificate(unittest.TestCase):
    def test_opposite_geometry_defects_quantified(self):
        result=prove_case((-5,5));self.assertTrue(result['passed']);self.assertEqual(result['independent_bits'],148)

    def test_unrepaired_geometry_output_rejected(self):
        desc=output_changed('f1',7*f.FIELDS+f.COL['f1'])
        with self.assertRaises(AssertionError):prove_case((0,1),desc)

    def test_hidden_controller_input_to_geometry_rejected(self):
        desc=output_changed('age',7*f.FIELDS+f.COL['s2_rb'])
        with self.assertRaisesRegex(ValueError,'dependency'):prove_case((0,1),desc)

    def test_unvoted_controller_output_rejected(self):
        desc=output_changed('s2_rb',7*f.FIELDS+f.COL['s2_rb'])
        with self.assertRaises(AssertionError):structural(desc)

    def test_unvoted_signal_output_rejected(self):
        desc=output_changed('signal',7*f.FIELDS+f.COL['signal'])
        with self.assertRaises(AssertionError):structural(desc)

    def test_inconsistent_backup_routing_rejected(self):
        desc=f.self_description();desc=output_changed('s0_head',desc.outputs[f.COL['s1_head']])
        with self.assertRaisesRegex(AssertionError,'coherent'):structural(desc)

    def test_bad_pair_rejected(self):
        for pair in ((0,0),(-6,1),(0,)):
            with self.assertRaises(ValueError):prove_case(pair)

if __name__=='__main__':unittest.main()
