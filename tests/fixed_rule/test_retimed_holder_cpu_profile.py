"""Captured Signals, mixed physical flag fronts and safe context composition."""
import unittest
import numpy as np
from gacsca.fixed_rule import retimed_holder_cpu_profile as profile,retimed_holder_cpu_events as events
from gacsca.fixed_rule import retimed_holder_rule as f,retimed_holder_core as c,retimed_holder_program as p,retimed_holder_native as native


def world(age,right=(1,0,1)):
    n=len(right);data=np.zeros((n,f.Q),dtype=np.uint64)
    data[:,:p.layout().memory_count]=np.arange(p.layout().memory_count,dtype=np.uint64)+17
    return profile.World(data,np.zeros((n,len(events.CONTROL)),dtype=np.uint64),np.zeros(n,dtype=np.uint64),age=age,right=right)


def cone(read,at,ticks):
    rows={pos:read(pos) for pos in range(at-7*ticks,at+7*ticks+1)}
    for step in range(ticks):
        radius=7*(ticks-step-1)
        rows={pos:native.local_step(tuple(rows[pos+j] for j in f.NEIGHBORHOOD)) for pos in range(at-radius,at+radius+1)}
    return rows[at]


class Profile(unittest.TestCase):
    def test_mixed_forcing_cutoff_and_clearing_match_raw_F(self):
        for age in (c.WF_START-1,c.WF_START+1,c.WF_START+101,c.WF_END-1,c.WF_END,c.WF_END+f.Q//2-1):
            w=world(age);positions=[col*f.Q+a for col in range(w.n) for a in (0,1,73,f.Q-8,f.Q-3,f.Q-1)]
            expected={at:cone(w.cell,at,1) for at in positions}
            w.quiet_advance(1)
            for at,wanted in expected.items():self.assertEqual(w.cell(at),wanted,(age,at))

    def test_literal_capture_retains_right_bit_and_rejects_left(self):
        w=world(c.CAPTURE_AGE-1,right=(0,));w.data[0,1:6]=0;w.data[0,f.Q-5:]=1
        expected={at:cone(w.cell,at,1) for at in (1,3,f.Q-5,f.Q-3,f.Q-1)}
        w.step();self.assertEqual(w.right.tolist(),[1])
        for at,wanted in expected.items():self.assertEqual(w.cell(at),wanted)
        w=world(c.CAPTURE_AGE-1,right=(0,));w.data[0,1:6]=1;before=w.data.copy()
        with self.assertRaisesRegex(RuntimeError,'rejected \\(-33\\)'):w.step()
        np.testing.assert_array_equal(w.data,before);self.assertEqual(w.age,c.CAPTURE_AGE-1);self.assertEqual(w.right.tolist(),[0])

    def test_active_controller_keeps_complete_physical_context(self):
        w=world(c.WF_START+20000,right=(1,))
        fields=dict(head=1,phase=c.READ_B,pc=17,rb=73,rd=73,value=123,alu=c.NAND)
        w.heads[0]=[fields.get(name,0) for name in events.CONTROL];w.where[0]=73
        expected={at:cone(w.cell,at,3) for at in (71,73,75)}
        self.assertEqual(w.cell(73).f1,1)
        w.advance(3)
        for at,wanted in expected.items():self.assertEqual(w.cell(at),wanted)

    def test_forcing_emission_rejected_atomically(self):
        w=world(c.WF_START+20000,right=(1,));target=p.layout().history(0,1,0)
        fields=dict(head=1,phase=c.TRANSMIT,pc=17,ra=73,rb=target,rd=0)
        w.heads[0]=[fields.get(name,0) for name in events.CONTROL];w.where[0]=73
        before=(w.data.copy(),w.heads.copy(),w.where.copy(),w.age,w.time)
        with self.assertRaisesRegex(RuntimeError,'emission during forcing'):w.advance(1)
        for actual,wanted in zip((w.data,w.heads,w.where),before[:3]):np.testing.assert_array_equal(actual,wanted)
        self.assertEqual((w.age,w.time),before[3:]);self.assertEqual(len(w.packets),0)

if __name__=='__main__':unittest.main()
