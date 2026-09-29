"""Full-state parity of canonical factorization, including damaged raw replicas."""
import os
import unittest
from unittest.mock import patch
import numpy as np
from gacsca.fixed_rule import compact16_holder_canonical_gpu as gpu
from gacsca.fixed_rule import compact16_holder_literal_cone as cone
from gacsca.fixed_rule import compact16_holder_rule as f
from experiments.fixed_rule.validate_compact16_holder_endpoint import guard
from experiments.fixed_rule.audit_compact16_holder_dense_noise import restore


def random_raw(age,n=f.Q):
    rng=np.random.default_rng(2026092801+age);raw=rng.bit_generator.random_raw((n,f.FIELDS))
    for k,(_,width) in enumerate(f.SCHEMA):
        if width<64:raw[:,k]&=np.uint64((1<<width)-1)
    raw[:,f.COL['address']]=np.arange(n)%f.Q;raw[:,f.COL['age']]=age
    return cone.normalize(raw)


@unittest.skipUnless(os.environ.get('FIXED_RULE_GPU_TESTS')=='1','explicit GPU opt-in')
class Canonical(unittest.TestCase):
    def test_arbitrary_complete_states_across_clock_events(self):
        clocks=sorted({0,1,f.U-2,f.U-1,508479339,*(max(0,x-1) for x in (*f.RESET_AGES,*f.ACTIVE_ENDS,*f.VOTE_AGES,f.CAPTURE_AGE,f.WF_START,f.WF_END))})
        for age in clocks:
            with self.subTest(age=age):
                raw=random_raw(age)
                with gpu.World(raw) as world:
                    np.testing.assert_array_equal(world.read(),raw)
                    for _ in range(2):
                        raw=cone.step(raw)
                        with guard(),patch.object(cone,'step',side_effect=AssertionError('host transition')):world.run(1)
                        np.testing.assert_array_equal(world.read(),raw)

    def test_saved_nonzero_fronts_to_full_literal_checkpoints(self):
        with np.load('figs/fixed_rule/compact16_holder_dense_noise_v1.npz',allow_pickle=False) as z:
            for case in range(8):
                with self.subTest(case=case):
                    with gpu.World(restore(z,case,32)) as world:
                        previous=32
                        for tick in (128,511,512):
                            with guard():world.run(tick-previous)
                            np.testing.assert_array_equal(world.read(),restore(z,case,tick));previous=tick

    def test_multicolony_seam(self):
        raw=random_raw(f.WF_START-1,2*f.Q)
        with gpu.World(raw,device_budget=128*1024**2) as world:
            for _ in range(2):
                raw=cone.step(raw);world.run(1);np.testing.assert_array_equal(world.read(),raw)

    def test_domain_rejections(self):
        raw=random_raw(1)
        for name,value in (('address',7),('age',2),('p3_index',9),('s2_phase',8)):
            changed=raw.copy();changed[3,f.COL[name]]=value
            with self.subTest(field=name),self.assertRaises(ValueError):gpu.World(changed)
        with self.assertRaises(ValueError):gpu.World(raw[:-1])
        with self.assertRaises(RuntimeError):gpu.World(raw,device_budget=1)


if __name__=='__main__':unittest.main()
