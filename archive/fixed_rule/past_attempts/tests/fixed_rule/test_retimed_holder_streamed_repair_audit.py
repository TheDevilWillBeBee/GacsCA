"""Audit distinctions: decoded equality, scratch differences and real bit sets."""
import unittest
import numpy as np
from experiments.fixed_rule.audit_retimed_holder_streamed_repair import observed_physical_faults,difference_categories
from gacsca.fixed_rule import retimed_holder_rule as f,retimed_holder_program as p


class RepairAudit(unittest.TestCase):
    def test_one_encoded_bit_has_five_actual_physical_faults(self):
        a=np.zeros((3,f.FIELDS),dtype=np.uint64);b=a.copy();b[1,7]=8
        faults=observed_physical_faults(a,b);self.assertEqual(faults.shape,(5,3));self.assertTrue(np.all(faults[:,2]==8))
        primary=f.Q+p.layout().info[7]
        expected={(primary-d,f.COL[f's{d+2}_data'],8) for d in f.OFFSETS}
        self.assertEqual(set(map(tuple,faults)),expected)
    def test_non_single_bit_difference_rejected(self):
        a=np.zeros((1,f.FIELDS),dtype=np.uint64);b=a.copy();b[0,0]=3
        with self.assertRaises(AssertionError):observed_physical_faults(a,b)
    def test_equal_info_does_not_hide_history_or_controller_word(self):
        g=p.layout();a=np.zeros((1,g.memory_count+5),dtype=np.uint64);b=a.copy();b[0,g.history(0,0,f.COL['s2_rb'])]=1
        result=difference_categories(a,b);self.assertEqual(result['info'],0);self.assertEqual(result['total'],1);self.assertEqual(result['history'],1)
        b[0,g.info[f.COL['s2_rb']]]=1;self.assertEqual(difference_categories(a,b)['info'],1)
    def test_tail_and_query_residue_included(self):
        g=p.layout();a=np.zeros((1,g.memory_count+5),dtype=np.uint64);b=a.copy();b[0,-1]=1;b[0,g.memory_count-1]=1
        self.assertEqual(difference_categories(a,b)['other_scratch'],2)
        self.assertEqual(difference_categories(a,b)['total'],2)


if __name__=='__main__':unittest.main()
