import random
import unittest
from gacsca.fixed_rule import signal_rule as r,signal_native as native
from gacsca.fixed_rule.signal_world import SignalWorld,seed_signals


class SignalWorldTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.lib=native.library()

    def test_whole_state_sparse_execution_matches_complete_native_rule(self):
        rng=random.Random(3802)
        for age in (0,r.CAPTURE_AGE-2,96*r.Q-2,98*r.Q-2,r.U-2):
            positions=(*range(10),*range(r.Q-10,r.Q),*range(100,104))
            world=SignalWorld({p:rng.randrange(512) for p in positions},data={p:1 for p in positions[::2]},age=age)
            for _ in range(6):
                support={((p+j)%r.Q) for p in world.states for j in range(-5,6)}|set(world.data)|{r.Q//2}
                expected={p:native.local_step(tuple(world.record(p+j) for j in range(-5,6)),self.lib) for p in support}
                world.step()
                for p,out in expected.items():self.assertEqual(world.record(p),out)
                self.assertTrue(set(world.states).issubset(support))

    def test_capture_creates_signal_without_any_initial_signal_or_flags(self):
        data={p:1 for p in (*range(1,6),*range(r.Q-5,r.Q))}
        world=SignalWorld({},data=data,age=r.CAPTURE_AGE-2)
        world.step();self.assertEqual(world.states,{})
        world.step();self.assertEqual(world.states,seed_signals())
        world.run(6);self.assertEqual(world.states,seed_signals())

    def test_quiet_jump_has_event_and_actual_fixed_point_guards(self):
        data={p:1 for p in range(1,6)}
        fast=SignalWorld(seed_signals(),data=data,age=r.CAPTURE_AGE)
        slow=SignalWorld(seed_signals(),data=data,age=r.CAPTURE_AGE).run(20)
        fast.skip_quiet(20)
        self.assertEqual(fast.age,slow.age);self.assertEqual(fast.states,slow.states)
        self.assertEqual(fast.data,slow.data)
        for world,ticks in ((SignalWorld({},age=r.CAPTURE_AGE-1),1),
                            (SignalWorld(seed_signals(),age=96*r.Q-2),2),
                            (SignalWorld({100:1},age=r.CAPTURE_AGE),1),
                            (SignalWorld({100:16},age=r.CAPTURE_AGE),1)):
            with self.assertRaises(ValueError):world.skip_quiet(ticks)

    def test_signals_initiate_physical_workspace_and_flag_waves(self):
        world=SignalWorld(seed_signals(),age=96*r.Q-1)
        self.assertFalse(any(v&15 for v in world.states.values()))
        world.step()
        self.assertEqual(sum(bool(v&4) for v in world.states.values()),5)
        self.assertEqual(sum(bool(v&8) for v in world.states.values()),5)
        self.assertFalse(any(v&3 for v in world.states.values()))
        world.step()
        self.assertGreater(sum(bool(v&1) for v in world.states.values()),0)
        world.run(62)
        self.assertGreater(sum(bool(v&1) for v in world.states.values()),100)
        self.assertGreater(sum(bool(v&2) for v in world.states.values()),0)
        self.assertEqual(world.age,96*r.Q+63)


if __name__=='__main__':unittest.main()
