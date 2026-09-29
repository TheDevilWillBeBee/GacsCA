from dataclasses import replace
import unittest
from gacsca.fixed_rule import small_holder_rule as f
from experiments.fixed_rule.certify_small_holder_event_support import certify


class EventSupport(unittest.TestCase):
    def test_actual_descriptor_has_checked_procedure_support(self):
        result=certify()
        self.assertTrue(result['passed'])
        self.assertEqual(result['logical_procedure_offsets'],[-3,-2,-1,0,1,2,3,4])

    def test_dependency_outside_event_window_is_rejected(self):
        desc=f.self_description();outputs=list(desc.outputs)
        outputs[f.COL['s2_data']]=14*f.FIELDS+f.COL['s4_data']
        with self.assertRaisesRegex(AssertionError,'event window'):
            certify(replace(desc,outputs=tuple(outputs)))


if __name__=='__main__':unittest.main()
