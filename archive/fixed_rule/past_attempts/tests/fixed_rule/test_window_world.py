"""Exact local checks for the implicit-padding representation and WAIT skip."""
from dataclasses import replace
import random
import unittest
import numpy as np
from gacsca.fixed_rule import windowed as r,window_rule as f,window_program as b
from gacsca.fixed_rule.window_world import World
from gacsca.fixed_rule.windowed_native import dense_step,library


def empty_cores(n=1):
    core=r.project_array(b.template()).copy()
    core[:,r.COL['head']]=0
    return np.tile(core,(n,1))


def at(world,position):
    k,a=divmod(position%(world.colonies*f.COLONY_CELLS),f.COLONY_CELLS)
    return world.cell(k,a)


def assert_local_step(test,world,positions):
    expected={p:r.local_step(at(world,p-1),at(world,p),at(world,p+1)) for p in positions}
    world.run(1)
    for p,value in expected.items(): test.assertEqual(at(world,p),value,p)


class WindowWorldTests(unittest.TestCase):
    def test_projection_full_description_native_and_raw_controller(self):
        rng=random.Random(1971); circuit=f.self_description(); lib=library()
        self.assertEqual(r.WIDTH,237)
        self.assertEqual(r.identity()['rom_sha256'],'c4ff8d6fb3c8900b0853e6df52a91be5e4a5e9c2146156dc0e3c1b532c3bfbd2')
        for _ in range(100):
            row=tuple(r.Cell(**{name:rng.randrange(1<<width) for name,width in r.SCHEMA}) for _ in range(3))
            expanded=tuple(r.lift(c) for c in row)
            expected=f.local_step(*expanded)
            self.assertEqual(f.decode_cell(circuit.evaluate(tuple(bit for c in expanded for bit in f.encode_cell(c)))),expected)
            self.assertEqual(r.lift(r.local_step(*row)),expected)
            self.assertEqual(r.cells_from_array(dense_step(r.array_from_cells(row),lib))[1],r.project(expected))
            self.assertEqual(r.decode_cell(r.encode_cell(row[1])),row[1])

    def test_full_distance_mail_and_second_boundary_drop(self):
        g=b.layout(); q=g.colony_cells; size=g.computation_cells; distance=q-size
        cores=empty_cores(3)
        for field,value in dict(rp_valid=1,rp_bit=1,rp_target=5).items():cores[size-1,r.COL[field]]=value
        for field,value in dict(lp_valid=1,lp_bit=1,lp_target=6).items():cores[0,r.COL[field]]=value
        # A previously crossed left packet must drop on leaving its second colony.
        for field,value in dict(lp_valid=1,lp_cross=1,lp_bit=1,lp_target=7).items():cores[size,r.COL[field]]=value
        with World(cores) as world:
            assert_local_step(self,world,range(-3,3))
            self.assertEqual(world.pending,2)
            self.assertEqual(world.cell(0,size).rp_valid,1)
            self.assertEqual(world.cell(2,q-1).lp_valid,1)
            self.assertEqual(world.cell(0,q-1).lp_valid,0)
            metrics=world.run(distance-2)
            self.assertEqual(metrics['literal_core_ticks'],0)
            self.assertEqual(metrics['wait_ticks_skipped'],distance-2)
            # Inspect both channels immediately before and across core reentry.
            points=[q+j for j in range(-3,4)]+[2*q+size+j for j in range(-4,4)]
            assert_local_step(self,world,points)
            assert_local_step(self,world,points)
            self.assertEqual(world.pending,0)
            self.assertEqual(world.cell(1,0).rp_cross,1)
            self.assertEqual(world.cell(2,size-1).lp_cross,1)
            world.run(size)
            self.assertEqual(world.cell(1,5).bit,1)
            self.assertEqual(world.cell(2,6).bit,1)
            self.assertEqual(world.cell(0,7).bit,0)
            self.assertEqual(world.cell(1,6).bit,0)
            self.assertEqual(world.cell(2,5).bit,0)

    def test_opposite_packets_cross_without_interaction_in_padding(self):
        g=b.layout(); size=g.computation_cells; q=g.colony_cells; distance=q-size
        cores=empty_cores(2)
        for field,value in dict(rp_valid=1,rp_bit=1,rp_target=5).items():cores[size-1,r.COL[field]]=value
        for field,value in dict(lp_valid=1,lp_bit=0,lp_target=6).items():cores[size,r.COL[field]]=value
        with World(cores) as world:
            world.run(1);world.run(distance//2-3)
            mid=size+distance//2
            for _ in range(6):assert_local_step(self,world,range(mid-8,mid+9))
            self.assertEqual(world.pending,2)

    def test_wait_skip_matches_literal_core_ticks_and_resumes_exactly(self):
        g=b.layout(); pc=next(i for i,op in enumerate(g.instructions) if op.kind==f.WAIT)
        position=g.memory_count+pc; cores=empty_cores()
        for field,value in dict(head=1,pc=pc,rd=12345,ra=0xCAFEBABE,rb=0xDEADBEEF,value=1).items():cores[position,r.COL[field]]=value
        with World(cores) as skipped,World(cores) as literal:
            metrics=skipped.run(12345)
            literal.run(12345,skip_wait=False)
            np.testing.assert_array_equal(skipped.cores,literal.cores)
            self.assertEqual(metrics['wait_ticks_skipped'],12345)
            self.assertEqual(metrics['literal_core_ticks'],0)
            self.assertEqual(skipped.cell(0,position).rd,0)
            skipped.run(7);literal.run(7,skip_wait=False)
            np.testing.assert_array_equal(skipped.cores,literal.cores)

    def test_locality_at_core_edges_for_arbitrary_raw_controls(self):
        rng=random.Random(1972);g=b.layout();size=g.computation_cells
        cores=empty_cores()
        locations=(0,1,size-2,size-1,g.memory_count+17)
        for p in locations:
            for name,width in r.SCHEMA:
                if name!='address':cores[p,r.COL[name]]=rng.randrange(1<<width)
        points=set()
        for p in locations:
            points.update(range(p-35,p+36))
        with World(cores) as world:
            for _ in range(20):assert_local_step(self,world,points)

    def test_noncanonical_padding_assumption_is_not_silently_accepted(self):
        cores=empty_cores();cores[3,r.COL['address']]=99999
        with self.assertRaisesRegex(ValueError,'noncanonical'):World(cores)


if __name__=='__main__':unittest.main()
