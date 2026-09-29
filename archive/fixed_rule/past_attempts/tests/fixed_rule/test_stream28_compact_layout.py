"""Encoded three-history gather and static gate-slot capacity checks."""
import unittest

from gacsca.fixed_rule import stream28_compact_layout as layout
from gacsca.fixed_rule import stream28_compact_vote as physical
from experiments.fixed_rule.audit_stream28_compact_gather import check as gather_check
from experiments.fixed_rule.place_stream28_compact_gates import check as place_check
from experiments.fixed_rule.schedule_compact_operands import schedule


class CompactLayout(unittest.TestCase):
    def test_all_projected_inputs_have_local_launch_and_accept(self):
        before_rule=physical.local_step
        schedule=layout.build()
        result=gather_check()
        self.assertEqual(len(schedule.gathered),761)
        self.assertEqual(result['packet_paths'],2283)
        self.assertEqual(result['literal_local_launch_steps'],2283)
        self.assertEqual(result['literal_local_accept_steps'],2283)
        self.assertGreater(result['literal_combined_endpoint_steps'],0)
        self.assertIs(physical.local_step,before_rule)

    def test_changed_own_dag_gate_and_route_slots_pack(self):
        result=place_check()
        self.assertEqual(result['Q'],8192)
        self.assertEqual(result['max_gate_slots_per_site'],3)
        self.assertEqual(result['max_routes_per_gate_site'],38)
        self.assertEqual(result['placed_gate_instances'],14076)

    def test_explicit_operand_schedule_distinguishes_4q_from_8q(self):
        short=schedule(4*physical.Q)
        self.assertFalse(short['passed'])
        self.assertGreaterEqual(short['failed_event'][2],4*physical.Q)
        long=schedule(8*physical.Q)
        self.assertTrue(long['passed'])
        self.assertEqual(long['gate_instances'],14076)
        self.assertEqual(long['operand_packets'],24664)
        self.assertLess(long['latest_event'],8*physical.Q)


if __name__=='__main__':unittest.main()
