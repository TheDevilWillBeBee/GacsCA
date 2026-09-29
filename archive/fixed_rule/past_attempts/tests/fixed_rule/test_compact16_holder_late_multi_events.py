"""Collision-aware transport parity, including a deliberately unsafe mutation."""
import os
import unittest
import numpy as np
from gacsca.fixed_rule import compact16_holder_late_multi_events as multi,compact16_holder_canonical_gpu as canonical
from gacsca.fixed_rule import compact16_holder_rule as f
from tests.fixed_rule.test_compact16_holder_late_events import saved
from experiments.fixed_rule.validate_compact16_holder_endpoint import guard


def heads(positions,directions):
    raw=saved(4)
    for name,_ in f.PROCEDURE:
        if name=='data' or name.startswith(('lp_','rp_')):continue
        primary=np.zeros(f.Q,dtype=np.uint64)
        if name=='head':primary[positions]=1
        if name=='direction':primary[positions]=directions
        if name=='pc':primary[positions]=2**30
        for d in f.OFFSETS:raw[:,f.COL[f's{d+2}_{name}']]=np.roll(primary,-d)
    return raw


@unittest.skipUnless(os.environ.get('FIXED_RULE_GPU_TESTS')=='1','explicit GPU opt-in')
class Multi(unittest.TestCase):
    def test_two_and_three_head_interactions(self):
        cases=(([100,104],[0,1]),([100,103],[0,1]),([100,101],[0,0]),([10,25],[1,1]),([100,108,116],[0,1,1]))
        for positions,directions in cases:
            raw=heads(positions,directions)
            with self.subTest(positions=positions,directions=directions),multi.World(raw) as fast,canonical.World(raw) as literal:
                previous=0
                for tick in (1,4,16,64):
                    with guard():fast.run(tick-previous);literal.run(tick-previous)
                    np.testing.assert_array_equal(fast.raw(),literal.read());previous=tick

    def test_actual_two_head_full_colony_interval(self):
        raw=saved(4)
        with multi.World(raw) as fast,canonical.World(raw) as literal:
            with guard():metrics=fast.advance(f.Q);literal.run(f.Q)
            np.testing.assert_array_equal(fast.raw(),literal.read())
            self.assertGreater(metrics['synchronous_transport_or_quiet_ticks'],f.Q//2)
            self.assertLess(metrics['synchronous_literal_ticks'],100)

    def test_omitting_pair_bound_changes_the_actual_transition(self):
        raw=heads([100,104],[0,1])
        with multi.World(raw) as unsafe,canonical.World(raw) as literal:
            unsafe.lib=multi.library(unsafe=True)
            with guard():unsafe.run(4);literal.run(4)
            self.assertFalse(np.array_equal(unsafe.raw(),literal.read()))
            self.assertEqual(np.count_nonzero(unsafe.raw()[:,f.COL['s2_head']]),2)
            self.assertEqual(np.count_nonzero(literal.read()[:,f.COL['s2_head']]),1)


if __name__=='__main__':unittest.main()
