"""Reject missing physical state and false recovery in saved GPU repair evidence."""
from pathlib import Path
import unittest
import numpy as np
from experiments.fixed_rule.audit_retimed_holder_cuda_encoded_repair import validate
from gacsca.fixed_rule import retimed_holder_rule as f,retimed_holder_quotient as q

GPU=Path('figs/fixed_rule/retimed_holder_cuda_encoded_repair_v1.npz')
CPU=Path('figs/fixed_rule/retimed_holder_cpu_encoded_repair_v2.npz')

@unittest.skipUnless(GPU.exists() and CPU.exists(),'saved repair execution required')
class RepairAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with np.load(GPU,allow_pickle=False) as z:cls.saved={name:z[name] for name in z.files}
        with np.load(CPU,allow_pickle=False) as z:cls.reference={name:z[name] for name in z.files}

    def test_complete_saved_state_passes(self):
        self.assertTrue(validate(self.saved,self.reference)['all_saved_physical_rejoin_fields_match'])

    def test_premature_erasure_of_encoded_fault_rejected(self):
        z=dict(self.saved);z['after_first_lower_tick']=z['initial']
        with self.assertRaises(AssertionError):validate(z,self.reference)

    def test_omitted_rejoin_controller_state_rejected(self):
        z=dict(self.saved);del z['rejoin_actual_active_rows']
        with self.assertRaises(KeyError):validate(z,self.reference)

    def test_non_Data_rejoin_fault_rejected(self):
        z=dict(self.saved);z['rejoin_actual_active_rows']=z['rejoin_actual_active_rows'].copy()
        z['rejoin_actual_active_rows'][0,0,q.COL['pc']]^=np.uint64(1)
        with self.assertRaises(AssertionError):validate(z,self.reference)

    def test_saved_physical_transition_fault_rejected(self):
        z=dict(self.saved);z['late_probe_after_one_tick']=z['late_probe_after_one_tick'].copy()
        middle=len(z['late_probe_positions'])//2
        z['late_probe_after_one_tick'][middle,f.COL['s2_pc']]^=np.uint64(1)
        with self.assertRaisesRegex(AssertionError,'saved faulty transition'):validate(z,self.reference)

if __name__=='__main__':unittest.main()
