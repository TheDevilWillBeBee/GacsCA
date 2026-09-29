import random
import unittest
from gacsca.fixed_rule import windowed as r,window_rule as f,window_program as b,window_initial as init
from gacsca.fixed_rule.window_world import World


class WindowInitialTests(unittest.TestCase):
    def test_lazy_initialization_matches_explicit_core_and_implicit_padding(self):
        top=(r.Cell(bit=1),r.Cell(head=1,phase=6,rd=0xDEADBEEF,address=123456789))
        g=b.layout();rng=random.Random(812)
        with World.encode(top) as world:
            for k in range(2):
                for a in (0,1,g.info_start,g.info_start+f.WIDTH-1,g.computation_cells-1,g.computation_cells,g.colony_cells-1,*[rng.randrange(g.colony_cells) for _ in range(30)]):
                    self.assertEqual(init.cell_at(top,1,k*g.colony_cells+a),world.cell(k,a))
            self.assertEqual(world.decode(),top)

    def test_fixed_rule_and_complete_controller_through_three_initial_levels(self):
        top=(r.Cell(bit=1,head=1,phase=6,rd=0xABCDEF12,pc=0xFFFFFFFF,address=70000),)
        g=b.layout();identity=r.identity()
        for depth in (1,2,3):
            count=init.physical_cells(1,depth-1)
            for p in (0,count-1,count//2):
                self.assertEqual(init.decode_parent(top,depth,p),init.cell_at(top,depth-1,p))
                self.assertEqual(len(r.encode_cell(init.cell_at(top,depth,p))),237)
            self.assertEqual(init.resource_estimate(1,depth)['fixed_rule'],identity)
            self.assertEqual(g.colony_cells,1<<28)
        self.assertEqual(r.step_ring((r.Cell(address=123456789,bit=1),)),(r.Cell(address=123456789,bit=1),))


if __name__=='__main__':unittest.main()
