"""Raw committed-state reset and complete capture/flag-boundary composition."""
import os
import unittest
import numpy as np
from gacsca.fixed_rule import compact16_holder_coherent_epochs as epochs,compact16_holder_canonical_gpu as canonical
from gacsca.fixed_rule import compact16_holder_rule as f,compact16_holder_literal_cone as cone
from tests.fixed_rule.test_compact16_holder_late_events import signals,saved
from experiments.fixed_rule.validate_compact16_holder_endpoint import guard


def committed(case):
    if case==4:
        with np.load('figs/fixed_rule/compact16_holder_mail_macrostep_v1.npz',allow_pickle=False) as z:return z['postcommit'].copy()
    with np.load(f'figs/fixed_rule/compact16_holder_all_noise_macrosteps_v2_case{case}.npz',allow_pickle=False) as z:return z[f'case{case}_postcommit'].copy()


@unittest.skipUnless(os.environ.get('FIXED_RULE_GPU_TESTS')=='1','explicit GPU opt-in')
class Epochs(unittest.TestCase):
    def test_all_eight_raw_commits_reset_without_decoding(self):
        for case in range(8):
            raw=committed(case)
            with self.subTest(case=case),epochs.World(raw=raw) as world,canonical.World(raw) as literal:
                np.testing.assert_array_equal(world.raw(),raw)
                with guard():world.advance(1);literal.run(1)
                np.testing.assert_array_equal(world.raw(),cone.step(raw));np.testing.assert_array_equal(world.raw(),literal.read())
                with guard():world.advance(127);literal.run(127)
                np.testing.assert_array_equal(world.raw(),literal.read())

    def test_capture_can_use_literal_signal_repair(self):
        raw=committed(0);raw[:,f.COL['age']]=f.CAPTURE_AGE-2
        with epochs.World(raw=raw) as world:
            wanted=raw
            for _ in range(4):
                wanted=cone.step(wanted)
                with guard():world.advance(1)
                np.testing.assert_array_equal(world.raw(),wanted)

    def test_complete_both_signal_flag_interval(self):
        raw=committed(3);raw[:,f.COL['age']]=f.WF_START-2
        primary=np.zeros(f.Q,dtype=np.uint64);primary[[3,3100,f.Q-3]]=1;signals(raw,primary)
        with epochs.World(raw=raw) as world,canonical.World(raw) as literal:
            for age in (f.WF_START-1,f.WF_START,f.WF_START+1,f.WF_END-1,f.WF_END,f.WF_END+f.Q):
                amount=age-world.age
                with guard():world.advance(amount);literal.run(amount)
                np.testing.assert_array_equal(world.raw(),literal.read())
            self.assertIsNone(world._flags)

    def test_inactive_opposing_heads_do_not_limit_time_jump(self):
        raw=saved(4);raw[:,f.COL['age']]=f.ACTIVE_ENDS[-1]+1
        heads=np.flatnonzero(raw[:,f.COL['s2_head']]);self.assertEqual(len(heads),2)
        for d in f.OFFSETS:
            raw[(heads[0]-d)%f.Q,f.COL[f's{d+2}_direction']]=0
            raw[(heads[1]-d)%f.Q,f.COL[f's{d+2}_direction']]=1
        with epochs.World(raw=raw) as world:
            amount=f.U-1-world.age
            with guard():metrics=world.advance(amount)
            wanted=raw.copy();wanted[:,f.COL['age']]=f.U-1
            np.testing.assert_array_equal(world.raw(),wanted)
            self.assertEqual(metrics['synchronous_literal_ticks'],0)
            self.assertEqual(metrics['synchronous_transport_or_quiet_ticks'],amount)

    def test_flag_interval_restore_and_mail_guard(self):
        raw=committed(3);raw[:,f.COL['age']]=f.WF_START
        with self.assertRaises(ValueError):epochs.World(raw=raw)
        raw[:,f.COL['age']]=f.WF_START-2
        for d in f.OFFSETS:raw[(100-d)%f.Q,f.COL[f's{d+2}_lp_valid']]=1
        with epochs.World(raw=raw) as world:
            world.advance(1);before=world.raw()
            with self.assertRaises((RuntimeError,ValueError)):world.advance(1)
            np.testing.assert_array_equal(world.raw(),before)


if __name__=='__main__':unittest.main()
