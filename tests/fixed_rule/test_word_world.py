from dataclasses import replace
import random
import unittest
import numpy as np
from gacsca.fixed_rule import word_rule as f,word_projected as r,word_program as p
from gacsca.fixed_rule.word_world import World,library,pointer
from gacsca.fixed_rule.word_native import array_from_cells
from gacsca.fixed_rule.word_description import build


def empty_cores(n=1,age=0):
    core=r.project_array(p.template()).copy();core[:,r.COL['head']]=0;core[:,r.COL['age']]=age
    return np.tile(core,(n,1))


def at(world,pos):
    k,a=divmod(pos%(world.colonies*f.Q),f.Q);return world.cell(k,a)


def check_local_step(test,world,positions):
    expected={i:r.local_step(tuple(at(world,i+j) for j in range(-5,6))) for i in positions}
    world.run(1)
    for i,value in expected.items():test.assertEqual(at(world,i),value,i)


class WordWorldTests(unittest.TestCase):
    def test_healthy_specialization_matches_complete_rule_for_raw_workspace(self):
        rng=random.Random(2311);lib=library();program=build(healthy_domain=True)
        for age in (0,15,f.U-1):
            for address in (0,1,100,f.Q-1):
                for _ in range(5):
                    cells=[f.Cell(**{name:rng.randrange(1<<width) for name,width in f.SCHEMA}) for _ in range(11)]
                    cells=tuple(replace(c,address=(address+j-5)%f.Q,age=age,f1=0,f2=0,wf1=0,wf2=0) for j,c in enumerate(cells))
                    expected=f.local_step(cells)
                    values=tuple(word for c in cells[4:7] for word in f.encode_cell(c))
                    self.assertEqual(f.decode_cell(program.evaluate(values)),expected)
                    inputs=array_from_cells(cells[4:7]);out=np.empty((1,f.FIELDS),dtype=np.uint64)
                    lib.ww_healthy_local(pointer(inputs),pointer(out));self.assertEqual(f.decode_cell(out[0].tolist()),expected)

    def test_five_hops_to_distinct_colonies_and_full_word_payload(self):
        g=p.layout();size=g.computation_cells;cores=empty_cores(11,age=f.U-3)
        for field,value in dict(rp_valid=1,rp_remaining=5,rp_target=7,rp_data=0xFEDCBA9876543210).items():cores[size-1,r.COL[field]]=value
        for field,value in dict(lp_valid=1,lp_remaining=3,lp_target=8,lp_data=(1<<64)-1).items():cores[0,r.COL[field]]=value
        arrival=5*f.Q-size+8
        with World(cores) as world:
            check_local_step(self,world,range(-6,7))
            check_local_step(self,world,range(size-6,size+7))
            world.run(arrival-world.time-1)
            self.assertEqual(world.cell(5,7).data,0)
            check_local_step(self,world,[5*f.Q+i for i in range(1,14)])
            self.assertEqual(world.cell(5,7).data,0xFEDCBA9876543210)
            self.assertEqual(world.cell(8,8).data,(1<<64)-1)
            self.assertEqual(world.pending,0)
            self.assertEqual(world.cell(0,100000).age,(f.U-3+arrival)%f.U)
            self.assertTrue(np.all(world.cores[:,r.COL['age']]==(f.U-3+arrival)%f.U))
            self.assertEqual(world.cell(4,7).data,0)
            self.assertEqual(world.cell(9,8).data,0)

    def test_missing_target_drops_after_requested_colony(self):
        g=p.layout();cores=empty_cores(7)
        for field,value in dict(lp_valid=1,lp_remaining=3,lp_target=0xFFFFFFFF,lp_data=1).items():cores[0,r.COL[field]]=value
        with World(cores) as world:
            world.run(3*f.Q)
            self.assertEqual(world.cell(4,0).lp_remaining,0)
            self.assertEqual(world.cell(4,0).lp_valid,1)
            check_local_step(self,world,[4*f.Q+i for i in range(-5,6)])
            self.assertEqual(world.pending,0)
            self.assertEqual(world.cell(3,f.Q-1).lp_valid,0)

    def test_wait_and_uniform_age_match_literal_transitions(self):
        g=p.layout();pc=next(i for i,op in enumerate(g.instructions) if op.kind==f.WAIT)
        position=g.memory_count+pc;cores=empty_cores(age=f.U-3)
        for name,value in dict(head=1,pc=pc,rd=1000,value=(1<<64)-1).items():cores[position,r.COL[name]]=value
        with World(cores) as fast,World(cores) as literal:
            result=fast.run(1001);literal.run(1001,skip_wait=False)
            np.testing.assert_array_equal(fast.cores,literal.cores)
            self.assertEqual(result['wait_ticks_skipped'],1000)
            self.assertEqual(fast.cell(0,position).age,998)

    def test_encoding_contains_raw_maintenance_and_controller_fields(self):
        top=(r.Cell(data=0xFEDCBA9876543210,head=1,phase=7,pc=0xFFFFFFFF,rd=(1<<64)-1,
                    alu=7,address=400,age=f.U-1,f1=1,f2=1,wf1=1,wf2=1),)
        with World.encode(top) as world:
            self.assertEqual(world.decode(),top);self.assertTrue(world.check_boundary())
        cores=r.encode_cores(top);cores[p.layout().info_start+f.COL['index'],r.COL['data']]^=np.uint64(1)
        with self.assertRaisesRegex(ValueError,'program record'):r.decode_cores(cores)
        row=tuple(r.Cell(address=100+j) for j in range(-5,6));row=list(row);row[5]=replace(row[5],address=200)
        lifted=tuple(r.lift(c) for c in row);raw=f.local_step(lifted)
        self.assertEqual(raw.address,100)
        self.assertNotEqual(raw,r.lift(r.project(raw))) # static-Address shortcut is now false

    def test_damaged_physical_structure_is_rejected(self):
        for name,value in (('address',999),('age',1),('wf1',1),('f2',1)):
            cores=empty_cores();cores[3,r.COL[name]]=value
            with self.assertRaisesRegex(ValueError,'canonical'):World(cores)


if __name__=='__main__':unittest.main()
