"""Exact initial physical faults; no repair or domain rounding is allowed."""
import unittest
import numpy as np
from gacsca.fixed_rule import retimed_holder_initial_info_faults as faults,retimed_holder_endpoint_image_array as image
from gacsca.fixed_rule import retimed_holder_program as p,retimed_holder_rule as f


class InitialFaults(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.saved=np.load('figs/fixed_rule/retimed_holder_depth2_repair_fixture_v1.npz',allow_pickle=False)
    @classmethod
    def tearDownClass(cls):cls.saved.close()
    def initial(self,key):
        bank=np.zeros((1,p.layout().memory_count+5),dtype=np.uint64);bank[0,list(p.layout().info)]=self.saved[key]
        return image.render(bank,np.zeros((1,2),dtype=np.uint64),0)
    def test_exact_two_and_three_copy_images(self):
        for key,count in (('two',50),('three',75)):
            actual=self.initial('healthy');result=faults.apply(actual,self.saved[key+'_physical_faults'])
            self.assertEqual(result['physical_bit_faults'],count)
            np.testing.assert_array_equal(actual,self.initial('dirty_'+key))
    def test_partial_or_inconsistent_replicas_reject_atomically(self):
        initial=self.initial('healthy');before=initial.copy();good=self.saved['two_physical_faults']
        for mode in ('missing','wrong_mask','duplicate'):
            bad=good.copy()
            if mode=='missing':bad=bad[:-1]
            elif mode=='wrong_mask':bad[0,2]=2
            else:bad=np.concatenate((bad,bad[:1]))
            with self.assertRaises(ValueError):faults.apply(initial,bad)
            np.testing.assert_array_equal(initial,before)
    def test_geometry_and_outside_info_rejected(self):
        initial=self.initial('healthy');good=self.saved['two_physical_faults']
        for field,pos in ((f.COL['address'],0),(f.COL['s2_data'],0),(f.COL['s2_data'],f.Q*f.Q)):
            bad=good.copy();bad[0,:2]=pos,field
            with self.assertRaises(ValueError):faults.apply(initial,bad)
    def test_no_faults_preserve_full_state(self):
        initial=self.initial('healthy');before=initial.copy()
        self.assertEqual(faults.apply(initial,np.empty((0,3),dtype=np.uint64))['encoded_word_changes'],0)
        np.testing.assert_array_equal(initial,before)


if __name__=='__main__':unittest.main()
