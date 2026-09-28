from functools import lru_cache
import random
import unittest
import numpy as np
from gacsca.fixed_rule import holder_rule as f,holder_core as c,holder_projected as r,holder_program as p,holder_quotient as q,holder_initial as initial,holder_native as native,holder_packed as packed,holder_cuda_local as gpu
from gacsca.fixed_rule.holder_prefix_world import library,pointer

class HolderCudaLocal(unittest.TestCase):
    def test_lossless_all_controller_fields_and_padding_rejection(self):
        rng=random.Random(42);a=np.array([[rng.getrandbits(w) for _,w in q.SCHEMA] for _ in range(200)],dtype=np.uint64)
        np.testing.assert_array_equal(packed.unpack(packed.pack(a)),a)
        self.assertEqual((packed.WIDTH,packed.WORDS),(604,10))
        bad=packed.pack(a);bad[0,-1]|=np.uint64(1)<<np.uint64(packed.WIDTH%64)
        with self.assertRaises(ValueError):packed.unpack(bad)
        a[0,q.COL['head']]=2
        with self.assertRaises(ValueError):packed.pack(a)

    def test_gpu_matches_cpu_and_complete_physical_controller(self):
        rng=random.Random(1201);inputs=[];physical=[]
        for age in (0,1,16*f.Q,32*f.Q,72*f.Q,c.CAPTURE_AGE-1,c.CAPTURE_AGE,96*f.Q-2):
            for base in (0,p.layout().info[0],p.layout().computation_cells-1,f.Q-3):
                @lru_cache(None)
                def read(pos):return q.Cell(**{n:rng.getrandbits(w) for n,w in q.SCHEMA if n not in ('address','age','f1','f2','wf1','wf2')},address=(base+pos)%f.Q,age=age)
                physical.append(tuple(r.lift(initial.coherent_cell(read,pos)) for pos in range(-7,8)))
                for pos in range(-2,3):inputs.append([q.encode_cell(read(pos+j)) for j in range(-5,6)])
        a=np.array(inputs,dtype=np.uint64);outputs,metrics=gpu.step(a);cpu=library()
        self.assertLess(metrics['explicit_device_bytes'],64*1024**2)
        self.assertLess(metrics['host_transfer_bytes'],16*1024**2)
        for old,got in zip(a,outputs):
            raw=np.array([c.encode_cell(q.lift(q.decode_cell(row.tolist()))) for row in old],dtype=np.uint64);expected=np.empty(c.FIELDS,dtype=np.uint64)
            cpu.ww_prefix_local(pointer(raw),pointer(expected));np.testing.assert_array_equal(got,q.encode_cell(q.project(c.decode_cell(expected.tolist()))))
        for i,raw in enumerate(physical):
            new={d:q.decode_cell(outputs[5*i+d+2].tolist()) for d in range(-2,3)}
            expected=r.project(native.local_step(raw));self.assertEqual(initial.coherent_cell(new.__getitem__,0),expected)

    def test_gpu_domain_and_batch_bound_rejections(self):
        a=np.array([[q.encode_cell(q.Cell(address=(100+j)%f.Q,age=1)) for j in range(-5,6)]],dtype=np.uint64)
        for field in ('address','age','f1','wf2'):
            bad=a.copy();bad[0,2,q.COL[field]]^=1
            with self.assertRaises(ValueError):gpu.step(bad)
        with self.assertRaises(ValueError):gpu.step(np.repeat(a,4097,axis=0))

if __name__=='__main__':unittest.main()
