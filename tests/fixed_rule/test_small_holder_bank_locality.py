import unittest
from gacsca.fixed_rule import small_holder_bank as bank, small_holder_bank_cuda as gpu
from gacsca.fixed_rule import small_holder_rule as f, small_holder_quotient as q


class BankLocality(unittest.TestCase):
    def test_raw_changes_outside_radius_do_not_change_output(self):
        reference=bank.Builder(1,1)
        changed=bank.Builder(1,1)
        for pos in (92,108,1000,f.Q-1):
            changed.set_raw_fields(pos,**{n:(1<<w)-1 for n,w in f.SCHEMA})
        changed.set_logical(200,q.Cell(**{n:(1<<w)-1 for n,w in q.SCHEMA}))
        with gpu.Resident(reference.freeze()) as a,gpu.Resident(changed.freeze()) as b:
            self.assertEqual(a.evaluate((100,)).tolist(),b.evaluate((100,)).tolist())
            self.assertNotEqual(a.evaluate((108,),reconstruct=True).tolist(),b.evaluate((108,),reconstruct=True).tolist())


if __name__=='__main__':unittest.main()
