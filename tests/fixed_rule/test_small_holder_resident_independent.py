import unittest
from unittest.mock import patch

import numpy as np

from gacsca.fixed_rule import small_holder_resident_independent as independent
from gacsca.fixed_rule import small_holder_resident_period as synchronous
from gacsca.fixed_rule import small_holder_core as c, small_holder_rule as f
from gacsca.fixed_rule import small_holder_projected as r, small_holder_quotient as q
from gacsca.fixed_rule import small_holder_program as p, small_holder_native as native
from gacsca.fixed_rule.wordcode import Program


class IndependentPhysical(unittest.TestCase):
    def compare(self, logical, ticks, colonies=1, age=1):
        parents=tuple(r.Cell(address=i) for i in range(colonies))
        with independent.World(parents,age=age,logical=logical) as fast, synchronous.World(parents,age=age,logical=logical) as slow:
            with patch.object(Program,'evaluate',side_effect=AssertionError('host evaluator')),patch.object(f,'local_step',side_effect=AssertionError('host upper rule')):
                metrics=fast.batch(ticks)
            slow.run(ticks)
            self.assertEqual(fast.age,slow.age)
            np.testing.assert_array_equal(fast.stored(),slow.stored())
            # Include physical reconstruction at both colony boundaries and
            # the moving controller; stored rows alone are not raw states.
            probes=tuple(col*f.Q+a for col in range(colonies) for a in (0,1,5,100,p.layout().computation_cells-1,f.Q-5,f.Q-1))
            self.assertEqual(fast.physical_cells(probes),slow.physical_cells(probes))
            return metrics

    def test_distinct_metadata_queries_use_independent_event_times(self):
        count=8
        logical={i*f.Q:q.Cell(address=0,age=1,head=1,phase=c.READ_META,ra=200,rb=1,rd=i,value=1) for i in range(count)}
        metrics=self.compare(logical,count+8,count)
        self.assertEqual(metrics['colony_literal_ticks'],count)
        self.assertEqual(metrics['max_colony_literal_ticks'],1)

    def test_actual_instruction_fetch_read_write_wait_halt_and_reflection(self):
        rom=p.base_rom();g=p.layout()
        # Real hard-wired opcodes, not a separate toy ROM or interpreter.
        kinds=sorted(set(map(int,rom[g.memory_count:-1,0])))
        for kind in kinds:
            pc=next(i for i,row in enumerate(rom[g.memory_count:-1]) if row[0]==kind)
            a=g.memory_count+pc
            logical={a:q.Cell(address=a,age=1,head=1,phase=c.FETCH,pc=pc,rd=3 if kind==c.WAIT else 0)}
            # SEND merely fetches here; stop before it can emit a packet.
            self.compare(logical,2 if kind==c.SEND else 2*f.Q+23)
        self.compare({0:q.Cell(age=1,head=1,direction=1,phase=c.READ_META,ra=3,rb=2,rd=f.Q-3,value=1)},2*f.Q+23)

    def test_all_noncommunicating_active_phases_and_raw_native_event(self):
        for phase in (c.READ_A,c.READ_B,c.WRITE,c.READ_LOAD,c.READ_META,c.WAIT_META):
            logical={5:q.Cell(address=5,age=1,head=1,phase=phase,ra=5,rb=5,rd=5,value=123,alu=1,data=19)}
            self.compare(logical,3*f.Q+17)
        with independent.World((r.Cell(),),age=1,logical={5:q.Cell(address=5,age=1,head=1,phase=c.WRITE,rd=5,value=123)}) as world:
            points=tuple(range(1,11))
            expected=tuple(native.local_step(world.physical_cells(tuple((a+j)%f.Q for j in f.NEIGHBORHOOD))) for a in points)
            world.batch(1)
            self.assertEqual(world.physical_cells(points),expected)

    def test_stationary_signals_survive_independent_control(self):
        logical={a:q.Cell(address=a,age=1,signal=1<<(5-a)) for a in range(1,6)}
        logical.update({a:q.Cell(address=a,age=1,signal=1<<(f.Q-1-a)) for a in range(f.Q-5,f.Q)})
        logical[0]=q.Cell(age=1,head=1,phase=c.READ_META,ra=200,rb=1,rd=100,value=1)
        self.compare(logical,f.Q+100)

    def test_rejections_leave_data_controller_and_clock_unchanged(self):
        cases=(
            ({5:q.Cell(address=5,age=1,head=1,phase=c.TRANSMIT,ra=5,rb=7,data=99)},1,200000),
            ({5:q.Cell(address=5,age=1,head=1,phase=c.WRITE,rd=5,value=123)},2*f.Q,1),
            ({5:q.Cell(address=5,age=1,head=1),6:q.Cell(address=6,age=1,head=1)},3,200000),
            ({5:q.Cell(address=5,age=1,lp_data=8)},3,200000),
            ({5:q.Cell(address=5,age=1,phase=2)},3,200000),
            ({5:q.Cell(address=5,age=1,signal=1)},3,200000),
        )
        for logical,ticks,budget in cases:
            with independent.World((r.Cell(),),age=1,logical=logical) as world:
                before=world.stored()
                with self.assertRaises(RuntimeError):world.batch(ticks,event_budget=budget)
                self.assertEqual((world.time,world.age),(0,1))
                np.testing.assert_array_equal(world.stored(),before)
        with independent.World((r.Cell(),),age=f.ACTIVE_ENDS[0]-1) as world:
            with self.assertRaises(RuntimeError):world.batch(2)
            self.assertEqual(world.time,0)
        with independent.World((r.Cell(),),age=0) as world:
            with self.assertRaises(RuntimeError):world.batch(1)
            self.assertEqual(world.time,0)


if __name__=='__main__':unittest.main()


class IndependentIntegration(unittest.TestCase):
    def test_mail_fallback_barriers_and_wrap_match_synchronous(self):
        cases=(
            (1,{5:q.Cell(address=5,age=1,head=1,phase=c.TRANSMIT,ra=5,rb=7,data=99)},100),
            (f.ACTIVE_ENDS[0]-3,{0:q.Cell(age=f.ACTIVE_ENDS[0]-3,head=1)},8),
            (f.RESET_AGES[1]-2,{},5),
        )
        for age,logical,ticks in cases:
            with independent.World((r.Cell(),),age=age,logical=logical) as fast,synchronous.World((r.Cell(),),age=age,logical=logical) as slow:
                result=fast.advance(ticks,chunk=13);slow.run(ticks)
                np.testing.assert_array_equal(fast.stored(),slow.stored())
                self.assertEqual(result['physical_ticks'],ticks)
                self.assertEqual(ticks,result['independent_ticks']+result['synchronous_literal_ticks']+result['synchronous_transport_or_quiet_ticks'])
                if logical and age==1:self.assertGreater(result['rejected_batches'],0)
        with synchronous.World((r.Cell(),)) as initial:state=initial.stored()
        state[:,q.COL['age']]=f.U-2
        with independent.World.from_stored(state) as fast,synchronous.World.from_stored(state) as slow:
            fast.advance(5);slow.run(5)
            np.testing.assert_array_equal(fast.stored(),slow.stored())
            self.assertEqual((fast.time,fast.age),(5,3))

    def test_suffix_with_active_flag1_preserves_complete_controller(self):
        from gacsca.fixed_rule import small_holder_flag_profile as profile
        with synchronous.World((r.Cell(),)) as initial:state=initial.stored()
        age=f.WF_START+11000;g=p.layout()
        addresses=[*range(g.computation_cells),*range(f.Q-5,f.Q)]
        state[:,q.COL['age']]=age
        state[:,[q.COL[x] for x in ('f1','f2','wf1','wf2')]]=np.array([profile.bits(age,a) for a in addresses])
        state[-5:,q.COL['signal']]=[16,8,4,2,1]
        state[100,q.COL['head']]=1;state[100,q.COL['phase']]=c.WRITE
        state[100,q.COL['rd']]=100;state[100,q.COL['value']]=0x987654321
        with independent.World.from_stored(state) as fast,synchronous.World.from_stored(state) as slow:
            self.assertTrue(fast.physical_cells((100,))[0].f1)
            fast.batch(3000);slow.run(3000)
            np.testing.assert_array_equal(fast.stored(),slow.stored())
            self.assertEqual(fast.physical_cells(tuple(range(94,108))),slow.physical_cells(tuple(range(94,108))))
            self.assertEqual(fast.logical_cells((100,))[0].data,0x987654321)
