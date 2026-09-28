import unittest
from gacsca.fixed_rule import retimed_holder_core as c, retimed_holder_rule as f
from experiments.fixed_rule.finish_retimed_holder_geometry_flags import flag_step,interval_step,interval_bits


class GeometryFlags(unittest.TestCase):
    def test_all_eight_bit_patterns_match_scalar_maintenance(self):
        for bits in range(256):
            expected=0
            for site in range(8):
                cells=tuple(c.Cell(address=(site+j)%f.Q,age=1024,
                                   f1=((bits >> (site+j))&1) if 0<=site+j<8 else 0) for j in range(-5,6))
                out=c.maintenance(cells)
                self.assertEqual(out['address'],site);self.assertEqual(out['f2'],0)
                expected|=out['f1'] << site
            self.assertEqual(flag_step(bits),expected)

    def test_all_short_intervals_and_boundary_intervals(self):
        for base in (0,100,f.Q-20):
            for left in range(base,base+10):
                for right in range(left,base+10):
                    self.assertEqual(flag_step(interval_bits(left,right)),interval_bits(*interval_step(left,right)))

    def test_two_flags_do_not_create_a_spurious_interval(self):
        self.assertEqual(interval_step(100,101),(None,None))
        self.assertEqual(flag_step(3 << 100),0)


if __name__=='__main__':unittest.main()
