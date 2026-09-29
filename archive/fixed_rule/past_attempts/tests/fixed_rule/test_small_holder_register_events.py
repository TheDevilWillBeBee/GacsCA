import random
import unittest
from unittest.mock import patch
import numpy as np
from gacsca.fixed_rule import small_holder_register_events as fast
from gacsca.fixed_rule import small_holder_resident_gather as reference
from gacsca.fixed_rule import small_holder_core as c, small_holder_rule as f
from gacsca.fixed_rule import small_holder_projected as r, small_holder_quotient as q
from gacsca.fixed_rule import small_holder_program as p
from gacsca.fixed_rule.small_holder_prefix_description import build
from gacsca.fixed_rule.wordcode import Program


class RegisterEvents(unittest.TestCase):
    def test_slice_retains_exact_consumed_expressions(self):
        # Width-valid arbitrary neighborhoods: no initial-state specialization.
        rng = random.Random(260926)
        original, sliced = build(), fast.event_program()
        for _ in range(120):
            words = tuple(rng.getrandbits(w) for _ in range(11) for _,w in c.SCHEMA)
            expected = original.evaluate(words)
            self.assertEqual(sliced.evaluate(words),tuple(expected[c.COL[n]] for n in fast.EVENT_FIELDS))
        self.assertEqual(sliced.inputs,original.inputs)
        self.assertEqual(len(sliced.operations),1564)
        self.assertEqual(f.self_description().digest(),'af2de0673ac685bb83e8a319751b7f10e22c05037809ff0479bdf292a789fbb6')

    def test_complete_active_event_checkpoints(self):
        source = p.layout().info[f.COL['s2_value']]
        target = p.layout().history(0,1,0)
        cases = [
            (1,source,dict(head=1,phase=c.TRANSMIT,ra=source,rb=target,rd=2,data=0x123456789ABCDEF0),2*f.Q),
            (c.VOTE_AGES[0]+1,source,dict(head=1,phase=c.WRITE,rd=source,value=(1<<64)-1),f.Q),
            (c.VOTE_AGES[0]+1,0,dict(head=1,direction=1,phase=c.READ_META,rd=f.Q-2,ra=source,rb=2,value=1),3*f.Q),
            (c.VOTE_AGES[0]+1,0,dict(head=1,direction=1,phase=c.WAIT_META,rd=source,value=555),3*f.Q),
        ]
        for age,at,fields,ticks in cases:
            logical={at:q.Cell(address=at,age=age,**fields)}
            with fast.World((r.Cell(),)*3,age=1,logical={at:q.Cell(address=at,age=1,**fields)}) as a,reference.World((r.Cell(),)*3,age=1,logical={at:q.Cell(address=at,age=1,**fields)}) as b:
                if age!=1:
                    for world in (a,b):
                        self.assertEqual(world.lib.rp_restore_age(world.handle,age),0)
                        world.age=age
                with patch.object(Program,'evaluate',side_effect=AssertionError('host evaluator')),patch.object(f,'local_step',side_effect=AssertionError('host upper rule')):
                    ma=a.batch(ticks); mb=b.batch(ticks)
                self.assertEqual(ma,mb)
                np.testing.assert_array_equal(a.stored(),b.stored())

    def test_atomic_rejection_and_actual_fallback(self):
        source=p.layout().info[0]; target=p.layout().history(0,1,0)
        logical={source:q.Cell(address=source,age=1,head=1,phase=c.TRANSMIT,ra=source,rb=target,rd=2,data=77),source-1:q.Cell(address=source-1,age=1,rp_target=target,rp_data=11,rp_remaining=1,rp_valid=1)}
        with fast.World((r.Cell(),),age=1,logical=logical) as a,reference.World((r.Cell(),),age=1,logical=logical) as b:
            initial=a.stored()
            with self.assertRaises(RuntimeError):a.batch(4)
            self.assertEqual((a.age,a.time),(1,0))
            np.testing.assert_array_equal(a.stored(),initial)
            ma=a.advance(4); mb=b.advance(4)
            self.assertEqual(ma,mb)
            np.testing.assert_array_equal(a.stored(),b.stored())

if __name__=='__main__':unittest.main()
