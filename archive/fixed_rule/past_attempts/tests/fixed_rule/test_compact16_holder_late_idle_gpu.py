"""Exact idle shortcut, interval boundaries and atomic domain rejection."""
import os
import unittest
import numpy as np
from gacsca.fixed_rule import compact16_holder_canonical_gpu as gpu,compact16_holder_late_idle_gpu as idle
from gacsca.fixed_rule import compact16_holder_rule as f,compact16_holder_literal_cone as cone
from experiments.fixed_rule.validate_compact16_holder_endpoint import guard
from tests.fixed_rule.test_compact16_holder_canonical_gpu import random_raw


def idle_raw(age):
    raw=random_raw(age);rng=np.random.default_rng(2026092802);data=rng.bit_generator.random_raw(f.Q);bits=rng.integers(0,2,f.Q,dtype=np.uint64)
    for d in f.OFFSETS:
        for name,_ in f.PROCEDURE:raw[:,f.COL[f's{d+2}_{name}']]=np.roll(data,-d) if name=='data' else 0
        for name in ('wf1','wf2'):raw[:,f.COL[f'w{d+2}_{name}']]=0
    raw[:,f.COL['f1']]=raw[:,f.COL['f2']]=0
    raw[:,f.COL['signal']]=sum(np.roll(bits,-d)<<np.uint64(d+2) for d in f.OFFSETS)
    return raw


@unittest.skipUnless(os.environ.get('FIXED_RULE_GPU_TESTS')=='1','explicit GPU opt-in')
class Idle(unittest.TestCase):
    def test_literal_parity_and_commit_boundary(self):
        for age in (idle.LAST_EVENT+1,f.ACTIVE_ENDS[-1]-1,f.U-3):
            raw=idle_raw(age);ticks=min(64,f.U-1-age)
            # Native literal reference, including the active/inactive boundary.
            expected=raw
            for _ in range(ticks):expected=cone.step(expected)
            with gpu.World(raw) as world:
                with guard():idle.advance(world,ticks)
                np.testing.assert_array_equal(world.read(),expected)
                self.assertEqual(world.age,age+ticks)
                if world.age==f.U-1:
                    with guard():world.run(1)
                    np.testing.assert_array_equal(world.read(),cone.step(expected))

    def test_long_advance_preserves_every_nonclock_word(self):
        raw=idle_raw(idle.LAST_EVENT+1)
        with gpu.World(raw) as world:
            with guard():idle.advance(world,f.U-1-world.age)
            expected=raw.copy();expected[:,f.COL['age']]=f.U-1
            np.testing.assert_array_equal(world.read(),expected)
            with self.assertRaises(ValueError):idle.advance(world,1)
            np.testing.assert_array_equal(world.read(),expected)

    def test_bad_complete_state_rejected_without_mutation(self):
        raw=idle_raw(idle.LAST_EVENT+1)
        for name in ('s2_head','s2_pc','s2_lp_valid','s2_data','f1','f2','w0_wf1','signal'):
            changed=raw.copy();changed[17,f.COL[name]]^=np.uint64(1)
            with self.subTest(field=name),gpu.World(changed) as world:
                with self.assertRaises(ValueError):idle.advance(world,10)
                self.assertEqual(world.time,0);np.testing.assert_array_equal(world.read(),changed)
        with gpu.World(idle_raw(idle.LAST_EVENT)) as world:
            with self.assertRaises(ValueError):idle.advance(world,1)


if __name__=='__main__':unittest.main()
