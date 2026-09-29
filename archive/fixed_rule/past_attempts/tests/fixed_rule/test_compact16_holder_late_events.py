"""Complete-state parity and rejection tests for late stationary-Signal events."""
import os
import unittest
import numpy as np
from gacsca.fixed_rule import compact16_holder_late_events as events,compact16_holder_canonical_gpu as canonical
from gacsca.fixed_rule import compact16_holder_rule as f,compact16_holder_literal_cone as cone
from gacsca.fixed_rule import compact16_holder_resident_independent as independent
from experiments.fixed_rule.audit_compact16_holder_dense_noise import restore
from experiments.fixed_rule.validate_compact16_holder_endpoint import guard


def saved(case=0):
    with np.load('figs/fixed_rule/compact16_holder_canonical_noise_v1.npz',allow_pickle=False) as z:return restore(z,case,16384)


def signals(raw,primary):
    raw[:,f.COL['signal']]=sum(np.roll(primary,-d)<<np.uint64(d+2) for d in f.OFFSETS)


@unittest.skipUnless(os.environ.get('FIXED_RULE_GPU_TESTS')=='1','explicit GPU opt-in')
class LateEvents(unittest.TestCase):
    def test_all_saved_states_complete_parity(self):
        for case in range(8):
            raw=saved(case)
            with self.subTest(case=case),events.World(raw) as fast,canonical.World(raw) as literal:
                np.testing.assert_array_equal(fast.raw(),raw)
                previous=0
                for tick in (1,2,32,128):
                    with guard():fast.advance(tick-previous);literal.run(tick-previous)
                    np.testing.assert_array_equal(fast.raw(),literal.read());previous=tick

    def test_period_and_inactive_boundaries(self):
        for age,ticks in ((f.ACTIVE_ENDS[-1]-2,4),(f.U-2,2)):
            raw=saved(6);raw[:,f.COL['age']]=age;wanted=raw
            for _ in range(ticks):wanted=cone.step(wanted)
            with events.World(raw) as world:
                with guard():world.advance(ticks)
                np.testing.assert_array_equal(world.raw(),wanted)
                if world.age==0:
                    for call in (lambda:world.advance(1),lambda:world.run(1),lambda:world.step()):
                        with self.assertRaises(ValueError):call()
                    np.testing.assert_array_equal(world.raw(),wanted)

    def test_signals_across_colony_seams(self):
        raw=np.concatenate((saved(0),saved(1)));primary=np.zeros(len(raw),dtype=np.uint64)
        primary[[0,3,f.Q-1,f.Q,f.Q+3120,2*f.Q-1]]=1;signals(raw,primary)
        with events.World(raw) as world:
            wanted=raw
            for _ in range(3):wanted=cone.step(wanted)
            with guard():world.advance(3)
            np.testing.assert_array_equal(world.raw(),wanted)

    def test_two_head_reflection_and_merge(self):
        raw=saved(4);positions=np.flatnonzero(raw[:,f.COL['s2_head']]);self.assertEqual(len(positions),2)
        for name,_ in f.PROCEDURE:
            if name=='data' or name.startswith(('lp_','rp_')):continue
            values=raw[positions,f.COL['s2_'+name]].copy();primary=np.zeros(f.Q,dtype=np.uint64);primary[[10,25]]=values
            for d in f.OFFSETS:raw[:,f.COL[f's{d+2}_{name}']]=np.roll(primary,-d)
        with events.World(raw) as fast,canonical.World(raw) as literal:
            with self.assertRaises(independent.BatchRejected):fast.batch(64)
            np.testing.assert_array_equal(fast.raw(),raw)
            with guard():metrics=fast.advance(128);literal.run(128)
            np.testing.assert_array_equal(fast.raw(),literal.read())
            self.assertGreater(metrics['synchronous_literal_ticks'],0)

    def test_domain_rejection(self):
        raw=saved(0)
        for name in ('signal','s0_data','f1','w1_wf2','address','age','p3_index'):
            changed=raw.copy();changed[7,f.COL[name]]^=np.uint64(1)
            with self.subTest(field=name),self.assertRaises(ValueError):events.World(changed)
        changed=raw.copy()
        for d in f.OFFSETS:changed[(100-d)%f.Q,f.COL[f's{d+2}_lp_valid']]=1
        with self.assertRaises(ValueError):events.World(changed)


if __name__=='__main__':unittest.main()
