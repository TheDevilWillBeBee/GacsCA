import random
import unittest
from dataclasses import replace
from gacsca.fixed_rule import delivery_rule as r,delivery_factorization as factor,delivery_native as native


class DeliveryFactorizationTests(unittest.TestCase):
    def test_complete_raw_factorization_with_arbitrary_flags_controller_and_mail(self):
        rng=random.Random(25251);lib=native.library()
        for k in range(360):
            age=(0,32*r.Q,64*r.Q,70*r.Q,r.CAPTURE_AGE-1,96*r.Q-1,96*r.Q,98*r.Q-1,112*r.Q,r.U-1)[k%10]
            a=(0,1,3,5,100,r.Q-6,r.Q-3,r.Q-1)[k%8]
            cells=tuple(r.Cell(**{**{name:rng.getrandbits(width) for name,width in r.SCHEMA},'address':(a+j)%r.Q,'age':age}) for j in range(-5,6))
            split=factor.local_step(cells)
            self.assertEqual(split,r.local_step(cells));self.assertEqual(split,native.local_step(cells,lib))
            clean=r.local_step(tuple(replace(c,**{name:0 for name in factor.FLAGS}) for c in cells))
            for name in factor.INDEPENDENT:self.assertEqual(getattr(split,name),getattr(clean,name),name)

    def test_received_data_survives_even_when_computed_flag1_clears_mail(self):
        cells=[r.Cell(address=100+j,age=70*r.Q+1) for j in range(-5,6)]
        cells[5]=replace(cells[5],kind=r.MEM,index=100)
        cells[4]=replace(cells[4],rp_valid=1,rp_target=100,rp_data=55)
        for i in (6,7,8):cells[i]=replace(cells[i],f1=1)
        out=factor.local_step(tuple(cells));self.assertEqual(out.f1,1);self.assertEqual(out.data,55)
        self.assertTrue(all(getattr(out,name)==0 for name in factor.MAIL))
        self.assertEqual(out,r.local_step(tuple(cells)))
        cells[5]=replace(cells[5],address=999)
        with self.assertRaises(ValueError):factor.local_step(tuple(cells))


if __name__=='__main__':unittest.main()
