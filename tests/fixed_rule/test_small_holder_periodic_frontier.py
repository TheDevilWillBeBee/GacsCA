from dataclasses import replace
import unittest
import numpy as np
from gacsca.fixed_rule import small_holder_rule as f,small_holder_native as native
from gacsca.fixed_rule import small_holder_periodic_bounded_cuda as gpu
from gacsca.fixed_rule import small_holder_periodic_initial as init,small_holder_projected as r,small_holder_core as c


class Frontier(unittest.TestCase):
    def test_metadata_exceptions_persist_and_more_than_one_worker_round_is_updated(self):
        bg=native.array_from_cells((f.Cell(),f.Cell(age=17),f.Cell(age=31)))
        size=900
        exceptions={pos:replace(f.decode_cell(bg[pos%3].tolist()),p3_a=pos+9) for pos in range(0,size,30)}
        dense=[exceptions.get(pos,f.decode_cell(bg[pos%3].tolist())) for pos in range(size)]
        with gpu.World(bg,size,exceptions) as world:
            for _ in range(2):
                expected=native.step_ring(tuple(dense));metrics=world.step()
                self.assertGreater(metrics['candidate_evaluations'],gpu.WORKERS)
                got=[]
                for start in range(0,size,gpu.MAX_READ):got.extend(world.read(tuple(range(start,min(size,start+gpu.MAX_READ)))))
                self.assertEqual(tuple(got),expected)
                self.assertEqual(world.read((30,))[0].p3_a,39)
                self.assertIn(30,world.positions)
                dense=list(expected)

    def test_frontier_includes_newly_reached_head_and_written_data(self):
        bg=init.encoded_background(r.Cell());bg[:,f.COL['age']]=1
        exceptions={}
        for d in f.OFFSETS:
            pos=100-d
            fields=dict(zip((n for n,_ in f.SCHEMA),map(int,bg[pos])))
            for name,value in dict(data=11,head=1,phase=c.WRITE,rd=100,value=91).items():fields[f's{d+2}_{name}']=value
            exceptions[pos]=f.Cell(**fields)
        probes=tuple(range(91,111))
        def old(pos):return exceptions.get(pos%f.Q,f.decode_cell(bg[pos%f.Q].tolist()))
        expected=tuple(native.local_step(tuple(old(pos+j) for j in f.NEIGHBORHOOD)) for pos in probes)
        with gpu.World(bg,f.Q,exceptions) as world:
            self.assertNotIn(103,world.positions)
            world.step()
            self.assertIn(103,world.positions)
            self.assertEqual(world.read(probes),expected)
            self.assertEqual(world.read((100,))[0].s2_data,91)
            self.assertEqual(world.read((103,))[0].s0_head,1)


if __name__=='__main__':unittest.main()
