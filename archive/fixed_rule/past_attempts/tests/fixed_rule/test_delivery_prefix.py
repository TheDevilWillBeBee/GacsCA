import ctypes
import random
import unittest
from dataclasses import replace
import numpy as np
from gacsca.fixed_rule import delivery_rule as f,delivery_projected as r,delivery_program as p
from gacsca.fixed_rule.delivery_prefix_world import World,library,pointer
from gacsca.fixed_rule.delivery_prefix_description import build


def initial(age=1):
    with World.encode((r.Cell(address=100),)) as world:a=world.stored
    a[:,r.COL['age']]=age;return a


class DeliveryPrefixTests(unittest.TestCase):
    def test_prefix_specialization_matches_complete_rule_on_its_domain(self):
        rng=random.Random(2771);desc=build();lib=library()
        for k in range(120):
            age=(0,32*f.Q,64*f.Q,70*f.Q,72*f.Q,f.CAPTURE_AGE-1,80*f.Q,96*f.Q-2)[k%8]
            address=(0,3,p.layout().computation_cells-1,f.Q-5,f.Q-1)[k%5]
            cells=tuple(f.Cell(**{**{n:rng.getrandbits(w) for n,w in f.SCHEMA},'address':(address+j)%f.Q,'age':age,'f1':0,'f2':0,'wf1':0,'wf2':0}) for j in range(-5,6))
            expected=f.local_step(cells);raw=tuple(w for c in cells for w in f.encode_cell(c))
            self.assertEqual(expected,f.decode_cell(desc.evaluate(raw)))
            a=np.array(raw,dtype=np.uint64);out=np.empty(f.FIELDS,dtype=np.uint64)
            lib.ww_prefix_local(pointer(a),pointer(out));self.assertEqual(expected,f.decode_cell(out.tolist()))

    def test_local_write_matches_complete_projected_rule(self):
        a=initial();i=p.layout().info[0]
        a[i,r.COL['head']]=1;a[i,r.COL['phase']]=f.WRITE;a[i,r.COL['rd']]=i;a[i,r.COL['value']]=12345
        with World(a) as world:
            positions=range(i-5,i+6)
            expected={x:r.local_step(tuple(world.cell(0,x+j) for j in range(-5,6))) for x in positions}
            world.run(1,skip_wait=False,skip_scan=False)
            for x,out in expected.items():self.assertEqual(world.cell(0,x),out)
            self.assertEqual(world.cell(0,i).data,12345)

    def test_packet_gap_and_colony_boundary_are_real_local_flights(self):
        g=p.layout();a=initial();start=g.computation_cells-1;target=f.Q-3
        for name,value in (('rp_valid',1),('rp_target',target),('rp_data',93)):a[start,r.COL[name]]=value
        distance=target-start
        with World(a) as world:
            world.run(100)
            self.assertEqual(world.cell(0,start+100).rp_data,93)
            self.assertEqual(world.cell(0,start+100).rp_valid,1)
            self.assertEqual(world.cell(0,target).data,0)
            world.run(distance-101)
            self.assertEqual(world.cell(0,target-1).rp_valid,1)
            expected=r.local_step(tuple(world.cell(0,(target+j)%f.Q) for j in range(-5,6)))
            world.run(1)
            self.assertEqual(world.cell(0,target),expected)
            self.assertEqual(world.cell(0,target).data,93)
            self.assertEqual(world.pending,0)
        a=initial();last=len(a)-1
        for name,value in (('rp_valid',1),('rp_target',1),('rp_data',55),('rp_remaining',1)):a[last,r.COL[name]]=value
        with World(a) as world:
            world.run(2);self.assertEqual(world.cell(0,1).data,55)
        a=initial()
        for name,value in (('lp_valid',1),('lp_target',f.Q-3),('lp_data',77),('lp_remaining',1)):a[0,r.COL[name]]=value
        with World(a) as world:
            world.run(3);self.assertEqual(world.cell(0,f.Q-3).data,77)

    def test_capture_and_majority_prevent_an_unjustified_quiet_jump(self):
        a=initial(f.CAPTURE_AGE-1);g=p.layout()
        for index in (1,2,3,g.computation_cells,g.computation_cells+1,g.computation_cells+2):a[index,r.COL['data']]=1
        with World(a) as fast,World(a) as slow:
            fast.run(12);slow.run(12,skip_wait=False,skip_scan=False)
            np.testing.assert_array_equal(fast.stored,slow.stored)
            for target in (3,f.Q-3):
                for e in range(-2,3):self.assertEqual((fast.cell(0,target+e).signal>>(2-e))&1,1)

    def test_unsupported_flags_signals_and_window_are_rejected(self):
        for name in ('f1','f2','wf1','wf2','signal'):
            a=initial();a[3,r.COL[name]]=1
            with self.assertRaises(ValueError):World(a)
        with World(initial(96*f.Q-2)) as world:
            world.run(1)
            with self.assertRaises(RuntimeError):world.run(1)


if __name__=='__main__':unittest.main()
