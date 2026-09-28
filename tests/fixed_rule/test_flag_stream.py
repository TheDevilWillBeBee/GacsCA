import unittest
import ctypes
import random
import numpy as np
from gacsca.fixed_rule.delivery_rule import Q,U
from gacsca.fixed_rule.flag_byte_native import Evolution
from gacsca.fixed_rule.flag_byte_stream import World


class StreamTests(unittest.TestCase):
    def test_chunk_boundaries_preserve_exact_periodic_physical_state(self):
        runs=[(1,255,65535),(Q//128,(1<<64)-1,(1<<64)-1),(Q//64,0,0)]
        positions=[*range(20),*range(Q//16-10,Q//16+10),*range(Q//8-20,Q//8)]
        with World(runs,1,98*Q) as stream:
            for target in (1,19,257,1024,4096):
                stream.run(target-stream.info['time'],chunk=127)
                with Evolution(runs,1,98*Q,target) as whole:
                    for position in positions:self.assertEqual(stream.at(position),whole.at(position),(target,position))
            self.assertGreater(stream.info['chunks'],5)
            self.assertLess(stream.info['live_nodes'],stream.info['peak_nodes'])
            nodes,root=stream.snapshot();self.assertGreaterEqual(int(nodes[root,0]),20)
    def test_non_power_of_two_ring_entire_dag_matches_single_query(self):
        rng=random.Random(448)
        runs=[(1,rng.getrandbits(64),rng.getrandbits(64)),(Q//64+1,0,(1<<64)-1),(3*Q//64,(1<<64)-1,0)]
        with World(runs,3,98*Q) as stream,Evolution(runs,3,98*Q,1009) as whole:
            stream.run(1009,chunk=73)
            a,root=stream.snapshot();b,_=whole.proof();other=whole.info['final'];seen=set()
            def equal(x,y):
                if (x,y) in seen:return
                seen.add((x,y));ka,la,ra=map(int,a[x]);kb,lb,rb=map(int,b[y]);self.assertEqual(ka,kb)
                if not ka:self.assertEqual((la,ra),(lb,rb))
                else:equal(la,lb);equal(ra,rb)
            equal(root,other)
            self.assertGreater(len(seen),100)

    def test_exhausted_one_tick_budget_preserves_entire_committed_dag(self):
        rng=random.Random(351)
        runs=[(i+1,rng.getrandbits(64),rng.getrandbits(64)) for i in range(512)]+[(Q//64,0,0)]
        with World(runs,1,98*Q) as stream:
            before,root=stream.snapshot()
            with self.assertRaises(RuntimeError):stream.advance(1,budget=1024)
            after,other=stream.snapshot();self.assertEqual(root,other);np.testing.assert_array_equal(before,after)
            self.assertEqual(stream.info['time'],0)

    def test_independent_leaf_verifier_rejects_disagreement_before_commit(self):
        runs=[(Q//64,(1<<64)-1,(1<<64)-1)]
        with World(runs,1,98*Q) as stream:
            before,root=stream.snapshot();bad=np.zeros(384,dtype=np.uint8);two=np.zeros(768,dtype=np.uint8)
            pointer=ctypes.POINTER(ctypes.c_uint8)
            stream.lib.fs_tables(stream.handle,bad.ctypes.data_as(pointer),two.ctypes.data_as(pointer))
            with self.assertRaisesRegex(RuntimeError,'audit'):stream.advance(1)
            after,other=stream.snapshot();self.assertEqual(root,other);np.testing.assert_array_equal(before,after)
            self.assertEqual(stream.info['time'],0)

    def test_retry_is_exact_and_failed_request_preserves_committed_state(self):
        runs=[(Q//128,(1<<64)-1,(1<<64)-1),(Q//64,0,(1<<64)-1)]
        with World(runs,1,98*Q) as stream:
            row=stream.advance(100000,budget=4096)
            self.assertGreater(row['rejected'],0)
            with Evolution(runs,1,98*Q,row['time']) as full:
                for position in (0,1,2,100,Q//16,Q//8-1):self.assertEqual(stream.at(position),full.at(position))
            before=stream.info;sample=[stream.at(p) for p in range(20)]
            with self.assertRaises(RuntimeError):stream.advance(U)
            self.assertEqual(stream.info,before);self.assertEqual([stream.at(p) for p in range(20)],sample)
        with self.assertRaises(ValueError):stream.at(0)


if __name__=='__main__':unittest.main()
