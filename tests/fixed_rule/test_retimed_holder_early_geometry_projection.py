import unittest
import numpy as np
from gacsca.fixed_rule import retimed_holder_rule as f
from gacsca.fixed_rule import retimed_holder_geometry_projection as projection
from gacsca.fixed_rule.wordcode import Program
from experiments.fixed_rule.certify_retimed_holder_early_geometry_projection import certify
from experiments.fixed_rule.audit_retimed_holder_fresh_geometry_projection import scalar_output


class GeometryProjection(unittest.TestCase):
    def test_complete_descriptor_domain(self):
        row=certify()
        self.assertEqual(row['geometry_outputs_independent'],4)
        self.assertEqual(row['zero_Wf_outputs'],10)

    def test_foreign_Data_dependency_rejected(self):
        desc=f.self_description();out=list(desc.outputs)
        out[f.COL['f1']]=7*f.FIELDS+f.COL['s2_data']
        with self.assertRaisesRegex(AssertionError,'depends on other state'):
            certify(Program(desc.inputs,desc.operations,tuple(out)))

    def test_Wf_feedback_rejected(self):
        desc=f.self_description();out=list(desc.outputs)
        out[f.COL['w2_wf1']]=7*f.FIELDS+f.COL['f1']
        with self.assertRaisesRegex(AssertionError,'nonzero Wf'):
            certify(Program(desc.inputs,desc.operations,tuple(out)))

    def test_random_geometry_scalar_parity_including_d3(self):
        rng=np.random.default_rng(41)
        for age in (0,14,15,16,1023,32767):
            state=np.column_stack((rng.integers(0,f.Q,37),rng.integers(0,2,(37,2))))
            result=projection.step(state,age)
            for site in range(len(state)):
                np.testing.assert_array_equal(result[site],scalar_output(state,age,site))

    def test_canonical_geometry_with_arbitrary_flags(self):
        rng=np.random.default_rng(42)
        state=np.column_stack((np.arange(f.Q),rng.integers(0,2,(f.Q,2))))
        result=projection.step(state,15)
        np.testing.assert_array_equal(result[:,0],state[:,0])
        for site in (0,1,2,3,4,5,f.Q-1,f.Q-2,f.Q-5,16400):
            np.testing.assert_array_equal(result[site],scalar_output(state,15,site))

    def test_projection_refuses_clock_outside_certificate(self):
        state=np.zeros((11,3),dtype=np.int64)
        with self.assertRaises(ValueError): projection.step(state,32768)


if __name__=='__main__': unittest.main()
