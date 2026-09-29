"""Complete G parity on arbitrary physical states, locality and input guards."""
import os
import random
import unittest
from unittest.mock import patch
import numpy as np
from gacsca.fixed_rule import compact16_holder_dense_gpu as gpu, compact16_holder_literal_cone as cone
from gacsca.fixed_rule import compact16_holder_rule as f, compact16_holder_projected as r
from experiments.fixed_rule.validate_compact16_holder_endpoint import guard


def random_raw(n):
    rng=random.Random(2026092782+n)
    return np.array([f.encode_cell(r.lift(r.Cell(**{name:rng.getrandbits(width) for name,width in r.SCHEMA}))) for _ in range(n)],dtype=np.uint64)


@unittest.skipUnless(os.environ.get('FIXED_RULE_GPU_TESTS')=='1','explicit GPU opt-in')
class Dense(unittest.TestCase):
    def test_arbitrary_complete_states_and_small_rings(self):
        for n in (1,17,257):
            raw=random_raw(n)
            with gpu.World(raw) as world:
                np.testing.assert_array_equal(world.read(),raw)
                for _ in range(3):
                    raw=cone.step(raw)
                    with guard(),patch.object(cone,'step',side_effect=AssertionError('host physical transition')):world.run(1)
                    np.testing.assert_array_equal(world.read(),raw)
                self.assertEqual(world.time,3)

    def test_saved_nonzero_fronts_and_controllers(self):
        with np.load('figs/fixed_rule/compact16_holder_literal_noise_v1.npz',allow_pickle=False) as z:
            for case in ('rate2_trial0_final','rate2_trial2_final'):
                raw=z[case].copy()
                with gpu.World(raw) as world:
                    for _ in range(4):
                        raw=cone.step(raw)
                        with guard():world.run(1)
                        np.testing.assert_array_equal(world.read(),raw)

    def test_radius_seven(self):
        raw=random_raw(41);changed=raw.copy();changed[0]=random_raw(1)[0]
        with gpu.World(raw) as first,gpu.World(changed) as second:
            first.run(1);second.run(1)
            np.testing.assert_array_equal(first.read()[8:34],second.read()[8:34])

    def test_bad_raw_state_or_budget_rejected(self):
        raw=random_raw(1);changed=raw.copy();changed[0,f.COL['address']]=1<<15
        with self.assertRaises(ValueError):gpu.World(changed)
        changed=raw.copy();changed[0,f.COL['p3_index']]^=np.uint64(1)
        with self.assertRaises(ValueError):gpu.World(changed)
        with self.assertRaises(RuntimeError):gpu.World(raw,device_budget=1)


if __name__=='__main__':unittest.main()
