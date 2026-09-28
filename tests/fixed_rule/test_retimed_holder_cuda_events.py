"""Opt-in bounded actual-GPU cones and atomic rejection tests."""
import os
import unittest
import numpy as np
from test_retimed_holder_cuda_contract import fixture
from gacsca.fixed_rule import retimed_holder_cuda_bridge as bridge
from gacsca.fixed_rule import retimed_holder_resident_independent as gpu
from gacsca.fixed_rule import retimed_holder_native as native,retimed_holder_rule as f
from gacsca.fixed_rule import retimed_holder_core as c,retimed_holder_program as p


def literal_cone(read,center,ticks):
    rows={pos:read(pos) for pos in range(center-7*ticks,center+7*ticks+1)}
    for t in range(ticks):
        radius=7*(ticks-t-1)
        rows={pos:native.local_step(tuple(rows[pos+j] for j in f.NEIGHBORHOOD)) for pos in range(center-radius,center+radius+1)}
    return rows[center]


@unittest.skipUnless(os.environ.get('FIXED_RULE_GPU_TESTS')=='1','explicit bounded GPU test invocation required')
class CUDAEvents(unittest.TestCase):
    def test_short_bursts_match_every_raw_field_in_literal_cones(self):
        cases=[(73,phase,d,{}) for phase in (c.READ_A,c.READ_B,c.WRITE,c.READ_LOAD,c.WAIT_META) for d in (0,1)]
        cases += [(at,c.READ_B,d,{}) for at in (0,len(p.base_rom())-1) for d in (0,1)]
        cases += [(len(p.base_rom())-1,c.READ_META,0,dict(rb=k,rd=len(p.base_rom())-1,value=1)) for k in range(7)]
        cases += [(p.layout().memory_count+p.layout().entries[4],c.FETCH,0,dict(pc=p.layout().entries[4]))]
        for at,phase,d,extra in cases:
            cpu=fixture(at,phase,direction=d,**extra)
            positions=(at-2,at,at+2)
            expected=tuple(literal_cone(cpu.cell,pos,3) for pos in positions)
            with bridge.from_cpu(cpu) as world:
                world.batch(3,extra_device_budget=32*1024**2)
                actual=world.physical_cells(tuple(pos%f.Q for pos in positions))
                self.assertEqual(actual,expected,(at,phase,d))

    def assert_unchanged(self,world,before):
        for a,b in zip(world.snapshot(),before[:3]):np.testing.assert_array_equal(a,b)
        self.assertEqual((world.age,world.time),before[3:])

    def test_SEND_rejection_is_atomic(self):
        cpu=fixture(73,c.TRANSMIT,ra=73,rb=80,rd=0)
        with bridge.from_cpu(cpu) as world:
            before=(*world.snapshot(),world.age,world.time)
            with self.assertRaises(gpu.BatchRejected) as caught:world.batch(1,extra_device_budget=32*1024**2)
            self.assertEqual(caught.exception.code,-4)
            self.assert_unchanged(world,before)

    def test_event_budget_rejection_is_atomic(self):
        pc=p.layout().entries[4];cpu=fixture(p.layout().memory_count+pc,c.FETCH,pc=pc)
        with bridge.from_cpu(cpu) as world:
            before=(*world.snapshot(),world.age,world.time)
            with self.assertRaises(gpu.BatchRejected) as caught:world.batch(200000,event_budget=1,extra_device_budget=32*1024**2)
            self.assertEqual(caught.exception.code,-4)
            self.assert_unchanged(world,before)

    def test_device_budget_and_clock_boundary_rejections_are_atomic(self):
        cpu=fixture(73,c.READ_A)
        with bridge.from_cpu(cpu) as world:
            before=(*world.snapshot(),world.age,world.time)
            with self.assertRaises(gpu.BatchRejected) as caught:world.batch(1,extra_device_budget=1)
            self.assertEqual(caught.exception.code,-2)
            self.assert_unchanged(world,before)
            with self.assertRaises(gpu.BatchRejected) as caught:world.batch(f.U-world.age)
            self.assertEqual(caught.exception.code,-1)
            self.assert_unchanged(world,before)

if __name__=='__main__':unittest.main()
