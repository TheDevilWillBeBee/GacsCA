import unittest
import numpy as np
from gacsca.fixed_rule import small_holder_resident_general as general,small_holder_resident_gather as old
from gacsca.fixed_rule import small_holder_rule as f,small_holder_projected as r,small_holder_quotient as q,small_holder_core as c,small_holder_native as native
from gacsca.fixed_rule import small_holder_resident_faults as faults


def signals(age,right,left):
    logical={}
    for col,(a,b) in enumerate(zip(right,left)):
        for address in range(1,6):logical[col*f.Q+address]=q.Cell(address=address,age=age,signal=b<<(5-address))
        for address in range(f.Q-5,f.Q):logical[col*f.Q+address]=q.Cell(address=address,age=age,signal=a<<(f.Q-1-address))
    return logical


class GeneralResident(unittest.TestCase):
    def test_full_physical_steps_with_both_signals_and_active_controller(self):
        age=f.WF_START-2;right=(1,0,1);left=(1,1,0);logical=signals(age,right,left)
        logical[100]=q.Cell(address=100,age=age,head=1,phase=c.WRITE,rd=100,value=99)
        with general.World((r.Cell(),)*3,age=age,logical=logical) as world:
            for offset in (0,1,2,3,19,f.Q//2,2*f.Q+2,3*f.Q+2):
                world.advance(offset-world.time)
                points=tuple(sorted({(col*f.Q+a)%(3*f.Q) for col in range(3) for a in (*range(-3,9),98,99,100,101)}))
                expected=tuple(r.lift(r.project(native.local_step(world.physical_cells(tuple((pos+j)%(3*f.Q) for j in f.NEIGHBORHOOD))))) for pos in points)
                world.step();self.assertEqual(world.physical_cells(points),expected)
            self.assertIsNone(world._flags)

    def test_repeated_short_advances_preserve_flag_clock_and_old_right_only(self):
        age=f.WF_START-2;logical=signals(age,(1,0),(0,0))
        with general.World((r.Cell(),)*2,age=age,logical=logical) as a,old.World((r.Cell(),)*2,age=age,logical=logical) as b:
            for ticks in (1,1,1,7,257,3*f.Q):
                a.advance(ticks);b.advance(ticks)
                points=tuple(col*f.Q+i for col in range(2) for i in (0,1,3,7,100,f.Q-8,f.Q-3,f.Q-1))
                self.assertEqual(a.physical_cells(points),b.physical_cells(points))
            with self.assertRaisesRegex(ValueError,'supported resident reference'):faults.World(a)


if __name__=='__main__':unittest.main()
