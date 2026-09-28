"""Small A100 parity tests; no substantial simulation workload."""
from dataclasses import replace
import unittest
import numpy as np
from gacsca.fixed_rule import flag_cuda as cuda,delivery_rule as f,delivery_native as native

M=f.Q//64
MASK=(1<<64)-1

class CudaFlags(unittest.TestCase):
    def test_temporal_halo_and_partition(self):
        rng=np.random.default_rng(48019);a=rng.bit_generator.random_raw(2*M).reshape(M,2)
        for ticks in (0,1,17,257,512,515):
            with self.subTest(ticks=ticks):
                want=cuda.advance(a,ticks,reference=True)
                np.testing.assert_array_equal(cuda.advance(a,ticks),want)
                if ticks==515:np.testing.assert_array_equal(cuda.advance(a,ticks,block_ticks=127),want)

    def test_actual_uniform_shortcut_and_edges(self):
        a=np.zeros((M,2),dtype=np.uint64)
        a[:M//4,0]=MASK;a[M//4:M//2,1]=MASK;a[M//2:3*M//4]=MASK
        a[255:258]=np.array([[1,3],[MASK,0],[0,MASK]],dtype=np.uint64)
        a[-1]=[MASK,17]
        want=cuda.advance(a,513,reference=True)
        np.testing.assert_array_equal(cuda.advance(a,513),want)
        np.testing.assert_array_equal(cuda.advance(a,513,shortcuts=False),want)

    def test_complete_native_rule_one_step(self):
        rng=np.random.default_rng(920);a=rng.bit_generator.random_raw(2*M).reshape(M,2);got=cuda.advance(a,1)
        positions=[*range(12),*range(f.Q-12,f.Q),*[int(v) for v in rng.integers(0,f.Q,size=100)]]
        for x in positions:
            cells=[]
            for delta in range(-5,6):
                pos=(x+delta)%f.Q;word,bit=divmod(pos,64)
                cells.append(f.Cell(address=pos,age=98*f.Q,f1=(int(a[word,0])>>bit)&1,f2=(int(a[word,1])>>bit)&1))
            expected=native.local_step(tuple(cells));word,bit=divmod(x,64)
            self.assertEqual(((int(got[word,0])>>bit)&1,(int(got[word,1])>>bit)&1),(expected.f1,expected.f2))

    def test_local_cone_and_domain_guards(self):
        ticks=257;center=256*64+31;rng=np.random.default_rng(388)
        a=rng.bit_generator.random_raw(2*M).reshape(M,2);b=a.copy()
        lo=center-5*ticks;hi=center+5*ticks
        for word in range(M):
            if word*64+63<lo or word*64>hi:b[word]=~b[word]
        first=cuda.advance(a,ticks);second=cuda.advance(b,ticks)
        for k in range(2):self.assertEqual((int(first[center//64,k])>>(center%64))&1,(int(second[center//64,k])>>(center%64))&1)
        for kw in ({'age':98*f.Q-1},{'age':f.U},{'block_ticks':513}):
            with self.assertRaises(ValueError):cuda.advance(a,1,**kw)
        with self.assertRaises(ValueError):cuda.advance(a[:-1],1)

if __name__=='__main__':unittest.main()
