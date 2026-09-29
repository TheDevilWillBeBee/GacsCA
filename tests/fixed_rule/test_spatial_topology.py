"""Full-DAG static topology and optimistic routing-bound checks."""
import unittest

from experiments.fixed_rule.explore_spatial_topology import explore
from gacsca.fixed_rule import spatial_epoch as physical
from gacsca.fixed_rule import spatial_fanout_compiler as compiler


class SpatialTopology(unittest.TestCase):
    def test_static_topology_preserves_capacity_and_causal_order(self):
        placement=explore()
        compiled=compiler.compile_capacity()
        summary=placement.summary
        self.assertEqual(len(placement.sites),len(compiled.nodes))
        self.assertEqual(len(placement.slots),len(compiled.nodes))
        self.assertEqual(summary['first_eight_sites_pinned'],4653)
        self.assertEqual(summary['pinned_slot_depth_inversions'],0)
        self.assertTrue(summary['site_order_and_dag_acyclic'])
        self.assertLessEqual(summary['max_routes_per_site'],physical.ROUTE_SLOTS)
        self.assertLessEqual(summary['max_gate_slots_per_site'],physical.GATE_SLOTS)

    def test_communication_bound_improves_load_only_layout(self):
        summary=explore().summary
        self.assertLess(summary['optimistic_latest_output_completion'],
                        physical.PERIOD)
        self.assertGreater(summary['load_balanced_optimistic_output_completion'],
                           physical.PERIOD)
        self.assertGreater(summary['optimistic_output_speedup'],4)


if __name__=='__main__':unittest.main()
