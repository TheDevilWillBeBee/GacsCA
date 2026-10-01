"""Early flag outputs depend on live controller state, not static ROM rows."""
from dataclasses import replace
import unittest

from gacsca.fixed_rule import spatial_epoch8 as spatial
from gacsca.fixed_rule import stream28_holder_rule as holder
from gacsca.fixed_rule import stream28_compact_vote8 as combined
from experiments.fixed_rule.measure_compact8_flag_slice import audit,flag_slice


class FlagSliceTest(unittest.TestCase):
    def test_full_rule_parity_and_static_independence(self):
        result=audit(8)
        self.assertTrue(result['passed'])
        self.assertEqual(result['required_raw_inputs'],56)
        self.assertEqual(result['required_spatial_inputs'],0)
        self.assertEqual(result['required_holder_static_inputs'],0)

    def test_live_flag_dynamics_change_the_outputs(self):
        base=[combined.Cell(holder.Cell(address=100+j,age=1000),
                            spatial.Cell(address=100+j)) for j in range(-7,8)]
        program=flag_slice()
        def value(changes):
            rows=list(base)
            for offset,fields in changes.items():
                item=rows[7+offset]
                rows[7+offset]=combined.Cell(replace(item.holder,**fields),
                                             item.evaluator)
            return program.evaluate(tuple(word for cell in rows
                                          for word in combined.encode_cell(cell)))
        self.assertEqual(value({}),(0,0))
        self.assertEqual(value({j:{'f1':1} for j in (1,2,3)}),(1,0))
        self.assertEqual(value({j:{'f2':1} for j in (-1,-2,-3,-4)}),(0,1))


if __name__=='__main__':unittest.main()
