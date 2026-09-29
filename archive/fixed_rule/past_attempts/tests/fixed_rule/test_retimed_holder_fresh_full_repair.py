import unittest
import numpy as np
from gacsca.fixed_rule import retimed_holder_rule as f, retimed_holder_core as c
from gacsca.fixed_rule.wordcode import Program
from experiments.fixed_rule.certify_retimed_holder_geometry_procedure_effects import certify_effects,certify_zero
from experiments.fixed_rule.join_retimed_holder_fresh_full_repair import neighbor_static_independence,healthy_heads,check_zero_neighborhoods


class FreshFullRepair(unittest.TestCase):
    def test_complete_descriptor_effects_and_zero_domain(self):
        self.assertEqual(certify_effects()['complete_procedure_outputs'],90)
        self.assertEqual(certify_zero()['zero_procedure_Signal_Wf_outputs'],101)

    def test_unaccounted_geometry_write_rejected(self):
        desc=f.self_description();out=list(desc.outputs)
        out[f.COL['s2_data']]=7*f.FIELDS+f.COL['address']
        with self.assertRaisesRegex(AssertionError,'unaccounted geometry effect'):
            certify_effects(Program(desc.inputs,desc.operations,tuple(out)))

    def test_head_birth_in_empty_domain_rejected(self):
        desc=f.self_description();out=list(desc.outputs)
        out[f.COL['s2_head']]=7*f.FIELDS+f.COL['f1']
        with self.assertRaisesRegex(AssertionError,'zero procedure domain'):
            certify_zero(Program(desc.inputs,desc.operations,tuple(out)))

    def test_neighbor_metadata_read_rejected(self):
        self.assertEqual(neighbor_static_independence()['unused_neighbor_static_inputs'],686)
        desc=f.self_description();out=list(desc.outputs)
        out[f.COL['s2_value']]=6*f.FIELDS+f.COL['p3_a']
        with self.assertRaisesRegex(AssertionError,'neighbor static metadata'):
            neighbor_static_independence(Program(desc.inputs,desc.operations,tuple(out)))

    def test_scalar_healthy_head_has_actual_computation(self):
        heads=healthy_heads()
        self.assertEqual(heads[128]['phase'],c.FETCH)
        self.assertEqual(heads[9913]['phase'],c.WRITE)
        self.assertEqual(heads[16989]['value'],(1<<64)-3)
        self.assertEqual(heads[16989]['rd'],9905)

    def test_nonzero_data_cannot_be_ignored_at_a_geometry_defect(self):
        data=np.zeros(f.Q,dtype=np.uint64);data[30960]=17
        with self.assertRaisesRegex(AssertionError,'nonzero Data'):
            check_zero_neighborhoods(data,127,[30960])

    def test_nearby_controller_cannot_be_ignored(self):
        data=np.zeros(f.Q,dtype=np.uint64)
        with self.assertRaisesRegex(AssertionError,'healthy controller'):
            check_zero_neighborhoods(data,30969,[30960])


if __name__=='__main__':unittest.main()
