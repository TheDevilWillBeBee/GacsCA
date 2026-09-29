import unittest
from types import SimpleNamespace
import numpy as np
from gacsca.fixed_rule import retimed_holder_rule as f, retimed_holder_core as c
from experiments.fixed_rule.audit_retimed_holder_contextual_macrostep import Replay,TransportGuard,COL
from experiments.fixed_rule.audit_retimed_holder_contextual_recovery import GlobalProcedures
from tests.fixed_rule.test_retimed_holder_global_events import ring


class ArrayView:
    def __init__(self,raw):
        self.raw = raw
        self.base = SimpleNamespace(size=len(raw),age=int(raw[0,f.COL['age']]))
    def cells(self,positions):
        return self.raw[np.asarray(positions)%len(self.raw)].copy()


class MacrostepAudit(unittest.TestCase):
    def test_complete_neighborhood_memo_matches_scalar_replay(self):
        raw = ring([{200:dict(pc=4000000,rb=2**63+17)}, {200:dict(pc=4000000,rb=2**63+19)}])
        view = ArrayView(raw)
        memo,scalar = Replay(view),GlobalProcedures(view)
        for tick in range(8):
            memo.step(view.base.age+tick);scalar.step(view.base.age+tick)
        np.testing.assert_array_equal(memo.words,scalar.words)
        self.assertEqual(int(memo.words[208,COL['rb']]),2**63+17)
        self.assertEqual(int(memo.words[f.Q+208,COL['rb']]),2**63+19)
        self.assertLessEqual(memo.unique_evaluations,memo.evaluations)

    def test_transport_must_stop_before_operand_effect(self):
        view = ArrayView(ring([{200:dict(phase=c.READ_A,ra=205)}]))
        model = Replay(view)
        guard = TransportGuard()
        with self.assertRaisesRegex(AssertionError,'skipped'):
            guard.advance(model,view.base.age,6)
        guard.advance(model,view.base.age,5)
        self.assertEqual(model.live,{205})

    def test_opposed_collision_cannot_be_skipped(self):
        view = ArrayView(ring([{200:dict(pc=4000000),210:dict(pc=4000001,direction=1)}]))
        with self.assertRaisesRegex(AssertionError,'interaction'):
            TransportGuard().advance(Replay(view),view.base.age,5)

    def test_first_marker_reflection_cannot_be_skipped(self):
        view = ArrayView(ring([{}, {2:dict(pc=4000000,direction=1)}]))
        with self.assertRaisesRegex(AssertionError,'first-marker'):
            TransportGuard().advance(Replay(view),view.base.age,3)


if __name__ == '__main__':
    unittest.main()
