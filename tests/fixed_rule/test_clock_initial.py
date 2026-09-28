from dataclasses import replace
import random
import unittest
import numpy as np
from gacsca.fixed_rule import clock_rule as f,clock_projected as r,clock_program as p,clock_initial as init
from gacsca.fixed_rule.clock_world import World


class ClockInitialTests(unittest.TestCase):
    def test_three_initial_depths_keep_rule_rom_width_and_all_raw_fields(self):
        top=(r.Cell(address=12345,age=f.U-1,head=1,phase=7,pc=0xFFFFFFFF,rd=f.MASK,value=f.MASK,f1=1,wf2=1),)
        identity=r.identity();self.assertEqual(r.WIDTH,585)
        self.assertEqual(identity['full_rule']['description_sha256'],'6bee308cd32c9637d6598034932ed2ee956f60f0e4045ef0a1726f9ed0697ee2')
        self.assertEqual(identity['rom_sha256'],'7e2f5ef0e1ed995f128defad316f8e4c868d6b2c6812f2ab0cad236a3af3a81a')
        for depth in (1,2,3):
            n=init.physical_cells(1,depth-1)
            for i in (0,n//2,n-1):
                self.assertEqual(init.decode_parent(top,depth,i),init.cell_at(top,depth-1,i))
                self.assertEqual(len(r.encode_cell(init.cell_at(top,depth,i))),24)
            self.assertEqual(init.resources(1,depth)['fixed_rule'],identity)
        g=p.layout();base=r.Cell(address=100)
        for name,width in r.SCHEMA:
            value=(1<<width)-1;c=replace(base,**{name:value});core=r.encode_cores((c,))
            self.assertEqual(r.decode_cores(core),(c,))
            self.assertEqual(int(core[g.info[f.COL[name]],r.COL['data']]),value)
            bad=core.copy();bad[g.info[f.COL['index']],r.COL['data']]^=np.uint64(1)
            with self.assertRaisesRegex(ValueError,'program record'):r.decode_cores(bad)

    def test_lazy_initialization_matches_physical_cores_and_padding(self):
        top=(r.Cell(address=99,head=1),r.Cell(data=f.MASK,age=f.U-1));g=p.layout();rng=random.Random(2707)
        with World.encode(top) as world:
            for colony in range(2):
                for address in (0,*g.info,*g.hold,g.computation_cells-1,g.computation_cells,f.Q-1,*[rng.randrange(f.Q) for _ in range(15)]):
                    self.assertEqual(init.cell_at(top,1,colony*f.Q+address),world.cell(colony,address))

    def test_explicit_flagged_cap_is_same_rule_and_quiet_cap_counterexample(self):
        for age in (0,15,16*f.Q,32*f.Q,64*f.Q,72*f.Q,96*f.Q,98*f.Q,112*f.Q,f.U-1):
            top=init.terminal_data(payload=0xFEDCBA9876543210,age=age)
            self.assertEqual(r.step_ring(top),(replace(top[0],age=(age+1)%f.U),))
            for depth in (1,2,3):self.assertEqual(init.decode_parent(top,depth,0),init.cell_at(top,depth-1,0))
        clean=tuple(r.Cell(address=j%f.Q) for j in range(-5,6))
        out=r.local_step(clean)
        self.assertEqual(out.head,1)
        self.assertNotEqual(out,replace(clean[5],age=1))

    def test_damaged_physical_structure_is_rejected(self):
        for name,value in (('age',1),('address',999),('f1',1),('f2',1),('wf2',1)):
            core=r.encode_cores((r.Cell(address=100),));core[3,r.COL[name]]=value
            with self.assertRaisesRegex(ValueError,'canonical'):World(core)


if __name__=='__main__':unittest.main()
