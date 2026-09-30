import unittest

from experiments.fixed_rule.u20_repair.differential import run
from gacsca.fixed_rule.wordcode_and import Builder


class DifferentialTest(unittest.TestCase):
    def test_hop_selector_exhaustive_finite_domain(self):
        for offset in range(-7,8):
            builder=Builder(1)
            output=builder.select(0,builder.const(abs(offset)),builder.const(0))
            program=builder.finish((output,))
            for selected in (0,1):
                expected=abs(offset) if selected else 0
                self.assertEqual(program.evaluate((selected,))[0],expected)
                if selected and abs(offset)>1:
                    self.assertNotEqual(selected & abs(offset),expected)

    def test_all_raw_outputs(self):
        receipt=run(random_cases=32)
        self.assertEqual(receipt['outputs_checked'],receipt['cases']*421)
        self.assertEqual(set(receipt['route_offsets']),
                         {str(i) for i in range(-7,8) if i})


if __name__=='__main__':unittest.main()
