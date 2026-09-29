"""Initialization and fixed-ROM identity; no deeper dynamics claimed."""
import random
import unittest
from gacsca.fixed_rule import projected as rule,projected_initial as init,addressed,addressed_block


class ProjectedInitialTests(unittest.TestCase):
    def test_lazy_matches_materialized(self):
        top=(rule.Cell(bit=1,address=33),rule.Cell(head=1,phase=4,pc=17,address=65535))
        physical=rule.encode(top)
        rng=random.Random(501)
        for position in [0,len(physical)-1]+[rng.randrange(len(physical)) for _ in range(100)]:
            self.assertEqual(init.cell_at(top,1,position),rule.cells_from_array(physical[position:position+1])[0])

    def test_same_physical_rule_and_rom_through_three_initial_levels(self):
        top=(rule.Cell(bit=1,pc=5,rp_valid=1,address=3999),rule.Cell(head=1,address=7607))
        before=rule.identity()
        rng=random.Random(502)
        for depth in (1,2,3):
            count=init.physical_cells(len(top),depth-1)
            for position in (0,count-1,rng.randrange(count)):
                self.assertEqual(init.decode_parent(top,depth,position),init.cell_at(top,depth-1,position))
                self.assertEqual(len(rule.encode_cell(init.cell_at(top,depth,position))),125)
            self.assertEqual(init.resource_estimate(len(top),depth)['fixed_rule'],before)

    def test_quiescent_top_uses_same_projected_rule(self):
        for bit in (0,1):
            top=(rule.Cell(bit=bit,address=0),)
            self.assertEqual(rule.step_ring(top),top)
            offset=sum(width for name,width in addressed.SCHEMA[:5])
            digit=addressed_block.layout().info_start+offset
            for depth in (1,2,3):
                position=sum(digit*addressed_block.layout().colony_cells**j for j in range(depth))
                self.assertEqual(init.cell_at(top,depth,position).bit,bit)


if __name__=='__main__':
    unittest.main()
