import unittest
import random
import numpy as np
from gacsca.fixed_rule import small_holder_stream_initial as stream,small_holder_initial as old
from gacsca.fixed_rule import small_holder_resident_mixed as gpu,small_holder_resident_period as baseline
from gacsca.fixed_rule import small_holder_rule as f,small_holder_projected as r,small_holder_quotient as q,small_holder_program as p,small_holder_flag_profile as profile,small_holder_native as native
from experiments.fixed_rule.prove_small_holder_mixed_right import prove


class Streaming(unittest.TestCase):
    def setUp(self):
        rng=random.Random(883)
        self.top=tuple(r.Cell(**{name:rng.getrandbits(width) for name,width in r.SCHEMA}) for _ in range(2))
        self.ring=stream.InitialRing(self.top)
    def test_complete_raw_chunks_match_recursive_initializer_at_three_depths(self):
        for depth in range(4):
            positions=[-3,-1,0,1,2,f.Q-1,f.Q,f.Q+1]
            positions+=list(p.layout().info[::13])
            if depth>1:positions+=[p.layout().info[i]*f.Q+p.layout().info[j] for i,j in ((3,17),(71,53),(92,100))]
            got=self.ring.raw(depth,positions)
            wanted=np.array([f.encode_cell(r.lift(old.cell_at(self.top,depth,x))) for x in positions],dtype=np.uint64)
            np.testing.assert_array_equal(got,wanted)
            self.assertEqual(self.ring.resources(depth)['description_sha256'],f.self_description().digest())
            self.assertEqual(got.shape[1],f.FIELDS)
    def test_decoding_keeps_every_raw_controller_at_each_depth(self):
        for depth in (1,2,3):
            for parent in (0,1,p.layout().info[5],f.Q+3):
                words=[]
                positions=[parent*f.Q+a for a in p.layout().info]
                for at in range(0,len(positions),stream.CHUNK):
                    words.extend(self.ring.raw(depth,positions[at:at+stream.CHUNK])[:,f.COL['s2_data']])
                np.testing.assert_array_equal(words,self.ring.raw(depth-1,[parent])[0])
        with gpu.World.from_hierarchy(self.top,1) as world:
            self.assertEqual(world.decode(),self.top)
            identity=gpu.library()._name
        # Capacity is an execution limit, checked before consuming huge input.
        for depth in (2,3):
            with self.assertRaises((RuntimeError,ValueError)):gpu.World.from_hierarchy(self.top,depth,device_budget=1)
            self.assertEqual(identity,gpu.library()._name)
    def test_stream_validation_rejects_missing_metadata_width_and_count(self):
        valid=self.ring.raw(0,[0])
        bad=valid.copy();bad[0,0]^=1
        with self.assertRaises(ValueError):gpu.World.from_raw_chunks(1,[bad])
        bad=valid.copy();bad[0,f.COL['s2_head']]=2
        with self.assertRaises(ValueError):gpu.World.from_raw_chunks(1,[bad])
        with self.assertRaises(ValueError):gpu.World.from_raw_chunks(2,[valid])
        with self.assertRaises(ValueError):gpu.World.from_raw_chunks(1,[valid,valid])
        with self.assertRaises(ValueError):self.ring.raw(2,range(stream.CHUNK+1))


class MixedRight(unittest.TestCase):
    def test_full_physical_symbolic_certificate(self):
        result=prove();self.assertTrue(result['passed'])
        self.assertEqual(len(result['cases']),4)
        for case in result['cases']:
            self.assertEqual(case['neighboring_right_assignments'],8)
            self.assertEqual(case['descriptor_sha256'],f.self_description().digest())
    def test_mixed_wave_and_independent_controller_match_full_native(self):
        g=p.layout();rows=g.computation_cells+5;addresses=[*range(g.computation_cells),*range(f.Q-5,f.Q)]
        with baseline.World((r.Cell(),)*3) as initial:template=initial.stored()
        for age in (profile.START,f.WF_START+5000,f.WF_END-1,f.WF_END+5000):
            state=template.copy()
            for bit,part in zip((0,1,0),state.reshape(3,rows,len(q.SCHEMA))):
                part[:,q.COL['age']]=age;part[-5:,q.COL['signal']]=np.array([16,8,4,2,1])*bit
                part[:,[q.COL[x] for x in ('f1','f2','wf1','wf2')]]=np.array([profile.bits(age,a) for a in addresses])*bit
                part[100,q.COL['head']]=1;part[100,q.COL['phase']]=3;part[100,q.COL['rd']]=100;part[100,q.COL['value']]=777
            with self.assertRaises(ValueError):baseline.World.from_stored(state)
            with gpu.World.from_stored(state) as world:
                lo,hi=profile.interval(age)
                local={a%f.Q for center in (0,100,lo,hi,f.Q-3) for a in range(center-3,center+4)}
                points=tuple(col*f.Q+a for col in range(3) for a in sorted(local))
                expected=tuple(native.local_step(world.physical_cells(tuple((point+j)%(3*f.Q) for j in f.NEIGHBORHOOD))) for point in points)
                world.step();self.assertEqual(world.physical_cells(points),expected)
            if age==f.WF_START+5000:
                with gpu.World.from_stored(state) as fast,gpu.World.from_stored(state) as slow:
                    fast.batch(100);slow.run(100)
                    np.testing.assert_array_equal(fast.stored(),slow.stored())


if __name__=='__main__':unittest.main()
