"""Physical bits above compact geometry moduli remain faultable hardware."""
import unittest
import numpy as np
from gacsca.fixed_rule import compact16_holder_rule as f, compact16_holder_projected as r, compact16_holder_program as p
from gacsca.fixed_rule import compact16_holder_literal_cone as cone, compact16_holder_pulse_domain as domain


class HighBits(unittest.TestCase):
    def test_full_width_faults_across_colony_wrap(self):
        self.assertEqual(dict(r.SCHEMA)['address'],15)
        self.assertEqual(dict(r.SCHEMA)['age'],32)
        self.assertEqual(f.Q,1<<14);self.assertEqual(f.U,1<<30)
        image=cone.BankImage(np.arange(p.layout().memory_count+5,dtype=np.uint64)[None,:],np.array([[1,1]],dtype=np.uint64))
        bad=r.Cell(**{name:(1<<width)-1 for name,width in r.SCHEMA})
        self.assertTrue(domain.locally_two_sparse((f.Q-1,0),size=f.Q))
        for age in (0,f.WF_START-1,f.U-1):
            def initial(positions):
                raw=image.cells(positions);raw[:,f.COL['age']]=age;return raw
            result=cone.evolve(initial,{-1:bad,0:bad},size=f.Q,ticks=2)
            with self.subTest(age=age):self.assertTrue(result['rejoined'])


if __name__=='__main__':unittest.main()
