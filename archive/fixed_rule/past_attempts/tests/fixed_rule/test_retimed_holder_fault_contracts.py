"""Retimed CUDA flag parity, full-width packing, locality and resource guards."""
import os,random,unittest
from dataclasses import replace
import numpy as np
from gacsca.fixed_rule import retimed_holder_general_faults as faults,retimed_holder_resident_general as general
from gacsca.fixed_rule import retimed_holder_resident_faults as raw,retimed_holder_flags_gpu as flags
from gacsca.fixed_rule import retimed_holder_flags_cpu as cpu_flags,retimed_holder_cpu_general as cpu
from gacsca.fixed_rule import retimed_holder_rule as f,retimed_holder_projected as r
from gacsca.fixed_rule import retimed_holder_raw_packed as packed


class RawPacking(unittest.TestCase):
    def test_every_raw_field_and_width_roundtrips(self):
        rng=random.Random(9021)
        rows=np.array([[rng.getrandbits(width) for _,width in f.SCHEMA] for _ in range(33)],dtype=np.uint64)
        rows[0]=0;rows[1]=[(1<<width)-1 for _,width in f.SCHEMA]
        np.testing.assert_array_equal(packed.unpack(packed.pack(rows)),rows)
        self.assertEqual(f.WIDTH,4090);self.assertEqual(r.WIDTH,2704)
        self.assertEqual(f.NEIGHBORHOOD,tuple(range(-7,8)))
        self.assertEqual(f.self_description().digest(),'6e2f29f61bf281ec5d346cd58e717cf7e5b0afea263d2c17a18a58de295d8d23')


@unittest.skipUnless(os.environ.get('FIXED_RULE_GPU_TESTS')=='1','explicit bounded GPU invocation required')
class FaultContracts(unittest.TestCase):
    def test_arbitrary_packed_flags_match_CPU_across_clock_boundaries(self):
        rng=np.random.default_rng(9022)
        for age,ticks in ((f.WF_START-1,7),(f.WF_START+100,7),(f.WF_END-1,7),(f.U-2,2)):
            initial=rng.integers(0,2**64,size=(2*f.Q//64,2),dtype=np.uint64)
            right,left=(1,0),(1,1)
            with flags.World(right,left,age=age,initial=initial) as gpu,cpu_flags.World(right,left,age=age,runs=cpu.pack_runs(initial)) as ref:
                gpu.run(ticks);ref.run(ticks);expected=np.empty_like(initial);start=0
                for end,one,two in ref.runs:expected[start:int(end)]=(one,two);start=int(end)
                np.testing.assert_array_equal(gpu.read(),expected)

    def test_literal_budget_preserves_wrong_full_state(self):
        with general.World((r.Cell(),),age=100) as base,faults.World(base) as world:
            target=73;changes={}
            for d in (-1,0,1):
                cell=r.project(world.read((target+d,))[0]);changes[target+d]=replace(cell,**{f's{2-d}_data':cell.s2_data^1})
            world.inject(changes)
            with self.assertRaisesRegex(RuntimeError,'literal defect budget'):
                world.advance(10,absorb_data=False,absorb_flags=False,literal_budget=1)
            self.assertEqual(world.time,1);self.assertEqual(base.time,1)
            self.assertTrue(world.positions);self.assertEqual(world.read((target,))[0].s2_data,1)

    def test_frontier_capacity_rejection_is_atomic(self):
        with general.World((r.Cell(),),age=100) as base,faults.World(base) as world:
            points=tuple(64+16*i for i in range(raw.CAPACITY//15+1))
            world.inject({pos:r.Cell(address=pos,age=100,s2_pc=1024) for pos in points})
            positions=world.positions;before=base._core.snapshot();values=world.read(points[:100])
            with self.assertRaisesRegex(ValueError,'causal frontier'):world.step()
            self.assertEqual(world.time,0);self.assertEqual(base.time,0);self.assertEqual(world.positions,positions)
            self.assertEqual(world.read(points[:100]),values)
            for a,b in zip(base._core.snapshot(),before):np.testing.assert_array_equal(a,b)

    def test_outside_radius_seven_cannot_change_center_output(self):
        rng=random.Random(9023);center=100
        with general.World((r.Cell(),),age=100) as a,general.World((r.Cell(),),age=100) as b:
            with faults.World(a) as left,faults.World(b) as right:
                common=r.Cell(**{name:rng.getrandbits(width) for name,width in r.SCHEMA})
                left.inject({center:common});right.inject({center:common,center+8:r.Cell(**{name:rng.getrandbits(width) for name,width in r.SCHEMA})})
                left.step();right.step();self.assertEqual(left.read((center,)),right.read((center,)))

if __name__=='__main__':unittest.main()
