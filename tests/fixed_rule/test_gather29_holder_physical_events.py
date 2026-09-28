"""Regression: new controller events agree with literal physical F in flight."""
import random
import unittest

from gacsca.fixed_rule import gather29_holder_rule as f
from gacsca.fixed_rule import gather29_holder_native as native
from gacsca.fixed_rule import gather29_holder_projected as r
from gacsca.fixed_rule import gather29_holder_core as c
from experiments.fixed_rule.validate_gather29_holder_physical_events import check


class Gather29PhysicalEvents(unittest.TestCase):
    def test_new_native_compiler_matches_scalar_raw_rule(self):
        rng=random.Random(2026092843)
        cases=[tuple(f.Cell(**{name:rng.getrandbits(width)
                               for name,width in f.SCHEMA})
                     for _ in f.NEIGHBORHOOD) for _ in range(4)]
        for age in (*c.RESET_AGES,*c.VOTE_AGES,c.CAPTURE_AGE,f.U-1):
            cases.append(tuple(r.lift(r.Cell(address=(f.Q-7+j)%f.Q,
                                                  age=age))
                               for j in f.NEIGHBORHOOD))
        for cells in cases:
            self.assertEqual(native.local_step(cells),f.local_step(cells))

    def test_actual_branch_and_marked_gather_events_match_literal_F(self):
        result=check()
        self.assertTrue(result['passed'])
        self.assertEqual(result['case_count'],8)
        self.assertEqual(result['complete_literal_raw_site_steps'],8*f.Q)
        self.assertEqual(result['physical_rule_sha256'],f.self_description().digest())


if __name__=='__main__':unittest.main()
