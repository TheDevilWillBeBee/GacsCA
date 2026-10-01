import unittest
from unittest.mock import patch

import numpy as np

from gacsca.fixed_rule import stream28_compact_layout as layout_module
from gacsca.fixed_rule import stream28_dual_holder_rule20 as holder
from gacsca.fixed_rule import stream28_dual_pass20 as physical
from gacsca.fixed_rule.u20_repair.initial import initialize,decode_info
from experiments.fixed_rule.compact8_address_rom import project_all_dual_static
from experiments.fixed_rule.build_compact8_circuit import static_plan


class InitialTest(unittest.TestCase):
    def test_upper_static_is_not_host_supplied(self):
        with patch('experiments.fixed_rule.compact8_address_rom.project_all_dual_static',
                   side_effect=AssertionError('host upper ROM oracle called')):
            raw,upper=initialize(15,1234)
        self.assertEqual(raw.shape,(15*physical.Q,physical.FIELDS))
        self.assertEqual(decode_info(raw),tuple(map(lambda c: __import__(
            'gacsca.fixed_rule.stream28_dual_projected20',fromlist=['encode_cell'])
            .encode_cell(c),upper)))
        sources=static_plan(True,True)['raw_sources']
        static=set(layout_module.build().static_inputs)
        for col in range(15):
            for site,wire in sources.items():
                if wire in static:
                    self.assertEqual(int(raw[col*physical.Q+site,
                                             holder.COL['s2_data']]),0)
        self.assertGreater(len({c.holder.address for c in upper}),1)


if __name__=='__main__':unittest.main()
