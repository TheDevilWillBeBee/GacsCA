import unittest
from unittest.mock import patch
import numpy as np
from gacsca.fixed_rule import small_holder_resident_gather as fast,small_holder_resident_mixed as slow
from gacsca.fixed_rule import small_holder_rule as f,small_holder_core as c,small_holder_program as p,small_holder_projected as r,small_holder_quotient as q,small_holder_native as native
from gacsca.fixed_rule.wordcode import Program


class Gather(unittest.TestCase):
    def compare(self,logical,ticks,colonies=3,full=False):
        parents=tuple(r.Cell(address=i) for i in range(colonies))
        with fast.World(parents,age=1,logical=logical) as a,slow.World(parents,age=1,logical=logical) as b:
            with patch.object(Program,'evaluate',side_effect=AssertionError('host evaluator')),patch.object(f,'local_step',side_effect=AssertionError('host upper rule')):metrics=a.batch(ticks)
            b.run(ticks)
            addresses={0,1,f.Q-1,p.layout().computation_cells-1,p.layout().computation_cells,p.layout().info[0],p.layout().history(0,1,0)}
            for pos,cell in logical.items():
                local=pos%f.Q;addresses.update(((local-ticks)%f.Q,(local+ticks)%f.Q,local))
                for track in ('lp','rp'):
                    if getattr(cell,track+'_valid'):addresses.add(getattr(cell,track+'_target'))
                if cell.phase==c.TRANSMIT:addresses.add(cell.rb)
            points=tuple(col*f.Q+at for col in range(colonies) for at in sorted(addresses))
            for offset in range(0,len(points),100):self.assertEqual(a.physical_cells(points[offset:offset+100]),b.physical_cells(points[offset:offset+100]))
            if full:np.testing.assert_array_equal(a.stored(),b.stored())
            return metrics
    def packet(self,address,target,track='rp',hops=0,data=99):
        return q.Cell(address=address,age=1,**{track+'_target':target,track+'_data':data,track+'_remaining':hops,track+'_valid':1})
    def test_real_ballistic_crossings_deliveries_drops_and_ring_wrap(self):
        target=p.layout().history(0,1,0)
        for track in ('lp','rp'):
            for hops in (0,1,3,7):
                for start in (0,f.Q-1):
                    for dt in (1, f.Q+17,8*f.Q):
                        self.compare({start:self.packet(start,target,track,hops)},dt)
        # More than fifteen colonies exercises the bounded source halo.
        self.compare({16*f.Q+f.Q-1:self.packet(f.Q-1,target,'rp',7)},7*f.Q,colonies=17)
    def test_actual_transmit_payloads_and_surviving_packets(self):
        source=p.layout().info[f.COL['s2_value']];target=p.layout().history(0,1,0)
        for direction in (0,1):
            logical={source:q.Cell(address=source,age=1,data=0x123456789ABCDEF0,head=1,phase=c.TRANSMIT,ra=source,rb=target,rd=2|direction)}
            self.compare(logical,1,full=True)
            self.compare(logical,f.Q+source+target,full=True)
    def test_receive_priority_and_latest_delivery_match_full_native(self):
        target=p.layout().history(0,1,0)
        logical={target-1:self.packet(target-1,target,'rp',data=123),target+1:self.packet(target+1,target,'lp',data=456)}
        with fast.World((r.Cell(),),age=1,logical=logical) as world:
            points=tuple(range(target-3,target+4))
            expected=tuple(native.local_step(world.physical_cells(tuple((a+j)%f.Q for j in f.NEIGHBORHOOD))) for a in points)
            world.batch(1);self.assertEqual(world.physical_cells(points),expected)
            self.assertEqual(world.logical_cells((target,))[0].data,123)
        logical[target+2]=self.packet(target+2,target,'lp',data=789)
        self.compare(logical,3,full=True)
    def test_atomic_rejection_of_protected_access_collision_and_capacity(self):
        target=p.layout().history(0,1,0);source=p.layout().info[0]
        cases=(
            {target:q.Cell(address=target,age=1,head=1,phase=c.READ_A,ra=target)},
            {target:q.Cell(address=target,age=1,head=1,phase=c.WRITE,rd=target,value=77)},
            {source:q.Cell(address=source,age=1,head=1,phase=c.TRANSMIT,ra=source,rb=target,rd=2,data=77),source-1:self.packet(source-1,target,'rp',1)},
            {i:self.packet(i,target,'rp',1) for i in range(100,133)},
            {100:self.packet(100,p.layout().info[0])},
        )
        for logical in cases:
            with fast.World((r.Cell(),),age=1,logical=logical) as world:
                before=world.stored()
                with self.assertRaises(RuntimeError):world.batch(3)
                self.assertEqual((world.age,world.time),(1,0));np.testing.assert_array_equal(world.stored(),before)
    def test_collision_fallback_retains_exact_physical_overwrite(self):
        source=p.layout().info[0];target=p.layout().history(0,1,0)
        logical={source:q.Cell(address=source,age=1,head=1,phase=c.TRANSMIT,ra=source,rb=target,rd=2,data=77),source-1:self.packet(source-1,target,'rp',1,data=11)}
        with fast.World((r.Cell(),),age=1,logical=logical) as a,slow.World((r.Cell(),),age=1,logical=logical) as b:
            metrics=a.advance(4);b.run(4)
            self.assertEqual(metrics['rejected_batches'],1);np.testing.assert_array_equal(a.stored(),b.stored())


if __name__=='__main__':unittest.main()
