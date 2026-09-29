from dataclasses import replace
from unittest.mock import patch
import unittest
import numpy as np
from gacsca.fixed_rule import clock_rule as f,early_program as p,early_projected as r,early_initial as initial
from gacsca.fixed_rule import clock_program as oldp,clock_projected as oldr
from gacsca.fixed_rule.early_world import World
from gacsca.fixed_rule.clock_world import World as OldWorld
from gacsca.fixed_rule.wordcode import Program


def damage_static(core,program=p,projected=r):
    result=core.copy();g=program.layout()
    for base in range(0,len(result),g.computation_cells):
        for name in f.STATIC:
            width=dict(f.SCHEMA)[name]
            result[base+g.info[f.COL[name]],projected.COL['data']]^=np.uint64((1<<width)-1)
    return result


class EarlyRepairTests(unittest.TestCase):
    def test_local_prefix_repairs_all_seven_words_and_preserves_every_dynamic_field(self):
        g=p.layout();top=tuple(r.Cell(address=a,age=f.U-1,data=f.MASK,head=1,phase=7,pc=0xFFFFFFFF,rd=f.MASK,value=f.MASK,f1=1,wf2=1)
            for a in (0,g.memory_count+g.description_instruction,g.computation_cells-1,f.Q-1))
        corrupted=damage_static(r.encode_cores(top))
        with self.assertRaisesRegex(ValueError,'program record'):r.decode_cores(corrupted)
        with World(corrupted) as world:
            with patch.object(Program,'evaluate',side_effect=AssertionError('host evaluator')),patch.object(f,'local_step',side_effect=AssertionError('host transition')):
                world.run(p.repair_ticks()-1)
                for k,c in enumerate(top):
                    address=k*g.computation_cells+g.info[f.COL['last']]
                    self.assertNotEqual(int(world.cores[address,r.COL['data']]),r.lift(c).last)
                world.run(1)
            self.assertEqual(world.decode(),top)
            for k,c in enumerate(top):
                values=world.cores[k*g.computation_cells+np.array(g.info),r.COL['data']]
                self.assertEqual(tuple(map(int,values)),f.encode_cell(r.lift(c)))

    def test_baseline_without_prefix_does_not_repair_the_same_corruption(self):
        top=(oldr.Cell(address=143,age=321,head=1,phase=f.READ_B,rb=143,rd=112,value=f.MASK,data=f.MASK,alu=f.NAND),)
        with OldWorld(damage_static(oldr.encode_cores(top),oldp,oldr)) as world:
            world.run(p.repair_ticks())
            with self.assertRaisesRegex(ValueError,'program record'):world.decode()

    def test_early_repair_uses_current_input_address_not_future_repaired_address(self):
        top=(r.Cell(address=143,age=321,head=1,phase=f.READ_B,rb=143,rd=112,value=f.MASK,data=f.MASK,alu=f.NAND),)
        with World(damage_static(r.encode_cores(top))) as world:
            world.run(p.repair_ticks())
            self.assertEqual(world.decode(),top)
            self.assertEqual(int(world.cores[p.layout().info[f.COL['index']],r.COL['data']]),143)
        neighborhood=tuple(r.Cell(address=100+j,age=1) for j in range(-5,6))
        cells=list(neighborhood);cells[5]=replace(top[0],address=143)
        self.assertEqual(r.local_step(cells).address,100)

    def test_new_projection_keeps_complete_descriptor_and_depth_independence(self):
        g=p.layout();self.assertEqual(g.description_sha256,f.self_description().digest())
        self.assertEqual(g.description_sha256,oldp.layout().description_sha256)
        self.assertEqual(r.WIDTH,585)
        self.assertNotEqual(r.identity()['rom_sha256'],oldr.identity()['rom_sha256'])
        top=initial.terminal_data(age=17);identity=r.identity()
        for depth in (1,2,3):
            self.assertEqual(initial.resources(1,depth)['fixed_rule'],identity)
            self.assertEqual(initial.decode_parent(top,depth,0),initial.cell_at(top,depth-1,0))
        self.assertEqual(len(g.instructions),len(oldp.layout().instructions)+14)
        for i,name in enumerate(f.STATIC):
            load,meta=g.instructions[2*i:2*i+2]
            self.assertEqual((load.kind,load.a),(f.LOAD,g.info[f.COL['address']]))
            self.assertEqual((meta.kind,meta.a,meta.b),(f.META,g.info[f.COL[name]],i))


if __name__=='__main__':unittest.main()
