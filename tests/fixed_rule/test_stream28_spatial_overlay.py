"""Fixed combined holder/evaluator alphabet and local stage-five handoff."""
from dataclasses import replace
import unittest

from gacsca.fixed_rule import spatial_epoch as spatial
from gacsca.fixed_rule import stream28_holder_rule as holder
from gacsca.fixed_rule import stream28_spatial_overlay as combined
from experiments.fixed_rule.audit_stream28_spatial_overlay import check


class StreamSpatialOverlay(unittest.TestCase):
    def test_capture_keeps_immutable_spatial_site_address(self):
        base=holder.Cell(address=23,age=combined.CAPTURE_AGE)
        spatial_cell=spatial.Cell(address=17,kind=spatial.SOURCE)
        neighborhood=(combined.Cell(base,spatial_cell),)*15
        after=combined.local_step(neighborhood)
        self.assertEqual(after.evaluator.address,17)

    def test_exact_full_state_encoding_and_fixed_radius(self):
        self.assertEqual((combined.Q,combined.U,combined.WIDTH),
                         (8192,268435456,6424))
        self.assertEqual(combined.NEIGHBORHOOD,tuple(range(-7,8)))
        raw=replace(holder.Cell(address=17,age=combined.CAPTURE_AGE),
                    s0_pc=123456789,s2_data=0x123456789abcdef0,
                    s4_lp_target=0x87654321,w4_wf2=1,signal=17)
        packet=spatial.Packet(1,2863,0,3,0xfedcba9876543210)
        spatial_cell=spatial.Cell(address=17,age=2026,kind=spatial.GATE,
                                 active_slot=2,source_value=0xabcdef,
                                 arg0=0x5555,arg1=0xaaaa,ready=3,
                                 result=0xf0f0,done=1,mail=packet,
                                 routes=(spatial.Route(1,2863,0,3,2,28930),)+
                                        (spatial.EMPTY_ROUTE,)*(spatial.ROUTE_SLOTS-1))
        cell=combined.Cell(raw,spatial_cell)
        encoded=combined.encode_cell(cell)
        self.assertEqual(len(encoded),combined.FIELDS)
        self.assertEqual(combined.decode_cell(encoded),cell)
        with self.assertRaises(ValueError):combined.decode_cell(encoded[:-1])
        with self.assertRaises(ValueError):combined.local_step((cell,)*14)
        with self.assertRaises(ValueError):combined.local_step((cell,)*16)

    def test_all_hold_outputs_commit_to_five_replicas(self):
        transition=combined.local_step;width=combined.WIDTH
        result=check()
        self.assertTrue(result['passed'])
        self.assertEqual(result['all_hold_sites'],154)
        self.assertEqual(result['complete_raw_upper_fields_checked'],154)
        self.assertEqual(result['literal_fivefold_hold_commit_steps'],770)
        self.assertEqual(result['literal_fivefold_info_commit_steps'],770)
        self.assertGreater(result['source_sites_captured'],700)
        self.assertIs(combined.local_step,transition)
        self.assertEqual(combined.WIDTH,width)


if __name__=='__main__':unittest.main()
