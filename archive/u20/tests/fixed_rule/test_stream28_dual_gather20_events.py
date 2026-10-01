"""Packet-flight skips must respect the physical edge countdown."""
from dataclasses import replace
import unittest
from unittest.mock import patch

from gacsca.fixed_rule import stream28_compact_layout as layout_module
from gacsca.fixed_rule import stream28_dual_core20 as core
from experiments.fixed_rule.run_dual_gather20_events import check


class GatherFlightTest(unittest.TestCase):
    def test_one_colony_retains_all_three_histories(self):
        receipt=check(colonies=1)
        self.assertTrue(receipt['passed'])
        self.assertEqual(receipt['packet_boundary_crossings_checked'],2283)
        self.assertEqual(receipt['complete_history_words_checked'],2283)

    def test_extra_ring_lap_cannot_fake_a_valid_route(self):
        original=layout_module.build()
        index=next(i for i,route in enumerate(original.routes)
                   if route.stage==0 and route.arrival-route.launch+
                   15*core.Q<core.STREAM_FRAME)
        routes=list(original.routes)
        routes[index]=replace(routes[index],arrival=routes[index].arrival+
                              15*core.Q)
        corrupted=replace(original,routes=tuple(routes))
        with patch.object(layout_module,'build',return_value=corrupted):
            with self.assertRaisesRegex(AssertionError,
                                        'packet countdown disagrees'):
                check(colonies=15)


if __name__=='__main__':unittest.main()
