"""Packet transport, simultaneous delivery, and guarded physical SEND tests."""
import unittest
import numpy as np
from gacsca.fixed_rule import retimed_holder_cpu_gather as g,retimed_holder_cpu_events as e
from gacsca.fixed_rule import retimed_holder_rule as f,retimed_holder_core as c,retimed_holder_program as p
from gacsca.fixed_rule import retimed_holder_native as native

TARGET=p.layout().history(0,1,0)

def world(packets=(),*,head=None,n=1):
    data=np.zeros((n,f.Q),dtype=np.uint64)
    data[:,:p.layout().memory_count]=np.arange(p.layout().memory_count,dtype=np.uint64)+0x1000
    heads=np.zeros((n,len(e.CONTROL)),dtype=np.uint64);where=np.zeros(n,dtype=np.uint64)
    if head is not None:
        at,fields=head;heads[0]=[fields.get(name,0) for name in e.CONTROL];where[0]=at
    return g.World(data,heads,where,age=100,packets=packets)


def cone(read,center,ticks):
    rows={pos:read(pos) for pos in range(center-7*ticks,center+7*ticks+1)}
    for step in range(ticks):
        radius=7*(ticks-step-1)
        rows={pos:native.local_step(tuple(rows[pos+j] for j in f.NEIGHBORHOOD)) for pos in range(center-radius,center+radius+1)}
    return rows[center]


def snapshot(w):return w.data.copy(),w.heads.copy(),w.where.copy(),w.packets.copy(),w.age,w.time


class GatherPackets(unittest.TestCase):
    def unchanged(self,w,before):
        for actual,wanted in zip((w.data,w.heads,w.where,w.packets),before[:4]):np.testing.assert_array_equal(actual,wanted)
        self.assertEqual((w.age,w.time),before[4:])

    def test_boundary_transport_all_hops_matches_raw_literal_cones(self):
        for n in (1,2):
            for track in (0,1):
                for hops in range(8):
                    start=0 if track==0 else f.Q-1;target=f.Q-1 if track==0 else 1
                    w=world([(start,track,target,0xdeadbeef,hops)],n=n)
                    centers=(start,start+(-2 if track==0 else 2))
                    expected={at:cone(w.cell,at,3) for at in centers}
                    w.advance(3)
                    for at,wanted in expected.items():self.assertEqual(w.cell(at),wanted,(n,track,hops,at))

    def test_simultaneous_delivery_right_track_wins(self):
        w=world([(TARGET+1,0,TARGET,0x111,0),(TARGET-1,1,TARGET,0x222,0)])
        expected={at:cone(w.cell,at,1) for at in range(TARGET-2,TARGET+3)}
        result=w.advance(1)
        self.assertEqual(result['packets_delivered'],2);self.assertEqual(len(w.packets),0)
        self.assertEqual(int(w.data[0,TARGET]),0x222)
        for at,wanted in expected.items():self.assertEqual(w.cell(at),wanted)

    def test_full_rule_SEND_birth_and_subsequent_transport(self):
        for direction in (c.LEFT,c.RIGHT):
            controls=dict(head=1,phase=c.TRANSMIT,pc=17,ra=73,rb=TARGET,rd=(2<<1)|direction)
            w=world(head=(73,controls));centers=(70,73,76)
            expected={at:cone(w.cell,at,4) for at in centers}
            result=w.advance(4)
            self.assertEqual(result['packets_emitted'],1)
            self.assertEqual(len(w.packets),1);self.assertEqual(int(w.packets[0,3]),0x1000+73)
            for at,wanted in expected.items():self.assertEqual(w.cell(at),wanted)

    def test_repeated_ring_laps_consume_hops(self):
        for track in (0,1):
            source=TARGET+10 if track==0 else TARGET-10
            w=world([(source,track,TARGET,0xcafe,7)])
            before=7*f.Q+9
            result=w.advance(before)
            self.assertEqual(result['packets_delivered'],0);self.assertEqual(int(w.packets[0,4]),0)
            expected={at:cone(w.cell,at,1) for at in (TARGET-1,TARGET,TARGET+1)}
            result=w.advance(1)
            self.assertEqual(result['packets_delivered'],1);self.assertFalse(len(w.packets))
            for at,wanted in expected.items():self.assertEqual(w.cell(at),wanted)

    def test_protected_controller_access_rejected_atomically(self):
        for phase,register in ((c.READ_A,'ra'),(c.READ_B,'rb'),(c.WRITE,'rd'),(c.TRANSMIT,'ra'),(c.READ_LOAD,'ra')):
            controls=dict(head=1,phase=phase,pc=17);controls[register]=TARGET
            w=world([(TARGET-1,1,TARGET,123,0)],head=(TARGET,controls));before=snapshot(w)
            with self.assertRaisesRegex(RuntimeError,'rejected \\(-11\\)'):w.advance(1)
            self.unchanged(w,before)

    def test_birth_collision_and_capacity_reject_atomically(self):
        controls=dict(head=1,phase=c.TRANSMIT,pc=17,ra=73,rb=TARGET,rd=0)
        for capacity,code in ((None,-14),(1,-12)):
            w=world([(72,1,TARGET,123,0)],head=(73,controls));before=snapshot(w)
            with self.assertRaisesRegex(RuntimeError,'rejected \\('+str(code)+'\\)'):w.advance(1,packet_capacity=capacity)
            self.unchanged(w,before)

    def test_segmented_calls_preserve_live_mail(self):
        packets=[(0,0,TARGET,123,2),(f.Q-1,1,5,456,2)]
        a,b=world(packets),world(packets)
        a.advance(200)
        for ticks in (1,2,17,180):b.advance(ticks)
        np.testing.assert_array_equal(a.data,b.data)
        self.assertEqual(sorted(map(tuple,a.packets)),sorted(map(tuple,b.packets)))
        self.assertEqual(a.age,b.age)

if __name__=='__main__':unittest.main()
