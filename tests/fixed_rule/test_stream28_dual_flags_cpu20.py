"""Packed Wf/Flag skip must match the fixed U20 literal recurrence."""
import random
import unittest

import numpy as np

from gacsca.fixed_rule import stream28_dual_core20 as core
from gacsca.fixed_rule.stream28_dual_flags_cpu20 import (
    World,library,pointer)


class PackedDualFlagsTest(unittest.TestCase):
    def test_every_bit_matches_literal_raw_maintenance(self):
        rng=random.Random(2026092941)
        lib=library()
        for trial in range(36):
            base=(0,64,core.Q-64)[trial%3]
            age=(core.WF_START-1,core.WF_START,
                 core.WF_END-1,core.WF_END)[trial%4]
            signal_right=trial%2
            signal_left=int(trial%3!=0)
            raw=np.array([rng.getrandbits(64) for _ in range(6)],
                         dtype=np.uint64)
            output=np.empty(2,dtype=np.uint64)
            lib.fw_word(pointer(raw),pointer(output),
                        int(base==0),int(base==core.Q-64),
                        signal_right,signal_left,
                        int(core.WF_START<=age<core.WF_END))
            def cell(relative):
                word,bit=divmod(relative,64)
                f1=(int(raw[2*(word+1)])>>bit)&1
                f2=(int(raw[2*(word+1)+1])>>bit)&1
                address=(base+relative)%core.Q
                on=core.WF_START<=age<core.WF_END
                return core.Cell(address=address,age=age,f1=f1,f2=f2,
                    wf1=int(on and address>=core.Q-5 and signal_right),
                    wf2=int(on and address<=4 and signal_left and not f1))
            for bit in range(64):
                actual=core.maintenance(tuple(cell(bit+delta)
                                              for delta in range(-5,6)))
                self.assertEqual((int(output[0])>>bit)&1,actual['f1'],
                                 (trial,bit,'f1'))
                self.assertEqual((int(output[1])>>bit)&1,actual['f2'],
                                 (trial,bit,'f2'))

    def test_skip_stops_at_both_forcing_boundaries(self):
        with World((1,),(1,),age=core.CAPTURE_AGE) as fast,\
             World((1,),(1,),age=core.CAPTURE_AGE) as slow:
            first=core.WF_START-core.CAPTURE_AGE
            fast.run(first)
            slow.run(first,skip_fixed=False)
            np.testing.assert_array_equal(fast.runs,slow.runs)
            self.assertEqual(fast.info['age'],core.WF_START)
            span=core.WF_END-core.WF_START
            fast.run(span)
            slow.run(span,skip_fixed=False)
            np.testing.assert_array_equal(fast.runs,slow.runs)
            self.assertEqual(fast.info['age'],core.WF_END)
            self.assertGreater(fast.info['quiet_ticks'],0)


if __name__=='__main__':unittest.main()
