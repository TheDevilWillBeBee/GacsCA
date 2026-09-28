from dataclasses import replace
import random
import unittest
from gacsca.fixed_rule import word_rule as f,word_projected as r,word_program as p,word_initial as init
from gacsca.fixed_rule.word_world import World


class WordInitialTests(unittest.TestCase):
    def test_lazy_matches_physical_initial_representation(self):
        top=(r.Cell(address=100,age=f.U-1,data=(1<<64)-1,pc=0xFFFFFFFF,head=1),r.Cell(address=500,f1=1,wf2=1))
        rng=random.Random(2421);g=p.layout()
        with World.encode(top) as world:
            for k in range(len(top)):
                for a in (0,g.info_start,g.info_start+f.FIELDS-1,g.computation_cells-1,g.computation_cells,f.Q-1,*[rng.randrange(f.Q) for _ in range(30)]):
                    self.assertEqual(init.cell_at(top,1,k*f.Q+a),world.cell(k,a))

    def test_same_rule_raw_state_width_and_rom_for_three_initial_levels(self):
        top=(r.Cell(address=123456,age=f.U-1,head=1,phase=7,rd=(1<<64)-1,data=0xABCDEF0123456789),)
        identity=r.identity();self.assertEqual(r.WIDTH,585)
        self.assertEqual(identity['rom_sha256'],'7e179505523acec223aac9dba89703ea05c80a927c9f72afcab0fd6dfcf1fb8b')
        for depth in (1,2,3):
            n=init.physical_cells(1,depth-1)
            for i in (0,n-1,n//2):
                self.assertEqual(init.decode_parent(top,depth,i),init.cell_at(top,depth-1,i))
                self.assertEqual(len(r.encode_cell(init.cell_at(top,depth,i))),24)
            self.assertEqual(init.resources(1,depth)['fixed_rule'],identity)

    def test_periodic_terminal_configuration_obeys_same_rule(self):
        for age in (0,15,f.U-1):
            top=init.TerminalOrbit(payload=0xFEDCBA9876543210,age=age)
            for address in (0,1,5,p.layout().computation_cells-1,p.layout().computation_cells,f.Q-1):
                neighborhood=tuple(top[(address+j)%f.Q] for j in range(-5,6))
                self.assertEqual(r.local_step(neighborhood),replace(top[address],age=(age+1)%f.U))
            for depth in (1,2,3):
                self.assertEqual(init.decode_parent(top,depth,0),init.cell_at(top,depth-1,0))


if __name__=='__main__':unittest.main()
