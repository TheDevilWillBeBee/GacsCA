"""Opt-in literal packet tests of retimed CUDA, compared with complete raw F."""
import os
import unittest
import numpy as np
from test_retimed_holder_cpu_gather import world,cone,TARGET
from gacsca.fixed_rule import retimed_holder_cuda_packets_bridge as bridge
from gacsca.fixed_rule import retimed_holder_resident_independent as independent
from gacsca.fixed_rule import retimed_holder_rule as f,retimed_holder_core as c


@unittest.skipUnless(os.environ.get('FIXED_RULE_GPU_TESTS')=='1','explicit bounded GPU invocation required')
class CUDAPackets(unittest.TestCase):
    def compare(self,state,ticks,centers=()):
        expected=tuple(cone(state.cell,at,ticks) for at in centers) if ticks<=4 else ()
        with bridge.from_cpu(state) as gpu:
            bridge.compare(gpu,state)
            gpu.batch(ticks,extra_device_budget=32*1024**2)
            state.advance(ticks)
            bridge.compare(gpu,state)
            if expected:self.assertEqual(gpu.physical_cells(tuple(at%(state.n*f.Q) for at in centers)),expected)

    def test_boundary_packets_all_hops_and_directions(self):
        for n in (1,2):
            for track in (0,1):
                for hops in range(8):
                    at=0 if track==0 else f.Q-1
                    state=world([(at,track,TARGET,0xdeadbeef,hops)],n=n)
                    self.compare(state,3,(at,at+(-2 if track==0 else 2)))
        # Nonaliasing finite packet halo, including more than 15 colonies.
        self.compare(world([(16*f.Q+f.Q-1,1,TARGET,123,7)],n=17),7*f.Q)

    def test_real_SEND_and_signal_buffer_payload(self):
        for target in (TARGET,3,f.Q-3):
            for direction in (c.LEFT,c.RIGHT):
                controls=dict(head=1,phase=c.TRANSMIT,pc=17,ra=73,rb=target,rd=(2<<1)|direction)
                self.compare(world(head=(73,controls)),4,(70,73,76))

    def test_actual_tail_and_left_signal_buffer_deliveries(self):
        for target in (1,3,5,f.Q-5,f.Q-3,f.Q-1):
            # Both directions, including wrapped arrival after consuming a hop.
            for track in (0,1):
                at=(target+(1 if track==0 else -1))%f.Q
                hops=int((track==0 and at<target) or (track==1 and at>target))
                state=world([(at,track,target,0x123456789abcdef0,hops)])
                self.compare(state,1,(target-2,target,target+2))
                self.assertEqual(int(state.data[0,target]),0x123456789abcdef0)

    def test_delivery_priority_laps_and_segmentation(self):
        self.compare(world([(TARGET+1,0,TARGET,0x111,0),(TARGET-1,1,TARGET,0x222,0)]),1,(TARGET-2,TARGET,TARGET+2))
        for track in (0,1):
            at=TARGET+10 if track==0 else TARGET-10
            state=world([(at,track,TARGET,0xcafe,7)])
            with bridge.from_cpu(state) as gpu:
                for ticks in (1,17,7*f.Q-9,1):
                    gpu.batch(ticks,extra_device_budget=32*1024**2);state.advance(ticks);bridge.compare(gpu,state)
                self.assertFalse(len(state.packets))

    def test_protected_access_and_birth_collision_reject_atomically(self):
        for target in (TARGET,3,f.Q-3):
            for phase,reg in ((c.READ_A,'ra'),(c.READ_B,'rb'),(c.WRITE,'rd'),(c.TRANSMIT,'ra'),(c.READ_LOAD,'ra')):
                controls=dict(head=1,phase=phase,pc=17);controls[reg]=target
                # A tail position is outside the supported controller core.
                if target==f.Q-3:continue
                state=world([(target-1,1,target,123,0)],head=(target,controls))
                with bridge.from_cpu(state) as gpu:
                    with self.assertRaises(independent.BatchRejected):gpu.batch(1)
                    bridge.compare(gpu,state)
        controls=dict(head=1,phase=c.TRANSMIT,pc=17,ra=73,rb=TARGET,rd=0)
        state=world([(72,1,TARGET,123,0)],head=(73,controls))
        with bridge.from_cpu(state) as gpu:
            with self.assertRaises(independent.BatchRejected):gpu.batch(1)
            bridge.compare(gpu,state)

if __name__=='__main__':unittest.main()
