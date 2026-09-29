"""Saved GPU evidence must reject missing controllers and unrelated Data faults."""
from pathlib import Path
import unittest
import numpy as np
from experiments.fixed_rule.audit_retimed_holder_cuda import validate

ARTIFACT=Path('figs/fixed_rule/retimed_holder_cuda_full15_v1.npz')


@unittest.skipUnless(ARTIFACT.exists(),'saved GPU evidence required')
class CUDAAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with np.load(ARTIFACT,allow_pickle=False) as data:cls.saved={key:data[key] for key in data.files}

    def test_complete_receipt_passes(self):
        self.assertTrue(validate(self.saved,15)['all_raw_Hold_matches_scalar_and_descriptor'])

    def test_missing_raw_controller_rejected(self):
        data=dict(self.saved);del data['initial_heads']
        with self.assertRaisesRegex(AssertionError,'missing complete state'):validate(data,15)

    def test_absent_active_dynamics_rejected(self):
        data=dict(self.saved);data['initial_heads']=np.zeros_like(data['initial_heads'])
        with self.assertRaisesRegex(AssertionError,'absent active computation'):validate(data,15)

    def test_unrelated_Data_corruption_rejected(self):
        data=dict(self.saved);data['gpu_bank']=data['gpu_bank'].copy();data['gpu_bank'][0,50]^=np.uint64(1)
        with self.assertRaises(AssertionError):validate(data,15)

    def test_residual_GPU_controller_rejected(self):
        data=dict(self.saved);data['gpu_counts']=data['gpu_counts'].copy();data['gpu_counts'][0]=1
        with self.assertRaises(AssertionError):validate(data,15)

if __name__=='__main__':unittest.main()
