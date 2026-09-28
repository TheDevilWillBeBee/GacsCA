"""Reject missing persistent state or wrong raw simulated controller outputs."""
from pathlib import Path
import unittest
import numpy as np
from experiments.fixed_rule.audit_retimed_holder_cuda_periods import validate
from gacsca.fixed_rule import retimed_holder_rule as f,retimed_holder_program as p
from gacsca.fixed_rule import retimed_holder_packed as packed,retimed_holder_quotient as q

GPU=Path('figs/fixed_rule/retimed_holder_cuda_periods15_v1.npz')
CPU=Path('figs/fixed_rule/retimed_holder_cpu_periods_15_v1.npz')

@unittest.skipUnless(GPU.exists() and CPU.exists(),'saved period evidence required')
class PeriodAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with np.load(GPU,allow_pickle=False) as data:cls.gpu={key:data[key] for key in data.files}
        with np.load(CPU,allow_pickle=False) as data:cls.cpu={key:data[key] for key in data.files}

    def test_complete_two_periods_pass(self):
        result=validate(self.gpu,self.cpu,2)
        self.assertEqual([row['changed_upper_controller_words'] for row in result['period_results']],[70,65])

    def test_signal_loss_detected_even_with_correct_Info(self):
        data=dict(self.gpu);data['boundary_counts']=data['boundary_counts'].copy();data['boundary_counts'][0]=0
        with self.assertRaisesRegex(AssertionError,'Signal/controller/mail'):validate(data,self.cpu,2)

    def test_hidden_controller_residue_rejected(self):
        data=dict(self.gpu);data['boundary_sparse']=data['boundary_sparse'].copy()
        col=int(np.flatnonzero(data['boundary_right'][0])[0]);row=packed.unpack(data['boundary_sparse'][0,col,:1])
        row[0,q.COL['pc']]=1;data['boundary_sparse'][0,col,:1]=packed.pack(row)
        with self.assertRaises(AssertionError):validate(data,self.cpu,2)

    def test_non_Info_Data_corruption_rejected(self):
        data=dict(self.gpu);data['boundary_banks']=data['boundary_banks'].copy();data['boundary_banks'][1,0,50]^=np.uint64(1)
        with self.assertRaises(AssertionError):validate(data,self.cpu,2)

    def test_corrupted_raw_operand_in_both_GPU_and_CPU_rejected(self):
        data=dict(self.gpu);cpu=dict(self.cpu)
        data['boundary_banks']=data['boundary_banks'].copy();cpu['boundary_data']=cpu['boundary_data'].copy()
        address=p.layout().info[f.COL['s2_rb']]
        data['boundary_banks'][1,0,address]^=np.uint64(1);cpu['boundary_data'][1,0,address]^=np.uint64(1)
        with self.assertRaisesRegex(AssertionError,'raw Info'):validate(data,cpu,2)

if __name__=='__main__':unittest.main()
