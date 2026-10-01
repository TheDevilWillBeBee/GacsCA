"""Initialization and decode relation on a closed lower physical ring."""
import unittest

import numpy as np

from gacsca.fixed_rule import stream28_compact_layout as layout_module
from gacsca.fixed_rule import stream28_dual_holder_rule20 as holder
from gacsca.fixed_rule import stream28_dual_pass20 as physical
from gacsca.fixed_rule import stream28_dual_projected20 as projected
from gacsca.fixed_rule.gpu_validation.initial import initialize, decode_info
from experiments.fixed_rule.build_compact8_circuit import static_plan
from experiments.fixed_rule.compact8_address_rom import project_all_dual_static


class InitialTest(unittest.TestCase):
    def test_all_static_sources_info_hold_and_fivefold_copies(self):
        raw, upper = initialize(15, 20260929)
        layout = layout_module.build()
        sources = static_plan(True, True)['raw_sources']
        static = set(layout.static_inputs)
        data = raw[:, holder.COL['s2_data']]
        self.assertEqual(len(decode_info(raw)), len(upper))
        for offset in holder.OFFSETS:
            np.testing.assert_array_equal(
                raw[:, holder.COL[f's{offset+2}_data']], np.roll(data,-offset))
        for col, cell in enumerate(upper):
            want = projected.encode_cell(projected.project(cell))
            self.assertEqual(decode_info(raw)[col], want)
            self.assertEqual(tuple(map(int,raw[col*physical.Q+np.asarray(layout.hold),
                                                holder.COL['s2_data']])),want)
            neighbors = tuple(upper[(col+j)%len(upper)]
                              for j in physical.NEIGHBORHOOD)
            words = tuple(word for neighbor in neighbors
                          for word in physical.encode_cell(neighbor))
            addressed = project_all_dual_static(cell.holder.address,words,True)
            for site,wire in sources.items():
                if wire in static:
                    self.assertEqual(int(data[col*physical.Q+site]),addressed[wire])

    def test_upper_causal_cone_size(self):
        for periods, ring in ((1,15),(2,29)):
            center = ring//2
            support = range(center-7*periods,center+7*periods+1)
            self.assertEqual(len(support),14*periods+1)
            self.assertGreaterEqual(min(support),0)
            self.assertLess(max(support),ring)


if __name__ == '__main__': unittest.main()
