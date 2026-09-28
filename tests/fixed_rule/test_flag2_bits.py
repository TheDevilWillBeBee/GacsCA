import unittest
from gacsca.fixed_rule import delivery_rule as r
from gacsca.fixed_rule.flag2_bits import Flag2Bits
from gacsca.fixed_rule.canonical_flag_world import FlagProjection


class Flag2BitsTests(unittest.TestCase):
    def test_bitplanes_match_literal_local_physical_projection(self):
        for age in (96*r.Q+1,98*r.Q-2,100*r.Q):
            bits=(1<<100)|(1<<106)|7
            fast=Flag2Bits(bits,age=age)
            states={p:2 for p in range(bits.bit_length()) if (bits>>p)&1}
            if fast.wf2:
                for p in range(5):states[p]=states.get(p,0)|8
            slow=FlagProjection(states,age=age)
            for _ in range(80):
                fast.step();slow.step()
                expected=sum(1<<p for p,v in slow.states.items() if v&2)
                self.assertEqual(fast.bits,expected);self.assertEqual(fast.age,slow.age)

    def test_window_initiation_cutoff_and_nonrigid_profile(self):
        world=Flag2Bits();world.step();self.assertTrue(world.wf2);self.assertEqual(world.bits,0)
        world.step();self.assertEqual(world.bits,255)
        values=[]
        for _ in range(260):
            values.append((world.bits.bit_length(),world.bits.bit_count()));world.step()
        self.assertTrue(any(length!=count for length,count in values))
        world=Flag2Bits(age=98*r.Q-1);world.step()
        self.assertFalse(world.wf2);self.assertEqual(world.bits,255)
        world.step();self.assertNotEqual(world.bits,255)
        with self.assertRaises(ValueError):Flag2Bits(age=79*r.Q)


if __name__=='__main__':unittest.main()
