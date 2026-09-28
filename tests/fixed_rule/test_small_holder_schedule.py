"""Distinguish spatial colony size from actual fixed clock deadlines."""
import unittest
from gacsca.fixed_rule import small_holder_core as c, small_holder_rule as f, small_holder_program as p

class SmallSchedule(unittest.TestCase):
    def test_independent_parameters_and_complete_budget(self):
        self.assertEqual((f.Q,f.U),(32768,1<<32))
        self.assertNotEqual(f.U,128*f.Q)
        self.assertEqual(dict(c.SCHEMA)['address'],15)
        self.assertEqual(dict(c.SCHEMA)['age'],32)
        g=p.layout();budget=g.timing_certificate()
        self.assertTrue(budget['fits'])
        self.assertGreaterEqual(f.Q-g.computation_cells-5,14)
        for i,row in enumerate(budget['gathers']):
            deadline=(c.VOTE_AGES[0] if i==2 else c.ACTIVE_ENDS[i])-c.RESET_AGES[i]
            self.assertEqual(row['deadline'],deadline)
            self.assertGreater(deadline,max(row['head_stopped'],row['last_arrival']))
        self.assertGreater(c.ACTIVE_ENDS[4]-c.RESET_AGES[4],budget['evaluation_ticks'])
        self.assertGreater(c.CAPTURE_AGE-c.VOTE_AGES[0],budget['stage3_last_delivery'])

    def test_recovery_spacing_and_spatial_forcing_duration(self):
        # This checks a source-derived inequality, not the full noisy lemma.
        gray_repair_bound=2*f.Q+1100
        rests=[following-end for end,following in zip(c.ACTIVE_ENDS,(*c.RESET_AGES[1:],f.U))]
        self.assertGreater(min(rests),gray_repair_bound)
        self.assertEqual(c.WF_END-c.WF_START,2*f.Q)
        self.assertLess(c.WF_END+f.Q//2,c.RESET_AGES[4])
        self.assertLess(c.VOTE_AGES[0],c.CAPTURE_AGE)
        self.assertLess(c.CAPTURE_AGE,c.ACTIVE_ENDS[2])
        self.assertLess(c.ACTIVE_ENDS[2],c.WF_START)
        self.assertEqual(c.VOTE_AGES[1],c.RESET_AGES[4])

if __name__=='__main__':unittest.main()
