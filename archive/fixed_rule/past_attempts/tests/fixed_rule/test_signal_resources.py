import unittest
from gacsca.fixed_rule import signal_rule as r
from gacsca.fixed_rule.signal_resources import transcript,measure


class SignalResourcesTests(unittest.TestCase):
    def test_current_vote_schedule_cannot_finish_before_capture(self):
        x=measure();g=transcript()
        self.assertEqual(g.description_sha256,r.self_description().digest())
        self.assertEqual(len(g.info),r.FIELDS)
        self.assertEqual(len(g.wires),r.self_description().wires)
        self.assertEqual(x['operations'],2825)
        self.assertEqual(x['core_cells'],8256)
        self.assertLess(x['evaluation_ticks'],8*r.Q)
        self.assertGreater(x['stage3_vote_72Q_earliest_evaluation_end'],r.CAPTURE_AGE)
        self.assertGreater(x['stage3_vote_70Q_gather_margin'],0)
        self.assertGreater(x['stage3_vote_70Q_delivery_margin'],0)
        # Signal is genuinely gathered/evaluated/copied, not left outside raw E/D.
        for stage in range(3):
            sends=[op for op in g.instructions[slice(*g.stage_ranges[stage])] if op.kind==r.base.SEND and op.a==g.info[r.COL['signal']]]
            self.assertEqual(len(sends),10)
        self.assertTrue(any(op.kind==r.base.ADD and op.d==g.hold[r.COL['signal']] for op in g.instructions[slice(*g.stage_ranges[4])]))


if __name__=='__main__':unittest.main()
