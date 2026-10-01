"""Native complete-F backend must agree with the literal fixed local rule."""
import unittest

from gacsca.fixed_rule import spatial_epoch8 as spatial
from gacsca.fixed_rule import stream28_dual_pass20 as physical
from gacsca.fixed_rule import stream28_dual_holder_rule20 as holder
from gacsca.fixed_rule import stream28_dual_native20 as native
from experiments.fixed_rule.certify_stream28_dual_pass20 import neighborhood


class NativeFixedRuleTest(unittest.TestCase):
    def test_local_clock_vote_early_final_and_boundary(self):
        ages=(0,holder.RESET_AGES[1],holder.RESET_AGES[2],
              holder.VOTE_AGES[0],physical.EARLY_CAPTURE_AGE,
              physical.EARLY_RUN_START+120,physical.EARLY_RUN_STOP,
              holder.CAPTURE_AGE,holder.RESET_AGES[4]+100,
              physical.U-1)
        for age in ages:
            for site in (0,2496,3218,8191):
                rows=neighborhood(site,age,source=0x1234,
                                  output=age in (physical.EARLY_RUN_START+120,
                                                 holder.RESET_AGES[4]+100),
                                  value=0xA5)
                self.assertEqual(native.local_step(rows),
                                 physical.local_step(rows),(site,age))

    def test_ring_uses_only_the_fixed_radius_seven_rule(self):
        age=physical.EARLY_CAPTURE_AGE
        cells=tuple(physical.Cell(
            holder.Cell(address=site,age=age,
                        **{f's{k}_data':site*17+k for k in range(5)}),
            spatial.Cell(address=site,kind=spatial.SOURCE))
            for site in range(17))
        result=native.step_ring(cells)
        self.assertEqual(len(result),len(cells))
        for site in range(len(cells)):
            local=tuple(cells[(site+offset)%len(cells)]
                        for offset in physical.NEIGHBORHOOD)
            self.assertEqual(result[site],physical.local_step(local))
        with self.assertRaises(ValueError):native.local_step(cells)


if __name__=='__main__':unittest.main()
