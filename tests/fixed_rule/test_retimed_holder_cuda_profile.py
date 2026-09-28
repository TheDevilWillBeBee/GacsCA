"""Opt-in exact retimed capture, flag fronts and persistent Signal tests."""
import os
import unittest
import numpy as np
from test_retimed_holder_cpu_profile import world,cone
from gacsca.fixed_rule import retimed_holder_cuda_packets_bridge as bridge
from gacsca.fixed_rule import retimed_holder_core as c,retimed_holder_rule as f


@unittest.skipUnless(os.environ.get('FIXED_RULE_GPU_TESTS')=='1','explicit bounded GPU invocation required')
class CUDAProfile(unittest.TestCase):
    def test_literal_capture(self):
        cpu=world(c.CAPTURE_AGE-1,right=(0,));cpu.data[0,1:6]=0;cpu.data[0,f.Q-5:]=1
        points=(1,3,f.Q-5,f.Q-3,f.Q-1)
        expected=tuple(cone(cpu.cell,at,1) for at in points)
        with bridge.from_cpu(cpu) as gpu:
            gpu.step();cpu.step();bridge.compare(gpu,cpu)
            self.assertEqual(gpu.physical_cells(points),expected)

    def test_flag_fronts_and_wrap(self):
        for age in (c.WF_START-1,c.WF_START+1,c.WF_START+101,c.WF_END-1,c.WF_END,c.WF_END+f.Q//2-1,f.U-1):
            cpu=world(age);points=tuple(col*f.Q+a for col in range(cpu.n) for a in (0,1,73,f.Q-8,f.Q-3,f.Q-1))
            expected=tuple(cone(cpu.cell,at,1) for at in points)
            with bridge.from_cpu(cpu) as gpu:
                gpu.step();cpu.step();bridge.compare(gpu,cpu)
                self.assertEqual(gpu.physical_cells(points),expected,age)

    def test_active_flagged_controller_and_signal_survival(self):
        from gacsca.fixed_rule import retimed_holder_cpu_events as events
        cpu=world(c.WF_START+20000,right=(1,))
        fields=dict(head=1,phase=c.READ_B,pc=17,rb=73,rd=73,value=123,alu=c.NAND)
        cpu.heads[0]=[fields.get(name,0) for name in events.CONTROL];cpu.where[0]=73
        points=(71,73,75,f.Q-3)
        expected=tuple(cone(cpu.cell,at,3) for at in points)
        with bridge.from_cpu(cpu) as gpu:
            gpu.batch(3);cpu.advance(3);bridge.compare(gpu,cpu)
            self.assertEqual(gpu.physical_cells(points),expected)

if __name__=='__main__':unittest.main()
