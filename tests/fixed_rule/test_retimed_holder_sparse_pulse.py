"""Cyclic sparsity predicate and distributed full-state repair at clock boundaries."""
import itertools,random,unittest
import numpy as np
from gacsca.fixed_rule import retimed_holder_pulse_domain as domain,retimed_holder_literal_cone as cone
from gacsca.fixed_rule import retimed_holder_rule as f,retimed_holder_projected as r,retimed_holder_program as p


class SparsePulse(unittest.TestCase):
    def test_predicate_matches_all_small_ring_subsets(self):
        size=13
        for mask in range(1<<size):
            sites=[i for i in range(size) if mask>>i&1]
            expected=all(sum((pos-start)%size<11 for pos in sites)<=2 for start in range(size))
            self.assertEqual(domain.locally_two_sparse(sites,size=size),expected)

    def test_distributed_full_state_pulse_six_clock_contexts(self):
        g=p.layout();rng=random.Random(2026092710)
        bank=np.array([[rng.getrandbits(64) for _ in range(g.memory_count+5)]],dtype=np.uint64)
        image=cone.BankImage(bank,np.array([[1,1]],dtype=np.uint64));sites=[100+11*j+d for j in range(8) for d in (0,1)]
        self.assertTrue(domain.locally_two_sparse(sites,size=f.Q));self.assertEqual(len(sites),16)
        changes={pos:r.Cell(**{name:rng.getrandbits(width) for name,width in r.SCHEMA}) for pos in sites}
        for age in (0,1,f.CAPTURE_AGE-1,f.WF_START-1,f.WF_END-1,f.U-1):
            def initial(positions):
                raw=image.cells(positions);raw[:,f.COL['age']]=age;return raw
            result=cone.evolve(initial,changes,size=f.Q,ticks=2)
            with self.subTest(age=age):self.assertTrue(result['rejoined'])

    def test_three_copy_negative_control(self):
        g=p.layout();image=cone.BankImage(np.zeros((1,g.memory_count+5),dtype=np.uint64),np.zeros((1,2),dtype=np.uint64))
        def initial(positions):
            raw=image.cells(positions);raw[:,f.COL['age']]=17;return raw
        sites=(199,200,201);self.assertFalse(domain.locally_two_sparse(sites,size=f.Q))
        changes={pos:r.Cell(address=pos,age=17,**{f's{2-(pos-200)}_data':1}) for pos in sites}
        result=cone.evolve(initial,changes,size=f.Q,ticks=2);self.assertFalse(result['rejoined'])

    def test_invalid_positions_rejected(self):
        with self.assertRaises(ValueError):domain.locally_two_sparse((-1,),size=f.Q)
        with self.assertRaises(ValueError):domain.locally_two_sparse((0,),size=10)

if __name__=='__main__':unittest.main()
