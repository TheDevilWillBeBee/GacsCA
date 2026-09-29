"""Literal raw-state checks for two-sided Signals and unrestricted flag words."""
import unittest
import numpy as np

from gacsca.fixed_rule import compact16_holder_cpu_general as general
from gacsca.fixed_rule import compact16_holder_cpu_events as events
from gacsca.fixed_rule import compact16_holder_rule as f, compact16_holder_core as c
from gacsca.fixed_rule import compact16_holder_program as p, compact16_holder_native as native
from gacsca.fixed_rule import compact16_holder_flags_cpu as packed


def world(age, right=(1,0,1), left=(0,1,1), random_flags=True):
    n = len(right); data = np.zeros((n,f.Q), dtype=np.uint64)
    data[:,:p.layout().memory_count] = np.arange(p.layout().memory_count, dtype=np.uint64)+17
    flags = None
    if random_flags:
        flags = np.random.default_rng(883).integers(0,2**64,size=(n*f.Q//64,2),dtype=np.uint64)
    return general.World(data,np.zeros((n,len(events.CONTROL)),dtype=np.uint64),
                         np.zeros(n,dtype=np.uint64),age=age,right=right,left=left,flags=flags)


def cone(read, at, ticks):
    rows = {pos:read(pos) for pos in range(at-7*ticks,at+7*ticks+1)}
    for step in range(ticks):
        radius = 7*(ticks-step-1)
        rows = {pos:native.local_step(tuple(rows[pos+j] for j in f.NEIGHBORHOOD))
                for pos in range(at-radius,at+radius+1)}
    return rows[at]


class GeneralContext(unittest.TestCase):
    def test_every_packed_bit_at_edges_and_interior_matches_full_F(self):
        checked = 0
        for age in (c.WF_START-1,c.WF_START,c.WF_END-1,c.WF_END):
            w = world(age)
            positions = [col*f.Q+start+bit for col,start in ((0,0),(1,64),(2,f.Q-64)) for bit in range(64)]
            expected = {at:cone(w.cell,at,1) for at in positions}
            if age == c.WF_START:  # This age also executes the physical reset.
                wanted_flags, _ = w._flags_after(1)
                w.step()
                np.testing.assert_array_equal(w.flags,wanted_flags)
            else:
                w.quiet_advance(1)
            for at,wanted in expected.items():
                self.assertEqual(w.cell(at),wanted,(age,at)); checked += 1
        self.assertEqual(checked,768)

    def test_literal_capture_keeps_both_signal_sides(self):
        w = world(c.CAPTURE_AGE-1,right=(0,),left=(0,),random_flags=False)
        w.data[0,1:6] = 1; w.data[0,f.Q-5:] = 1
        positions = (0,1,3,5,6,f.Q-5,f.Q-3,f.Q-1)
        expected = {at:cone(w.cell,at,1) for at in positions}
        w.step()
        self.assertEqual(w.right.tolist(),[1]); self.assertEqual(w.left.tolist(),[1])
        for at,wanted in expected.items():
            self.assertEqual(w.cell(at),wanted)

    def test_literal_forcing_and_wrap_match_all_raw_fields(self):
        for age in (c.WF_START-1,c.WF_END-1,f.U-1):
            w = world(age,right=(1,),left=(1,))
            positions = (0,1,4,7,64,f.Q-8,f.Q-1)
            expected = {at:cone(w.cell,at,1) for at in positions}
            w.step()
            for at,wanted in expected.items():
                self.assertEqual(w.cell(at),wanted,(age,at))

    def test_active_controller_under_arbitrary_flags_and_atomic_send_rejection(self):
        w = world(c.WF_START+100,right=(1,),left=(1,))
        values = dict(head=1,phase=c.READ_B,pc=17,rb=73,rd=73,value=123,alu=c.NAND)
        w.heads[0] = [values.get(name,0) for name in events.CONTROL]; w.where[0] = 73
        expected = {at:cone(w.cell,at,3) for at in (71,73,75)}
        w.advance(3)
        for at,wanted in expected.items():
            self.assertEqual(w.cell(at),wanted)
        values = dict(head=1,phase=c.TRANSMIT,pc=17,ra=73,rb=next(p.layout().history(0,w//f.FIELDS-7,w%f.FIELDS) for w in p.layout().gathered_inputs if w//f.FIELDS!=7),rd=0)
        w.heads[0] = [values.get(name,0) for name in events.CONTROL]; w.where[0] = 73
        before = tuple(a.copy() for a in (w.data,w.heads,w.where,w.flags,w.right,w.left))
        age,time = w.age,w.time
        with self.assertRaisesRegex(RuntimeError,'packet emission'):
            w.advance(1)
        for actual,wanted in zip((w.data,w.heads,w.where,w.flags,w.right,w.left),before):
            np.testing.assert_array_equal(actual,wanted)
        self.assertEqual((w.age,w.time),(age,time))

    def test_arbitrary_flags_clear_without_assumed_front(self):
        w = world(c.WF_END)
        w.quiet_advance(f.Q//2)
        self.assertFalse(np.any(w.flags[:,0]))
        w.quiet_advance(f.Q//2)
        self.assertFalse(np.any(w.flags))

    def test_fixed_point_skip_matches_literal_and_stops_at_clock_boundary(self):
        for age in (0,c.WF_START-2,c.WF_END-2):
            with packed.World((1,),(1,),age=age) as fast, packed.World((1,),(1,),age=age) as slow:
                fast.run(12); slow.run(12,skip_fixed=False)
                np.testing.assert_array_equal(fast.runs,slow.runs)
                self.assertEqual(fast.info['age'],slow.info['age'])
        with packed.World((0,),(0,),age=f.U-1) as w:
            w.run(1); self.assertEqual(w.info['age'],0)
            with self.assertRaises(ValueError):
                w.run(1)


if __name__ == '__main__':
    unittest.main()
