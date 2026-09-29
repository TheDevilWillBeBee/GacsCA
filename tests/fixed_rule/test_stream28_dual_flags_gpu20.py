"""Literal GPU Flag recurrence agrees with independent CPU packed recurrence."""
import shutil
import unittest

import numpy as np

from gacsca.fixed_rule import stream28_dual_flags_cpu20 as cpu
from gacsca.fixed_rule import stream28_dual_flags_gpu20 as gpu
from gacsca.fixed_rule import stream28_dual_holder_rule20 as rule


@unittest.skipUnless(shutil.which('nvidia-smi') and
                     shutil.which('/usr/local/cuda/bin/nvcc'),
                     'CUDA toolchain/GPU unavailable')
class U20FlagGPUParityTest(unittest.TestCase):
    def test_both_forcing_boundaries_and_full_active_window(self):
        states={3:1,rule.Q-4:2,rule.Q-3:3}
        runs=cpu.pack_sparse(states)
        for age,ticks in ((rule.WF_START-3,20),
                          (rule.WF_END-3,20),
                          (rule.WF_START-1,rule.WF_END-rule.WF_START),
                          (rule.U-1,1)):
            with self.subTest(age=age,ticks=ticks):
                with cpu.World((1,),(1,),age=age,runs=runs) as reference,\
                     gpu.World((1,),(1,),age=age,runs=runs) as device:
                    reference.run(ticks,skip_fixed=False)
                    device.run(ticks)
                    np.testing.assert_array_equal(device.runs,reference.runs)
                    self.assertEqual(device.info['age'],reference.info['age'])


if __name__=='__main__':unittest.main()
