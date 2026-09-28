"""Complete packet retention, delivery, collision and sparse event parity."""
import os
import unittest
import numpy as np
from gacsca.fixed_rule import compact16_holder_late_mail_events as mail,compact16_holder_canonical_gpu as canonical
from gacsca.fixed_rule import compact16_holder_rule as f,compact16_holder_literal_cone as cone
from tests.fixed_rule.test_compact16_holder_late_events import saved
from experiments.fixed_rule.validate_compact16_holder_endpoint import guard


def put(raw,pos,name,value):
    for d in f.OFFSETS:raw[(pos-d)%len(raw),f.COL[f's{d+2}_{name}']]=value


@unittest.skipUnless(os.environ.get('FIXED_RULE_GPU_TESTS')=='1','explicit GPU opt-in')
class Mail(unittest.TestCase):
    def test_cross_colony_delivery_and_priorities(self):
        raw=np.concatenate((saved(3),saved(7)))
        for pos,direction,target,payload,remaining in ((0,'lp',f.Q-3,17,1),(f.Q-1,'rp',3,29,1),(2,'rp',3,41,0),(4,'lp',3,53,0)):
            for name,value in (('target',target),('data',payload),('remaining',remaining),('valid',1)):put(raw,pos,direction+'_'+name,value)
        for name,value in (('head',1),('phase',3),('rd',3),('value',67)):put(raw,3,name,value)
        wanted=raw
        with mail.World(raw) as world:
            np.testing.assert_array_equal(world.raw(),raw)
            for _ in range(8):
                wanted=cone.step(wanted)
                with guard():world.advance(1)
                np.testing.assert_array_equal(world.raw(),wanted)

    def test_actual_emission_and_two_colony_length_interval(self):
        with np.load('figs/fixed_rule/compact16_holder_all_noise_macrosteps_v2_case4.npz',allow_pickle=False) as z:raw=z['case4_stopped_raw'].copy()
        with mail.World(raw) as fast,canonical.World(raw) as literal:
            previous=0
            for tick in (1,128,2*f.Q):
                with guard():metrics=fast.advance(tick-previous);literal.run(tick-previous)
                np.testing.assert_array_equal(fast.raw(),literal.read());previous=tick
            self.assertGreater(metrics['synchronous_transport_or_quiet_ticks'],f.Q)

    def test_invalid_packet_residue_evolves_and_bad_replica_rejected(self):
        raw=saved(3);put(raw,100,'rp_target',19)
        with mail.World(raw) as world:
            with guard():world.advance(1)
            np.testing.assert_array_equal(world.raw(),cone.step(raw))
        for name,value in (('s0_lp_remaining',8),('s1_lp_target',17)):
            changed=raw.copy();changed[101,f.COL[name]]=value
            with self.subTest(field=name),self.assertRaises(ValueError):mail.World(changed)


if __name__=='__main__':unittest.main()
